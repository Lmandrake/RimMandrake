# RimStarWars: Trophy Craft — validation walk
subject: src/RimStarWars/TrophyCraft  (packageId `mandrake.rsw.trophycraft`)
deps: `mlie.starwarsanimalcollection` (the donor Wyyyschokk the drop patch targets; the patch is a quiet no-op without it); RimUtinni's `WyyyschokkFangPendantFactions.xml` supplies the observer factions
list: no named modset_builder tier yet; the smallest tier is BRIDGE + the donor mod + `mandrake.rsw.trophycraft` + the five DLCs
status-hint: TROPHY_CRAFT_FIRST_SCRIPT_1 — wyyyschokk fang drop, fang pendant recipe and neck layer, observer opinion thought with a settings slider; first script drafted, never run live

Sources: `src/RimStarWars/TrophyCraft/About/About.xml` description, `Defs/**`, `Patches/RSW_TrophyCraft_WyyyschokkFangDrop.xml`, `Source/*.cs`, `src/RimUtinni/UtinniPatches/Patches/WyyyschokkFangPendantFactions.xml`.

## must be true
Agent-owned, not hashed. Chains and components are in `src/RimStarWars/TrophyCraft/validation.py`.
- Every def the mod ships loads in the running game (the fang, the pendant, the recipe, the neck apparel layer, the observer thought), and the donor `Wyyyschokk` it patches is present; a def that fails to load is dropped whole and silently. [About.xml; `Defs/`] → defs_resolve.every_shipped_def_resolves, defs_resolve.donor_wyyyschokk_resolves
- The def-probe instrument can say "not found". [method] → defs_resolve.control_probe_can_say_absent
- Both Mod Settings fields (the pendant-opinion toggle and the opinion magnitude multiplier) write and read back, numbers numerically, and restore. [`RSW_TrophyCraftSettings.cs`; CLAUDE.md "superb Mod Settings"] → settings_roundtrip.settings_probe_finds_fields, settings_roundtrip.socialConsequenceEnabled_round_trips, settings_roundtrip.opinionMultiplier_round_trips
- A butchered wyyyschokk drops fangs: the donor def's `butcherProducts` carries `RSW_WyyyschokkFang`, and an unpatched animal's does not. [`RSW_TrophyCraft_WyyyschokkFangDrop.xml`] → fang_drop.donor_butcher_products_carry_the_fang, fang_drop.probe_can_say_absent_on_an_unpatched_animal (the first reports UNMEASURED while `get_defs` returns `butcherProducts` as bare type names)
- The recipe cords 4 fangs and 5 textiles into one pendant at a hand or electric tailoring bench for 400 work, with no research gate. [`RSW_TrophyCraft_Recipes.xml`] → crafting.recipe_work_amount_400, crafting.probe_reads_a_different_work_amount_control, crafting.recipe_takes_fangs_and_makes_a_pendant (the last reports UNMEASURED while the record lists read as bare type names)
- The pendant is a Neck-only apparel on its own `RSW_Neck` layer so it never collides with the 153 shirts and vests that share vanilla `Middle`; the layer draws between Middle (100) and Shell (200). [`RSW_TrophyCraft_ApparelLayerDefs.xml`; `RSW_TrophyCraft_Items.xml`] → crafting.neck_layer_draws_between_middle_and_shell, crafting.pendant_wears_on_the_neck_layer (the second reports UNMEASURED while the apparel record reads as a bare type name)
- The thought uses this mod's own thought and worker classes. [`RSW_TrophyCraft_Thoughts.xml`] → social_thought.thought_classes_and_base_offset
- An observer of a configured faction forms +8 opinion of a pendant wearer, scaled by the multiplier, and nothing when the toggle is off or the faction is not listed. [`RSW_ThoughtWorker_ObserverFactionApparel.cs`; About.xml] → social_thought.observer_forms_opinion_of_a_pendant_wearer, social_thought.opinion_multiplier_scales_the_offset (both report UNMEASURED: the factions list ships empty at this tier and no tool equips apparel or reads social thoughts)
- The pendant icon and the fang art read as intended. → UNCOVERED: visual (the pendant has no worn graphic by design); the judge pass, never a script

## the walk
1. [D] defs_resolve, settings_roundtrip: reads and a write/restore of the settings class
2. [D] crafting, fang_drop: scalar reads of the recipe, layer and donor def; controls on `Make_Patchleather` and `Wolf_Timber`
3. [S] social_thought: class read; the observer firing stays UNMEASURED with its reason

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "butcherProducts can be patched with `<li>`" — it is dictionary-keyed (`<RSW_WyyyschokkFang>3</...>`); an `<li>` discards the whole donor def. The static check goes red on an `<li>` inside the patch value.
RULED OUT: "`MayRequire` on the fang-drop Operation gates it" — inert on a top-level Operation (PATCH_MAYREQUIRE_GUARD_INERT_1); the patch is a `PatchOperationConditional` on the donor node and the static check goes red if `MayRequire` returns.
RULED OUT: "the thought needs a list of factions at this tier" — `factionDefNames` ships empty on purpose (RimUtinni adds the campaign's three); the static check goes red if it ships non-empty or loses the node the RimUtinni Add patch targets.
RULED OUT: "a def-count read proves the drop landed" — the drop is a patch onto a third-party def, so the def resolving says nothing about its butcherProducts; the drop is read from that field with an unpatched control.
