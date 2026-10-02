# RimStarWars: Bacta — validation walk
subject: src/RimStarWars/Bacta  (packageId `mandrake.rsw.bacta`)
deps: none beyond Core (loadAfter `mandrake.rm.flowworks`, not required); all five DLCs on the tier
list: bacta   # modset_builder tier `bacta` (3 mods with dependencies)
status-hint: the bacta tank (Building_Enterable + CompBactaImmersion) and its fluid: fast healing of wounds, burns, organ injuries and, slowly, scars; never regrows a missing part, never touches the brain; bacta is bought not made; field patch/spray, medical droid facility, corpse revival (off by default)

## must be true
Source for every line: `About/About.xml` description, `Defs/`, `Source/*.cs`, `Patches/`, items BACTA_TANK_CORE_1 / BACTA_REVIVAL_MECHANIC_1 / BACTA_SIDE_ITEMS_1. Agent-owned, not hashed. Chains and components are in `src/RimStarWars/Bacta/validation.py`.
- Every shipped def loads and resolves: the tank, the fluid, the patch, the spray, the medical droid, the research project, the corpse job, both WorkGivers, both administer recipes. → content.defs_resolve
- The tank is a `Building_BactaTank` on a Normal ticker carrying the immersion, shell, refuelable (capacity 30), power and facility comps; the droid carries a facility comp. → content.tank_def_wiring
- Bacta, patch and spray are tradeable exotic goods (tag ExoticMisc, tradeability All) and are bought, not crafted. → content.fluid_and_items_trade
- The three trader-stock patches landed (a patch that matches nothing logs nothing). → content.trader_stock_patch_landed
- The doctor-recipe patches landed on Human and on animals. → content.doctor_recipes_patch_landed
- Settings ship at their documented defaults, revival OFF, every other toggle ON. → content.settings_ship_defaults
- Neither load nor ticking leaves an Error log line naming Bacta. → content.no_bacta_errors_in_log, tank_heals.no_bacta_errors_after_ticking
- The tank takes bacta through the ordinary vanilla Refuel job and reads back what it holds. → tank_heals.tank_refuels_via_vanilla_job
- A powered, fuelled tank takes a colonist who walks in (EnterBuilding); with healing switched off it says so and does nothing to the occupant or the fluid. → tank_heals.enters_and_reports_off
- A fresh wound closes at the tuned rate (woundHealPerDay 30 = 0.125 severity per 250-tick pass). → tank_heals.heals_fresh_wound_at_tuned_rate
- Bacta is consumed only while it heals (fluidCostPerDay 5 = 0.021 per pass). → tank_heals.drains_bacta_while_healing
- Bacta never regrows a missing part and never touches an injury on the brain, even while it heals the rest. → tank_heals.never_regrows_never_touches_brain
- When nothing healable is left the occupant is released; what bacta may not touch stays. → tank_heals.ejects_when_nothing_left
- A permanent injury is NOT erased while scar erasure is off, and is erased while it is on (scarHealPerDay). → tank_scar.scar_erasure_off_keeps_the_scar, tank_scar.scar_erasure_on_removes_the_scar
- No power, no healing and no drain; power back, healing resumes. → tank_power.unpowered_tank_does_not_heal, tank_power.powered_tank_heals_again
- Hunger and tiredness are held while immersed when suspendNeedsEnabled, and run normally when it is off. → tank_needs_and_dry.needs_held_while_immersed
- A tank that runs dry keeps its occupant when autoEject is off and releases them when it is on. → tank_needs_and_dry.dry_tank_holds_occupant_when_autoeject_off, tank_needs_and_dry.dry_tank_ejects_when_autoeject_on
- A powered, linked medical droid is reported as assisting and stops when medicalDroidEnabled is off. → tank_droid.linked_droid_is_reported_assisting, tank_droid.droid_toggle_off_stops_the_assist
- A bacta patch is unusable with fieldItemsEnabled off, and closes a fresh wound and is consumed with it on. → field_patch.patch_unusable_when_field_items_off, field_patch.patch_closes_a_fresh_wound
- Revival is off by default and refuses a corpse; refuses a corpse older than revivalWindowHours; revives a fresh one when on. → revival.revival_off_by_default_refuses_corpse, revival.revival_window_refuses_old_corpse, revival.revival_on_revives_into_the_tank
- The infection assist (infectionAssistEnabled, immunityGainPerDay, tendQuality): immunity is not readable through the bridge and `WoundInfection` kills a pawn on add (MEASURED 2026-09-24). → UNCOVERED: no tool reads an ImmunityRecord, and the only safe tendable disease fixture is unproven; file a companion `[Tool]` item before covering
- The bacta spray, the `RSW_Administer*` doctor-bill path, fieldItemPotency, medicalDroidHealMultiplier: same mechanism as covered lines at a different dose. → UNCOVERED: dose-ratio checks need a long run per case; first script covers the mechanism through the patch and the droid line
- The suspended pawn, glass shell and fluid column are drawn correctly. → UNCOVERED: visual (section 4 boundary; art acceptance is BACTA_TANK_ART_1)

## the walk
1. [D] content chain: defs, tank wiring, trade tags, both patches, shipped settings, log (components above)
2. [B] tank_heals chain: build and power a tank, fuel it through the Refuel job, walk a colonist in, add Cut(Torso 4.0) + MissingBodyPart(Kidney) + Bruise(Brain 2.0); 2500 ticks healing OFF then 2500 ON, then woundHealPerDay 120 until release
3. [B] tank_scar chain: make an injury permanent with the dev action found by `rimworld/search_debug_actions`, immerse with scar erasure off, then on
4. [B] tank_power, tank_needs_and_dry, tank_droid, field_patch, revival chains as named

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**The tank**
- [ ] `bacta_tank_reads_as_tank` — `RSW_BactaTank` reads at play zoom as an upright
      medical tank, and a patient inside reads as floating in fluid. (guess: art is
      placeholder today)
- [ ] `bacta_tank_occupied_distinguishable` — an occupied and an empty tank are
      distinguishable at a glance.
- [ ] `bacta_fluid_level_visible` — a tank low on bacta looks different from a full
      one. (guess)

**The fluid and the field kit**
- [ ] `bacta_items_read_as_bacta` — `RSW_Bacta`, `RSW_BactaPatch` and
      `RSW_BactaSpray` in a stockpile read as three different medical goods.
- [ ] `bacta_wounds_close_visibly` — a wounded colonist's health tab shows wounds
      closing over a short stay in the tank. (guess)

### cannot show

- [ ] `bacta_never_regrows_limb` — a missing limb restored by the tank.
- [ ] `bacta_never_placeholder_art` — the placeholder tank art shipping as final.
      (guess: art status is his call)

## anti-guessing notes
- RULED OUT: "bacta should heal a pawn who walks in with no wounds" — `CompBactaImmersion.CompTick` releases an occupant the first pass nothing healable remains (autoEject), so every chain adds its wound BEFORE entering, and the scar-off phase sets autoEjectEnabled false.
- RULED OUT: "WoundInfection is a safe infection fixture" — MEASURED 2026-09-24: adding it at severity 1.0 kills the pawn that tick, success:true (BACTA_TANK_CORE_1 live note). The infection assist is UNCOVERED rather than risked.
- RULED OUT: "Mod Settings are readable with rimworld/get_mod_settings" — the fields are `public static`; only `jawa/mod_settings_field` reaches them (BRIDGE_STATIC_SETTINGS_FIELDS_1).
- RULED OUT: "the bacta is lost or doubled when two traders list it" — Better Traders ships its own copy of the three trader kinds (BACTA_TANK_CORE_1 note); stock may be added twice, a tuning note, not a defect, and no check asserts exactly one row.
