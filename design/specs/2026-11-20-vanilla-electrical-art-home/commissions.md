# The first commissions, 2026-11-20 (item RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART)

## The resolution rule used

128 px per cell of `drawSize`, rounded up (owner 2026-08-23, `skills/generating-rimworld-sprites/SKILL.md` "128 px per
cell of occupancy"; the creature rule he pointed at). Battery `drawSize (2,3)` -> north/south 256x384, east 384x256.
Wall lamp `drawSize 1` -> 128 per facing. UI icons have no world size: 256 square (a gizmo is drawn 75 px at UI scale 1,
about 150 px at UI scale 2).

## How the art was made, and why not through the art daemon

All 15 jobs filed to the artpipe daemon at 15:51 PST FAILED in about 3 s each: the daemon's Codex worker homes
(`~/.codex_workers/artpipe/w0..w4`) hold an `auth.json` last refreshed 2026-11-10 whose refresh token is dead ("refresh
token was already used. Please log out and sign in again"). Every artpipe job fails until those homes are signed in
again. Copying `auth.json` between homes forks the token lineage (`generating-rimworld-sprites` traps), so the art was
rendered serially on the shared Codex home with `art/gen_direct.py`, the same route the standing lamp's four looks took
in October (`src/RimMandrake/Utils/mockups/messy_conduit/round5_art_jobs.py`). Prompts: `art/make_jobs.py`. Each
north/south facing is an edit of its look's east picture, so the facings are the same object. Conform (size, position):
`art/install_vea_art.py conform`. Raw renders: `D:\ClaudeWork\rimmandrake\scratch\vea_20261120\raw`.

## The judge

GPT through `src/RimMandrake/Utils/gpt_consult.py` against `design/RimMandrake/art_judge_brief.md`, on judge sheets that show each
picture at 128 px per cell beside a vanilla colonist at the same scale (`scale_panel.human_sprite`) and at 32 px per cell.
The judge did not make the art. A first round without the colonist returned UNSURE on every picture (D1: no true-scale
panel) and decided nothing. Verdicts, every round: `infrastructure/state/delegated/2026-11-20/{VEA_Icons,Battery,WallLamp}.json`.
Judge sheets: `art/judge_sheets/`.

| commission | pictures | judged | result |
|---|---|---|---|
| 1. battery, four looks (east + north; south = north) | 8 (+2 redraws) | yes, 3 rounds for Modern | Scrapper, Industrial, Futuristic KEEP. **Modern: east KEEP, north REDO three times** (C2: the north facing is not the same size as the east one; first too small, then its front face too tall, then too shallow). Stopped there; the Modern battery is owed. |
| 2. standing lamp, re-examined | 0 | n/a | All four GSS looks are **128x128 on a 1-cell lamp = 128 px per cell [measured]**, at the standard: none regenerated. Their real detail was checked too (a 64 px round trip loses RMSE 18-29 of their colour, so they hold more than 64 px of detail). The low-resolution lamp a player sees is the **unstyled** lamp, which draws vanilla's 64 px `LampStanding`: any lamp built without a picked look, or one an ideoligion styled. |
| 3. wall lamp, four looks (east, north, south; west mirrors east) | 12 (+2 redraws) | yes | **12 of 12 KEEP** after redrawing Modern north and Modern east (both C2 size mismatches). |
| 4. power pole buttons: Link wire, Unlink wire, Unlink all | 3 | yes | **3 of 3 KEEP.** |
| 5. one icon per look, shared by every mod with the looks | 4 | yes | **4 of 4 KEEP.** |

**26 kept pictures are in the art store** (`art.py put`), each with its sha and planned texture path in
`art/put_record.json`. Planned paths:

- wall lamp: `src/RimMandrake/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Styles/<Look>/WallLamp_{north,east,south}.png`
- pole buttons: `.../GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/UI/Commands/{LinkWire,UnlinkWire,UnlinkAll}.png`
- look icons: the same picture at `RimMandrake/<Mod>/UI/Looks/<Look>.png` in Gimme Some Slack and FlowWorks (each mod
  ships its own copy at its own texPath root, `design/NAMING_SCHEME_PLAN.md`)
- battery: Machine Looks (`design.md`), a mod that does not exist yet

## Why nothing is installed in a mod yet, and why there is no review sheet yet

- **A new PNG under Gimme Some Slack's `Textures/` turns `selftest_gss_stub_art_census.py` red** until it gets a row in
  `Source/Core/StubJoinAudit.cs` (`StubArt.Census`). That is a C# change and a DLL rebuild of the mod whose 0.1.0 just
  passed, so it belongs to the GSS version that wires the art: the pole buttons are a fault fix (today a red X), so
  **0.1.1**; the wall lamp and the look icons in the style menu are new features, so **0.2.0**. The battery waits for
  Machine Looks.
- **The gated sheet builder cannot show candidates that are installed nowhere beside a vanilla-only row.**
  `art_sheet.py --textures` with the pictures as `reference_textures` fails `scaled_review_gate.py` req 3 ("donor art only
  and no pending/active render job") for the wall-lamp rows, because reference pictures do not count as ours. An earlier
  build passed only because the texPath lookup for the vanilla battery put a **wrong picture** (a suit charger) in the
  battery rows' IN GAME column; that sheet,
  `Transient/biome_ffar/vanilla_electrical_looks_sheet_2026-11-20.html`, is wrong and must not be served (the hook keeps
  agents from deleting sheet files; it is untracked and expires). The sheet is built when the art is installed with its
  wiring: then every row has art of ours and the builder works as designed.

## The battery's charge bar [UNMEASURED]

The game draws the battery's charge bar over the middle of the picture. Each look has a dark gauge window there, but
whether the window lies along or across the bar, in each facing, was not checked in game. Check it at the first live
look at Machine Looks.
