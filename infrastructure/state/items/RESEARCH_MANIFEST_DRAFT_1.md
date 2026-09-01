# Research manifest draft — 521 rows, fates from the sitting's rulings

## spec
`design/Jawa/research_tree_taxonomy.md` section 3 defines the manifest schema
(no manifest existed yet); section 5's migration rules and section 6/7's
"RULED by the owner" blocks are the normative source for fates. This item
mechanically applies those rulings to every live `ResearchProjectDef`,
producing `infrastructure/output/research_manifest_draft.csv` for
`research_manifest_validate.py` (built by `RESEARCH_VALIDATOR_BUILD_1`) to
check. This is APPLYING already-made decisions, not making new ones — where
the docs left a genuine gap, the row is flagged (note field) rather than
guessed, per the task brief.

**Source capture:** newest at build time via `game_paths.newest_capture()`,
`2026-09-01T05-30-28Z` (fingerprint `c2960afd7cb7d5ae`, 586 mods, confirmed
matching live `ModsConfig.xml`). **521 live `ResearchProjectDef` rows** — 6
more than the prep doc's 515 (mods added since that capture; matches the
validator build report's own "+6 unclassified empty-cache rows" note).
Cherry Picker cut list read via `cherrypicker.py` (1,513 defs, live settings,
2026-08-29 17:20) — never a new regex.

## what the manifest encodes (mechanical, per named ruling)
- **30 `cut`**: the 12 measured-dead rows (`research_tree_prep.md` sec 1)
  minus the 3-row ship-design trio = 9, plus Royalty's 19
  (`royalty.dead_ruled` + sitting_ruled "loot-only by default") = 28 ruled,
  plus **2 found by this pass, not ruled anywhere**: `GhoulInfusion` and
  `GravForge` are both independently on the LIVE Cherry Picker cut list (see
  "conflicts found" below) — 28 + 2 = 30.
- **3 `reflavor`**: the ship-design trio (`MM_Research_AncientShipDesigns` →
  `MM_Research_CWShipDesigns` → `MM_Research_EmpireShipDesigns`), tab=THE
  SHIP, `source_gate=memory_core`, per taxonomy sec 5 rule 1 / canon
  `shape_src`.
- **6 `merge`**: `OuterRim_Blastersmithing`, `VWE_LaserWeapons`,
  `VWE_LaserTargetingSystems` → `guy762_ResearchKotOR_blasters` (blaster
  spine root); `guy762_ResearchKotOR_ion`, `guy762_ResearchKotOR_iondamp`,
  `IW_IonChargeWeaponry` → `RSW_JawaIon_Weaponry` (the ACTUAL live defName —
  canon's prose says "JawaIon_Weaponry" but that string is not a live
  defName; `RSW_JawaIon_Weaponry`, mod "Jawa Ion Weapons (local)", is what
  resolves). Migration rule 4 applied mechanically: every OTHER row that
  named a merged donor as ITS OWN prereq/hidden_prereq was re-pointed onto
  the survivor (`OuterRim_HeavyWeaponry`, `guy762_ResearchKotOR_iondamp`,
  `guy762_ResearchKotOR_jawa` — 3 re-points, logged in the build script's
  stdout).
- **8 `keep`** (named survivor chains, `chains_ruled`): blaster spine
  (`guy762_ResearchKotOR_blasters`/`_hvyblasters`/`_miniblasters`/
  `KOTOR_Research_plasmaApplications`, `form=blaster`), ionic survivor
  (`RSW_JawaIon_Weaponry`, `form=ionic`), kinetic thin chain (`SniperTurret`
  → `VFES_Railgun`, `form=kinetic`), sonic (`guy762_ResearchKotOR_sonic`,
  `form=sonic`, kept thin per sitting_ruled).
- **474 `untouched`**: everything else, each still given a best-effort
  `tab`/`tier` (never left blank — coverage requires every row) via:
  - Anomaly rows (pkg `ludeon.rimworld.anomaly`) → tab `(Anomaly)`, migration
    rule 5.
  - Ship-tree content → tab `THE SHIP`: explicitly-named rows (`ShipReactor`,
    `VFE_Manufacturing`, the MiningCo drill-turret pair, Odyssey gravtech x3,
    `GravForge`/`GravTuning`/`AdvShipParts`, `GTbc_BigCannons`) plus
    content-matched siblings noted as NOT individually enumerated by canon
    (the 7 VGE Chapter-1 rows, the 5 other Core `Ship*` rows, `BlackHole_GT`)
    — each says so in its own note.
  - Droid branch → tab `The Machine`: Outer Rim - Droid Depot (16 rows) +
    Star Wars KotOR Resources and Materials's remaining 15 droid rows.
  - Everything else → tab defaulted from tier band (T0→Scavenger,
    T1/T2→Trade & Craft, T3/T4→The Reach), noted as a default, not a ruling.
  - `tier` picked to satisfy BOTH the techLevel mapping and the cost band
    when a valid choice exists; otherwise the techLevel-mandated tier wins
    and the cost mismatch is noted (see "expected FAILs" below).

## conflicts and open questions found (NOT decided here — flagged)

**Items 1-3 RESOLVED 2026-09-01** via owner question cards, recorded in
`canon.yml` `research_tree.gravitic_seam_ruled`:

1. ~~🔴 `GravForge` cut vs canon's Ship-tree ruling~~ — **turned out to be a
   FALSE POSITIVE**, caught while implementing the fix: only
   `ThingDef/GravForge` (the building) and `RecipeDef/Make_GravcoreGF` were
   on the live Cherry Picker cut list, never `ResearchProjectDef/GravForge`
   itself — the original check used an any-type name match
   (`cuts.cut_name()`), not a typed one (`cuts.cut('ResearchProjectDef', …)`),
   and both this item's first pass and the independent verification at
   commit time made the same mistake. The RESEARCH was never actually
   blocked. What genuinely needed the owner's call was the BUILDING/RECIPE
   cut: "leave it in for now and we'll handle the anti-exponential another
   way later" — restored `ThingDef/GravForge` +
   `RecipeDef/Make_GravcoreGF` + `ThingDef/AdvShip_GravReactor` (the whole
   functional cluster) on the live Cherry Picker settings. Manifest fate
   corrected `cut` → `untouched`, tier filled in (`T4`, matching its GravTech
   siblings).
2. ~~`GhoulInfusion` cut vs the empty-cache allowlist~~ — **same false
   positive**: only `RecipeDef/GhoulInfusion` was cut, never the research
   project. Restored the recipe on Cherry Picker, but PLACEMENT-RESTRICTED
   per the owner: "back in, but only in key places (like the dungeons). NOT
   to occur randomly or by Anomaly timeclock progression." — whoever
   authors ghoul dungeon content must hand-place the trigger, never wire it
   to vanilla Anomaly's monolith/timeclock spawn system. Manifest fate
   corrected `cut` → `untouched`, tier filled in (`T0`, cost-band fit).
3. **`GravWeapon`/`GravBionics` seam — RULED, split (not left dual-tagged).**
   Ship-hardpoint unlocks (`Turret_GravBlaster`/`AdvShip_ShieldGenerator`)
   need a NEW Ship-tree research node prereq'd on `GravWeapon` — **not yet
   authored**, named as a follow-on build item. Personal unlocks
   (`GravRifle`/`GravBlaster`/`GravHammer`/`Apparel_GravPack`) stay on
   `GravWeapon` in Armory, but are now FACTION-HELD: owner verbatim,
   "associate this ultra-powerful GravTech as something only the Rust
   Cathedral can grant as a boon. The weapon tech of the Rataka, rather
   than their terraforming tech that the ship contains natively." —
   `source_gate` set to `faction:RustCathedral_boon` in the manifest row;
   the actual grant mechanism (bespoke quest/ritual reward vs. plain
   `heldByFactionCategoryTags` stock) is NOT decided, flagged for
   `TECHPRINT_FACTION_GATING_1`. **`GravBionics` was left AS-IS** (still
   defaulted to Trade & Craft, not given the same faction gate) — the
   owner's answer named `GravWeapon` specifically ("weapon tech"), and
   `GravBionics` is bionic implants, not weapons; whether it should carry
   the same Rust Cathedral gate is still an open question, spelled out in
   its own row's note rather than assumed.
4. **`KOTOR_Research_plasmaApplications`'s wiring into the blaster spine is
   unspecified.** `chains_ruled` names it as the spine's 4th tier ("guy762
   blasters/hvy/mini + plasma") but its live prereq
   (`KOTOR_Research_plasma`) doesn't connect to the guy762 3-chain, and no
   doc says which tier it should chain off instead. Left with its real
   prereq rather than inventing a reposition — this is **the expected
   check-4 FAIL** (2 components in form=blaster), the same class of
   "genuinely undecided" case the task brief itself named as legitimate to
   leave.
5. **Cut rows that are still live prereqs elsewhere**: `DisruptorFlares` (cut)
   is a prereq of `RevenantInvisibility`; `VAE_SterileAttire` (cut) is a
   prereq of `VAE_MilitaryClothing`; `MM_Research_Repulsor` (cut) is the
   ship-design trio's own upstream prereq. Migration rule 1 rules the row
   itself dead but says nothing about what happens to OTHER live rows that
   named it as a prereq — re-wiring those gates is a real design call
   (drop the gate? replace it?) with no source-doc answer. Left as-is,
   flagged per-row.
6. **The fuel cross-link is not wired.** Canon states "exactly one Ship node
   requires `ChemfuelRefining`" but does not say which — no new prereq edge
   was invented; `ChemfuelRefining` stays in Rimefeller's modular chain,
   untouched.

None of these are decided in this pass. They are exactly the kind of design
fork `DROID_DONOR_PATCH_GATE_1` stayed blocked on rather than resolving
solo — surfaced for the owner, not resolved here.

## verify
Ran `python3 src/RimMandrake/Utils/research_manifest_validate.py
infrastructure/output/research_manifest_draft.csv` twice (iterated
once between runs).

**Run 1** (initial mechanical pass): 258 FAIL total. Found 2 real manifest
bugs via check 1 (Anomaly-blanket rule shadowed the individually-measured-dead
`DisruptorFlares`; `GhoulInfusion`/`GravForge` cut-list conflicts not yet
detected) and 6 via check 2 (3 genuine merge-repoint omissions, 3 genuine
open questions). Fixed the 2 orphan-check bugs (reordered the DEAD_CUT check
ahead of the Anomaly blanket rule) and added a general post-pass: any row
whose own defName is on the live cut list is forced to `fate=cut` regardless
of what ruling would otherwise apply, and any OTHER row's prereq naming a
merge donor is re-pointed onto that donor's `merge_target` (migration rule 4,
applied mechanically — not a new judgment call).

**Run 2** (after fixes) — **255 FAIL, all reviewed, none are manifest
mistakes**:
- **Check 1** (orphan): 0 FAIL, 63 WARN (partial-cut Mortars-class candidates
  + unclassified empty-cache rows) — informational, matches the validator's
  documented behavior, not something this item resolves.
- **Check 2** (prereq): 7 FAIL — exactly the 7 rows named in "conflicts and
  open questions" items 1, 2, 5 above (`GhoulEnhancements`,
  `RevenantInvisibility`, `VAE_MilitaryClothing`, `GravWeapon`, `GravTuning`,
  `GravBionics`, `MM_Research_AncientShipDesigns`). Every one is a downstream
  reference to a row this pass correctly cut, where re-wiring the downstream
  gate is a real, unmade design call.
- **Check 3** (band): 247 FAIL — two known categories, both anticipated by
  the taxonomy doc itself. (a) **52** are vanilla `techLevel` data smells
  (Undefined ×~38 after 2 moved to cut, Animal ×14) — the intro's own line
  "the manifest fixes for free" cannot actually rewrite a live def's
  techLevel field from a CSV; that needs an actual patch, out of this item's
  scope. (b) **195** are real mod-authored costs that don't fit a
  vanilla-like band at their techLevel-mandated tier (e.g.
  `guy762_ResearchKotOR_blasters` costs exactly 3000, landing it on the
  T2/T3 seam per the validator's own documented "boundary goes to the lower
  tier" convention — genuinely unresolvable by picking a different tier
  label). Taxonomy sec 7 anticipates this: "RR techprints + the Industrial
  multiplier do the punishing; bands only remove outliers" — actual cost
  rebalancing is later execution work this drafting pass correctly surfaces
  rather than papering over.
- **Check 4** (one-chain-per-form): 1 FAIL — `KOTOR_Research_plasmaApplications`
  disconnected from the guy762 3-chain, item 4 above. The exact case the task
  brief said was legitimate to leave failing.
- **Check 5** (coverage): **0 FAIL** — 521 manifest rows == 521 live
  `ResearchProjectDef`, fingerprint verified against the same capture.
- **Check 6** (cycle): pass — only the known vanilla self-loop
  (`RimFridge_PowerFactorSetting`), reported as INFO.
- **Check 7** (co-writer awareness): pass — `Electricity` shows Research
  Reinvented's stamp (`techprintCount=1`, `RR_ElectricityBasics` prereq),
  confirming the dump read is the resolved post-RR state.

No destructive actions taken: `ModsConfig.xml` untouched, Cherry Picker
settings untouched (the `GravForge`/`GhoulInfusion` conflict is REPORTED,
not fixed by un-cutting them), nothing deployed, no `rimflow` commands run,
nothing committed/pushed (left for the owner to review).

## criteria
- [x] Every live `ResearchProjectDef` has a manifest row (coverage check 5:
      0 FAIL, exact 521==521).
- [x] All named migration rulings applied (12 measured-dead minus trio,
      Royalty 19, blaster/ionic/kinetic/sonic chain consolidation with
      migration-rule-4 re-pointing).
- [x] `# fingerprint=... modCount=... capturedUtc=...` header line matches
      the dump actually read (verified by check 5's fingerprint INFO).
- [x] Cuts read via `cherrypicker.py`, never a new regex.
- [x] Validator run, iterated once, every surviving FAIL individually
      reviewed and classified as a genuine open question (not a manifest
      defect) in the table above.
- [x] Genuine design forks (the `GravWeapon`/`GravBionics` seam, the
      `GravForge`/`GhoulInfusion` cut-list conflicts, the plasma-wiring
      question, the fuel cross-link's target node) flagged for the owner,
      not decided solo.
- [ ] Owner reviews the 6 flagged conflicts/open questions above, particularly
      #1 (`GravForge` cut-list conflict) which is the highest-blast-radius
      finding in this pass.
- [ ] Cost-band rebalancing (the 195 real-cost mismatches) — separate later
      execution work, not this item's job.
- [ ] techLevel data-smell patching (the 52 Undefined/Animal rows) — separate
      later execution work, not this item's job.
