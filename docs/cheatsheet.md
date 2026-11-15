# Luna on one page · Luna en una página

**English** · [Español](#español)

## Run it in 15 minutes
```bash
git clone https://github.com/aws-ug-ensenada/claude-on-aws-ensenada.git
cd claude-on-aws-ensenada/assistant
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python luna.py                      # an agent: weather, rates, your to-do list
```
You need an AWS account with Claude turned on in Amazon Bedrock ([bedrock-access.md](bedrock-access.md)), or a Claude API key.

## Make it your business: five steps
1. **Preset:** `python setup/new_preset.py my-shop --business "My Shop" --about "Owns a small shop"`
2. **Files:** put your CSV exports in `business/my-shop/`
3. **Documents:** policies and price lists in `my_documents/`, then `python setup/create_knowledge_base.py`
4. **Tools:** plug in an MCP server, or write one `@tool` function ([extend.md](extend.md))
5. **Rules:** ask a person before risky steps; add a Bedrock Guardrail

Check it: `python luna.py --preset my-shop --check` · Run it: `python luna.py --preset my-shop`

## The idea
**Agent = brain + hands + rules.** Brain: Claude. Hands: tools and MCP servers. Rules: instructions, guardrails, approval. The framework that runs the loop is **Strands Agents** (open source, AWS).

---

## Español

## Pruébalo en 15 minutos
```bash
git clone https://github.com/aws-ug-ensenada/claude-on-aws-ensenada.git
cd claude-on-aws-ensenada/assistant
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python luna.py                      # un agente: clima, tipo de cambio, tu lista de tareas
```
Necesitas una cuenta de AWS con Claude activado en Amazon Bedrock ([bedrock-access.md](bedrock-access.md)), o una llave de la API de Claude.

## Hazlo para tu negocio: cinco pasos
1. **Preset:** `python setup/new_preset.py mi-negocio --business "Mi Negocio" --about "Dueño de un negocio pequeño"`
2. **Archivos:** tus exportaciones CSV en `business/mi-negocio/`
3. **Documentos:** políticas y listas de precios en `my_documents/`, luego `python setup/create_knowledge_base.py`
4. **Herramientas:** conecta un servidor MCP, o escribe una función con `@tool` ([extend.md](extend.md))
5. **Reglas:** pide confirmación antes de acciones riesgosas; agrega un Guardrail de Bedrock

Revísalo: `python luna.py --preset mi-negocio --check` · Ejecútalo: `python luna.py --preset mi-negocio`

## La idea
**Agente = cerebro + manos + reglas.** Cerebro: Claude. Manos: herramientas y servidores MCP. Reglas: instrucciones, guardrails, aprobación. El marco que ejecuta el ciclo es **Strands Agents** (código abierto, de AWS).
