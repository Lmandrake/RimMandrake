# Deep history — the Rakata, the Assailant, and what still runs

## One people, two names [owner 2026-08-20]

**`Rakata` is the ENDONYM; `the Forsaken` / `the Forgotten` is the EXONYM.**
Nobody alive says "Rakata" except a Rakata, a scholar, or a sleeper — a Jawa, a
Hutt factor or an Imperial clerk says *the Forsaken*. Register rule for ALL
authored text. (The `AB_RockyCrags` biome's own description of "a mysterious
humanoid alien race simply known as Forsakens" is the same people — the name
was already in the stack.)

## Who they were — both halves are true [owner 2026-08-20 + 2026-08-29]

**Terraformers and mega-builders**: they made this world habitable, brought
metal down from the asteroids, built the vaults, the works the Geonosians
worship, and the Utinni. **And they were tyrants**: *"destructive,
self-destroying, dark force wielding megastructure-building tyrants bent on
conquest and domination. Until they met something so awful that it, in turn,
ate them alive."* Victims AND tyrants; neither cancels the other.

**The player arc is a designed REVERSAL**: sympathy first (the sleeper
backstories are deliberately the sympathy layer), revelation second (the flesh
dungeon, `ASSAILANT_FLESH_DUNGEON_1`). The knife's twist: the player's own
vessel is tyrant technology. ⚠️ **Register guard: tyranny is revealed content —
never ambient in a pre-reveal bio, label or tooltip.**

## The Assailant [owner 2026-08-20]

Unnamed, unknowable **in-world**: *"their technology literally rots and leaves
little trace to study."* The rumour — never more than a rumour, never confirmed
in any def or dialogue — says **Sith**: ancient sorcerer-alchemists, precursor
to the Sithspawn tradition. The rot explains everything at once: why the author
is unknown, why **everything scavengeable on this planet is Rakatan** (the
campaign's entire material economy is one side's leavings), why the Ascendant
Helix must come here in person (the only surviving specimen of that technology
is the living residue in the strange biomes), and why the Arsenal is the
*victims'* machines. The Assailant must **never become sympathetic** — the
point is that something could do this TO the Rakata [owner 2026-08-29].

The **self-replicating flesh** was the Assailant's weapon. It is still running:
contained in breached vaults, escaped and naturalised in the poison forest, the
mycotic jungle, the gelatinous superorganism (R-H8: the strange biomes'
genetics are bioweapon residue). Do not weld this to the forsaken crags — the
crags read as chemistry that was always here; two alien facts are richer than
one explained one.

## The war and the sleepers [owner 2026-08-29]

The fall took **nearly a generation** of fighting and losing. The casket
sleepers are the **war generation** — grown children of the last great Rakata,
hardened, PTSD-scarred, fierce survivors, superb researchers, excellent with
frightening weaponry, and **violently against genetic modification and the
technology that births such things** (trauma from the flesh-weapon; the VQE
"patients" carrying archite genes are Rakata the enemy TOOK and flesh-shaped).
They wake believing the war is still on, because nobody ever told them it was
over. **Everything the Forsaken left behind is still executing its last
instruction** — machines, sleepers, and the ship alike. That is the theme.

Sleepers are an APPEARANCE + encounter surface, not a faction: vanilla ancients
patched to xenotype `RimMandrakeRakata`, labels using the exonym ("Forsaken
soldier"), gear and spawn behavior untouched. The `Ancients` faction stays
hidden. Build detail: `worldbuilding/ANCIENTS_AS_RAKATA_SPEC.md`.

## The Forgotten Arsenal

`FactionDef Mechanoid`, relabelled — **a class of thing, not an army**:
self-replicating Rakatan defensive systems, buried by sand, still guarding
fortified vaults. Legibility is the design: it guards a perimeter, it does not
hunt. Mechanoids stay in the raid roster in full [owner 2026-08-15, 2026-08-20
— twice ruled against emptying it]; the emphasis belongs at the vaults.
Lore wall: Arsenal mechanoids are ancient self-replicating tech, **utterly
incompatible with modern droid parts** — the boundary between mechanoids and
droids (`08_droids.md`).

## The vaults — three things inside [owner 2026-08-15]

| contents | meaning |
|---|---|
| ① mechanoid garrisons (the bulk) | the vault did its job; everything still switched on |
| ② the enemy's flesh weapons, out of control | the vault was breached and lost; what killed the defenders is still multiplying |
| ③ frozen Rakata, still believing a war is on | the rare one, and the emotional core — a scene, not an encounter |

## The Rust Cathedral

The one mega-structure patch (`AB_MechanoidIntrusion`, 236 tiles by the
substellar point): the Forsakens' asteroid-fed factory complexes, ground to a
rusty halt, preserved by low humidity and zero tectonics. **One patch in the
world, sited by hand; a map MADE OF treasure** (its walls are literally metal).
Its costs are set together [owner 2026-08-19]: stationary legible hazards
(toxic pools that damage; sulfuric dressing for the acid look — no true acid
terrain exists in the stack) + Arsenal garrisons at their densest + **sacrilege**
— it is sacred to the Free Droid Enclaves (8 of their 12 settlements stand on
Cathedral ground; remote from ORGANICS is what its remoteness means). The
sacred core is ~10 faction-owned Buildings at −15 goodwill each from a neutral
0; mineable bulk is free. Hostility has enormous hysteresis (hostile at −75,
un-hostile only at 0) — desecration is survivable, repentance is expensive.

## The Utinni was there at the beginning

The ship is a Forsaken **initiator** — one of the vessels that started this
world (`06_the_ship.md`). Every ruin is her people's; a woken sleeper who sees
her sees an initiator with the wrong crew aboard.
