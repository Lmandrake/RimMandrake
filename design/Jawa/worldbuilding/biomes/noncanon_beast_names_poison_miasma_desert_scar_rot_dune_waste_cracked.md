# Non-canon beast names — Poison Forest, Miasma, Desert, Scarlands, the Rot, Dune Sea, Wasteland, Cracked Lands

**DRAFT for the owner, 2026-09-24. Nothing applied.** Phase 1, batch 2 of
`NONCANON_BEAST_RENAME_1` (census + drafted names, by biome), continuing
`noncanon_beast_names_crags_nightside_contagion_slime.md` — whose Appendix A/B census is the
source here and is not re-derived. Beasts only; flora is its own track. Every drafted name and
alternate below (104 words) passed `python3 src/RimMandrake/Utils/check_pseudo_sw_name.py`
(104/104, shape + no collision with the 137 canon entries), a sweep against every `<label>` in
`src/` (5,522 labels, probe `bokka` hit, 0 collisions), a first-four-letter stem sweep against
the 623 coined stems already ruled or drafted planet-wide (Rot, Lantern Deeps, batch 2, batch 3
and the September roster docs — one overlap found and swapped: *thrixeth* → *krexxa*, against
the crags' *thrizzik*), and a Wookieepedia `list=search` sweep (probes `bantha` hit, `zzqxxv`
missed; one exact title found and swapped: *kondra* is a real page → *dunkara*). The checker
judges shape; the owner judges taste. Strike what you dislike, say what it should be, or say
*"all fine"*.

Format follows the three precedents: current label → **drafted label** (alternate), one-line
rationale, lowercase RimWorld labels, **defNames do not change here** (that is
`DONOR_DEFS_PORT_TO_OURS_1`'s question). Label and description are wired together on
acceptance, never the label alone; life stages, eggs and items that carry the stem follow it.

## What is already ruled or settled, so it is not re-drafted

- **Batch 2 (the DesertPort sixteen) is RULED and APPLIED** (`32ecbc8cb`). Seven Desert and
  Dune Sea donor rows are port-named by it and confirmed below (§ Desert) — each port's
  description is the donor's text rewritten, so donor and port are one beast with one name.
- **The Rot's ruled fauna** (rennok, gromma, durrok, mullgoth, vorrugath, chittik, skerrith,
  grellik) stand. **The Wasteland's** grutt, grithe, kroffa, puffmite stand. **The ikee** stands.
- **Batch 3's drafts** are cross-referenced, not re-drafted: *ozhilla* (ocular jelly),
  *blistered bulloo* (infected aerofleet), *vulloth* (helixien), *mubbrak* (decay drake),
  *bezzul* (plasmorph), *thollum* (slurrypede), *kessik* (murkling), *lesser wollub* (small
  amoeba), *vosska*/*ommok*/*khorrak*/*korrum*/*vozzik*/*kudda* (ports).
- **Three census corrections, MEASURED this pass against Wookieepedia's own text** (corrected in
  the first batch's Appendix A/B in the same commit — correctness outranks seat):
  - `RSW_ShiroTrap` *shiro-trap* is **CANON (Legends)**, not "non-canon wearing a real title":
    the Wookieepedia *Shiro-trap* page describes exactly our def — "not a separate creature, but
    a symbiotic pairing of a Tooke trap plant and a Shiro", Naboo, *The Gungan Frontier*. Our
    description is that text. Renaming it would be the defect the item forbids. **Keep.**
  - `WarWyrm` *war wyrm* is **CANON (Legends)**: the *Sith wyrm* page ("originally an infant
    exogorth… Naga Sadow… fourth moon of Yavin") is what our description paraphrases, and the
    def's own text says "sometimes called the 'sith wyrm'". **Keep**; whether the label should
    read *sith wyrm* (the canon title) is a canon-label question, not this item's.
  - `FeralGrazer` *feral grazer* is **CANON (Legends)**: *Grazer (Alderaan)* — "docile, four
    legged, slow-moving herbivore native to Alderaan… related to the Nerf. Wild grazers were
    significantly leaner". Our description is that text. **Keep.**
- **Two defs are dead or misplaced and draw no name:** `AA_Dunealisk` (Dune Sea roster row) —
  the whole Alpha Animals `-lisk` clade was retired by Cherry Picker cut at `7bad94185`
  (`WYYYSCHOKK_FERALISK_MERGE_1`); the roster row names a dead def and is stale.
  `RSW_ShaleGorger` (Scarlands roster row, owner's own round-2 note: *"Scarlands, oddly"*) is a
  **sea beast** — it lives in `SeaBeasts_Opee.xml` as the invented "heavy benthic" morph of the
  canon opee sea killer (`sea_beasts_roster.md` row `opee_opt3`, `star_wars_canon_names.md` line
  98). It belongs to the sea batch, which is blocked on `TERMINALBIOMES_RM_MOD_BUILD_1`, and as an
  invented morph of a canon species it will want the canon variant shape there (*jungle worrt*),
  not a fresh stem.

## Style rules applied

Batch 3's six rules unchanged (coined not compounded · never a real Star Wars name · one stem
per species, kinship in the description · variants take the canon variant shape, life stages
keep their plain stage word · one accent per biome · a multi-homed def has one name planet-wide,
drafted where its job is written), plus:

7. **A biome whose cast already carries ruled names keeps THAT accent.** The Desert continues the
   batch-2 sixteen (doubled consonant, -a/-ik/-ok, 5–7 letters); the Rot continues rennok /
   durrok / skerrith / grellik (liquids, -ok/-ik/-ith/-oth); the Wasteland continues kroffa /
   grutt / grithe (dry fricatives, clipped). New accents only where nothing is ruled yet:
   **Poison Forest** — glassy and acidic: thin front vowels, ts/sk/x/ss, -ix/-iss/-eth.
   **Miasma** — nasal-velar: nd/ng/nk clusters, back vowels, open endings; no m-/b-/w- openings
   (those are the Slime's). **Scarlands** — voiceless and clipped, like designations worn into
   names: t/k/ts/ch/x, short vowels, -t/-ak/-ix. **Cracked Lands** — dry then sudden: q and tt,
   -a/-aq. **Dune Sea** — the Desert accent said once into silence, with one long vowel.
8. **A donor coinage that already passes the checker is offered a rename, not forced one** —
   the *vellara bloom* precedent. Two such rows below (*yooka*, *norphea*) carry the offer with
   the existing word as the alternate.
9. **Agent-invented art names are not rulings.** Four rows here carry a name an art-regen wave
   coined for its prompt (*Scarrend*, *Fenshear*, *Slagmaw*, *Verdaunt* — `ART_REGEN_WAVE5/6/7`).
   None was owner-ruled, all four are English compounds that fail THE STANDARD, and the *Mycolith*
   → *vorrugath* precedent shows the ruled label supersedes them. The artpipe job ids stay as
   history; the drafted label wins. Flagged per row.

---

## Batch 4a — Poison Forest (`poison_forest.json`, 24 rows; 17 in scope, 12 drafted here)

*A forest of ambushers under a sourceless twilight, where everything alive is sealed or
poisoned and the ground hums with chemistry.* The accent is glass and acid — thin vowels,
hissing clusters, clipped endings. 10 stems, 12 defs.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AM_Dryad_Corruptor` · `AM_Dryad_Ocular` · `AM_Dryad_Tumorous` | corruptor / ocular / tumorous dryad | three castes of one corrupted Gauranlen dryad line (bs 0.67): the pod-sower, the eye-studded, the tumour-grown (edible growths) | **tessik** · **eyed tessik** · **tumorous tessik** | essix | One stem for one species, castes as plain modifiers (rule 4). *tess-* thin and wet, *-ik* small. The sower is the base caste because it makes the others. ⚠️ **Scope flag 3 below** — "dryad" is a vanilla Ideology family word. |
| `RSW_Screecher` (+ eggs) | screecher | pollution-mutated corvid that stuns with its cry, pack hunter (bs 1.0) — also Wasteland, one name | **isskra** | vexxit | The cry then the snap: *iss-* the shriek, *-kra* the beak. Removes a false canon read — *Screecher* is a real Kirtania creature and this is not it (`NONCANON*`). |
| `Visceral` | visceral | human-sized sealed insectoid horror, rending raptorial legs, hide-tearing maw (bs 1.2) | **krexxa** | eskrith | Two hard cracks and an open end: *kr-* the legs closing, *-xx-* the maw. "Visceral" is an English adjective. (First draft *thrixeth* swapped — shared its opening with the crags' *thrizzik*.) |
| `AA_BedBug` | bedbug | paralysing-bite ambusher insect, a pest everywhere (bs 0.5) | **tsikka** | ikseth | Small and sibilant, the tick of something you did not see; *-kka* the bite. Both halves of "bedbug" are Earth words. |
| `AA_CrystalMit` | crystalmit | silicon-based rock-eater, rubble-clearing mit gone wild (bs 0.5) | **skixxet** | tsekkit | Crunch in the mouth: *skix-* stone breaking, *-et* the click. Matches the crystal fans of the trunks (sheet §1). |
| `AA_GiantCrownedSilkie` | giant crowned silkie | large flightless silk-and-egg bird, placid farm stock (bs 1.1); silhouette eye-test owed | **ithessa** | tsellia | Three soft syllables for the one gentle thing in the forest; *-essa* the silk. "Silkie" is an Earth chicken breed. |
| `GR_Beetlefleet` | beetlefleet | chitinous hydrogen-float that bounces off things and explodes on death (bs 0.3) — also Wasteland, one name | **skibbex** | tsobbix | A drift and a pop: *ski-* the float, *-bbex* the burst. Named here because the Poison Forest sheet gives it its "sealed, sit-and-wait" job. |
| `AA_LuciferBug` | luciferbug | tiny insectoid that brews luciferium and detonates (bs 0.15) | **zithix** | kizzeth | The smallest and sharpest word in the set — *z*, *th*, *x*, nothing soft. "Lucifer" is an Earth name and a RimWorld drug word. |
| `AA_Radyak` | radyak | peaceful radiation-eating ruminant, six bionic stomachs, uranium crystals through the hide (bs 2.5) | **urrixa** | ixxareth | The biggest grazer gets the roundest opening — *urr-* a slow chew — and the forest's *-ixa* crystal ending. "Radyak" is rad + yak. |
| `AA_RipperHound` | ripper hound | hulking chitin-ripping canine bred against insectoids; affectionate (bs 1.5) | **tharrix** | vixxar | *th-* the breath of a big dog, *-arr-* the growl, *-ix* the claw. "Ripper hound" is two English words. |

**Not drafted:** `AA_OcularJelly` *ozhilla*, `AA_InfectedAerofleet` *blistered bulloo*,
`AA_Helixien` *vulloth*, `AA_DecayDrake` *mubbrak*, `AA_Plasmorph` *bezzul* — batch 3.
`AA_Wildpod` *mullgoth* — ruled (see batch 3 flag 2 for its second name). Canon kept: Neebray,
Lylek, Mynock, Silooth, Skalder, Granite slug.

Read aloud: tessik, isskra, krexxa, tsikka, skixxet, ithessa, skibbex, zithix, urrixa, tharrix.

---

## Batch 4b — the Miasma (`the_miasma.json`, 32 rows; 15 in scope, 11 drafted here)

*The lifeboat at the drain: everything ends up here and is worked, ferociously, toward
something not ready.* Hot, wet, crowded, stinking. The accent is nasal and velar — *nd*, *ng*,
*nk* — with back vowels and open endings, a gurgle in every word; nothing opens on m/b/w,
which the Slime owns. 9 stems, 11 roster defs.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `VFEI2_Swarmling` · `VFEI2_BlackSwarmling` | swarmlings · black swarmlings | juvenile insectoids of the VFE hive / Black Hive; harmless, slow, metamorphose (bs 0.2) — also Wasteland, Greentide | **nunda** · **black nunda** | kinnu | Soft nasal plural-feeling word for a thing never seen singly; the Black Hive variant takes the plain modifier. ⚠️ **Scope flag 3** — a framework mod's juvenile stage; and `AA_Swarmling` is a different def already ruled *chittik*. |
| `RSW_CrestedDragon` (+ eggs) | crested dragon | crest-headed wet lizard, "cute squeaky noises", channel predator (bs 0.7) | **dunkara** | ondura | The squeak is in the *-ka-*; *dun-* the wet weight before it. Art wave 6 coined *Verdaunt* for its prompt — an English compound, not a ruling (rule 9). (First draft *kondra* swapped — a real Wookieepedia page.) |
| `RSW_AaroxisDendoria` (+ pupa, + larvae "cinnabar caterpillar", + eggs) | aaroxis dendoria | wingless engineered silk moth; crimson larva, red-bellied pupa (bs 1.0) | **ombuna** · **ombuna pupa** · **ombuna caterpillar** | nandoro | Round, humming, slow — a moth that never flies. Life stages keep the plain stage word (rule 4); "cinnabar caterpillar" loses its Earth-pigment name with the family. "Aaroxis dendoria" is a fake Latin binomial. |
| `AA_RaptorShrimp` | raptor shrimp | regenerating, bullet-shrugging crustacean ambusher — "the grass has eyes" (bs 1.4) | **drangok** | kunggra | *dr-* the lunge out of the reeds, *-ang-* the delta's nasal, *-ok* the claw closing. Art wave 7's *Fenshear* is an English compound (rule 9). |
| `AA_Mantrap` | mantrap | weaponised acid-spitting flytrap, root-maze ambusher (bs 2.0) | **undakka** | tondak | The trap in three beats: *un-* still, *-dak-* shut, *-ka* the acid. ⚠️ **Flag 2** — a second, different def in the Cracked Lands wears the same label "mantrap" and gets its own name there (*saqqat*). |
| `AA_Lockjaw` | lockjaw | huge-bite shallows reptile, paralysing disease, not aggressive, slow (bs 2.5) | **enduk** | gungora | Short, blunt, a jaw closing on *-duk*. Also removes a half-collision: *Luudrian lockjaw* is a real canon creature. |
| `AA_Thermadon` | thermadon | fire-breathing augmented Blackspider, thermal-grenade shock trooper (bs 1.5) | **skondu** | kandruk | Something built for a war: clipped *skon-* and a swallowed *-du*. "Thermadon" is Greek heat + Earth dinosaur suffix. |
| `RSW_PodWorm` | pod worm | large, passive glow-pod caste of the hives, wanders off (bs 4.0) | **lundoba** | ongollu | Three slow open syllables for a bs-4 body that hurts nothing; *lund-* the bulk, *-oba* the pod. |
| `JRWBeelzebufo` | (giant ambush frog; owner ruled 2026-09-10: **rename + redefine**, keep the body plan, alienise) | the biome's big sit-and-wait frog | **onggada** | dubbong | The owner asked for this rename in the roster. A croak made nasal — *ong-* from the throat, *-gada* the jump. "Beelzebufo" is an Earth fossil genus. |

**Not drafted:** `AA_Helixien` *vulloth*, `AA_DecayDrake` *mubbrak*, `AA_Slurrypede` *thollum*
— batch 3. `RSW_SiltLampreyJuv`, `RSW_RustNipperJuv` — the sea nursery, sea batch (blocked on
`TERMINALBIOMES_RM_MOD_BUILD_1`). Canon kept: the Naboo fish juveniles, Blarth, Blixus, Bogwing,
Grank, Marsh haunt, Runyip, Shiro, Vornskyr, Whisperbird, Zakkeg, Sando.

Read aloud: nunda, dunkara, ombuna, drangok, undakka, enduk, skondu, lundoba, onggada.

---

## Batch 4c — the Desert (`desert.json`, 53 rows; 15 in scope, 8 drafted here, 7 port-named CONFIRMED)

*The long shade.* The cast already speaks the batch-2 accent — vurra, skorra, zhakka, vosska,
khorrak, thurra, ommok, ossik, chikka, kudda, ulgga, vozzik, bokka — so the eight remaining
beasts join it rather than start a new one: a doubled consonant, five to seven letters, -a/-ik/-ok.

### Port-named rows — CONFIRMED, not re-drafted

Each donor row's port carries a ruled label, and each port's description is the donor's text
rewritten (MEASURED from `RSW_DesertPortMisc_Races.xml`): `AA_DesertAve` = `RSW_Sandstrider`
**ossik** · `AA_Needleroll` = `RSW_Spineroller` **kudda** · `AA_SandProwler` = `RSW_Dunestalker`
**vosska** · `AA_SandSquid` = `RSW_Sandmaw` **ommok** · `AA_MammothWorm` = `RSW_Tuskcoil` **ulgga**
· `AA_Terramorph` = `RSW_Ferroclaw` **khorrak** · `AA_Gigantelope` = `RSW_Sandhorn` **thurra**.
All seven pass `check_pseudo_sw_name.py` today (13/13 with bokka, korrum, vozzik, chikka,
skorra, vurra). When `DONOR_DEFS_PORT_TO_OURS_1` swaps the roster row to the port, the name
comes with it.

### Drafted

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `RSW_Jellypot` | jellypot | insect-jelly sac on legs, lives by hives, sits in a shadow and waits (bs 0.65) | **pommik** | tubbra | A fat little word: *pomm-* the sac, *-ik* small. "Jellypot" is two English nouns. |
| `RSW_GreatDevourer` (+ eggs) | great devourer | armoured worm that gorges on small prey to ecosystem collapse; owner's note: *"relative of the Sarlacc wandering the desert"* (bs 2.5) | **hakkro** | vollak | A mouth first: *hakk-* the gulp, *-ro* the length behind it. Kinship to the sarlacc goes in the description, never the name (rule 2). Removes a false canon read — *Great Devourer* is a named canon Gorax (`NONCANON*`). |
| `RSW_Groundrunner` | groundrunner | bear-mole chimera, rock-breaking claws, mines, docile and lazy (bs 2.0) | **dobbak** | tokkra | Blunt and heavy on the front paws: *dobb-* the dig, *-ak* the rock giving. |
| `RSW_MatureFleshbeast` | mature fleshbeast | pulsating fleshy behemoth that swallows prey whole; owner's note: *"immature sarlacc"* (bs 6.0) | **vukkoroth** | thakkuma | Three syllables for a bs-6 body, as vorrugath and ghorrumak have: *vukk-* the swallow, *-oroth* the dark it goes into. The "sarlacc" reading lives in the description. |
| `RSW_SandLion` | **vekka** (live in the def) | heavy big-cat sand-swimmer, claws-first ambush from under the dune (bs 2.0) — also Dune Sea, one name | **shakkir** | rokkasa | ⚠️ **Flag 1** — *vekka* was written by the porting agent (`1a0c8969c`, 2026-09-20), not ruled by the owner, and it is a canon character's given name (*Vekka Lodik*); batch 3 swapped three drafts for exactly that. *shakkir* is the offered swap — *sha-* sand sliding, *-kkir* the strike. If he likes *vekka*, it stands. |
| `RSW_TruffleMole` | truffle mole | fungus-sniffing sand burrower, 0.4 cells (bs 0.9) — also Dune Sea, one name | **pikkut** | sobbik | Small, quick, nose-first: *pikk-* the snout, *-ut* the burrow. "Truffle" and "mole" are both Earth words. |
| `JOE_Cephalope` | cephalope | deer-sized tentacled sand-spider-squid, venomous beak, fast, aggressive (bs 1.2) — also Dune Sea, one name | **qorrax** | zurrak | *q-* the beak, *-orr-* the tentacles dragging, *-ax* like horax and vulptex for something you do not want to meet. "Cephalope" is Greek. |
| `JOE_Landopus` | landopus | tiny bad-tempered eight-tentacle-two-arm squid, lethal neurotoxin, water defender (bs 0.15) | **ippok** | zubbit | The smallest word in the desert for the smallest killer in it: *ipp-* a pinch, *-ok* the bite. |

**Not drafted:** the seven port-named rows above; `RSW_Stoneback` *bokka* (ruled);
`FeralGrazer` — **canon**, corrected this pass. Canon kept: the 36 SWAC creatures of the roster.

Read aloud with the ruled sixteen: pommik, hakkro, dobbak, vukkoroth, shakkir, pikkut, qorrax,
ippok — the same place.

---

## Batch 4d — Dune Sea / Deep Desert (`dune_sea_deep_desert.json`, 16 rows; 8 in scope, 1 drafted here)

*Time does not pass.* One native remains unnamed; the rest are the Desert's, named there.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `AA_SpinedGow` | spined gow | cow-goat farm beast with neural spine-sails that drink heat, rich milk (bs 2.75) | **aurrok** | ohmmak | The Desert accent with one long open vowel in front of it — *au-* a sound held under the noon star, *-rrok* the plated back. "Gow" is cow + goat. |

**Not drafted:** `AA_SandLion`, `RSW_TruffleMole`, `JOE_Cephalope` — named in the Desert (one
name planet-wide). `AA_Needleroll` *kudda*, `AA_BoulderMit` *korrum*, `AA_TetraSlug` *vozzik* —
port-named. `AA_Eyeling` *ikee* — ruled. `WarWyrm` — **canon** (*Sith wyrm*), corrected this
pass. `AA_Dunealisk` — **dead def**, clade retired at `7bad94185`; the roster row is stale.
Canon kept: Gizka, Kreetle, Scurrier, Granite slug, Krayt dragon, Greater krayt dragon.

---

## Batch 4e — the Scarlands (`the_scarlands.json`, 15 rows; 12 in scope, 9 drafted here)

*A battlefield where the whole story is still legible in the ground, except who the enemy
was.* Five of these are the Isopoda hive — bioengineered "to destroy the mechanoid", still
executing fragments of a dead doctrine. The accent is voiceless and clipped, designations worn
down into names: t, k, ts, ch, x; short vowels; -t/-ak/-ix. 9 stems, 12 defs with siblings.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `RSW_FoundryBeetle` (+ `…Pupa` "foundry pupa", `…Larvae` "foundry grub", + eggs) | foundry beetle | massive-mandibled plated herbivore, crust-and-wreck-lichen browser, bred as a war bug (bs 2.4) | **takkret** · **takkret pupa** · **takkret grub** | chottak | Two hard knocks of mandible on plate: *takk-*, *-ret*. Art wave 5's *Slagmaw* is an English compound and not a ruling (rule 9). |
| `SW_Electrictick` | Electrictick | medium hive caste, runs on a discharge organ and dies when it empties; explodes — a munition with legs (bs 0.25) | **tzikket** | kitsak | The static in the name: *tz-* the crackle, *-ikket* the small quick body. |
| `SW_Electricgryllotalpa` | Electricgryllotalpa | large caste that SHOOTS focused arcs (bs 1.5) | **katchit** | tsokkat | *kat-* the aim, *-chit* the arc leaving. "Gryllotalpa" is the Latin for mole cricket; no colonist would say it. |
| `SW_Juggernautbeetles` | Juggernautbeetles | giant thick-shelled charger, discharge-organ forepaws, burning blade; rare (bs 3.0) | **kroxxat** | tarkkot | The heaviest word in the set: *krox-* the charge, *-xat* the plate. Singular — the donor label is a plural. |
| `SW_Electricfish` | Electricfish | medium, the lowest caste, gathers and works (bs 1.0) | **chekkit** | tsattik | Small and busy: *chek-*, *-kit*. The hive's worker gets the plainest word. |
| `SW_Grenadierworm` | Grenadierworm | giant caste carrying tzikket eggs, hatches and sprays them in combat (bs 2.5) | **xattuk** | tsorrak | *x-* the spray, *-attuk* the fat body it comes from. The one *x*-opening in the set for the strangest weapon. |
| `RG_Rimclaw` | rimclaw | fast, intelligent pollution-adapted iguana apex predator, toxic cloud on death (bs 1.0) | **kettix** | tsakkar | Quick and sharp, *-ix* the claw. Art wave 6's *Scarrend* is an English compound (rule 9). ⚠️ The owner knows *rimclaw* as a live word — he renamed a Weeping Stones tree away from it on 2026-09-24 (*"Tree turns to Rockfinger"*); renaming the animal frees it, and the tree stays Rockfinger. |
| `RSW_CrystalFairyMole` | crystal fairy mole | small crystal-plated-back mole, 1 cell (bs 0.86) | **pittok** | sottik | *pitt-* the small digging body, *-ok* the plate. "Fairy" is the word that must go. |
| `RSW_MegaphoridLarva` (+ `RSW_Megaphorid` adult, not rostered) | megaphorid maggot | ravenous larva that bursts out of an infected animal; the adult is a glass-cannon fly that injects its young (bs 0.32) | **tsutta maggot** · **tsutta** (adult) | oxxit | The larva keeps its plain stage word (rule 4); the adult owns the stem. *tsu-* the buzz, *-tta* the bite. |

**Not drafted:** `AA_Helixien` *vulloth*, `AA_AcanthamoebaGiganteaSmall` *lesser wollub* —
batch 3. `RSW_ShaleGorger` — a **sea beast** misfiled here (see the settled list above); sea
batch. `RSW_Korrum` *korrum*, `RUT_ScarRoach` — ours. Canon kept: Mynock.

Read aloud: takkret, tzikket, katchit, kroxxat, chekkit, xattuk, kettix, pittok, tsutta —
one hive, one accent.

---

## Batch 4f — the Rot (`the_rot.json`, 20 rows; 11 in scope of which 1 is canon, 10 drafted here)

*The planet's gut: a pale forest with a heartbeat of rot.* Eight names are ruled already and set
the accent — rennok, gromma, durrok, mullgoth, vorrugath, chittik, skerrith, grellik: liquids
and rolled *rr*, endings in -ok, -ik, -ith, -oth. 6 stems, 10 roster defs (the hornet is five).

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `RSW_PustuleHornet` · `RSW_ColonyPustuleHornet` · `RSW_PustuleHornetSpawned` · `RSW_PustuleHornetQueen` · `RSW_ColonyPustuleHornetQueen` (+ `RSW_PustuleHornetStinger` item) | pustule hornet ×3 · pustule queen ×2 | neurotoxic hive wasps that vent toxic gas when hurt; the wild, colony-loyal and hive-spawned forms; two queens, fast and dangerous (bs 0.32 / 1.0) | **zillok** (all three hornets) · **zillok queen** (both queens) · **zillok stinger** | tirrok | One species, one stem; the colony/wild/spawned split is code, not something a colonist sees (the labels are already identical). *zill-* the wing-whine, *-ok* the sting. "Pustule" is a lab word. |
| `AA_AngelMoth` (+ `AA_AngelMothLarva`, event reserve) | angel moth | clothes-eating moth, abandoned waste-disposal project; timid larva (bs 0.75) | **mollith** · **mollith larva** | yorrok | Soft as wool and just as ruined: *moll-*, *-ith*. "Angel" is an Earth word. |
| `AA_AnimaColossus` | anima colossus | six-legged, six-eyed cold-blooded colossus with anima trees on its back; trimmed for wood (bs 6.0) | **kerrugoth** | wurrogath | Three syllables for the third colossus, its own stem beside vorrugath (mycoid) and thummorak (overgrown) — kinship in the description (rule 3). *kerr-* the footfall, *-ugoth* the grove on its back. "Anima" is a RimWorld word. |
| `RSW_SmogMoth` (+ `…Larvae` "smog caterpillar", + eggs) | smog moth | large moth with faintly glowing wing-markings, luminous abdomen as a lure; owner: *"neat flier"* (bs 0.77) | **illoth** · **illoth caterpillar** | thillik | Light with no weight: *ill-* the glow, *-oth* the dark round it. "Smog" is an Earth word. |
| `RSW_Thrumbungus` (+ `RSW_ThrumbungusShroom` / `RSW_Proj_ThrumbungusShroom` items; ⚠️ `RUT_ThrumbungusShroom` weapon in RotSporeKit) | thrumbungus | gigantic gentle fungal amalgam, beautiful resistant hide; owner: *"multi-hued, surface partially digesting itself"* (bs 4.0) | **brullith** · **brullith mushroom** | sullogath | "Thrumbo" is a RimWorld word, "fungus" a Latin one; neither belongs in the galaxy. *brull-* the bulk, *-ith* the hide. The mushroom items carry the stem — including RotSporeKit's, which is a second mod's file. |
| `RSW_Yooka` | yooka | towering hunchbacked camel-llama grazer among the tall fungi, no predators, unconcerned (bs 2.1) | **yurrok** | gurrolla | **Offer, not a forced rename (rule 8):** *yooka* already passes the checker and reads coined — but it is the name of a well-known real-world game character (*Yooka-Laylee*), which is the same tell as "beelzebufo". *yurrok* keeps the *y-* he has seen and joins the Rot's -ok row. If he wants *yooka*, it stands. |

**Not drafted:** `RSW_ShiroTrap` — **canon (Legends)**, corrected this pass; keep. The eight
ruled names above. Canon kept: Snoruuk.

Read aloud with the ruled eight: zillok, mollith, kerrugoth, illoth, brullith, yurrok.

---

## Batch 4g — the Wasteland (`wasteland.json`, 15 rows; 9 in scope, 4 drafted here)

*No outlet: a just-lost sunset, flickering with wrathful lightning.* The wretched register is
already ruled — kroffa, grutt, grithe, puffmite — so the four remaining take the same dry,
fricative accent: *f*, *th*, *kh*, clipped.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `RSW_BloodletterPetrel` (+ eggs) | bloodletter petrel | small bird that drinks the blood of its prey rather than eat toxic flesh (bs 0.32) | **fithrak** | graffit | A dry little rasp: *fith-* the beak, *-rak* the bird. "Petrel" is an Earth seabird, "bloodletter" an English kenning. |
| `VAEWaste_Megatardi` | megatardi | massive slow blind six-legged tardigrade-thing, eats wastepacks, gentle pack animal, toxic cloud on death (bs 2.0) | **thuffor** | khuddoth | Slow breath through a slow body: *thuff-*, *-or*. "Tardi" is the Earth tardigrade with "mega" in front. |
| `GR_Spidercat` | spidercat | insectoid-feline hybrid, silk-hairball spit, blinding ranged attack (bs 0.85) | **khiffet** | vraffik | *kh-* the hiss, *-iff-* the spit, *-et* small. Removes a false canon read — *Spidercat* is a real Tasariq temple guardian and this is not it (`NONCANON*`). |
| `RSW_Sacapillar` (+ eggs) | sacapillar | timid larva-like bug floating on a thorax of putrescent gas, ridden as a pack animal (bs 2.4) | **thoffra** | khubbur | Air leaving something soft: *thoff-* the gas, *-ra* the float. "Sacapillar" is sac + caterpillar. |

**Not drafted:** `VFEI2_Swarmling` / `VFEI2_BlackSwarmling` *nunda* / *black nunda* and
`RSW_Screecher` *isskra*, `GR_Beetlefleet` *skibbex* — named above, one name planet-wide.
`AA_Terramorph` *khorrak* — port-named. `Toxalope` — Biotech, scope question (batch 3 flag 4).
Ruled: grutt, grithe, kroffa, puffmite. Canon kept: Borcatu.

Read aloud with the ruled four: fithrak, thuffor, khiffet, thoffra.

---

## Batch 4h — the Cracked Lands (`the_cracked_lands.json`, 12 rows; 7 in scope, 5 drafted here)

*The flood: a thin line of green hiding in the shade beside the razor's edge of barren nothing.*
The sheet's own bands name the cast — the Sealed (dormant until woken), the Spenders (flood-week
life), the Patient (the no-truce kill at the hidden water). The accent is dry then sudden:
*q*, *tt*, an open *-a* or a stopped *-aq*.

| defName | current label | the creature | drafted label | alternate | why |
|---|---|---|---|---|---|
| `RSW_MutagenicNorphea` (+ norphea eggs) | mutagenic norphea | toxin-dependent insectoid that secretes a mutagen; the Sealed — lies dormant until woken (bs 0.32) | **qattora** | **norphea** (as is, lab adjective dropped) | **Offer (rule 8):** *norphea* is a donor coinage that already passes the checker; "mutagenic" is the part no colonist says. Primary gives the Cracked accent — *qatt-* the shell cracking open, *-ora* the liquid. Alternate keeps his known word bare. |
| `RSW_SandLeaper` | sand leaper | small quick chitin-armoured rodent, flood-week life; the Spenders (bs 0.2) | **qetta** | ottiq | Two quick clicks: *qet-*, *-ta*. Small, gone before you look. |
| `RSW_Creature_Mantrap` | mantrap | giant proto-footed flytrap, spd 0.15, lure predator at the hidden water; the Patient (bs 0.77) | **saqqat** | tuqqa | The stillness and the snap in one word: *saq-* a wait, *-qat* the jaws. ⚠️ **Flag 2** — the Miasma's `AA_Mantrap` is a different creature with the same label and takes *undakka*. |
| `RSW_SandPillar` (+ eggs) | sandpillar | colossal caterpillar that stays juvenile for life yet breeds (bs 0.8); wired on `RM_FloodedCanyon` | **luttaq** | ittaqa | *lutt-* the long soft body, *-aq* the stop: something that never finishes. |
| `DA_RockTroll` | rock troll | colossal eyeless cave dweller, self-petrifying wounds as ablative armour, surfaces only if provoked (bs 4.5) | **uttaqar** | dhaqqoth | Three syllables for the biggest thing under the pans, stone in every consonant. "Troll" is an Earth folklore word. |

**Not drafted:** `AA_SandSquid` *ommok* — port-named. `AA_Murkling` *kessik* — batch 3 (crags).
Canon kept: Can-cell, Convor, Eopie, Gornt, Woolamander.

Read aloud: qattora, qetta, saqqat, luttaq, uttaqar.

---

## Flags for the owner — things a name cannot fix

1. **`RSW_SandLion` already reads *vekka* in the live def, and nobody ruled it.** The porting
   agent wrote it (`1a0c8969c`, 2026-09-20, *"Port AA_SandLion as RSW_SandLion (vekka)"*); it is
   not among batch 2's sixteen and appears on no reaction sheet. It passes the checker, but
   Wookieepedia returns *Vekka Lodik* — a character's given name — which is the collision batch 3
   swapped three drafts for. *shakkir* is offered above; *vekka* stands if he prefers it. Either
   way it needs his word, because right now it is shipping as a ruled name without a ruling.
2. **Two different defs wear the label "mantrap":** `AA_Mantrap` (Alpha Animals, bs 2.0,
   acid-spitting, the Miasma) and `RSW_Creature_Mantrap` (BMT port, bs 0.77, proto-footed, the
   Cracked Lands). They are drafted separately (*undakka* / *saqqat*). If he reads them as one
   creature, one should be cut from a roster instead — but that is a roster sitting's call.
3. **Scope questions, drafted anyway so the words exist:** the three `AM_Dryad_*` castes are
   variants of the vanilla Ideology **dryad** family — renaming three castes to *tessik* while
   every other Gauranlen dryad on the planet still says "dryad" breaks the family unless the
   base castes are patched too (a game-wide label patch, batch 3 flag 4's question). The two
   `VFEI2_*Swarmling` defs are the **juvenile stage of a framework mod's whole insectoid line**;
   renaming the juvenile alone leaves it metamorphosing into a vanilla-named megaspider. Both
   need a yes on scope before the names matter.
4. **Four rows carry an agent-invented art name that is not a ruling and fails THE STANDARD**
   (rule 9): *Scarrend* (rimclaw), *Fenshear* (raptor shrimp), *Slagmaw* (foundry beetle),
   *Verdaunt* (crested dragon) — all English compounds coined by `ART_REGEN_WAVE5/6/7` for their
   prompts, with rendered art filed under those job ids. The drafted labels supersede them; the
   ids stay as artpipe history. Nothing to decide unless he liked one of those words.
5. **The first batch's census carried three canon creatures as non-canon or uncertain** —
   shiro-trap (as `NONCANON*`), war wyrm and feral grazer (as `UNCERTAIN`). All three are Legends
   creatures whose Wookieepedia text our descriptions paraphrase (quoted in the settled list
   above). Corrected in that file's Appendix A/B in this commit; nothing else there changes.
   Two batch-3 `UNCERTAIN` rows remain: `Vapaad` (probably the Legends *Vaapad*, misspelt),
   `TetnissCrab`.
6. **Two stale roster rows:** `AA_Dunealisk` in `dune_sea_deep_desert.json` names a def the
   owner retired with the `-lisk` clade (`7bad94185`); `RSW_ShaleGorger` in `the_scarlands.json`
   is a sea beast (the opee's benthic morph) rostered on dry land. Neither is drafted; both are
   roster-sitting findings, not this item's.
7. **Two donor coinages are offered a rename rather than forced one** (rule 8): *yooka* → *yurrok*
   (a real-world game character's name), *mutagenic norphea* → *qattora* or bare *norphea*.
8. **`RUT_ThrumbungusShroom`** — the thrumbungus's mushroom is also a weapon def in a **second
   mod** (`src/RimUtinni/RotSporeKit/Defs/ThingDefs_Weapons/`). Accepting *brullith* touches
   RotSporeKit as well as SWBestiary.

## What remains — biomes not drafted in either pass

| roster | in scope | notes |
|---|---:|---|
| `the_twilight_sea` 7 · `the_grey_sea` 5 · `the_scald` 4 · Miasma nursery 2 · `RSW_ShaleGorger` | ~19 | the sea batch — one accent, after `TERMINALBIOMES_RM_MOD_BUILD_1` settles which defs exist (batch 3 flag 6) |
| `the_propane_lakes` | 4 | frostbound behemoth, frostmite, aurora sylph, sky eel (terramorph port-named, slurrypede *thollum*) |
| `arid_shrubland` | 3 | imperial toad, moss beetle, hydra (needlepost/cactipine/terrorworm port-named) |
| `the_forge` 5 · `the_pyrelands` 5 · `the_fever_wood` 4 · `the_greentide` 4 · `the_sump` 4 · `the_webwork` 3 · `the_rust_cathedral` 2 · `the_lantern_deeps` 1 · `the_blue_desert` 1 | 29 | small biomes; several now have their own September roster docs with `RM_` invented casts — check those before drafting, they may already carry names |

Planet-wide in scope after this pass: **161** distinct defs (162 less the shiro-trap
correction; war wyrm and feral grazer were UNCERTAIN and never counted); **42** roster defs
drafted in batch 3, **60** roster defs (52 stems, 104 words with alternates) drafted here,
7 + 3 port-named rows confirmed. Roughly 55 remain, 19 of them the sea batch.

## On acceptance

- Wire **label + description together** on every accepted row; rename every sibling that carries
  the stem (eggs, larvae, pupae, stinger, mushroom items — listed per row); then re-run the
  `src/` label collision sweep and `check_pseudo_sw_name.py` on the final list.
- Donor defs (`AA_`, `AM_`, `GR_`, `VFEI2_`, `SW_`, `RG_`, `DA_`, `JRW`) take a label/description
  patch in `src/RimUtinni/UtinniPatches/Patches/` on the `Ikee_Rename.xml` /
  `RotSpecies_NamesAndSizes.xml` pattern; `RSW_`/`JOE_`/`VAEWaste_` defs under `src/` are edited in
  place. When `DONOR_DEFS_PORT_TO_OURS_1` ports a donor def, the port is born with the ruled label.
- Record the rulings in this file (strike-throughs and his words), as the precedents do.
