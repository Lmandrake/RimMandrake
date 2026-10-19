# RimStarWars: Trophy Craft — validation walk
subject: src/RimStarWars/TrophyCraft  (packageId `mandrake.rsw.trophycraft`)
deps: `mlie.starwarsanimalcollection` (the donor Wyyyschokk the drop patch targets; the patch is a quiet no-op without it)
list: no named modset_builder tier yet; the smallest tier is BRIDGE + the donor mod + `mandrake.rsw.trophycraft` + the five DLCs
status-hint: TROPHY_CRAFT_FIRST_SCRIPT_1 — wyyyschokk fang drop (a trade good); the fang pendant, its recipe, the neck layer and the observer thought were removed (owner, picks_icons_sheet_2026-10-19: "drop"); first script drafted, never run live

Sources: `src/RimStarWars/TrophyCraft/About/About.xml` description, `Defs/**`, `Patches/RSW_TrophyCraft_WyyyschokkFangDrop.xml`, `Source/*.cs`.

## must be true
Agent-owned, not hashed. Chains and components are in `src/RimStarWars/TrophyCraft/validation.py`.
- Every def the mod ships loads in the running game (the fang), and the donor `Wyyyschokk` it patches is present; a def that fails to load is dropped whole and silently. [About.xml; `Defs/`] → defs_resolve.every_shipped_def_resolves, defs_resolve.donor_wyyyschokk_resolves
- The def-probe instrument can say "not found". [method] → defs_resolve.control_probe_can_say_absent
- Both Mod Settings fields (the opinion toggle and multiplier, left in Source/ after the pendant's removal and read by nothing) write and read back, numbers numerically, and restore. [`RSW_TrophyCraftSettings.cs`; CLAUDE.md "superb Mod Settings"] → settings_roundtrip.settings_probe_finds_fields, settings_roundtrip.socialConsequenceEnabled_round_trips, settings_roundtrip.opinionMultiplier_round_trips
- A butchered wyyyschokk drops fangs: the donor def's `butcherProducts` carries `RSW_WyyyschokkFang`, and an unpatched animal's does not. [`RSW_TrophyCraft_WyyyschokkFangDrop.xml`] → fang_drop.donor_butcher_products_carry_the_fang, fang_drop.probe_can_say_absent_on_an_unpatched_animal (the first reports UNMEASURED while `get_defs` returns `butcherProducts` as bare type names)
- The fang art reads as intended. → UNCOVERED: visual; the judge pass, never a script

## the walk
1. [D] defs_resolve, settings_roundtrip: reads and a write/restore of the settings class
2. [D] fang_drop: the donor def's butcherProducts; control on `Wolf_Timber`

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "butcherProducts can be patched with `<li>`" — it is dictionary-keyed (`<RSW_WyyyschokkFang>3</...>`); an `<li>` discards the whole donor def. The static check goes red on an `<li>` inside the patch value.
RULED OUT: "`MayRequire` on the fang-drop Operation gates it" — inert on a top-level Operation (PATCH_MAYREQUIRE_GUARD_INERT_1); the patch is a `PatchOperationConditional` on the donor node and the static check goes red if `MayRequire` returns.
RULED OUT: "a def-count read proves the drop landed" — the drop is a patch onto a third-party def, so the def resolving says nothing about its butcherProducts; the drop is read from that field with an unpatched control.
