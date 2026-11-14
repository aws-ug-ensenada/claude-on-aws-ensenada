"""Find the resources the setup/ scripts created, by name, so cleanup works on a machine that has no config.local.yaml.

Read-only: it only lists and describes. Returns the same shape config.local.yaml uses.
"""

import boto3
from botocore.exceptions import ClientError

import _local

NAME = "luna-docs"  # keep in step with setup/create_knowledge_base.py


def _try(fn, default=None):
    try:
        return fn()
    except ClientError:
        return default


def guardrail_id() -> str | None:
    client = boto3.client("bedrock", region_name=_local.REGION)
    for g in client.list_guardrails().get("guardrails", []):
        if g["name"] == "luna-assistant":
            return g["id"]
    return None


def memory_id() -> str | None:
    client = boto3.client("bedrock-agentcore-control", region_name=_local.REGION)
    for m in client.list_memories().get("memories", []):
        if m["id"].startswith("luna_assistant-"):
            return m["id"]
    return None


def knowledge_base() -> dict:
    region = _local.REGION
    account = boto3.client("sts", region_name=region).get_caller_identity()["Account"]
    kb: dict = {}
    bucket = f"{NAME}-{account}-{region}"
    if _try(lambda: boto3.client("s3", region_name=region).head_bucket(Bucket=bucket)) is not None:
        kb["bucket"] = bucket
    vector_bucket = f"{NAME}-vectors-{account}"
    index = _try(lambda: boto3.client("s3vectors", region_name=region).get_index(vectorBucketName=vector_bucket, indexName=NAME))
    if index:
        kb["vector_bucket"] = vector_bucket
        kb["index_arn"] = index["index"]["indexArn"]
    role = f"{NAME}-knowledge-base"
    if _try(lambda: boto3.client("iam").get_role(RoleName=role)):
        kb["role"] = role
    agent = boto3.client("bedrock-agent", region_name=region)
    for k in agent.list_knowledge_bases().get("knowledgeBaseSummaries", []):
        if k["name"] == NAME:
            kb["id"] = k["knowledgeBaseId"]
            sources = agent.list_data_sources(knowledgeBaseId=k["knowledgeBaseId"]).get("dataSourceSummaries", [])
            if sources:
                kb["data_source_id"] = sources[0]["dataSourceId"]
    return kb


def discover() -> dict:
    """{'guardrail': {'id': …}, 'memory': {'id': …}, 'knowledge_base': {…}} for whatever exists."""
    found: dict = {}
    if gid := guardrail_id():
        found["guardrail"] = {"id": gid}
    if mid := memory_id():
        found["memory"] = {"id": mid}
    if kb := knowledge_base():
        found["knowledge_base"] = kb
    return found
