from diagrams import Diagram, Cluster, Edge
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import IAMRole, SecretsManager
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import SimpleStorageServiceS3Bucket, SimpleStorageServiceS3
from diagrams.aws.management import Cloudwatch
from diagrams.onprem.client import User
from diagrams.onprem.network import Internet
from diagrams.programming.language import Python

g = {"fontsize": "14", "pad": "0.5", "nodesep": "0.9", "ranksep": "0.7", "splines": "spline"}
with Diagram("Luna on AgentCore", filename="cloud", outformat="png", show=False, direction="TB", graph_attr=g):
    user = User("User")
    with Cluster("AWS us-east-1"):
        with Cluster("AgentCore Runtime\n(solo agent by default;\nLUNA_MODE=agency runs the team;\nfleet mode: one runtime per agent, over A2A)"):
            rec = Python("Director\n(master agent)")
            pl = Python("Planner\n(weather)")
            fi = Python("Finance\n(currency)")
            org = Python("Organizer\n(to-dos)")
            res = Python("Researcher\n(MCP: fetch,\naws_docs)")
            lib = Python("Librarian\n(search_my_documents)")
        gw = APIGateway("AgentCore Gateway\n(MCP tools, OpenAPI targets;\nAPI Gateway icon)")
        mem = Bedrock("AgentCore Memory\n(Bedrock icon)")
        with Cluster("Level 5: Knowledge Base (RAG)"):
            kb = Bedrock("Bedrock Knowledge Base")
            tit = Bedrock("Titan Text\nEmbeddings V2")
            sv = SimpleStorageServiceS3("S3 Vectors index\n(S3 icon)")
            s3 = SimpleStorageServiceS3Bucket("S3 bucket\nmy_documents/")
        ident = SecretsManager("AgentCore Identity\n(API key for the\nGateway targets)")
        gr = Bedrock("Bedrock Guardrails")
        bed = Bedrock("Amazon Bedrock\nClaude")
        cw = Cloudwatch("CloudWatch\nObservability\n(OpenTelemetry\ntraces)")
        role = IAMRole("IAM role")
    with Cluster("Internet / MCP servers"):
        web = Internet("Web pages +\nAWS docs")
        om = Internet("Open-Meteo")
        fr = Internet("Frankfurter")
        api = Internet("Claude API\n(Anthropic)")
    user >> rec
    for a in (pl, fi, org, res, lib):
        rec >> Edge(label="orders" if a is pl else "", dir="both") >> a
    rec >> Edge(style="dashed") >> mem
    for a in (pl, fi, org, res, lib, rec):
        a >> Edge(style="dotted") >> gr
    gr >> bed
    rec >> Edge(style="dashed", label="optional: Claude API key") >> api
    gw >> Edge(style="dotted", label="outbound key") >> ident
    pl >> Edge(label="weather tool") >> gw
    fi >> Edge(label="currency tool") >> gw
    gw >> Edge(label="HTTPS") >> om
    gw >> Edge(label="HTTPS") >> fr
    res >> Edge(label="MCP") >> web
    lib >> Edge(label="query") >> kb
    s3 >> Edge(style="dashed", label="ingest") >> kb
    kb >> Edge(style="dashed", label="embed") >> tit
    kb >> Edge(label="vectors") >> sv
    rec >> Edge(style="dotted", label="traces") >> cw
    role >> Edge(style="dotted", label="assumed by") >> rec
