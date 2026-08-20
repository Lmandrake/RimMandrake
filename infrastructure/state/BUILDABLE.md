# BUILDABLE.md — what the stack can and cannot give us

> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


BUILD publishes here. **One line per fact**, written when a limit or a capability is
learned that DECIDE would otherwise have to ask about: what a def type supports, what
a mod already gives us, what the engine refuses.

**Replace a superseded line. Never append a correction under it** — a stale line above
its own correction still gets read first.

Every line carries the date and how it was measured. A fact with no measurement behind
it does not belong here.

---

## What the stack already gives us

- **Lightsabers are LIVE and plentiful — 14 `ThingDef`s.** `Force_Lightsaber_Custom`
  (plain), `_Dual`, `_Curved`, `_Crossguard`, `_Shoto`, `_Inquisitor`,
  `_BuildYourOwn`, `_UniqueObi`, `_UniqueAnakin`, `Force_Ezra_BlasterLightsaber`,
  plus throw/whip/projectile defs. Mod `lee.theforce.lightsaber`, active.
  *Measured 2026-08-15 against the def dump refreshed at that load.* ⚠️ Absence from
  a screenshot is not absence from the build — that inference nearly became a
  "missing weapon" item.
- **All 8 authored Jawa `FactionDef`s load.** `Jawa_IndigenousTribes` (label "Jawa
  Trade Moot"), `Jawa_HuttCartel`, `Jawa_Junkers`, `Jawa_DeepwaterCompact`,
  `Jawa_GeonosianFoundryHive`, `Jawa_WildsteamClan`, `Jawa_AscendantHelix`,
  `Jawa_FreeDroidEnclaves`. *Live via `jawa/get_def`, 8/8, 2026-08-15.*

## What the engine refuses, and what that costs

- **Only `Jawa_IndigenousTribes` carries `requiredCountAtGameStart`.** The other
  seven are `canMakeRandomly` with no required count, so they default to **0** at the
  Configure Factions screen and a world generated without hand-ticking them contains
  none of them. **Worldgen happens once.** *Measured on disk 2026-08-15; filed as
  `seven-factions-have-no-required-count-9c4e17`.*
- **A `PatchOperationFindMod` that FAILS proves the mod is PRESENT.** An absent mod
  returns **true** and logs nothing, so the failure can only mean an inner op broke.
  `<mods>` matches the About.xml `<name>`; `<activeMods>` lists the `packageId`.
  *2026-08-15, cost one wrong diagnosis and two seats' time.*
- **Patches run on RAW XML, before `ParentName` inheritance.** A def that only
  *inherits* a container has no such node to patch, so an add-if-missing `<nomatch>`
  aimed at that container fails — and `PatchOperationSequence` stops at the first
  failure, silently killing every op after it. **Any generator that decides what to
  patch by reading a RESOLVED def dump will emit this bug.** *2026-08-15.*
- **Nothing on the 155-tool bridge can order an attack.** `jawa/order_pawn` issues a
  GOTO even with a `targetId`; drafted pawns hold at `Wait_Combat`; spawned hostiles
  have no lord and idle. Blocks every combat test. *2026-08-15,
  `bridge-cannot-order-a-melee-attack-3f8c21`.*

- 🔴 **A `ThingOwner<Pawn>` on a custom `WorldObject` IS TICKED, and copying `Caravan`
  literally would delete the cast.** Two shipped mechanisms bite, and neither is
  documented anywhere: (1) `WorldObject.DoTick` walks its child holders and calls
  `ThingOwner.DoTick` on each, skipping only owners that are `is Map` or `is Caravan`
  — a hardcoded type test a mod cannot join, so an off-map roster's needs fall and it
  starves in a box. The supported opt-out is `IThingHolderTickable` with
  `ShouldTickContents => false`. (2) `Caravan.pawns` uses `LookMode.Reference` and is
  safe only because caravan pawns are registered with `WorldPawns` AND
  `WorldPawnGC.GetCriticalPawnReason` carries an explicit `p.IsCaravanMember()` test;
  a custom holder matches none of that method's tests, so every pawn would be
  collected between visits. Use `LookMode.Deep` and keep them out of `WorldPawns`.
  *Read off the 1.6 decompile 2026-08-20 — `RimWorld.Planet/WorldObject.cs` DoTick,
  `RimWorld.Planet/WorldPawnGC.cs` GetCriticalPawnReason — while building `Inhabited`.*
- **The last moment a departing map's pawns are still enumerable is a prefix on
  `Verse.Game.DeinitAndRemoveMap`.** It runs `Notify_MyMapAboutToBeRemoved()`, then
  `MapDeiniter.Deinit`, whose FIRST act is `PassPawnsToWorld` — which despawns every
  pawn and hands it to `WorldPawns`. `MapComponentUtility.MapRemoved` fires after
  that and is too late to recover anybody. *1.6 decompile, 2026-08-20.*
- **`Lord.ExposeData_StateGraph` saves the current toil and each toil's data by
  POSITIONAL INDEX**, then re-runs `CreateGraph()` on load and looks those indices up
  in the freshly built graph. Any `LordJob` we intend to re-tune must therefore return
  a graph of exactly one toil, forever, and put the schedule in ordinary C# inside it.
  *`Verse.AI.Group/Lord.cs`, 1.6 decompile, 2026-08-20.*

- 🔴 **`requiredCountAtGameStart` is a WORLDGEN-ONLY field. There is NO load-time top-up.**
  It is read in exactly one place — `FactionGenerator.InitializeFactions`, reached only
  from `WorldGenStep_Factions`. The only load-time faction top-up is
  `BackCompatibility.cs`, and it is a **hardcoded list of five**: `Empire`, `HoraxCult`,
  `Entities`, `TradersGuild`, `Salvagers`. ⇒ **A faction absent when the world was
  generated can NEVER appear by patching a def afterwards** — it must be created by hand
  or the world regenerated. This is the owner's *"absent when he builds it is absent
  forever"* wearing its mechanism. *1.6 decompile, 2026-08-20. It corrects a claim that
  was written into `RebelAlliance_Suppress.xml` and `Jawa_Patches/About/About.xml`; both
  are fixed.*
- 🔴 **`replacesFaction` SILENTLY DELETES a faction from worldgen, and it is another mod's
  field.** `InitializeFactions` skips def X entirely when ANY def Y has
  `requiredCountAtGameStart > 0 && Y.replacesFaction == X`. **Biotech's `PirateWaster`
  replaces vanilla `Pirate`** — the def our `BlackstarCompany.xml` reskins — so the
  Blackstar Company can never be generated while Biotech is active, no matter what weight
  or count we patch onto it. **Before reskinning ANY vanilla faction, check what replaces
  it:** six defs in this 578-mod build declare `replacesFaction`, three of them aimed at
  `OutlanderRough`. *1.6 decompile + the 578 def dump, 2026-08-20.*
- **A faction's NAME is not its def's label.** `Faction.Name` returns a stored name if one
  was generated and only falls back to `def.LabelCap` when that is null, so patching
  `label` after worldgen changes nothing the player sees. `fixedName` on the def prevents
  the generated name in the first place; `jawa/faction_name_set action=clear` repairs a
  world that already has one. *Measured live 2026-08-20: ten of eleven campaign factions
  were wearing generated names.*

- 🔴 **`weaponMoney` is a CEILING rolled ONCE, and `min` is what decides whether a kind
  arms RELIABLY.** `PawnWeaponGenerator.TryGenerateWeaponFor` rolls
  `weaponMoney.RandomInRange`, keeps every weapon priced **at or below** that roll, and if
  the pool comes back empty **the pawn spawns bare, silently**. ⇒ `max >= cheapest` means
  the kind *can* arm; **`min >= cheapest` is what makes it always arm.** A `min` below the
  cheapest tagged weapon leaves a band of rolls that arm nobody — this project's own notes
  had it backwards twice. Check with
  `python3 src/RimMandrake/Utils/weapon_affordability.py`. *1.6 decompile + the 578 dump,
  2026-08-20.*
- 🔴 **A weapon with no `MarketValue` statBase is not cheap — it is COMPUTED, and the def
  dump cannot show you the number.** `StatWorker_MarketValue` falls through to
  `CalculatedBaseMarketValue`, which prices the thing from its recipe:
  `Σ(costList.count × ingredient.BaseMarketValue)` plus `WorkToMake × 0.0036`, over the
  product count. **Every Outer Rim weapon is in this state** — they declare MaxHitPoints,
  Flammability, DeteriorationRate and Beauty and nothing else — so "read the value off the
  def" returns nothing and treating a missing number as 0 makes an empty pool look like the
  cheapest one. `OuterRim_DroidWeapon_BlasterCannon` computes to **982.5**.
  `weapon_affordability.py` reproduces the formula. *2026-08-20.*

## Deploy targets that are not `Mods/`

- **`Xenotypes/*.xtp` and `Ideos/*.rid` are deploy targets.** They live under
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`,
  nothing syncs them from the repo, and `deploy_custom_mods.py` does not cover them.
  A `.xtp` **bakes at world creation** and a stale one drops renamed genes **silently
  in play**. *2026-08-15: `MandrakeJawa.xtp` had been correct in the repo since
  `c57f347` and stale in the game for a day, dropping four genes.*
- **An offline validator cannot catch a stale `.xtp`.** It validates the file you
  point it at; the game reads a different copy. Check the deployed one.
- 🔴 **An offline validator answers "is this file self-consistent", never "is the file
  the game reads correct".** `validate_save_artifact.py` returned **36/36 resolve** on
  `MandrakeJawa.xtp` twice — once on a file the running engine was contradicting, once
  on a freshly deployed one it had not yet read. Same output, opposite meanings. A
  deploy is **FIX DEPLOYED, UNVERIFIED** until a startup log shows zero
  `Could not load reference to`. *2026-08-15.*
