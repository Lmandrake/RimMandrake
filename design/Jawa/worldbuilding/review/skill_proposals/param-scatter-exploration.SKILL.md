# param-scatter-exploration (PROPOSED SKILL — draft, not installed)

_Drafted 2026-09-05 by the creature-distribution analysis pass. skills/ is curated
only in fresh-context sessions; this is the full draft. Working reference
implementation: `design/Jawa/worldbuilding/review/gen_creature_explorer.py` →
`review/viz/creature_explorer.html` (1,165 creatures, 15 axes, sprite hovers,
basket extraction)._

## Description (for the skill listing)
Build the owner an ANY-AXIS scatter workbench over a register: a single offline
HTML file where he picks param1 × param2 himself, sees the actual game sprite on
hover, filters by the categorical fields, and clicks outliers into a basket that
exports as a defName list. Use when the question is exploratory ("let me poke at
the distribution"), when static figures answered THEIR questions but the owner will
have his own, and after any register regeneration (the page regenerates with it).

## The pattern

### 1. It is a generator, not a page
`gen_<subject>_explorer.py`, committed next to the register generator. It slims
each row to the plottable fields + identity + sprite path and embeds the JSON in a
template. Regenerating the register then regenerating the explorer is one command
each; the HTML itself says "GENERATED — edit the generator".

### 2. Where it lives decides what it can show
- **Local file next to the art** (`review/viz/…`), sprites referenced by RELATIVE
  path (`../creature_art/<defName>.detail.png`). This is why it is NOT a claude.ai
  Artifact: thousands of local sprites cannot ride along (16 MB cap) and hovering
  the real art is the point. Give the owner the complete native Windows path.
- It is also NOT a review-sheet: it captures no decisions. Say so on the page —
  the basket is localStorage-only, and anything worth keeping must be copied out.
  If the session turns into keep/cut decisions, hand off to the review-sheets
  skill and its decisions-file machinery instead of growing this page one.

### 3. The axis menu
- Every numeric register field, plus DERIVED axes with the formula in the label
  ("K = bestHit ÷ bodySize (derived)") — derived-and-labeled beats making the
  owner compute ratios in his head.
- Per-axis log toggles, with sane defaults (log for anything spanning decades).
- null ≠ 0: rows missing a value for the chosen pair drop out and the status bar
  says how many dropped — never plot a missing value at zero.

### 4. Reference laws draw themselves
Keep a small registry: (x-field, y-field) → law curves. When the owner lands on a
pair the project has a law for (yield vs size, damage band, sprite-scale law), the
law appears; when he lands elsewhere, none is faked. The status line states
whether a law is drawn. This turns free exploration into judgment against the
same doctrine the static portfolio used.

### 5. The basket (the deck lesson, applied)
From the tech-tree pptx rounds: **the artifact the owner manipulates is the
decision record — always ship the extraction path.** Here: click a point to
collect it, chips removable, "copy defNames JSON" button. An outlier safari ends
as a pasteable list for a rimflow item, not as a memory. Persist the basket in
localStorage (per-browser convenience only) and say exactly that on the page.

### 6. Minimum QA without a browser
node --check the extracted <script>; verify the sprite relative path against the
real art directory; verify the embedded row count; state in the notes that
first-open rendering was not eyeballed if no browser was available — the fix is
one generator edit, not a reason to ship nothing.

## Interaction grammar worth reusing elsewhere
hover = identity + art + stats · click = collect · chips = un-collect ·
copy button = the only exit that keeps data · filters are ANDed and cheap ·
"live only" is a first-class toggle wherever Cherry Picker exists.

## Failure modes prevented
- Publishing a sprite-dependent page where the sprites cannot follow it.
- An exploration page that silently becomes an unrecorded decisions store.
- Derived quantities the owner must compute mentally, or nulls plotted as zeros.
- A one-off HTML nobody can regenerate after the next register rebuild.
