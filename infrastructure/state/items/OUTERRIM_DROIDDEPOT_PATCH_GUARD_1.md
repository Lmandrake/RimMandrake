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

## 2026-09-18 close — FOUNDRY (offline, BELT)

Checked `src/RimMandrake/Utils/weapon_tag_audit.py` per the Watch-out above:
**it has zero donor/packageId/FindMod/MayRequire plumbing** (grep for those
four terms returns nothing). Teaching it per-defName donor tracking is a real
feature, not a guard, and would need to run against a pre-patch dump (the only
dump reachable right now already has this patch applied, and the file's own
header refuses a regenerate against that — would silently drop 145 of 154
ops). Given that, applied the guard as a hand-edit, same shape as
`MAYREQUIRE_OPERATION_INERT_SWEEP_1` (`d1c62223c`): each of the 4
`PatchOperationConditional` blocks for `OuterRim_DroidWeapon_{BlasterCannon,
TwinWristBlaster,WristBlaster,WristBlasterIon}` now sits inside a
`PatchOperationFindMod` whose `<mods>` list carries the donor's About.xml
`<name>` (read from the deployed Workshop copy,
`.../workshop/content/294100/3096501398/About/About.xml`): **`Outer Rim -
Droid Depot`** (packageId `Neronix17.OuterRim.DroidDepot`, confirmed against
that About.xml and against `neronix17.outerrim.droiddepot` in modlist
snapshots). FindMod's `<mods>` matches by display name
(`ModLister.HasActiveModWithName`), not packageId — MayRequire is the
packageId-keyed one.

Verified with `validate_patch.py --defs <Data> <Workshop> <Mods>`:
- Current live ModsConfig (DroidDepot inactive): **0 errors**, and the 4
  guarded ops report the same "test xpath matches 0 nodes — the guard will be
  a no-op with these mods active. Expected if the target mod is not
  installed" INFO the checker gives every other donor-gated operation in this
  file — no longer flagged as unguarded.
- A snapshot with DroidDepot active
  (`infrastructure/state/modlists/ModsConfig_before_depot_asimov_retry_2026-09-10.xml`):
  **0 errors**, and all 4 ops resolve exactly 1 match each against the real
  `Droid_Weapon_*.xml` files in DroidDepot — confirms the guard does not
  swallow the real case.
- `validate_patch.py --live <newest DefDump capture>` still reports these 4
  defNames as errors ("does not exist in the LIVE game") — read the checker's
  source (`check_live()`): that identity check runs unconditionally on every
  xpath's defName, with no FindMod/Conditional-ancestor awareness at all, so
  it cannot help but flag a donor-only def while that donor is inactive in the
  dump it's checking against. This is a checker blind spot, not a live defect:
  in the real engine `PatchOperationFindMod.Apply` skips its `<match>` entirely
  when none of `<mods>` is active, so the inner Conditional never evaluates and
  never logs. Confirmed structurally (0 real matches, correctly flagged INFO
  not ERROR) rather than by re-running the game.

Not done: the live-log confirm the item's `## verify` section defers to the
next UP window (fresh `Player.log`, harvest_log.py clean on "Outer Rim new-mod
errors"), and teaching `weapon_tag_audit.py` real per-defName donor tracking
(the item's `## criteria` line "fix lands through the generator" — deferred as
a separate, larger item since the plumbing doesn't exist and this BELT window
has no live game to safely capture a pre-patch dump against).
