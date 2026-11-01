# Bedrock access and quotas

What an AWS account needs before Luna can call Claude on Amazon Bedrock, and how to fix it when it can't. The account has to clear three gates for each Claude model. Clearing one doesn't clear the others, and Bedrock reports all three with similar errors.

| Gate | Done once per | Cost | What you see when it's missing |
|---|---|---|---|
| 1. Anthropic use-case form | account | free | the form pops up in the playground |
| 2. Model agreement (AWS Marketplace subscription) | account and model | free; pay per token | `AccessDeniedException` |
| 3. Tokens-per-minute quota above 0 | account, model and region | free | `AccessDeniedException: … is not available for this account … contact AWS Sales` |

The third gate is easy to miss. AWS gives some accounts, often new ones or ones with little Bedrock history, an **applied quota of 0** on the newest models, even though the AWS default is in the millions. At that point the agreement and the IAM permissions are both fine, but every call is still refused. Older models on the same account can work normally, which makes it look like a model-access problem rather than a quota.

## Quotas Luna needs

Region **us-east-1**. Luna calls Claude through the `global.` inference profiles, so the **Global cross-region** quotas are the ones that matter. The `us.` profiles use the plain *Cross-region* quotas, and cost 10% more.

Luna's defaults are **Claude Haiku 4.5** (Luna and every specialist) and **Claude Sonnet 4.6** (the Director in agency and fleet mode, and the `professional` preset). On the presenter's account both had their normal quota from the start. The 5.5 models are the ones that start at 0.

| Model | Default in Luna? | Quota name in Service Quotas | Code | AWS default |
|---|---|---|---|---|
| Claude Haiku 4.5 | ✅ Luna, every specialist | Global cross-region model inference tokens per minute for Anthropic Claude Haiku 4.5 | `L-9A11C666` | 5,000,000 |
| Claude Sonnet 4.6 | ✅ Director, `professional` preset | Global cross-region model inference tokens per minute for Anthropic Claude Sonnet 4.6 | `L-7BEE40FB` | 6,000,000 |
| Claude Haiku 5.5 | when you switch | Global cross-region model inference tokens per minute for Anthropic Claude Haiku 5.5 | `L-F26CA8D1` | 10,000,000 |
| Claude Sonnet 5.5 | when you switch | Global cross-region model inference tokens per minute for Anthropic Claude Sonnet 5.5 | `L-31AB82D0` | 6,000,000 |
| Claude Opus 5.5 | when you switch | Global cross-region model inference tokens per minute for Anthropic Claude Opus 5.5 | `L-A103A344` | 30,000,000 |

If you use the `us.` profiles instead, the matching codes are `L-58BE175A` (Haiku 4.5), `L-15B8E632` (Sonnet 4.6), `L-47520EB7` (Haiku 5.5), `L-94A31E46` (Sonnet 5.5) and `L-A4430697` (Opus 5.5).

Nothing else Luna uses has needed a quota request. Titan Text Embeddings V2 (level 5) allows 300,000 tokens per minute by default. AgentCore (levels 3 and 8) had no quota at 0. Service Quotas doesn't list S3 Vectors.

## Check an account

```bash
# Gate 2: the agreement. "AVAILABLE" means accepted.
aws bedrock get-foundation-model-availability --model-id anthropic.claude-haiku-5-5 \
  --region us-east-1 --query agreementAvailability.status

# Gate 3: the applied quota. 0 means every call is refused.
for q in L-F26CA8D1 L-31AB82D0; do
  aws service-quotas get-service-quota --service-code bedrock --quota-code $q --region us-east-1 \
    --query '[Quota.QuotaName,Quota.Value]' --output text
done
```

A one-word test call, which costs a fraction of a cent:

```bash
aws bedrock-runtime converse --region us-east-1 --model-id global.anthropic.claude-haiku-5-5 \
  --messages '[{"role":"user","content":[{"text":"hola"}]}]' --inference-config maxTokens=10
```

## Fix it

**Gate 1, the use-case form.** In the Bedrock console for us-east-1, open **Model catalog**, open **Claude Haiku 5.5**, choose **Open in playground**, and fill in **Submit use case details**. For a personal or community demo, *Intended users: Internal* and a one-line description are enough.

**Gate 2, the agreement.** Sending a message in the playground normally creates it. If the status stays `NOT_AVAILABLE`, accept it from the CLI. The command needs the offer's `offerToken`, which is a long base64 string; passing its `offerId` (`offer-…`) fails with *Invalid Base 64 data*.

```bash
T=$(aws bedrock list-foundation-model-agreement-offers --model-id anthropic.claude-haiku-5-5 \
      --region us-east-1 --query 'offers[0].offerToken' --output text)
aws bedrock create-foundation-model-agreement --model-id anthropic.claude-haiku-5-5 \
  --offer-token "$T" --region us-east-1
```

The status goes from `PENDING` to `AVAILABLE` in about a minute. To undo it, run `aws bedrock delete-foundation-model-agreement --model-id … --region us-east-1`.

**Gate 3, the quota.** Open **Service Quotas → AWS services → Amazon Bedrock** in us-east-1, search for the quota name from the table, select it, and choose **Request increase at account level**.

- The form doesn't accept values below the AWS default. For Haiku 5.5, enter **10000000**.
- A request at or near the default can be approved automatically. Anything above the default, such as 10,000,000 for Sonnet 5.5, becomes an **AWS Support case** that a person reviews. That can take from hours to days. If AWS asks for a justification, answer on the case in **AWS Support Center**.
- Until AWS approves, the *Applied* column keeps showing 0. Track progress under **Quota request history**, or from the CLI:

  ```bash
  aws service-quotas list-requested-service-quota-change-history --service-code bedrock --region us-east-1 \
    --query 'RequestedQuotas[].[QuotaCode,DesiredValue,Status,CaseId]' --output text
  ```

A higher quota is only a ceiling. You still pay only for the tokens you use.

**The request can be denied automatically.** On an account with little Bedrock history, both cases closed within 20 minutes, with the quota still at 0 and this reply:

> To maintain service quality and ensure a reliable experience for all customers, model access for a given account may depend on factors such as regional availability, account history, and usage patterns. We are unable to approve your request at this time. Accessibility is subject to change automatically as time passes.

A system makes this decision from the account's history, so a better justification on the case is unlikely to change it.

**Another region doesn't get around it.** On 2026-11-01 the presenter's account had the full Haiku 5.5 quota (10,000,000 tokens per minute) in us-west-2 and eu-central-1, and every availability flag said `AVAILABLE` (agreement, authorization, entitlement, region), yet calls in all three regions were still refused with *"not available for this account"*. So the 0 in us-east-1 is a symptom: AWS holds the Claude 5.x models back for the whole account. Check the flags and quotas in another region with:

```bash
aws bedrock get-foundation-model-availability --model-id anthropic.claude-haiku-5-5 --region us-west-2
aws service-quotas list-service-quotas --service-code bedrock --region us-west-2 \
  --query "Quotas[?contains(QuotaName,'Claude Haiku 5.5')].[QuotaName,Value]" --output text
```

What can help:

- Use the account: steady, normal use of the models it already allows (Claude 4.x) builds the history the reply refers to. Re-check the quota every week or two.
- Ask someone at AWS to escalate. The reply points to an Account Manager or Solutions Architect; for an AWS User Group, the group's AWS community contact is the closest equivalent.
- Run Claude 5.5 through the Claude API instead ([next section but one](#the-claude-api-instead-of-bedrock)).
- Use Claude 4.x on Bedrock in the meantime, which is what Luna does by default.

**Request quotas days before a talk or workshop.** Ask attendees to check gate 3 on their own accounts ahead of time as well.

## Switching to Claude 5.5

Once the 5.5 quotas on your account are above 0, try 5.5 without changing any file:

```bash
python luna.py --set model.id=global.anthropic.claude-haiku-5-5 \
               --set agency.director.model=global.anthropic.claude-sonnet-5-5
```

To make it the default, change `model.id` and `agency.director.model` in `config.yaml` (and `model.id` in `presets/professional.yaml`). `pricing.yaml` has prices for both families, so the cost line stays right.

Claude 4.x needs no agreement step: it subscribes on the first call.

## The Claude API instead of Bedrock

Luna can call Claude through the Claude API with your own key, which skips the Bedrock gates above. Use it when an account can't get Claude 5.5 on Bedrock yet, or to show that the same agent runs on either provider.

1. In the [Claude Console](https://platform.claude.com), add credit under **Billing** and set a **monthly spend limit**. A Claude.ai subscription (Pro or Max) doesn't include API access. API spending is billed by Anthropic, so an AWS Budget doesn't see it.
2. Under **API keys**, create a key with an expiry that covers the date you need it.
3. Put the key in an environment variable without echoing it or pasting it anywhere else:
   ```bash
   read -rs ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY
   ```
4. Run Luna on it:
   ```bash
   python luna.py --set model.provider=anthropic --set model.id=claude-haiku-5-5 \
                  --set agency.director.model=claude-sonnet-5-5
   ```
   Model IDs work with or without the Bedrock prefix: `global.anthropic.claude-haiku-5-5` becomes `claude-haiku-5-5`, and Bedrock's `-v1:0` suffix is dropped.

What still works, tested on 2026-10-31 with Haiku 5.5 and Sonnet 5.5:

| Level | On the Claude API |
|---|---|
| 1, 4, 6, 7 · agent, MCP, agency, fleet | ✅ |
| 3 · Memory (AgentCore, in AWS) | ✅ It still needs AWS credentials |
| 5 · Your documents (knowledge base, in AWS) | ✅ It still needs AWS credentials |
| 2 · Bedrock Guardrails | ✅ **For what you type.** A hook checks your input with Bedrock's standalone ApplyGuardrail API before Claude sees it (`core.input_guardrail`); answers aren't checked on this path. The startup line shows `guardrail (your input, via ApplyGuardrail)` |
| 8 · Cloud | Possible, but the key then has to be stored in AWS (Secrets Manager or AgentCore Identity); not worked out yet |

On Haiku 5.5 a solo answer cost about **$0.0006** and an agency answer about **$0.012**, against about $0.004 and $0.018 on Claude 4.x through Bedrock.

**Leaked a key?** If a key ends up in a chat, a ticket or a repository, delete it under **API keys** right away and create a new one.

## History on the presenter's account

| Date | What |
|---|---|
| 2026-10-31 | Use-case form submitted in the console. |
| 2026-10-31 | Haiku 5.5 agreement accepted from the CLI (the playground didn't create it). |
| 2026-10-31 | Quotas found at 0 for every Claude 5.5 model, both `global.` and `us.` profiles. |
| 2026-10-31 | Quota increases requested: `L-F26CA8D1` (Haiku 5.5) and `L-31AB82D0` (Sonnet 5.5), both to 10,000,000. Each one became a support case. |
| 2026-10-31 | Both cases closed within 20 minutes: **denied** ("unable to approve your request at this time", based on account history). Quotas still 0. |
| 2026-10-31 | Luna's defaults switched to Claude Haiku 4.5 and Sonnet 4.6. |
| 2026-10-31 | Claude 5.5 tested through the Claude API with the presenter's own key; all levels except Guardrails work (the input guardrail was added on 2026-11-01). |
| 2026-11-01 | Haiku 5.5 quota is 10,000,000 in us-west-2 and eu-central-1 (0 in us-east-1), all availability flags `AVAILABLE`, but calls are refused in every region: an account-level hold on Claude 5.x. |
