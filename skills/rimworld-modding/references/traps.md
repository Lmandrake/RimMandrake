# traps.md — earned lessons, by topic

Every entry below cost a real debug cycle. **Read the one file that matches what
you are about to do**, not all of them.

| If you are about to… | Read |
|---|---|
| write or debug a patch, an xpath, or a def | [`traps-xml-and-defs.md`](traps-xml-and-defs.md) |
| trust what a script, grep, census or the def dump just told you | [`traps-tooling.md`](traps-tooling.md) |
| call art missing, wrong, or broken | [`traps-art.md`](traps-art.md) |
| chase a mod that is absent, dead, or ignoring its files | [`traps-mods-and-managers.md`](traps-mods-and-managers.md) |
| believe a diagnosis, or call into a running game | [`traps-diagnosis.md`](traps-diagnosis.md) |
| give a creature flight, or touch a flyer's def or art | [`flight.md`](flight.md) |
| add a comp to a plant, guard a patch with `MayRequire`, or add a `.cs` to a hand-listed csproj | [`project-engine-facts.md`](project-engine-facts.md) |
| **write or debug a quest** | **a different skill: `skills/rimworld-quests/`** |

**If you only read one, read `traps-tooling.md`.** The single most repeated
failure in this project is not a wrong patch, it is **a tool that answered
confidently — and answered a different question than the one asked.**

## Appending

At the end of a task, if something surprised you, append it to the matching file:
what it looked like, what was actually true, what worked. Keep it to a few lines.

**It goes in only if it is specific, non-obvious and RimWorld-bound** — an error
string, a flag, an xpath, a defName, a number — **and still true today.** General
software or process advice is not a trap; that is what made this log unusable
once already. If it would change what `SKILL.md` tells you to do by default, put
it in `SKILL.md` instead and do not log it here.

**Never number an entry, and never cite one by number, line or heading.** Say
"as per the trap file" and stop.

## Generators that rewrite shared output
- **`modcheck/required_checks.py` ignores `--help` and rewrites `required_checks.json` for EVERY mod from the working tree**, so in a shared clone it bakes peers' uncommitted scripts (e.g. a `validation.py` with no suite) into the manifest. Regenerate it only from a clean tree, or at a landing that owns every changed script. Its `load_error` embeds the clone's absolute path (DeepDrill, TileFeatures), so every regeneration churns those two rows. Likewise `mod_archive.py build`/`add` rewrites every About copy and the whole `ALL_ORIGINAL_MODS.tsv` from the live disk (32 About files, 1500 tsv lines): after `add`, restore everything but your row.
- **`retarget_donor_patch.py` renames donor-named blocks onto the `RSW_`/`RM_` twin even when a twin block already exists**, so a generated per-animal file ends with two blocks for one def and the later one wins (AnimalTolerances_Ashkarr: 56 pairs; the later raw-band pin undid the fitted ComfyTemperature band on 61 bounds, a silent hard spawn gate). After any retarget pass check generated patch files for repeated xpath writes with differing values and keep the widest. `gen_vault_layouts.py` and `gen_vault_quests.py` are byte-reproducible offline (run them; `git diff` must be empty); `gen_races_mod.py --check` proves the StarWarsRaces defs.

## FlowWorks hose links and SelfTest pins
- **`RM_HoseLinks` slot cache reaches some inputs only through its 60-tick phased audit, not the same tick:** a trail cleared and refilled to the same length with the same far cell (`KeyOf` folds trail identity+count) matters only for HoseCut over a raised leaf; a port changing owner by `SetFactionDirect` bypasses the `SetFaction` topology patch (the liquid net has the same gap); a leaf built already raised was folded into GlobalKey via `RM_Drawbridges.RaisedLeafCount`. The pre-Move `RM_HoseLinks.Live` check still re-reads HoseCut/Spawned at transfer. FlowWorks SelfTest `Src()` collapses whitespace runs to one space, so source pins must use single spaces; `selftest_flowworks_stock.py` waits silently on the seat dotnet lock (an empty log on timeout means queued, not hung).

## Searching for our own work
- **A mod NAME match is not a mechanism match, and an installed-mod `About.xml` sweep cannot find our own mods.** `Terramorph` in the Mods folder is OUR art override for the `AA_Terramorph` creature, not a terraforming mod (the real slow-terraform donor is Fertile Fields 1.6, workshop 3225843229, license unstated: pattern only). 'Moving dunes' and 'sand swimmers' are our mods (`mandrake.rm.movingdunes`; the sand-swimmer work is spread across FlowWorks and SWBestiary). Search `src/` and item ids for our own work, not installed mods.
