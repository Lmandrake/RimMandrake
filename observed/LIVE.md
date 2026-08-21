## 🔴 The def-dump collision fix IS DEPLOYED and the dump IS ARMED — CHECK, 2026-08-21 12:50

`REGISTRY.jsonl`'s `OFFICIAL-2026-08-21` entry says the producer fix is
*"fixed in d7cf154, undeployed"*. **That half is now wrong — measured, not assumed:**

| reading | result |
|---|---|
| `git hash-object` of the repo DLL vs `git rev-parse d7cf154:<same path>` | **identical** — `648cf742…` |
| `md5sum` repo DLL vs the deployed game copy | **identical** — `8b9e89bb…`, 26,112 bytes both |
| `deploy_custom_mods.py --mod RimDefDump` | `in sync (2 files)` |
| `DefDump/dump_request.txt` | `all` — armed at 12:36 |

⇒ **The next cold load produces a clean, collision-free capture with no further action.**
The 824 defs lost to 8 filename collisions come back on that load; colliding types get
`<FullName>.json` and the manifest carries a `defTypes` index.

⚠️ **What is still TRUE about the frozen capture:** `OFFICIAL-2026-08-21`
(`capturedUtc 2026-08-21T08:20:20Z`) predates the DLL build (10:02) and therefore **is**
damaged. A count of a shadowed type off that capture is **UNMEASURED, not zero** — the
registry's `knownDamage` is right about the artifact and stale only about the deploy.

🔑 **What remains is the OWNER's and only his.** After the load, `refresh.py` will report
**`REPLACED`** — that is the freeze detector working, not a fault. Re-freezing is not
automated and an agent must not do it. The command, in full:

```
python3 src/RimMandrake/rimflow/cli.py note --seat OWNER   # (see dumps/README.md — the freeze is a registry append)
```

⇒ Append one line to `infrastructure/state/dumps/REGISTRY.jsonl` with a new `id`
(`OFFICIAL-2026-08-22` or the day's date), `supersedes: OFFICIAL-2026-08-21`, the new
`capturedUtc` read out of `manifest.json`, and a `knownDamage` that now says the
collisions are FIXED. Owner, 2026-08-21: *"deploy the fix, re-capture, re-freeze."*


## Def dump, 2026-08-21 — two read-traps measured on the 578-mod dump

- 🔴 **`BiomeDef.wildAnimals` lists ALL 1024 animals on ALL 80 biomes**, with the absent ones
  at `commonality: 0`. A substring search for a defName returns **80 of 80** and means
  nothing. The membership test is `commonality > 0`. Measured against `IceSheet`, `Ocean`
  and `Space` (all zero) versus `Wasteland` 1.2, `ExtremeDesert` 0.5, `ZBiome_DesertOasis` 0.8.
- 🔴 **`PawnKindDef.xenotypeChances` is absent from the dump entirely** — zero of 1736
  PawnKindDefs carry the key. A check on it off the dump is UNMEASURED, never failed.
  `useFactionXenotypes` IS present on all 1736 and is safe to read.
- ⚠️ **`BiomeDef` carries no `texture` field in the dump either**, so a world-texture check
  cannot be done offline from it. Read the mod XML or look at the planet.

## 2026-08-21 — two things we had recorded as impossible, and both are now routine

🔴 **A MAP CAN BE CREATED FROM THE WORLD SCREEN, WITHOUT LANDING.** Owner, 08:19: with
**godmode on, click a tile and take `DEV: Generate Settlement` from the lower left.** It
builds an empty settlement map; a colonist can then be spawned into it. This is the route
CHECK looked for and did not find on 2026-08-21 04:00 — `list_debug_action_children("Actions")`
NREs at the world screen (documented), so the action is unreachable by enumeration and has
to be reached through the tile's own context menu.
⇒ **A quicktest map no longer costs a landing site or a colony**, and a world can be kept at
`maps 0` for painting and given a throwaway map afterwards.

🔴 **SAVES DO ROUND-TRIP ON THIS MOD LIST. Retire "no save loads."** Owner saved the
generated map and loaded it back, 2026-08-21 08:25, 13.2 MB, and the game came back healthy —
`maps 1`, a live colonist, `ErrorWhileLoadingGame 0`, `Exception in FinalizeLoading 0`.
⚠️ **The qualifier is load-bearing: this is the list WITHOUT `thereallemon.factioncontrol`.**
With it active, three separate saves aborted at
`FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix` — see
`LOAD_ABORT_IS_FACTIONCONTROL_1`. So the correct statement is *"saves load once FactionControl
is out"*, not *"saves load"*, and anything asserting either without naming the mod list is
unsafe.
⭐ This is also the first evidence that a save carrying a **MAP** survives the round trip; the
earlier clean load was a world with `<maps />` empty.

## 🔴 `jawa/spawn_pawn`'s `faction` parameter decides the pawn's SPECIES — 2026-08-21

`faction: "hostile"` drops the pawn into whatever faction currently opposes the player, and
**all 67 of our PawnKindDefs carry `useFactionXenotypes: true`** — so the xenotype comes from
the faction the pawn JOINS, not from the kind.

⇒ Spawning a roster test with `faction: "hostile"` measures the wrong faction's
`xenotypeSet`. It produced a reading of **"49 of 55 kinds spawn Baseliners"**, which looked
like the whole species roster being broken and was entirely an artifact. Re-spawned into
their own factions, the same kinds return Geonosians 4/4, MandrakeJawa 5/5, and a
five-species mercenary company.

✅ **Always pass the kind's OWN faction defName when testing a roster.** `hostile`, `player`
and `none` are for combat and staging tests, not for anything that reads what a pawn IS.

⚠️ And `xenotypeChances` cannot settle this offline — the key is absent from all 1,736
PawnKindDefs in the dump, so a dump answer is UNMEASURED. `useFactionXenotypes` IS present
and is the field that tells you the faction decides.
