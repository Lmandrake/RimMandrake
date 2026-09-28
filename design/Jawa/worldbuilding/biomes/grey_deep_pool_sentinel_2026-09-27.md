# The Grey Deep pool sentinel — the orruhmu (2026-09-27)

Status: DESIGN DRAFT — written by a DESIGN subagent for BENCH, unblocking
`GREYSEA_RULED_CONTENT_1` §9. The ruling this executes (Q13, question card,
2026-09-27, recorded on `GREYSEA_FLOOR_PASS_1`): **ONE new solitary species,
haunts brine-pool shores, squirts the crystallising protein shower when
crowded.** The owner's original sentence (sheet §4d, verbatim): *"Brine pools
and the creatures near them have a unique defence: they squirt out a protein
shower causing ultra-rapid crystallisation."*

Sources read, not remembered: `the_grey_deep.md` (frozen sheet; §6 bans),
`grey_deep_sitting_agenda_2026-09-27.md` (Q13 framing + §3 ruled inputs),
`the_grey_deep_danger_floor_pass_2026-09-27.md`,
`infrastructure/state/items/GREYSEA_RULED_CONTENT_1.md`, and the live source:
`src/RimMandrake/DivingInteraction/Source/RM_BrineEncasement.cs`,
`MapComponent_BrineCrystallisation.cs`,
`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml`,
`RM_GreySeaFauna.xml`, `RM_GreySeaFloorLife.xml`.

Laws honoured throughout, never re-argued: the danger philosophy is **the
place kills, the animals mostly don't** — this creature is the ruled exception
alongside the haarn; ban 4 (**no glow** — no light tell anywhere in this
design); solitary everything (ban 2); never a tomb (the encased are mined out,
wide rescue window); ban 6 (no vanilla-Earth organism by name or read).

## 1. Identity

**The orruhmu** (`RM_Orruhmu`) — a squat, urn-shaped bellows-sac that stations
itself on brine-pool shores and is, until it moves, one more salt dome. Body
plan: a low rounded mantle crusted in the same white jacket mineral as the
statuary, cauliflower-textured and marred like everything mineral in the Grey;
beneath the crust, a soft grey bellows body on a ring of short shuffling pads;
at the crown, a puckered white spout — the only tell that this dome breathes.
It shuffles a few cells a day between stations at a pool's lip, drinks from
the super-brine (the pool is both its larder and its ammunition), and waits.
It is patient the way the whole biome is patient: it does not hunt, does not
flee, does not care about you — until you crowd it.

**Why it belongs to the Grey's register.** Mineral mimicry is the floor's
house style — the giant pretends to be a pillar, the haarn pretends to be a
helmet, the sallik pretends to be a pebble — and the orruhmu pretends to be a
salt dome, completing the set at the one station nothing else guards. It is
grey-on-grey (white crust over grey flesh, no colour anywhere), solitary
(`wildGroupSize 1`, rare), and slow. And its defence enforces the biome's own
law on the player: **the Grey is a sea of solitary things, and the orruhmu
punishes company.** One pawn at a pool shore is a harvester; two are a crowd.

**bodySize 0.6** — bigger than the haarn (0.4), well under the fessk (0.9):
at RimWorld zoom it reads as a knee-high dome, exactly salt-dome-sized, which
is the point. The player's first orruhmu is discovered, not spotted.

**Catchable? No — floor resident only, no `*Catch` twin.** Argued both ways:
the every-fishable-lives rule runs one direction — everything you can PULL OUT
must also live below — and does not oblige the converse; the anchors
(reefback, fessk) already stand as floor-only precedent. For catchability: a
thirteenth-plus catch row would be free variety. Against, and decisive: the
orruhmu is not in the water column — it is a shore-walker at the pool lips of
the floor pocket map, no more fishable from the surface shore than a pillar
is; and a creature whose organ is a crystallising weapon, hauled up on a
line, invites exactly the "harvest the squirt" economy that Q7 just refused
for the anti-crystal sprig (pure dressing, no product). The sea is not
negotiated with; neither is its sentinel. Floor-only.

## 2. The squirt

**The mechanism is the existing one, reused — no second engine.** The Grey's
crystallisation already has one consequence and two triggers, live in
`src/RimMandrake/DivingInteraction/Source/`: standing on pool terrain
(certain) and standing in a chimney plume (a roll per sweep), both handled by
`MapComponent_BrineCrystallisation`, both resolving into
**`RM_Building_BrineEncasement.TryEncase()`** — the mineable jacket thing
(def `RM_BrineEncasement`) that holds the pawn, ticks the `RM_Smothered`
timer, and ejects on mine-out. The squirt is the **third trigger on that same
consequence.** Build shape: lift the private
`MapComponent_BrineCrystallisation.Encase(Pawn, ThingDef)` into a small shared
static (`BrineEncasementUtility.Encase(Pawn)` — clear the cell's edifice, make
the jacket, `TryEncase`, spawn, message), call it from both the map component
and the orruhmu's one new comp, `RM_CompPoolSentinelSquirt` (a `ThingComp` on
the race def). The only new C# is the trigger; the encasement, the smother
clock, the rescue, the message and the Scribe are all the shipped code.

**Trigger — crowded, deterministically.** Every rare tick (250 ticks) the
comp counts spawned humanlike and mechanoid pawns within **5 cells**
(animals never count and are never sprayed — the same deliberate scope as the
shipped map component). The rule, no rolls anywhere:

- **0–1 pawns in range: nothing, ever.** A lone harvester can work beside a
  orruhmu all day. The counterplay is the biome's own law: come alone.
- **2 or more: the orruhmu swells.** One full rare tick of visible tell — the
  bellows inflates, the crust plates lift, a wet pressurising hiss (sound +
  swollen graphic/overlay + inspect line "swelling", **no light, no glow** —
  the tell is silhouette and sound, readable in murk at 5 cells because it is
  IN the 5 cells). If the crowd disperses below 2 before the next rare tick,
  it subsides: backing off during the swell always cancels, the same
  walk-out beat the chimney plume teaches.
- **Still crowded after the swell: it squirts** — a white protein jet at the
  **nearest** intruder in range, who is encased on the spot: the standard
  `RM_BrineEncasement` jacket, mined out by friends, smother timer at the
  shipped wide-rescue rate. One pawn per squirt, never an area wipe.

**Cooldown: 15,000 ticks (6 in-game hours).** A spent orruhmu is flat, its
crust dull (inspect line "spent"), and it shuffles to the pool lip to drink —
the pool refills its ammunition, which is why it never strays from the shores.
While spent it is just a strange dome; a second squirt needs a second visit's
worth of patience from it.

**What it does NOT do — the negative space is ruled:**

- **Never a tomb.** The jacket is the ruled encasement — mined out, wide
  smother window ("a rescue you have time to mount"), no decay of the
  encased (ban 5), eject-alive on mine.
- **No light tell, no glow** (ban 4) — the swell is shape and sound only;
  the spray is white matter, not luminance.
- **It never hunts.** No manhunter, no pursuit, no melee worth the name; the
  squirt has 5 cells of reach and the orruhmu does not chase what leaves them.
- **It never sprays animals** and is never itself encased (native chemistry);
  it walks pool-lip cells unharmed, which is its whole niche.
- **No harvest of the mechanism.** No gland item, no crystallising weapon
  from the corpse — the Q7 ruling's spirit (the sea is not negotiated with)
  covers its sentinel. Butchers to ordinary meat and a little salt crystal.

## 3. Stats sketch

Calibrated against the shipped Grey cast (fessk bodySize 0.9 / haarn 0.4 /
floor life 0.08–0.4; nothing on this floor is fast):

| field | value | why |
|---|---|---|
| bodySize | 0.6 | dome-sized; between haarn and fessk |
| baseHealthScale | 1.1 | crusted — the toughest small thing on the floor |
| MoveSpeed | 0.7 | a shuffle; it guards, it does not travel |
| Wildness | 1.0 | never tamed — a tamed encaser is a weapon, and the Grey tames nothing |
| foodType | VegetarianRoughAnimal (the hessal's filter-feeder read) | it drinks the pool; hungerRate 0.1 |
| lifeExpectancy | 120 | sentinel-patient, elder-adjacent |
| predator | false | it guards, it doesn't hunt |
| manhunterOnDamageChance | 0 | its whole offence is the squirt; wounded, it just subsides |
| tools | one blunt "mantle shove", power 4 | token melee so the job graph is legal, never a threat |
| combatPower | 45 | the squirt priced in, so raid-point math respects it |
| wildGroupSize | 1 | solitary everything |
| commonality | 0.05 in `<wildAnimals>` | rumour-rare, like the corrik; roughly one per floor, found at a pool |

## 4. Name

🔴 **RULED 2026-09-27: the shipping name is ORRUHMU (`RM_Orruhmu`) — the owner's own
typed coinage on the ratification card**, a variant of the drafted "orruhm". Evidence
for the exact string: 0 src/dump hits (inherited — any "Orruhmu" hit would contain
"Orruhm", which measured 0) and Wookieepedia search 0 hits (sanity probe dianoga=10,
same call). The candidate table below is the record of what was offered.

Register: the Grey cast is short invented words with doubled letters —
fessk, haarn, oomal, immu, maalu, nissik, grusk, sorruth, essarn, otheska,
corrik, thollim, sallik, karrud, hessal (read live from `RM_GreySea.xml`
`<wildAnimals>`). All three candidates follow it; all three were proven
available on both instruments, with sanity probes proving each instrument
could see.

**Instrument 1 — collision grep** over `src/` (recursive, case-insensitive)
and the live def dump (`DefDump/defs.sqlite`, 79,062 defs, `def_name`+`label`
LIKE match). Probes: `Fessk` → 16 src hits / 5 dump defs; `Haarn` → 32 / 2;
`Korrum` → 5 dump defs. The instrument sees.
**Instrument 2 — Wookieepedia search API**
(`action=query&list=search&srsearch=<name>`), never a guessed exact title.
Probe: `dianoga` → 3 hits (Dianoga, Dianoga/Legends, …). The instrument sees.

| candidate | src grep | def dump | Wookieepedia search | verdict |
|---|---|---|---|---|
| **Orruhmu** (recommended) | 0 | 0 | `search: []` — 0 hits | CLEAN |
| Tessum (alternate) | 0 | 0 | `search: []` — 0 hits | CLEAN |
| Orruhm (alternate) | 0 | 0 | `search: []` — 0 hits | CLEAN |

(A fourth candidate, Ollusk, was dropped on 5 `src/` hits before the canon
check.) `design/` was also swept for all three: 0 files. **Shipping name: the orruhmu, `RM_Orruhmu`** — the doubled r and round
-uhmu sit beside oomal/immu/maalu, and it says nothing in any language we
could find.

## 5. Art brief

One row for `infrastructure/artpipe/art_lists/`, exact column format of
`stillsand_roster_fillout.csv` (id, rimflow_item_id, prompt, canvas_w,
canvas_h, reference, facings, style_notes, priority, background, channel).
Per the daemon's rule the prompt contains no camera or view-direction words —
surface and creature only.

```csv
id,rimflow_item_id,prompt,canvas_w,canvas_h,reference,facings,style_notes,priority,background,channel
RM_Orruhmu,GREYSEA_RULED_CONTENT_1,"RimWorld game animal sprite: the orruhmu, a squat urn-shaped bellows creature disguised as a salt dome — a low rounded mantle armoured in knobbly white salt crust, cauliflower-textured and slightly chipped and clouded, over soft grey flesh just visible at the seams, a ring of short stubby pads beneath, and a small puckered pale spout at the crown. It should read as a mineral formation first and an animal second. No nameable Earth animal.",256,256,,"south,east,north","pool-shore sentinel, bs~0.6; the read is a salt dome that is secretly breathing; grey-on-grey murk register: bone and salt whites over grey flesh, dim directionless grey-green gloom, no glow, no luminance, crust marred and never perfect; painterly vanilla-RimWorld animal art style",70,transparent,codex
```

## 6. Def wiring notes

- **Race + kind land in the RM-tier Grey fauna file**:
  `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_GreySeaFauna.xml`
  (the anchor-cast file — ThingDef + PawnKindDef pair, per the fessk's shape
  in that file).
- **Roster wiring** in
  `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml`
  `<wildAnimals>` uses the **shorthand element form** — `BiomeAnimalRecord`'s
  custom loader reads node NAME as animal, node TEXT as commonality:
  `<RM_Orruhmu>0.05</RM_Orruhmu>`. **Never `<li>`** — a `<li>` row is silently
  dropped and can discard the def.
- **`animalDensity` must stay > 0** or the orruhmu (and the whole roster) is
  dead content — `RM_GreySea` already sets `animalDensity 0.1` (verified
  live this pass), so nothing to change, only nothing to break.
- **The comp class goes in DivingInteraction**, beside the encasement engine
  it calls: `src/RimMandrake/DivingInteraction/Source/` gains
  `RM_CompPoolSentinelSquirt.cs` (+ the small `BrineEncasementUtility`
  refactor of `MapComponent_BrineCrystallisation.Encase`). The
  TerminalBiomes→DivingInteraction reference is the established pattern —
  `RM_BrineElder.xml`'s `thingClass` already crosses it, and
  `mandrake.rm.divinginteraction` is a HARD dependency in TerminalBiomes'
  About.xml — so the race def may name the comp class directly.
- ⚠️ `RM_DivingInteraction`'s csproj sets `EnableDefaultCompileItems false`
  and lists every file: **each new .cs is a two-file change** (`<Compile
  Include>` line or it compiles into nothing, with no error).
- The comp attaches to an ANIMAL pawn, so plain `CompTickRare` is correct —
  the Plant `CompTickLong` trap does not apply here.
- One Mod Settings toggle rides the existing `RM_DivingSettings` block
  (`greyPoolDefenceEnabled` gates the pools; the sentinel gets its own
  `greyPoolSentinelEnabled`, default on) — per the every-mod settings rule.
