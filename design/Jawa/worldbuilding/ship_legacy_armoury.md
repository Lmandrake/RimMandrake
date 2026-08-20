# The ship's legacy armoury — laser weapons as inherited technology

_A retired seat, 2026-08-13. **Owner's ruling**, recorded the day it was made:_

> *"The lasers are uniquely interesting: they represent custom weaponry from our
> old, powerful spaceship that we can start to build at a certain point of tech
> growth from onboard files. In v2 we will earn that right; in v1 we'll just have
> it available in the research tree as usual."*

⚠️ **I had called this mod redundant an hour earlier.** Wrong — I judged it as
*more guns* beside the Outer Rim blasters. It is not more guns; it is **the only
piece of technology in the stack that can be the ship's own**, and that is a
narrative slot nothing else fills.

---

## The mod already ships the progression — we reflavour, we do not author

`Vanilla Weapons Expanded – Laser`, `vanillaexpanded.vwel`, ws `1989352844`,
**installed and currently inactive**. Read from its own defs, not its store page:

| tier | what it ships | research |
|---|---|---|
| **Salvaged** | salvaged laser pistol / rifle / shotgun / sniper, plus **`unstable` shot variants** — visibly worse projectiles | `salvaged laser weapons` |
| **Full** | laser pistol / rifle / SMG / shotgun / sniper / **minigun**, **laser sword**, **tesla gun** | `ultratech laser weapons` |

⭐ **That is the owner's design, already built.** Cobbled-together, unstable
weapons first; the real ship-grade article later. **Two research projects exist,
a `salvage laser weapon` recipe exists, and the unstable projectiles exist.** The
work here is naming and gating, not authoring.

## The fiction

**These are not laser weapons the clan invented. They are the ship's.**

The gravship was something before it was a home — and its armoury is in its
files, not its holds. The clan can *read* what it once carried long before it can
*make* it. Early attempts come out unstable because the Jawas are building from a
schematic they only half understand, with materials the schematic never named.

**The full tier is the moment the ship stops being scrap the clan lives in and
becomes a thing the clan has recovered.** That is the emotional beat, and it is
why this belongs to the flagship (*the gravship ships DEEP*)
rather than to the weapons row.

## 🔴 The coherence rule — the tiers are not equal, and this is the whole trick

The mod patches `PawnKinds_Pirate.xml` and `FactionDef_Misc.xml`, so **other
factions carry these weapons by default.** Left alone, the ship's unique armoury
is what every pirate is holding, and the fiction dies on first contact.

> **The salvaged tier may circulate freely. The full tier is ours alone.**

Salvaged lasers *should* be out in the world — they are what scavengers make
from the same wrecks the clan works, and finding one on a raider is evidence the
technology is real and recoverable. **Nobody else fields the full tier.** The
mod's own two-tier split does this for us; we only remove the full tier from
other factions' pawn groups.

## v1 versus v2

- **v1 — enable it and leave the research where the mod puts it.** Ordinary
  research tree, no gating, no reflavour required to ship. The owner ruled this
  explicitly. It costs one ModsConfig line.
- **v2 — earn it.** The research unlocks are gated behind **recovering ship
  data**, not behind ordinary tech progression: the schematics come out of the
  hull, so the player must restore the systems that hold them. This is the
  natural hook for the deck plan's data spaces and needs no new mechanic beyond
  a research prerequisite.
- **v2 — rename.** The two research projects and the weapon labels take the
  ship's own naming. Cheap, and it is what makes them *ours* rather than a
  vanilla-expanded pack.

## Two loose threads, flagged not resolved

- ⚠️ **The `laser sword`.** It is a melee energy weapon already on disk, and
  `design/Jawa/force_users_build_spec.md` is a Jedi/Sith build the owner flagged
  as a joint job — while `lee.theforce.lightsaber` is active in `ModsConfig.xml`
  and **not installed** (filed at BUILD). **Do not casually make the laser sword a
  lightsaber.** If Force users get a distinct weapon, a common laser sword
  cheapens it; if they do not, this is the cheapest possible route. **Decide
  when the Force spec is decided, not before.**
- **Anti-bloat, stated so it holds later:** this closes the "do we want more
  weapon mods" question. **We do not.** One inherited-technology line, tiered,
  is worth more than three more packs of guns, and the reason it works is that
  it is *scarce*.
