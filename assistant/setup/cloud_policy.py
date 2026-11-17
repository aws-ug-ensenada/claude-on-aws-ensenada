"""Level 8 — IAM policy that lets the cloud runtime use the guardrail, memory and knowledge base you created.

  python setup/cloud_policy.py

The runtime role that AgentCore creates can already call Claude on Bedrock and write logs and traces.
This adds least-privilege access to the resources in config.local.yaml, and nothing else:
  guardrail      → bedrock:ApplyGuardrail
  memory         → read and write events, retrieve memory records
  knowledge base → bedrock:Retrieve
It writes agentcore/luna.policy.json (git-ignored: it holds your account ID), which agentcore.json lists
under additionalPolicies. Run it again after you create or delete one of these resources, then deploy.
Creates nothing in AWS.
"""

import json
import pathlib

import boto3

import _local

OUT = pathlib.Path(__file__).parent.parent.parent / "agentcore" / "luna.policy.json"


def main() -> None:
    """Write agentcore/luna.policy.json with one least-privilege statement per resource in config.local.yaml (level 8)."""
    local, region = _local.read(), _local.REGION
    account = boto3.client("sts", region_name=region).get_caller_identity()["Account"]
    statements = []
    if (g := local.get("guardrail") or {}).get("id"):
        statements.append({
            "Sid": "Guardrail",
            "Effect": "Allow",
            "Action": "bedrock:ApplyGuardrail",
            "Resource": f'arn:aws:bedrock:{region}:{account}:guardrail/{g["id"]}',
        })
    if (m := local.get("memory") or {}).get("id"):
        statements.append({
            "Sid": "Memory",
            "Effect": "Allow",
            "Action": [f"bedrock-agentcore:{a}" for a in ("CreateEvent", "GetEvent", "ListEvents", "DeleteEvent", "RetrieveMemoryRecords")],
            "Resource": f'arn:aws:bedrock-agentcore:{region}:{account}:memory/{m["id"]}',
        })
    if (kb := local.get("knowledge_base") or {}).get("id"):
        statements.append({
            "Sid": "KnowledgeBase",
            "Effect": "Allow",
            "Action": "bedrock:Retrieve",
            "Resource": f'arn:aws:bedrock:{region}:{account}:knowledge-base/{kb["id"]}',
        })
    if not statements:
        # IAM rejects an empty policy, so grant something harmless instead of breaking the deploy.
        statements.append({"Sid": "Nothing", "Effect": "Allow", "Action": "sts:GetCallerIdentity", "Resource": "*"})
    OUT.write_text(json.dumps({"Version": "2012-10-17", "Statement": statements}, indent=2) + "\n")
    print(f"✅ {OUT.relative_to(OUT.parent.parent)}: {', '.join(s['Sid'] for s in statements)}")


if __name__ == "__main__":
    main()
