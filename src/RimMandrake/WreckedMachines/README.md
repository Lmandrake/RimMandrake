# WreckedMachines

_Authored mod. `packageId: mandrake.rm.wreckedmachines`. Started 2026-08-12._

Three visual states for large machines owned by other mods — **wrecked →
kludged → restored** — so the Kolyska's dead factory is something the crew
restores in place rather than clears away.

> **STATUS: ART PIPELINE ONLY.** No defs are authored yet, the mod is not
> enabled in `ModsConfig.xml`, and nothing is deployed. That is deliberate —
> see [Why art before defs](#why-art-before-defs). Do not add it to the load
> order until `check_sprite.py` passes for at least one machine.

## What lives where

| Path | What it is |
|---|---|
| `About/About.xml` | Mod metadata. Hard-depends on VFE-Factory. |
| `DESIGN.md` | **The design.** What the three tiers mean, how a tier is advanced, and the one open question. Read before authoring anything. |
| `MACHINES.md` | **The register** of which machines this mod treats, and their per-machine status. |
| `Defs/` | Tier ThingDefs. Empty until art exists. |
| `Textures/` | Finished damaged art, in the layout RimWorld loads. Empty until art exists. |
| `art_source/` | **The workshop.** Per machine: pristine donor art, the empty holes to fill, measurements, contact sheet, the 4-facing sheet and the three generated briefs. Not shipped to the game. |
| `Source/` | The tooling. Not shipped to the game. |

## The pipeline

```bash
# 1. pull the pristine art, build the 4-facing sheet, write the three briefs
python Source/grab_source_art.py VFEFactory_AutomatedSmelter

# 2. give BRIEF_1_WRECKED.md + sheets/SOURCE_SHEET.png to the image model.
#    Save what comes back, then:
python Source/sheet.py split AutomatedSmelter --tier wrecked --sheet <returned> --then-fit
python Source/check_sprite.py AutomatedSmelter --tier wrecked

# 3. BRIEF_2_KLUDGED.md + the WRECKED sheet you just got back
python Source/sheet.py split AutomatedSmelter --tier kludged --sheet <returned> --then-fit
python Source/check_sprite.py AutomatedSmelter --tier kludged

# 4. BRIEF_3_REPAIRED.md + the KLUDGED sheet
python Source/sheet.py split AutomatedSmelter --tier repaired --sheet <returned> --then-fit
python Source/check_sprite.py AutomatedSmelter --tier repaired

# 5. only once those pass: author the tier defs
```

**The three states are a chain, not a fan-out.** Each is drawn *by modifying the
previous one*, which is what keeps a hole torn in step 1 still present, patched,
in step 3. And all four facings travel together in **one 2x2 sheet**, so the
model draws one machine seen four ways instead of four machines that share a
name.

`grab_source_art.py --list` shows what is currently treated.

### What the grabber gives you

For each machine it writes `art_source/<Machine>/` containing:

- **`restored/`** — the donor mod's own textures, copied. This is tier 3 *and*
  the reference every damaged version is drawn against.
- **`wrecked/`, `kludged/`** — empty, each with a `HOLES.txt` naming the exact
  files that must appear. The gaps are visible in a file browser.
- **`MANIFEST.json`** — the ThingDef facts (texPath, graphicClass, drawSize,
  tile size, build cost, research) plus per-file measurements. This is what the
  validator checks candidates against.
- **`CONTACT_SHEET.png`** — all facings on a checkerboard, so alpha is visible.
- **`BRIEF_1_WRECKED.md` / `BRIEF_2_KLUDGED.md` / `BRIEF_3_REPAIRED.md`** — the
  sequential briefs, each self-contained because each is pasted into a fresh
  conversation.
- **`sheets/SOURCE_SHEET.png`** + `SHEET_LAYOUT.json` — all four facings in one
  2x2 image for the model, and the geometry needed to cut the result back apart.
  These two are **inputs** and are tracked. Everything else that lands in
  `sheets/` is a model **output** awaiting the cut, and is now gitignored
  (`*/sheets/*_SHEET.png`) — 13 of them, ~21 MB, accumulated for the smelter
  alone in one afternoon and were swept on 2026-08-12. Once a sheet has been
  cut, the per-facing PNGs in the tier folder are the product; the sheet is
  scaffolding. Sweep it before you leave a machine.

### What the fitter does

Image models do not respect canvas specs — the pilot art came back at 1536×1024
and 1448×1086 against a required 640×512, one of them with no alpha at all. But
the *machines* were drawn at silhouette aspect ratios of 1.329 and 1.333 against
the reference's 1.328. The art was right; only the packaging was wrong, and
packaging is arithmetic.

`fit_sprite.py` restores alpha (edge-keyed at a tolerance derived from the
border, then morphologically sealed), despeckles, trims, scales, and
**registers** the result against the reference by maximising mask overlap —
because damaged art is missing chunks, so its bounding-box centre is not where
the machine actually sits. Originals are moved to `<tier>/_raw/`, never
destroyed.

### What the validator catches

Wrong canvas size · no alpha channel · blank or near-empty images · a
silhouette that drifted off its footprint · colour-vs-greyscale drift · a
"damaged" file that is byte-identical to the original. All decidable offline in
milliseconds.

## Why art before defs

A cold game load costs ~23–30 minutes and is the scarcest resource in this
project. Every failure mode above is invisible until a pawn stands next to the
machine — and every one is arithmetic on numbers we already have. So the rule
here is: **no def is written for a tier whose art has not passed the
validator.** The tooling exists to make the reload prove something we could not
have known offline, and nothing else.

## Dependencies

Hard: **Vanilla Furniture Expanded - Factory** (`VanillaExpanded.VFEFactory`,
WS 3686924415), which itself needs VFE-Core and Harmony.

No C# and no Harmony patching of our own — this is defs plus textures. If that
changes, it needs a decision recorded in `DESIGN.md`, not a quiet dependency.

## Deployment

Same as every authored mod here — the repo copy is **not** what the game reads:

```bash
python ../../Utils/deploy_custom_mods.py            # plan
python ../../Utils/deploy_custom_mods.py --apply
```

`Source/`, `art_source/` and `*.md` are excluded from deployment; the game only
receives `About/`, `Defs/` and `Textures/`. See `../README.md`.

## Related project docs

- `design/Jawa/worldbuilding/ship_deck_plan.md` — **owns** the SACRED SCRAP ruling and the
  repair-as-progression ladder this mod implements. The authority.
- `vendor/wisdom/Factory_lore.md` — how the VFE-Factory machines actually work.
- `design/Jawa/art/graphics_overhaul_protocol.md` — the general method for
  overhauling art in this stack.
