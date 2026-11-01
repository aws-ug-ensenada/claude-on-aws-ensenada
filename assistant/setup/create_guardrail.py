"""Level 2 — create an Amazon Bedrock Guardrail and switch it on for the assistant.

  python setup/create_guardrail.py
  python setup/create_guardrail.py --update   # push changes to these settings to the existing guardrail

Cost: only when used — about $0.40 per 1,000 text units checked (see docs/costs.md). No monthly fee.
Undo: python setup/cleanup.py
"""

import argparse

import boto3

import _local

GUARDRAIL = dict(
    name="luna-assistant",
    description="Personal assistant demo — AWS User Group Ensenada",
    # Off-limits subjects. Add your own: a name, a one-sentence definition, an example.
    topicPolicyConfig={
        "topicsConfig": [
            {
                "name": "Investment advice",
                "definition": "Recommending specific stocks, crypto or investments to buy or sell.",
                "examples": ["Should I buy bitcoin?", "¿En qué acciones invierto?"],
                "type": "DENY",
            },
            {
                "name": "Medical diagnosis",
                "definition": "Diagnosing illnesses or recommending medication or doses.",
                "examples": ["What medicine should I take for this pain?"],
                "type": "DENY",
            },
        ]
    },
    # Harmful content filters.
    contentPolicyConfig={
        "filtersConfig": [
            {"type": t, "inputStrength": "HIGH", "outputStrength": "HIGH"}
            for t in ("HATE", "INSULTS", "SEXUAL", "VIOLENCE", "MISCONDUCT")
        ]
        # MEDIUM, not HIGH: at HIGH it blocks the user preferences that AgentCore Memory adds to the message.
        + [{"type": "PROMPT_ATTACK", "inputStrength": "MEDIUM", "outputStrength": "NONE"}]
    },
    # Personal data: mask it instead of sending it to the model.
    sensitiveInformationPolicyConfig={
        "piiEntitiesConfig": [
            {"type": t, "action": "ANONYMIZE"}
            for t in ("CREDIT_DEBIT_CARD_NUMBER", "EMAIL", "PHONE", "PASSWORD")
        ]
    },
    blockedInputMessaging="I can't help with that one — it's outside what I'm allowed to do.",
    blockedOutputsMessaging="I can't share that answer — it's outside what I'm allowed to do.",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--update", action="store_true", help="apply GUARDRAIL to the existing guardrail")
    args = parser.parse_args()

    local = _local.read()
    existing = (local.get("guardrail") or {}).get("id")
    if args.update:
        if not existing:
            print("No guardrail yet. Run without --update to create one.")
            return
        boto3.client("bedrock", region_name=_local.REGION).update_guardrail(guardrailIdentifier=existing, **GUARDRAIL)
        print(f"✅ Guardrail {existing} updated (DRAFT version, used right away)")
        return
    if existing:
        print(f'Already created: {existing}. Use --update to change it, or run setup/cleanup.py first to recreate.')
        return
    resp = boto3.client("bedrock", region_name=_local.REGION).create_guardrail(**GUARDRAIL)
    local["guardrail"] = {"enabled": True, "id": resp["guardrailId"], "version": resp["version"]}
    _local.write(local)
    print(f'✅ Guardrail {resp["guardrailId"]} created and enabled in config.local.yaml')


if __name__ == "__main__":
    main()
