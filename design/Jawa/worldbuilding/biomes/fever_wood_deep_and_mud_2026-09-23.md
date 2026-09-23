# The Fever Wood — the mud, the water, and the thing in it

_Owner + MACBENCH, 2026-09-23, two card rounds plus free-text. This sheet records
rulings only; the biome's definition stays in `the_fever_wood.md`._

🔴 **This sitting SUPERSEDES hard ban 1 of the frozen sheet.** See §0. Everything else
here is amendment-adds-detail under the freeze rule.

---

## 0. 🔴 Ban 1 is superseded — the thing below is now ambient, and it is NAMED

`the_fever_wood.md` §6 ban 1 reads:

> 🔴 **The deep thing is never resolved in ordinary play** — no ambient spawn, no codex
> entry, no name in player-facing text; it is built, and it emerges ONLY as the plotted
> event.

**That ban no longer holds.** The owner's rulings this sitting give the creature ambient
tentacle strikes, loot it scatters as bait, a captive specimen on display in a town, and
an explicit intent that the player *"learn the lore at last."* The sheet's own unfreeze
path is an owner ruling at a sitting recorded on the item that changes it — this is that
record.

⛔ **What must change as a consequence:** `FEVER_WOOD_MECHANICS_1`'s F4 was deliberately
built as a spawner *referenced by nothing*, specifically so ban 1 held "by construction."
That rationale is void. F4's dormancy is now a build-order fact, not a design requirement.

✅ **What survives the supersession:** the plot-reserved *full emergence* is still a
distinct, bigger event. Ambient play gets tentacles; the whole animal rising is still the
plot's to spend. Ordinary play is no longer *evidence only*, but it is still not the
whole creature.

---

## 1. The creature — ours, mapped to the dianoga

**Owner, verbatim:**

> *"I should also say we should just make up our own tentacled eldritch horror down there
> and map it to the Dianoga when Utinni is active."*

⇒ **Two layers, one creature.**

- The franchise-free tier gets **our own invented giant tentacled pool-dweller** — the
  biome's centrepiece, so the free mod is whole without Star Wars.
- When the campaign layer is active it **maps to the dianoga**. Canon reference:
  `design/RimStarWars/canon_references/dianoga/description.md`, expanded with deep
  research this same day.

**Owner, verbatim, on what it is:**

> *"It's the classic Star Wars beast that is so big it can't even enter the screen, but it
> can reach up with tentacles to lash out, grab, pull under. The 'garbage monster' from
> Star Wars (and we have such a creature in our beast list already). So this would be a
> really, really big one that you never can kill, but you can drive it off."*

> *"The Dianoga grow to unusual size in this environment... shocking even to those who know
> them."*

⇒ 🔑 **The horror is SCALE, not mystery.** The species is known and named. What is shocking
is the size. This is why §0's supersession costs nothing: naming it does not spend the
dread, because the dread was never "what is it."

🔑 **It never enters the screen.** It is not a pawn you fight. The body is off-map /
under-map forever; only tentacles are ever rendered. **Never killable — only driven off.**

### Canon that does mechanical work (all sourced, see the canon entry)

| canon fact | what it buys |
|---|---|
| **Changes colour — "black, gray, or even transparent"** | A pool that looks empty may not be. The unknown is a canon ability, not an invented hidden-state system. |
| **A humming language whose "reverberations carried so completely in the water, that language scared away all nearby prey"** | The mechanism for §3's silence ruling, and why nothing native drinks at the mirrors. |
| **Excellent hearing** | Noise near a pool calls it — thrashing in mud, gunfire, a fight. Links the mud to the beast causally. |
| **Entirely water-dependent, dries out in open air** | It can never leave, only reach. Structural reason it is undefeatable rather than merely tough. |
| **Regenerates lost limbs** | Tentacles are destructible and grow back — "drive it off" with real mechanism under it. |
| **Omnivorous, eats fish, crabs and bones** | It strips a victim to nothing, so only inedible metal and gear is left. Makes §2's loot bait physically motivated. |
| **The giant form's weak point is the EYESTALK** | The canon-attested way one was beaten. The obvious route to "drive it off." |

---

## 2. The bait — why anyone goes near the water at all

Decision taken by question card: **a slow renewing trickle** (not a depleting hoard).

**Owner, verbatim:**

> *"Definitely (2), and if you live there, you might even see a rare moment of a tentacle
> coming up and placing a new item. We should also define different sizes and maybe types
> of tentacles (act like different species, but they are all connected to the same great
> elder being)"*

And on the origin of the idea:

> *"Now we need reasons why someone would get near the pools to begin with. Perhaps it
> literally strips loot of its victims and scatters it near the pools to attract you:
> treasure to lure."*

⇒ **Three things owed here.**

1. **Gear keeps appearing at the pool margins over time** — stripped from its victims. The
   pools stay live all game, not just early.
2. ⭐ **A rare visible deposit event**: a tentacle rises and *places* an item. Seeing it is
   the moment the player understands where the treasure comes from. This is a set-piece, so
   it should be rare enough to feel like a sighting.
3. 🔑 ⭐ **Tentacles are a pseudo-bestiary.** Different **sizes** and **types**, each
   behaving like its own species, **all connected to one great elder being**. This is the
   biggest design addition of the sitting: it gives the water its own roster without ever
   rendering the animal. Canon supports the variety directly — ordinary dianoga tentacles
   are **suckered** and **membraned**, the giant form's are **barbed**.

⚠️ **The margin already had three economic draws** before this ruling — bog-timber,
potter's clay, and the seep-oils (`the_fever_wood.md` §7). The bait is a **fourth** layered
on those, not the only reason to approach.

---

## 3. Reach, and the mud that delivers you to it

Decisions taken by question card:

- **Reach scales with the pool.** A small mirror is a minor hazard; a great one is deadly
  far inland. ⇒ **Pool size reads as threat level at a glance**, and map generation can
  place both safe and lethal water. This must be *taught* to the player or it looks
  inconsistent.
- **Mud is only deadly near water.** Being stuck causes no damage by itself. The killer is
  being held within reach — of a pool, or of an arriving raid.

🔑 **The mud and the water are ONE mechanic, and it is already half-built.** For the deep
thing's strike, `FEVER_WOOD_MECHANICS_1` F1 already implemented a downed-pawn countdown
that another pawn clears by carrying them out. **Being stuck in mud is that same mechanism
with the damage removed.** So the mud costs very little new code, and it converts the water
from *forbidden* (avoidable, therefore scenery) into *lethal*.

**The ground is a three-state gradient, and the gradient is the danger curve:**

| state | behaviour |
|---|---|
| bough-shadow silt | walkable, slow, safe |
| sink-mud | can catch a pawn — immobilised until it frees itself or another pawn pulls it out |
| mirror pool | nothing enters; reach scales with size |

**Stick chance should scale with weight** — heavy things sink. ⇒ This is *why* both raiders
funnel onto the boughways and causeways, which is where the player wants them.

⚠️ **UNMEASURED engine question, Desktop only:** whether a hediff that zeroes a pawn's
Moving capacity reliably pins it mid-path without corrupting its job queue. Do not assert
this from the laptop — RimSage has never connected here.

---

## 4. The crown's cacophony, and the one thing that silences it

Decision taken by question card: **the crown goes quiet ONLY for the water.**

⇒ Silence means the thing below stirred, **and nothing else**. Not raids, not predators, not
a pawn in the mud. The rarest signal is the loudest, and it welds the birds to the biome's
one rule.

**The owner's brief for the birds:**

> *"Perhaps dramatic beautiful birds that swoop, shrill, and warble to create the typical
> 'swamp cacaphony' that replaces the eerie silence the webwork squares already
> specialize in?"*

⇒ **The crown is the LOUDEST place on the planet**, deliberately, because the Webwork next
door owns silence (`the_webwork.md` §9: *"the quietest green place on the planet"*). The two
wetlands are a matched pair of opposite sound registers.

🔑 **This closes a gap the mechanics item already identified.** `RM_MapComponent_SilenceCue`
exists in `src/RimMandrake/CreatureBehaviors/`, and `FEVER_WOOD_MECHANICS_1`'s F2 pass
recorded its one defect: *no public "hush now" entry point an unrelated event can call.* The
birds are the consumer that justifies building it.

✅ And the frozen sheet already wrote the payoff, before any of this existed —
`the_fever_wood.md` §9: *"crown-life constant and easy; ground-level none — then a ripple,
and everything above goes silent to watch."*

**Owed:** several birds with *distinct call registers* — swoopers, shrillers, warblers — so
the chorus is layered and its collapse is legible rather than a single sound switching off.
Canon injection candidates already built and homeless: `RSW_CanCell`, `RSW_Neebray`,
`RSW_Porg`, `RSW_Sacapillar`, `RSW_Mynock`.

---

## 5. The two-front war — lures, and staggered arrival

**Owner, verbatim:**

> *"I like buildable lures. Both enemies like helpless prey chained down and wounded. Spares
> you... but using one before they come also increases the likelihood that one or both
> comes. And if only one comes, that's not so good... they might look around. Shouldn't both
> come precisely at the same time. One comes, there's tension, then maybe the other arrives
> too."*

⇒ **The lure is a gamble, and that is the whole mechanic.**

| element | ruling |
|---|---|
| what a lure IS | **helpless prey, chained down and wounded** — both raiders want it |
| what it buys | it **spares you** — the raiders go for the bait instead of your colony |
| what it costs | building one **raises the chance a raid comes at all** |
| the failure case | ⚠️ **if only ONE arrives, that is bad** — it finishes the bait and *"they might look around"* |
| 🔴 timing | ⛔ **they must NOT arrive at precisely the same time.** One comes → tension → *maybe* the other arrives too |

🔑 **The staggered arrival is the design.** A simultaneous double-arrival is a spectacle you
watch; a staggered one is a wager you are living inside — you are hoping the second column
shows up, which is a genuinely novel thing to want during a raid.

✅ **Already built and sufficient:** `permanentEnemy` on both factions makes them hostile to
everyone *including each other* — one bool each, verified against the decompile in
`FEVER_WOOD_MECHANICS_1` F9. What is missing is the **paired staggered arrival event** and
the **lure building**.

⚠️ The sheet already names the player-side trick this serves (`the_fever_wood.md` §7b):
*"when both come at once, open the gates between them and stand back."*

---

## 6. The sap-drinker guild — one behaviour, many refusals

**Owner's brief:**

> *"Perhaps more creatures that sit and drink sugary sap and resist being bothered via
> various defenses?"*

⇒ A **guild**, not a creature. Every member shares *clamped to bark, drinks sap, does not
flee*; they differ only in **how they refuse to be bothered**. The thornbug
(`the_fever_wood.md` §4) is the existing member and its refusal is the nectar contract —
hard ban 6, *never yields under fear*.

Proposed siblings, each a different way the nectar economy can break — **not yet ruled**:

| refusal | the creature |
|---|---|
| camouflage + spines | the thornbug: looks like a thorn, yields only while calm |
| armour it makes itself | seals into hardened sap; must be cracked; drops a real material |
| defence by proxy | a **screamer** — sets the whole chorus off, pulling the crown's predators toward the disturbance |
| ⭐ defence by suicide | **releases its grip and drops into the pool** rather than be taken — which answers *why anything lives down there* |
| defence by inflation | swells so it cannot be pulled off; burst it for a one-time payout that kills a renewable source |
| chemical | sprays an irritant that sours the whole herd's yield for days |

🔑 **The ants steal them ALIVE** (§4, theft not slaughter), so a well-defended species is one
the ants *cannot take*. ⇒ Species placement becomes a real perimeter decision.

---

## 7. What this sitting did NOT settle

- **The flora roster.** The Fever Wood still carries **7 donor plant rows** (5 Alpha
  Biomes, 3 genuine canon Star Wars), one openly flagged as an *"interim single-tile body
  for the tower-trunks."* The owner's standing instruction is to invent our own complete
  roster first and inject Star Wars opportunistically — so these 7 are placeholders to
  replace, not a base to extend.
- ⚠️ **There is no living giant tree def at all.** `RUT_FeverTrunkHeartwood` and
  `RUT_FeverTrunkCore` exist as the mineable blob and its bookkeeping marker, but **no
  growing, fellable tree** — no equivalent of `RM_Greatbole`. The towers are currently a
  single-tile donor shrub.
- **The full fauna roster** beyond the guild and the birds.
- **Free-tier naming** for our own eldritch horror, its tentacle types, and the guild.
- 🔑 **Which tentacle types exist**, and how each behaves. §2's ruling establishes that they
  are a pseudo-bestiary; it does not enumerate them.

---

## Cross-references

- `the_fever_wood.md` — the frozen definition sheet. §0 above supersedes its ban 1.
- `design/RimStarWars/canon_references/dianoga/description.md` — the canon target, expanded
  2026-09-23 with the giant form, the eyestalk weak point, the product line, and an explicit
  note that **"lavender" is unsourced**.
- `kits/fever_wood_kit_spec.md` + `FEVER_WOOD_MECHANICS_1` — F1 supplies the rescue-window
  mechanism §3 reuses; F2 names the silence-cue gap §4 closes; F9 supplies the mutual
  hostility §5 builds on; F4's dormancy rationale is voided by §0.
- `the_webwork.md` — the silence this biome's cacophony is written against.
