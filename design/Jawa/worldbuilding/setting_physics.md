<!-- status: live -->
# setting_physics.md — the physical laws of this universe

_Started 2026-08-10. The constitution the balance work derives from.
Companion to `balance_paradigm.md` (why we change values) and `concept.md`
(the pillars)._

**Why this document exists.** Without settled physical law, every def is a fresh
argument and the world drifts into mush. With it, most balance questions stop
being opinions and become **derivations**. When someone asks "how much damage
should the ion carbine do to a battle droid", the answer should be lookup-able
here, not negotiated.

**Discipline:** these are *our* laws. Where Star Wars canon is useful we take it;
where canon is vague or inconvenient we decide, write it down, and stay
consistent. Consistency beats fidelity.

---

## Part 1 — The forms of harm

Seven ways a thing can be hurt. Every weapon, creature and hazard in the game
delivers one or more of these, and every defence resists one or more.

| form | delivers | archetype |
|---|---|---|
| **Kinetic** | momentum into mass | slugthrower, claw, falling rock, impact |
| **Thermal** | energy into surface | blaster bolt, flamethrower, star |
| **Cutting-plasma** | sustained melt along a line | lightsaber, plasma torch |
| **Ionic** | charge into circuitry | ion gun, EMP, storm |
| **Neural** | shock into nervous system | stun blaster, venom, sonic |
| **Chemical** | reaction into material | acid, corrosion, toxin |
| **Gravitic** | displacement of mass | tractor beam, repulsor, shockwave |

**The central claim: no single form is universally best.** Every one is decisive
somewhere and useless somewhere else. That is the engine of the whole design —
it is what makes loadout a decision, what stops power inflation, and what makes
new weapons interesting without making them stronger.

---

## Part 2 — The laws

### L1 — Energy trades penetration for heat

A blaster bolt is contained plasma. It dumps its energy **at the surface** it
strikes.

- Against flesh: catastrophic. Flash-boiling tissue, cauterised wounds, and the
  reason a torso hit ends a person.
- Against thick refractory mass: it **ablates** — it burns off a layer and stops.
  Ten bolts into a hull scar it; they do not breach it.

**Derives:** blasters are supreme anti-personnel and poor anti-material. Your
1–2 shot lethality contract against unarmoured targets is a *physical
consequence*, not a tuning choice.

### L2 — Kinetic trades heat for penetration

A slug carries momentum, not energy. It defeats by punching through.

- Beats armour optimised against energy — ablative plating does little against a
  hypersonic mass.
- Costs: weight, recoil, ammunition logistics, noise. It is the crude, reliable,
  unglamorous answer.

**Derives:** slugthrowers stay relevant forever as the counter to energy-armour,
which keeps a whole weapon family alive without power creep. They are the
"peasant's answer to a knight", and that is a good story.

### L3 — A lightsaber cuts by melting, and melting takes time

**This is the load-bearing law.** The blade parts matter by melting a line
through it. The limit is not hardness — it is **how much mass sits in the way**
and **how long the blade stays in contact**.

- **Anything a person can wear is defeated instantly.** Personal armour is thin
  by necessity; a human must carry it. There is no wearable plate that stops a
  lightsaber.
- **Vehicle-grade plating resists.** A tank's flank is too much mass to melt
  through in the half-second of a swing. A lightsaber-armed duellist can *stall*
  a walker, not kill one.
- **Cutting a bulkhead is a task, not an attack.** Seconds to minutes, standing
  still, vulnerable. It is an infiltration verb, not a combat verb.
- **And it is a bomb.** A lightsaber holds more energy in less containment than
  anything else a person carries; when it fails it goes off spectacularly. See
  **L17a** — this is why duels happen over reactor shafts, and why an intact
  recovered blade is a prize.

**Derives, and this is why the law matters:**
- Lightsabers are supreme against people and near-useless against armour —
  so **they never become the universal answer**, and vehicles get a reason to
  exist. Melee gods are checked by machinery rather than by arbitrary caps.
- The counter to a Jedi is a *vehicle*, a *ranged line*, or numbers — not a
  better sword. That is a much better set of scenes.

### L4 — Ion disrupts; it does not destroy

Ionic damage floods circuitry with charge.

- **Zero damage to flesh.** An ion bolt through a person is a warm breeze.
- **Decisive against droids, vehicles, turrets, powered armour and shields** —
  it disables rather than destroys, which means it *captures* rather than kills.

🔴 **L4 IS AMENDED — IT IS NOT LITERAL, AND THE OWNER'S LOCKED SPEC D1 GOVERNS.**
_DECIDE, 2026-08-22, closing `ION_CAPTURES_PEOPLE_NOT_DROIDS_1`. **This entry reversed an
earlier ruling of my own from the same day**, which read L4 literally and declared the ion
blaster droids-only. That was wrong: it contradicted an owner decision I had not read._

⛔ **"Zero damage to flesh… a warm breeze" is superseded.** The owner locked the weapon's
behaviour on **2026-08-08**, `design/Jawa/mods/required_mods.md` → **LOCKED SPEC D1**:

> *"SINGLE-TARGET STUN GUN with **tiered effect by target class**… **strongest vs pure
> machines/mechanoids, strong vs droids & vehicles, weakest vs flesh people** (but still
> capable of eventually dropping a person with sustained/stacked fire). **This tiering IS
> the tactical identity** — you can nearly one-shot-disable a mech but must gang up + use
> terrain to take a healthy raider alive."*

and reaffirmed it the same day against the Outer Rim alternative: *"still BUILD OUR OWN,
keep the locked spec… only a bespoke def gives industrial-tier + buildable-from-start +
**capture-on-flesh** + self-contained all at once."*

⇒ **Ion is a GRADIENT, not a switch.** Read L4's second bullet as the *top* of that
gradient, not as the whole of it. Flesh is the weakest tier — slow, needing stacked fire and
terrain — **not exempt.**

### 🔴 The real defect: the top tier does not exist
**Measured live 2026-08-22** (`infrastructure/state/observed/2026-08-22/ion_buildup/`):

| target | applied | result |
|---|---|---|
| `Tribal_Warrior` | `JawaIon_Damage` ×6 @ 8 | downed, **alive, zero injury hediffs, no blood** — ✅ **D1's weakest tier, working exactly as specified** |
| `Mech_Scyther` | `JawaIon_Damage` ×13, up to @ 20 | **nothing.** `stunned=False`, `stunTicks=0`, no hediff |
| `Mech_Scyther` (control) | vanilla `EMP` ×1 @ 20 | `stunned=True`, 570 ticks |

⇒ **The weapon is not inverted and it is not backwards. It implements the bottom of D1's
gradient faithfully and the top of it not at all** — and the top is the half the owner
called the tactical identity. A Jawa clan whose famous anti-droid weapon cannot touch a
droid, on a world whose progression is gated on captured droid brains, is the defect.

**Why, mechanically:** the whole effect is the `JawaIon_Stun` **hediff**, and a mechanoid
cannot receive a hediff. `harmsHealth: false` means it takes no HP either;
`externalViolenceForMechanoids: true` only classifies the hit as violence;
`combatLogRules: Damage_EMP` is cosmetic. ⇒ **A hediff-only route can never reach the target
class this weapon exists to beat.**

✅ **Keep `DamageWorker_IonBuildup` exactly as it is for flesh.** Add the machine tier
alongside it. Carried by `ION_MACHINE_TIER_MISSING_1` (BUILD). The `KNOWN INERT` comment in
the mod source is **stale** — the worker fires.

⚠️ **L5 survives this, narrowly, and the reason matters.** Ion drops a person *slowly and
expensively*; stun/neural drops one *fast*. The two tools still differ, so L5's *"designed
reason for team composition"* holds — but it is a gradient, not the clean mirror L5 claims.
**Do not cite L5 to argue ion cannot touch people; the owner ruled otherwise.**

**Derives:** ion is the archetype of the verb-budget weapon (`balance_paradigm.md`
Axis 10): near-zero damage, entirely new possibility. It must be the *only*
convenient answer to something, or nobody carries it. Salvage-intact is that
something.

### L5 — Stun is the mirror of ion

Neural weapons overwhelm a nervous system.

- Excellent against organics; **completely inert against machines**.
- Non-lethal by nature: the capture verb for people, as ion is for droids.

**Derives:** a squad facing mixed droid-and-organic opposition genuinely needs
two tools. That is a designed reason for team composition, straight out of the
physics.

### L6 — A shield is plasma, and plasma stops plasma

**Like repels like.** A deflector screen is a contained plasma field, and it is
built to defeat the two things this galaxy shoots most: **blaster bolts and
lightsabers**, which are themselves plasma. Against those it is superb.

Against **matter** it is much weaker:

- **Mass and momentum push through.** A heavy melee blow, a thrown rock, a body.
- **Metal parts it far faster than anything else.** A vibro-blade, a spear, a
  slug: the more metallic and concentrated the strike, the quicker the screen
  fails.
- Bombardment by sheer weight of fire will also collapse it — see L17.

**The governing distinction is SPEED.** The screen resists things arriving fast
and hot. Anything **slow** walks straight through: a blade, a spear, a shoulder,
a thrown rock — and, decisively, **a grenade rolled along the ground**. This is
canon and it is the most useful single fact about shields: droid screens are
defeated by *rolling* a charge under them, which then detonates inside.

#### L6a — A shield is worn, not built

A screen must anchor against the matter around it — ground, walls, debris. That
anchoring is what stops incoming mass, and it is also what makes the shield a
**burden**:

- **Omnidirectional deployment costs mobility.** Fully enclosed, the bearer is
  slowed severely — the field is gripping the terrain in every direction and
  dragging it. Stand still and be nearly invulnerable to fire; move and be slow
  enough to be flanked, charged or mined.
- **Or project it in ONE direction** and keep your speed. Then it is an
  arm-shield: excellent forward, useless from the side or behind.

So a deflector is not a wall, it is **a physical shield that happens to be made
of plasma**, with the same ancient tradeoff soldiers have always had: cover or
speed, frontage or flanks.

**Derives:** shields stop being an "I win" item without any arbitrary nerf. The
counter to a turtled shield-bearer is *time and position* — flank them, close
with them, or make the ground under them lethal. The counter to a mobile one is
simply to shoot it from the side.

#### L6b — Consequences

**(a) You can shoot OUT from inside.** Fire originating within the field passes
freely; the screen is looking outward. A shielded position is therefore a
*fortress with an asymmetry*: they can shoot you, you cannot shoot them.

**(b) So the counter to a shield is to close, not to escalate.** You do not need
a bigger gun — you need to reach it with metal. That converts a shield wall into
a *charge*, which is the most cinematic scene in the setting and exactly the
Gungan-line image. It also means primitive weapons — spears, blades, heavy
kinetics — are the correct answer to the galaxy's most advanced defence, which is
a beautiful inversion and keeps the whole low-tech armoury permanently relevant.

**(c) An overwhelmed generator detonates** (L17). Collapsing a shield is not a
neutral event; it is an explosion at the shield's own position. Shields are
therefore a hazard to stand behind as well as an advantage — and blowing one is
a *tactic*.

**Derives:** a shielded target does not want a bigger gun, it wants a *different
verb*. This is the verb budget expressed as physical law, and it is the single
strongest anti-inflation mechanism we have.

### L7 — Armour is three unrelated technologies

There is no such thing as "good armour", only armour good *against something*.

| armour type | defeats | fails against |
|---|---|---|
| **Mass / plate** | kinetic, claws, impact | thermal (heats), ion (conducts) |
| **Ablative / refractory** | thermal, blasters | kinetic (punches through) |
| **Insulative / Faraday** | ionic, neural, electrical | everything physical |

- **Leather and hide are mass armour, cheap tier.** Genuinely good against teeth
  and claws — the wildlife of this world — and nearly worthless against a
  blaster. Dress for the animals or dress for the war.
- **Advanced composite armour** layers mass + ablative, which is why it earns the
  ~5-shot contract against a standard blaster — and why a *heavy* weapon still
  breaks that contract in one hit.

### L8 — A few materials cheat, and they are rare on purpose

Beskar, cortosis, phrik: dense, refractory, lightsaber-resistant alloys.

- They are the exception that proves L3 — and their scarcity is the only thing
  keeping L3 intact.
- **Never craftable at scale.** Quest-earned, salvaged, inherited. This is a hard
  guardrail: a mass-producible lightsaber-proof armour deletes an entire law.

### L9 — Scale law: ship weapons are two orders above personal

Turbolasers and ship-scale ordnance are not big guns; they are a different
category of event.

- Nothing person-portable meaningfully damages capital plating.
- Nothing ship-scale is *precise*. They delete areas, not targets.
- Consequence: when ship weaponry enters a scene, the question changes from
  "can we win this fight" to "how do we stop being here". That genre-shift is
  the point.

### L10 — Droids obey a different biology

- **No pain, no fear, no bleeding, no morale.** They do not rout and cannot be
  demoralised.
- **Immune** to neural, toxic, disease, temperature-stress, suffocation.
- **Acutely vulnerable to ionic**, and to kinetic damage against their frames.
- **Physically delicate unless purpose-built for war.** A protocol droid comes
  apart. A battle droid is armoured, and *looks* it.
- **Slow.** Droids do not sprint. Their menace is inevitability.
- **Poor unarmed, competent armed** — tools that were never meant to brawl.

### L11 — Living armour is mass armour, with one desert exception

Natural hide, chitin and bone are **mass** armour (L7): big animals shrug off
claws and slugs.

- So by default, **blasters are the right answer to big animals** — energy
  bypasses mass armour.
- **The exception, and it defines this world:** fauna evolved for extreme heat
  are naturally **ablative**. Desert megafauna resist thermal weapons.

**Derives — this is the best consequence in the document:** on a desert world,
the standard blaster is the *wrong tool* for the local megafauna. Colonists must
fall back on slugthrowers, vibro-weapons, traps and terrain to face the things
that actually live here. That single law makes the setting's ecology and its
armoury tell the same story, and it gives the crude kinetic weapons a permanent
home.

### L12 — The environment is a participant

- **Sand fouls mechanisms.** Slugthrowers jam, droid joints degrade, vehicles
  need maintenance. Energy weapons do not care.
- **Heat is a weapon.** Thermal-resistant creatures are comfortable where
  colonists are not; midday is a defensive asset for them.
- **Storms are ionic.** They disable droids and shields, and they arrive on the
  weather system, not on the raid system.

**Derives:** the desert is not scenery, it is an active balancing force that
periodically inverts who has the advantage — and it does so on a schedule the
player can learn and exploit.

### L13 — Explosives are the universal answer, and armour barely helps

Blast does not care what you are made of. It is the one form of harm with no
hard counter, and its armour ladder runs **backwards** from every other law:

| worn | effect vs blast |
|---|---|
| **Ablative / refractory** | *somewhat* useful — mass and refractory layers eat overpressure |
| **Advanced composite** | a little |
| **Standard armour or clothing** | **nothing at all** |

**Derives:** explosives are the great equaliser and therefore must be
**scarce, loud and dangerous to the user**. They are the answer when there is no
other answer — a siege tool, a last resort, a trap. If explosives become plentiful
the entire armour economy collapses, because no other law can push back on them.

**Guardrail:** blast is the one place where scarcity (`balance_paradigm.md`
Axis 16) is doing *all* the balancing work. Treat availability as the only lever.

#### L13a — Blast is the shield-killer, because blast can be delivered SLOWLY

A grenade **rolled** rather than thrown is slow, low and in contact with the
ground — every property a deflector screen fails to stop (L6). It passes through
and detonates inside, where the shield is no help at all.

Ranked by how well they defeat a shield:

| delivery | vs shield | why |
|---|---|---|
| **Mine / buried charge** | **◎ decisive** | already inside the anchor zone; the bearer walks onto it |
| **Explosive trap** | **◎ decisive** | stationary, slow, emplaced — the shield never had a chance to stop it |
| **Rolled grenade** | **◎** | slow and ground-hugging; the canonical droid-shield killer |
| **Thrown grenade** | ○ | arrives faster and higher; may be partly deflected |
| **Missile / rocket** | **△** | fast and hot — precisely what a screen is built to stop |

**Derives, and this is a big one: mines and emplaced traps are the premier
anti-shield weapon.** That makes trap-laying a genuine tactical discipline rather
than early-game filler, rewards prepared ground and defensive play, and gives a
low-tech colony a real answer to advanced infantry. It also pairs with L6a — a
shield-bearer is *slow*, which is exactly the target profile a minefield wants.

### L13b — Missiles barely exist in this galaxy, and that is a consequence not a choice

If a warhead must arrive fast to arrive at all, and fast is exactly what
deflector screens stop (L6), then guided missiles are **strictly worse than a
blaster** against any defended target. So the galaxy never developed them at
infantry or fighter scale.

**Derives:** the setting's explosions come overwhelmingly from **things being
killed**, not from ordnance being launched (L17). Wrecked droids, ruptured
reactors, overloaded generators, spent power cells. This is why the battlefields
of this universe look the way they do — full of detonations, nearly empty of
rockets.

It also protects the armour economy: if missiles were viable, L13's
no-hard-counter problem would arrive at range and in volume.

#### L13c — …except the SLOW ones. The torpedo exception

The rule above kills the *hypersonic* missile — the guided anti-tank round that
arrives too fast to be stopped and too fast to get through a screen. It does not
kill the **torpedo**, and the difference is the whole design.

Run L6 backwards. Shields stop things arriving **fast**; slow things walk
through. So the surviving warhead in this galaxy is one that **drifts**:

- **It is slow enough to pass a deflector screen** — the same property that lets
  a rolled grenade under a droid shield (L13a) lets a torpedo through a
  fortified line. Missiles become the **ranged** anti-shield weapon, where mines
  are the **emplaced** one.
- **It is slow enough to be seen, dodged, shot down or walked away from.** That
  is the counterplay that makes a no-hard-counter weapon (L13) tolerable, and it
  is why this is not a loophole in L13's scarcity guardrail.
- **So it is only worth firing at something that cannot move**: an emplacement, a
  vehicle, a shield generator, a bunkered position, a VAST creature. Against
  infantry it is a waste — they simply step aside.

That is a torpedo, and it is thoroughly of this fiction: a proton torpedo
drifting down a trench, a Mandalorian's wrist rocket, an ion torpedo lobbed at a
walker. **Slow, rare, specialist, aimed at things that cannot dodge.**

#### L13d — And the best ones do not carry damage at all

A slow warhead is a **delivery system**, and what it delivers need not be blast.
Carrying a *verb* across a battlefield is the thing nothing else in the armoury
can do (L4, L15, L16):

| warhead | delivers | used on |
|---|---|---|
| **ion torpedo** | disable | vehicles, turrets, shield generators — and leaves them salvageable (L17) |
| **buzz droid** | sabotage that persists | anything mechanical |
| **net / adhesive** | pin | something too big to stop, briefly |
| **gas / tox** | area denial | dug-in positions |
| **EMP burst** | blackout | a shielded strongpoint |
| conventional blast | damage | the boring one |

**Derives:** the missile stops being a bigger gun and becomes the **only way to
put an effect somewhere you cannot reach**. That is a distinct tactical role
nothing else fills, it keeps the weapon rare and specialist rather than a damage
escalation, and it obeys the anti-exponential pillar: a new option, not a bigger
number.

**Design consequence for the roster:** cut the hypersonic launchers wholesale —
they are Earth weapons wearing a new name. Keep a *small* number of slow,
effect-carrying torpedoes, and give them a faction identity (Mandalorian wrist
rockets, a Rebel-pattern launcher) so they read as specialist kit rather than
standard issue.

### L14 — Vibro-weapons shear; they are the anti-ablative

A vibro-blade oscillates a hardened edge at enormous frequency. It defeats armour
by **concentrating force into a vanishingly thin line** — the opposite technique
to a lightsaber.

| | lightsaber | vibro-blade |
|---|---|---|
| method | **melts** a broad path | **shears** a narrow one |
| beaten by | *mass* — thick plate is too much to melt (L3) | *nothing thick, but it is slow to get through* |
| supreme against | flesh, thin armour, anything a person wears | **ablative and refractory armour** |
| vs shields | parts them (plasma-on-plasma) | **parts them fastest** — metal (L6) |

**Derives:** vibro-weapons are the deliberate counter to the armour class that
beats blasters. So the loop closes: blaster → beaten by ablative → beaten by
vibro → beaten by mass plate → beaten by blaster's heat. **No armour is safe from
everything and no weapon beats everything**, purely from the physics.

This is also why a technologically backward opponent with good blades is
genuinely dangerous, which is a story we want to be able to tell.

### L15 — The Force is magical, and it does not do damage

The Force is **not** one of the seven forms of harm and must never become a
damage type. It is a source of **verbs** — the strangest ones in the setting.

- Displace, pull, pin, crush-grip, hurl.
- Fear, calm, confuse, persuade, cloud a mind.
- Sense, foresee, locate, reveal.
- Endure — resist heat, pain, fatigue, poison.

**Derives:** Force users are not artillery, they are *problem-changers*. They
turn a fight into a different fight. This keeps them mythic rather than
statistically dominant, and it keeps them inside the anti-exponential pillar: a
Force user grants new options, never bigger numbers.

**Guardrail:** any proposed Force power expressible as "X damage" is
mis-specified. Rewrite it as a verb or drop it.

### L16 — Lightning is the neural verb, and it is rarely lethal

Force lightning and ion-blaster discharge are the **same phenomenon** at
different sources, which is why they behave alike:

- They **stun, overwhelm, down and incapacitate** — non-lethally or
  semi-lethally.
- Against machines they follow L4 (disable).
- Against organics they follow L5 (neural shock).
  ✅ **CONFIRMED CORRECT — DECIDE, 2026-08-22.** This bullet was briefly struck earlier the
  same day and the strike was wrong. It agrees with the owner's **LOCKED SPEC D1**
  (`design/Jawa/mods/required_mods.md`, 2026-08-08): ion is tiered, and flesh is its weakest
  tier rather than an exempt one. **L4's "warm breeze" is the line that gives**, and it is
  amended above.

**Derives:** electricity is the *capture* damage type for both target classes at
once — the single most useful non-lethal tool in the setting, and the reason a
Force user or an ion-armed trooper can end a fight without a body. Downed is not
dead, and this is where most of our prisoners, salvage and mercy come from.

It also links a famous Force power to a common weapon effect through one
mechanism, which is the kind of coherence this document exists to produce.

### L17 — Everything explodes: enormous power, minimal safety

**This is a law about the whole civilisation, not one device.** This galaxy runs
staggering energy through equipment with almost no containment margin. Reactors,
droids, turrets, vehicles, shield generators, power conduits — when they fail,
they fail *violently*.

- **Destroyed machinery detonates.** Expect it as the default, not the exception.
  This explicitly includes **droids** — every one is a walking charge.
- **Overloaded shield generators detonate** — collapsing a shield is an explosion
  at the shield's own position.
- **Powered weapons detonate when their durability runs out.** A blaster is a
  containment vessel for plasma; a worn-out containment vessel fails the only way
  this civilisation's equipment knows how. Your weapon is a bomb on a timer, and
  the timer is visible (L18).
- Battlefields therefore become *progressively more dangerous* as they fill with
  wrecks and stressed equipment.

#### L17a — Detonation scale tracks energy DENSITY, not object size

How big the explosion is has nothing to do with how big the thing was. It tracks
how much energy was crammed into how little containment. The ladder:

| device | failure |
|---|---|
| spent power cell | a pop and a scorch |
| blaster / powered weapon | moderate — clears a room's worth of space |
| droid | significant; do not be adjacent |
| vehicle, reactor, generator | large, and at the shield's own position if it was projecting one |
| **lightsaber** | **spectacular, and wildly disproportionate to its size** |

**A lightsaber is the densest energy object a person can carry.** It holds a
blade of plasma inside a force envelope small enough to fit in a hand — the most
extreme containment ratio in the setting. When that containment fails it does not
merely break. It **goes off**, and it is the single most violent thing that can
happen at infantry scale.

Consequences, and they are all good ones:

- **Killing a duellist is dangerous to the killer.** Winning a lightsaber fight in
  a corridor may collapse the corridor. Melee against a Force user carries a risk
  that has nothing to do with the Force.
- **Never fight one indoors near anything you value.** Duels want to happen on
  gantries, in hangars, over reactor shafts — which is exactly where they *do*
  happen, and now we know why.
- **An intact recovered lightsaber is a genuine prize**, because most do not
  survive their owner's defeat. This is the in-fiction reason they are rare, and
  it justifies the quest-gating in a way "the GM said so" never could.
- **It is the strongest argument for ion (L4/L16).** Disable the wielder and the
  weapon survives; destroy the wielder and you may lose both the prize and the
  room. Electricity is how you take a lightsaber intact.
- **A dying Jedi is a set-piece.** The death of a great duellist should be
  visible from across the map.

Three more things fall out of L17, and the third is the best:

1. **Machines are hazardous to fight at close range.** Standing next to a droid
   you are killing is a mistake. This gives droids a threat profile even while
   losing, and it makes melee against machines a real decision.
2. **Shooting the power source is a legitimate tactic** — generators, packs,
   conduits become targets with disproportionate payoff.
3. **It is the economic justification for ion weapons.** Killing a droid or a
   vehicle *destroys* it; **disabling it with ion leaves it intact to salvage.**
   That single fact answers the hardest question about the verb budget — "why
   would anyone carry a zero-damage weapon?" — with *because you want the thing
   afterwards.* Ion is the difference between a crater and a prize.

**Derives, thematically:** the constant machinery explosions in this setting are
not a visual tic, they are a statement about its engineering culture — power
worshipped, safety margins unaffordable or unfashionable. Everything is a bomb
that has not gone off yet.

### L18 — Ablation is visible: armour degrades

Implied by L1, and now a rule. Energy weapons ablate — they burn away material —
so **armour wears out under sustained fire and must be maintained or replaced**.

- Refractory and ablative layers degrade **fastest**, because degrading is
  literally how they work. Their protection is consumable.
- Mass plate degrades slowly but permanently.
- Degradation must be **legible**: the player should be able to see that a suit
  is spent before it fails, or it is just invisible bad luck.

**Derives:** armour becomes a *supply* concern rather than a one-time purchase.
A long siege erodes defenders even when they are winning, which is dramatically
correct, and it gives the crafting economy a permanent job.

---

## Part 3 — The interaction matrix

The payoff. Read a row against a column to answer most balance questions.
**◎ decisive · ○ effective · △ poor · ✕ useless**

| ↓ weapon \ target → | unarmoured person | ablative armour | advanced armour | vehicle / ship | droid | big beast | desert megafauna | shielded |
|---|---|---|---|---|---|---|---|---|
| **Blaster (standard)** | ◎ 1–2 shots | △ ablates (L7) | ○ ~5 shots | △ | ○ | ○ | **△** (L11) | **✕** (L6) |
| **Blaster (heavy)** | ◎ | ○ | ◎ can one-shot | ○ | ◎ | ◎ | ○ | **✕** (L6) |
| **Slugthrower** | ○ | ○ | ○ | △ | ◎ frames | ○ | **◎** (L11) | ○ metal (L6) |
| **Spear / primitive melee** | ○ | ○ | △ | ✕ | ○ | **○** reach | **◎** (L11) | **◎** mass+metal |
| **Vibro-blade** | ◎ | **◎** shears (L14) | ○ | △ | ◎ | ◎ | ◎ | **◎ fastest** (L14) |
| **Lightsaber** | ◎ | ◎ | ◎ | △ stall only (L3) | ◎ | ◎ | ◎ | ◎ plasma (L6) |
| **Ion / lightning** | ✕ dmg · ○ **downs** | ✕ | △ powered | ○ disables | **◎ intact** (L17) | ✕ | ✕ | **◎** drops it |
| **Stun** | ◎ capture | ○ | ○ | ✕ | ✕ | ○ | ○ | ○ |
| **Grenade (thrown)** | **◎** | ○ *somewhat* | ○ *a little* | ◎ | ◎ | ◎ | ◎ | ○ partly deflected |
| **Grenade (rolled)** | ◎ | ○ | ○ | ◎ | ◎ | ◎ | ◎ | **◎ passes through** (L13a) |
| **Mine / explosive trap** | ◎ | ○ | ○ | ◎ | ◎ | ◎ | ◎ | **◎ decisive** (L13a) |
| **Missile / rocket** | ◎ | ○ | ○ | ◎ | ◎ | ◎ | ◎ | **△** — why they don't exist (L13b) |
| **Ship weapon** | ◎ overkill | ◎ | ◎ | ◎ | ◎ | ◎ | ◎ | ○ overloads |
| **Fire / thermal** | ○ | △ | △ | ✕ | ○ | ○ | **✕** (L11) | ✕ |
| **The Force** | *verbs only* (L15) | — | — | — | — | — | — | — |

**Every column has at least one ✕ or △ row** — except **explosives**, which is
deliberately the exception and is balanced by scarcity alone (L13). If a future
addition breaks that property, the addition is wrong.

**The closed loop, readable straight off the table:**
blaster → beaten by **ablative** → beaten by **vibro** → beaten by **mass plate**
→ beaten by **blaster heat**. And shields beat plasma → beaten by **metal and
mass** → which are the primitive weapons. Nothing dominates.

---

## Part 4 — What these laws forbid

Guardrails. A proposal violating one of these is rejected without further
argument.

1. **No universal weapon.** Anything effective in every column is mis-specified.
2. **No universal armour.** L7 makes this physically impossible; keep it so.
3. **No mass-produced law-breakers.** Beskar-class materials stay quest-gated
   (L8).
4. **No vertical scaling.** New tech grants new *verbs*, not bigger numbers on
   the same verb (pillar: anti-exponential).
5. **No player-scalable ship weaponry.** Ship-scale stays a threat category and
   an earned story beat, never a purchasable upgrade (L9).
6. **No unavoidable lethality.** Anything that can kill without warning violates
   the counterplay rule; give it a telegraph or remove it.
7. **No plentiful explosives.** Blast has no hard counter (L13), so availability
   is the only thing balancing it. Cheap or craftable-at-scale explosives delete
   the armour economy outright.
8. **No damaging Force powers.** Any power expressible as "X damage" is
   mis-specified (L15). Rewrite it as a verb or drop it.
9. **No safe machinery.** If a machine can be destroyed and does *not* detonate,
   it needs a stated reason (L17) — the default is that it goes up.

---

## Part 5 — The VAST tier has a working precedent

**`LEVIATHANS:SANDWORM` (`chezhou.creature.sandworm`) is already installed, and
it is built exactly the way the paradigm says a VAST creature must be.**

Discovered 2026-08-10 — and notably it appears in **no** animal analysis,
because it is not an animal:

- `SandWorm_Thing` — a ThingDef with **no `<race>` element**. Not a pawn.
- `SandWorm_HitProxy` — a separate hit surface, i.e. it is bigger than one tile.
- Plus a **WorldObjectDef**, a **QuestScriptDef**, its own **WeatherDef** and its
  own **SongDef**, driven by custom C# (`ChezhouLib`).

That is the template: a VAST creature is a **world object with weather and music
attached**, encountered through a quest script — terrain that happens to be
alive, not a spawn on the animal table. It gets a name, a soundtrack, and a
change in the sky.

Use it as the reference implementation for every VAST entity we author.

---

## Part 6 — Open questions

**Resolved 2026-08-10:** the Force is verbs, not damage (L15) · armour degrades
under ablation (L18) · vibro-weapons shear and counter ablative armour (L14) ·
shields are plasma-vs-plasma, you may fire outward from within, and metal breaks
them fastest (L6) · machinery detonates as a civilisational trait (L17).

**Resolved 2026-08-11:** shields are worn, directional and mobility-taxing, and
slow things pass through (L6a) — which answers "are personal shields too strong"
without a nerf · rolled grenades, mines and traps are the premier anti-shield
weapons (L13a) · missiles barely exist because speed is what shields stop (L13b)
· droids and powered weapons detonate, weapons when durability expires (L17).

Still open:

- **What jams, and how visibly?** L12 needs a legible failure state or it is just
  invisible bad luck.
- **How fast is "slow" for cutting a bulkhead?** (L3) Needs a real number before
  any infiltration content is designed around it.
- **Do organics benefit from Faraday-type armour vs lightning?** (L16) If yes,
  there is an anti-stun counter-loadout; if no, electricity has no armour answer
  at all — which may be correct given it is non-lethal.
