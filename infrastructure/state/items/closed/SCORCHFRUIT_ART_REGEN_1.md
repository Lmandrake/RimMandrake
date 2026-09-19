## spec
Owner (2026-09-14, filing title): "ScorchFruit art: half-buried in ash, cracking
open, no stalk" — verbatim: "it should show that it is half-ash buried and
cracking open, not a pod rising up on a mysterious stalk that wasn't there
before. Regen art."

**Already done by an earlier pass, discovered this session.** A Fable session
delivered 4 half-buried candidates on 2026-09-14
(`Transient/scorchfruit_regen_2026-09-14/`), the owner picked all four as
`Graphic_Random` variants ("Can't we have it have a few options it picks
between"), and a follow-up commit
(`097183478`, "ScorchFruit ships as 4 random ash-buried variants, tint
dropped, stalk art dead") wired them in and deployed. The owner then confirmed
SHIPPED on the ledger 2026-09-16, verbatim: "Love the Item, the pod shouldn't
have a stalk but lay in ashes on the ground." Current def:
`src/RimMandrake/Pyrelands/Defs/ThingDefs_ScorchFruit/ScorchFruit.xml` —
`RM_FE_Plant_ScorchFruit` uses `Graphic_Random` over
`Textures/Things/Plant/RM_FE_ScorchFruitPod/{A,B,C,D}.png`, no `<color>` tint
(the def's own comment records why: `CutoutPlant` multiplies, and
`(150,70,40)` was turning the grey ash to mud).

**Regression found and fixed this session**: a later, unrelated commit
(`c63807a9d`, "Pyrelands: rescue 5 flora textures that lived only in the game
copy", 2026-09-17) ran `deploy_custom_mods.py --pull` and mistook a stale
leftover in the deployed game copy — the OLD single-file
`Textures/Things/Plant/RM_FE_ScorchFruitPod.png` (byte-identical origin to the
one `097183478` deleted, same 33049 bytes) — for lost work, and re-added it to
the repo. Read it: it is exactly the rejected "pod rising up on a stalk"
art — a visible woody stem at the base, floating on a plain background, no
ash. Since Graphic_Random resolves against the folder
(`.../RM_FE_ScorchFruitPod/`), the stray flat file sitting beside that folder
was inert in-game, but it is exactly the inaccurate material the owner ruled
against, sitting live in the repo and in the deployed Mods folder — a clear
case of the CLAUDE.md rule "inaccurate material is DELETED, not
superseded-in-place."

**Canvas-size law check**: `RM_FE_Plant_ScorchFruit`'s
`visualSizeRange` is `0.8~1.1` (≈1 cell). Per
`common.canvas_for_cells()` in `src/RimMandrake/Utils/artpipe/common.py`,
`want = 1.1 * 128 ≈ 141px`, which is below `CANVAS_FLOOR_PX = 256`, so the
correct canvas is the floor, 256px. All four shipped variants are already
256x256 RGBA — no canvas correction needed.

## verify
- Read all four shipped variants by eye against the owner's three notes:
  `RM_FE_ScorchFruitPodA/B/C/D.png` (256x256 RGBA each, confirmed via PIL) —
  every one shows a cracked woody pod, molten interior visible through the
  crack, sitting in a pile of grey ash that covers its lower half, and no
  stalk/stem anywhere in the composition. Matches "half-ash buried", "cracking
  open", and "no stalk" on all four.
- Read the reintroduced flat file
  (`RM_FE_ScorchFruitPod.png`, pre-deletion) and confirmed it is the OLD
  rejected art: an intact pod on a visible stalk, not buried in ash — exactly
  what the owner's note asked to remove. Deleted from the repo
  (`git rm`) and pruned from the deployed game copy via
  `deploy_custom_mods.py --mod Pyrelands --apply --prune` (plan showed the
  single stale line, applied, result: "VERIFIED in sync").
- `validate_patch.py` against `ScorchFruit.xml`, with `--defs` pointed at the
  real Data/Mods/Workshop roots and `--live` at tonight's freshest DefDump
  capture (`2026-09-18T05-05-13Z`): `OK - 0 errors, 0 warning(s)`. (One
  unrelated WARN in the run, `mandrake.rm.fluidcanals` folder not found under
  `--defs` — a pre-existing FlowWorks/FluidCanals rename-tracking issue,
  nothing to do with this def.)
- `PIL.Image.open()` on all four shipped textures: opens clean, 256x256,
  mode RGBA, non-zero byte size (41313–67659 bytes each).

## criteria
ScorchFruit's shipped art shows the pod half-buried in ash, visibly cracking
open with its interior showing, and carries no stalk in the composition — on
every variant, in both the repo and the deployed game copy — with no leftover
copy of the rejected stalk-and-floating-pod art anywhere in either tree.
