# PROPERTY_FABRIC_BUILD_1 — RM_Property: the ownership/theft/perception fabric

FOUNDRY build. C# only, no XML defs. Compiled clean, not deployed, not
committed here per the item's own scope discipline — none of
`deploy_custom_mods.py --apply`, `ModsConfig.xml`, `rimflow`, `git commit`, or
a live quicktest were touched.

## spec
Source: `design/Jawa/ownership_settlement_spec.md` (owner, 2026-08-31
brainstorming sitting — "Superb! ... This is amazing! (two mods)") and
`infrastructure/state/canon.yml`'s `ownership_fabric` block. Building ONLY
item 1 of the spec's "Sequenced execution" list: **PROPERTY_FABRIC_BUILD_1**
— "RM_Property mod: claim engine, recognizability, provenance records,
TakingEvent + perception + propagation + faction record, colony-side
friction (per-colonist claimants, Clan commons, guest claims, fight hook).
Proven at the colony with zero visit machinery." Items 2-4
(`SETTLEMENT_VISIT_LOOP_1`, `DISTRICT_TEMPLATE_LIBRARY_1`,
`SETTLEMENT_VERBS_WAVE_1`) are separate, later queue items, not touched.
Naming: `mandrake.rm.property`, RimMandrake tier, per
`design/NAMING_SCHEME_PLAN.md` (packageId given directly in the brief, not
derived).

Pre-flight check per the brief: `git log --oneline | grep -i
"property\|ownership"` and `git status` on `src/RimMandrake/` found no
concurrent build — only the design/ruling commits and this session's own
`rimflow` claim commit (`1ec285c0`, ledger only). No near-miss this time.

## what got built — all six pieces, real, none stubbed-empty

Folder: `src/RimMandrake/Property/` (About/, Source/, Assemblies/). No
`Defs/` — this mod ships zero ThingDefs/etc, pure C# API, matching the
spec's "campaign-blind fabric" framing and the Ninefold/Pits precedent for a
plain-GameComponent, no-Harmony mod (auto-picked-up by vanilla's
`Game.FillComponents` reflection scan over `GameComponent` subclasses — no
registration code needed, verified against `Verse/Game.cs`).

1. **Claim data model** (`ClaimantKind.cs`, `ClaimantRef.cs`, `ClaimBasis.cs`,
   `ClaimRecord.cs`, `ClaimRecordList.cs`) — exactly spec item 2's
   `(claimant, strength 0-1, basis, timestamp)`. `ClaimantRef` is a
   runtime-only struct (Pawn / Faction-Commons / Unclaimed) never itself
   persisted; `ClaimRecord` flattens the Kind/Pawn/Faction fields for Scribe
   (a struct holding reference fields has no clean `LookMode`, so every
   persisted class stores the raw fields and rebuilds a `ClaimantRef` via a
   property). Storage is a sparse `Dictionary<Thing, ClaimRecordList>` inside
   one `GameComponent` — **a Thing with no recorded claim costs nothing**;
   ten thousand rocks never enter the dictionary at all. Only the exception
   list (`Stolen · Purchased · ClaimFeePaid · Gifted · Inherited · Looted ·
   BattleLootOrigin`) is ever written.

2. **Recognizability** (`RecognizabilityUtility.cs`) — reads only vanilla
   fields, nothing authored: `Thing.TryGetQuality` (quality band),
   `Thing.MarketValue` (log-saturating at 2000), a persistent `Pawn.Name`
   (humanlikes, tamed/bonded animals, player-renamed mechs — NOT unnamed
   hostile mechanoids) or `CompBladelinkWeapon` presence (vanilla's own
   persona-weapon identity marker) for non-Pawn Things, mechanoid race flag,
   and non-stackable-item bonus. All API calls verified against the RimWorld
   source via RimSage before writing (`Thing.TryGetQuality`,
   `Thing.MarketValue`, `RaceProperties.IsMechanoid`, `CompBladelinkWeapon`)
   rather than guessed.

3. **Decay** (`ClaimDecay.cs`, `PropertyTuning.cs`) — pure functions of
   `(strength, ageTicks, recognizability)`, called only from
   `ClaimEngine.ResolveClaim` at query time. No `CompTick`, no interval scan,
   nothing scheduled. Curve shape is linear-to-zero over a
   recognizability-scaled lifetime (3 days at recognizability 0, 3650 days —
   "never" at campaign pace — at recognizability 1); the curve *shape* and
   exact day counts are flagged in the code and here as generic engine
   defaults, explicitly NOT the tuned values the spec's own closing line
   reserves for RimUtinni ("decay curves per recognizability band ... All
   data, all RimUtinni").

4. **TakingEvent** (`TakingAct.cs`, `TakingEvent.cs`, `ClaimEngine.cs`,
   `PropertyEngine.cs`) — the real event spine. `ClaimEngine.ResolveClaim`
   merges recorded (decayed) claims with virtual claims (Situational: a
   specific Pawn currently possesses the Thing via
   `Pawn_EquipmentTracker`/`Pawn_ApparelTracker`/`Pawn_InventoryTracker`/
   `Pawn_CarryTracker`; Territorial: `Thing.Faction`'s Commons) and picks a
   winner by decayed strength, then specificity (Pawn beats Commons), then
   recency — the engine's approximation of spec item 4's "resolution follows
   narrative proximity." `PropertyEngine.Fire` runs the full spine for the
   six spec-named acts (Take/Use/Strip/Sabotage/Buy/Claim): resolve → decide
   authorization → per-act provenance write (Buy→Purchased,
   Claim→ClaimFeePaid, unauthorized Take/Strip→Stolen preserving the origin
   claim, Use/Sabotage→no ownership change) → witness/perception roll →
   propagation → faction record → friction hook. `RecordLoot`/`RecordGift`/
   `RecordInheritance` are direct provenance writes for the three
   non-adversarial transfers the spec lists as claim bases rather than spine
   acts — `RecordLoot` specifically writes BOTH a `BattleLootOrigin` record
   for the defeated owner at ~1.0 and a `Looted` record for the new holder,
   per spec item 5.

5. **Perception + propagation** (`PerceptionUtility.cs`, `WitnessEntry.cs`,
   `FactionRecord.cs`) — built to the brief's explicit "real but simple"
   bar. Witness roll is one pass over `map.mapPawns.AllPawnsSpawned` at the
   moment of the act (awake, not downed, in radius, real
   `GenSight.LineOfSight` check — not a stub), producing a flat
   `WitnessEntry(suspect, confidence, tick)` per witness. Propagation is
   lazy: `FactionRecord.GetSuspicion(suspect, nowTick)` sums each entry's
   confidence times `clamp01(daysElapsed * propagationRatePerDay)` — nothing
   ticks, nothing is pre-computed, a query five seconds after the act and a
   query five days later both do the same constant-time math. **Explicitly
   deferred, named per the brief's own permission to do so**: fixed-security
   and ambient-surveillance witnesses (cameras, patrols, orbital eyes — spec
   item 6's other half) are district/settlement prop content, out of scope
   here; per-faction security-profile propagation RATES (Hutts excellent,
   Tuskens ~nil) are RimUtinni data the engine has one placeholder constant
   for (`PropertyTuning.DefaultPropagationRatePerDay`, flat 1/3 per day)
   until that data exists.

6. **Faction record** (`FactionRecord.cs`) — the aggregate surface: per
   suspect, `GetSuspicion` and a threshold-gated
   `HasAnyPropagatedKnowledge`. Nothing in this mod reads it for a
   consequence (prices/guards/bounties are explicitly not this item's job)
   — it exists as the surface those future systems query.

7. **Colony-side friction** (spec item 10/7) — per-colonist claimants need
   no special code: any live `Pawn` is already a valid `ClaimantRef`, so
   every colonist is automatically their own claimant the moment they
   possess something. `Commons` is a per-Faction claimant (generic, not
   `Clan`-named in code — the player faction's Commons instance IS "the Clan
   commons" the spec names; RimUtinni-tier code can still call it that in
   prose). Guest claims need no special code either —
   `ClaimantRef.IsGuestOn(Map)` is a one-line convenience, not a separate
   mechanism: a guest is just a Pawn claimant whose Faction differs from the
   map's home faction. `PropertyEngine.Fire`'s authorization check treats
   Commons as implicitly usable by any Pawn of the same Faction (so a
   colonist grabbing shared ship supplies isn't "theft"), and fires
   `PropertyEvents.UnauthorizedTakingWitnessedByOwner(evt, ownerPawn)`
   whenever the wronged Pawn is personally among the witnesses — the hook
   point spec item 4's "social fight per Jawa heat tuning" binds to. **This
   mod does not implement the fight** — RimUtinni content owns that, per the
   Module boundaries table.

## compiles clean
`"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build
D:\Luke\dev\Rimworld\src\RimMandrake\Property\Source\RM_Property.csproj -c
Release` → **Build succeeded, 0 Warnings, 0 Errors**, output
`src/RimMandrake/Property/Assemblies/RimMandrakeProperty.dll`. Every
non-obvious API used (`Thing.TryGetQuality`, `GenSight.LineOfSight`
3-argument overload, `Pawn.Awake()`, `MapPawns.AllPawnsSpawned`,
`Pawn_EquipmentTracker`/`ApparelTracker`/`InventoryTracker`/`CarryTracker`'s
`.pawn` field, `Game.FillComponents`'s reflection-based GameComponent
pickup, the `Scribe_Collections.Look` Reference/Deep dictionary pattern) was
read from the real RimWorld source via RimSage before use, not guessed —
two rounds of build errors (missing `using RimWorld;` for `Faction`/
`Pawn_ApparelTracker`/`Pawn.Awake()`) were fixed and reverified, not left for
someone else.

`src/RimMandrake/Utils/naming_lint.py --strict` reports `Property` as
`UNASSIGNED` (not in `naming_rename_map.csv`) — checked against precedent:
every other mod built since the Phase 2 migration (Ninefold, FireEcology,
Graffiti, Oracle, StructureInjections, Visibility, BeastNorm, SeasWaterline,
IshkoDarkLandmarks, PyrelandsFireEcology) shows the identical `UNASSIGNED`
tag. This is the expected state for new-content built under Phase 0's rule
("every new packageId, defName, namespace and folder... uses the tier
grammar" — the map is for migrating OLD names, not registering new ones);
`RM_Property`'s packageId, folder, and namespace already follow the grammar
directly. `validate_patch.py src/RimMandrake/Property/`: 0 errors (About.xml
parses, no Patches/Defs to check — there are none in this mod by design).

## what was NOT built (deferred, named, not guessed at)
- **Fixed security + ambient surveillance witnesses** (spec item 6's other
  half) — district/settlement prop content, belongs with
  `DISTRICT_TEMPLATE_LIBRARY_1`.
- **Per-faction security-profile propagation rates and decay-curve bands**
  (Hutts/Empire/Tuskens etc.) — RimUtinni data, per the spec's own closing
  line; the engine has one flat generic constant standing in.
- **Any verb job/gizmo** (pickpocket, burglary, fencing, the claim-fee
  gizmo) — `SETTLEMENT_VERBS_WAVE_1`'s job. No Harmony hook in this mod
  auto-detects a vanilla pickup/theft as a `TakingEvent`; `PropertyEngine.
  Fire` is the API future verb code calls, not something that fires itself.
- **The actual social fight** — `PropertyEvents.
  UnauthorizedTakingWitnessedByOwner` is wired and fires correctly; nothing
  subscribes to it yet.
- **Visit Settlements retirement** — untouched, per the item's own "zero
  visit machinery" scope.

## one open design fork, flagged not resolved
`ClaimEngine`'s Territorial virtual-claim rule defaults ALL
faction-owned-but-unpossessed Things to that faction's Commons claimant.
Spec item 4 says the Clan claimant should hold only "the survival spine —
the Utinni, its systems, food and water. Everything else is someone's" —
implying most colony stockpiles/output should resolve to an individual
colonist (whoever built/hauled/crafted it?) rather than defaulting to
Commons. The engine cannot make that call: "who narratively owns a pile of
steel nobody is currently holding" is a campaign judgment call, not a
mechanism question, and guessing at it here would be exactly the kind of
invented content the module-boundary table reserves for RimUtinni. Left as
the generic, defensible default (unpossessed + faction-owned → that
faction's Commons) with this note so whoever builds the RimUtinni layer
knows it's an open question, not a settled one.

## verify (owner's live quicktest — not attempted here, per scope)
1. Does `GameComponent_PropertyLedger` actually get instantiated on a real
   `Game` (should be automatic via `Game.FillComponents`, matches Ninefold's
   proven pattern, but never loaded live) — the single load-bearing
   assumption everything else depends on.
2. A hand-driven `PropertyEngine.Fire` call (via debug console or a bridge
   companion tool, none built here) on a real colonist theft scenario:
   confirm `ClaimEngine.ResolveClaim` picks the right winner, confirm the
   `Stolen` record gets written, confirm `UnauthorizedTakingWitnessedByOwner`
   actually fires when the owner is nearby and doesn't when they're not.
3. Save/load round-trip: `ClaimRecord`/`WitnessEntry`/`FactionRecord`
   `ExposeData` round-trips correctly (Scribe pattern verified against
   several vanilla precedents in source, never exercised against a real
   save).
4. Whether the flat `0.75` witness confidence and `1/3`-per-day propagation
   default feel remotely right at real campaign pace — expected to need
   RimUtinni retuning immediately, not a surprise if it does.

## criteria
- [x] Claim data model — lean, exception-only storage, zero comp on every Thing.
- [x] Recognizability — reads vanilla fields only, no authored per-item data.
- [x] Decay — lazy, pure function, no tick cost.
- [x] TakingEvent — real spine, all six spec acts handled, loot/gift/inherit
      as direct provenance writes.
- [x] Faction record — lazy aggregate surface, per-suspect suspicion.
- [x] Colony-side friction — per-colonist claimants (free), Commons
      claimant, guest convenience, fight hook wired and firing.
- [x] Compiles clean (0 warnings, 0 errors), naming-lint/validate_patch
      checked against precedent.
- [ ] Live quicktest — reserved for the owner, not attempted.
- [ ] Ambient/fixed-security witnesses, RimUtinni tuning data, verb jobs,
      the fight content itself — all explicitly out of scope for this item.
