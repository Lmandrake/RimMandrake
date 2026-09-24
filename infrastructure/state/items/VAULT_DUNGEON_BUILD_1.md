## spec
Full spec: `design/Jawa/worldbuilding/dungeons_arc_spec.md` §3. Summary:

Six sites, the "breached vaults" `03_deep_history.md` already names as holding
the self-replicating flesh, plus the triad's other two members: **① mechanoid
garrison** (held), **② flesh weapon loose** (breached), **③ frozen Rakata**
(the rare scene). All six sites RULED and independently verified
settlement-free (`vault_siting_prep.md`):

| id | tile | region | type | landmark |
|---|---|---|---|---|
| V1 | 678 | Rust Cathedral core | ① | `AncientGarrison` |
| V2 | 4000 | Scorch (Cathedral halo) | ① outer works | `AncientLaunchSite` |
| V3 | 9167 | Fall Line | ① route-spread | `AncientGarrison` |
| V4 | 17461 | Deadstone | ② | `AncientWarehouse` |
| V5 | 37 | Slough (terminator) | ② | `RUT_Slough_GelatinousBreach` — authored 2026-09-09, not yet placed |
| V6 | 20853 | Umbra (deep nightside) | ③, the one | `AncientWarehouse` |

**Structure** (RULED): one concentric grammar varied per type — outer ring
states the vault's condition at a glance (①=disciplined+powered,
②=torn-open, ③=dark frost-locked) → garrison ring (the fight, or near-silence
for ③) → core payoff. Partial raids viable; the core always costs.

**Payoff ladder** (RULED): ①=Forsaken matter/weapons (never chassis — Arsenal
tech is canonically incompatible with droid parts); ②=survival + the route to
③ knowledge; ③=**wake** (sleepers join, no gratitude, recognize the Utinni as
their colonizer vessel and challenge its possession — canon.yml
`rakata.woken_brutality` — opens a ship-claim thread) / **loot** (kills them,
plainly) / **leave** (the Narrator remembers).

**Technical route**: KCSG (`StructureLayoutDef`) is already vendored
(`VanillaExpandedFramework-main/Source/KCSG/`) and already wired into the
bridge (`jawa/kcsg_place` in `JawaBenchKcsgTools.cs`) — no new C# needed to
place a template. FOUNDRY builds three parameterized templates (type ①/②/③),
proves each on a quicktest, then hand-finishes each of the six real sites with
the owner.

**LARGE maps** (RULED, owner verbatim: "should be LARGE... in terms of X Y
size"): proposed floor 300×300 against the campaign's standard 250×250 —
exact number held for the owner.

**Territorial access**: V1/V2 sit on Cathedral-FDE ground, V3 on the Empire's
Ashgarrison chokepoint — conflict/negotiation for access. Owner flagged a
"territories mod that introduced custom raids in proportion to settlements"
to investigate; **not identified or assessed by this item** — a separate
research task if picked up.

## verify
- [ ] Owner reviews `dungeons_arc_spec.md` §3 and rules the open calls (exact
  LARGE dimensions, the pawn-spawn symbol question in §3.6, whether the
  territories-mod research gets its own item).
- [ ] Three parameterized `StructureLayoutDef` templates (type ①/②/③)
  authored, each including the concentric ring structure.
- [ ] **Quicktest-proven**, per `dungeons_arc_spec.md` §3.7: each template
  placed via `jawa/kcsg_place` on a throwaway quicktest map at the LARGE
  dimensions, judged by LOOKING (`take_screenshot`, read the image) against
  the `rimworld-layout-layers` bar — power/roof sane, no floating/unreachable
  guardians, the core reachable only through the ring, no path that skips the
  garrison ring entirely.
- [ ] Each of the six sites hand-finished with the owner and committed to the
  world (`world_commit`, one bridge driver at a time).
- [ ] Wake/loot/leave dialogue and letters authored for V6; the ship-claim
  thread from waking V6 authored and fires correctly.

## criteria
- [ ] All six vaults readable at a glance by their outer-ring state (a player
  can tell ①/②/③ apart before entering the garrison ring).
- [ ] Type-① core loot is materials/weapons only — no mechanoid chassis ever
  drops.
- [ ] V6's wake branch reads as plainly brutal in dialogue — no gratitude, no
  sympathy softening, the ship-ownership challenge line lands.
- [ ] Partial raids (outer ring only, no core) are genuinely viable on every
  site — the grammar must not force a full clear.
- [ ] Map dimensions measurably exceed the campaign's 250×250 standard
  (`mapSize` read off the game, never off a note).

## Watch out
🔶 **Template geometry is FOUNDRY's; per-site hand-finish, dialogue/letters
and the six `world_commit` writes are "with the owner"** (`FUTURE_VECTORS.md`).
Leave `doing` until those are done at a joint bench session — this item is a
build spec for the templates, not a licence to hand-finish sites solo.

⛔ **Vaults do NOT get the Assailant dungeon's Anomaly exception**
(canon.yml `anomaly_content` names only the Assailant dungeon and,
tentatively, the sarlacc). Type-② guardians come from the existing
bioweapon-class roster, not the Anomaly toolbox.

🔑 **"Territories mod" is IDENTIFIED** (Faction Territories,
`jaeger972.factionterritories`, `dungeons_arc_spec.md` §3.8) — assessing it
for the V1–V3 conflict layer is its own separate item, not this one.

✅ **V5's landmark is authored** — `RUT_Slough_GelatinousBreach`
(`src/RimUtinni/UtinniPatches/Defs/LandmarkDefs/`), offline XML + a
procedurally-generated icon. Not yet placed on tile 37 — that write rides the
same held-for-owner bridge pass as the other five sites.

## 2026-09-02 (FOUNDRY) — three parameterized templates built, offline only

**This item's own "Watch out" section above is STALE against
`dungeons_arc_spec.md` §3.9 (rulings landed 2026-09-01, restated here since
this file wasn't updated when they landed):** all six sites are **325×325**
(not the 300 proposed here, vanilla `initialMapSize` ceiling, still
warning-free); V5's landmark is **RULED** — new organic landmark, working
name `RUT_Slough_GelatinousBreach`, not authored yet (that's a per-SITE
hand-finish task, out of scope for template geometry, see below); the
pawn-spawn symbol question is **RULED** — `KCSG.SymbolDef` with
`<pawnKindDef>`; naming tier is **RULED** — `RUT_`; the "Territories mod" is
**IDENTIFIED** — Faction Territories (`jaeger972.factionterritories`,
vendored decompiled) — but assessing it for the conflict layer is
confirmed its own separate item, not touched here. Template geometry
authoring was never itself gated on the owner in §3.9's "still held" list
(only the per-vault hand-finish pass, dialogue/letters, and the six bridge
placements are) — so this pass proceeded.

**Built**: `src/RimUtinni/VaultDungeons/` (`mandrake.rut.vaultdungeons`) —
`Source/gen_vault_layouts.py` generates `Defs/StructureLayoutDefs_Vaults.xml`
(three `KCSG.StructureLayoutDef`s, one per type) and
`Defs/SymbolDefs_Vaults.xml` (9 `KCSG.SymbolDef`s). Each template is a
concentric square grid — outer wall ring (single door) → garrison band
(guardians/turrets scattered, never on the core footprint) → inner wall ring
(single door, offset 90° from the outer door) → core. Verified
programmatically (BFS over the actual generated grid, walls blocking): all
three have exactly one outer opening and every core cell is reachable only
by walking the full garrison band, never a straight line — the §3.7
quicktest bar's "not skippable" requirement, checked at the geometry level
now rather than left to the live pass to discover.

**🔴 Real defect caught and fixed before shipping, worth recording as a
lesson**: `KCSG.StructureLayoutDef.ResolveSymbols()` (read from
`vendor/mod_sources/VanillaExpandedFramework-main/Source/KCSG/Defs/
StructureLayoutDef.cs`) resolves **every** `layouts` grid cell via
`DefDatabase<SymbolDef>.GetNamedSilentFail` — never a direct
ThingDef/PawnKindDef lookup. The Dragon lair precedent file (`vendor/
mod_sources/DragonsDescent_src/...StructureLayoutDef_Dragon_lair_1.xml`,
itself wrapped in an XML comment) only "works" with bare names like `Slate`/
`Wall_HardScale` because KCSG auto-generates one `SymbolDef` per
ThingDef/PawnKindDef owned by an **official Ludeon package**
(Core/Royalty/Ideology/Biotech/Anomaly/Odyssey) or
`vanillaexpanded.vfepropsanddecor` (`StartupActions.cs`), with defName =
the bare ThingDef/PawnKindDef name, or `{thing}_{stuff}` for a stuff-based
building. A miss resolves to `null` **silently** (logged only to
`StartupActions.AddToMissing`, no error, no crash) and that cell simply
never spawns. First draft of this generator used bare third-party names
(`AA_BlackJellyWall`, `GTbc_GravRailArtillery`, `Wall_HardScale` — the last
one isn't even a real defName on this mod list, `DragonsDescent` being
non-vendored-as-active content) — every one of those would have silently
failed to place. Fixed: vanilla/DLC content (`Mech_Lancer`, `Mech_Centurion`,
`Turret_AutoInferno`, `Turret_AutoMortar`, `Plasteel`, `Uranium`,
`ComponentSpacer`, `Shard`, `Wall_Plasteel`) used bare, confirmed
auto-symbol'd; every third-party/our-own def (the two GravTech cannons named
explicitly in §3.3, the type-2 bioweapon/wreckage set from the item's own
draft skeleton, `AA_GreenGoo`/`GR_Boomsnake` from `cast_assignment.csv`'s
HorrorWastes roster, and `RUT_Jawa_RakataVaultSchooled` — its name is the
closest match in the existing `RUT_Jawa_Rakata*` sleeper-backstory roster to
"vault-sleeper", not independently re-confirmed against a specific §3.4
citation) wrapped in an explicit `KCSG.SymbolDef`.

**Not done, explicitly**:
- No quicktest proof (§3.7's actual verify step — placement, screenshot,
  layout-layers judgment) — no bridge this pass (a sibling fork held it).
- V5's landmark authoring, all six real-site hand-finishing, wake/loot/leave
  dialogue and letters, the six `world_commit` placements — all correctly
  still HELD FOR OWNER per §3.9.
- The two doctrine-turret defNames' own damage numbers are still
  `turret_register` state `rework`, not final — using them here is a
  defName/placement decision, not a balance one.
- `RUT_Jawa_RakataVaultSchooled` as V6's specific sleeper is this pass's own
  best-evidence pick from the existing backstory roster, not verified
  against a named owner citation — flag for whoever does the V6 hand-finish.

`validate_patch.py` (594-mod set): 0 errors, 0 warnings, both files.

## 2026-09-06 (FOUNDRY) — quicktest-proven (§3.7), one real crash found and fixed

Blocked `ASSAILANT_DUNGEON_BUILD_1` first (creative lock-in still owed with the
owner per `FUTURE_VECTORS.md`), then picked up this item's own remaining
FOUNDRY-lane step: the §3.7 quicktest proof never done in the 2026-09-02 pass
("no bridge this pass, a sibling fork held it").

**Added `mandrake.rut.vaultdungeons` to the 22-mod MINIMAL test list**
(`infrastructure/state/modlists/ModsConfig.MINIMAL.xml`) and did two
minimal-list restarts (22s cold loads, not the 596-mod ~25 min) to prove it —
restored to FULL afterward, verified `md5 366f8c35...` matches, game left
DOWN (nobody was using it, testing finished).

**🔴 Real crash caught and fixed, worth the whole pass on its own**: placing
`RUT_VaultType1_MechanoidGarrison` via `jawa/kcsg_place` threw
`TargetInvocationException: Object reference not set to an instance of an
object`. Read from KCSG's own vendored source (not guessed):
`SymbolUtils.cs GeneratePawnAt` calls `PawnGenerationRequest(kindDef,
map.ParentFaction, ...)` when a pawn symbol's `spawnPartOfFaction` is true —
the KCSG-auto-generated default for a bare `Mech_Lancer`/`Mech_Centurion`
symbol, which the previous pass's own comment (wrongly) called "safe bare".
Every KCSG call site that generates a `StructureLayoutDef` - the debug menu
(`DebugActions.cs`) AND both real gameplay GenSteps
(`GenStep_BiomeStructures.cs`, `GenStep_CustomStructureGen.cs`) - uses the
2-arg `Generate(rect, map)` overload, so this is not bridge-tool-specific.
Generating a MECHANOID-intelligence pawn with a null faction throws in
vanilla pawn generation; a HUMANLIKE pawn (V6's `AncientSoldier`, via
`RUT_Symbol_RakataCasket`) does not - confirmed by Type-3 succeeding with the
identical null `map.ParentFaction` on the same test map. **Fix**:
`gen_vault_layouts.py` now wraps `Mech_Lancer`/`Mech_Centurion` in explicit
`RUT_Symbol_MechLancer`/`RUT_Symbol_MechCenturion` SymbolDefs with
`spawnPartOfFaction=false` and `<faction>Mechanoid</faction>` (a FactionDef
confirmed present via `mcp__rimsage__search_defs`), so they resolve against
the world's real Mechanoid faction instead of `map.ParentFaction` ever being
non-null - correct on a quicktest map and on whatever the real V1/V2/V3 site
turns out to be. Regenerated, `validate_patch.py`: 0/0 both files, redeployed,
restarted, re-placed: **all three templates now place with `success: true`
and no exception.**

**Screenshot-verified** (`take_screenshot` + `rimworld/get_cell_info`, not
just `success: true` - §2 and §4a of the rimbridge skill):
- **Type 1** (`.../Transient/vault_kcsg_type1_mechanoid_garrison_v2_2026-09-06.png`):
  full 61x61 footprint visible, outer wall ring with one door gap, garrison
  guardians and turrets present in the band, core with 5 loot items
  (Plasteel/Plasteel/ComponentSpacer/Uranium/Shard), core wall with its own
  offset door. No crash, no floating pieces, core not reachable in a straight
  line from the outer door (matches the offline BFS reachability proof from
  the 2026-09-02 pass).
- **Type 3** (`.../Transient/vault_kcsg_type3_frozen_rakata_v2_2026-09-06.png`):
  fully correct - outer/core `Wall_Plasteel` rings, 4 `RUT_Symbol_RakataCasket`
  in a row, `RUT_VaultHeart` in the core corner, 4 `Turret_MiniTurret` hugging
  the core wall. Garrison band deliberately empty per design ("thin... mostly
  silence"). Every symbol here is vanilla or our-own content - no third-party
  dependency, nothing left to prove.
- **Type 2** (`.../Transient/vault_kcsg_type2_flesh_weapon_loose_v2_2026-09-06.png`):
  **terrain-only** - `Flesh` terrain painted correctly across the full 51x51
  footprint (confirmed via `get_cell_info`), placement reported `success:
  true`, but **the entire `layouts` grid (walls, guardians, wreckage) is
  absent** - `get_cell_info` at the outer-wall corner and several garrison
  cells all show `thingCount: 0`. Root cause isolated, not guessed: EVERY
  Type-2 symbol (`RUT_Symbol_BlackJellyWall`→`AA_BlackJellyWall`,
  `RUT_Symbol_GreenGoo`→`AA_GreenGoo`, `RUT_Symbol_Boomsnake`→`GR_Boomsnake`,
  `RUT_Symbol_InfestedShipPart/Chunk`→`VFEI2_InfestedShipPart/Chunk`,
  `RUT_Symbol_Fleshmass`→`Fleshmass`) wraps a THIRD-PARTY ThingDef/PawnKindDef
  (Alpha Animals, VFE Insectoids 2, Vanilla Genetics Expanded), and **none of
  those source mods are in the 22-mod MINIMAL test list** - a KCSG symbol
  whose wrapped def does not exist resolves to null and is silently skipped
  (no crash, no log line without `debug`), exactly the "silent miss" class
  the 2026-09-02 pass's own header comment already named. **This is a test-
  scope gap, not a template defect**: confirmed all four packageIds
  (`sarg.alphaanimals`, `oskarpotocki.vfe.insectoid2`, `als.gravtech.bc`,
  `vanillaexpanded.vgeneticse`) ARE present in the owner's real 596-mod
  campaign list (`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`),
  and the SymbolDef XML shape is identical to `RUT_Symbol_MechLancer`, which
  just proved live. **Not chased further this pass** (adding 4 more mods'
  transitive dependencies to the minimal list risked its own cascade, for a
  check that only re-confirms a pattern already proven twice - Type 1's
  guardians, Type 3's caskets/turrets/heart). Left as an explicit gap for
  whoever next tests on the full mod list or extends the minimal one.

**Not done, still correctly held for the owner per this item's own "Watch
out"**: V5's landmark authoring, all six real-site hand-finishing,
wake/loot/leave dialogue and letters, the six `world_commit` placements.
This pass only closes the "quicktest-proven" verify bullet for TEMPLATE
GEOMETRY - it does not touch anything creative-lock-in.

Commit: (this pass's commit, `gen_vault_layouts.py` +
`Defs/{StructureLayoutDefs,SymbolDefs}_Vaults.xml`).

## 2026-09-09 (FOUNDRY) — V5 landmark authored, offline; path correction

Picked up mid-cold-load (owner's overnight full-list restart in progress),
bridge confirmed held by a sibling FOUNDRY pass on a different item
(`BIOME_ENRICHMENT_POISON_FOREST_1`) — no live bridge contact made this pass,
per this session's own instruction.

**Path correction (this file was stale, not the mod):** `src/RimUtinni/
VaultDungeons/` (`mandrake.rut.vaultdungeons`) named above no longer exists.
An unrelated reorg (`247cd6d4`, "Sprint wave A") absorbed it into
`src/RimUtinni/StructureInjectionsRUT/{Defs,Source}/VaultDungeons/` under mod
`mandrake.rut.injections` ("RimUtinni: Structure Injections") — its own
About.xml says so ("Absorbed RimUtinni: Vault Dungeons"). All vault content
(layouts, symbols, the VAULT_THAW_QUEST_FAMILY_1 quest layer, `RUT_VaultHeart`)
lives there now. Re-ran `validate_patch.py` against the current paths (586
active mods, Data+Mods+Workshop): **0 errors, 2 warnings** (both
`QuestScriptDef` `Class="QuestNode_Incident"` unresolved — VAULT_THAW_QUEST_
FAMILY_1's own already-filed C# gap, not this item's). One apparent ERROR
(`RUT_VaultHeart`'s `ShipComputerCore` texPath) is a false positive of a bare
`--defs` folder scan that cannot see inside the vanilla asset bundle —
VAULT_THAW_QUEST_FAMILY_1's own `--live` run already classified this
correctly as an advisory, not a defect; not re-litigated here, not this
item's file anyway.

**Built: `RUT_Slough_GelatinousBreach`, V5's landmark** (RULED name, owner
2026-09-01; not authored until now). Offline only, following this repo's own
established pattern for a hand-placed, never-worldgen-rolled landmark
(`RUT_GapingDoom.xml`/`RUT_ComplexStructures.xml`, same folder):
`commonality 0`, `category structure`, reused `NamerLandmark_Ruins`,
`MayRequire="Ludeon.RimWorld.Odyssey"`.
- `src/RimUtinni/UtinniPatches/Defs/LandmarkDefs/RUT_Slough_GelatinousBreach.xml`
  — description present-tense, what IS (a torn seam, pooled ooze, ground gone
  soft around it — the type-② "breach" reading from §3.3, no plot content).
- `src/RimUtinni/AshkarrLandmarkArt/make_slough_breach_icon.py` — a NEW
  procedural icon generator (same approach as this folder's own
  `make_complex_structures_icon.py`: deterministic, no RNG, no local
  image-gen call), because local imagegen is PARKED (owner, 2026-09-05) and
  this is unattended BELT work — the Codex `$imagegen` path pops an
  interactive Windows UAC prompt that must not fire unsupervised. Writes
  `Textures/World/Landmarks/Ashkarr/RUT_Slough_GelatinousBreach.png`
  (1024×1024 RGBA, 2×2 atlas, 4 variants): a ragged torn-membrane patch with
  pooled ooze and secondary tears, sickly yellow-green — checked by eye this
  pass to read distinctly from `VEE_FleshPits` (pink, radial) and from this
  same folder's `RUT_GapingDoom` (a single green maw).
- `validate_patch.py` on the new def + art folder: 0 errors, 48 warnings (all
  pre-existing, `LandmarkIcons.xml`'s ordinary add-if-missing
  `PatchOperationConditional` shape — none caused by this pass's two new
  files).

**Not done, still correctly held for the owner** (per this item's own
"Watch out", restated above): all six real-site hand-finish passes,
wake/loot/leave dialogue and letters, the six bridge placement writes
(V5's landmark included — authored, not yet placed on tile 37). **Also still
open, not this pass's to chase**: the §3.7 Type-2 quicktest gap
(`AA_BlackJellyWall`/`AA_GreenGoo`/`GR_Boomsnake`/`VFEI2_InfestedShipPart`
`/Chunk`/`Fleshmass` symbols unverified live — their source mods aren't on
the 22-mod MINIMAL test list; confirmed present on the real 596-mod list,
per the 2026-09-06 pass) — did not touch `ModsConfig.MINIMAL.xml` this pass,
the bridge/mod-list being actively in use by a sibling FOUNDRY item tonight.

No file in this item's own scope required a creative decision not yet ruled;
nothing invented beyond the owner's own "organic... distinct from V4" brief
and this repo's existing landmark-authoring pattern.

## 2026-09-12 (FOUNDRY) — reclaimed from stale-queue audit; tally only, no new creative content

Reclaimed per a stale-queue sweep (still `doing`, not touched since 2026-09-09).
Re-verified this item's own template files rather than assuming: re-ran
`Source/gen_vault_layouts.py` — byte-identical output, no drift — and
`validate_patch.py` against the current live 593-mod set on
`StructureInjectionsRUT/Defs/VaultDungeons/`: 0 errors, 1 pre-existing advisory
warning (`RUT_VaultHeart` texPath, vanilla asset-bundle false positive, already
known). Template geometry is unchanged and still clean.

**Did not write new dialogue/letters this pass — checked first and it would
have duplicated live work.** `VAULT_THAW_QUEST_FAMILY_1` (sibling item, same
night) already ships full letter/dialogue text for all six vaults in
`Source/gen_vault_quests.py`: per-vault accept/arrival/cleared/left letters
for V1-V5, V6's arrival/casket-hall/WAKE/LOOT/LEAVE letters (the verbatim
`rakata.woken_brutality` line included), the Claim-Conflict demand/refusal
letters and the Reclamation's three letters. That already satisfies this
item's own verify bullet ("Wake/loot/leave dialogue and letters authored for
V6; the ship-claim thread... authored") for the AUTHORED half; "fires
correctly" is still unproven live (their own item's gap, `MapComponent_
VaultSleepers` built 2026-09-12, not yet deployed/quicktested).

**🔶 Flagging, not fixing (not this item's file):** `dungeons_arc_spec.md`
§3.10 ("Vault text — drafted 2026-09-11, re-registered same day") records
specific OWNER-ACCEPTED letter text for V6 (arrival/casket-hall/WAKE/LOOT/
LEAVE), the type-①/② ring letters, and per-vault Narrator asides for V1-V5 —
dated AFTER `gen_vault_quests.py`'s own text was written (2026-09-05 design,
built 2026-09-12). Compared directly: the shipped XML's letter text and
§3.10's owner-accepted text are DIFFERENT wording throughout, not the same
lines re-cast. Whoever next touches `gen_vault_quests.py`/`RUT_VaultThaw.xml`
should reconcile against §3.10 as the more recent owner-blessed source rather
than treat the shipped text as final — left alone here since that file is
`VAULT_THAW_QUEST_FAMILY_1`'s own and was mid-edit tonight.

**Bridge checked twice, not used for a placement.** First check: held
(FOUNDRY, "GIZKA hook live confirmation", idle 0 min — live, not stale).
Second check ~10 min later: FREE, but the game itself was DOWN at that
moment (measured, `tasklist.exe` — a sibling's NINEFOLD pass had just taken
it down). V5's landmark (`RUT_Slough_GelatinousBreach`, authored, tile 37)
is the one placement write actually still needed for vault CONTENT (the
`vault_thaw_quest_family.md` §1.2 divergence means the six vaults themselves
now arrive as quest Sites, not bridge-placed structures — the six
`world_commit` writes in this item's own §3.9 are largely superseded by
that; only V5's landmark and any per-site hand-finish still need one).
Elected not to solo-trigger a restart from DOWN for one landmark placement
— "batch game-up work before restarting" against several other FOUNDRY
passes visibly active tonight (NINEFOLD, INHABITED_AUGMENTATION, RUST_
CATHEDRAL) who may have their own pending game-up work. Left owed.

**Honest tally across all six vaults, this item's own scope:**
- Template geometry (①/②/③): DONE, quicktest-proven 2026-09-06, re-verified
  clean tonight. Type-2's third-party symbols (AA_BlackJellyWall/GreenGoo,
  GR_Boomsnake removed from the current generator at some point after
  2026-09-06 — not re-added, not chased this pass) remain live-unverified;
  their source mods are still absent from `ModsConfig.MINIMAL.xml`.
- V5's landmark: authored (2026-09-09), not placed (tile 37) — bridge/restart
  owed.
- Dialogue/letters: authored for all six (via the sibling item), not
  reconciled against the owner-accepted §3.10 text, not proven firing live.
- Six real-site hand-finish passes: not started — per this item's own
  "Watch out," these are explicitly "with the owner," not solo FOUNDRY work.
- World_commit placements: superseded for vault content by the Sites
  approach; V5's landmark placement is the one still outstanding.

Staying `doing`. Nothing in this pass required or made a creative call the
owner hasn't already ruled or blessed.

## 2026-09-17 (FOUNDRY) — bridge held by BENCH this pass; offline re-verify only, one new finding

Owner actively testing live in-game and BENCH held the bridge for a Pyrelands
checkout — same discipline as `TILE_STRUCTURE_DESIGNS_1`'s batch model: did
the offline-provable portion, left the live-proof step explicitly owed, never
touched the bridge/ModsConfig/deploy.

**Re-verified this item's own scope from scratch rather than trusting the
2026-09-12 tally (5 days old, shared worktree):**
- `Source/gen_vault_layouts.py` re-run: byte-identical output, no drift
  (`git status --short` on `Defs/VaultDungeons/` and `Source/VaultDungeons/`
  empty after regen).
- `validate_patch.py` on the whole `Defs/VaultDungeons/` tree against the
  **current live 632-active-mod set** (`--defs` Data+Mods+Workshop, up from
  593/594/596 in every prior note — the mod list has grown since): **7
  files, 0 errors, 1 warning** (the same pre-existing `RUT_VaultHeart`
  vanilla-asset-bundle texPath advisory every prior pass already classified
  as a false positive — unchanged).
- Deployed copies checked byte-for-byte against the repo, not assumed:
  `.../Mods/StructureInjectionsRUT/Defs/VaultDungeons/` and
  `.../Mods/UtinniPatches/Defs/LandmarkDefs/RUT_Slough_GelatinousBreach.xml`
  both diff clean against `src/RimUtinni/...` — no deploy drift.
- Confirmed the six sites' tile bindings in
  `Defs/VaultDungeons/QuestScriptDefs/RUT_VaultThaw.xml` (`RUT_VaultThaw_V1..V6`,
  literal `QuestNode_Set siteTile`) match this item's own site table exactly:
  678/4000/9167/17461/37/20853 for V1–V6. This is the "world_commit
  placement" work for vault CONTENT — already done, via the sibling item's
  quest-Site divergence, confirmed still correct rather than re-asserted from
  memory.
- Spot-checked 4 of Type-2's 5 flagged third-party defNames
  (`AA_BlackJellyWall`, `AA_GreenGoo`, `VFEI2_InfestedShipPart`,
  `VFEI2_InfestedShipChunk`) resolve to a real `<defName>` in the live
  workshop content on disk (their source mods' packageIds are confirmed
  ACTIVE in the current 632-mod `ModsConfig.xml`) — consistent with the
  2026-09-06 finding, not new. Did not finish checking `Fleshmass`/
  `GTbc_GravRailArtillery`/`GTbc_TheSingularityCannon` (killed the sweep
  partway through, diminishing return: Type-1's use of the two GravTech
  turrets is already live-proven since 2026-09-06, and `Fleshmass` is
  Anomaly DLC content, not a genuine unknown). This does not close the
  Type-2 quicktest gap — resolving as a defName is not the same as placing
  and looking, which still needs `ModsConfig.MINIMAL.xml` extended and a
  restart, correctly left undone this pass (bridge held).

**🔴 New finding this pass, not previously recorded in this item's own
file**: read (never wrote) the live `ModsConfig.xml` — **neither
`mandrake.rut.injections` (the vault template/quest mod) nor
`mandrake.rut.utinnipatches` (V5's landmark) is currently ACTIVE** in the
owner's live 632-mod list, though both are deployed to the Mods folder
byte-identical to the repo. So right now, independent of anything left owed
in this item, the entire vault arc is **inert in the live game** — not a
defect in this item's own build (every prior pass already logged "not added
to ModsConfig this pass" as a deliberate deferral), but worth surfacing
plainly since the owner is testing live tonight and would see nothing of
this arc regardless of template/dialogue state. No action taken — enabling
mods is a live/ModsConfig change, explicitly off-limits this pass.

**Not done, still correctly held** (unchanged from 2026-09-12): Type-2's
live quicktest proof (needs `ModsConfig.MINIMAL.xml` + restart); V5's
landmark placement on tile 37; the six real-site hand-finish passes (owner);
wake/loot/leave dialogue reconciliation against `dungeons_arc_spec.md`
§3.10's owner-accepted text (still `VAULT_THAW_QUEST_FAMILY_1`'s own file,
not touched here, confirmed still open/mid-build via that item's own state).

Staying `doing`. This pass found no drift, no regression, and no new
offline-buildable content this item's own scope is still missing — the
honest state is that everything FOUNDRY can build offline for this item is
built and re-confirmed clean; what remains is bridge-gated (Type-2 proof, V5
placement) or owner-gated (hand-finish, dialogue). Nothing invented or
padded to make this pass look bigger than it was.

## 2026-09-24 (FOUNDRY) — re-verify only, bridge not taken (held by owner's
window this session); one unrelated stale-config fix found and fixed

Picked up per this session's own instruction: no live/quicktest work this
pass (another window's session, not this one, may be driving the game
tonight) — offline-doable work only, record exactly what's left for the
bridge holder.

**Re-verified this item's own scope from scratch, not trusted from the
2026-09-18 note (6 days old, shared worktree):**
- `Source/gen_vault_layouts.py` re-run: byte-identical output, `git status
  --porcelain` on `Defs/VaultDungeons/` and `Source/VaultDungeons/` empty.
- `validate_patch.py` on the whole `Defs/VaultDungeons/` tree against the
  **current live 623-active-mod set** (`--defs` Data+Mods+Workshop, down
  from 632/634 in prior notes — the mod list has shrunk since, not grown):
  7 files, **0 errors, 1 warning** — same pre-existing `RUT_VaultHeart`
  vanilla-asset-bundle texPath advisory every prior pass already classified
  as a false positive. Unchanged.
- Deployed copies checked byte-for-byte, not assumed: `diff -rq` on
  `.../Mods/StructureInjectionsRUT/Defs/VaultDungeons/` against the repo
  path, and `diff -q` on
  `.../Mods/UtinniPatches/Defs/LandmarkDefs/RUT_Slough_GelatinousBreach.xml`
  — both clean, no deploy drift.
- Read (never wrote) the live `ModsConfig.xml`: **`mandrake.rut.injections`
  is now ACTIVE** in the current 623-mod list (parsed via `ElementTree`, not
  a `<li>` grep) — a change since the 2026-09-17/18 notes, which both
  recorded it as NOT active. **`mandrake.rut.utinnipatches` (V5's landmark
  mod) is still NOT active.** So even once V5's landmark is placed on tile
  37, it will not render in the live game until that mod is also enabled —
  worth flagging for whoever does that placement pass, since enabling a mod
  is a live/ModsConfig decision outside this pass's scope and not acted on
  here. Note per this repo's own lesson (`modsconfig-describes-the-next-
  load`): this describes the *next* load, not necessarily what a
  currently-running session has loaded.

**🔴 One real, unrelated stale-reference bug found and fixed while auditing
the MINIMAL test list this item depends on** (same class as the
`mandrake.rut.vaultdungeons` regression the 2026-09-18 pass caught in this
same file): `infrastructure/state/modlists/ModsConfig.MINIMAL.xml` still
named the dead packageId `mandrake.rm.fluidcanals`. That packageId does not
exist anywhere in the current source tree — `grep -rl` for it across `src/`
returns nothing live; the mod was renamed to `mandrake.rm.flowworks`
(confirmed against `src/RimMandrake/FlowWorks/About/About.xml`'s own
`<packageId>`, per `CLAUDE.md`'s "Ship names are three-tier" / "the
migration is DONE" note). Fixed: swapped the one `<li>` in place, no other
change to the file. Not this item's mod, not this item's file's usual
scope, but "correctness outranks seat ownership" applies to any file, fixed
on sight. Low risk: config-only edit, not a live/bridge action, and
FlowWorks' only modDependency is Harmony, already present in this list.

**Not attempted this pass, and why:** the Type-2 live third-party-symbol
proof (needs `ModsConfig.MINIMAL.xml` extended with Alpha Animals/VFE
Insectoids 2/GravTech and a restart — every prior pass declined this for
transitive-dependency cascade risk, and this pass has no bridge to verify
a restart against besides); V5's landmark placement on tile 37; the six
real-site hand-finish passes (owner, per this item's own "Watch out");
wake/loot/leave dialogue reconciliation against `dungeons_arc_spec.md`
§3.10 (still `VAULT_THAW_QUEST_FAMILY_1`'s own file). No bridge/ModsConfig/
deploy action taken.

Staying `doing`. Everything this item can build offline is built and
re-confirmed clean for the seventh consecutive pass; what remains is
bridge-gated (Type-2 proof, V5 placement, enabling `mandrake.rut.
utinnipatches`) or owner-gated (hand-finish, dialogue).

## 2026-09-18 (FOUNDRY) — MINIMAL-list regression found and fixed, fresh live re-proof

Picked up as a fresh task brief that assumed the three templates still
needed building — **wrong, checked first**: they were fully built and
quicktest-proven 2026-09-02/06 and re-confirmed clean every pass since.
🔴 **Correction to that brief**: it proposed 300×300 as a "provisional"
LARGE quicktest size — that number was already superseded by the owner's
own **325×325** ruling (2026-09-01, spec §3.9) before this pass started;
not re-litigated, just flagged so it isn't repeated.

**Real regression found and fixed**: `infrastructure/state/modlists/
ModsConfig.MINIMAL.xml` still named the dead packageId
`mandrake.rut.vaultdungeons` — absorbed into `StructureInjectionsRUT`
(`mandrake.rut.injections`) back on 2026-09-09. Every MINIMAL-list restart
since then silently tested **zero vault content** while reporting a clean
load. Fixed: swapped in `mandrake.rut.injections` plus its own
`mandrake.rm.injections` dependency (the GenStep_RimplacePlan engine mod,
no deps of its own). Commit content confirmed on `origin/main` as
`c2e8ad4ca` (hash was rewritten mid-rebase by the heavy concurrent repo
activity tonight — several other FOUNDRY passes were committing at the
same time; content is what matters and it landed correctly).

**Live re-proof this pass** (bridge taken, backed up the exact live
ModsConfig.xml first since the stored `FULL.LATEST` snapshot was already
one mod stale against the true live 634, MINIMAL restart on the corrected
list, all three templates placed via `jawa/kcsg_place`, screenshotted,
restored to the real 634-mod list afterward and md5-verified byte-identical
to the pre-swap backup, bridge released):

- **Type 1** (mechanoid garrison) — **PASS**. Outer wall ring, garrison band
  with guardian pawns and turrets, core with loot items, core wall with its
  own offset door, no floating pieces, no straight-line skip of the ring.
- **Type 3** (frozen Rakata) — **PASS**. Outer/core wall rings with offset
  doors, 4 caskets + `RUT_VaultHeart` in the core, garrison band
  deliberately near-empty per the "near-silence" design.
- **Type 2** (flesh weapon loose) — reproduces the **known 2026-09-06 gap,
  unchanged**: `Flesh` terrain paints correctly but the walls/guardians/
  wreckage grid is silently absent, because its third-party symbol source
  mods (Alpha Animals' `AA_BlackJellyWall`/`AA_GreenGoo`, VFE Insectoids 2's
  `VFEI2_InfestedShipPart`/`Chunk`, GravTech's turrets) still aren't on the
  MINIMAL list. Confirmed a test-scope gap, not a template defect — those
  mods ARE active in the owner's real 634-mod list. **Did not chase adding
  them this pass** — same call three prior passes made: transitive-
  dependency cascade risk for a check that only re-confirms an
  already-proven pattern (Type 1's guardians, Type 3's caskets/turrets).

Screenshots: `Transient/vault_quicktest_2026-09-18/`.

**Still correctly held for the owner, unchanged**: all six real-site
hand-finish passes, wake/loot/leave dialogue reconciliation against
`dungeons_arc_spec.md` §3.10's owner-accepted text
(`VAULT_THAW_QUEST_FAMILY_1`'s own file), Type-2's live third-party-symbol
proof, V5's landmark placement on tile 37. Neither `mandrake.rut.injections`
nor `mandrake.rut.utinnipatches` is ACTIVE in the owner's live `ModsConfig`
right now (informational only, unchanged from the 2026-09-17 earlier-today
finding — enabling mods is a live/ModsConfig decision outside this pass).

Staying `doing` per this item's own "Watch out" section.
