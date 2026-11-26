# Droids — the five states and Droidworks

Governing aesthetic [owner, frozen sheet 2026-08-29]: *"Everything in Star Wars
should feel like bringing it in to the shop, not magical tech."* The 15 owner
rulings of 2026-09-06 and the build: `droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md`.
Buildable engineering + port plan: `droid_system_build_spec.md`. Open
assumptions: `droidworks_assumptions.md`.

**No droid faction exists** [owner 2026-09-06, ruling 2]: droids ride every
faction's own loadouts (Empire, Hutt and Junker kits carry the KotOR chassis),
and wild droids are factionless crashed units gone strange in the desert. The
Free Droid Enclaves are a faction of their own and do not raid you unless you
are in their territory and already their enemy.

## The platform ruling [owner 2026-08-29, twice in one day]

The three shipped frameworks (ABF/Synstructs carrying KotOR, Asimov carrying
Droid Depot, vanilla-mechanoid carrying JDS) are **not the destination**:
*"we will not build on any one of the packs... borrow from them and make our
own."* The platform is **Droidworks** (`mandrake.droidworks`) — one independent
mod, HAR as its only framework dependency, all art yanked in (owner regenerates
it freely), the source packs **retired with credit** once their retirement
checks pass. **Every droid in the game ports to it: 85 kinds** (44 KotOR + 20
Droid Depot + 1 Galactic Empire + 4 ours + 16 JDS) onto seven chassis families plus the Primitive family, with 57 thin
concrete races under them (consolidation ruled over 1:1). **JDS Separatists become capturable on
port** — one rule for all droids; the old "never taken alive" was
platform-forced and dissolves with it.

## The five states [ruled twice on the frozen sheet]

1. **Functional** — with or without damage.
2. **Transient stun** — ion flicker, seconds; the droid may not even fall over
   and resumes what it was doing; ion works *extremely well* on droids.
3. **Downed/off** — disabled, will NOT self-reboot; an object, capturable;
   reboot needs outside help: a Crafting 4 pawn [owner 2026-09-06, ruling 12].
4. **Damaged/unbootable** — "dead"; shop-repairable; parts reusable.
5. **Catastrophic → detonation** — explosion proportional to **current stored
   charge** (a wreck has no power, hence cannot explode). Gonk and the KX-12
   are explosive by nature; combat droids may carry deliberate deny-your-parts
   modules; everything else detonates only here.

Parts always survive tiers 4 and (partly) 5 — **except Forgotten Arsenal
mechanoids**: ancient self-replicating tech, utterly incompatible with modern
droid parts. That is the lore wall between mechanoids and droids.

## The shop-centric lifecycle

CUT as magic: ingestible repair kits, field reactivation kits, skill disks,
healer auras, the auto-factory, battery-eating-as-food, surgery as the install
verb. REPLACED by: repair benches and reassembly harnesses — repair is parts
off, parts fixed, parts on; assembly is lego from the same parts. Overclock is
a bench job (reversible, ~+15% for power/heat/mood). Charging is three tiers
(room nimbus / dock / socket) with spectacular visuals; power is minimal but
necessary (combat ~daily, protocol ~monthly). Rest is self-repair cycles;
maintenance is oil baths and cleaning.

## Embodied software

Star Wars has no abstract software; experience is woven into the body and
**the head is the identity component** — it follows the droid through rebuilds.
No skill disks. **Memory wipe RANDOMIZES traits** (clears idiosyncrasies,
relations, social; faction → player) — mechanically useful, socially
uncomfortable; long-unwiped droids accrete personality (drift). Behavior has
three recognizable sources: **BORN** (chassis psychology — the Assembly slot),
**INSTALLED** (modules carry attitudes — the spider-arm changes who you are;
KotOR's six apparel slots are the chassis), **EXPERIENCED** (the
Service-Record slot; reset only by wipe).

## Formatting, capture, and the bolt

- Tiers: **blank** (deformatted standby, no needs) / **mindless** (a REDUCED
  state, not a default: low-level work only, no needs) / **programmable**
  (complex skills — machines, repair, plants, self-defense; Mood but not
  Joy/Beauty/Comfort) / **sapient** (full inner life: morale, breaks, savants,
  bonds — also with non-sapient droids — and rebellion if denied maintenance and
  recreation; deformatting a sapient is killing someone) [needs by tier: owner
  2026-09-06, ruling 4]. Faction ethics of deformatting: embraced by Junkers,
  Helix, Empire; lobotomy-in-illness (unethical, sometimes necessary) to most
  factions; murder to the Free Droid Enclaves and the Homestead.
- **Brains are import-only** [owner 2026-09-06, ruling 6, the standing
  anti-exponential rule]: personality matrices, processors and databanks come
  from off-world makers and nobody on this world can make one. Only the
  Primitive tier (the G2 repair droid) is fabricated here, never its brain.
- **Capture is manual and up close**: the **data spike**, a consumable keyed
  per faction, made by destructively consuming a damaged droid head of that
  faction. No precision electronic warfare in Star Wars: droids are hardened
  against outside signals, and a large dish-blast area disable is the only
  ranged concession.
- **The restraining bolt is a big deal**: quells rebellion, forces obedience,
  blocks socialization, radiates a mood debuff, disables all idiosyncratic
  benefits — and sapients accrue **resentment that persists after removal →
  instant rebellion when freed**. Droids un-bolt each other during rebellions;
  battle damage shears bolts. The Enclaves treat every bolt as slavery (their
  goodwill layer: `worldbuilding/restraining_bolt_technical.md`). Every bolt is
  also water economics (`02_world.md`).

## Damage model

Immune: poison, frostbite, heat below ~300 °C. Extremely vulnerable: ion/stun.
Droideka shields become a high-power module with detonation risk on collapse;
no mechanitor control anywhere on the platform.

## Build state (2026-08-29/30)

Phase-0 C# written (power need, powered-down state, detonation comp — no
Harmony needed); art yanked (454 textures) + extraction data; FOUNDRY building
DLL/XML/ion-guard/generator + charging trio, bolt core, wipe+spike, pilot gonk,
retirement evidence. The shop CUSTOMER layer (visitors bringing broken droids for repair or upgrade
for profit) is **v1**, as regular events in a pack on top, not inside the
platform [owner 2026-08-29; v1 by ruling 2, 2026-09-06].
The port boundary is the next fresh start from the frozen world [owner
2026-09-06, ruling 10].
