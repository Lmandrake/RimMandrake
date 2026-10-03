# UtinniStatues — validation walk
subject: src/RimUtinni/UtinniStatues  (packageId `mandrake.rut.utinnistatues`)
deps: none (Ideology optional, loadAfter only)
list: minimal + all DLC + this mod
status-hint: Utinni statues, step 1 of design/RimMandrake/statue_mods_spec.md — three carved statue tiers whose placed statue is dedicated to one of the Nine (or a votive / the crawler relief) by a picker button. Placeholder art until the 16 carvings land.

## must be true
- Loads with no error naming this mod's defs or classes. → load_clean.no_errors_naming_this_mod
- The three statue tiers and their sculptor's-table recipes resolve. → defs.all_defs_resolve
- A placed statue dedicated to Sh'kaar is named "idol of Sh'kaar" and honours Sh'kaar the All-Searing. → dedicate.statue_takes_the_chosen_god
- Dedicating it again to another god changes it. → dedicate.rededicate_changes_it
- A tier offers only the carvings of its own size (no 2x2 relief on a 1x1 statue). → dedicate.tier_offers_only_its_own_size
- The grand statue takes the crawler relief. → dedicate.grand_takes_the_crawler
- The chosen carving's art draws once its PNG exists. → UNCOVERED: no carving PNG has landed yet (UTINNI_STATUES_ART_WIRING_1); needs a screenshot then.
- "Utinni statues can be carved" OFF withdraws the three recipes from the sculptor's table. → UNCOVERED: takes effect at startup only; needs a restart with the toggle off, then a get_defs of TableSculpting's recipes.
- Only the player's own statue shows the Dedicate button. → UNCOVERED: no bridge reader for gizmos.
- Dedicating a stone or metal grand statue to Sh'kaar's grand carving rebuilds it as the fuelled burning idol (R5/R11). → shkaar_idol.shkaar_grand_becomes_the_burning_idol
- Rededicating the burning idol to another grand carving makes it the cold grand again. → shkaar_idol.rededicated_idol_goes_cold
- "Sh'kaar's idol burns" OFF: a grand dedicated to Sh'kaar stays cold. → shkaar_idol.burning_off_stays_cold
- The fuelled idol draws a crown flame and glows; empty, it goes dark. → UNCOVERED: visual; refuel it on a quicktest and screenshot.
- In the campaign (mandrake.rut.patches) the idol takes Sumpgas, not chemfuel ("Sumpgas fuels the idol"). → UNCOVERED: startup-only; needs a campaign-list load and a get_defs of the refuelable's fuel filter.
- A wooden grand dedicated to Sh'kaar stays cold with a message. → UNCOVERED: needs a WoodLog-stuff spawn; cheap to add once spawn_batch stuff is proven.

## anti-guessing notes
- RULED OUT: "a child def's <comps> replaces SculptureBase's comps" — Verse.XmlInheritance.RecursiveNodeCopyOverwriteElements appends list elements unless Inherit="False" (RimSage, 2026-10-03).
