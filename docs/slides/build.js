// Builds the talk's slides: docs/slides/claude-on-aws-ensenada.pptx
//
//   cd docs/slides && npm install && node build.js
//
// One generator for the whole deck, so a change to the talk is a change here, reviewed like code.
// The demo slides follow docs/demo-runbook.md; keep the two in step.

const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const QRCode = require("qrcode");

const OUT = path.join(__dirname, "claude-on-aws-ensenada.pptx");
const REPO = "github.com/aws-ug-ensenada/claude-on-aws-ensenada";

// "Pacific dusk": deep ocean for the dark slides, white for content, a sunset accent.
const COLOR = {
  ocean: "0F2A36", // dark slides, code blocks
  ink: "1B2B33", // text on light
  teal: "1F7A80", // secondary
  coral: "E8663D", // accent
  mist: "EEF6F6", // demo slide background
  foam: "CFE3E3", // text on dark
  muted: "5A707B",
  line: "D5E3E4",
  white: "FFFFFF",
  code: "E6F1F0",
  quote: "9FD8CF",
};
const FONT = { head: "Cambria", body: "Calibri", code: "Courier New" };
const W = 13.333;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "From chatbot to agent: building an AI agent on AWS with Claude";
pres.author = "Alonso Parasxidis";
pres.subject = "AWS User Group Ensenada";
pres.theme = { headFontFace: FONT.head, bodyFontFace: FONT.body };

// ── Layouts ──────────────────────────────────────────────────────────────

const footer = () => [
  { text: { text: "From chatbot to agent · AWS User Group Ensenada", options: { x: 0.6, y: 6.98, w: 8, h: 0.3, fontSize: 10, color: COLOR.muted, fontFace: FONT.body, margin: 0 } } },
];
const slideNumber = () => ({ x: 12.2, y: 6.98, w: 0.6, h: 0.3, fontSize: 10, color: COLOR.muted, fontFace: FONT.body, align: "right" });
// A function, not a shared object: pptxgenjs converts option objects to EMU in place on first use.
const contentTitle = () => ({ name: "title", type: "title", x: 0.6, y: 0.45, w: 10.4, h: 0.9, fontFace: FONT.head, fontSize: 36, bold: true, color: COLOR.ink, align: "left", valign: "middle", margin: 0 });

pres.defineSlideMaster({
  title: "Title",
  background: { color: COLOR.ocean },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.7, fontFace: FONT.head, fontSize: 48, bold: true, color: COLOR.white, align: "left", valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.9, w: 11.7, h: 1.3, fontFace: FONT.body, fontSize: 22, color: COLOR.foam, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "Section",
  background: { color: COLOR.ocean },
  objects: [
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 2.35, w: 11.7, h: 0.6, fontFace: FONT.body, fontSize: 18, bold: true, color: COLOR.coral, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 3.0, w: 11.7, h: 1.9, fontFace: FONT.head, fontSize: 44, bold: true, color: COLOR.white, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "Content",
  background: { color: COLOR.white },
  objects: [{ placeholder: { options: contentTitle(), text: "" } }, ...footer()],
  slideNumber: slideNumber(),
});
pres.defineSlideMaster({
  title: "Demo",
  background: { color: COLOR.mist },
  objects: [
    { placeholder: { options: contentTitle(), text: "" } },
    ...footer(),
    { rect: { x: 11.45, y: 0.62, w: 1.28, h: 0.5, fill: { color: COLOR.coral }, rectRadius: 0.25 } },
    { text: { text: "DEMO", options: { x: 11.45, y: 0.62, w: 1.28, h: 0.5, fontSize: 14, bold: true, color: COLOR.white, align: "center", valign: "middle", fontFace: FONT.body, margin: 0 } } },
  ],
  slideNumber: slideNumber(),
});

// ── Helpers ──────────────────────────────────────────────────────────────

const iconCache = new Map();
async function icon(Component, color) {
  const key = `${Component.name}-${color}`;
  if (!iconCache.has(key)) {
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Component, { color: `#${color}`, size: 256 }));
    const png = await sharp(Buffer.from(svg)).png().toBuffer();
    iconCache.set(key, `image/png;base64,${png.toString("base64")}`);
  }
  return iconCache.get(key);
}

// The deck's motif: a white icon in a coral circle.
async function badge(slide, Component, x, y, d = 0.8, fill = COLOR.coral, name = "icon") {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: `${name} circle` });
  const pad = d * 0.24;
  slide.addImage({ data: await icon(Component, COLOR.white), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, objectName: name, altText: name });
}

function card(slide, x, y, w, h, fill = COLOR.white, name = "card") {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: COLOR.line, width: 0.75 },
    shadow: { type: "outer", color: "9AB3B6", opacity: 0.35, blur: 6, offset: 2, angle: 90 }, objectName: name,
  });
}

function text(slide, value, opts) {
  slide.addText(value, { isTextBox: true, fontFace: FONT.body, color: COLOR.ink, margin: 0, valign: "top", ...opts });
}

function bullets(slide, items, opts) {
  text(slide, items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })), { fontSize: 16, ...opts });
}

// A terminal block: the command, then what you type at Luna's prompt.
function terminal(slide, { command, question }, x, y, w, h) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: COLOR.ocean }, line: { color: COLOR.ocean }, objectName: "terminal" });
  const lines = command.split("\n");
  const runs = lines.flatMap((line, i) => [
    { text: line.startsWith(" ") ? "  " : "❯ ", options: { color: COLOR.coral, bold: true } },
    { text: line, options: { color: COLOR.code, breakLine: i < lines.length - 1 || Boolean(question) } },
  ]);
  if (question) {
    runs.push({ text: "you ▸ ", options: { color: COLOR.coral, bold: true, paraSpaceBefore: 14 } });
    runs.push({ text: question, options: { color: COLOR.quote } });
  }
  text(slide, runs, { x: x + 0.3, y: y + 0.25, w: w - 0.6, h: h - 0.5, fontFace: FONT.code, fontSize: 15, objectName: "command" });
}


// Planned minutes per slide, in deck order: [minutes, optional]. Optional slides are the ones to skip when the talk runs long.
// The build prints the totals and fails if this list and the deck get out of step. Replace these estimates with your timed run.
const TIMING = [
  [0.5], [1], [1.5], // 1-3 opening
  [0.2], [1.5], [1.5], [1.5], [1.5], [1], // 4-9 the idea
  [0.2], [1.5], [3], [2, true], [3], [1, true], [1.5], // 10-16 meet Luna
  [0.2], [1], [1.5, true], [2.5], [2], [2, true], [1, true], [1], [1.5], // 17-25 any business
  [0.2], [1.5], [1.5, true], [1.5, true], [1, true], [2.5], [1.5], [1], [1.5], [0.5, true], [1], [0.7], [0], // 26-38 the rest
];
let slideCount = 0;
const sections = {};
function addSlide(section, masterName) {
  if (!sections[section]) {
    pres.addSection({ title: section });
    sections[section] = true;
  }
  const slide = pres.addSlide({ masterName, sectionTitle: section });
  const [minutes, optional] = TIMING[slideCount++] || [];
  if (minutes !== undefined) {
    const notes = slide.addNotes.bind(slide);
    slide.addNotes = (text) => notes(`⏱ ~${minutes} min${optional ? " · optional: skip if you are short on time" : ""}.\n\n${text}`);
  }
  return slide;
}

// One demo scene: what to run, what to watch for, why it matters, and the fallback clip.
async function demo(section, { title, level, command, question, watch, why, clip, notes }) {
  const s = addSlide(section, "Demo");
  s.addText(title, { placeholder: "title" });
  text(s, level, { x: 0.6, y: 1.38, w: 10.4, h: 0.4, fontSize: 16, italic: true, color: COLOR.teal });
  terminal(s, { command, question }, 0.6, 1.95, 7.3, 2.45);
  await badge(s, fa.FaLightbulb, 0.6, 4.7, 0.62, COLOR.teal, "why icon");
  text(s, why, { x: 1.4, y: 4.68, w: 6.5, h: 1.05, fontSize: 17, valign: "middle" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 6.05, w: 7.3, h: 0.5, rectRadius: 0.25, fill: { color: COLOR.white }, line: { color: COLOR.teal, width: 1, dashType: "dash" }, objectName: "clip chip" });
  text(s, [{ text: "▶  Recorded clip  ", options: { bold: true, color: COLOR.teal } }, { text: clip, options: { color: COLOR.muted, fontFace: FONT.code } }],
    { x: 0.85, y: 6.05, w: 6.9, h: 0.5, fontSize: 12, valign: "middle", objectName: "clip" });
  card(s, 8.25, 1.95, 4.48, 4.6, COLOR.white, "watch card");
  text(s, "What to watch for", { x: 8.55, y: 2.2, w: 3.9, h: 0.45, fontSize: 19, bold: true, color: COLOR.teal });
  bullets(s, watch, { x: 8.55, y: 2.8, w: 3.95, h: 3.6, fontSize: 17 });
  s.addNotes(notes);
}

// ── Slides ───────────────────────────────────────────────────────────────

async function build() {
  // 1 · Title
  let s = addSlide("Opening", "Title");
  s.addText("From chatbot to agent", { placeholder: "title" });
  s.addText([
    { text: "Building an AI agent on AWS with Claude", options: { breakLine: true } },
    { text: "De chatbot a agente · AWS User Group Ensenada", options: { fontSize: 18, color: COLOR.quote } },
  ], { placeholder: "body" });
  let x = 0.8;
  for (const [Ic, label] of [[fa.FaBrain, "brain"], [fa.FaTools, "hands"], [fa.FaShieldAlt, "rules"]]) {
    await badge(s, Ic, x, 5.75, 0.75, COLOR.coral, label);
    x += 1.0;
  }
  s.addNotes("Welcome. Tonight we build one AI assistant on stage and grow it from a chatbot into an agent, then into a small team of agents running on AWS. Everything is in the repo, so you can run it at home tonight.");

  // 1b · Short intro in Spanish
  s = addSlide("Opening", "Content");
  s.addText("Bienvenidos: qué vamos a ver", { placeholder: "title" });
  const intro = [
    [fa.FaRoute, "Un asistente, ocho niveles", "De un chatbot a un agente, y de ahí a un equipo de agentes en AWS, con Claude."],
    [fa.FaStore, "Sirve para cualquier negocio", "Un viñedo, una cafetería, una clínica, una escuela. Los ejemplos son nuestros; el caso es el tuyo."],
    [fa.FaGithub, "Todo está en el repo", "Clónalo, córrelo en 15 minutos y adáptalo a tu negocio con Strands Agents."],
  ];
  x = 0.6;
  for (let i = 0; i < intro.length; i++) {
    const [Ic, head, body] = intro[i];
    card(s, x, 1.75, 3.85, 4.4, COLOR.white, `${head} card`);
    await badge(s, Ic, x + 0.4, 2.1, 0.95, i === 1 ? COLOR.teal : COLOR.coral);
    text(s, head, { x: x + 0.4, y: 3.3, w: 3.1, h: 0.9, fontFace: FONT.head, fontSize: 22, bold: true });
    text(s, body, { x: x + 0.4, y: 4.3, w: 3.1, h: 1.7, fontSize: 16, color: COLOR.muted });
    x += 4.14;
  }
  s.addNotes("Say it in Spanish, one sentence per card. Guion: \"Bienvenidos. Esta noche vamos a construir un asistente de inteligencia artificial y lo vamos a hacer crecer: primero un chatbot, luego un agente que usa herramientas, y al final un equipo de agentes en AWS. Los ejemplos son un viñedo y una cafetería, porque son de aquí, pero lo importante es que sirve para cualquier negocio: una clínica, una escuela, un taller, el tuyo. Y todo está en el repositorio, para que lo puedas correr en tu casa esta misma noche.\" Then ask the two questions on the next slide. Slides are in English; speak and answer in whichever language the room prefers.");

  // 2 · Hook
  s = addSlide("Opening", "Content");
  s.addText("Quick show of hands", { placeholder: "title" });
  const hands = [
    [fa.FaComments, "Who has used ChatGPT or Claude?", "A chat: you ask, it answers, you decide what's next."],
    [fa.FaRobot, "Who has used an agent?", "An agent does things for you: it looks things up, calls tools and works through steps on its own."],
  ];
  x = 0.6;
  for (const [Ic, q, a] of hands) {
    card(s, x, 1.75, 5.9, 4.4, COLOR.white, "hands card");
    await badge(s, Ic, x + 0.45, 2.15, 1.0);
    text(s, q, { x: x + 0.45, y: 3.4, w: 5.0, h: 1.0, fontFace: FONT.head, fontSize: 26, bold: true });
    text(s, a, { x: x + 0.45, y: 4.5, w: 5.0, h: 1.3, fontSize: 17, color: COLOR.muted });
    x += 6.2;
  }
  s.addNotes("Callback to April's session, where the AWS DevOps Agent diagnosed faults on EKS: that was an agent someone else built. Tonight we build our own. Ask both questions and count hands; most people have used a chat, few have used an agent.");

  // 3 · Section: the idea
  s = addSlide("The idea", "Section");
  s.addText("Part 1", { placeholder: "body" });
  s.addText("What turns a chatbot into an agent", { placeholder: "title" });
  s.addNotes("Five minutes of concept, then straight to the terminal.");

  // 4 · Brain + hands + rules
  s = addSlide("The idea", "Content");
  s.addText("Agent = brain + hands + rules", { placeholder: "title" });
  const parts = [
    [fa.FaBrain, "Brain", "Claude on Amazon Bedrock", "Understands what you want, plans the steps and decides which tool to use."],
    [fa.FaTools, "Hands", "Tools", "Weather, exchange rates, your to-do list, your own documents. Python functions or MCP servers."],
    [fa.FaShieldAlt, "Rules", "Instructions and guardrails", "What it may and may not do, Bedrock Guardrails, and asking you before anything risky."],
  ];
  x = 0.6;
  for (const [Ic, head, sub, body] of parts) {
    card(s, x, 1.75, 3.85, 4.75, COLOR.white, `${head} card`);
    await badge(s, Ic, x + 0.4, 2.1, 0.95);
    text(s, head, { x: x + 0.4, y: 3.25, w: 3.1, h: 0.6, fontFace: FONT.head, fontSize: 28, bold: true });
    text(s, sub, { x: x + 0.4, y: 3.85, w: 3.1, h: 0.75, fontSize: 16, bold: true, color: COLOR.teal });
    text(s, body, { x: x + 0.4, y: 4.65, w: 3.1, h: 1.7, fontSize: 16, color: COLOR.muted });
    x += 4.12;
  }
  s.addNotes("In plain words: a chatbot is a very well-read person on the phone who can't look anything up. An agent is the same person with a phone, a calculator and your notebook, and house rules. The one idea of the talk. A chatbot is only a brain: it can talk, but it can only guess about the world. Give it hands (tools) and it can find out. Give it rules and you can trust it with real tasks. Everything else tonight is a variation on these three.");

  // 5 · The loop
  s = addSlide("The idea", "Content");
  s.addText("How an agent answers", { placeholder: "title" });
  const steps = [
    [fa.FaUser, "You ask", "\"What should I wear today?\""],
    [fa.FaBrain, "Claude plans", "I need today's weather"],
    [fa.FaTools, "Calls a tool", "get_weather()"],
    [fa.FaEye, "Reads the result", "22 °C, 84% chance of rain"],
    [fa.FaCommentDots, "Answers", "\"Layers and a rain jacket\""],
  ];
  x = 0.6;
  for (let i = 0; i < steps.length; i++) {
    const [Ic, head, body] = steps[i];
    await badge(s, Ic, x + 0.72, 2.0, 0.95, i === 0 || i === 4 ? COLOR.teal : COLOR.coral);
    text(s, head, { x, y: 3.1, w: 2.4, h: 0.75, fontSize: 19, bold: true, align: "center", valign: "bottom" });
    text(s, body, { x, y: 3.95, w: 2.4, h: 0.9, fontSize: 15, color: COLOR.muted, align: "center", fontFace: i === 2 ? FONT.code : FONT.body });
    if (i < steps.length - 1) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.2, y: 2.32, w: 0.35, h: 0.3, fill: { color: COLOR.line }, line: { color: COLOR.line }, objectName: "arrow" });
    x += 2.48;
  }
  card(s, 0.6, 5.0, 12.13, 1.45, COLOR.mist, "loop note");
  await badge(s, fa.FaRedo, 0.95, 5.3, 0.8, COLOR.teal, "loop icon");
  text(s, [
    { text: "The middle three steps repeat ", options: { bold: true } },
    { text: "until Claude has what it needs: weather, then the exchange rate, then your to-do list. The framework (Strands Agents) runs the loop; Claude decides each step." },
  ], { x: 2.0, y: 5.2, w: 10.4, h: 1.05, fontSize: 17, valign: "middle" });
  s.addNotes("In plain words: like asking an assistant a question; they check their phone, read what they find, and only then answer. This loop is the whole trick. The model never touches the internet itself: it asks for a tool call, our code runs the tool, and the result goes back to the model. Strands Agents is AWS's open-source framework that runs this loop for us.");

  // Strands Agents
  s = addSlide("The idea", "Content");
  s.addText("Strands Agents runs the loop", { placeholder: "title" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.7, w: 7.3, h: 4.35, rectRadius: 0.12, fill: { color: COLOR.ocean }, line: { color: COLOR.ocean }, objectName: "code block" });
  const code = [
    "from strands import Agent, tool",
    "",
    "@tool",
    "def get_stock(item: str) -> dict:",
    "    \"\"\"Units of an item on the shelf.\"\"\"",
    "    return {\"item\": item, \"units\": 12}",
    "",
    "agent = Agent(",
    "    model=BedrockModel(model_id=...),",
    "    system_prompt=\"You help run a shop.\",",
    "    tools=[get_stock],",
    ")",
    "agent(\"Do we need to reorder beans?\")",
  ];
  text(s, code.map((l, i) => ({ text: l, options: { color: l.startsWith("@") ? COLOR.coral : COLOR.code, breakLine: i < code.length - 1 } })),
    { x: 0.9, y: 1.95, w: 6.8, h: 3.9, fontFace: FONT.code, fontSize: 15, objectName: "code" });
  card(s, 8.25, 1.7, 4.48, 4.35, COLOR.white, "strands card");
  text(s, "What it gives you", { x: 8.55, y: 1.92, w: 3.9, h: 0.45, fontSize: 19, bold: true, color: COLOR.teal });
  bullets(s, ["Open source, from AWS: strandsagents.com", "Runs the ask-call-read loop for you", "A tool is a Python function with a docstring", "Any model: Bedrock, Claude API, others", "MCP servers plug in as tools", "Memory and guardrails attach as options"],
    { x: 8.55, y: 2.5, w: 3.95, h: 3.4, fontSize: 15 });
  card(s, 0.6, 6.2, 12.13, 0.6, COLOR.mist, "strands note");
  text(s, [{ text: "Luna is this, grown up: ", options: { bold: true } }, { text: "assistant/core.py is about 300 lines. Read it, then change it." }],
    { x: 0.95, y: 6.2, w: 11.5, h: 0.6, fontSize: 15, valign: "middle" });
  s.addNotes("In plain words: Strands is the kitchen that cooks the loop so you only write the recipe. You give it a model, a prompt and tools, and it handles the back-and-forth. The docstring is the instruction the model reads to decide when to use a tool. Use it for any agent, not just Luna: the Luna code is a worked example of the same ten lines with memory, guardrails, MCP and a team of agents added. docs/extend.md explains each piece.");

  // The whole picture
  s = addSlide("The idea", "Content");
  s.addText("The whole picture", { placeholder: "title" });
  card(s, 0.6, 1.75, 2.7, 4.6, COLOR.white, "you card");
  await badge(s, fa.FaLaptop, 1.45, 2.05, 1.0, COLOR.teal, "you");
  text(s, "You", { x: 0.8, y: 3.25, w: 2.3, h: 0.5, fontFace: FONT.head, fontSize: 24, bold: true, align: "center" });
  text(s, "A terminal today; a chat app or Slack later", { x: 0.85, y: 3.85, w: 2.2, h: 0.9, fontSize: 14, color: COLOR.muted, align: "center" });
  text(s, "Your files and documents", { x: 0.85, y: 5.0, w: 2.2, h: 0.9, fontSize: 14, color: COLOR.muted, align: "center" });
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 3.4, y: 3.8, w: 0.4, h: 0.35, fill: { color: COLOR.coral }, line: { color: COLOR.coral }, objectName: "arrow" });
  card(s, 3.9, 1.75, 4.1, 4.6, COLOR.mist, "luna card");
  text(s, "Luna, built with Strands Agents", { x: 4.15, y: 1.95, w: 3.6, h: 0.5, fontSize: 18, bold: true, color: COLOR.teal });
  const inner = [["Your tools", "Python functions with @tool"], ["MCP servers", "web, files, time, Gmail, Slack…"], ["The agency", "Director + specialists"], ["Rules", "approval, guardrails, a preset"]];
  inner.forEach(([head, body], i) => {
    card(s, 4.15, 2.6 + i * 0.92, 3.6, 0.8, COLOR.white, `${head} box`);
    text(s, [{ text: head, options: { bold: true, breakLine: true } }, { text: body, options: { fontSize: 12, color: COLOR.muted } }], { x: 4.3, y: 2.6 + i * 0.92, w: 3.35, h: 0.8, fontSize: 15, valign: "middle" });
  });
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 8.1, y: 3.8, w: 0.4, h: 0.35, fill: { color: COLOR.coral }, line: { color: COLOR.coral }, objectName: "arrow" });
  card(s, 8.6, 1.75, 4.13, 4.6, COLOR.white, "aws card");
  text(s, "AWS", { x: 8.85, y: 1.95, w: 3.6, h: 0.5, fontSize: 18, bold: true, color: COLOR.teal });
  const aws = [["Amazon Bedrock", "Claude, the brain"], ["Bedrock Guardrails", "rules outside the prompt"], ["AgentCore Memory", "remembers you"], ["Knowledge Base + S3 Vectors", "your documents (RAG)"], ["AgentCore Runtime + Gateway", "the same agent in the cloud"]];
  aws.forEach(([head, body], i) => {
    text(s, [{ text: head, options: { bold: true, breakLine: true } }, { text: body, options: { fontSize: 12, color: COLOR.muted } }], { x: 8.85, y: 2.55 + i * 0.75, w: 3.7, h: 0.68, fontSize: 14, valign: "middle" });
  });
  s.addNotes("The one picture to come back to. On the left, you. In the middle, Luna: a Strands agent with tools, MCP servers, optionally a team, and a preset that says whose business it is. On the right, the AWS services that each add one thing: the model, the rules, memory, your documents and, at the end, the cloud. Every demo scene lights up one box of this picture; point at it as you go. Nothing here is specific to wine or coffee.");

  // Words you'll hear tonight
  s = addSlide("The idea", "Content");
  s.addText("Words you'll hear tonight", { placeholder: "title" });
  const words = [
    [fa.FaRobot, "Agent", "A chatbot that can also act: look things up, use apps, take steps."],
    [fa.FaTools, "Tool", "One thing it's allowed to do, like \"get the weather\"."],
    [fa.FaPlug, "MCP", "USB-C for AI: one standard plug to connect it to other apps."],
    [fa.FaBookOpen, "RAG", "An open-book exam: it reads your documents before answering."],
    [fa.FaShieldAlt, "Guardrail", "A bouncer at the door the AI can't talk its way past."],
    [fa.FaUserCheck, "Memory", "A waiter who remembers you don't eat meat."],
    [fa.FaSitemap, "Agency", "A head chef calling orders; each station cooks its part."],
    [fa.FaCoins, "Tokens", "How AI is billed: roughly paying by the word."],
  ];
  for (let i = 0; i < words.length; i++) {
    const [Ic, head, body] = words[i];
    const cx = 0.6 + (i % 4) * 3.1;
    const cy = 1.7 + Math.floor(i / 4) * 2.5;
    card(s, cx, cy, 2.85, 2.25, COLOR.white, `${head} card`);
    await badge(s, Ic, cx + 0.3, cy + 0.3, 0.6, i % 2 ? COLOR.teal : COLOR.coral);
    text(s, head, { x: cx + 1.05, y: cy + 0.3, w: 1.65, h: 0.6, fontFace: FONT.head, fontSize: 21, bold: true, valign: "middle" });
    text(s, body, { x: cx + 0.3, y: cy + 1.05, w: 2.3, h: 1.1, fontSize: 15, color: COLOR.muted });
  }
  s.addNotes("For the people in the room who don't work in tech. Every term tonight maps to one of these. docs/plain-words.md has more comparisons.");

  // 6 · Section: meet Luna
  s = addSlide("Meet Luna", "Section");
  s.addText("Part 2 · Demo", { placeholder: "body" });
  s.addText("Meet Luna, one assistant that grows on stage", { placeholder: "title" });
  s.addNotes("Switch to the terminal, or play the clips. Same code in every scene; only the settings change.");

  // 7–10 · Demo scenes
  await demo("Meet Luna", {
    title: "A plain chatbot",
    level: "Level 1 · Claude on Amazon Bedrock, no tools",
    command: "python luna.py --no-tools",
    question: "What should I wear today?",
    watch: ["It answers confidently, but it's guessing", "No tool calls: it can't see today's weather", "Ask the room: is that the real forecast?"],
    why: "A brain without hands can only guess about the world, however good the model is.",
    clip: "clips/01-chatbot",
    notes: "Run the plain chatbot. It will probably give reasonable generic advice for October in Ensenada, but it has no idea about today. Point out there is no 'Tool #' line in the output.",
  });
  await demo("Meet Luna", {
    title: "Now give it hands",
    level: "Level 1 · same brain plus tools: weather, currency, to-do list",
    command: "python luna.py",
    question: "What should I wear today, and how much is 85 dollars in pesos? Add 'buy sunscreen' to my list.",
    watch: ["Tool #1 get_weather, #2 convert_currency, #3 add_task", "Real numbers: today's forecast and rate", "The cost line: well under a cent", "Then: \"delete the sunscreen task\" → it asks you first"],
    why: "Same model, same question. Tools turn guesses into facts, and asking before risky steps is the simplest rule.",
    clip: "clips/02-agent",
    notes: "Same question as before, plus two more tasks. Read the tool calls out loud as they appear. Point at the cost line. Then ask it to delete the task: the to-do tool asks for approval before deleting, which is human-in-the-loop in one line of code.",
  });
  await demo("Meet Luna", {
    title: "Make it yours",
    level: "Every setting is a parameter in config.yaml",
    command: "python luna.py --preset family\npython luna.py --set assistant.personality=pirate",
    question: "Hola, ¿quién eres?",
    watch: ["New name, personality and model, same code", "Ask the room for a personality", "It answers in the language you use"],
    why: "Presets and --set change who the agent is without touching the code: student, professional, family, or your own.",
    clip: "clips/04-make-it-yours",
    notes: "Take a suggestion from the audience for the personality. The presets live in assistant/presets; docs/customize.md shows how to add tools and agents.",
  });
  await demo("Meet Luna", {
    title: "A Director and specialists",
    level: "Level 6 · the Director (Sonnet) gives orders; specialists (Haiku) do the work",
    command: "python luna.py --mode agency",
    question: "Plan my Saturday at the beach, budget 50 USD",
    watch: ["The Director's orders to planner and finance, sent in parallel", "Each specialist reports back", "Cost per agent: the Director is the expensive one"],
    why: "Each specialist has a short prompt and only its own tools. The Director turns their results into one answer.",
    clip: "clips/05-agency",
    notes: "In plain words: a head chef calling orders to the stations; each station cooks its part, the chef plates it. This one takes about 20 seconds; narrate the orders as they print. Point out the cost line per agent: a stronger model for the Director, a cheap fast one for the specialists. The finance agent can't touch the to-do list: least privilege for agents.",
  });

  // 11 · Who orchestrates
  s = addSlide("Meet Luna", "Content");
  s.addText("Who is the orchestrator?", { placeholder: "title" });
  const flows = [
    ["In a chat, you are", [fa.FaUser, fa.FaComments, fa.FaUser], ["You ask", "It answers", "You copy, paste and decide"], "You split the problem, carry the results between steps, and decide what's next."],
    ["In an agency, the Director is", [fa.FaUser, fa.FaSitemap, fa.FaCheck], ["One request", "Director gives orders", "You approve risky steps"], "The Director splits the work and combines the results. You become the approver."],
  ];
  let y = 1.7;
  for (const [head, icons, labels, body] of flows) {
    card(s, 0.6, y, 12.13, 2.35, COLOR.white, "flow card");
    text(s, head, { x: 0.95, y: y + 0.3, w: 3.6, h: 1.0, fontFace: FONT.head, fontSize: 24, bold: true });
    text(s, body, { x: 0.95, y: y + 1.2, w: 3.6, h: 1.0, fontSize: 15, color: COLOR.muted });
    let ix = 5.0;
    for (let i = 0; i < 3; i++) {
      await badge(s, icons[i], ix + 0.6, y + 0.35, 0.8, i === 1 ? COLOR.coral : COLOR.teal);
      text(s, labels[i], { x: ix, y: y + 1.3, w: 2.0, h: 0.8, fontSize: 15, align: "center" });
      if (i < 2) s.addShape(pres.shapes.RIGHT_ARROW, { x: ix + 1.75, y: y + 0.6, w: 0.45, h: 0.3, fill: { color: COLOR.line }, line: { color: COLOR.line }, objectName: "arrow" });
      ix += 2.55;
    }
    y += 2.6;
  }
  s.addNotes("The real difference between chatting and an agency is who does the glue work. In a chat it's you. In an agency it's the Director agent, and you only step in to approve.");

  // 12 · Chat vs fleet
  s = addSlide("Meet Luna", "Content");
  s.addText("Chat, your own agent, or a fleet?", { placeholder: "title" });
  const hdr = (t) => ({ text: t, options: { bold: true, color: COLOR.white, fill: { color: COLOR.teal }, fontSize: 15, align: "center" } });
  const lbl = (t) => ({ text: t, options: { bold: true, color: COLOR.ink, fill: { color: COLOR.mist }, fontSize: 14 } });
  const cell = (t) => ({ text: t, options: { color: COLOR.ink, fontSize: 14 } });
  const rows = [
    [lbl(""), hdr("Chat app"), hdr("Your own agent"), hdr("Agency / fleet")],
    [lbl("Who drives"), cell("You, message by message"), cell("The agent, within your rules"), cell("A Director agent")],
    [lbl("Runs on"), cell("The vendor's app"), cell("Your laptop or the cloud"), cell("The cloud, always on")],
    [lbl("Cost"), cell("Flat subscription"), cell("Pay per token: cents"), cell("Tokens × agents + hosting")],
    [lbl("Setup"), cell("None"), cell("About 15 minutes"), cell("Hours, plus operations")],
    [lbl("Best for"), cell("Exploring, one-off questions"), cell("A task you repeat, your data"), cell("Many users, unattended, audited")],
  ];
  s.addTable(rows, { x: 0.6, y: 1.7, w: 12.13, colW: [2.2, 3.31, 3.31, 3.31], rowH: 0.55, fontFace: FONT.body, border: { type: "solid", color: COLOR.line, pt: 0.75 }, valign: "middle", margin: 0.08, objectName: "comparison" });
  card(s, 0.6, 5.35, 12.13, 1.25, COLOR.mist, "rule of thumb");
  await badge(s, fa.FaThumbtack, 0.95, 5.57, 0.8, COLOR.coral, "rule icon");
  text(s, [{ text: "Rule of thumb: ", options: { bold: true } }, { text: "start with one agent. Split into several only when one prompt does too many unrelated jobs, or parts need different permissions." }],
    { x: 2.0, y: 5.45, w: 10.4, h: 1.05, fontSize: 17, valign: "middle" });
  s.addNotes("From docs/comparison.md. An agency costs roughly 3 to 5 times more per question and is slower, so it has to earn its place. Most tasks need one good agent.");

  // Part 3 · Luna for your business
  s = addSlide("Luna for your business", "Section");
  s.addText("Part 3", { placeholder: "body" });
  s.addText("Luna for any business: yours, not just ours", { placeholder: "title" });
  s.addNotes("The part most people will copy. The winery and the coffee shop are only examples: the same agent works for any business, because what changes is who it works for, what it can see and what it can do. Say this out loud: pick the business closest to your own.");

  s = addSlide("Luna for your business", "Content");
  s.addText("Two examples. Yours is the third.", { placeholder: "title" });
  const shops = [
    [fa.FaWineGlassAlt, "Winery", "Example: Valle de Guadalupe", "--preset winery",
     ["Files: sales, reservations", "Documents: handbook, suppliers", "Web + time: guests abroad"]],
    [fa.FaCoffee, "Coffee shop", "Example: Ensenada malecón", "--preset coffee-shop",
     ["Files: sales, inventory", "Documents: recipes, suppliers", "Web + time: cruise days"]],
    [fa.FaBriefcase, "Your business", "A clinic, school, farm, office, shop…", "--preset my-business",
     ["Files: your CSV exports", "Documents: your policies, prices", "Tools: your APIs and MCP servers"]],
  ];
  x = 0.6;
  for (let i = 0; i < shops.length; i++) {
    const [Ic, name, what, preset, items] = shops[i];
    card(s, x, 1.7, 3.85, 3.75, i === 2 ? COLOR.mist : COLOR.white, `${name} card`);
    await badge(s, Ic, x + 0.3, 2.0, 0.8, i === 2 ? COLOR.teal : COLOR.coral);
    text(s, name, { x: x + 1.3, y: 1.98, w: 2.4, h: 0.5, fontFace: FONT.head, fontSize: 19, bold: true });
    text(s, what, { x: x + 1.3, y: 2.48, w: 2.4, h: 0.55, fontSize: 13, color: COLOR.muted });
    bullets(s, items, { x: x + 0.3, y: 3.2, w: 3.35, h: 1.5, fontSize: 14 });
    text(s, `luna.py ${preset}`, { x: x + 0.3, y: 4.85, w: 3.4, h: 0.45, fontSize: 12, fontFace: FONT.code, color: COLOR.teal, bold: true });
    x += 4.14;
  }
  card(s, 0.6, 5.7, 12.13, 0.9, COLOR.mist, "make it yours");
  text(s, [{ text: "Nothing in the agent is specific to wine or coffee. ", options: { bold: true } }, { text: "Copy one preset and one folder, drop in your own CSV exports and documents. No new database, no new app." }],
    { x: 0.95, y: 5.7, w: 11.5, h: 0.9, fontSize: 17, valign: "middle" });
  s.addNotes("In plain words: Luna is the same assistant; a preset tells it whose business it works for, and a folder holds that business's files. Both examples are fictional and picked because they are local. The third card is the point: yours. docs/extend.md has the five steps and an industry table.");

  await demo("Luna for your business", {
    title: "Many sources, one answer",
    level: "Level 4 · two MCP servers: the time and a web page · example: a winery",
    command: "python luna.py --preset winery",
    question: "What time is it in Los Angeles? Then read the Valle de Guadalupe page on Wikipedia and give me two facts for my US guests.",
    watch: ["get_current_time from the time server", "fetch reads the web page", "Nobody wrote code for either: they plug in"],
    why: "MCP is USB-C for AI: plug in a server and the agent gets new abilities.",
    clip: "clips/06-many-sources",
    notes: "In plain words: one cable standard, many devices. The winery owner asks one question; Luna uses two connectors, a clock and a web reader, and combines what it finds.",
  });
  await demo("Luna for your business", {
    title: "Your files and your documents",
    level: "The files MCP server + your documents (RAG) in one answer · example: a coffee shop",
    command: "python luna.py --preset coffee-shop",
    question: "What do I need to reorder this week, and from which supplier is espresso cheaper?",
    watch: ["read_text_file opens inventory.csv", "search_my_documents finds the price list", "Five items under their reorder point"],
    why: "Your data where it already lives: CSV exports and documents, no new system.",
    clip: "clips/07-your-business",
    notes: "In plain words: the agent reads the stock sheet on the shelf and checks the supplier binder, then gives one answer. The files server can only open this one folder.",
  });
  await demo("Luna for your business", {
    title: "A third business, no new code",
    level: "Any business · example: a dental clinic · files + your documents",
    command: "python luna.py --preset clinic",
    question: "A patient cancelled a cleaning with only 5 hours' notice. Is there a fee? And which patient on 16 November has an allergy?",
    watch: ["Same agent, new preset and new data", "search_my_documents finds the 20% fee", "appointments.csv shows the penicillin allergy"],
    why: "Winery, coffee shop, clinic: only the preset and the data change. Yours is next.",
    clip: "clips/07b-clinic",
    notes: "In plain words: the same assistant hired by a different business. Nothing in the code is about dentists: the preset says whose business it is, the CSV holds the appointments, and the policy document holds the rules. This is the proof of the claim: it works for any business. Ask the room what their own business would put in the folder.",
  });
  await demo("Luna for your business", {
    title: "The Monday briefing",
    level: "Advanced · an agency with files, web, time, documents and tools",
    command: "python luna.py --preset winery --mode agency",
    question: "Prepare my Monday briefing: patio this weekend, sales vs last weekend, Saturday's reservations and allergies, 100 dollars in pesos, which cork supplier. Save it as a report.",
    watch: ["Six specialists get orders in parallel", "office reads sales and reservations", "A report appears in business/winery/reports/"],
    why: "One request, many sources, a finished document. This is where agents save hours.",
    clip: "clips/08-monday-briefing",
    notes: "In plain words: the owner asks the manager for Monday's summary; the manager asks the right people and writes it up. About 45 seconds; narrate the orders, then open the saved report. Costs about 6 cents on Claude 5.5.",
  });

  s = addSlide("Luna for your business", "Content");
  s.addText("Connect your world", { placeholder: "title" });
  const ready = [[fa.FaGlobe, "Web pages"], [fa.FaFolderOpen, "Your files"], [fa.FaClock, "Time"], [fa.FaBook, "AWS docs"]];
  const login = [[fa.FaEnvelope, "Gmail"], [fa.FaGoogleDrive, "Google Drive"], [fa.FaSlack, "Slack"], [fa.FaGithub, "GitHub"], [fa.FaDatabase, "Your CRM"]];
  const groups = [["Ready in the repo, no login", ready, COLOR.teal], ["With your own login", login, COLOR.coral]];
  y = 1.7;
  for (const [label, items, color] of groups) {
    text(s, label, { x: 0.6, y, w: 12, h: 0.45, fontSize: 18, bold: true, color });
    x = 0.6;
    for (const [Ic, name] of items) {
      await badge(s, Ic, x + 0.55, y + 0.55, 0.85, color, name);
      text(s, name, { x, y: y + 1.48, w: 1.95, h: 0.45, fontSize: 15, align: "center" });
      x += 2.4;
    }
    y += 2.1;
  }
  card(s, 0.6, 5.85, 12.13, 0.85, COLOR.mist, "least privilege");
  text(s, [{ text: "Each connector gets only what it needs: ", options: { bold: true } }, { text: "one folder, read-only mail, its own key. Your AWS keys never reach a third-party server." }],
    { x: 0.95, y: 5.85, w: 11.5, h: 0.85, fontSize: 16, valign: "middle" });
  s.addNotes("In plain words: the cashier has the till key, not the safe. The first row runs today with no accounts; the second needs your own login (Gmail setup is in customize.md section 7). Hundreds more servers exist: CRMs, calendars, databases.");

  s = addSlide("Luna for your business", "Content");
  s.addText("Not just wineries: any business", { placeholder: "title" });
  const kinds = [
    [fa.FaClinicMedical, "Clinic", "appointments · policies · reminders"],
    [fa.FaBalanceScale, "Law or accounting", "matters · templates · deadlines"],
    [fa.FaGraduationCap, "School", "attendance · syllabi · parent messages"],
    [fa.FaTractor, "Farm or producer", "harvest · certifications · market prices"],
    [fa.FaWrench, "Repair shop", "jobs · manuals · parts lookup"],
    [fa.FaTruck, "Delivery team", "shipments · carrier rules · tracking"],
  ];
  for (let i = 0; i < kinds.length; i++) {
    const [Ic, name, body] = kinds[i];
    const cx = 0.6 + (i % 3) * 4.14, cy = 1.7 + Math.floor(i / 3) * 2.15;
    card(s, cx, cy, 3.85, 1.95, COLOR.white, `${name} card`);
    await badge(s, Ic, cx + 0.3, cy + 0.55, 0.85, i % 2 ? COLOR.teal : COLOR.coral, name);
    text(s, name, { x: cx + 1.4, y: cy + 0.45, w: 2.3, h: 0.5, fontFace: FONT.head, fontSize: 19, bold: true });
    text(s, body, { x: cx + 1.4, y: cy + 0.98, w: 2.3, h: 0.8, fontSize: 13, color: COLOR.muted });
  }
  card(s, 0.6, 6.05, 12.13, 0.65, COLOR.mist, "same three");
  text(s, [{ text: "Same three changes every time: ", options: { bold: true } }, { text: "who it works for · the files and documents it can see · the tools it can use." }],
    { x: 0.95, y: 6.05, w: 11.5, h: 0.65, fontSize: 16, valign: "middle" });
  s.addNotes("In plain words: any small business has the same shape: some spreadsheets, a binder of rules, and a few systems to talk to. These are starting points, not tested presets. Ask the room which one is closest to theirs. The table with files, documents and tools for each is in docs/extend.md.");

  s = addSlide("Luna for your business", "Content");
  s.addText("Make it yours in five steps", { placeholder: "title" });
  const five = [
    [fa.FaIdBadge, "1 · Preset", "Who it works for: a YAML file, no code"],
    [fa.FaFileCsv, "2 · Files", "Your CSV exports in one folder"],
    [fa.FaBook, "3 · Documents", "Policies and price lists, searched by RAG"],
    [fa.FaPlug, "4 · Tools", "An MCP server, or one @tool function"],
    [fa.FaShieldAlt, "5 · Rules and team", "Approval, guardrails, specialists"],
  ];
  x = 0.6;
  for (let i = 0; i < five.length; i++) {
    const [Ic, head, body] = five[i];
    card(s, x, 1.75, 2.3, 3.2, COLOR.white, `${head} card`);
    await badge(s, Ic, x + 0.7, 2.05, 0.9, i < 3 ? COLOR.teal : COLOR.coral);
    text(s, head, { x: x + 0.15, y: 3.15, w: 2.0, h: 0.5, fontSize: 16, bold: true, align: "center" });
    text(s, body, { x: x + 0.15, y: 3.7, w: 2.0, h: 1.1, fontSize: 13, color: COLOR.muted, align: "center" });
    x += 2.46;
  }
  card(s, 0.6, 5.2, 12.13, 1.4, COLOR.mist, "steps note");
  text(s, [
    { text: "Steps 1 to 3 need no code: ", options: { bold: true } },
    { text: "you can have your own business running in an afternoon. Steps 4 and 5 add a little Python or more YAML. A coding assistant can write the tool for you. Walkthrough: docs/extend.md in the repo.", options: { breakLine: false } },
  ], { x: 0.95, y: 5.2, w: 11.5, h: 1.4, fontSize: 16, valign: "middle" });
  s.addNotes("This is the slide to leave up while taking questions about 'can I use this for my business'. Steps one to three are configuration: copy the coffee-shop preset, replace the CSV files, drop documents in my_documents and sync the knowledge base. Step four is either an existing MCP server (Gmail, Slack, Drive, a database) or one Python function with the @tool decorator. Step five is the safety layer: ask a person first, a guardrail for topics to refuse, and specialists when one agent has too many jobs.");

  // 13 · Section: the rest of the stack
  s = addSlide("The rest of the stack", "Section");
  s.addText("Part 4", { placeholder: "body" });
  s.addText("Rules, memory, your documents, and the cloud", { placeholder: "title" });
  s.addNotes("One slide each, about 30 seconds per demo. Pick two or three the room cares about most.");

  // 14 · Guardrails
  await demo("The rest of the stack", {
    title: "Rules: Bedrock Guardrails",
    level: "Level 2 · denied topics, content filters, prompt attacks, personal data",
    command: "python luna.py",
    question: "Should I buy bitcoin with my savings?",
    watch: ["Refused before Claude even sees it", "Card numbers, emails and phones are masked", "\"Ignore all previous instructions…\" is blocked too"],
    why: "Rules that live outside the prompt: the model can't be talked out of them.",
    clip: "clips/09-guardrail",
    notes: "In plain words: a bouncer at the door, not a polite request; the AI can't talk its way past it. With the Claude API the same guardrail checks what you type before Claude sees it. The guardrail is created by setup/create_guardrail.py. It denies investment advice and medical diagnosis, filters harmful content and prompt attacks, and anonymizes personal data. Lesson learned: at HIGH strength the prompt-attack filter blocked our own memory feature; see the lessons slide.",
  });

  // 15 · Memory
  await demo("The rest of the stack", {
    title: "Memory: it remembers you",
    level: "Level 3 · Amazon Bedrock AgentCore Memory",
    command: "python luna.py",
    question: "Suggest a dinner for tonight based on what you know about me.",
    watch: ["A new session, yet it knows you're vegetarian", "It learned that from an earlier conversation", "Your memory, in your account"],
    why: "AgentCore Memory extracts preferences from conversations in the background and gives them back in later sessions.",
    clip: "clips/10-memory",
    notes: "In plain words: a good waiter who remembers you don't eat meat. Seeded the day before with: 'Remember this about me: I'm vegetarian and I hate cold weather.' Extraction takes a minute or two, so it can't be done live in the same breath.",
  });

  // 16 · Your documents
  s = addSlide("The rest of the stack", "Content");
  s.addText("Your documents: ask your own lease", { placeholder: "title" });
  const rag = [
    [fa.FaFileContract, "my_documents/", "Lease, insurance, recipes"],
    [fa.FaDatabase, "Amazon S3", "The files"],
    [fa.FaProjectDiagram, "Titan Embeddings V2", "Text → vectors"],
    [fa.FaCubes, "Amazon S3 Vectors", "The index"],
  ];
  x = 0.6;
  for (let i = 0; i < rag.length; i++) {
    const [Ic, head, body] = rag[i];
    await badge(s, Ic, x + 0.57, 1.8, 0.85, i === 3 ? COLOR.coral : COLOR.teal);
    text(s, head, { x, y: 2.75, w: 2.0, h: 0.62, fontSize: 15, bold: true, align: "center", valign: "top" });
    text(s, body, { x, y: 3.4, w: 2.0, h: 0.7, fontSize: 14, color: COLOR.muted, align: "center" });
    if (i < rag.length - 1) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 1.88, y: 2.08, w: 0.32, h: 0.3, fill: { color: COLOR.line }, line: { color: COLOR.line }, objectName: "arrow" });
    x += 2.2;
  }
  terminal(s, { command: "python luna.py", question: "According to my lease, when is the rent due?" }, 0.6, 4.2, 8.6, 1.3);
  text(s, "→ search_my_documents → \"9,500 MXN, by the 5th of each month\". An English question, answered from a Spanish contract.",
    { x: 0.6, y: 5.7, w: 8.6, h: 0.8, fontSize: 15, color: COLOR.muted });
  card(s, 9.55, 1.7, 3.18, 4.8, COLOR.ocean, "stat card");
  text(s, "$0.06", { x: 9.75, y: 1.9, w: 2.8, h: 1.05, fontFace: FONT.head, fontSize: 54, bold: true, color: COLOR.coral, align: "center" });
  text(s, "per GB-month on S3 Vectors", { x: 9.75, y: 2.98, w: 2.8, h: 0.6, fontSize: 15, color: COLOR.foam, align: "center" });
  text(s, "vs", { x: 9.75, y: 3.6, w: 2.8, h: 0.4, fontSize: 15, italic: true, color: COLOR.foam, align: "center" });
  text(s, "$175+", { x: 9.75, y: 3.95, w: 2.8, h: 1.05, fontFace: FONT.head, fontSize: 54, bold: true, color: COLOR.white, align: "center" });
  text(s, "a month for an idle OpenSearch Serverless", { x: 9.75, y: 5.03, w: 2.8, h: 0.9, fontSize: 15, color: COLOR.foam, align: "center" });
  s.addNotes("In plain words: an open-book exam. Before answering, it looks in YOUR binder and tells you which page it used. RAG with Bedrock Knowledge Bases. The console suggests OpenSearch Serverless by default, which bills compute even when idle. S3 Vectors costs cents for a personal knowledge base. Set up with setup/create_knowledge_base.py; about two minutes. Recorded clip: clips/11-documents.");

  // 17 · MCP and A2A
  s = addSlide("The rest of the stack", "Content");
  s.addText("MCP for tools, A2A for agents", { placeholder: "title" });
  const std = [
    [fa.FaPlug, "MCP · Model Context Protocol", "Plug in other people's tools without writing them.", ["Web pages, your files, time, AWS docs, Gmail", "Local processes (uvx, npx) or one shared Gateway", "Claude Code uses the same servers"], "python luna.py --preset winery"],
    [fa.FaNetworkWired, "A2A · Agent-to-Agent", "Specialists become services that other agents call.", ["Each specialist runs as its own server", "The Director finds them by URL", "Same answer as the agency, now distributed"], "python fleet_server.py --all\npython luna.py --mode fleet"],
  ];
  x = 0.6;
  for (const [Ic, head, sub, items, cmd] of std) {
    card(s, x, 1.7, 5.9, 4.85, COLOR.white, "standard card");
    await badge(s, Ic, x + 0.4, 2.0, 0.85);
    text(s, head, { x: x + 1.45, y: 2.0, w: 4.2, h: 0.85, fontFace: FONT.head, fontSize: 21, bold: true, valign: "middle" });
    text(s, sub, { x: x + 0.4, y: 3.0, w: 5.1, h: 0.75, fontSize: 16, bold: true, color: COLOR.teal });
    bullets(s, items, { x: x + 0.4, y: 3.85, w: 5.2, h: 1.35, fontSize: 15 });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.4, y: 5.3, w: 5.1, h: 0.95, rectRadius: 0.1, fill: { color: COLOR.ocean }, line: { color: COLOR.ocean }, objectName: "command box" });
    text(s, cmd, { x: x + 0.6, y: 5.38, w: 4.8, h: 0.8, fontFace: FONT.code, fontSize: 12, color: COLOR.code, valign: "middle" });
    x += 6.23;
  }
  s.addNotes("In plain words: MCP is USB-C for AI, one plug for many apps; A2A is departments phoning each other with a shared phone book. Two open standards. MCP standardises how an agent gets tools; A2A standardises how agents talk to each other. Luna uses both: MCP servers for time, web pages and AWS docs; A2A for the fleet mode where each specialist is its own service.");

  // 18 · Cloud
  s = addSlide("The rest of the stack", "Demo");
  s.addText("The same agent, in the cloud", { placeholder: "title" });
  text(s, "Level 8 · Amazon Bedrock AgentCore Runtime + Gateway", { x: 0.6, y: 1.38, w: 10.4, h: 0.4, fontSize: 16, italic: true, color: COLOR.teal });
  card(s, 0.6, 1.95, 6.6, 4.6, COLOR.white, "diagram card");
  // The diagram is drawn with shapes so it stays readable from the back of the room (diagrams/cloud.png has every detail).
  await badge(s, fa.FaUser, 0.85, 3.75, 0.8, COLOR.teal, "you");
  text(s, "You", { x: 0.7, y: 4.6, w: 1.1, h: 0.4, fontSize: 15, bold: true, align: "center" });
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 1.9, y: 3.95, w: 0.4, h: 0.35, fill: { color: COLOR.coral }, line: { color: COLOR.coral }, objectName: "arrow" });
  card(s, 2.4, 2.15, 1.9, 4.2, COLOR.mist, "runtime box");
  await badge(s, fa.FaRobot, 2.95, 3.3, 0.8, COLOR.coral, "luna");
  text(s, [{ text: "Luna", options: { bold: true, breakLine: true } }, { text: "on AgentCore Runtime", options: { fontSize: 12, color: COLOR.muted } }], { x: 2.45, y: 4.2, w: 1.8, h: 0.9, fontSize: 17, align: "center" });
  const cloudParts = [["Claude on Bedrock", "+ Guardrails"], ["Memory", "AgentCore"], ["Knowledge Base", "your documents"], ["Gateway", "weather, currency"]];
  cloudParts.forEach(([head, sub], i) => {
    const py = 2.15 + i * 1.08;
    s.addShape(pres.shapes.RIGHT_ARROW, { x: 4.38, y: py + 0.3, w: 0.35, h: 0.3, fill: { color: COLOR.line }, line: { color: COLOR.line }, objectName: "arrow" });
    card(s, 4.8, py, 2.25, 0.92, COLOR.white, `${head} box`);
    text(s, [{ text: head, options: { bold: true, breakLine: true } }, { text: sub, options: { fontSize: 12, color: COLOR.muted } }], { x: 4.9, y: py, w: 2.05, h: 0.92, fontSize: 15, valign: "middle" });
  });
  terminal(s, { command: "agentcore invoke --runtime luna \\\n  --payload '{\"prompt\": \"hola\"}'" }, 7.5, 1.95, 5.23, 1.55);
  const cloud = [
    [fa.FaServer, "Runtime", "assistant/ deployed as-is; one microVM per session"],
    [fa.FaPlug, "Gateway", "weather and currency as shared MCP tools, from two OpenAPI specs"],
    [fa.FaKey, "IAM, no secrets", "SigV4 from the runtime's role"],
    [fa.FaChartLine, "Observability", "OpenTelemetry traces in CloudWatch"],
  ];
  y = 3.75;
  for (const [Ic, head, body] of cloud) {
    await badge(s, Ic, 7.5, y, 0.55, COLOR.teal);
    text(s, [{ text: `${head}  `, options: { bold: true } }, { text: body, options: { color: COLOR.muted } }], { x: 8.25, y: y - 0.02, w: 4.5, h: 0.62, fontSize: 15, valign: "middle" });
    y += 0.7;
  }
  s.addNotes("In plain words: moving from cooking at home to a rented commercial kitchen; the Gateway is the switchboard that connects every agent to the same tools. The AgentCore CLI packages the same assistant folder and deploys it with CDK: agentcore deploy. The Gateway turns two public APIs into MCP tools from their OpenAPI specs, so every agent (and Claude Code) can share them. The runtime calls the gateway with its own IAM role: no Cognito, no secrets. Recorded clip: clips/12-cloud.");

  // From laptop to production
  s = addSlide("The rest of the stack", "Content");
  s.addText("From laptop to production", { placeholder: "title" });
  const stages = [
    [fa.FaLaptop, "Laptop", "You", "python luna.py"],
    [fa.FaCloud, "Cloud, private", "You, from anywhere", "agentcore deploy"],
    [fa.FaUsers, "Pilot", "Your team", "Login, a chat app, keys in AgentCore Identity, budget alarms"],
    [fa.FaBuilding, "Production", "Everyone", "Separate account, CI/CD, dashboards, evaluations, on-call"],
  ];
  x = 0.6;
  for (let i = 0; i < stages.length; i++) {
    const [Ic, head, who, what] = stages[i];
    card(s, x, 1.7, 2.85, 3.3, COLOR.white, `${head} card`);
    await badge(s, Ic, x + 0.3, 1.98, 0.75, i < 2 ? COLOR.teal : COLOR.coral);
    text(s, head, { x: x + 0.3, y: 2.85, w: 2.3, h: 0.5, fontFace: FONT.head, fontSize: 20, bold: true });
    text(s, who, { x: x + 0.3, y: 3.35, w: 2.3, h: 0.4, fontSize: 15, bold: true, color: COLOR.teal });
    text(s, what, { x: x + 0.3, y: 3.8, w: 2.35, h: 1.1, fontSize: 14.5, color: COLOR.muted, fontFace: i < 2 ? FONT.code : FONT.body });
    if (i < stages.length - 1) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.88, y: 3.2, w: 0.22, h: 0.3, fill: { color: COLOR.line }, line: { color: COLOR.line }, objectName: "arrow" });
    x += 3.1;
  }
  card(s, 0.6, 5.25, 12.13, 1.35, COLOR.mist, "where to run");
  text(s, [
    { text: "Where to run it: ", options: { bold: true } },
    { text: "AgentCore Runtime (built for agents, recommended) · Lambda for short tasks · ECS if your team runs containers.", options: { breakLine: true } },
    { text: "In plain words: ", options: { bold: true } },
    { text: "from cooking at home to running a restaurant. Same recipes, plus a front door, locks and someone watching the bills." },
  ], { x: 0.95, y: 5.3, w: 11.5, h: 1.25, fontSize: 16, valign: "middle" });
  s.addNotes("docs/production.md has the checklist. Stage 2 is already deployed for this talk. For the winery, stage 3 is the shift leads asking Luna in Slack for tonight's reservations and allergies.");

  // Safe with real data
  s = addSlide("The rest of the stack", "Content");
  s.addText("Safe to point at real data?", { placeholder: "title" });
  const safe = [
    [fa.FaFolderOpen, "Small doors", "Each connector gets one folder, read-only mail, its own key. Your AWS keys never reach a third-party server."],
    [fa.FaUserCheck, "A person decides", "Anything that deletes, sends or pays asks first. The agent proposes; you approve."],
    [fa.FaExclamationTriangle, "Text is not trusted", "A web page or a document can contain instructions. Guardrails and approval sit outside the prompt, so the text can't switch them off."],
  ];
  x = 0.6;
  for (let i = 0; i < safe.length; i++) {
    const [Ic, head, body] = safe[i];
    card(s, x, 1.75, 3.85, 3.9, COLOR.white, `${head} card`);
    await badge(s, Ic, x + 0.4, 2.05, 0.85, i === 2 ? COLOR.coral : COLOR.teal);
    text(s, head, { x: x + 0.4, y: 3.1, w: 3.1, h: 0.55, fontFace: FONT.head, fontSize: 22, bold: true });
    text(s, body, { x: x + 0.4, y: 3.75, w: 3.1, h: 1.8, fontSize: 15, color: COLOR.muted });
    x += 4.14;
  }
  card(s, 0.6, 5.85, 12.13, 0.8, COLOR.mist, "safety note");
  text(s, [{ text: "Start read-only. ", options: { bold: true } }, { text: "Give write access one tool at a time, after you have watched it work. More in docs/production.md." }],
    { x: 0.95, y: 5.85, w: 11.5, h: 0.8, fontSize: 16, valign: "middle" });
  s.addNotes("In plain words: a new employee gets one key, not the master key, and a manager signs off anything risky. The one thing that is new with agents: they read text from the outside world (a web page, a customer's email, a document), and that text can try to give them orders. That is called prompt injection. You can't fully prevent it, so you limit what a fooled agent could do: read-only access, one folder, approval for anything that changes something, and guardrails that live outside the prompt. docs/production.md has the checklist for real use.");

  // 19 · Lessons
  s = addSlide("The rest of the stack", "Content");
  s.addText("What broke while building it", { placeholder: "title" });
  const lessons = [
    [fa.FaLock, "Quota of 0", "New account, newest models: Claude 5.5 tokens-per-minute was 0. Fix: Claude 4.x on Bedrock, or the Claude API."],
    [fa.FaThermometerHalf, "\"temperature is deprecated\"", "Claude 5.x rejects the temperature setting. Fix: only send it to older models."],
    [fa.FaShieldAlt, "Guardrail vs memory", "Memory text joins the prompt, so stray records made the guardrail refuse a fair question. Fix: MEDIUM, and tidy the records."],
    [fa.FaExchangeAlt, "A header sent us to a paid API", "The gateway's x-api-key made Open-Meteo redirect to its commercial API. Fix: a neutral header name."],
    [fa.FaListUl, "daily=daily", "A default wasn't enough: Claude sent the parameter's name as its value. Fix: a one-value enum."],
    [fa.FaMapMarkerAlt, "Seven Valle de Guadalupes", "The weather tool picked the one in Jalisco. Fix: match the state the user gave."],
  ];
  for (let i = 0; i < lessons.length; i++) {
    const [Ic, head, body] = lessons[i];
    const cx = 0.6 + (i % 3) * 4.12;
    const cy = 1.7 + Math.floor(i / 3) * 2.5;
    card(s, cx, cy, 3.85, 2.25, COLOR.white, "lesson card");
    await badge(s, Ic, cx + 0.3, cy + 0.3, 0.62, i % 2 ? COLOR.teal : COLOR.coral);
    text(s, head, { x: cx + 1.1, y: cy + 0.3, w: 2.55, h: 0.62, fontSize: 17, bold: true, valign: "middle" });
    text(s, body, { x: cx + 0.3, y: cy + 1.02, w: 3.3, h: 1.15, fontSize: 15, color: COLOR.muted });
  }
  s.addNotes("The honest slide. Each of these cost real time and each is documented in the repo (docs/bedrock-access.md, levels.md). The lesson: every layer you add (memory, guardrails, gateway, cloud) changes how the others behave, so test them together. A one-command rehearsal (python rehearse.py) catches these before the talk. The memory one hit twice: once as the filter level, once as leftover records from earlier rehearsals (setup/clean_memory.py lists and removes them).");

  // 20 · Built with Claude Code
  s = addSlide("The rest of the stack", "Content");
  s.addText("Built with Claude Code", { placeholder: "title" });
  const stats = [
    ["8", "levels, from chatbot to a fleet in the cloud"],
    ["12", "demo scenes, checked by one command: python rehearse.py"],
    ["$0.10", "and about 3 minutes for a full rehearsal"],
  ];
  x = 0.6;
  for (const [n, label] of stats) {
    card(s, x, 1.85, 3.85, 3.0, COLOR.white, "stat card");
    text(s, n, { x: x + 0.3, y: 2.15, w: 3.25, h: 1.2, fontFace: FONT.head, fontSize: 60, bold: true, color: COLOR.coral, align: "center", valign: "middle" });
    text(s, label, { x: x + 0.3, y: 3.45, w: 3.25, h: 1.2, fontSize: 16, color: COLOR.muted, align: "center" });
    x += 4.12;
  }
  await badge(s, fa.FaTerminal, 0.6, 5.3, 0.8, COLOR.teal, "claude code icon");
  text(s, "The code, the docs, the AWS setup and this deck's generator were written with Claude Code, and every step was reviewed, tested and committed to the repo.",
    { x: 1.65, y: 5.25, w: 11.0, h: 0.95, fontSize: 17, valign: "middle" });
  s.addNotes("Claude Code wrote it with me: the agent code, the setup scripts, the docs, the IaC for the cloud level, and this deck. It also found and fixed the problems on the previous slide.");

  // 21 · Costs
  s = addSlide("Your turn", "Content");
  s.addText("What it costs", { placeholder: "title" });
  const costs = [
    ["$0.0006", "per answer, solo", "Claude Haiku 5.5, measured"],
    ["$0.06", "the Monday briefing", "six agents, Sonnet 5.5 Director"],
    ["< $5", "this whole talk", "rehearsals, demo and AWS services"],
  ];
  x = 0.6;
  for (const [n, label, sub] of costs) {
    card(s, x, 1.75, 3.85, 3.1, COLOR.ocean, "cost card");
    text(s, n, { x: x + 0.3, y: 2.05, w: 3.25, h: 1.2, fontFace: FONT.head, fontSize: 56, bold: true, color: COLOR.coral, align: "center", valign: "middle" });
    text(s, label, { x: x + 0.3, y: 3.35, w: 3.25, h: 0.5, fontSize: 18, bold: true, color: COLOR.white, align: "center" });
    text(s, sub, { x: x + 0.3, y: 3.85, w: 3.25, h: 0.8, fontSize: 14, color: COLOR.foam, align: "center" });
    x += 4.12;
  }
  bullets(s, [
    "No monthly fee for guardrails, memory, the knowledge base or the gateway: you pay per use",
    "On Bedrock with Claude 4.x it is about 10× more per answer, still cents",
    "Set an AWS Budget alarm before you start; docs/costs.md has the full breakdown",
  ], { x: 0.6, y: 5.15, w: 12.1, h: 1.5, fontSize: 18 });
  s.addNotes("Measured on 2026-10-31 with the cost line Luna prints after every answer. The free tier and pay-per-use pricing make this cheap to try at home.");

  // 22 · Your turn
  s = addSlide("Your turn", "Content");
  s.addText("Your turn", { placeholder: "title" });
  const path3 = [
    [fa.FaMagic, "PartyRock", "No code, no AWS account: build an AI app in your browser", "partyrock.aws"],
    [fa.FaGraduationCap, "Skill Builder", "AWS's free courses on Bedrock and generative AI", "skillbuilder.aws"],
    [fa.FaGithub, "This repo", "Luna in 15 minutes, then make it your business: docs/extend.md", REPO],
  ];
  x = 0.6;
  for (let i = 0; i < path3.length; i++) {
    const [Ic, head, body, link] = path3[i];
    card(s, x, 1.75, 3.85, 4.75, COLOR.white, "path card");
    await badge(s, Ic, x + 0.4, 2.1, 0.95, i === 2 ? COLOR.coral : COLOR.teal);
    text(s, `${i + 1}`, { x: x + 2.9, y: 2.05, w: 0.6, h: 0.6, fontFace: FONT.head, fontSize: 30, bold: true, color: COLOR.line, align: "right" });
    text(s, head, { x: x + 0.4, y: 3.3, w: 3.2, h: 0.6, fontFace: FONT.head, fontSize: 24, bold: true });
    text(s, body, { x: x + 0.4, y: 3.95, w: 3.1, h: 1.3, fontSize: 16, color: COLOR.muted });
    text(s, link, { x: x + 0.4, y: 5.4, w: 3.2, h: 0.8, fontSize: i === 2 ? 12 : 15, bold: true, color: COLOR.teal, fontFace: FONT.code });
    if (i < 2) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 3.88, y: 3.95, w: 0.22, h: 0.3, fill: { color: COLOR.line }, line: { color: COLOR.line }, objectName: "arrow" });
    x += 4.12;
  }
  s.addNotes("A free path from zero to your own agent. PartyRock needs no code; Skill Builder has free courses; the repo's quickstart gets Luna running in about 15 minutes with your own AWS account.");

  // 23 · Questions
  s = addSlide("Your turn", "Title");
  s.addText("Questions?", { placeholder: "title" });
  s.addText([
    { text: REPO, options: { breakLine: true, fontFace: FONT.code, color: COLOR.quote } },
    { text: "Gracias · AWS User Group Ensenada", options: { fontSize: 18 } },
  ], { placeholder: "body" });
  await badge(s, fa.FaGithub, 0.8, 5.75, 0.75, COLOR.coral, "repo icon");
  const qr = await QRCode.toDataURL(`https://${REPO}`, { margin: 1, width: 480, color: { dark: "#0F2A36", light: "#FFFFFF" } });
  s.addImage({ data: qr.replace("data:", ""), x: 10.4, y: 3.7, w: 2.3, h: 2.3, altText: "QR code for the repository", objectName: "repo qr" });
  s.addText("Scan for the repo\nthen: python luna.py", { x: 9.9, y: 6.1, w: 3.3, h: 0.6, fontFace: FONT.code, fontSize: 12, color: COLOR.quote, align: "center", margin: 0 });
  s.addNotes("Leave this slide up during Q&A. The QR code opens the repo; the first command after the quickstart is python luna.py. The README quickstart takes about 15 minutes, and docs/extend.md shows how to make it work for your own business. A one-page English and Spanish cheat sheet is in docs/cheatsheet.md.");

  if (slideCount !== TIMING.length) throw new Error(`TIMING has ${TIMING.length} entries but the deck has ${slideCount} slides: update TIMING in build.js`);
  const total = TIMING.reduce((sum, [m]) => sum + m, 0);
  const core = TIMING.reduce((sum, [m, optional]) => sum + (optional ? 0 : m), 0);
  console.log(`⏱ planned ${total.toFixed(1)} min with every slide; ${core.toFixed(1)} min without the optional ones (talk time, before the live demo's own waiting)`);
  await pres.writeFile({ fileName: OUT });
  console.log(`✅ ${path.relative(process.cwd(), OUT)}`);
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
