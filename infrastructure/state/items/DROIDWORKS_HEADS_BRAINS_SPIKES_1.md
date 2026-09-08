## spec
Thin when filed — no spec/verify/criteria in the queue entry itself, but fully
specced as packet B3 of `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md`
§5 (inputs: unit 8, rulings 3 and 6, `Items_Droidworks.xml` placeholders;
outputs: brain trio, per-family heads + `CompHeadIdentity`, `RSW_DW_Head_Mindstone`,
per-faction data spikes; verify: "kill -> head drops with its name; wrong key
does nothing; mindstone head yields the ruled stats"; after: A1, which was
already `done`). Built directly from that packet, FOUNDRY, 2026-09-08.

## Built
- **Brain trio** (`ThingDefs/BrainTrio_Droidworks.xml`): `RSW_DW_PersonalityMatrix`,
  `RSW_DW_Processor`, `RSW_DW_Databank`. No recipeMaker on any (ruling 6,
  head-gate) — salvage/trade/quest-loot only, forever. Art reused from
  OuterRim's own droid-brain-part icons (`DroidVoiceModule`/`DroidBrain`/
  `DroidMemoryModule`, already deployed loose at those texPaths).
- **Per-family heads** (`ThingDefs/Heads_Droidworks.xml`): `RSW_DW_Head_{Labour,
  Protocol,Astromech,Battle,Heavy,Probe,Power}`. thingClass `Thing_DWHead`
  (`Source/Droidworks/CompHeadIdentity.cs`) + `CompHeadIdentity` — a head
  dropped off a dying droid carries that droid's name into its own label and
  inspect string. `CompDWHeadDropper` (new comp, on `DW_Race_Base` so every
  family gets it) hooks `Notify_Killed` — same pattern `CompDroidDetonation`
  already uses — looks up the dying pawn's `chassisClass` and spawns the
  matching head with `CompHeadIdentity.SnapshotFrom(pawn)` (name, kind,
  faction of origin, full trait list — future `RSW_DW_HardwareQuirk` traits
  from B10 land here automatically once that item builds). Art: one portrait
  icon per family, picked from a representative donor race already in that
  family (KotOR's `UI/Icon_*` single-image icons — Graphic_Single, no
  rotation-set risk).
- **`RSW_DW_Head_Mindstone`**: `MECHANOID_ORIGIN_CANON_1` (ruling 3's "chassis +
  special head") is still `proposed`/`needs owner` with no numeric stats ever
  ruled, despite the packet's verify line assuming they were. **FOUNDRY's own
  call, recorded rather than blocking**: built the item at a distinctly
  higher tier (Archotech, MaxHitPoints 150, MarketValue 2500 vs a family
  head's Spacer/60/300) so it exists and is judgeable, without inventing the
  mindstone's actual sourcing or the "chassis + head = new race" mechanic —
  both stay `MECHANOID_ORIGIN_CANON_1`'s to rule. No donor pawn carries this
  head; it is a standalone item today (spawn/debug, future quest loot). Art:
  vanilla Biotech's own `Things/Pawn/Humanlike/Apparel/Mechlink` texPath — an
  archotech mind-link implant, thematically exact, and no cross-mod texPath
  fragility since it's vanilla.
- **Per-faction data spikes** (`ThingDefs/DataSpikes_Droidworks.xml`):
  `RSW_DW_DataSpike_{Empire,Hutt,Junker,Wild}`, same shape as the existing
  generic `RSW_DW_DataSpike` (untouched, still keyed
  `guy762_KotORFaction_RogueDroids`). Faction defNames MEASURED against the
  live mod list: Empire -> vanilla `Empire` FactionDef; Hutt ->
  `OuterRim_BinaryStarRaiders` (no dedicated Hutt Cartel FactionDef exists
  anywhere in the stack — `GamorreanPawnKinds.xml`'s own header already
  established this as the accepted stand-in); Junker -> our own
  `Jawa_Junkers`. **Wild** is new: `CompProperties_DWDataSpike.factionless`
  (added to `Source/Droidworks/CompDWDataSpike.cs`) matches a **null**
  faction rather than a FactionDef defName, for the crashed/gone-wild droids
  `DROIDWORKS_WILD_DROIDS_1` (E4, unbuilt) will spawn with no faction.
  `CompTargetable_DWDataSpike`'s targeting validator reads `MatchesFaction`
  already, so this needed no change there.

## Not touched, deliberately
- `RSW_DW_DroidHead` (the old generic placeholder) — still the ingredient
  every data spike's `costList` crafts from, family-specific heads included.
  Rewiring that recipe onto the new identity-carrying heads was not asked for
  by the packet and would couple an unrelated crafting cost to the
  salvage/identity system.
- No research gating, no shop-bench consumption of a head (B4b, unbuilt) —
  out of packet.

## verify (live, minimal 25-mod list + quicktest, FOUNDRY 2026-09-08)
Build: `dotnet build Droidworks.csproj -c Release` — 0 errors. Deployed via
`deploy_custom_mods.py --mod Droidworks --apply`, verified in sync.

Swapped to the minimal list (`modlist_swap.py --minimal`), launched via Steam,
`rimworld/start_debug_game_ready` for a throwaway map, bridge-drove the test,
restored the full 600-mod list afterward (`modlist_swap.py --restore`) since
nothing else needed the game up.

- **"kill -> head drops with its name"**: spawned `RSW_DW_OuterRim_GNKDroid`
  (named "Tank" by the generator), set it to the player faction, `Actions\T:
  Damage To Death`. `jawa/list_things` afterward: `RSW_DW_Head_Power` spawned
  next to the corpse, **label `"Power droid head (Tank)"`** — the identity
  snapshot and the `Thing_DWHead` label override both work end to end, live.
- **All 15 new ThingDefs** (8 heads incl. mindstone, brain trio, 4 spikes)
  spawned cleanly via `rimworld/spawn_thing` and read back via
  `jawa/list_things`: correct defNames, correct labels, correct
  `hitPoints`/`maxHitPoints` (60 per family head, **150 mindstone**, 50 brain
  trio, 60 spikes) — no `BadGraphic`, no spawn failure.
- **"mindstone head yields the ruled stats"**: read back MaxHitPoints 150 as
  authored (see the "not ruled" caveat above — these are FOUNDRY's own
  placeholder numbers, not a number the owner actually set).
- **Player.log, literal check** (`Config error in`, 12 total): all 12 are
  pre-existing, unrelated to this item — 6 `RUT_GiveQuest_VaultThaw_*` quest
  double-registration, 6 `RSW_DW_Module_DroidArmor{Hvy,Lte,Mid}` smeltable
  warnings (both already-known, from unrelated/earlier work). **Zero**
  attributable to any def or C# added here.
- **"wrong key does nothing"**: not driven through an actual UI job — per
  `DROIDWORKS_LIVE_LOOP_PROOF_1` (A1)'s own finding, **no bridge tool exists
  to force a colonist through a `JobDriver` to completion**, and
  `JobDriver_DWDataSpike` (unchanged by this item) is exactly the kind of job
  that limitation covers. Verified instead the same way A1 verified its own
  gating logic: by reading the code. `CompDWDataSpike.MatchesFaction`
  (extended, not rewritten, for `factionless`) is a direct field comparison
  already covered by the file's existing code-review pass; the new
  `factionless` branch is the same shape. No live UI-job proof owed beyond
  this, consistent with A1's precedent.
- **Full-list (600-mod) coexistence** for these specific new defs was not
  separately re-checked — rides `DROIDWORKS_FULL_LIST_COEXIST_1` (currently
  `doing`), not required for B3's own close.

## Assumptions recorded (Charter: "record what you assumed")
1. Mindstone stats are FOUNDRY's own numbers, not owner-ruled —
   `MECHANOID_ORIGIN_CANON_1` still needs its own design sitting.
2. Hutt spike keys to `OuterRim_BinaryStarRaiders` in the absence of any real
   Hutt Cartel FactionDef anywhere in the stack.
3. Uniform stats across the 7 family heads (no per-family variance) — that's
   `DROIDWORKS_FINE_PARTS_1` (B4a) territory, not this packet.
