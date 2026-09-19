## Spec
All 7 juvenile ThingDefs in `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_MiasmaNurseryJuveniles.xml`
(`RSW_MeeJuv`, `RSW_FaaJuv`, `RSW_LaaJuv`, `RSW_YobshrimpJuv`,
`RSW_SiltLampreyJuv`, `RSW_RustNipperJuv`, `RSW_OpeeSeaKillerJuv`) load with
a **null `thingClass`** — confirmed new on the 2026-09-10 restart (absent
from the prior load's log entirely) via
`python.exe src/RimMandrake/Utils/check_config_errors.py`:

```
Config error in RSW_FaaJuv: has null thingClass.
Config error in RSW_FaaJuv: animal has trainability = null.
Config error in RSW_FaaJuv: renderTree is null.
Config error in RSW_FaaJuv: RSW_FaaJuv has no combatPower.
```
(x7, one block per species — same four lines each)

This is the "whole ThingDef discarded" failure class (`MANYWATERS_COLOR_SUPPORT_1`
hit the same signature from a different cause). A reviewing subagent
(`ab04b4d40052f3631`, tonight) read this exact file in full and found it
"clean as-is" against the file's OWN documented design (the life-stage-
capping mechanism) — it did not catch this runtime symptom, because a
static XML read can't see def-inheritance resolution failing.

Each of the 7 ThingDefs uses `ParentName="RSW_<name>" MayRequire="mandrake.rsw.swbestiary"`,
where `RSW_<name>` is a real, active ThingDef (`Name="RSW_<name>"`, itself
`ParentName="AnimalThingBase"`) defined in
`src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Scalefish.xml`
(confirmed present, confirmed the mod is active in the live 579-mod
ModsConfig.xml). The matching PawnKindDefs use the identical pattern.

**ROOT-CAUSED 2026-09-11 (real ground truth, live Player.log, not guessed):**
grepping the actual live `Player.log` (the same 579-mod, 2026-09-10 23:41
load the Config errors above came from) for the surrounding lines shows the
REAL failure, one line before every "null thingClass" block:

```
XML error: Could not find parent node named "RSW_Mee" for node "ThingDef".
XML error: Could not find parent node named "RSW_Mee" for node "PawnKindDef".
```

(x7, one pair per species — both the ThingDef AND the PawnKindDef fail to
find their parent, not just one). This is `Verse.XmlInheritance.GetBestParentFor`
returning null because `nodesByName["RSW_Mee"]` (etc.) has NO entry at all —
i.e. the abstract adults (`Name="RSW_Mee"` / `Name="RSW_Faa"` / … on the
ThingDef+PawnKindDef pairs in SWBestiary's `SeaBeasts_Scalefish.xml` /
`SeaBeasts_Opee.xml` / `SeaBeasts_Swarm.xml`) were **not present in the
running game at all** under those Name attributes. `ResolveXmlNodeFor` then
falls back to `node.resolvedXmlNode = node.xmlNode` — the Juv's own tiny raw
XML, unmerged — which is exactly "null thingClass / trainability=null /
renderTree=null / no combatPower": none of those fields exist on the Juv's
own explicit XML, only on the (unreachable) parent.

**The actual cause: deploy drift, not an XML-authoring bug.**
`git blame` on `SeaBeasts_Scalefish.xml` line 11 shows the `Name="RSW_Mee"`
etc. attributes were added and committed in `4b1f5b71` ("Miasma nursery:
juvenile-locked sea beasts, wildAnimals patch") — the SAME commit that added
this Juv file. The repo copy was correct and clean (`git status --porcelain`
on the whole `src/RimStarWars/SWBestiary/` tree: nothing uncommitted). But
`deploy_custom_mods.py --mod SWBestiary --apply` was never re-run after that
commit, so the LIVE `Mods/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/*.xml`
on disk still had the pre-Miasma versions — `<ThingDef ParentName=
"AnimalThingBase">` with **no `Name=` attribute at all** — confirmed by a
byte diff between the deployed copy and the repo copy (5 files differed:
the 3 SeaBeasts_*.xml plus 2 unrelated stale files, `RSW_MlieWaveB_Bodies.xml`
and `RSW_Absorbed_Protovermes.xml`, also now caught up). Exactly
CLAUDE.md's "writing a file is not deploying it" — the fix landed in the
repo, was never shipped to `C:\Program Files (x86)\Steam\steamapps\common\
RimWorld\Mods`, and the live game had nothing for `ParentName="RSW_Mee"` to
find.

**Fix applied:** `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod
SWBestiary --apply` (plan reviewed first, git status on SWBestiary clean —
no other window's uncommitted work at risk). Post-deploy, the live and repo
copies of all 3 SeaBeasts_*.xml are byte-identical (verified via `diff`,
exit 0). `validate_patch.py` against the full live 579-mod set (Data + Mods
+ Workshop 294100, `--mods-config` the live ModsConfig.xml) now reports
`OK - 0 errors, 0 warning(s)` for `RUT_MiasmaNurseryJuveniles.xml`, including
its ParentName-resolution check.

**Not yet proven on an actual NEXT LOAD** — no cold restart was triggered by
this fix (out of scope for a scoped bug-fix pass; restarting is FOUNDRY's/
BENCH's call). The deploy diff and validate_patch.py's parent-resolution
pass are strong evidence the fix is real, but the criteria below ask for the
Config-error lines to clear on a real load — whoever restarts next should
confirm via `check_config_errors.py` that none of the 4 lines recur for any
of the 7 species.

## Verify
```
PROVE   the actual merged ThingDef for RSW_FaaJuv (or any of the 7) via
        jawa/get_defs (real schema, not guessed) or a fresh RimSage def-dump
        index that includes tonight's mods
EXPECT  either thingClass resolves correctly once queried properly (meaning
        the ConfigError is itself a false/misleading signal), or a genuine
        inheritance-resolution failure is visible in the merged def
LIES    a clean validate_patch.py run says nothing about this -- it's a
        runtime inheritance-resolution symptom, not an XML-patch-matching one
```

## Criteria
- [x] Real root cause identified (not guessed) via a live/fresh-dump def read
      — live Player.log's own "Could not find parent node named" lines, plus
      a byte diff proving the deployed SWBestiary copy was stale.
- [x] Fix applied to all 7 species uniformly (same mechanism, same fix) —
      one `deploy_custom_mods.py --mod SWBestiary --apply` fixes the shared
      cause (all 7 inherit from the same stale-deployed adult defs).
- [ ] `has no combatPower`/`trainability = null`/`renderTree is null`/
      `has null thingClass` all clear on the next load for all 7 — NOT YET
      confirmed on an actual restart; deploy diff + validate_patch.py's
      ParentName-resolution pass are the evidence so far.
