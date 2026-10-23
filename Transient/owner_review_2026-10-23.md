# Owner review, 2026-10-23 (FOUNDRY bridge helper)

**Nothing from this sitting is ready for you to walk yet.** One save was made, and it is withheld because it is broken.
The four biome saves were not made: the game was in use for your save-e walk.

## FlowWorks

| save | state | why |
|---|---|---|
| `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_Review_FlowWorks_20261023.rws` | **WITHHELD, do not walk** | Pre-review found two problems. (1) Every dug water square, and a painted vanilla lake, draws as flat grey-brown with no water look. The test map was a biomes_sprint quicktest on RM_TheRot. (2) Every frame came out zoomed in on a fraction of its row. Filed as `WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT`. |

What the save would show once the water draws correctly (grid key; site origin 100,100 on a 250x250 map):
- **Ladders and pits:** four 3x3 pits, 3 deep (x 100-120, z 100). Spikes, dry and under 1 m (z 108).
- **Water-depth ladder:** 0.2, 0.5, 1, 1.5, 2 and 5 m, plus a dry 1 m hole (z 134).
- **Hoses:** pump, pipe and hose girth scenes (x 170-212, z 100-165).
- **Picks** (z 172-186):
  - a pipe faucet fed from a tank (x 100-106);
  - a 4 m pit with steel guardrails on its north and east lips, the other lips bare (x 111);
  - a canal joining a vanilla lake at 2.5 m of water, and one joining a dug pond at 1 m (x 121-135): do they read as one colour?
  - a 2 m canal holding 1 m of water, to show the wall depth band (x 138).

Your FlowWorks walk today is BENCH's save e.

## Four biomes (Pyrelands, Leaning Scrub, Cauldron, Contagion)

**Not staged.** The game was deployed and loaded on the `biomes_sprint` tier at about 06:20 PDT. BENCH then took it for your save-e walk, and the bridge is held for you. No biome rows were run and no biome save exists. The plan is unchanged and is in `D:\Luke\dev\RimMandrake\Transient\four_biomes_review_package.md`:
- Pyrelands: the calm2 fixture, `--tag calm2 --tile 5`.
- Cauldron: a fresh map for `vent_gardens`.
- Leaning Scrub: its rows, but the warden rows are now gone with the fluff cut.
- Contagion: its rows.

## What was caught this sitting

- FlowWorks live session: 95 rows on a fish map, 64 PASS / 9 FAIL / 21 UNMEASURED. Every finding is filed on its item:
  - colonists keep getting bruised, which voided most liquid and hose rows;
  - trench cover reads 0.493 against a bar of 0.441;
  - a downed pawn was not rescued from a 5 m pocket;
  - a raid island was not sealed;
  - validation_v2 is missing the new wet-cost toggles.
- A dangling BlueDesert sound reference left by a fluff cut: `ABLATION_SOUNDS_FIX_CUT_LEFT_AN_ECHO`.
