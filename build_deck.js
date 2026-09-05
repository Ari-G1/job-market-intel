const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5

// ---- palette ---------------------------------------------------------------
const NAVY = "1E2761";
const ICE = "CADCFC";
const WHITE = "FFFFFF";
const INK = "1A1A2E";
const MUT = "5A6070";
const LIGHT = "F4F6FB";
const GREEN = "2E7D32"; // required
const AMBER = "B8860B"; // preferred
const GREY = "7A7F87"; // boilerplate
const RED = "B23A3A"; // wrong / baseline miss

const HEAD = "Cambria";
const BODY = "Calibri";
const W = 13.33;

// ---- helpers ---------------------------------------------------------------
function titleBar(slide, text, kicker) {
  if (kicker) {
    slide.addText(kicker.toUpperCase(), {
      isTextBox: true, x: 0.6, y: 0.45, w: 12.1, h: 0.3,
      fontFace: BODY, fontSize: 12, bold: true, color: AMBER, charSpacing: 2, margin: 0,
    });
  }
  slide.addText(text, {
    isTextBox: true, x: 0.6, y: kicker ? 0.75 : 0.5, w: 12.1, h: 0.9,
    fontFace: HEAD, fontSize: 32, bold: true, color: NAVY, margin: 0,
  });
}

function chip(slide, text, x, y, w, fill) {
  slide.addText(text, {
    isTextBox: true, shape: pres.ShapeType.roundRect, rectRadius: 0.06,
    x, y, w, h: 0.4, fill: { color: fill }, color: WHITE,
    fontFace: BODY, fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0,
  });
}

// layout a row-wrapped set of chips inside a band; returns next y
function chipBlock(slide, items, x0, y0, fill, maxX) {
  let x = x0, y = y0;
  const h = 0.4, gap = 0.12;
  for (const it of items) {
    const w = Math.max(0.9, 0.22 + it.length * 0.105);
    if (x + w > maxX) { x = x0; y += h + gap; }
    chip(slide, it, x, y, w, fill);
    x += w + gap;
  }
  return y + h;
}

// ============================================================ SLIDE 1 — TITLE
(() => {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("AI-Powered Job Market Intelligence", {
    isTextBox: true, x: 0.9, y: 2.25, w: 11.5, h: 1.0,
    fontFace: HEAD, fontSize: 40, bold: true, color: WHITE, margin: 0,
  });
  s.addText("& Semantic CV Matching", {
    isTextBox: true, x: 0.9, y: 3.15, w: 11.5, h: 0.8,
    fontFace: HEAD, fontSize: 40, bold: true, color: ICE, margin: 0,
  });
  s.addText("Not just which skills a posting names — but why each one is there.", {
    isTextBox: true, x: 0.9, y: 4.15, w: 11.5, h: 0.5,
    fontFace: BODY, fontSize: 18, italic: true, color: ICE, margin: 0,
  });
  s.addText("Big Data and AI  ·  solo project (lecturer-approved)", {
    isTextBox: true, x: 0.9, y: 5.35, w: 11.5, h: 0.4,
    fontFace: BODY, fontSize: 15, color: WHITE, margin: 0,
  });
  // motif: three attribution-class dots
  [[GREEN, 0.9], [AMBER, 1.3], [GREY, 1.7]].forEach(([c, x]) => {
    s.addShape(pres.ShapeType.ellipse, { x, y: 1.7, w: 0.28, h: 0.28, fill: { color: c } });
  });
  s.addNotes("One line: this project is about extracting not just which skills a posting names, but why — required, preferred, boilerplate, or not expected.");
})();

// ========================================================= SLIDE 2 — PROBLEM
(() => {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  titleBar(s, "A keyword search sees eleven flat terms", "The problem");

  // left framing
  s.addText([
    { text: "The posting itself marks which skills are mandatory, which are a plus, and which are just the company describing its own product.", options: { breakLine: true, paraSpaceAfter: 10 } },
    { text: "Recovering that distinction is the whole project.", options: { bold: true, color: NAVY } },
  ], { isTextBox: true, x: 0.6, y: 2.0, w: 5.0, h: 3.6, fontFace: BODY, fontSize: 17, color: INK, margin: 0, valign: "top" });

  // right: posting card
  s.addShape(pres.ShapeType.roundRect, { x: 6.0, y: 1.85, w: 6.7, h: 5.1, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "D8DEEA", width: 1 }, shadow: { type: "outer", blur: 6, offset: 2, angle: 90, color: "B9C2D6", opacity: 0.5 } });
  s.addText("Posting 3902915545 — Java Architect", { isTextBox: true, x: 6.25, y: 2.0, w: 6.2, h: 0.4, fontFace: BODY, fontSize: 14, bold: true, color: NAVY, margin: 0 });

  s.addText("REQUIRED  ·  7", { isTextBox: true, x: 6.25, y: 2.5, w: 6.2, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: GREEN, charSpacing: 1, margin: 0 });
  let y = chipBlock(s, ["Java", "RESTful APIs", "Spring Boot", "Spring Security", "Spring Data", "Spring MVC", "MS SQL"], 6.25, 2.85, GREEN, 12.4);

  s.addText("PREFERRED  ·  3  (\u201cconsidered a plus\u201d)", { isTextBox: true, x: 6.25, y: y + 0.18, w: 6.2, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: AMBER, charSpacing: 1, margin: 0 });
  y = chipBlock(s, ["Apache Camel", "Kubernetes", "NoSQL"], 6.25, y + 0.5, AMBER, 12.4);

  s.addText("BOILERPLATE  ·  ~half the text", { isTextBox: true, x: 6.25, y: y + 0.18, w: 6.2, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: GREY, charSpacing: 1, margin: 0 });
  s.addText("\u201cWho are we? First Derivatives\u2026\u201d, the KX product paragraphs, Managed Services blurb, and the EEO statement. A naive keyword pass pulls \u201cKX\u201d out as a skill — it is the company\u2019s product name.", { isTextBox: true, x: 6.25, y: y + 0.5, w: 6.25, h: 1.0, fontFace: BODY, fontSize: 11.5, italic: true, color: MUT, margin: 0, valign: "top" });

  s.addNotes("A keyword extractor sees eleven flat terms. The posting marks 7 as mandatory (inside years-of-experience bullets), 3 as a plus, and roughly half the text is the company talking about itself. Recovering that distinction is the project. Note: Kubernetes sits in a compound 'is considered a plus' clause — a defensible preferred, and a good example of why per-skill attribution with an evidence span beats a flat keyword list.");
})();

// =============================================== SLIDE 3 — RESEARCH QUESTION
(() => {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  titleBar(s, "One measured question", "Research question");
  s.addText([
    { text: "Can an LLM correctly distinguish ", options: {} },
    { text: "why", options: { italic: true, color: NAVY } },
    { text: " a technical skill is mentioned — ", options: {} },
    { text: "required / preferred / boilerplate / not-expected", options: { bold: true, color: NAVY } },
    { text: " — more accurately than a keyword baseline?", options: {} },
  ], { isTextBox: true, x: 0.6, y: 2.0, w: 12.1, h: 1.6, fontFace: HEAD, fontSize: 26, color: INK, margin: 0, lineSpacingMultiple: 1.1 });

  const box = (x, tag, title, body, col) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 4.1, w: 5.85, h: 2.5, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "D8DEEA", width: 1 } });
    s.addText(tag.toUpperCase(), { isTextBox: true, x: x + 0.3, y: 4.35, w: 5.2, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: col, charSpacing: 2, margin: 0 });
    s.addText(title, { isTextBox: true, x: x + 0.3, y: 4.7, w: 5.25, h: 0.5, fontFace: HEAD, fontSize: 19, bold: true, color: NAVY, margin: 0 });
    s.addText(body, { isTextBox: true, x: x + 0.3, y: 5.25, w: 5.25, h: 1.2, fontFace: BODY, fontSize: 14, color: INK, margin: 0, valign: "top" });
  };
  box(0.6, "The experiment", "Skill attribution", "Measured on a frozen gold set. This is the graded AI claim, evaluated against a baseline.", GREEN);
  box(6.85, "The product", "CV matching", "A semantic matcher that uses the attribution to compute missing required skills. The demo.", AMBER);
  s.addNotes("State the split explicitly so this doesn't read as a generic job recommender: the experiment (attribution) is what's measured; the product (CV matching) is what's demoed.");
})();

// =================================================== SLIDE 4 — ARCHITECTURE
(() => {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  titleBar(s, "Four course technologies, one pipeline", "Architecture");

  const node = (x, y, w, label, sub, fill, txt) => {
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.95, rectRadius: 0.06, fill: { color: fill }, line: { color: "C9D2E4", width: 1 } });
    s.addText([
      { text: label, options: { bold: true, fontSize: 12.5, color: txt || WHITE, breakLine: true } },
      { text: sub, options: { fontSize: 9.5, color: txt ? MUT : ICE } },
    ], { isTextBox: true, x: x + 0.05, y, w: w - 0.1, h: 0.95, fontFace: BODY, align: "center", valign: "middle", margin: 0 });
  };
  const arrow = (x1, y1, x2, y2) => s.addShape(pres.ShapeType.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color: NAVY, width: 1.5, endArrowType: "triangle" } });

  // main pipeline row (y ~1.95)
  const yr = 1.95, wN = 1.72, gap = 0.18, x0 = 0.6;
  const xs = [];
  for (let i = 0; i < 6; i++) xs.push(x0 + i * (wN + gap));
  node(xs[0], yr, wN, "Kaggle CSV", "123,849", "8A93A8", null);
  node(xs[1], yr, wN, "Kafka", "jobs.raw", NAVY, null);
  node(xs[2], yr, wN, "Spark", "Bronze \u2192 Silver", NAVY, null);
  node(xs[3], yr, wN, "Gazetteer UDF", "baseline · 111 terms", "8A93A8", null);
  node(xs[4], yr, wN, "LLM enrich", "Anthropic API", GREEN, null);
  node(xs[5], yr, wN, "Elasticsearch", "dense_vector kNN", NAVY, null);
  for (let i = 0; i < 5; i++) arrow(xs[i] + wN, yr + 0.475, xs[i + 1], yr + 0.475);

  // course-tech legend
  s.addText("Navy = course technology (Docker · Kafka · Spark · Elasticsearch).  Docker runs Kafka and Elasticsearch as containers.", { isTextBox: true, x: 0.6, y: 3.15, w: 12.1, h: 0.35, fontFace: BODY, fontSize: 12, italic: true, color: MUT, margin: 0 });

  // branch boxes
  const esX = xs[5];
  const branch = (x, y, tag, body, col) => {
    s.addShape(pres.ShapeType.roundRect, { x, y, w: 5.85, h: 1.9, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "D8DEEA", width: 1 } });
    s.addText(tag, { isTextBox: true, x: x + 0.3, y: y + 0.2, w: 5.25, h: 0.35, fontFace: BODY, fontSize: 13, bold: true, color: col, charSpacing: 1, margin: 0 });
    s.addText(body, { isTextBox: true, x: x + 0.3, y: y + 0.62, w: 5.3, h: 1.15, fontFace: BODY, fontSize: 13, color: INK, margin: 0, valign: "top" });
  };
  branch(0.6, 4.0, "DEMO · CV matching", "CV \u2192 LLM parse \u2192 user confirms \u2192 embed (same model) \u2192 cosine kNN \u2192 skill gap = required \u2212 confirmed  (set arithmetic, computed).", GREEN);
  branch(6.85, 4.0, "EVALUATION · kept separate", "40 gold postings, frozen by seed before any prompt existed. Compared to a majority-class baseline. Not part of what runs in the demo.", AMBER);
  s.addNotes("One line per stage. Land on: the gazetteer is both the deterministic baseline extractor AND the evaluation universe. Evaluation is drawn separate on purpose — it is the experiment, not the product.");
})();

// ===================================================== SLIDE 5 — EXPERIMENT
(() => {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  titleBar(s, "The comparison is against the base rate, not zero", "The experiment");

  const row = (y, head, body, col) => {
    s.addShape(pres.ShapeType.ellipse, { x: 0.6, y, w: 0.5, h: 0.5, fill: { color: col } });
    s.addText(head, { isTextBox: true, x: 1.35, y: y - 0.05, w: 11.2, h: 0.4, fontFace: BODY, fontSize: 17, bold: true, color: NAVY, margin: 0 });
    s.addText(body, { isTextBox: true, x: 1.35, y: y + 0.33, w: 11.2, h: 0.5, fontFace: BODY, fontSize: 14, color: INK, margin: 0 });
  };
  row(2.15, "40 gold postings, frozen by seed", "IDs fixed before any prompt existed. Prompt iteration confined to a disjoint 10-posting dev set.", NAVY);
  row(3.35, "Baseline = majority class", "Every skill the keyword extractor detects is scored \u201crequired\u201d — the base rate to beat.", GREY);
  row(4.55, "Three metrics reported", "Detection F1 · attribution accuracy on the common set (headline) · end-to-end accuracy.", GREEN);
  row(5.75, "Raw counts alongside percentages", "n=40, ~255 hand-labelled mentions. Figures are indicative, not precise.", AMBER);
  s.addNotes("The comparison is against the base rate (majority class), never against zero. Gold IDs frozen before prompts existed removes the risk of tuning to the test set.");
})();

// ======================================================== SLIDE 6 — RESULTS
(() => {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  titleBar(s, "The LLM beats the base rate on attribution", "Results · this dataset");

  s.addChart(pres.ChartType.bar, [
    { name: "Majority-class baseline", labels: ["Attribution accuracy"], values: [76.4] },
    { name: "LLM", labels: ["Attribution accuracy"], values: [87.3] },
  ], {
    x: 0.6, y: 1.95, w: 6.4, h: 4.6,
    barDir: "col", barGrouping: "clustered",
    chartColors: [GREY, GREEN],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"',
    dataLabelFontFace: BODY, dataLabelFontSize: 13, dataLabelColor: INK,
    valAxisMinVal: 0, valAxisMaxVal: 100, valAxisHidden: true,
    catAxisLabelColor: INK, catAxisLabelFontFace: BODY, catAxisLabelFontSize: 12,
    valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showTitle: false, showLegend: true, legendPos: "b", legendColor: INK, legendFontFace: BODY, legendFontSize: 12,
  });
  s.addText("Common set: 200/229 vs 175/229", { isTextBox: true, x: 0.6, y: 6.55, w: 6.4, h: 0.35, fontFace: BODY, fontSize: 12, italic: true, color: MUT, align: "center", margin: 0 });

  // stat callouts
  const stat = (y, big, label, note, col) => {
    s.addShape(pres.ShapeType.roundRect, { x: 7.4, y, w: 5.3, h: 1.35, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "D8DEEA", width: 1 } });
    s.addText(big, { isTextBox: true, x: 7.65, y: y + 0.15, w: 2.2, h: 1.05, fontFace: HEAD, fontSize: 30, bold: true, color: col, align: "left", valign: "middle", margin: 0 });
    s.addText([{ text: label, options: { bold: true, color: NAVY, breakLine: true } }, { text: note, options: { fontSize: 11, color: MUT } }], { isTextBox: true, x: 9.7, y: y + 0.15, w: 2.85, h: 1.05, fontFace: BODY, fontSize: 13, valign: "middle", margin: 0 });
  };
  stat(1.95, "80.3%", "End-to-end", "vs 75.9% baseline · 200/249", GREEN);
  stat(3.5, "0.911", "Detection F1", "gazetteer 0.988 wins by construction — shown, not hidden", GREY);
  s.addText("Indicative, not precise: n=40, and mentions within a posting are not independent, so the true interval is wider than a naive binomial.", { isTextBox: true, x: 7.4, y: 5.15, w: 5.3, h: 1.3, fontFace: BODY, fontSize: 12.5, italic: true, color: MUT, margin: 0, valign: "top" });
  s.addNotes("Say the raw counts out loud: 200 of 229 vs 175 of 229. Detection F1 favours the baseline by construction because the gold universe is gazetteer-bounded — show it, don't hide it. End the slide on the honesty caveat.");
})();

// =================================================== SLIDE 7 — SHARPEST CASE
(() => {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  titleBar(s, "One posting makes the whole argument", "The sharpest case");

  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 2.0, w: 12.1, h: 1.5, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "D8DEEA", width: 1 } });
  s.addText([
    { text: "\u201cExperience with Oracle Application Test Suites (OATS) ", options: { color: INK } },
    { text: "(NOT Required)", options: { bold: true, color: RED } },
    { text: "\u201d", options: { color: INK } },
  ], { isTextBox: true, x: 0.9, y: 2.25, w: 11.5, h: 1.0, fontFace: HEAD, fontSize: 22, italic: true, valign: "middle", margin: 0 });
  s.addText("Posting 3905827892", { isTextBox: true, x: 0.9, y: 3.05, w: 11.5, h: 0.3, fontFace: BODY, fontSize: 11, color: MUT, margin: 0 });

  const card = (x, tag, verdict, body, col, ok) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 3.95, w: 5.85, h: 2.6, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "D8DEEA", width: 1 } });
    s.addText(tag.toUpperCase(), { isTextBox: true, x: x + 0.3, y: 4.2, w: 5.25, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: MUT, charSpacing: 1, margin: 0 });
    s.addText([{ text: (ok ? "\u2713  " : "\u2717  "), options: { color: col, bold: true } }, { text: verdict, options: { color: col, bold: true } }], { isTextBox: true, x: x + 0.3, y: 4.55, w: 5.25, h: 0.55, fontFace: HEAD, fontSize: 22, margin: 0 });
    s.addText(body, { isTextBox: true, x: x + 0.3, y: 5.2, w: 5.3, h: 1.2, fontFace: BODY, fontSize: 14, color: INK, margin: 0, valign: "top" });
  };
  card(0.6, "Keyword baseline", "required", "The term OATS is present, so a keyword pass must score it as a requirement. It cannot do otherwise.", RED, false);
  card(6.85, "LLM attribution", "not_expected", "Reads the parenthetical and assigns the rare class. Only 3 of 55,088 mentions — rare, but real.", GREEN, true);
  s.addNotes("This one example is the argument in miniature. The keyword baseline is structurally unable to get it right; the term is in the text. not_expected is rare but real.");
})();

// ========================================================== SLIDE 8 — DEMO
(() => {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("LIVE DEMO", { isTextBox: true, x: 0.6, y: 0.5, w: 12.1, h: 0.4, fontFace: BODY, fontSize: 13, bold: true, color: AMBER, charSpacing: 3, margin: 0 });
  s.addText("Uncheck a skill \u2192 watch the gap recompute", { isTextBox: true, x: 0.6, y: 0.9, w: 12.1, h: 0.8, fontFace: HEAD, fontSize: 30, bold: true, color: WHITE, margin: 0 });

  // screenshot placeholder frame
  s.addShape(pres.ShapeType.roundRect, { x: 0.9, y: 2.0, w: 8.4, h: 4.7, rectRadius: 0.06, fill: { color: "16204E" }, line: { color: ICE, width: 1, dashType: "dash" } });
  s.addText("[ live demo — fallback: recording ]", { isTextBox: true, x: 0.9, y: 4.1, w: 8.4, h: 0.5, fontFace: BODY, fontSize: 15, italic: true, color: ICE, align: "center", margin: 0 });

  // computed / generated labels
  s.addShape(pres.ShapeType.roundRect, { x: 9.6, y: 2.0, w: 3.1, h: 2.2, rectRadius: 0.08, fill: { color: WHITE } });
  s.addText([{ text: "COMPUTED", options: { bold: true, color: GREEN, charSpacing: 1, breakLine: true, paraSpaceAfter: 6 } }, { text: "gap = required \u2212 confirmed skills. Deterministic set arithmetic.", options: { color: INK } }], { isTextBox: true, x: 9.85, y: 2.25, w: 2.6, h: 1.7, fontFace: BODY, fontSize: 13, valign: "top", margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 9.6, y: 4.5, w: 3.1, h: 2.2, rectRadius: 0.08, fill: { color: WHITE } });
  s.addText([{ text: "GENERATED", options: { bold: true, color: AMBER, charSpacing: 1, breakLine: true, paraSpaceAfter: 6 } }, { text: "advice panel. LLM output, validated, in a separate labelled region.", options: { color: INK } }], { isTextBox: true, x: 9.85, y: 4.75, w: 2.6, h: 1.7, fontFace: BODY, fontSize: 13, valign: "top", margin: 0 });
  s.addNotes("Run the demo live. The moment to land: unchecking a skill the LLM extracted and watching the match set and the skill-gap panel recompute. Narrate the computed vs generated boundary as it happens. If the live app isn't ready, this slide anchors the recording.");
})();

// ====================================================== SLIDE 9 — INSIGHTS
(() => {
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  titleBar(s, "What the corpus shows — in this dataset", "Insights");

  const card = (x, big, label, note, col) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 2.1, w: 3.85, h: 3.9, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "D8DEEA", width: 1 } });
    s.addText(big, { isTextBox: true, x: x + 0.25, y: 2.5, w: 3.35, h: 1.1, fontFace: HEAD, fontSize: 42, bold: true, color: col, margin: 0 });
    s.addText(label, { isTextBox: true, x: x + 0.25, y: 3.65, w: 3.4, h: 0.7, fontFace: BODY, fontSize: 16, bold: true, color: NAVY, margin: 0, valign: "top" });
    s.addText(note, { isTextBox: true, x: x + 0.25, y: 4.45, w: 3.4, h: 1.4, fontFace: BODY, fontSize: 13, color: MUT, margin: 0, valign: "top" });
  };
  card(0.6, "71.6%", "of cleaned postings name zero technologies", "87,203 of 121,842. The technical corpus is a minority.", GREY);
  card(4.72, "29.7%", "of mentions are not stated as requirements", "Of 55,088 mentions: 70.3% required, 22.2% preferred, 7.5% boilerplate, 3 not-expected — 16,355 not required.", GREEN);
  card(8.85, "fused words", "an HTML-stripping artifact, found not assumed", "\u201cConsultingFD\u201d. Diagnosed from a grounding failure — drove the whitespace-stripped check.", AMBER);
  s.addText("Every figure describes this dataset, not the labour market.", { isTextBox: true, x: 0.6, y: 6.25, w: 12.1, h: 0.4, fontFace: BODY, fontSize: 13, italic: true, color: MUT, margin: 0 });
  s.addNotes("Every number is 'in this dataset' (3,995 enriched postings). The 29.7% non-required is the research question at corpus scale. Per-class raw counts: required 38,733, preferred 12,246, boilerplate 4,106, not-expected 3; total 55,088. Full aggregate committed in docs/insights.txt. The fused-word artifact was found by diagnosing a grounding failure, not assumed.");
})();

// =================================================== SLIDE 10 — LIMITATIONS
(() => {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("LIMITATIONS", { isTextBox: true, x: 0.6, y: 0.55, w: 12.1, h: 0.4, fontFace: BODY, fontSize: 13, bold: true, color: AMBER, charSpacing: 3, margin: 0 });
  s.addText("Volunteered, not defended under questioning", { isTextBox: true, x: 0.6, y: 0.95, w: 12.1, h: 0.8, fontFace: HEAD, fontSize: 30, bold: true, color: WHITE, margin: 0 });

  const items = [
    ["n = 40 gold postings", "Results are indicative. Raw counts reported alongside every percentage."],
    ["Gold universe bounded to the gazetteer", "Hands perfect detection recall to the baseline — conservative against our own claim."],
    ["Retrieval depends on LLM extraction", "The embedding is title + extracted skills, not the full description. MiniLM truncates at 256 word-pieces."],
    ["Kafka replay, not live scraping", "Stated honestly. A live source adds a day for no additional grade."],
  ];
  let y = 2.2;
  for (const [h, b] of items) {
    s.addShape(pres.ShapeType.ellipse, { x: 0.7, y: y + 0.05, w: 0.22, h: 0.22, fill: { color: ICE } });
    s.addText(h, { isTextBox: true, x: 1.15, y, w: 11.4, h: 0.4, fontFace: BODY, fontSize: 18, bold: true, color: ICE, margin: 0 });
    s.addText(b, { isTextBox: true, x: 1.15, y: y + 0.4, w: 11.4, h: 0.5, fontFace: BODY, fontSize: 14, color: WHITE, margin: 0 });
    y += 1.15;
  }
  s.addNotes("Thirty seconds, unprompted. Volunteering these is worth more than defending them under questioning.");
})();

pres.writeFile({ fileName: "presentation.pptx" }).then(f => console.log("wrote", f));