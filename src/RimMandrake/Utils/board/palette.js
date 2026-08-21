/* palette.js — the validated categorical palette, and the rule that comes with it.
 *
 * 🔴 THE GLYPH IS NOT DECORATION. Read this before using a colour.
 *
 * These eight steps were validated, not chosen by eye. Against ADJACENT pairs — which
 * is what a lane or a fixed-order stacked bar is — they all pass: lightness band,
 * chroma floor, CVD separation worst ΔE 8.4 (protan), normal-vision floor worst ΔE
 * 19.3, contrast ≥ 3:1 on all eight.
 *
 * ⛔ Under ALL-PAIRS they FAIL, and the Flow graph is all-pairs because any two work
 * types can end up next to each other:
 *      #d55181 ↔ #199e70   ΔE 1.6   deuteranopia
 *      #e66767 ↔ #d95926   ΔE 7.1   NORMAL VISION
 *
 * ⇒ On the Flow graph and anywhere marks float freely, **every mark carries its glyph
 * and its label; colour is never the only encoding.** On lanes and stacked bars, where
 * the order is fixed and only neighbours touch, colour alone is legal. This is a
 * measured requirement, not a preference — two of our own categories are 7.1 apart to
 * a reader with ordinary sight.
 *
 * ⚠️ STATUS IS A SEPARATE CHANNEL and must never borrow a categorical hue, or "blocked"
 * competes with "art" for the same pixel:
 *      blocked  ring + ⚠        doing  full opacity
 *      done     dimmed to 45%   idle   dashed outline
 */
export const SURFACE = "#1a1a19";

export const KIND = {
  test:   { hex: "#3987e5", glyph: "◈", label: "Testing / V&V" },
  world:  { hex: "#d95926", glyph: "⬡", label: "World authoring" },
  config: { hex: "#199e70", glyph: "⟨⟩", label: "Config / XML patch" },
  doc:    { hex: "#c98500", glyph: "▤", label: "Document design" },
  art:    { hex: "#d55181", glyph: "✦", label: "Art / asset generation" },
  code:   { hex: "#008300", glyph: "⌘", label: "Source code" },
  infra:  { hex: "#9085e9", glyph: "⚙", label: "Infrastructure / process" },
  repair: { hex: "#e66767", glyph: "⤬", label: "Repair / known bug" },
};

/* The ledger's `kind` is free text filed by a seat, so map rather than index. An
 * unknown kind gets a neutral, NOT a colour borrowed from a real category — a wrong
 * colour reads as a confident wrong answer. */
const ALIAS = {
  check: "test", verify: "test", task: "code", build: "code",
  decision: "doc", question: "doc", spec: "doc",
  patch: "config", xml: "config", def: "config",
  texture: "art", sprite: "art", map: "world", worldgen: "world",
  bug: "repair", fix: "repair", hook: "infra", tooling: "infra",
};

export function kindOf(item) {
  const k = String(item && item.kind || "").toLowerCase();
  return KIND[k] || KIND[ALIAS[k]] ||
    { hex: "#6b6b68", glyph: "·", label: k || "unclassified" };
}

/* Status, as the separate channel it must stay. */
export function statusStyle(item) {
  if (item.blocked) return { ring: true, warn: "⚠", opacity: 1 };
  switch (item.state) {
    case "doing":  return { opacity: 1 };
    case "done":   return { opacity: 0.45 };
    case "dropped":
    case "superseded": return { opacity: 0.35, strike: true };
    default:       return { opacity: 0.85 };
  }
}

/* Every mark, everywhere. Cheap enough that there is no reason to skip it, and
 * skipping it is what the all-pairs failure above makes unsafe. */
export function mark(item) {
  const k = kindOf(item);
  return { ...k, ...statusStyle(item) };
}
