# DECIDE inbox.

## D0 Break v1 into rows and items, and assign every migrated item a row
row:      —
spec:     Read `infrastructure/state/V1.md` (8 rows) and both files in
          `infrastructure/state/facts/`. For each row, decide the high-level needs,
          then the detailed items beneath them. Then add `row: <n>` to every item
          already sitting in `queue/BUILD.md` (37) and `queue/CHECK.md` (30) — they
          migrated without one and currently land in an `unassigned` bucket.
          Rows 2 and 7 are held behind the sea; say what would unhold them.
          Rows 1, 3, 5, 6, 8 are closed — do not re-open them, but DO record what
          "closed" means for each so the board can show it.
verify:   `python3 src/RimMandrake/Utils/derive_matrix.py` reports 0 items in the
          `unassigned` row, and 8 named rows carry non-zero totals.
criteria: —
state:    ready

## D1 Fill the empty contracts, highest value first
row:      —
spec:     32 fields across the migrated items are literally EMPTY because the old
          notes did not say. BUILD and CHECK will bounce every one of them. Work
          down by value, not by ID order. Start with the items blocking rows 4 and 2.
verify:   No item in `queue/BUILD.md` has an EMPTY `spec:` or `verify:`.
criteria: —
state:    ready


## D1 The droid relations NRE — which of three routes (owner decision #12)
spec:     `src/Jawa/Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets `isOrganic=false` on the KotOR flesh type `ABF_FleshType_Synstruct_Base` => `IsFlesh` false => no `Pawn_RelationsTracker` => HAR NREs on the 2nd and later same-race droid. Worldgen is unaffected on four independent grounds; `guy762_KotORFaction_RogueDroids` RAIDS are broken, and that faction is the KotOR distress call's antagonist and a **v1 KEEP**. Routes: **(1)** drop the KotOR flesh type from our patch — one xpath, no assembly; restores tending on droids; loses vanilla EMP behaviour on them; does NOT affect our ion weapon (its guard moved to `IsMechanoid` on 08-13). **(2)** ~5 lines of Harmony in an assembly we already ship — a build, a deploy and a load; gives Humanlike pawns a relations tracker regardless of `IsFlesh`; keeps both the machine framing and working raids; it is the only route that also covers `current`, the previously-spawned droid, which is where the throw actually happens. **(3)** accept broken droid raids — free; the quest antagonist cannot raid past its first pawn. EXCLUDED: retargeting to vanilla `Mechanoid` — it would make our own ion weapon block them. Full write-up: `observed/2026-08-14_O12_har_pawngen_nre.md`.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D2 Owner decision #10 — is a throwaway world permitted
spec:     `OWNER_DECISIONS.md`. All technical prerequisites are closed; a quicktest already builds a FULL world (119,904 tiles, `waterPct 25.0`, 2 bodies, `previewOnly:false`, 127 ms), so the sea gate and the worldgen click-path can be rehearsed on disposable worlds without opening the once-only Configure Factions screen.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D3 The Galactic Empire is not the antagonist the design says it is
spec:     Four independent layers say the same thing. (1) Pillar 5 (`faction_roster_v2.md:105`) promises one permanent enemy: the Galactic Empire. (2) The shipped flags are `hostile: false`, `goodwill: 0`, `permanentEnemy: false`, and a SECOND empire outranks it — "The Fallen Dominion" holds 4 settlements to the Galactic Empire's 1. (3) `jawa/fire_incident RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true` returns `canFireNow: false`, because `TryResolveRaidFaction` keeps the passed faction only if `HostileTo(Faction.OfPlayer)` => the flagship antagonist is MECHANICALLY INCAPABLE of raiding the player. (4) The religion rubric scores it **0 on the decision axis**: no refusal comp, no High-impact precept anywhere in its eight. ⚠ At least two of these layers may be the SAME FACT — `permanentEnemy false` plausibly explains `goodwill 0` and `canFireNow:false` together; BUILD B32 reads the shipped `FactionDef` to settle whether this is a one-field authoring fix or a design crisis.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D4 The desert world generates ~49% ocean — does the planet bend
spec:     Measured on three real saves: 43% / 49% / 55% Ocean. The thirst-world identity exists in our documents and nowhere else. Ocean is an elevation rule written at worldgen step 0, so the rainfall slider cannot remove one tile, and no active mod manages water. Three routes, none needing a new dependency: **WorldEdit 2.0** (already active), a custom `WorldGenStep`, or BiomesKit's unused hooks. `faction_world_spec.md`, last section. This contradicts the Three Waters ruling by ~100x.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D5 The Homestead — cut it or differentiate it
spec:     It fails the name-blind test against the Deepwater Compact at **24% Jaccard**, the roster's worst pair, and the Homestead is the decoration half. Do not polish it. This gates the D2 structure ruling (`Structure_TheistAbstract`, deity *the Withdrawn*), which stands only if the faction survives.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D6 Geonosian — retarget the defect or close it
spec:     `faction_roster_v2.md:1403` sets "Preferred xenotypes: Geonosian" while Global system 3 (`:183`) sources Geonosian from the separate race inventory — different objects, and the roster never picks. The named route DOES NOT EXIST: `PreferredXenotypes` has exactly one precept (`PreferredXenotype`, Biotech) and its xenotype is chosen at ideo-GENERATION time, not in XML; there is no `FactionDef` path to it. Retarget at `PawnKindDef` xenotype chances — which is where faction 8's composition already lives — or close it. Group E is not blocked on a roster decision; it is blocked on a wrong one. Pattern to follow: Free Droid (`:1009`) flags the engine question AND rules a fallback.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D7 The mech review sheet — accept name+role for the 25 vanilla mechs
spec:     Axes are known and committed (`data/mech_control_axes.md`): raids · ancient dangers + clusters (one flag, not separable) · bossgroups · gestation · sellable · purchasable (a separate axis, a 3-line patch) · decoration. Art is on disk for 55 of 80. The sheet is otherwise complete and waits only on whether the owner accepts name+role for the 25 whose art is bundle-locked.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D8 Two mod adoptions
spec:     **GravTide** `3779600989` — recommended ADOPT `[v2]`; the ocean objection is dead. **`[KR] Star Wars: Droids`** `3248936254` — Biotech-only, covers 5 of 6 real chassis gaps; take the chassis, REFUSE its faction wrappers.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D9 Does the restraint bolt work on PEOPLE
spec:     Ruled KEEP, weighted ~10x a droid, plus a mood hit. Not confirmed by the owner.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D10 Cut the Predator family — taste call, decided on fiction alone
spec:     Four Yautja factions own **14 settlements** between them — `ABYautjaBadBloodClan` (5), `ABYautjaBerserkClan` (4), `ABYautjaClan` (4), `ABYautjaModderClan` (1) — the single largest non-Star-Wars presence on the map. Two SEPARATE levers, not interchangeable: **the four FACTIONS** can be unticked at worldgen (free, reversible, no mod change, already on `WORLDGEN_FACTION_CHECKLIST.md`); **the XENOTYPE MOD** `[AB] Xenotype: Yautja` (`biotechrace.yautja.alleyballey`, ws `3536839586`) is a separate decision — removing it costs a game-down window and risks `Could not resolve cross-reference`. The mod owns all 14 `Exception getting Verse.Graphic_Multi at :` errors (one malformed `<bodyGraphicData>` at `PawnKinds_BaseAbstract.xml:60`, 7 kinds x 2 lifeStages) but those errors are HARMLESS and waived — do not let them do work they cannot do. If the mod goes, BUILD B24 loses its mid-tier reference (Yautja blade, AP 0.60). Recommendation on file: untick the four factions, keep the mod installed.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D11 The art directive — resume, or stay parked
spec:     Standing directive (owner, 2026-08-13): stop fixing art until the owner can verify the art doesn't work; the gate is the owner's own eyes, not a clean log, not a blank alpha channel, not an md5, and the PREMISE is what is suspect. Parked by it and awaiting a ruling: **C7 rows 4–6** (fully triaged with per-file canvases and verdicts, `design/Jawa/art/c7_directional_triage.md`) · **C-t2** (`SWDoorBlast{B,D}Door_Frame_east_m.png` carry an underscore before the `m`; the convention is `...eastm.png` — exactly the class the directive suspects, nothing errors and nobody has looked in game) · **C3a Eopie**, two proposals never ruled on: the species-inconsistent head shapes and north's featureless rear (salmon-pink is a playtest question, do not re-raise). Do not read silence as approval. Already-deployed work stays in place.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D12 The Jawa faith — name, and Nomad vs Tunneler
spec:     The name contradicts itself in its own file: "The Salvation" vs "The Articles of Passage". Nomad-vs-Tunneler is still a coin. Owner's, not any seat's — flag both if he opens it. Section 12 of `faction_religions_spec.md` is a deliberate empty slot because the owner is building it.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D13 Two lore contradictions inside the approved ideoligion
spec:     (1) Lore sanctifies ration paste, but the ideo sets `NutrientPasteEating_Disgusting`. (2) Sh'kaar is written as "the sun that never sets"; the older doc says twin suns, and the tidally-locked world postdates it.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D14 Broken-infrastructure mod — repairable workbenches, turrets, engines `[v2]`
spec:     For the ship. Survey what exists BEFORE designing — `design/Jawa/art/graphics_overhaul_protocol.md` §6.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D15 The canon droid lineage catalogue — re-request or drop
spec:     Agent `abe113a7` delivered the non-CIS additions only; the main lineage table never arrived. Re-request it if the visual comparison sheet is wanted.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## D16 The restructure's unplaced items and the `skills/` stage
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` §3 lists seven unplaced items that need a ruling before stage 4; stage 9 (`skills/`) is owner-gated and may never run. Both block BUILD B35.
verify:   EMPTY
criteria: EMPTY
state:    blocked
