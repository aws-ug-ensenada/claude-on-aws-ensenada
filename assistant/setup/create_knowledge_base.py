"""Level 5 — let the assistant search your own documents (RAG) and switch it on.

  python setup/create_knowledge_base.py          # about 2 minutes
  python setup/create_knowledge_base.py --sync   # after you add or change files in my_documents/

Creates, in this order:
  1. an S3 bucket with the files from my_documents/ (PDF, Word, Markdown, text, HTML, CSV…)
  2. an S3 vector bucket and index, where the embeddings live (Amazon S3 Vectors)
  3. an IAM role that lets Bedrock read 1 and write 2, and nothing else
  4. the knowledge base (Amazon Titan Text Embeddings V2) and its data source, then indexes the files

Cost: no monthly fee for the knowledge base; storage is pennies a month — see docs/costs.md.
Undo: python setup/cleanup.py
"""

import argparse
import json
import pathlib
import time

import boto3
from botocore.exceptions import ClientError

import _local

DOCS = pathlib.Path(__file__).parent.parent / "my_documents"
NAME = "luna-docs"
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
DIMENSIONS = 1024


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sync", action="store_true", help="re-upload my_documents/ and re-index")
    args = parser.parse_args()

    local = _local.read()
    kb = local.setdefault("knowledge_base", {"enabled": False})
    if args.sync:
        if not kb.get("enabled"):
            raise SystemExit("No knowledge base yet. Run without --sync first.")
        upload(kb["bucket"])
        ingest(kb["id"], kb["data_source_id"])
        return
    if kb.get("enabled"):
        print(f'Already created: {kb["id"]}. Use --sync to re-index, or setup/cleanup.py to recreate.')
        return

    region = _local.REGION
    account = boto3.client("sts", region_name=region).get_caller_identity()["Account"]
    s3 = boto3.client("s3", region_name=region)
    vectors = boto3.client("s3vectors", region_name=region)
    iam = boto3.client("iam")
    agent = boto3.client("bedrock-agent", region_name=region)

    def save(**values) -> None:
        # Saved after every step, so cleanup.py can find what exists even if a later step fails.
        kb.update(values)
        _local.write(local)

    if "bucket" not in kb:
        bucket = f"{NAME}-{account}-{region}"
        location = {} if region == "us-east-1" else {"CreateBucketConfiguration": {"LocationConstraint": region}}
        s3.create_bucket(Bucket=bucket, **location)  # private by default: S3 blocks public access on new buckets
        save(bucket=bucket)
        print(f"🪣 Bucket {bucket}")
    upload(kb["bucket"])

    if "vector_bucket" not in kb:
        vector_bucket = f"{NAME}-vectors-{account}"
        vectors.create_vector_bucket(vectorBucketName=vector_bucket)
        save(vector_bucket=vector_bucket)
        print(f"🧮 Vector bucket {vector_bucket}")
    if "index_arn" not in kb:
        index = vectors.create_index(
            vectorBucketName=kb["vector_bucket"],
            indexName=NAME,
            dataType="float32",
            dimension=DIMENSIONS,  # must match the embedding model
            distanceMetric="cosine",
            # Bedrock stores the chunk text and its own metadata here; they are too big to filter on.
            metadataConfiguration={"nonFilterableMetadataKeys": ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]},
        )
        save(index_arn=index["indexArn"])
        print(f"🧮 Vector index {NAME}")

    if "role" not in kb:
        role = f"{NAME}-knowledge-base"
        iam.create_role(
            RoleName=role,
            Description="Lets Amazon Bedrock read luna-docs and write its vector index",
            AssumeRolePolicyDocument=json.dumps(trust_policy(account, region)),
        )
        iam.put_role_policy(RoleName=role, PolicyName="access", PolicyDocument=json.dumps(role_policy(kb, account, region)))
        save(role=role)
        print(f"🔑 Role {role}")
    role_arn = iam.get_role(RoleName=kb["role"])["Role"]["Arn"]

    if "id" not in kb:
        print("Creating knowledge base…")
        created = retry_until_role_ready(
            lambda: agent.create_knowledge_base(
                name=NAME,
                description="My documents — personal assistant demo, AWS User Group Ensenada",
                roleArn=role_arn,
                knowledgeBaseConfiguration={
                    "type": "VECTOR",
                    "vectorKnowledgeBaseConfiguration": {
                        "embeddingModelArn": f"arn:aws:bedrock:{region}::foundation-model/{EMBEDDING_MODEL}",
                        "embeddingModelConfiguration": {
                            "bedrockEmbeddingModelConfiguration": {"dimensions": DIMENSIONS, "embeddingDataType": "FLOAT32"}
                        },
                    },
                },
                storageConfiguration={"type": "S3_VECTORS", "s3VectorsConfiguration": {"indexArn": kb["index_arn"]}},
            )
        )
        save(id=created["knowledgeBase"]["knowledgeBaseId"])
    wait_for(lambda: agent.get_knowledge_base(knowledgeBaseId=kb["id"])["knowledgeBase"]["status"], "ACTIVE")
    print(f'📚 Knowledge base {kb["id"]}')

    if "data_source_id" not in kb:
        source = agent.create_data_source(
            knowledgeBaseId=kb["id"],
            name="my-documents",
            dataSourceConfiguration={"type": "S3", "s3Configuration": {"bucketArn": f'arn:aws:s3:::{kb["bucket"]}'}},
            # Split files into ~300-token passages that overlap a little, so answers aren't cut in half.
            vectorIngestionConfiguration={
                "chunkingConfiguration": {
                    "chunkingStrategy": "FIXED_SIZE",
                    "fixedSizeChunkingConfiguration": {"maxTokens": 300, "overlapPercentage": 20},
                }
            },
        )
        save(data_source_id=source["dataSource"]["dataSourceId"])

    ingest(kb["id"], kb["data_source_id"])
    save(enabled=True)
    print(f'✅ Knowledge base {kb["id"]} created and enabled in config.local.yaml')


def upload(bucket: str) -> None:
    s3 = boto3.client("s3", region_name=_local.REGION)
    files = sorted(f for f in DOCS.iterdir() if f.is_file() and not f.name.startswith("."))
    for f in files:
        s3.put_object(Bucket=bucket, Key=f.name, Body=f.read_bytes())
    print(f"⬆️  Uploaded {len(files)} file(s) from my_documents/")


def ingest(kb_id: str, data_source_id: str) -> None:
    agent = boto3.client("bedrock-agent", region_name=_local.REGION)
    job = agent.start_ingestion_job(knowledgeBaseId=kb_id, dataSourceId=data_source_id)["ingestionJob"]
    print("Indexing documents…")

    def status() -> str:
        nonlocal job
        job = agent.get_ingestion_job(knowledgeBaseId=kb_id, dataSourceId=data_source_id, ingestionJobId=job["ingestionJobId"])[
            "ingestionJob"
        ]
        return job["status"]

    wait_for(status, "COMPLETE")
    stats = job.get("statistics", {})
    print(
        f'📄 Indexed: {stats.get("numberOfNewDocumentsIndexed", 0)} new, '
        f'{stats.get("numberOfModifiedDocumentsIndexed", 0)} changed, '
        f'{stats.get("numberOfDocumentsFailed", 0)} failed'
    )


def trust_policy(account: str, region: str) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": account},
                    "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock:{region}:{account}:knowledge-base/*"},
                },
            }
        ],
    }


def role_policy(kb: dict, account: str, region: str) -> dict:
    """Least privilege: one embedding model, one bucket (read), one vector index (read/write)."""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "EmbedWithTitan",
                "Effect": "Allow",
                "Action": "bedrock:InvokeModel",
                "Resource": f"arn:aws:bedrock:{region}::foundation-model/{EMBEDDING_MODEL}",
            },
            {
                "Sid": "ListDocuments",
                "Effect": "Allow",
                "Action": "s3:ListBucket",
                "Resource": f'arn:aws:s3:::{kb["bucket"]}',
                "Condition": {"StringEquals": {"aws:ResourceAccount": account}},
            },
            {
                "Sid": "ReadDocuments",
                "Effect": "Allow",
                "Action": "s3:GetObject",
                "Resource": f'arn:aws:s3:::{kb["bucket"]}/*',
                "Condition": {"StringEquals": {"aws:ResourceAccount": account}},
            },
            {
                "Sid": "ReadWriteVectorIndex",
                "Effect": "Allow",
                "Action": [
                    "s3vectors:PutVectors",
                    "s3vectors:GetVectors",
                    "s3vectors:DeleteVectors",
                    "s3vectors:QueryVectors",
                    "s3vectors:GetIndex",
                ],
                "Resource": kb["index_arn"],
            },
        ],
    }


def retry_until_role_ready(call, attempts: int = 10):
    """A new IAM role takes a few seconds to be usable everywhere in AWS."""
    for attempt in range(attempts):
        try:
            return call()
        except ClientError as e:
            if e.response["Error"]["Code"] not in ("ValidationException", "AccessDeniedException") or attempt == attempts - 1:
                raise
            time.sleep(6)


def wait_for(get_status, done: str, every: int = 5) -> None:
    while (status := get_status()) != done:
        if status in ("FAILED", "STOPPED", "DELETE_UNSUCCESSFUL"):
            raise SystemExit(f"❌ Status {status}. Check the Bedrock console, then run setup/cleanup.py.")
        time.sleep(every)


if __name__ == "__main__":
    main()
