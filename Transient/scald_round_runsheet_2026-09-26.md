# The Scald round — pre-flight run sheet, 2026-09-26

_Written by BENCH while the bridge was held by FOUNDRY. Everything below is
MEASURED offline, with the game up under another seat. Nothing here has been
deployed and nothing has been tested. The round is turnkey the moment the bridge
frees AND the Grey Sea wave stops committing into TerminalBiomes._

## Why the round did not run

| blocker | state when written |
|---|---|
| Bridge | HELD by FOUNDRY since 2026-09-26T20:34:42Z, for *live verification of ExplosiveGrowth + Scarlands/Miasma/Sump/Greentide fixes*. Live, inside the 45-min window. Not forced — the owner said hold. |
| Game | **RUNNING** (`./game` measured it; the ledger said DOWN and was corrected). |
| `EnvironmentalHazards` | Its entire drift is `RimMandrake.EnvironmentalHazards.dll` + `.srchash`. Windows refuses to write a memory-mapped assembly while the game runs (`WinError 1224`). Gated on shutdown regardless of the bridge. |
| `TerminalBiomes` | The Grey Sea build wave was still committing into it (`6ab38fd77`, `78097f340`). Deploying mid-flight ships a half-built Grey Sea into the Scald's test and destroys attribution. |

## 🔴 Three pre-flight findings that would each have broken the round

### 1. `LuminousPigment` is neither deployed nor in the mod list — and the Scald now depends on it

MEASURED: the live `ModsConfig.xml` holds **629 active mods** (parsed from
`activeMods`, not grepped). `mandrake.rm.luminouspigment` is **NOT IN LIST**, and
there is no `Mods\LuminousPigment` folder at all.

But commit `8052842e7` (2026-09-26, earlier the same day) created that mod and
**moved the Scald's only franchise-free flora into it**:

- `RM_WelcomeBlanket` → `RM_Crowncarpet`
- `RM_RainbowPigment` → `RM_Deepfire`

and rewrote `TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml`'s `wildPlants` row
plus `About.xml` to depend on the new mod.

⇒ **Deploying TerminalBiomes without also deploying AND listing LuminousPigment
leaves the Scald's `wildPlants` row pointing at a def no loaded mod supplies** —
an unresolved cross-reference, and the franchise-free Scald loses its only
flora. The round is **three** mods, not two.

### 2. `--prune` is REQUIRED on TerminalBiomes, and it is provably safe

Seven `-` lines (in game, not in repo). They are **not** orphans — checking git
history before acting was what settled it:

| game-only file | what it actually is |
|---|---|
| `Defs/ThingDefs_Items/RM_RainbowPigment.xml` | deliberately deleted at `8052842e7`; renamed to `RM_Deepfire` in LuminousPigment |
| `Defs/ThingDefs_Plants/RM_WelcomeBlanket.xml` | deliberately deleted at `8052842e7`; renamed to `RM_Crowncarpet` |
| `Textures/.../RM_Saal/RM_Saal.png` | stale single-file predecessor of the new 3-variant set |
| `Textures/.../RM_ShullaCatch/RM_ShullaCatch.png` | same |
| `Textures/.../RM_BladderboilCatch/RM_BladderboilCatch.png` | same |
| `Textures/.../RM_RainbowPigment/RM_RainbowPigment.png` | deleted with the def at `8052842e7` |
| `Textures/Things/Building/Natural/RUT_ScaldVent.png` | flat predecessor of the new `RUT_ScaldVent/_A`+`_B` folder |

Nothing in that list is an only-copy. Prune is safe.

🔴 **And prune is NECESSARY, because of a `Graphic_StackCount` hazard.** MEASURED
in the game folder right now, each of the three catch folders holds exactly one
file — the stale flat one:

```
RM_Saal/RM_Saal.png        RM_ShullaCatch/RM_ShullaCatch.png        RM_BladderboilCatch/RM_BladderboilCatch.png
```

The Scald wave's new art is `_a`/`_b`/`_c` **inside those same folders**. So a
plain `--apply` leaves each folder holding **four** files, with a stray
non-variant sitting inside a `Graphic_StackCount` directory. Prune clears it.

⚠️ Leaving the two stale XML defs is worse than untidy: with LuminousPigment
deployed, the live game would carry **both** the old welcome blanket and the new
crowncarpet as separate plants.

### 3. The ledger's game state was wrong

`./game` measured **RUNNING** against a recorded **DOWN**; corrected in place.
Never open a round on the recorded state.

## The round, in order, when it opens

```bash
# 0. preconditions — BOTH must hold
python3 src/RimMandrake/rimflow/cli.py bridge who        # must be free, or the owner hands it over
git log --oneline -3 -- src/RimMandrake/TerminalBiomes   # Grey Sea wave must have stopped committing

python3 src/RimMandrake/rimflow/cli.py bridge take --for "Scald round: deploy + quicktest RM_TheScald"

# 1. close the game FIRST — the DLL cannot be written while it runs (WinError 1224),
#    and modset_builder --apply refuses while Player.log is warm (<3 min). Kill, then swap.
#    Copy the old Player.log out before launching — it is overwritten at next launch.

# 2. deploy — plan first, read the plan, then apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod TerminalBiomes --prune       # then --apply --prune
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod EnvironmentalHazards          # then --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod LuminousPigment               # then --apply  (NEW — never deployed)

# 3. add mandrake.rm.luminouspigment to the mod list, or step 2 bought nothing

# 4. minimal list + the three targets, launch via Steam (NEVER the bare exe)
#    poll Player.log for "Bridge token:" — NOT the JawaBench ready line, which is lazy

# 5. quicktest RM_TheScald

# 6. harvest the WHOLE log, not just what changed
python.exe src/RimMandrake/Utils/harvest_log.py

# 7. restore the 629-mod list. Leaving his machine on the minimal list is the one
#    unacceptable outcome.
```

## Decision strings to write BEFORE launching (load-round skill §2 — still owed)

Not yet written. Each item riding this load needs its exact `Player.log` string,
its baseline, and what each outcome means — **including an expected-PRESENT
string**, because absence of an error line is necessary but not sufficient.

Items riding it: `SCALD_MECHANICS_1` (its only remaining bar), plus confirmation
of `SCALD_ART_UPGRADE_WAVE_1`, `SCALD_WATER_AGITATION_FLECKS_1`,
`SEA_FISHABLES_ALIVE_IN_DEPTHS_1` (Scald) and `SCALD_STEAM_WEATHER_DESIGN_1`.

⚠️ One assembly (`EnvironmentalHazards`) rides this load. Per the skill's §3 that
is fine solo, but if the Grey Sea wave has also rebuilt a DLL by then, write one
expected-failure signature per assembly into
`infrastructure/state/EXPECTED_FAILURES_next_load.md` **before** launching. A
signature invented after reading the log is a story that fits, not evidence.
