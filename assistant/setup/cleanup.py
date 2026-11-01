"""Delete everything the setup/ scripts created (guardrail, memory, knowledge base) and reset config.local.yaml.

  python setup/cleanup.py

The cloud deployment (level 8) is removed separately:  agentcore remove all --yes && agentcore deploy --yes
"""

import time

import boto3
from bedrock_agentcore.memory import MemoryClient
from botocore.exceptions import ClientError

import _local


def main() -> None:
    local = _local.read()
    guardrail_id = (local.get("guardrail") or {}).get("id")
    memory_id = (local.get("memory") or {}).get("id")
    kb = local.get("knowledge_base") or {}
    if guardrail_id:
        boto3.client("bedrock", region_name=_local.REGION).delete_guardrail(guardrailIdentifier=guardrail_id)
        print(f"🗑️  Guardrail {guardrail_id} deleted")
    if memory_id:
        print("Deleting memory (up to a few minutes)…")
        MemoryClient(region_name=_local.REGION).delete_memory_and_wait(memory_id)
        print(f"🗑️  Memory {memory_id} deleted")
    if kb:
        delete_knowledge_base(kb)
    local.pop("guardrail", None)
    local.pop("memory", None)
    local.pop("knowledge_base", None)
    _local.write(local)
    if not (guardrail_id or memory_id or kb):
        print("Nothing to delete.")


def delete_knowledge_base(kb: dict) -> None:
    """Reverse order of setup/create_knowledge_base.py; skips whatever was never created."""
    region = _local.REGION
    agent = boto3.client("bedrock-agent", region_name=region)
    if kb.get("id"):
        if kb.get("data_source_id"):
            agent.delete_data_source(knowledgeBaseId=kb["id"], dataSourceId=kb["data_source_id"])
        agent.delete_knowledge_base(knowledgeBaseId=kb["id"])
        print("Deleting knowledge base…")
        while True:  # the vector index can only go once the knowledge base is gone
            try:
                agent.get_knowledge_base(knowledgeBaseId=kb["id"])
                time.sleep(5)
            except ClientError as e:
                if e.response["Error"]["Code"] != "ResourceNotFoundException":
                    raise
                break
        print(f'🗑️  Knowledge base {kb["id"]} deleted')
    if kb.get("vector_bucket"):
        vectors = boto3.client("s3vectors", region_name=region)
        if kb.get("index_arn"):
            vectors.delete_index(indexArn=kb["index_arn"])
        vectors.delete_vector_bucket(vectorBucketName=kb["vector_bucket"])
        print(f'🗑️  Vector bucket {kb["vector_bucket"]} deleted')
    if kb.get("bucket"):
        bucket = boto3.resource("s3", region_name=region).Bucket(kb["bucket"])
        bucket.objects.all().delete()
        bucket.delete()
        print(f'🗑️  Bucket {kb["bucket"]} deleted')
    if kb.get("role"):
        iam = boto3.client("iam")
        iam.delete_role_policy(RoleName=kb["role"], PolicyName="access")
        iam.delete_role(RoleName=kb["role"])
        print(f'🗑️  Role {kb["role"]} deleted')


if __name__ == "__main__":
    main()
