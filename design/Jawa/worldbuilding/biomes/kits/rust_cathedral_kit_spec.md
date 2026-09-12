# RUST_CATHEDRAL_MECHANICS_1 — C# mechanics kit spec (DRAFT)

Engine mapping for the mechanics fixed in
`design/Jawa/worldbuilding/biomes/the_rust_cathedral.md` (frozen sheet — §5/§6
bans, §7 wall ladder, §7b hum-mood, §4 eels and bolts) plus the owner's
2026-09-07 roach addendum on the item. **No new lore here.** Every engine class
named below was verified against the vanilla 1.6/Odyssey source via RimSage on
2026-09-11 unless marked ❓. Donor DLL claims were measured with a real
metadata reader (dnfile TypeDef/TypeRef/MethodDef enumeration), not `strings`.

Ruled-comp reuse baseline: the six RM_ generic comps ruled IN 2026-09-11
(`design/Jawa/worldbuilding/alpha_family_source_review.md` §4, build item
`ALPHA_MECHANICS_KIT_1`), referenced as **RC1–RC6** per
`kits/scarlands_kit_spec.md`'s header.

Naming: mechanism classes at **RM_** tier (a banded biome-attitude value, a
vermin-cleaner ThinkNode — nothing below is Star-Wars- or Utinni-specific as a
*mechanism*); content defs (the hum's sounds and thresholds, wall/resource
defs, bolts, eels, roaches) at **RUT_** per `design/NAMING_SCHEME_PLAN.md`.
"Jawa" is lore text only.

Register law (sheet §6): every player-facing string this kit ships is §P
register. Ban 1 (no §GM truth), ban 2 (no mercy explanation), ban 6 (no
deep-drill explanation) are linter-checkable and repeated per mechanic below.

---

## 1. The hum-mood system (attitude value · layered tones · bolt-dance display · droid commentary · hysteresis)

**Player experience.** The hum is everywhere on Cathedral ground, and it
*reacts*. Mine deck plate all day and it stays a warm drone. Hook an eel, crack
a strange wall, park a deep drill — and a new tone slides in under the first,
then another. The bolts' dances go stiff, then stop. A droid, if you have one,
says something unhelpful and frightened. Push on anyway and the letters start;
push past those and the Sentinels' faction flips hostile — and stays hostile
long after you stop.

**Engine route — the ledger is vanilla, the voice is new:**

- **The ledger (zero C#).** The attitude's slow layer IS faction-13 player
  goodwill (the Forsaken Arsenal, hidden faction), exactly as the 2026-08-19
  sacrilege economics ruled. VERIFIED the ruled hysteresis is *vanilla
  behavior, not custom work*: `FactionRelation.CheckKindThresholds` flips to
  Hostile at goodwill ≤ **−75** and returns a Hostile faction to Neutral only
  at ≥ **0** (`FactionRelation.cs:24-46`) — the −75/0 hysteresis ships in the
  engine. Standing offenses (sacred buildings claimed/occupied) can ride
  `GoodwillSituationDef` natural-goodwill pressure: VERIFIED
  `Faction.NaturalGoodwill` + the ReachNaturalGoodwill drift (`Faction.cs:106,
  375-384`) walks actual goodwill toward the situation-defined value at ≤10 per
  step — that drift IS "the long ladder of warnings before −75".
- **The fast layer.** New **`RM_MapComponent_BiomeAttitude`** (M): one float
  ("irritation") that event inputs bump (per-mechanic below) and time decays;
  composite band 0–4 = f(goodwill, irritation), thresholds data-driven via a
  `RM_BiomeAttitudeDef` (new Def type, S) so other biomes could reuse the
  mechanism. Sustained max-irritation converts to goodwill ticks against
  faction 13 at a capped rate — the hum never flips hostility by itself; the
  ledger does.
- **Layered tones.** The map component holds one `Sustainer` per band layer,
  spawned/killed on band change — VERIFIED donor shapes:
  `UndercaveMapComponent` (staged OnCamera collapse sustainers,
  `UndercaveMapComponent.cs:130-141`) and `CompObelisk`'s three
  stage-sustainers (`CompObelisk.cs:174-200`). Content: `RUT_HumLayer0..4`
  SoundDefs. No WeatherDef route needed (VERIFIED `WeatherDef.ambientSounds`
  exists but weather is the wrong owner — the hum must survive weather
  changes).
- **Bolt-dance display.** The bolts (§3) read the band from the map component
  in their think tree — dance at high bands, stiffen, then **freeze at band
  0** (highest-priority conditional node). The bolts are the ONLY display
  creature (owner ruling on the item: roaches are fauna, not instrumentation —
  no roach tell of any kind, input or display).
- **Droid commentary.** S: the map component fires a `Messages.Message` on
  band *transitions* when a player droid is on the map, text drawn from a
  `RUT_HumCommentary` RulePack keyed by band. Every line is §P register; ban 2
  applies verbatim — the sheet's one permitted register is the droids' own
  incomprehension ("Why have you angered this place?..."). ❓ whether to
  attribute lines via the interaction-log (nicer) or plain messages (S) —
  build decides; no mechanical difference.
- **Hysteresis wiring check owed at build:** the ruled −15 per sacred building
  — VERIFIED vanilla fires `HistoryEventDefOf.AttackedBuilding` goodwill
  changes (`Faction.cs:793`) but ❓ whether the magnitude is settable to −15
  per building from XML; if not, one small Harmony postfix scoped to
  faction 13 buildings on Cathedral maps sets the ruled number.

**Reuse:** vanilla goodwill/hysteresis/situations; no RC comp fits (this is
map-state + audio, not hazards). New C#: `RM_MapComponent_BiomeAttitude` +
`RM_BiomeAttitudeDef`.

**INVENTED parameters (owner tunes):** irritation decay half-life 1 day; band
thresholds at composite 80/55/30/10; irritation→goodwill conversion −1 per 4h
at max band, capped −5/day; commentary cooldown 12h.

**v1:** ledger coupling + fast layer + 3 sustainer layers + bolt-band read +
message commentary. **Deferred:** hum-literacy as a learnable/tradeable
knowledge item (sheet §7 — wants its own design pass), per-colonist
teeth-felt mood thought, the once-in-a-great-while line-cycle ambient event
(pure dressing, its own S item).

**STAGED-LORE COUPLING:** commentary and letter text stay
staged-lore-addressable via `STAGED_LORE_BUILD_1` description swaps — no
second swap mechanism here (same rule as the Scarlands kit).

**Effort: M.**

---

## 2. Wall-tier mining defs (the wall ladder, §7)

**Player experience.** The map is made of money in tiers: endless deck plate
anyone may strip, seams of dead smartsteel worth real trade, strange sacred
walls that cost goodwill to claim — and, below everything, metal that is still
*live*, which the drill finds (§5).

**Engine route — almost entirely XML on the VERIFIED `MineableSteel` pattern**
(`RockBase` parent; `mineable`, `building.isResourceRock`,
`building.mineableThing`, `building.mineableYield`, `veinMineable`,
`MaxHitPoints` — full def read via RimSage):

- **Tier 1 — `RUT_CathedralDeckPlate`**: mineable wall ThingDef, yields
  vanilla `Steel`, generous lumps, unowned → zero goodwill, zero hum input.
  "Mine the bulk freely" made literal.
- **Tier 2 — `RUT_MineableDeadSmartsteel`**: yields new resource ThingDef
  **`RUT_DeadSmartsteel`** (stuff-capable ❓ — decide at build whether it is a
  trade commodity only or a buildable stuff; the sheet only requires
  "distinctly valuable"). Still free to mine (§5: "mineable bulk free").
  Description is §P: defunct alloy, nothing about micromachines' nature
  beyond what §P already says.
- **Tier 3 — the sacred tier**: NOT mineables — **faction-13-owned building
  ThingDefs** (`RUT_SacredWall_*` variants + the ~10 ruled sacred buildings,
  content pass). Destroying/claiming them is the sacrilege economics: vanilla
  `AttackedBuilding` goodwill (§1's ❓ magnitude check) + a hum irritation
  bump. "Worth mining out — really destroying and claiming" is priced, not
  prevented.
- **Tier 4 — the deep live-pattern metal**: a deep-drill resource, not a
  wall — VERIFIED `ThingDef.deepCommonality` / `deepCountPerPortion` /
  `deepLumpSizeRange` (`ThingDef.cs:96-102`; the engine enforces
  commonality↔lumpSize set together, `ThingDef.cs:1856-1858`). Resource
  **`RUT_LivePatternMetal`**, Cathedral map gen only. Drilling it is what
  arms §5 — the mechanic itself lives in §2 of the drill section below.

**Reuse:** vanilla mineable/deep-resource plumbing; no RC comp; **zero new C#**
(tier-3 goodwill magnitude rides §1's check).

**INVENTED parameters:** deck plate yield 35 Steel/lump-cell; smartsteel
market value ~8/unit, yield 25; live-pattern deepCountPerPortion 35.

**v1:** all four tiers as defs + map-gen scatter weights. **Deferred:** the
"rarer, stranger wall types" beyond one sacred wall variant (art-hungry;
content pass), wall-linked art atlases (rides the art pipe).

**Effort: S.**

---

## 3. Living bolts as mechanical wildlife

**Player experience.** Component-looking creatures a colonist tries to pick up
and simply move out of the way. They dance — complex, patterned, for no reason
anyone can name — and sometimes they stop, all at once, and old hands know
what that means. They cannot be tamed, they are not meat, and now and then one
sheds a curiosity worth selling.

**Engine route.** The donor roach mech (§6) proves the def shape live: a
mechanoid-fleshed PawnKind spawns as wild map fauna with no faction.

- **`RUT_LivingBolt`** ThingDef/PawnKindDef: mechanoid flesh (not organic →
  not butcherable into meat, exactly the sheet's implementation note), tiny
  bodySize, no trainability, negligible combat, wild spawn via the biome's
  `wildAnimals` roster (roster JSON already owns the cast; this kit owns the
  def shape).
- **The dance** — the one real piece of C#: **`RM_JobGiver_ResonantDance`**
  (M): emits short queued-move jobs in generated cell patterns (loops,
  figures, alignments), pattern energy scaled by the §1 band; a
  higher-priority conditional freezes the pawn at band 0 (stand job, no
  wander). Think tree assembled from vanilla subtree nodes the donor's own
  `AnimalConstantEatWastepack` tree demonstrates (measured in the donor XML).
- **Bolt-shed curiosities**: VERIFIED `CompSpawner : ThingComp`
  (`CompSpawner.cs:6`) on the race — periodically drops
  **`RUT_BoltShedCuriosity`** (trade-goods ThingDef). "Watched" (§7): picking
  one up adds a small §1 irritation bump; killing a bolt a large one (the
  bolts are its thoughts — §GM; the def description says none of this, ban 1).
- **Untameable/unhuntable polish**: no `race.wildness` taming route
  (trainability null) ❓ + verify at build the designator paths (hunt allowed
  but priced via the irritation bump — the sheet prices sacrilege, it does
  not un-button the gun).

**Reuse:** vanilla CompSpawner; no RC comp. New C#: `RM_JobGiver_ResonantDance`.

**INVENTED parameters:** 6–10 bolts per map; shed interval 4–8 days;
curiosity value ~40; irritation +3 pickup / +15 kill.

**v1:** def + dance/freeze + shed + watched pricing. **Deferred:** dance
choreography variety passes, synchronized multi-bolt figures, fleck/sound
garnish per dance.

**Effort: M** (the dance giver; the rest is XML).

---

## 4. Eel-fishing consequences

**Player experience.** The canals can be fished, and the eel-catch sells. But
the hum changes the moment a line goes in — every time, before anything else
happens — and a colony that fishes like it owns the water finds out by
letter, then by worse, that it does not.

**Engine route.** Odyssey's fishing stack, VERIFIED end to end:
`WaterBodyTracker` (per-body fish `Population`, `Notify_Fished`),
`Zone_Fishing`, `JobDriver_Fish`, `FishingUtility.GetCatchesFor` (biome
`fishTypes`, rare catches via `rareCatchesSetMaker`, negative catches gated
at 2%/cooldown), and **`NegativeFishingOutcomeDef`** — a whole vanilla Def
type keyed per `fishType` carrying letterLabel/letterText/damageDef/
damageAmountRange/addsHediff (read whole via RimSage).

- **`RUT_CoolantEel`** fish ThingDef, sole entry in the Cathedral biome's
  `fishTypes` (canal water bodies only — the 8 canal tiles). §P description
  only: blind, pale, old; nothing about being *kept* (ban 1).
- **Line-in tell (zero-Harmony route):** `RM_MapComponent_BiomeAttitude`
  scans on its own interval for pawns executing the fish job on Cathedral
  water — irritation bump the moment fishing *starts*, satisfying the
  sheet's "the moment a line goes in" without touching vanilla code. ❓ at
  build: if the interval scan feels laggy in play, a one-line Harmony
  postfix on `JobDriver_Fish` toil start replaces it.
- **Per-catch price:** each caught eel = irritation + a small direct
  faction-13 goodwill tick (the catch is the ledger-grade offense; the line
  in the water is hum-weather). Salable stays true — the sheet prices the
  eel-catch, it does not forbid it.
- **The sharp end:** one **`RUT_NegativeFishingOutcome_CoolantEel`**
  (vanilla `NegativeFishingOutcomeDef`, fishType = the eel): bite/shock
  damage + an undescribing letter. Vanilla's own 2% chance + 5-day cooldown
  gates it (VERIFIED `FishingUtility.cs:22-24,106-126`).
- **Population truth:** eels regrow per `WaterBodyTracker.Tick`'s
  population math; overfishing empties the canal the vanilla way. ❓ whether
  `map.TileInfo.MaxFishPopulation` is nonzero on the Cathedral's authored
  tiles — check against the frozen world data at build; if zero, the biome
  needs its fish-population stat set or the tracker never ticks.

**Reuse:** vanilla fishing stack + §1's component; no RC comp. New C#: none
beyond §1.

**INVENTED parameters:** irritation +5 line-in, +2 per catch; goodwill −1
per 3 catches within a day; eel market value ~18.

**v1:** eel def + biome fishTypes + line-in/per-catch pricing + one negative
outcome def. **Deferred:** rare-catch table for the canals
(`rareCatchesSetMaker` — a bolt-adjacent oddity; content pass), eel-catch as
a droid-faction trade good with its own price curve.

**Effort: S.**

---

## 5. The deep-drill response event — never described

**Player experience.** Dig deep enough and very bad things happen. No one's
quite sure what. *(That is the whole design. Ban 6 is absolute: no text —
letter, def description, commentary line, art note — ever describes the
response beyond "massive mechanoid movement".)*

**Engine route.** Vanilla already runs per-drill MTB incidents: VERIFIED
`StorytellerComp_DeepDrillInfestation` (MTB days per usable drill,
difficulty-scaled) firing category `IncidentCategoryDefOf.DeepDrillInfestation`
(`StorytellerComp_DeepDrillInfestation.cs`). The kit clones the shape, not the
bug spawner:

- **`RUT_DeepDrillCathedralResponse`** IncidentDef (category
  DeepDrillInfestation) + worker **`RUT_IncidentWorker_CathedralResponse`**
  (S/M): `CanFireNowSub` gates on Cathedral biome + a drill that has tapped
  `RUT_LivePatternMetal` (§2 tier 4). Effect: a large Sentinel force enters,
  converges on the drill site, destroys the drill and anything defending it,
  and **withdraws** — reusing the Scarlands kit's
  `RM_LordJob_DefendPerimeter` bound to the drill point, then a leave toil.
  Movement against the violation, never an assault on the colony: sheet §5's
  "massive mechanoid movement" implemented without breaching ban 3 (no
  manhunts, no pursuit past the bounded radii — the ruled 72/80 radii carry
  over).
- **Letter text**: label and one §P sentence that describes nothing. The
  storyteller comp rides the vanilla one via a small
  `StorytellerCompProperties_DeepDrillInfestation` entry pointed at the
  Cathedral incident ❓ — verify at build that category selection picks the
  RUT_ incident on Cathedral maps over vanilla infestation (both are
  UsableIncidentsInCategory candidates; if the roll can land on vanilla bugs
  here, gate vanilla's worker off Cathedral maps with a one-line patch).
- **Escalation coupling:** firing the event also floors the §1 band and takes
  a large goodwill bite — drilling the deep metal is the top of the
  sacrilege ladder.

**Reuse:** vanilla storyteller plumbing + Scarlands `RM_LordJob_DefendPerimeter`.
New C#: the incident worker (+ possible leave-toil addition to the lord, S).

**INVENTED parameters:** MTB 6 days per tapped drill; force size 2–3× current
threat-scale Sentinel points, capped; withdrawal 1 day after drill death.

**v1:** incident + worker + lord reuse + undescribing letter. **Deferred:**
pre-event tremor tells (flecks/sounds — dressing), partial responses at
shallower tiers.

**Effort: M.**

---

## 6. The roaches — the land cleaners (owner addendum, 2026-09-07)

**Player experience.** Small scuttling things working the ground: organic
roaches in the Scarlands' scar-dust, and in the Cathedral's shadow their
synthetic cousins — patient, incongruously hard to kill, cleaning a land
nothing else tends. The land counterpart to the coolant eels. They tell you
nothing about the hum, because they are fauna, not instrumentation (owner
ruling, verbatim on the item).

**Donor, MEASURED 2026-09-11 (dnfile metadata enumeration of
`Ling_Cockroach.dll`, 12 KB, both copies identical; defs and patch read from
the live workshop folder `3196253802`):**

- The DLL holds exactly four working types — `ThinkNode_EatWastepack`
  (+`JobDriver_EatWastepack`, `Toils_FenXi` helper): tamed roaches seek and
  consume wastepacks (TypeRefs include `PollutionUtility`);
  `Hediff_DeadBombToQiaoKeli`: a death-triggered hediff
  (`Notify_PawnDied`, `GenExplosion`, `GasType` refs) behind the donor's
  `ToxInBody` HediffDef; `Verb_JumpToFace`: a jump verb behind the mech's
  `Gun_JumpToFace` turret. **No Harmony, no game-wide hooks** — every class
  binds only where a def references it (think tree node, JobDef
  `driverClass`, HediffDef `hediffClass`, `verbClass`). An XML-clone reskin
  is therefore SAFE: our defs simply don't reference what we don't want,
  and no donor behaviour leaks in by itself.
- Donor defs measured: organic `Ling_Cockroach` (bodySize 2, healthScale 3,
  armor 0.65/0.75, `CompProperties_Milkable` → **Chocolate**, constant think
  tree `AnimalConstantEatWastepack` gated `ThinkNode_ConditionalOfPlayerFaction`
  — wastepack-eating is a *tamed* behavior in the donor); mech
  `Ling_Cockroach_Mechanoid` (BaseMechanoidWalker, combatPower 400, armor
  0.8/0.8, `CompProperties_TurretGun` → `Gun_JumpToFace`, custom BodyDef
  `Scorcher_SixLeg`). `Patches/Core.xml` does exactly one thing: adds the
  donor to `ResurrectMediumMech`'s ingredient filter — donor-scoped,
  irrelevant to clones.
- Labels are Chinese throughout — moot: we ship clones with our own text.

**Reskin plan (clone, never patch-in-place — the Scarlands kit's ruled
donor-retirement pattern):**

- **`RUT_ScarRoach`** (organic, Scarlands roster) and **`RUT_CathedralRoach`**
  (synthetic, Cathedral roster). Both **bodySize ~0.25** — and per the
  ceiling-fields lesson the item itself cites, melee/health/armor are tuned
  *separately, deliberately*: the synthetic keeps high armor (0.8/0.8-class)
  and healthScale at a fraction of the size — "strangely tough and powerful"
  for free, exactly as the item predicts.
- **Cleaners, not vermin:** new **`RM_ThinkNode_EatCleanable`** (S) —
  generalizes the donor's measured node to *wild* pawns (drop the
  player-faction gate) and to filth as well as wastepacks; data-driven
  target list via DefModExtension. The Cathedral's closed ecology becomes
  mechanical fact: eels clean the canals, roaches clean the land.
- **Dropped donor content:** chocolate milking, the `ToxInBody` death-bomb,
  the jump-to-face turret — none referenced by our clones. (Death-bomb ❓
  reconsider only if the owner wants the synthetic to sting when killed —
  not specced, not built.)
- ⛔ **No hum wiring, either direction** (owner, 2026-09-07, on the item):
  no attitude input, no freeze/scatter tell. Enforced structurally: the
  roach think trees never reference `RM_MapComponent_BiomeAttitude`.
- **Salability — DECIDED (the item asks this kit to decide):** roach parts
  join the salable list — the organic butchers normally; the synthetic
  breaks down to a small `RUT_CathedralRoach`-shell trade good — but they
  are **NOT watched**: no irritation, no goodwill price on hunting them.
  Rationale: "leave the roaches out of the hum mechanics for now" excludes
  inputs as much as displays; a watched harvest is a hum input by the back
  door. Reversible on the owner's word, like the ruling it follows.

**Reuse:** donor DLL retired from our path entirely; `RM_ThinkNode_EatCleanable`
is the one new class, RM_ tier (generic vermin-cleaner mechanism — plausible
future `SHIP_VERMIN_MOD_1` neighbor).

**INVENTED parameters:** bodySize 0.25/0.22; synthetic healthScale 1.6, armor
0.75/0.75; organic wildness high, no taming hook v1; clean interval — one
filth/wastepack per 2h active.

**v1:** two clone races + cleaner node + rosters (rides the existing roster
JSON's owner flag). **Deferred:** taming/pet register (owner's call),
synthetic-roach death sting, art (rides the art pipe; donor textures are
donor-licensed — clones need their own sprites).

**Effort: S/M** (cleaner node S; defs XML; art is the long pole and not this
kit's).

---

## Build order

1. **Wall ladder defs** (§2) — zero C#, proves the biome's economic floor on
   a quicktest map immediately.
2. **`RM_MapComponent_BiomeAttitude` + hum layers** (§1) — everything else
   plugs into it; provable with dev-mode irritation pokes and audible bands.
3. **Eel + fishing consequences** (§4) — mostly XML on §1; exercises the
   ledger coupling end to end.
4. **Living bolts** (§3) — the dance giver, once §1 gives it a band to read.
5. **Deep-drill response** (§5) — reuses the Scarlands lord; needs §2's
   tier-4 resource in place.
6. **Roaches** (§6) — independent of §1 by design; parallelizable any time
   after the cleaner node lands.

Verification per step: quicktest map + bridge (`rimworld-debug-testing`),
never a cold load; §5 gets one live drill-response run before force sizes are
tuned; §4's MaxFishPopulation ❓ is checked before any fishing claim is made.

## Cards for the owner

- **NONE outstanding as contradictions** — no mechanic above required
  breaking a frozen ruling; the −75/0 hysteresis turned out to be vanilla.
- Decisions taken inside the spec's granted authority, flagged for visibility:
  roach parts **salable but unwatched** (§6, rationale there);
  deep-drill response implemented as **converge-destroy-withdraw** movement
  (§5) — reads §5's "massive mechanoid movement" without breaching ban 3.
  Either is one word from the owner to reverse.
