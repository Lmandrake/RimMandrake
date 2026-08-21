<!-- status: live -->
# CHERRYPICK_AGENDA.md — everything we review together, and in what order

DECIDE owns this. Chain step 1. It is the running agenda for the interactive
cherrypick sessions; tick a row when its pass is finished.

**The mechanism already exists.** Cherry Picker is live at load order 11 with 24
entries, and **every entry is reversible by editing one file**. Nothing here is
destructive, so we can be decisive and correct later.

## 🔴 The principle — owner, 2026-08-15

> *"We're doing a trimming pass right now to get rid of things we KNOW we won't
> need. Easy cuts, obvious cuts, so that we're working with smaller item sets and
> closing in on a playable game. But it still needs human verification."*

⇒ **Obvious cuts only, and every batch is verified by the owner.** The point is to
shrink the working set before the hard passes (weapons, armour), not to make fine
judgements now.

⛔ **A rejected principle, recorded so it is not re-proposed:** *"we cut the
faction, so cut its gear too."* **Wrong.** The owner: *"we often accept silly
races in order to get the gear from their mod. That's a bad assumption. We can
always rename things."* Fiction of a race or faction says nothing about whether
its gear is wanted.

## 🔴 ITEMS are the unit. Mods are a CONSEQUENCE.

**Owner, 2026-08-15:** *"Don't offer me mods. We will decide on mods AFTER seeing
if we get rid of everything from a mod, reducing its value too far."*

⇒ **Never propose a whole-mod removal as a cherrypick decision.** Cut items. Then,
once a mod has lost most of what we wanted from it, ask whether it still earns its
slot — that is a separate, later question with its own risks (`ModsConfig`, a
game-down window, cross-reference errors).

## The three kinds of row

Not every category can be reviewed the same way. The honest split:

| kind | meaning |
|---|---|
| **PASS** | we go through it together and rule. It is small enough to be real. |
| **TARGETED** | far too large to review. No pass — we cut named things on sight, in play or when one offends. |
| **DERIVED** | not reviewed at all; it follows from a decision made elsewhere. |

## Done — do not re-open

| ✔ | category | how it was settled |
|---|---|---|
| ✅ | **Factions** | 21 untick / 6 keep, ratified, plus our own 13. Spent at the world screen |
| ✅ | **Biomes** | 29 removals + 4 keeps, via `PlanetTypeDef.biomeBlacklist`, not Cherry Picker |
| ✅ | **Anomaly content** | your 9 creature/object picks + 2 genes — the live 24 keys |
| ✅ | **Mod list** | **575** frozen 2026-08-15, two files, `deployed/config/v1_freeze/` (was 585; 585 − 11 + 1 = 575, reconciled in `V1_CHAIN.md`). ⚠️ Both counts are as of 2026-08-15; the LIVE list is 578 activeMods as of 2026-08-20 (`infrastructure/state/canon.yml` `modlist`) — a frozen count and a live count are different facts, do not reconcile them |

## PASS — the real work, in the order I recommend

| ✔ | # | category | size | the unit we decide in | why this order |
|---|---|---|---|---|---|
| ✅ | 1 | **Conventional firearms** | 74 cut | by item | AKs, Makarovs, service rifles, vanilla Core's 11 |
| ✅ | — | **The mechanitor system** | 33 cut | by item | Player mech control. Ancient variants KEPT as ruins scenery |
| ✅ | — | **Contemporary clothing + ruins apparel** | 34 cut | by item | Hoodies, jeans, lab coats; bulletproof masks and flak suits |
| ☐ | 1b | **Creatures that spawn on our biomes** | ~2,387 total | by item | Fiction-visible on the map. The next round |
| ☐ | 2 | **Weapons** | **845** | by mod first (60), then by tier | The hardest and the most load-bearing — pawn types cannot be equipped until it lands |
| ☐ | 3 | **Armour / apparel** | **886** | by mod, then by layer | No list exists at all today. Same blocker as weapons |
| ☐ | 4 | **Creatures / beasts** | **2,387** | by mod and by theme | Fiction-visible on the map. Your dinosaur review sits here |
| ☐ | 5 | **Mechs** | 80 | one sheet, name + role | Art on disk for 55; the other 25 need photographing first |
| ☐ | 6 | **Drugs & medicine** | subset of 4,393 | by class | Small real subset; most ingestibles are meals and raw food |
| ☐ | 7 | **Incidents & quests** | 358 / 243 | by name | Fiction-breakers arrive as events. Cheap to scan, high visibility |
| ☐ | 8 | **Traits** | 268 | one sheet | Stat-multiplier creep is the known risk here |
| ☐ | 9 | **Ideology styles** | 1,615 | by category | Low priority, but they decide what buildings LOOK like |

## TARGETED — no pass, ever. Cut on sight.

Reviewing these per-def is not possible and pretending otherwise wastes sessions.

| category | count | how it gets handled |
|---|---|---|
| **Buildings / furniture** | **8,742** | Cut only when one offends. `designationCategory` clearing hides a whole mod's menu cheaply |
| **Genes** | **4,833** | DERIVED — follows the xenotype decision |
| **Food & meals** | most of 4,393 | Only the fiction-breakers; nobody audits a meal list |
| **Recipes** | 2,951 | DERIVED from whatever items survive |
| **Hediffs** | 2,754 | DERIVED |
| **Terrain** | 1,240 | Handled by biome work, already done |

## DERIVED — decided elsewhere

| category | where it is decided |
|---|---|
| **Xenotypes / races** | 🔴 **Not a cherrypick.** Owner's ruling: build our OWN set as an amalgam of what exists, for total control. See `D23` |
| **Pawn kinds** | Follows weapons + apparel; that is chain step 3 |
| **Research** | Follows whatever items survive |

## How the sessions run

- I bring a **cluster** with the principle stated first, so you can agree with the
  principle rather than adjudicate every line.
- Default batch is **8–12 decisions**. Say *"smaller groups"* or *"bigger groups"*
  and I recalibrate.
- A principle you accept once is applied to everything it covers, and I list what
  it swept so you can spot-check rather than re-read.
- Anything you are unsure about goes to a **hold** list rather than a guess.

## Descoped — gone, not a cherrypick target

| mod | why |
|---|---|
| **`Vanilla Animals Expanded`** (`VanillaExpanded.VanillaAnimalsExpanded`) | Owner, 2026-08-15. 50 of its 51 animals cut in review; audited for non-animal content and there is none. Its 19 other ThingDefs are its own eggs, leathers, wool and the beaver dam; its sounds, bodies, damage types and maneuvers all serve `AEXP_` animals; its six patches touch only `AEXP_` defs plus biome and trader lists it adds itself to. The gila monster was the sole survivor and goes with it. No mod declares a dependency |
| **`Giant Snake (Continued)`** (`zal.giantsnake`) | Owner, 2026-08-15. Both its animals cut in review; nothing else in the mod. No mod declares a dependency |
| **`ReGrowth: Boiling`** (`regrowth.botr.boilingforest`) | Owner, 2026-08-15. The `RG_BoilingForest` biome was cut in the biome review, and the parts worth having turned out to be cosmetic — the six `BoilingWater*` terrains differ from vanilla water only by a glow colour, and in our stack are strictly WORSE (no `dbh_water` tag, so not a drinking source). We author our own scalding water and boiling rain instead: **B64**. Nothing is lost with the mod — VEF supplies the weather payload and the fog motes and `RG_HotSpringSand` live in **ReGrowth: Core**, which stays active |
| **`Skunks`** (`guppyfacesarecute.skunks`) | Owner, 2026-08-15. 5 ThingDefs, 1 pawn kind, 4 recipes — skunk, its meat, leather, corpse and gas. Nothing depended on it |
| **`Grimstone : Beasts`** (`abrolo.grimstone.beasts`) | Owner, 2026-08-15: *"not worth it. Not very high quality."* 37 ThingDefs, 7 creatures, 3 recipes. Nothing depended on it, and our `Armour_Leather.xml` and `MegafaunaYield.xml` reference it only inside `PatchOperationFindMod`, so they take the no-match branch silently |
| **`Big and Small - Sapient Animals`** (`redmattis.sapientanimals`) | Owner, 2026-08-15: *"This whole mod needs to go... We're descoping the mod."* It generated a `Humanlike`-intelligence twin of **every animal in the game — 1,073 defs**, all of them potential pawns (`HL_Penguin`, `HL_RockTroll`, `HL_Bantha`). Sapient talking animals are not this fiction. Set inactive in `ModsConfig.xml`; nothing declared a dependency on it. **Do not cherrypick its defs — they no longer load.** |

## Holds — decided later, on purpose

| item | why it is held |
|---|---|
| **`[AB] Xenotype: Yautja`** | 🔴 **Descoped 2026-08-15 on a FALSE PREMISE and RESTORED the same day.** I advised cutting it because its art was "unreviewable" — it was only unreviewable by our tooling, which could not read AssetBundles. UnityPy was installed the whole time and all 2,732 of its textures extract cleanly. The owner saw the weapons in game and liked them. **Judge it on the art now that the art is visible.** Its real costs are unchanged: 432 genes (9% of the pool) and 9 xenotypes competing with `D23` |
| **Megafauna** · **Mythic Ages: Megafauna Bestiary** | The design uses megafauna as the counter to Junker warcaskets. Big desert beasts fit the setting |
| **Onimods: Electric Torches and Braziers** | Sounds medieval, is lighting. Plausible on a scavenger world |
| **The eight D&D creatures** | bearded troll · rock troll · dwarven muffton · goldilox · black scribe · pilgrim · imperial redhound (*Dark Ages: Beasts and Monsters*) · griffar (*Grimstone: Beasts*). Owner, 2026-08-15: **hold for an image review** — names are a poor guide. Do them in the same pass as the weapons and clothing contact sheets |

## Method

**Whole-mod removals go through `ModsConfig`**, not Cherry Picker — 446 def-by-def
entries would be absurd. Reversible by re-ticking, but needs a game-down window
and carries `Could not resolve cross-reference` risk.
**Cherry Picker is for surgical cuts inside mods we keep.**
