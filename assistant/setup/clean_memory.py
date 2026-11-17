"""Level 3 — list and tidy what the memory has learned about the user.

  python setup/clean_memory.py                                  # list what it remembers
  python setup/clean_memory.py --keep vegetarian --keep cold    # show what would be deleted (everything else)
  python setup/clean_memory.py --keep vegetarian --keep cold --yes   # delete it

Memory learns from every conversation, including rehearsals, so before a demo it can hold stray
preferences ("reply with only the number of emails…"). The guardrail's prompt-attack filter can refuse
a request once such text is added to the prompt. --keep takes a case-insensitive regex; a record that
matches any of them stays. Deleting records can't be undone, but memory re-learns from later conversations.
"""

import argparse
import json
import re
import sys

import boto3

import _local

sys.path.insert(0, str(_local.FILE.parent))
from core import load_config  # noqa: E402


def records(cfg: dict) -> list[tuple[str, str]]:
    """(record id, preference text) for the current user."""
    actor = re.sub(r"[^a-zA-Z0-9-]", "-", cfg["user"]["name"]).lower()
    client = boto3.client("bedrock-agentcore", region_name=_local.REGION)
    out, token = [], None
    while True:
        kwargs = dict(memoryId=cfg["memory"]["id"], namespace=f"/preferences/{actor}", maxResults=100)
        resp = client.list_memory_records(**kwargs, **({"nextToken": token} if token else {}))
        for r in resp["memoryRecordSummaries"]:
            text = r["content"]["text"]
            try:
                text = json.loads(text).get("preference", text)
            except ValueError:
                pass
            out.append((r["memoryRecordId"], text))
        token = resp.get("nextToken")
        if not token:
            return out


def main() -> None:
    """List the user's memory records; with --keep, delete those that match no pattern (only with --yes)."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keep", action="append", default=[], metavar="REGEX", help="keep records matching this; delete the rest")
    parser.add_argument("--yes", action="store_true", help="actually delete (otherwise only show what would go)")
    args = parser.parse_args()

    cfg = load_config()
    if not (cfg.get("memory") or {}).get("enabled"):
        raise SystemExit("No memory (python setup/create_memory.py).")
    found = records(cfg)
    print(f"{len(found)} record(s) in {cfg['memory']['id']}:")
    doomed = []
    for rid, text in found:
        keep = not args.keep or any(re.search(k, text, re.I) for k in args.keep)
        print(f"  {'keep  ' if keep else 'DELETE'} {rid}  {text[:100]}")
        if not keep:
            doomed.append(rid)
    if not args.keep:
        print("Pass --keep REGEX (repeatable) to choose what to keep.")
        return
    if not doomed:
        print("Nothing to delete.")
    elif not args.yes:
        print(f"Dry run: {len(doomed)} would be deleted. Add --yes to delete them.")
    else:
        client = boto3.client("bedrock-agentcore", region_name=_local.REGION)
        for rid in doomed:
            client.delete_memory_record(memoryId=cfg["memory"]["id"], memoryRecordId=rid)
        print(f"Deleted {len(doomed)}.")


if __name__ == "__main__":
    main()
