# The Fever Wood fauna roster — 11 invented creatures, 2026-09-23

_MACBENCH, authored against the owner's rulings of 2026-09-23
(`fever_wood_deep_and_mud_2026-09-23.md`) and the frozen sheet (`the_fever_wood.md`).
Companion to `fever_wood_flora_roster_2026-09-23.md`, same sitting, same naming register._

---

## READ FIRST — what this roster is, and the three things it deliberately does not author

The sitting record ruled a great deal of fauna behaviour and named almost no species. This
document turns those rulings into a cast. It is **11 new `RM_`-tier creatures**, organised by
the bands the existing roster already uses (`rosters/the_fever_wood.json`: crown-flier,
wood-borer, sap-drinker, crown-grazer, wait-ambush, ground-slow, the-terribly-lost).

⛔ **Three things are out of scope and must not be folded in:**

| not here | why | who owns it |
|---|---|---|
| **the deep thing** | it is a set-piece with one elder being reaching through many pools, not a roster row — and its free-tier name was settled this sitting as the **Sekkulaath** | `FEVERWOOD_TENTACLE_BESTIARY_1` |
| **the two raiders** — Ants and Feralisks | 🔴 both arrive as **off-map raiders**, never as `wildAnimals` residents. The sheet's ban on native chase predators is why the crown is ambushable only through concealment | `FEVERWOOD_ANT_HIVE_DUNGEON_1`, and the sheet's §4 two-front war |
| **the 12 existing fauna rows** | evictions are stopped (owner, 2026-09-22) and rosters are handled at each biome's own sitting | that sitting, when it comes |

⚠️ **Naming follows §6o**: the same word-shape as the Greentide's roster, biased wetter and
slower. One planet, one language. ⛔ No name here collides with the Greentide's 22, the Fever
Wood's 18 plants, the Miasma's 24, or any shipped `RM_`/`RUT_`/`RSW_` def — checked this pass.
⚠️ The accepted cost of that ruling is that the two wetlands may blur, so **the distinguishing
work falls on silhouette**, which is why §6 is the acceptance test.

---

## 1. At a glance

| the sap-drinker guild (4) | the wood (1) | the crown (2) | the birds (4) |
|---|---|---|---|
| **thornbug** — the nectar contract, already in the sheet | **brathek** — digs your walls, slowly and visibly | **lommerel** — the crown's grazer | **chellow** — the chorus you can keep |
| **vaulm** — seals itself in its own sap | | **silloch** — the small patient predator | **murrelith** — plumage worth money |
| **ollareth** — screams, and the crown comes | | | **thavrik** — nests worth raiding |
| **drommath** — swells so it cannot be pulled off | | | **skellick** — ⭐ steals your things |

---

## 2. The sap-drinker guild — four species, one rule, four expressions

**Owner's brief:** *"Perhaps more creatures that sit and drink sugary sap and resist being
bothered via various defenses?"* ⇒ A **guild**, not a creature. Every member is clamped to
bark, drinks sap, and does not flee. They differ only in **how they refuse to be bothered.**

🔴 **Ruled this sitting, and both halves matter:**
- **Three new defences** (owner, verbatim): *"There should be three kinds of these sap-suckers,
  each with a different kind of defense above"* — and the guild is **four**, the thornbug
  keeping its own deal (§6g).
- **All four are herdable, and taming does NOT disarm them** (owner: *"1+3"*). A tamed one
  still triggers its refusal when frightened or mishandled.

🔑 **The whole guild works on consent, and fear is the universal failure mode.** That is one
rule with four expressions — and it is the thornbug's existing nectar contract generalised, not
a new idea bolted on.

| # | defName | label | silhouette FORM | the refusal | what it yields | band |
|---|---|---|---|---|---|---|
| 1 | `RM_Thornbug` | thornbug | **great thorn-shaped insect clamped flush to bark** | 🔴 **the contract** — yields only while it feels safe; a frightened herd dries up for days (hard ban 6, *never yields under fear*) | **nectar** — sweet and nourishing; the dairy the arboreal cantons run on | sap-drinker |
| 2 | `RM_Vaulm` | vaulm | **a smooth swollen bead of amber on the bark, no limbs visible** | **seals itself in hardened sap.** Bothered, it floods its own shell and sets; it must be cracked open to reach | ⭐ **lacquer** — a usable material, and the reason to bother with a sealed one | sap-drinker |
| 3 | `RM_Ollareth` | ollareth | **flat, wide, and ringed with open spiracles** | **screams for help** — sets the chorus off and pulls the crown's predators toward whatever is bothering it | nothing directly. 🔑 **Its value is that it makes the crown fight for it** | sap-drinker |
| 4 | `RM_Drommath` | drommath | **a taut grey sac, visibly inflating** | **swells until it cannot be detached.** Handled, it inflates rather than yield | a **large one-time payout** if burst — which destroys a renewable source | sap-drinker |

🔴 **The guild is a perimeter decision, not a barnyard.** The ants steal nectar-beasts **alive**
(theft, not slaughter), so a well-defended species is one the ants *cannot take* — and
`RM_Ollareth`'s refusal is the one that turns a theft raid into a fight the biome joins on your
side. ⇒ Which species you keep, and where, is a defensive choice.

⚠️ **Balance risk named at the card and accepted:** self-sabotaging livestock can read as
frustrating rather than characterful. ⇒ **The trigger conditions must be legible and
avoidable.** A rancher who keeps things calm should never be punished at random. ⛔ Do not ship
a random chance of refusal.

⛔ **"Drops into the pool" was OFFERED AND DECLINED** as a fourth defence — declined, not
deferred. ⚠️ It was the idea that would have explained why anything lives in the deep, and that
question was answered separately and completely (§6e: the pools are windows onto one water
table, the mud is the food, it eats the lost, and it farms). ⛔ **Do not quietly revive the
pool-drop mechanism**, for this guild or any other.

---

## 3. The wood — one borer, and it changes your base

🔴 **Ruled this sitting:** living borers **extend their galleries over time.** Bore-caves are
not a fixed map-gen feature — a trunk you live in keeps changing, and can open into places you
did not wall.

| # | defName | label | silhouette FORM | what it looks like | job | band |
|---|---|---|---|---|---|---|
| 5 | `RM_Brathek` | brathek | **long segmented cylinder, head plate wider than the body** | A heavy ringed grub the length of a forearm, pale and wet, with a dark rasping head-plate broader than the rest of it so the tunnel it cuts is always wider than the animal. Seen head-on in a gallery mouth, or as a moving bulge under bark. | ⭐ It **earns the sheet's own borer guild** rather than decorating caves it never made. And it is a **living excavation tool** — a colony that keeps brathek can cut trunk rooms nothing else on the planet can. | wood-borer |

⚠️ **Accepted cost, named at the card:** a creature that alters your walls without asking is a
security problem. ⇒ 🔴 **The digging must be slow and VISIBLE** — a player must be able to watch
a gallery advance and deal with it, and must never find a breach they had no warning of. ⚠️
**Rate unset**, and it is the single most important unset number in this roster.

⚠️ **Whether brathek can be DIRECTED is unsettled.** §6n establishes only that *sap-suckers* are
herdable, and the borer is not one. ⛔ Do not assume the excavation tool is steerable; that is a
separate ruling.

⚠️ `VFEI2_Megathrips` currently fills the wood-borer band at 0.5 as a donor row. This roster
does not remove it — see §7.

---

## 4. The crown — a grazer and its small patient predator

The sheet's §4 guild is *"canopy grazers and their small patient predators… all of it in
ambivalent harmony — nothing here is at war with the trees, because the trees are the only
reason anything is dry."*

| # | defName | label | silhouette FORM | what it looks like | job | band |
|---|---|---|---|---|---|---|
| 6 | `RM_Lommerel` | lommerel | **low broad body slung UNDER the branch it feeds on** | A soft-bodied grazer that hangs beneath a bough rather than standing on it, gripping with short hooked limbs, its back permanently silted and mossy from the crown's own debris. Reads upside-down, which nothing else in the crown does. | **The crown's grazer** — the herd that eats `RM_Verrow`'s gourds and the bough-soil's cover, and the reason the small predators have anything to wait for. Meat and hide at crown level, reachable from a boughway. | crown-grazer |
| 7 | `RM_Silloch` | silloch | **a still, flattened wedge pressed into bark, legs folded under** | Almost nothing to see: a flat mottled wedge the colour of wet bark, folded utterly motionless against a trunk, with only a pair of forward limbs held cocked. It does not stalk. It waits, sometimes for days, and then it is simply attached to something. | 🔑 **The crown's patient predator** — and the sheet's ban on native chase predators is exactly why it must be an ambusher. It is the reason `RM_Maulith`'s ribbon curtains are dangerous, since concealment is the biome's only ambush mechanism. | wait-ambush |

🔑 **Together they make the crown an ecology rather than a larder.** The grazer is drawn by the
crown's fruit; the ambusher is drawn by the grazer; and a player harvesting the crown is walking
into the middle of that. ⛔ Neither is at war with the trees — that is the sheet's *ambivalent
harmony* and it holds.

---

## 5. The birds — four roles, all four taken, and they must not look like parrots

**Owner, verbatim:** *"Some birds here steal items if you have Property mod. And these should be
alien birds, not just parrots. Very strange. Membranous, hairy, or weirdly shaped feathers."*

Decisions taken by question card: **tameable companions, plumage worth money, AND nests worth
raiding** — all of them, not a choice. Plus the thieves.

🔴 **Art direction, and it is a hard requirement rather than flavour:** membranous, hairy, or
weirdly-shaped feathers. ⛔ **A brightly-coloured Earth-parrot silhouette fails this brief even
with an exotic palette.** Each row below states what is alien about its plumage, because that is
the acceptance criterion.

🔑 **And per the standing rule: if it flies in the fiction, it flies in the game.** All four take
real flight — `MaxFlightTime` / `FlightCooldown` plus the race flags, which are **Core in 1.6**,
not Odyssey and not a donor framework. ⛔ The switch is a **stat**, not a `canFly` bool. ⚠️ The
flight *animation* is a separate whole-body directional flip-book; with no frames they fly
without a wing-beat, which is correct behaviour and a plainer look. ⛔ **Never block flight
waiting on frames**, and ⛔ never build a per-wing render-tree for it — that approach was tried
on the fire hawk and reversed.

| # | defName | label | silhouette FORM | what is ALIEN about it | role | band |
|---|---|---|---|---|---|---|
| 8 | `RM_Chellow` | chellow | **squat, round, with a wide membranous throat-fan** | No feathers on the head at all — bare wrinkled skin and a translucent throat-fan it inflates to call, veined and lit from behind | ⭐ **Tameable** — a private chorus you cultivate near the base | crown-flier |
| 9 | `RM_Murrelith` | murrelith | **long-tailed, with flat ribbon plumes instead of a fan** | Its tail "feathers" are **flat translucent ribbons**, not vaned quills — they hang and twist rather than spread, and they are what is worth money | **Plumage** — a real trade good. 🔑 The temptation is set directly against the alarm: selling feathers means shooting your own early-warning system | crown-flier |
| 10 | `RM_Thavrik` | thavrik | **heavy-bodied, short-winged, with hairy pelt-like covering** | Covered in coarse **hair rather than feathers** except on the flight surfaces, so it reads as a furred thing that flies | **Nests** — eggs and nest material high in the crown, guarded by the adults. A reason to climb | crown-flier |
| 11 | `RM_Skellick` | skellick | **small, long-limbed, with asymmetric crumpled plumes** | Plumes that look **damaged on purpose** — crumpled, unequal, sticking out at wrong angles; the untidiest silhouette in the crown | ⭐ **Thief** — it steals items. Gated `MayRequire="mandrake.rm.property"` | crown-flier |

✅ **The Property mod is OURS, verified on disk:** packageId `mandrake.rm.property` at
`src/RimMandrake/RimProperty/` with its own `Assemblies/`. ⇒ The stealing behaviour is a clean
`MayRequire` on content we control, **not a third-party dependency**, so it is legitimate in the
`RM_` tier.

⚠️ **Injection candidates already built and homeless, all fliers** — `RSW_CanCell`,
`RSW_Neebray`, `RSW_Porg`, `RSW_Sacapillar`, `RSW_Mynock`. Each must be checked against the
membranous/hairy/strange brief before use, and ⚠️ **`RSW_Porg` is canonically bird-cute and
probably fails it.** ⛔ These are additive Star Wars injection on the campaign patch layer only —
they never substitute for a row above.

---

## 6. The legibility matrix — the acceptance test

Every form must be nameable from a top-down sprite at display size. A duplicated row is a
failed roster, and with four sap-drinkers sharing a posture this is the section that matters
most.

| form | row | reads as |
|---|---|---|
| great thorn clamped flush to bark | thornbug | a thorn on the tree |
| smooth amber bead, no limbs | vaulm | a drop of resin |
| flat and wide, ringed with open spiracles | ollareth | a vent, or a grille |
| taut grey sac, visibly inflating | drommath | something about to burst |
| long cylinder, head plate wider than the body | brathek | a drill bit |
| broad body slung UNDER the branch | lommerel | **upside-down — the only row that is** |
| flat wedge folded motionless on bark | silloch | **bark, which is the point** |
| bare head, inflated membranous throat-fan | chellow | a lamp with a bellows |
| flat translucent ribbon tail-plumes | murrelith | torn cloth |
| hairy pelt, short wings | thavrik | a furred thing that should not fly |
| crumpled asymmetric plumes | skellick | something that has been in a fight |

🔑 **The four sap-drinkers are differentiated by state, not by body** — a thorn, a resin drop, a
grille and a swelling sac. That is deliberate: they are one guild, and a player should read
"another sap-sucker" and then "which one". ⚠️ **`RM_Silloch` must read as bark** and
`RM_Lommerel` must read as upside-down; an art pass that "corrects" either has broken the design.

---

## 7. What is owed

- 🔴 **All 11 need art**, and none exists. ⚠️ **MEASURED 2026-09-23: 0 of the 18 Fever Wood
  plants had any artpipe or decisions-sheet presence**, so this biome has no reservoir of
  already-ruled art to draw on — but run the same search per creature before queueing anyway
  (owner's standing rule, 2026-09-20). ⚠️ The artpipe daemon does not run on the Mac.
- 🔴 **`RM_Brathek`'s digging rate is unset** and is the roster's most consequential missing
  number. Slow and visible is the ruling; a rate that lets a gallery surprise a player breaks it.
- 🔴 **The guild's refusal triggers must be legible and avoidable, never random.** This is the
  accepted-risk mitigation and it is a design requirement, not a tuning note.
- ⚠️ **`CompProperties_HasGatherableBodyResource` has no precedent in this repo** — there were
  zero hits when the sitting recorded it. `RM_CompGatherableCalmGated` already compiles and is
  the thing to use for the nectar contract; `FEVERWOOD_SAP_SUCKER_GUILD_1` owns that build.
- ⚠️ **Whether `RM_Brathek` can be directed is unsettled**, and whether a tamed sap-sucker's
  refusal can be wired at all is an **engine question** — UNMEASURABLE on the Mac.
- **This document removes nothing from the live biome def.** The donor rows in the bands these
  creatures fill — `VFEI2_Megathrips` (wood-borer), `Gelagrub` (crown-grazer), `LongtailGorg`
  (wait-ambush), and the three donor crown-fliers — stand until this biome's roster sitting.
  ⛔ Evictions are stopped.
- ⛔ **Do not give the Ants or the Feralisks a `wildAnimals` row.** They are off-map raiders, and
  making either resident deletes the two-front war.

---

## 8. For the owner

1. ⚠️ **The guild's four members share a posture on purpose** — all clamped to bark, drinking
   sap — and are told apart by *state*: a thorn, a resin bead, a vent, a swelling sac. If you
   wanted four visibly different animals rather than four readings of one animal, that is a
   different art brief and worth saying now, before anything is drawn.
2. 🔴 **`RM_Brathek` is the one row that can annoy a player badly.** A creature that opens your
   walls is only characterful if you can always see it coming. I have written "slow and visible"
   in as a requirement, but the rate is yours and nobody has proposed one.
3. ⚠️ **I gave the birds four species, one role each.** Fewer birds carrying two roles apiece
   would be cheaper in art; four is the reading that keeps each silhouette doing one job. One
   row could be cut by giving the thief the plumage too.
4. ⚠️ **`RSW_Porg` probably fails your own brief.** It is on the homeless-flier list and it is
   canonically cute rather than strange, so I have flagged rather than used it.
