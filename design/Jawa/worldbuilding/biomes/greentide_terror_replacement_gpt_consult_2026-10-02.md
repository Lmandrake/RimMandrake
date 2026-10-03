SUBJECT: Greentide lunger — Vurrak candidates

**I recommend the Vurrak as a buckling bank-wedge:** the ground takes someone’s weight, folds upward, and runs after them on three unequal supports. That gives the accepted card a clear creature reveal and avoids both adjacent seizure and deep-water invisibility.

The references below inform the fear design; their anatomy does not carry into Greentide.

| Creature / source | Why it terrifies |
|---|---|
| **Mime — Alpha Animals** | Familiar company becomes suspect; excessive appetite offers a clue before the disguised colonist reveals its predatory nature. [Bestiary](https://rimworldbestiary.wiki.gg/wiki/Mime) |
| **Sightstealer — RimWorld: Anomaly** | Howls announce an unseen approach; knowing something is coming does not reveal where the attack will start. [Wiki](https://rimworldwiki.com/wiki/Sightstealer) |
| **Revenant — Anomaly** | Repeated invisible visits turn casualties into an accumulating deadline; tracking its traces gradually reverses the hunt. [Wiki](https://rimworldwiki.com/wiki/Revenant) |
| **Devourer — Anomaly** | Its leap and consumption remove a pawn from the fighting line, making rescue an immediate priority. [Wiki](https://rimworldwiki.com/wiki/Devourer) |
| **Metalhorror — Anomaly** | Concealed infection makes ordinary colony relationships uncertain; discovery can precipitate a collective emergence. [Wiki](https://rimworldwiki.com/wiki/Metalhorror) |
| **Sand Shark — Subnautica** | A small exposed fin betrays a predator concealed beneath apparently ordinary sand; disturbance converts scenery into motion. [Developer description](https://unknownworlds.com/en/news/subnautica-dev-update-5-lurking-darkness) |
| **Depths Worm — Don’t Starve** | A harvestable-looking lure weaponizes routine gathering; harvesting or lingering nearby brings the hidden body up. [Wiki](https://dontstarve.wiki.gg/wiki/Depths_Worm) |
| **White Lizard — Rain World** | Background camouflage conceals a living obstruction; visible eyes, mouth and anticipatory saliva reward careful observation. [Creature reference](https://rain-world-archive.fandom.com/wiki/White_Lizard) |

All eight are verified examples; none needs an **UNSURE** existence flag. The explanations of terror are my design interpretations.

For all five candidates, preserve **perfect quiescent disguise**. The fair tell starts when weight first lands, before damage. A permanent glowing seam would weaken the accepted card.

Use these shared rules:

- Natural, walkable bank cells adjoining river water are eligible. Deep water remains dangerous through the existing roster; evading a Vurrak into it is no safe escape.
- Contact produces a conspicuous deformation, sound and threat notification. Initial tuning: **90 ticks before the strike**, with an optional pause on first hostile reveal.
- The opener attacks a location fixed during the warning. Moving clear can cause a miss; it cannot silently retarget during launch.
- Afterward, the animal remains visible through combat and relocation. It eats, sleeps, bleeds, limps and leaves a recognizable corpse. Damage breaks disguise.
- Trigger eligibility includes colonists, visitors, raiders and other animals. No faction exemption or predator truce.
- Each is an **alternative realization of one species**, with Greentide commonality around **0.15**.

**1. Vurrak — buckling bank-wedge**

**Silhouette, palette, bodySize:** An asymmetric solid wedge with a high rear keel, three unequal buttress legs and a biting cleft beneath one shoulder. Petrol-violet hide, turquoise cartilage, chalk-pink teeth; exposed colours appear when its silt coating splits. **1.35.**

**Loop:** Flattens its keel and shoulders into a convincing bank shelf → a pawn entering its central pressure cell buckles the dorsal plate → it rears, pitches forward and bites at the marked cell → pursues briefly on its visibly uneven gait, feeds, then walks elsewhere to settle.

**Tell:** The “bank” rises beneath the pawn; three support joints unfold and the mouth becomes visible throughout the warning.

**Counterplay:** Draft and step inland immediately; shoot during the committed lunge or recovery. Restrict routine hauling away from unsurveyed banks.

**One mechanism:** New **bank-contact mode** feeding the existing `RM_CompAquaticAmbusher` lunge logic, if extractable. Replace its deep-water concealment predicate and rendering with a silt disguise; retain strike/cooldown handling.

**Risk:** A flat closed/open graphic could read as a pressure trap. The raised keel, locomotion and continued predation must appear immediately. Avoid a paired shell silhouette.

**2. Rellock — walking terrace**

**Silhouette, palette, bodySize:** Four thick body tiers compressed around an offset biting head, carried by two broad, unequal pedestal feet. Expanded, it looks like a leaning stack with a protruding shoulder rather than a long segmented animal. Aubergine skin, pale cyan joints, mauve tooth sockets. **1.65.**

**Loop:** Compresses into two adjoining silt terraces → loading the first terrace makes it compress; crossing onto the second releases its braced posture → tiers telescope upward and the whole animal lunges across the crossing → remains tall and awkward, takes several slow pursuit steps, then retreats visibly.

**Tell:** The first terrace sinks while the second rises. A broad jaw protrudes before release; neither cell deals immediate damage.

**Counterplay:** Reverse off the first terrace rather than continue across it; engage the exposed animal from inland.

**One mechanism:** New **ordered two-cell contact mode**, reusing aquatic lunge resolution. First contact arms a short crossing window; second contact commits the attack.

**Risk:** Highest danger of resembling a collapsible structure. No isolated spikes, detached tiles or instantaneous resetting. Its compressed proportions must avoid a burrowing-worm read.

**3. Urr el — rolling bank-knot**

**Silhouette, palette, bodySize:** Two rigid, unequal body hoops interlock around a muscular central bite block. No tail or projecting limbs; movement alternately loads the two hoops. Indigo outer surfaces, mint-white inner surfaces, plum musculature. **1.2.** Working spelling: **Urrel**.

**Loop:** Lies sideways, packed with silt so both hoops form one rounded bank hummock → weight entering across its water-facing rim rolls that rim inward → rotates upright and lunges two cells inland → overshoots, rights itself slowly, then pursues by alternating rolls.

**Tell:** A crescent of pale inner anatomy rotates into view; the hummock shifts sideways beneath the walker.

**Counterplay:** Retreat sideways from the marked inland attack line. Its recovery exposes the central musculature to gunfire.

**One mechanism:** New **direction-sensitive bank-contact mode**: compare the entering pawn’s previous cell with the disguised rim, then reuse the aquatic lunge along a fixed line.

**Risk:** Could become an animated wheel or resemble a coiled serpent. Keep both hoops thick, rigid, unequal and inseparable from the fleshy bite block. Avoid making movement a dune-style rolling pursuit marathon.

**4. Sammeth — load-drinking saddle**

**Silhouette, palette, bodySize:** A hollow, arched trunk spanning two stout lateral legs; a short vertical jaw hangs beneath the arch. Its upper back expands sideways into a load-bearing cushion. Wine-purple hide, opaque jade cushion, blue-white mouth lining. **1.5.**

**Loop:** Settles its cushion into a low bank shelf → sustained weight compresses fluid into its legs → the cushion visibly deflates and the arch lifts → both legs propel the body into a short upward-forward bite → remains standing, bites normally, then relocates.

**Tell:** Contact immediately exposes the mouth beneath a rising arch. The strike requires **120 ticks of continuous loading**; leaving releases the charge.

**Counterplay:** Keep moving after contact; never stop to shoot while standing on it. Fight from cleared inland ground.

**One mechanism:** New **continuous-load timer mode**, with the aquatic lunge fired only after uninterrupted occupancy.

**Risk:** Waiting for someone to stop could echo shiro’s sit-and-wait role. Its defining event must be compression of a living bank shelf, not merely proximity. The arch must rise into locomotion rather than close around and hold prey.

**5. Emmock — weighted silt crown**

**Silhouette, palette, bodySize:** Three unequal solid body lobes meet around an off-centre torso and lateral mouth. Each lobe is rigid and blunt; it walks by lifting and planting whole lobes. Bruise-blue exterior, lavender joint folds, acid-green oral ridges. **1.85.**

**Loop:** Spreads its lobes into a broad silt fan → any contact reveals flexing joints, but heavier loading bends its central latch → one lobe plants and the entire body pivots into a biting lunge → stays upright, advances in deliberate three-beat steps, feeds and resettles.

**Tell:** A loud joint crack and full anatomical reveal precede the attack. Light animals can expose it without releasing the latch.

**Counterplay:** Exploit its visible, slow recovery; use encounters with small wildlife to locate exposed individuals. Do not assume a previously crossed patch was harmless.

**One mechanism:** New **load-threshold mode**, approximating weight with triggering pawn `BodySize`—initial threshold **0.6**—then reusing aquatic lunge resolution.

**Risk:** Hidden size rules can feel arbitrary. Explain the threshold behaviour in its description. Flexible lobes would approach tentacles or slime; keep them rigid, articulated and visibly weight-bearing.

For a **RimWorld 1.6 implementation**, I would make one proposed `RM_CompBankAmbusher` with configurable contact modes. The existing comps were described in the prompt; their source is unavailable here, so reuse is conditional. Borrow lunge handling from AquaticAmbusher and conceal/reveal state handling from FalseShadeAmbusher where practical. None should inherit the mirrak’s shadow, adjacent seizure or 1.2 capture limit.

Keep each animal a normal pawn. A larger drawing needs explicitly registered pressure cells; `bodySize` should not be treated as a multi-cell footprint. Render a terrain-matched covering without changing actual terrain, and keep hidden labels, selection and search behaviour consistent with concealment. Save warning state, target cell and cooldown. Salinity can influence distribution later without adding a new combat system.

Ranks below use **1 = best**, including lowest build cost. Cost includes art and trigger handling.

| Candidate | Terror | Fairness / readability | Build cost | Distinct from mirrak | Distinct from dhollock |
|---|---:|---:|---:|---:|---:|
| **Vurrak** | 2 | 1 | 1 | 3 | 2 |
| **Rellock** | 1 | 3 | 4 | 2 | 1 |
| **Urrel** | 3 | 4 | 3 | 1 | 3 |
| **Sammeth** | 4 | 2 | 2 | 4 | 4 |
| **Emmock** | 5 | 5 | 5 | 5 | 5 |

**Choose Vurrak for production.** Rellock delivers the strongest “the shoreline stood up” moment, but needs more animation and contact logic. Vurrak achieves that fear with one pressure cell, a readable escape window and a body that immediately proves it is an animal.