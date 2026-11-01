"""Level 5 — search your own documents (RAG) in an Amazon Bedrock Knowledge Base.

Active only after:  python setup/create_knowledge_base.py
"""

import boto3
from strands import tool


def tools(cfg: dict) -> list:
    kb = cfg.get("knowledge_base") or {}
    if not kb.get("enabled"):
        return []
    client = boto3.client("bedrock-agent-runtime", region_name=cfg["model"]["region"])

    @tool
    def search_my_documents(question: str) -> list[dict]:
        """Search the user's own documents (contracts, policies, notes, recipes) for passages that answer a question.
        Use it for anything about the user's personal paperwork. Quote the source file in your answer.

        Args:
            question: What to look for, in plain words, e.g. "when is rent due".
        """
        resp = client.retrieve(
            knowledgeBaseId=kb["id"],
            retrievalQuery={"text": question},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": kb.get("results", 4)}},
        )
        return [
            {
                "text": r["content"]["text"],
                "source": r.get("location", {}).get("s3Location", {}).get("uri", "").rsplit("/", 1)[-1],
                "score": round(r.get("score", 0), 3),
            }
            for r in resp["retrievalResults"]
        ]

    return [search_my_documents]
