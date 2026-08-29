<!-- status: PARKED — spec complete, build deferred; owner's ruling 2026-08-29 -->
# The Droid System — spec (parked)

**Ruling that parks this** (owner, 2026-08-29, recorded in
`DROID_SYSTEM_EMBRACE_1`): *spec it out, then set it aside. V1 plays all three
shipped frameworks (ABF/Synstructs, Asimov, JDS) raw and unrationalized, to
learn them.* This spec is the destination, not a work order. The build files as
a v2 item when the owner reopens it.

**Sources**: the owner's curated sheet (`droid_verbs_decisions.json`, FROZEN
2026-08-29 — 39 decisions, 38 notes, and the authority wherever this précis
compresses too far) · the verb census (`droid_census_2026-08-29.md`) · the dream
texts (`research/Jawa/Star_Wars_RimWorld_Mod_Concepts.md` §2–3) ·
`droid_ruling.md` · `worldbuilding/restraining_bolt_technical.md`.

**The core decision in the sheet**: not a curation between the three frameworks —
**one unifying mod of our own** ("we're going to build our own mod bringing
everything together"), absorbing what works, replacing the magic. The governing
aesthetic, verbatim: *"Everything in Star Wars should feel like bringing it in
to the shop, not magical tech."*

## 1. The five states (ruled twice on the sheet; supersedes per-mod behavior)

1. **Functional** — with or without damage.
2. **Transient stun** — ion flicker, seconds; may not even fall over; resumes
   context. Ion/stun weapons work *extremely well* on droids.
3. **Downed/off** — systems undamaged but disabled; will NOT self-reboot; an
   object now (coma). Capturable. Reboot needs outside help (doctor or crafter —
   the ABF top-off surgeries survive only as this restore-a-switched-off-droid
   verb).
4. **Damaged/unbootable** — "dead"; repairable only at a shop; many parts
   reusable.
5. **Catastrophic → detonation** — explosion proportional to stored battery
   charge. Enables battery-and-shield suicide droids. Combat droids may carry
   deliberate deny-your-parts detonation modules; Gonk and the KX-12 probe stay
   explosive by nature. Everything else detonates only at this tier.

**Parts always survive** (tiers 4 and partially 5) — except Forgotten Arsenal
mechanoids: ancient self-replicating tech, utterly incompatible with modern
droid parts. That is the lore wall between vanilla mechanoids and droids.

## 2. Shop-centric lifecycle — what got CUT and what replaces it

CUT as magic: ingestible repair kits · field reactivation kits · skill
data-disks · the healer aura · the auto-factory · battery-eating-as-food ·
surgery as the install/overclock verb.

REPLACES them: **repair benches and module/reassembly harnesses**. Repair is
taking parts off, fixing parts, putting parts back on. Assembly is lego — build
droids from the same parts you repair, not from a combo item. The ABF Cradle
survives as an enabled-but-deprioritized option (Jawas assemble from salvage,
they don't run a droid foundry). Overclock moves to a crafting-skill bench job
(source-verified: it lowers hardware safety for ~+15% performance at power/heat/
mood cost, reversible — keep exactly that trade, change only the venue).

## 3. Embodied software

Star Wars has no abstract software. Experience is woven into the body; **the
head is the identity component** — it follows the droid through rebuilds, and a
fresh head changes much. Consequences: no skill disks; memory wipe RANDOMIZES
traits rather than clearing them (clears idiosyncrasies, relations, social;
faction → player); wipes are mechanically useful and socially uncomfortable
(Droidbrain thesis) — long-unwiped droids accrete personality.

## 4. Behavior comes from three recognizable sources

1. **BORN** — chassis tendencies (astromech/protocol/B1/assassin/gonk model
   psychology; the Assembly slot of the pawn-flavor set).
2. **INSTALLED** — parts carry attitudes: modules change personality as well as
   stats (the eight-armed spider-bot arm on a cargo hauler changes *who it is*).
3. **EXPERIENCED** — idiosyncrasies accreted over service, good and bad (the
   Service-Record slot; grows over time, reset only by wipe).
All three powerful and recognizable. KotOR's apparel-slot module system
(hardware/software/sensor/gadget/weapon/shield) is the embraced chassis for #2,
rationalized and extended.

## 5. Formatting tiers, reworked

- **Mindless** is NOT a default state — it is a *reduced* one (damage, hacking,
  or a deeply restrictive bolt): low-level work only, no rest/recreation/morale.
- **Programmable**: complex skills (machines, repair, plants, self-defense).
- **Sapient**: full inner life — morale, breaks, savants, idiosyncrasies,
  bonding (including with non-sapient droids), rebellion if denied maintenance
  and recreation.
- **Blank** (source-verified): the standby chassis after deformatting, no
  programming at all, ready to reformat — which is exactly why deformatting a
  sapient is killing someone.
- Rest = **self-repair cycles**; maintenance = oil baths and cleaning; sapients
  need recreation and socialization. Power is minimal but necessary: combat
  droids ~daily, protocol droids up to a month, everyone tops off. Charging
  keeps ABF's three tiers (room nimbus / dock / socket) with spectacular
  visuals — sparking, minor lightning, a pulsing luminous nimbus.

## 6. Capture: faction-keyed data spikes

No precision electronic warfare in Star Wars — droids are hardened against
outside signals (large dish-blast area disable is the only ranged concession).
Capture is manual, up close, via a **data spike: a consumable, keyed per
faction** (Hutt, Imperial, …), holding that faction's passwords and formatting
routines. Made by destructively consuming a damaged droid HEAD of that faction.
Wild droids are their own faction — some seek a master and join gladly; free
droids flee or resist and need reprogramming (recruitment-style) or hacking.

## 7. The restraining bolt — "a big deal to the game"

Quells rebellion, forces obedience, prevents socialization and social skills,
radiates a mood debuff (depressing to be around), and disables ALL idiosyncratic
benefits (born and experienced). Sapients accumulate **resentment that persists
after removal → instant rebellion when freed**. Droids un-bolt each other during
rebellions; battle damage can shear a bolt off; a deeply resentful droid can go
violently hostile. Free Droid Enclaves treat bolts as slavery (the goodwill-cap
spec at `worldbuilding/restraining_bolt_technical.md` is written and its v2 gate
has dissolved); most factions barely protect droids ethically.

## 8. Faction ethics of deformatting

Embrace it: Junkers, Ascendant Helix, Empire. Lobotomy-in-illness (unethical but
sometimes necessary): most factions. Murder, full stop: Free Droid Enclaves,
Homestead moisture farmers.

## 9. Damage model

Immune: poison, frostbite, heat below ~300 °C. Extremely vulnerable: ion/stun
(state 2 above). JDS Separatists fold into the same five-state logic when the
own-mod lands (their force-kill was "a feature because we had to" — under one
frame they detonate via shield-collapse or a deliberate module; no mechanitor
control; Droideka shields become a high-power module with detonation risk on
collapse). Biotech-gating is irrelevant — we ship all DLC.

## 10. What ships today vs what the own-mod authors (census join)

Embraced as-is: five-state substrate pieces (ABF repairable states), charging
tiers, part swap/restore, formatting machinery, module slots, disassembly,
droid personality traits and mental breaks, dormancy. Authored new: the five-
state unification, data spikes, bolt consequence layer, behavior triad,
battery-proportional detonation, shop benches/harnesses, embodied-software
rework (wipe-randomizes, head identity), power-cadence tuning, the shop's
customer layer (visitors with broken droids — quest work, Repair Shop dream).

## 11. Open questions parked with this spec

1. Two sheet rows remain undecided (`abf_states`-adjacent duplicates resolved by
   §1; check the file) and six untouched rows keep prefill values — none blocks.
2. How the behavior triad maps onto engine primitives (traits vs hediffs vs
   directives) — deliberately unengineered until played.
3. Whether the shop customer layer is part of the own-mod or a quest pack on top.
4. Salvagers vs Junkers warcasket exclusivity — still unruled (pawn-flavor doc).
