# VEXXITH_CLOSED_LOOP_BUILD_1 — the vexxith closed loop, after three answers

Split from `CAULDRON_GPT_ENRICHMENT_1` part 3. What already exists: `RM_Vexxith`
(`src/RimMandrake/Cauldron/Defs/ThingDefs_Items/RM_CauldronItems.xml`) is a Metallic stuff with
Flammability 0, high heat armour, MaxHitPoints factor 1.6. Spec: makes durable filter vessels,
vent-cap liners, fireproof doors and gravship scab-scrapers; poor weapons and ordinary walls.

## open questions

1. **Acid immunity needs a hook.** Vanilla has `AcidBurn`; nothing in our tree recognizes a
   material. Making things built of vexxith ignore it needs a Harmony patch on damage application,
   and the Cauldron assembly is deliberately Harmony-free. Add Harmony to the Cauldron mod, or put
   the hook in a shared assembly?
2. **Which recipes?** Filter vessels need the Filter-Works (`CAULDRON_MECHANICS_BUILD_1` part 4);
   vent-cap liners need vents (part 3); a vexxith-stuffed vanilla door is already fireproof — is a
   distinct plate-only door wanted? Gravship scab-scrapers sit next to Scabweight, which the owner
   declined (*"None of these thanks"*) — in or out?
3. **"Poor weapons and walls"** contradicts today's MaxHitPoints 1.6. A dedicated
   StuffCategoryDef (only the specialized defs accept it) or weaker stat factors? Numbers go to
   `DESIGN_MATERIALS_REVIEW_1` either way.
