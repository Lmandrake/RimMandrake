## spec
Found via `harvest_log.py` on game UP 2026-09-11 (570-mod session): "Outer Rim
new-mod errors" RED, 8 above baseline 0.

```
885/890/895/900: Verse.PatchOperationAdd(xpath=.../ThingDef[defName="OuterRim_DroidWeapon_{BlasterCannon,TwinWristBlaster,WristBlaster,WristBlasterIon}"]"): Failed to find a node with the given xpath
1130/1132/1134/1136: [RimStarWars Patches] Patch operation PatchOperationConditional(.../weaponTags) failed
```

Root cause (confirmed on disk, not inferred): `src/RimStarWars/StarWarsPatches/Patches/WeaponTags_Renormalise.xml`
has 4 `PatchOperationConditional` blocks (one per defName above) whose `nomatch`
branch adds `<weaponTags>` directly to the `ThingDef` node. When the ThingDef
itself doesn't exist, BOTH `match` and `nomatch` fail — there's no guard for
"the donor mod isn't active" the way this file's *other* operations don't need,
because those donors are active.

The 4 defNames are defined only in **`Neronix17.OuterRim.DroidDepot`**
(Workshop id 3096501398, `Defs/ThingDefs_Weapons/Droid_Weapon_BlasterCannon.xml`
in its 1.6 folder) — confirmed by grep on the actual mod files on disk. That
sub-mod is **not in the current 570-mod ModsConfig.xml**, while
`Neronix17.OuterRim.Core`/`GalacticEmpire`/`RebelAlliance`/`FurnitureAndDecor`
ARE active. Whether DroidDepot's absence from this list is intentional curation
or drift is unknown — not this item's call (see Watch out).

⛔ **`WeaponTags_Renormalise.xml` is GENERATED — do not hand-edit it.**
Regenerate only via `python3 src/RimMandrake/Utils/weapon_tag_audit.py`, and
🔴 never against a post-patch def dump (see the file's own header: a naive
regenerate today would emit 9 ops against the 154 already there, silently
deleting 145). The real fix belongs in the generator: wrap any operation whose
defName's owning mod is not universally active behind a `PatchOperationFindMod`
(`mods=["Neronix17.OuterRim.DroidDepot"]`) — check whether the generator
already tracks per-defName donor packageIds (it would need to, to build this
guard) before assuming the plumbing exists.

## verify
- With DroidDepot inactive: 0 "Failed to find a node" / "Patch operation ...
  failed" lines for these 4 defNames in a fresh `Player.log` (harvest_log.py
  clean on "Outer Rim new-mod errors").
- With DroidDepot active (if ever re-enabled): the 4 operations still fire and
  tag the weapons correctly — a `PatchOperationFindMod` guard must not silently
  swallow the real case too.
- `weapon_tag_audit.py` regenerate-and-diff still reports the expected op count
  (154 today) plus the new guard wrapper — no silent operation loss.

## criteria
- No live-log errors from this file when a patched defName's donor mod is
  absent, for these 4 or any future ones the generator's guard logic covers.
- Fix lands through the generator, not a hand-edit of the XML.

## Watch out
🔑 This is entirely a static/offline fix (generator logic) — no live game or
bridge needed to build or validate it (validate_patch.py + a dry-run regen
diff is enough); only the FINAL confirm needs a live log read, which the next
UP window can do for free.

⚠️ Before touching the generator: confirm with the owner (or check
`design/Jawa/worldbuilding/` / recent commits) whether DroidDepot being absent
from the active list is a deliberate content decision — if OuterRim droid
weapons are being retired project-wide, the right fix might be deleting these
4 operations outright (`inaccurate material is deleted, not superseded`
doctrine) rather than guarding them for a donor that's never coming back.
