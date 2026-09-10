# Reserved creature groups — extracted from the owner's fauna review notes

Source (read-only, never modified): `design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json`
(828 rows: 337 `fauna:<biome>:<def>`, 486 `homeless:<def>`, 5 non-fauna `q:` meta rows excluded from this sweep).

EXPLICIT = the row's own note names the group in the owner's words. INFERRED = pattern-matched
(a known flying-creature name/type with no note, or "assailant"-adjacent language short of the
literal "assailant dungeon(s)" phrase) — **the owner verifies every INFERRED row.**

A creature can appear in more than one group; each occurrence below is one hit, not a claim of
exclusivity.

---

## 1. dungeon-guardians (7: 2 explicit, 5 inferred)

| creature | source row | owner's words | confidence |
|---|---|---|---|
| AA_Mime | fauna:the_slime:AA_Mime | "Only assailant dungeons" | explicit |
| Toxalope | fauna:wasteland:Toxalope | "assailant dungeons" | explicit |
| AA_EngorgedTentacularAberration | homeless:AA_EngorgedTentacularAberration | "Assailant" | inferred |
| AA_UnblinkingEye | homeless:AA_UnblinkingEye | "assailant" | inferred |
| GR_AberrantFleshbeast | homeless:GR_AberrantFleshbeast | "Assailant territory" | inferred |
| GR_FleshGrowth | homeless:GR_FleshGrowth | "assailant" | inferred |
| GR_FleshMonstrosity | homeless:GR_FleshMonstrosity | "assailant" | inferred |

Note: the boom family's CUT commission traces to this group — Boomalope's own note reads
"Convert to a twisted thing the Assailants make in their dungeons" (see §9). Two rows use
"dungeon" without "assailant" (Hutt spicemines, mechanoid/rust cathedral) — held OUT of this
group, see NOTABLE in the parent report.

Added, `VQE_ANCIENTS_CURATION_1` (2026-09-10) — not from `fauna_assignment_register
.decisions.json` (VQE Ancients wasn't in the original review pool), owner-said "feed
VQEA_Spliceling/Splicehulk/Splicefiend/Splicetoot into the dungeon-guardians draft
roster, not biome fauna":

| creature | source | note |
|---|---|---|
| VQEA_Spliceling | VQE_ANCIENTS_CURATION_1 | flesh-mutant, same register as GR_FleshGrowth/GR_AberrantFleshbeast above |
| VQEA_Splicehulk | VQE_ANCIENTS_CURATION_1 | flesh-mutant |
| VQEA_Splicefiend | VQE_ANCIENTS_CURATION_1 | flesh-mutant |
| VQEA_Splicetoot | VQE_ANCIENTS_CURATION_1 | flesh-mutant (defName is singular — the donor's own containment building is "...Containments", the race is not) |

## 2. trader-beasts (1 explicit, 0 inferred)

| creature | source row | owner's words | confidence |
|---|---|---|---|
| Behemoth | homeless:Behemoth | "huuuge trader pack animal" | explicit |

Thin group — only one row carries "trader"/"caravan" language anywhere in 823 creature rows.

## 3. fliers (38: 4 explicit, 34 inferred)

Explicit (note itself says flyer/flier/flies):

| creature | source row | owner's words | confidence |
|---|---|---|---|
| AA_Skyeel | homeless:AA_Skyeel | "Electrostatic flyer over Propane Lakes" | explicit |
| Aiwha | homeless:Aiwha | "HUGE flyer, could appear anywhere, mountable..." | explicit |
| BMT_SmogMoth | homeless:BMT_SmogMoth | "Neat flier in the Rot" | explicit |
| Bogwing | homeless:Bogwing | "miasma flyer" | explicit |

Inferred (known flying-creature name/type, no flight language in note — owner verify each):

| creature | source row | owner's words | confidence |
|---|---|---|---|
| Convor | fauna:arid_shrubland / the_cracked_lands / the_fever_wood / the_greentide:Convor (4 rows) | (no note) | inferred |
| AA_InfectedAerofleet | fauna:poison_forest, fauna:the_contagion (2 rows) | (no note) | inferred |
| AA_Aerofleet | fauna:terminator_sea+grey_deep, +twilight_deep, the_forge (3 rows) | (no note) | inferred |
| Hawkbat | fauna:the_greentide:Hawkbat | (no note) | inferred |
| AA_FireWasp | fauna:the_pyrelands:AA_FireWasp | "I like this a lot" | inferred |
| BMT_GlowBat | fauna:the_rot:BMT_GlowBat | (no note) | inferred |
| AA_AngelMoth / AA_AngelMothLarva | homeless (2 rows) | "Rot" / "Wildsteam biomes" | inferred |
| AA_ColossalAerofleet | homeless:AA_ColossalAerofleet | "rare creature wherever normal aerofleets end up" | inferred |
| AA_EmpressButterfly / Larva | homeless (2 rows) | "Wildsteam areas" / "Wildsteam biomes" | inferred |
| AA_Locusts | homeless:AA_Locusts | "...huge numbers...event" | inferred |
| AA_SmallButterfly | homeless:AA_SmallButterfly | "flits around the arid shrubland" | inferred |
| BMT_BloodropMoth | homeless | (no note) | inferred |
| BMT_FacetMoth / Larvae / Pupa | homeless (3 rows) | "brightly colored...jungle" / "crystal caverns" / (none) | inferred |
| BMT_FamineLocust | homeless | (no note) | inferred |
| BMT_Megabat | homeless | (no note) | inferred |
| BMT_SmogMothLarvae | homeless | (no note) | inferred |
| BMT_Woollybat | homeless | (no note) | inferred |
| Drone_Wasp | homeless | (no note) | inferred |
| GR_FleshFlies | homeless | (no note) | inferred |
| Locust | homeless | (no note) | inferred |
| PoisonButterfly | homeless:PoisonButterfly | "Maybe a pet for beauty?" | inferred |
| VFEI2_Gigalocust | homeless | (no note) | inferred |
| VFEI2_Megawasp | homeless | (no note) | inferred |
| Vulture | homeless | (no note) | inferred |

Name-pattern matching used word-boundary splitting (not substring) to avoid false hits like
"Mammoth"/"Behemoth"/"Prowler" (contain moth/owl as substrings, not real month/owl words) —
those were excluded. Coverage is best-effort against name lore, not a def-level flight-capability
check; the owner's verification pass is load-bearing here.

## 4. named-plot-uniques (0 hits)

No row anywhere in the 823 creature rows uses "plot", "unique", "one-of-a-kind" language, or
"the deep thing". **This reserved group has zero signal in the notes.** Either the group is
populated by rows this sweep can't detect (verdict-only, no distinguishing note text) or the
owner has not yet written any plot-unique creature into this register. Flagged for the owner —
see UNKNOWN in the parent report.

## 5. event-only (4 explicit, 0 inferred)

| creature | source row | owner's words | confidence |
|---|---|---|---|
| AA_Locusts | homeless:AA_Locusts | "...eats plants ravenously and won't stop, event" | explicit |
| GiantAnt_Race | homeless:GiantAnt_Race | "Only the raiding events in the greentide jungles..." | explicit |
| Maalraas | homeless:Maalraas | "...ability to cloak and hunt, dangerous event" | explicit |
| Stintaril | homeless:Stintaril | "...attempting to infest the player's ship in events" | explicit |

## 6. mounts-and-work-beasts (3 explicit, 0 inferred)

| creature | source row | owner's words | confidence |
|---|---|---|---|
| Aiwha | homeless:Aiwha | "...mountable, air, sea, land..." | explicit |
| Behemoth | homeless:Behemoth | "huuuge trader pack animal" | explicit |
| Insectomorph | homeless:Insectomorph | "ridable mount associated with the Drug..." | explicit |

## 7. farmed-stock (0 hits)

No row uses "milk", "farm", "livestock", "pen", "shear", or "egg" as a whole word. One
near-miss: `homeless:Blurrg` — "Moisture Farmers territory, domesticated" — "Farmers" is a
faction name (the moisture-farming settlers), not the farmed-stock signal word "farm", so it is
held OUT of this group. See NOTABLE in the parent report.

## 8. reserve-pool (1 explicit, 0 inferred)

| creature | source row | owner's words | confidence |
|---|---|---|---|
| PoisonButterfly | homeless:PoisonButterfly | "Maybe a pet for beauty?" | explicit |

(Also double-counted in §3 fliers — PoisonButterfly hits both.)

## 9. boom family — CUT (15 of 15, ruling not row-derived)

Every member below is cut by direct owner ruling, not a note pattern. One new fleshy goo-sack
dungeon creature replaces the family — and Boomalope's own row is the textual source for that
commission (see §1).

| creature | source row | decision in register | note |
|---|---|---|---|
| Boomalope | fauna:the_pyrelands:Boomalope | move | "Convert to a twisted thing the Assailants make in their dungeons" |
| VFEI2_Boomtick | fauna:the_scarlands:VFEI2_Boomtick | in | "0.7 cells" |
| Boomrat | homeless:Boomrat | out | (none) |
| GR_Bearalope | homeless:GR_Bearalope | in | "follow the boom beasts" |
| GR_Boomabear | homeless:GR_Boomabear | out | (none) |
| GR_Boomalisk | homeless:GR_Boomalisk | out | (none) |
| GR_Boombeetle | homeless:GR_Boombeetle | in | "go with the boom" |
| GR_Boomcat | homeless:GR_Boomcat | in | "go with the boom" |
| GR_Boomffalo | homeless:GR_Boomffalo | out | (none) |
| GR_Boomsnake | homeless:GR_Boomsnake | move | "Pyrelands" |
| GR_Boomsquirrel | homeless:GR_Boomsquirrel | in | "with the boom creatures" |
| GR_Chickenlope | homeless:GR_Chickenlope | in | "goes along with the other boom creatures" |
| GR_Manalope | homeless:GR_Manalope | in | "wherever the boom creatures go" |
| GR_ParagonBoomalope | homeless:GR_ParagonBoomalope | in | "with the boom" |
| GR_Squirralope | homeless:GR_Squirralope | in | "with the other boom creatures" |

Note: 8 of these 15 carry `decision: in` in the register (the owner had provisionally kept
them before the boom-family cut ruling superseded that row-level call) — the family ruling
overrides the row decision.

## Rulings landed 2026-09-10 (fauna wrap sitting, owner-carded)

- **NINTH ROSTER RULED: faction-territory fauna** — one roster, faction column
  (Hutt / Helix / Wildsteam / Moisture Farmers). The 22+ faction-ground rows in
  move_mapping_v2's OPEN list belong here. Mechanism (settlement mapgen vs
  territory wilds) gets its own design pass.
- **Dungeon-guardians: ONE roster with a dungeon-owner column** (Assailant /
  Hutt spicemine / Rust Cathedral / mech dungeons). EnergySpider and GR_Mecharat
  move in with their owners marked; the goo-boom commission and the 4 VQEA
  Splice creatures are Assailant rows.
- **Jungle ambiguity RULED: all three go to BOTH jungles** — Tach, Rikknit,
  BMT_FacetMoth appear in the_greentide AND the_fever_wood.
- **Homeless disposal plan** (to be confirmed at the bucket sitting, not before):
  the 206 out-verdict rows bulk-cut; the 103 unannotated in/move rows get the
  by-bucket sitting.
- **Venomthorn (GR_Snakecat)**: no such plant exists in any doc or the stack —
  proposed as a new flora commission (Moisture Farmer territory antagonist
  plant); awaiting the owner's yes.
