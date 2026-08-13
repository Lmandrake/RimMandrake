# MACHINES — the treated register

_Which machines WreckedMachines gives a wrecked and kludged state to, and where
each one stands. Updated by hand; the machine list itself is enforced by
`TREATED` in `Source/grab_source_art.py`, and the two must agree._

**Adding a machine takes three edits:** add it to `TREATED`, run the grabber,
add a row here. Nothing else registers a machine.

---

## Currently treated

| Machine | defName | Owner | wrecked | kludged | repaired | Defs | Notes |
|---|---|---|---|---|---|---|---|
| Automated Smelter | `VFEFactory_AutomatedSmelter` | VFE-Factory | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 | ⬜ | **Pilot.** Phase 2 of the repair ladder — first machine the player restores. **All three art tiers complete**, 12 facings conformed and validated 2026-08-12. Defs are the only remaining work. See the caveats below. |

Legend: ⬜ not started · 🟨 partial · ✅ passes `check_sprite.py`

## Wrecked tier — done 2026-08-12, with two caveats

All four facings were generated through the new Claude-driven pipeline
(`skills/generating-rimworld-sprites/`), each edited from its own `restored/`
reference with the owner-chosen south wreck attached as a style anchor. Every
one conformed to its own canvas — including the **N/S ↔ E/W transposition** —
and passed the validator.

| facing | canvas | subject vs reference | coverage vs reference |
|---|---|---|---|
| north | 512×640 | placed (68,49) | 59.6% vs 60.7% |
| south | 512×640 | placed (69,49) | 58.9% vs 60.3% |
| east | 640×512 | placed (54,46) | 60.8% vs 61.7% |
| west | 640×512 | placed (52,47) | 60.6% vs 61.7% |

✅ **Cross-facing damage correspondence — REQUIREMENT DROPPED by the owner,
2026-08-12.** Breaches do not correspond to the same physical holes between
views, and the owner has ruled this beyond current image-generation technology
and acceptable as-is. Do not spend further effort on it, and do not re-raise it
as a defect.

✅ **North was regenerated** and the outlier replaced. v1 came out darker and
greyer and lost the rust-red backing panel; v2 anchors on the south wreck for
palette and brightness explicitly and matches its siblings. v1 is superseded.

⚠️ **The 2×2 sheet was tried and rejected on measurement, not taste.** A
generation returns roughly a fixed pixel budget, so four facings in one image
each get a quarter of it:

| approach | px per facing | oversampling vs a 512×640 sprite |
|---|---|---|
| 2×2 sheet (1254×1254) | ~393,000 | **1.2×** |
| individual (1120×1405) | ~1,574,000 | **4.8×** |

Sprite crispness comes from generating well above target and area-averaging
down; at 1.2× there is nothing to average. The sheet *did* hold layout and
per-cell orientation, and produced four panels more stylistically alike than
independent runs — but it did not deliver correspondence either, so it loses
4× resolution for nothing. **Generate facings individually, anchored to an
approved sibling.**

---

## Kludged tier — done 2026-08-12

Chained from the **wrecked** art, not the restored, per `DESIGN.md` §"the three
states are a chain" — which is what makes the wreck's torn holes still present,
patched over, in the kludged version.

The owner's brief, delivered: living fire burning inside the dome and visible
through the breach, hasty repairs in mismatched corrugated steel with metal
bands and tape, pipes and hoses and cables run at careless angles, and two or
three auxiliary units of visibly different technology grafted on and partly
doing the smelter's work.

⚠️ **The brief's one internal tension, and how it was resolved.** "Machines
outside supporting the function" versus "nothing leaves the outline" cannot both
hold literally. Resolved as: auxiliary units are **bolted onto the machine body,
inside the original silhouette** — outside the *smelter proper*, inside its
*footprint*. Every facing validated with the span check passing, which is the
proof: art projecting past the outline would have forced the conform step to
scale the machine down and the span check would have failed.

**Unexpected payoff.** The fire solves the readability problem the wrecked tier
has. At true display size a wreck reads as a dark rusty box; the kludged version
has a bright focal point and reads instantly. Value contrast, exactly as the
downscaling rule predicts.

### v2, 2026-08-12 — two owner corrections, both landed

**1. The conveyor belts must stay clear.** v1 buried them under patches and
pipes. They are the machine's functional read — a player needs to see where
material flows — and this had been stated in the original plan doc and missed.
The slatted panels are now bare and unobstructed on all four facings.

**2. No gaping holes with fire in them.** v1 read as a machine burning through
an open breach. The correct fiction is a machine *sealed up and running hot*:
every gap hastily covered, with only small flames and thin smoke escaping at
the seams. v2 does that — the dome is plated over and heat shows as glowing
points along the seams.

**Resolution fixed too.** Asking explicitly for "about 1400 pixels on its long
edge" stopped the model echoing the input resolution, so all four facings now
have full oversampling headroom. v1's west did not.

⚠️ **Smoke legitimately trips the fringe check**, and this changed the
validator. Thin smoke is genuinely semi-transparent, so it lands in the same
alpha 1–31 band that key residue does, and east and west were rejected for it.
Counting faint pixels cannot tell soft art from a defect. The check now tests
the *harm* instead: faint pixels reaching **beyond** the solid silhouette are a
defect, faint pixels **inside** it are soft art and warn rather than block.
Deliberate smoke and glow are therefore expected to raise a warning here — that
is correct behaviour, not something to silence.

v1 is superseded but recoverable from git (`9580b72`).

**Superseded pilot art** is kept at `wrecked/_superseded_pilot/` — the original
single-facing east view and its `_raw`. It is the evidence that produced the
subtractive-damage and containment rules, so it is preserved rather than
overwritten.

**Earlier pilot result (2026-08-12, superseded).** A first single-facing pass
produced the east view of `wrecked` and `kludged`; both conformed and validated.
They pre-date the sheet workflow and the containment rule.

**The workflow changed on 2026-08-12.** Facings are no longer generated one at a
time. All four now travel as a single 2x2 sheet (`sheets/SOURCE_SHEET.png`) so
the model draws one machine seen four ways, and the three states are produced as
a **chain** — wrecked, then kludged *from the wrecked sheet*, then repaired
*from the kludged sheet* — so damage persists coherently across all three.
Round-trip through `sheet.py make` → `split` → `fit_sprite` reconstructs the
originals at IoU 0.981–0.987 with the body at 100% x 100%, so the pipeline
itself costs nothing.

⚠️ **Two art-direction findings, now baked into the briefs.**

1. **Silhouette, not surface.** At true in-game size the kludged version reads
   well — lit indicators and hard cable shapes survive the downscale. The wrecked
   version read as brown mud, because its damage was all mid-tone surface
   corrosion. Damage must be **subtractive**: chunks torn out of the outline.
2. **Nothing may project past the outline.** Cables and hoses reaching outside
   the machine cost it its own size, because the fitter scales the whole drawing
   into the original footprint — measured at 14% of body size lost on the first
   wrecked attempt.

---

## Candidate queue — NOT yet treated

Ordered by the repair ladder in `design/Jawa/worldbuilding/ship_deck_plan.md`, so the
machines the player meets first get art first. **Do not start these until the
smelter has proven the pipeline end to end.**

| Phase | Machine | Why it matters |
|---|---|---|
| 2 | Automated Smelter | ✅ in the register above — salvage → metal, the engine of everything |
| 3 | Automated Cannery | Food security; the Phase-3 provision wing |
| 3 | Conveyor Oven | Same wing |
| 5 | Automated Assembler | Components — the Phase-5 fabrication unlock |
| 5 | Alloy Forge | Plasteel and gravlite; ⚠️ the gravlite recipe is separately gated |
| 5 | Automated Machining Bay | Component chain |
| 6 | Automated Ammunition Press | Phase-6 specialisation |
| 6 | Autoloom | Textiles |
| 6 | Medicine Granulator | Medicine |
| 6 | Neutroamine Synthetiser | Medicine chain |
| — | Automated Distillery, Mincer, Crematorium, Masonry Saw, Biofuel Refinery, Drill Platform, Fishfarm | Lower narrative weight; treat only if the art cost proves cheap |

VFE-Factory ships **~17 machines / 69 textures at ≥512px**. Full coverage at two
damaged tiers is **~138 images**. Treating every machine is a choice, not an
obligation — a partly-treated factory is fine, since untreated machines simply
never appear as wrecks.

---

## Policy: what qualifies

A machine earns treatment if **all** of:

1. **It is large and legible.** A 1×1 box does not read as holy wreckage.
2. **It sits in the ship's fiction.** It belongs in a factory wing the deck plan
   actually places.
3. **Its art is loose and readable.** Verified by the grabber, not assumed —
   VFE-Factory's textures turned out to be *interlaced* PNGs, which broke the
   first decoder pass.
4. **Its owner mod is a hard dependency we already accept.** Do not add a
   dependency to add a wreck.

A machine is **disqualified** if its restored tier is not something the campaign
wants the player to reach at all — in that case it is not a wreck, it is set
dressing, and belongs in a different mod.

---

## Donor mods

| Mod | packageId | Machines drawn from |
|---|---|---|
| Vanilla Furniture Expanded - Factory | `VanillaExpanded.VFEFactory` | all currently treated |

Every donor is a **hard dependency** in `About/About.xml`. The restored tier is
the donor's own building, unmodified — this mod never replaces or retextures the
original, it only adds damaged states in front of it.

⚠️ **Maintenance tail:** when a donor mod updates its art, our damaged versions
silently become inconsistent with it. Re-run `grab_source_art.py` after any
donor update; a changed `MANIFEST.json` measurement is the signal that our tiers
need redrawing.


---

## Repaired tier — done 2026-08-12

Chained from the **kludged** art with the restored donor attached as a second
reference for original detail, so the repair reads as a rebuild of the bodge
rather than a reset to factory-new.

Owner brief, delivered: polished up as far as this machine ever will be, rust
still showing in the pitting and along seams, the bolted-on auxiliary tech
removed and clean plating in its place, conduits and hoses still present but
routed in tidy parallel runs, the **internal smelter windows restored and lit
warm orange as in the original art**, and green status indicators added.

Two gaps needed a second targeted pass, both caught by eye rather than by the
validator:

1. **Green indicators were requested and did not appear at all** on the first
   pass. They are explicit in the brief, so this was a miss, not a judgement.
2. **West kept its bolted-on red control box and tank** when the other three
   facings correctly lost theirs.

Fixed with a single small edit from the repaired art rather than a regeneration
from the kludged — which is the skill's own rule, and it preserved everything
already correct: the restored windows, the neatened conduits, the clear
conveyors.

⚠️ **The validator passed the version missing its green indicators**, exactly as
it passed the 20%-undersized sprite earlier. It checks the contract, never the
brief. Every tier here has needed a human look after a green tick.
