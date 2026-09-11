# GREENTIDE_STANDALONE_MOD_1 — Greentide as its own RimMandrake-tier mod

Owner, 2026-09-11 card sitting (on the churnmud card), verbatim: "This is a
really cool mechanic and suggests making the Biome Greentide its own
RimMandrake level mod too."

## spec
- Package the Greentide biome + its kit (`design/Jawa/worldbuilding/biomes/
  kits/greentide_kit_spec.md`, all owner cards RULED 2026-09-11 — see its
  Owner rulings section: churnmud no-exemption, sealant from sap/resin,
  seek-shade AI + silence cue BOTH in v1) as its own RimMandrake-tier mod:
  packageId `mandrake.rm.<name>` per `design/NAMING_SCHEME_PLAN.md`, RM_
  prefixes for mechanisms; campaign-specific content (if any) stays RUT_ in
  the Utinni layer.
- The tier claim is the test: nothing in the mod may reference Star Wars or
  Utinni lore — Greentide must be playable on any RimWorld planet.
- Coordinate with `SHIP_VERMIN_MOD_1` / the ruled separate creature-behaviors
  assembly for where shared RM_ creature-AI classes live.

## verify
Mod folder with About.xml + packageId `mandrake.rm.*`; deploys via
deploy_custom_mods.py; no RSW_/RUT_ token and no Star Wars string inside;
kit mechanics all present per the spec's v1 list (including seek-shade and
silence cue, per the 2026-09-11 deferral rejection).

## criteria
Greentide loads and plays as a standalone RimMandrake mod; the Utinni
campaign consumes it as a dependency.
