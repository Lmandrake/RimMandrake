# WATCHER_CREATURES_MOD_1 — the watchers: shy creatures that peek, watch, and jerk away

Owner, 2026-09-30, typed during the Stillsand turn-3 sitting (after admitting the piinnok):
*"strikes me that there could be a new collection of creatures that just sit and watch and poke out
and then jerk away and hide when the players get near. Almost every biome could use this. It might
even be a mod of its own that now informs all of them."*

## spec

A cross-biome `RM_` mod (franchise-free tier): a shared behaviour kit, plus a family of small watcher
creatures, one or more per biome. The behaviour cycle is hidden → pokes out → watches (it faces the
nearest pawn) → jerks back and hides when a pawn comes within a radius → re-emerges after a delay.
Every biome's roster can draw on it.

Prior art to reuse, not re-invent (search done 2026-09-30):
- the piinnok (Stillsand, admitted the same sitting): its lens tracks pawns and sinks on a threat.
  It's the first member.
- `RM_JobDriver_Burrow` / `RM_BurrowOnFireExtension` (Pyrelands): burrow-to-hide.
- `RM_MurrekDrift` (Blue Desert).
- The Brine Crown's unbuilt two-state retraction (`RM_GreySeaFlora.xml`).

Constraints: no animal vanishes without a readable sign (a hole or mound shows where it hid); a
Mod Settings toggle per feature; every DLC is assumed present.

## owner rulings (card, 2026-09-30 18:11 PDT)

- **Hide** = the creature vanishes in place and leaves a **sign mark on the cell** (the readable
  sign the no-vanish constraint requires).
- **Flinch cue** = anything that is not its own kind.
- **Standalone:** it ships as its own mod, not folded into a biome mod.
- **Q9 (peek art), owner typed:** *"You should check that we even can have a creatuer look different
  in different mediums. Why not restrict its movements to be upon the Fine Sand of the deep desert?
  that was rather the original intention of the Deep Desert / Dunes biome: swimmers swim in it, and
  these creatures lurk just under its surface"*. Consequences:
  1. **Before ANY watcher art is made**, verify with the RimSage MCP tools (or a cited decompiled
     source) whether a pawn's rendered look can vary by the terrain under it. Record the answer,
     with the symbol read, in this item.
  2. **Bind each watcher's movement to ONE medium** (the Stillsand/deep-desert members to its fine
     sand), so a single baked peek pose is enough and no per-terrain look is needed.

## owner rulings (card, 2026-10-08, typed)

- **Scope:** *"All biomes. It's a new fixture."* Every shipping biome gets a member; the Rust
  Cathedral's is a machine, under its own ban question (pitch Q7).
- **Media:** *"Ground and water for now. And we can bake in their little holes and things as part
  of their art."* No Thing-medium.
- **Cues:** *"Full set."* Built 2026-10-08: seven optional per-member cues (gas, heat, fire, steam,
  shade, buried, light) on `RM_WatcherExtension.cues`, one Mod Settings toggle each.
- **Q9 answer** (terrain-dependent look): recorded with the RimSage symbols read in
  `design/RimMandrake/watcher_creatures_pitch.md` §2.

## criteria

- The Q9 terrain-look check is answered and recorded, and every member names its one medium.
- A design pitch is written and ruled by the owner: the kit mechanism, and a per-biome candidate
  member list drawn from existing rosters plus new creatures.
- The kit is built, and one member per biome is proven on a quicktest map.
