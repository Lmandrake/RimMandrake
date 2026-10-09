# Beskar armorer quest: three designs (2026-10-09)

Item: `BESKAR_ARMORER_QUEST_1`. Parent: `CANON_MATERIALS_BUILD_1` (its L7). Design only; no defs.

## 0. The ruling and the givens

Owner, typed 2026-10-09: *"(1) and a quest with Blackstar allows you to access that rare individual,
otherwise you just use the pieces you find. Never can reforge yourself, smelting destroys it (converts into
other lesser ores), only the rare location can properly reforge."* He chose by card to have the design drafted
now.

Fixed by that ruling, and the same in all three designs:

- Beskar pieces are salvage. The colony wears and wields them as found.
- No colony recipe makes beskar. `kotor_IngotBeskar_recipe` goes, and beskar mining routes yield nothing
  (`canon_materials_design_2026-10-09.md` §3.7, built under `CANON_MATERIALS_BUILD_1` L7).
- Smelting beskar, or anything made of it, destroys it and yields lesser material. Each design below proposes
  a yield; §7 compares them.
- Reforging happens in one place, at the hands of one person, reached through Blackstar.

What the designs differ on: how Blackstar leads you there, what and where "the rare location" is, what the
reforge costs and how long it takes, and what smelting returns.

## 1. What Blackstar is in this project

**The Blackstar Company is a faction: one mercenary outfit of contract hunters, built as a reskin of vanilla
`Pirate`.**

- Spec: `design/Jawa/worldbuilding/FACTION_SPEC.md` entry 10. Built: `src/RimUtinni/UtinniPatches/Patches/BlackstarCompany.xml`
  (label, description, the `Contract` ideoligion), `Defs/RulePackDefs/Namer_BlackstarCompany.xml`, and the
  pawn kinds `Jawa_Blackstar_Grunt · _Heavy · _Leader · _Specialist` in `Defs/PawnKindDefs/JawaFactionRoster.xml`.
- **`permanentEnemy true`, kept on purpose** (ruling R12), so the vanilla raid economy is not gutted. Every
  design below has to route around that: Blackstar cannot be an ordinary friendly quest asker.
- **Fiction:** *"one dangerous person with a name who is coming for you"*; professionals under a code; they
  take contracts and do not pillage. Ideoligion `the Contract`: *"a contract completed is sacred; a contract
  broken is unclean"*; hostile **when someone paid them, never otherwise** (`faction_religions.md` §10).
  No money ransom; honoured prisoner exchanges; **freeing a Named Hunter is the only lever on a permanent
  enemy** (`reconciled_lore/04_factions.md` §10, `09_arcs_dungeons_quests.md`: "the Blackstar truce token").
- **The Mandalorians are inside it.** Its leader is **Captain Jaxen Marr, a Mandalorian**
  (`faction_world_spec.md` rows 79 and 127); its Heavy pawn kind is "Mandalorian, beskar-pattern plate"
  (`pawnkind_roster.md` §10); the Creed is the faction's one sacred thing (`faction_religions.md` §10).
  That is the canon-shaped reason Blackstar knows where an armorer is.
- **On the planet:** 4 settlements at road junctions and ruins (`ASHKARR_WORLD_DEFINITION.md` line 586).
- **Named cast:** `design/Jawa/bridge/INHABITED_CAST_BLACKSTAR.md`: the Signing House, the boarding crew of
  the ship *Countersign*, and the Claims Office, which pays the Company's victims as a liability.
- Raid weight is Heat-scaled (`faction_roster_v2.md`): quiet until the player gets "hot".

## 2. Canon: beskar and the Armorer

Pulled from Wookieepedia's parse API 2026-10-09 (pages `The_Armorer`, `Beskar`, `Mandalorian_covert`):

- The Armorer forged armour and weapons for her Tribe **in a hidden covert**: first under Nevarro, then, after
  the Nevarro covert was exposed and massacred, a new covert on **Glavis Ringworld**, in space, whose cryo-furnace
  sat "next to a service corridor open to the vacuum of space".
- Tools: "a cryo-furnace, magnetic tongs, and a gravity hammer"; "the Mandalorian method for forging beskar was
  a closely guarded secret" (also cited in `canon_metal_fabrication_2026-10-09.md`).
- **Reforging salvage is canon, for a Mandalorian smith.** Din Djarin brought Imperial-stamped beskar from a
  bounty; she identified it as Purge spoils, forged him a pauldron, and he **"gave the excess to the Armorer for
  future foundlings"**. A tithe is canon.
- She melted Ahsoka's beskar spear because it was dangerous, and **reforged it into armour for Grogu at Djarin's
  request**: the customer chooses what the metal becomes.
- "The metal could also be reforged to any warrior's liking."
- She identifies signets and declares clans: the covert is a society, not a shop.
- Jawas handling beskar as salvage is canon (*The Mandalorian* Chapter 9, Boba Fett's armour).

## 3. What already exists that this reuses

Checked 2026-10-09: nothing in `src/` is a Mandalorian armorer quest, pawn, site or forge. What is reusable:

| piece | where | used by |
|---|---|---|
| Blackstar faction, pawn kinds, namer, ideo | `src/RimUtinni/UtinniPatches/` | all |
| `NAMED_HUNTER` role: Harmony seams on `GenGuest.PrisonerRelease` and `Pawn_GuestTracker.CapturedBy` for Blackstar pawns | `src/RimMandrake/RaidRedesigner/Source/Patch_PrisonerReleasedOrNamedHunter.cs`, `RoleTag.cs` | B (the trigger), A (optional) |
| Quest lodger in the player faction (`joinPlayer`), the shape that lets a visiting pawn be worked with | `src/RimUtinni/DroidRepairJobs/Defs/QuestScriptDefs/Quest_DroidRepairJob.xml` | B |
| Faction-specific settlement picker in C# (`RM_QuestNode_GetWildsteamSettlement`) | `src/RimUtinni/WildsteamEggBounty/Source/` | A, C |
| Trade-request delivery (`QuestNode_TradeRequest_Initiate`) | `RUT_WildsteamEggBounty.xml`, `RUT_FungalSoilTradeRequest.xml` | A (paying the contract in goods) |
| Site quests with a spawned map and a timeout | `src/RimUtinni/StructureInjectionsRUT/Defs/VaultDungeons/QuestScriptDefs/RUT_VaultThaw.xml`, `RUT_KraytDenQuest.xml` | A, C |
| Named persistent residents of a place (PLACE / CAST / ROUTE / FATE) and `SettlementManifestDefs` | `src/RimMandrake/Inhabited`, `src/RimUtinni/AshkarrInhabited/Defs/SettlementManifestDefs/` | A, C (the covert's cast) |
| Gravship to a planet layer; a layer of our own (`RM_SeabedLayer`) | built, `2db33bf23` | C |
| Odyssey orbital-site quest roots: `QuestNode_Root_Gravcore_OrbitalAncientPlatform`, `QuestNode_RequirementsToAcceptPlanetLayer` | decompiled 1.6 (RimSage, 2026-10-09; class names only, fields not yet read) | C |
| Beskar as stuff (`KOTOR_IngotBeskar` has `stuffProps`) and the Outer Rim beskar items | Armoury (ours), Outer Rim | all: reforge output is gear made *of* beskar stuff |

**What none of this covers, in every design:** the reforge itself. "Only she can do it" is a new verb, so it
needs a small C# piece (rimworld-quests §9). Cheapest form: an **Armorer's forge** workbench whose beskar
recipes accept a bill only from a pawn carrying an `RM_ArmorerOfTheTribe` marker (hediff or trait), plus a
`RecipeWorker` that converts the beskar *mass* of the ingredients into the chosen item. The vanilla bill UI
then is the reforge menu. (UNVERIFIED which seam gates a bill per pawn; read `WorkGiver_DoBill` before
building.)

## 4. Design A — The Contract (caravan to a hidden covert)

**The question it answers: what if Blackstar is an employer, and the covert is a place on the planet you
walk to?**

**How Blackstar leads you there.** Blackstar takes contracts, and the Contract says anyone not named walks away
untouched, so a deal with them is in character even though they stay `permanentEnemy`. Once the colony holds
any beskar piece, a letter arrives from Captain Jaxen Marr: a Blackstar contract (one name, one price, one
ending) that the Company would rather sub-let to a Jawa clan. The ask is one of: capture a named mark alive and
hold him for pickup, or deliver a specific salvage item. Fulfilled, the Company pays in **the covert's
location**, because Marr's Creed forbids paying it in beskar.
- Quest shape: `QuestNode_Sequence` → the asker is a generated Blackstar pawn (`QuestNode_GeneratePawn`, faction
  `Pirate`), not a settlement, so `permanentEnemy` never blocks it → the mark arrives as a quest pawn
  (vanilla `Util_Raid`-style arrival or a site) → `mark.Captured` / delivery `TradeRequest` → reward:
  `QuestNode_GenerateWorldObject` + `QuestNode_SpawnWorldObjects` of the covert site.
- Failure: the mark dies (`mark.Destroyed`) or the timer runs out. No goodwill change (they are already
  enemies); instead the next Blackstar hunt is Heat-scaled up. The quest can be offered again later.

**The rare location.** A **hidden covert on a surface tile**, as a permanent world object: a ruin under a
Blackstar settlement's road junction, two or three tiles from it. Inhabited supplies its cast: the Armorer and
two sworn guards, persistent pawns. Reached **by caravan**. It appears only after the contract; before that,
nothing on the map shows it.

**The reforge.** The caravan carries beskar in and enters the covert map. At the Armorer's forge you place
bills (the vanilla bill UI on her workbench); she works them while the caravan waits on the map. Output: any
apparel or weapon that takes beskar as stuff, using the **same beskar mass, minus a tithe of 1 in 5 kept "for
the foundlings"** (canon). Time: her work speed on a cryo-furnace, about **one day per armour piece**. A visit
can reforge everything you carried; you may return any number of times.

**Smelting beskar yourself:** steel and steel slag (`Steel` + `ChunkSlagSteel`), about a third of the mass
as steel.

**Cost to build:** one quest def, one world-object/site def with a fixed map layout (StructureInjections
pattern), one Inhabited cast, the forge workbench and its C# gate. **Risk:** caravans across Ash'karr are long;
the covert must be placed near a Blackstar settlement on the frozen map, which touches the world-paint pass
(`BIOME_PAINT_ONCE_AT_THE_END_1`), or be spawned by the quest at a free tile near one.

## 5. Design B — The Truce Token (the Armorer comes to you)

**The question it answers: what if the lever is the one the lore already names, freeing a Named Hunter, and
the "rare location" is a person who travels?**

**How Blackstar leads you there.** The lore's own mechanism: *freeing a Named Hunter is the only lever on a
permanent enemy*. When the colony **captures a Blackstar Mandalorian** (the Heavy pawn kind, beskar-pattern
plate) and **releases him unharmed**, the RaidRedesigner `NAMED_HUNTER` seam already fires. That release starts
the quest: the hunter owes a debt under the Contract, and he pays it the only way his Creed allows. He tells the
Armorer that this clan keeps beskar honourably.
- Quest shape: fired from C# on the release seam (route: `isRootSpecial`, weight 0, started by the existing
  Harmony patch), then a `QuestNode_Delay` of 10–20 days, then the visit.
- The choice: keep the Mandalorian as a prisoner (recruit him, take his plate) or free him and get the
  Armorer. His plate counts as found beskar either way; that is the trade.

**The rare location.** The Armorer **comes to the colony**, set down by Blackstar's ship *Countersign*
(shuttle arrival), with one sworn guard. She is a **quest lodger in the player faction**, the
`Quest_DroidRepairJob` shape, so she can work bills. She raises a portable cryo-forge (quest-spawned
building, removed when she leaves). She stays **5 days**, then leaves. "The rare location" is wherever she
stands.

**The reforge.** During the stay, you queue bills at her forge with whatever beskar you hold. Same-mass
output minus the 1-in-5 tithe. Time: whatever she finishes in 5 days (about 4–6 pieces). If she is harmed,
arrested or killed: the quest fails, the guard turns hostile, and every Blackstar faction pawn gets a
"broke the Contract" hunt against you (Heat to maximum). She returns each time **another** Named Hunter is
freed, so the service is repeatable but paid for in prisoners.

**Smelting beskar yourself:** steel plus durasteel slag (`KotORChunk_durasteel`, which the materials design
keeps re-meltable to durasteel), so a smelted beskar pauldron becomes "lesser ore" that is still a canon
metal.

**Cost to build:** the least. No site, no map, no world object. One quest def on an existing seam, the lodger
pattern already built, the forge workbench and gate. **Risk:** a visitor on your own map is less "rare place"
than the owner's words suggest; and it depends on the player taking a Mandalorian alive.

## 6. Design C — The Sworn Price (gravship to an orbital covert)

**The question it answers: what if the covert is canon's Glavis-style forge in space, and the price is a
person rather than goods?**

**How Blackstar leads you there.** Blackstar sells nothing to outsiders, but Captain Marr will **ransom the
coordinates for a Mandalorian foundling**: the colony must give one colonist to the Creed. The quest offers it
when the colony owns a gravship and holds beskar: Marr sends terms. Accept, and one colonist of your choice
swears the Creed.
- The sworn colonist stays yours but carries a permanent `RM_SwornOfTheCreed` state: never removes a helmet
  (a forced-apparel rule), a mood penalty if the clan breaks a contract, and they will not fight Blackstar
  Mandalorians. In exchange they are the only pawn the Armorer reforges for at full yield.
- Quest shape: `QuestNode_Sequence` with a pawn picked from the colony (the vanilla "choose a pawn"
  pattern is UNVERIFIED; read the shipped `Script_` defs before committing to it); reward: the covert site
  on the **orbit layer**, gated by `QuestNode_RequirementsToAcceptPlanetLayer`.

**The rare location.** An **orbital covert**: a derelict platform in the orbit layer with a cryo-furnace beside
a vacuum-open corridor, as canon has it. Reached **only by gravship**, the way the seabed is. Built on Odyssey's
orbital-platform site roots. The Armorer and a few sworn live there (Inhabited cast). A visit is one landing.

**The reforge.** Land, carry beskar off the ship, place bills. **One reforge per visit, for the sworn
colonist's gear at full mass; anyone else's gear at half mass** (the rest is tithe). Time: one day per piece,
while the gravship sits docked; gravship fuel is the travel cost. Repeatable for the rest of the game.

**Smelting beskar yourself:** nothing useful. Beskar comes out as steel slag only (`ChunkSlagSteel`), so it is
pointedly worse than either other design: the material is sacred and you destroyed it.

**Cost to build:** the most. An orbital site with a layout, an Odyssey quest root whose fields are not yet read,
the sworn-colonist state (apparel rule and thought defs, and C# for "will not fight"), the forge and gate.
**Risk:** the gravship is the late game, so for most of a run beskar cannot be reforged at all.

## 7. Side by side

| | A — The Contract | B — The Truce Token | C — The Sworn Price |
|---|---|---|---|
| Blackstar's role | employer: you do a contract | debtor: you free a Mandalorian hunter | broker: you give a colonist to the Creed |
| what it costs you | a job (capture a mark or deliver an item) | a captured Mandalorian and his plate | one colonist bound by the Creed, plus gravship fuel |
| the rare location | hidden covert on a surface tile | the Armorer herself, visiting by shuttle | orbital covert in the orbit layer |
| how you reach it | caravan | she comes to you | gravship only |
| reforge | any beskar gear, same mass less 1/5, ~1 day a piece, as often as you visit | same, but only during a 5-day stay | full mass for the sworn colonist, half for anyone else |
| repeatable | yes, revisit freely | once per freed hunter | yes, each landing |
| smelting yields | steel + steel slag (~1/3 mass) | steel + durasteel slag | steel slag only |
| when in a run | early-mid | whenever Blackstar raids | late (needs a gravship) |
| build size | medium: site, cast, quest, forge | small: quest on an existing seam, lodger, forge | large: orbital site, Odyssey root, sworn state, forge |
| fits "rare location" literally | yes | weakest | yes, strongest |

## 8. Recommendation

**Design A, with B's trigger available as a second way in.** A matches the owner's words most literally
("the rare location" is a place, and Blackstar's quest is what grants access), fits the faction's identity
(it takes contracts and does not pillage), and puts the reforge in reach mid-game, when beskar finds are
most common. Releasing a Named Hunter (B's mechanism, already wired in RaidRedesigner) can **also** reveal the
covert, so a player who never takes the contract still has a route. Keep C's orbital covert as a later
upgrade if the owner wants the canon Glavis staging; it costs too much to be the only route.

Smelting yield for A: steel plus steel slag. It reads as "lesser ore" and keeps beskar out of every colony
recipe chain.

## 9. Owner questions

1. Which design? (A contract + caravan covert / B freed hunter + visiting Armorer / C sworn colonist + orbital covert / A with B's trigger as a second way in)
2. What does Blackstar's quest ask of you? (capture a named mark / deliver a salvage item / free a Mandalorian prisoner / give a colonist to the Creed)
3. Where is the Armorer? (a covert on the surface / she visits your colony / an orbital covert by gravship)
4. What does a reforge return? (same beskar mass as gear of your choice, less a 1-in-5 tithe / same mass, no tithe / a fixed menu of Mandalorian pieces)
5. How often? (any number of visits / once per game / once per Blackstar quest)
6. What does smelting beskar yield? (steel + steel slag / steel + durasteel slag / slag only)
7. If the Armorer is harmed? (quest fails and Blackstar hunts you at max Heat / quest fails, nothing else / the covert is lost for good)

