# Deploying: inspect the consumer, and the pre-flight against the live mod list

Split out of `SKILL.md` 2026-08-19. The deploy PROCEDURE is `skills/rimworld-deploy/SKILL.md`;
this file is the part that is about proving a deploy actually reached the running game.

## 🔴 Inspect the CONSUMER, not the artifact

**Ask what the consumer last read, and when.** The process start time IS the
def-read time — RimWorld reads defs **once, at launch** — so anything under
`Mods/` newer than that StartTime is not loaded. **The three commands, and two
measured cases (a `GenStepDef` and a DLL) that both reported done and were both
false, are in `references/traps-mods-and-managers.md`.** Run them before calling
anything live.

⚠️ **Map-generation defs need MORE than a restart: they need a map generated after
it.** Loading a save re-runs no GenStep, so a correct fix is invisible on an old map.
The same holds one layer up: `xenotypeSet` is read at **pawn generation**, so a
patch landing after a world exists never fixes that world's colonists — and it
lives on the `PawnKindDef`, not on the `XenotypeDef` of the same name.

⚠️ **The bridge cannot answer this for you** — `jawa/get_def` returns the def that was
*loaded* and does not expose most fields, so a successful read is not proof the def is
current. **The mtime is the evidence.**

⭐ **Say which one you checked.** "Deployed" is a claim about disk; "live" is a claim
about a process. A report that does not distinguish them will be read as the stronger
of the two.

## Pre-flight: check the DEPLOYED copy against the LIVE mod list

Before a load you cannot repeat, run the check that neither the repo nor the
validator can do — **the game copy against the mod list it will actually load
with**. Both halves are needed; each hides a different failure.

1. **`deploy_custom_mods.py` with no `--apply`**, and read every mod's line. A def
   repointed in the repo and never deployed leaves the GAME holding the old
   reference. Six faction defs sat in exactly that state an hour before a launch.
2. **Resolve every `MayRequire` in the deployed defs against the live list.** 🔴 **A
   rename pass has to move the GATE as well as the name.** `<RimMandrakeGeonosianVariants
   MayRequire="btd.xenotyperemix.starwars">` names our def behind a mod that was
   just switched off, so the node is dropped at load and the faction's
   `xenotypeChances` is silently empty. The defName was right and the gate was a
   corpse. A dead gate on a mod that was NEVER active is fine — that is
   optional-compat working.
3. **Parse `activeMods`; never quote a number you read earlier.** With several
   seats sharing one install the count moved 582 → 580 → 578 → 576 inside an hour.
   `grep -c "<li>"` also over-counts by the 5 `knownExpansions`.

⚠️ **`validate_patch.py` resolves against the CURRENT load set, so `0 errors` cannot
prove independence from a mod you are about to REMOVE** — every stale reference
still resolves while the donor is installed. If you are retiring a mod, the check
is a separate pass that drops each departing packageId and asserts nothing points
there. Ours prints `references that die 0`.
