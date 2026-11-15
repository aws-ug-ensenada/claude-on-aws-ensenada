from diagrams import Diagram, Cluster, Edge
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import IAM
from diagrams.aws.storage import SimpleStorageServiceS3Bucket, SimpleStorageServiceS3
from diagrams.programming.flowchart import Document
from diagrams.generic.storage import Storage
from diagrams.generic.blank import Blank
from diagrams.onprem.client import User
from diagrams.onprem.network import Internet
from diagrams.programming.language import Python

g = {"fontsize": "14", "pad": "0.5", "nodesep": "0.4", "ranksep": "0.9", "splines": "spline"}
with Diagram("Run it on your laptop", filename="local", outformat="png", show=False, direction="TB", graph_attr=g):
    with Cluster("Your laptop"):
        user = User("User")
        agent = Python("Strands agent (Python)\nLuna")
        cfg = Document("config.yaml +\nyour preset")
        biz = Storage("business/ folder\n(your CSV files)")
        todo = Storage("to-do list (JSON)")
        with Cluster("Agency mode (optional)"):
            director = Python("Director\n(master agent)")
            pl = Python("Planner\n(weather)")
            fi = Python("Finance\n(currency)")
            org = Python("Organizer\n(to-dos, time)")
            re_ = Python("Researcher\n(web, AWS docs)")
            lib = Python("Librarian\n(my documents)")
            off = Python("Office\n(your files, exact counts)")
        with Cluster("MCP servers (local processes via uvx)"):
            mcp = Python("time / fetch / files /\naws_docs / Gmail, Slack…\n(you choose)")
    with Cluster("AWS us-east-1"):
        iam = IAM("IAM credentials")
        bed = Bedrock("Amazon Bedrock\nClaude Haiku 4.5 /\nSonnet 4.6")
        gr = Bedrock("Bedrock Guardrails\n(optional)")
        mem = Bedrock("AgentCore Memory\n(optional, Bedrock icon)")
        with Cluster("Level 5: your documents (RAG)"):
            kb = Bedrock("Bedrock Knowledge Base\n(Bedrock icon)")
            tit = Bedrock("Titan Text\nEmbeddings V2")
            s3 = SimpleStorageServiceS3Bucket("S3 bucket\nmy_documents/")
            sv = SimpleStorageServiceS3("S3 Vectors index\n(S3 icon)")
    with Cluster("Internet"):
        om = Internet("Open-Meteo\n(weather, free)")
        fr = Internet("Frankfurter\n(USD/MXN, free)")
        api = Internet("Claude API\n(Anthropic)")
    user >> Edge(label="chat (terminal)") >> agent
    cfg >> Edge(style="dotted") >> agent
    agent >> Edge(label="tool calls") >> todo
    agent >> Edge(label="optional", style="dashed") >> director
    for s_ in (pl, fi, org, re_, lib, off):
        director >> Edge(label="orders" if s_ is pl else "", dir="both") >> s_
    agent >> Edge(label="credentials") >> iam
    iam >> Edge(label="prompt + tools") >> bed
    agent >> Edge(label="optional", style="dashed") >> gr
    agent >> Edge(style="dashed") >> mem
    agent >> Edge(label="tool calls") >> om
    agent >> fr
    agent >> Edge(label="optional: Claude API key", style="dashed") >> api
    off >> Edge(label="one folder only", style="dashed") >> biz
    off >> Edge(style="dashed") >> mcp
    re_ >> Edge(style="dashed") >> mcp
    org >> Edge(style="dashed") >> mcp
    lib >> Edge(label="search_my_documents") >> kb
    s3 >> Edge(label="ingest", style="dashed") >> kb
    kb >> Edge(style="dashed", label="embed") >> tit
    kb >> Edge(label="store / query") >> sv
