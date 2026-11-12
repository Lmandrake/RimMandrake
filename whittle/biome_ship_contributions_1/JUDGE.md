# BIOME_SHIP_CONTRIBUTIONS_1: judge verdict, round 6

Judge: claude-opus-5-5, blind (I did not read DONE.md, BROADEN.md or other builder self-reports). 2026-11-12.
My own scratch: `D:\ClaudeWork\rimmandrake\judge_bsc1\` (rerun output, texture audit).

## Statement line

> Every-biome pass ... is done as `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md` says, shown by fresh evidence.

**true.** Here is what shows it, checked against the item's spec, verify and criteria:

- **Every shipped biome has a gift that can go on a ship (verify, first half).** I reran `python3 src/RimMandrake/Utils/ship_contributions.py` myself. It exited 0 with 24/24 PASS and 0 problems, and its output is line for line the same as `evidence/ship_contributions_run.txt` (only the header and footer differ). Its own selftest log says the 12 false lists each fail. I ran the selftest again (result below). The 24 is not a count that cannot see: I listed every mod that carries a `<BiomeDef`. The only ones outside Biomes.compose.json are TheBazaar (a `<BiomeDef>` in a comment only), Utils, and UtinniPatches (RUT_Umbra and the Jawa background water). None of those is a shipped biome mod.
- **The list matches what the mods ship (verify, second half).** I opened the defs behind the claims that are new or carry mechanics, and each one is backed:
  - The mast's ShadeGear comp exists, and `MaxCastCells = 16f` is in RM_MapComponent_ShadeGrid.cs.
  - The heat bank is a bare HeatPusher at 10/s, with no power or fuel comp.
  - The pattern hull has SelfhealHitpoints with ticksPerHeal 500. On a rare tick that comes to 120 HP a day.
  - The hexplate has Cleanliness 0.6.
  - The waste cask bay is a powered containment building, and Wastes C# exists that touches gravship launch.
  - The drive core is a GravshipFacility, and a StatPart multiplies GravshipRange.
  - The cold rack has no power comp (a ColdSink comp plus refuel).
  - The lanternstone floor and wall both carry glow.
  - The repulsor hardpoint is a variant of the Helix device and is stocked by RM_HelixCurators.
  
  The numbers in the prose agree with `evidence/prose_numbers_audit.md`.
- **Sweep and balance (spec, end of pass).** Two design-judge files are present and their fixes show in the table. The heater, water and light overlaps are each settled in their rows. The row the previous judge objected to now reads "five new builds", and exactly five rows are marked *new* (Cracked Lands, Long Shade, Pyrelands, Rust Cathedral, Sleeping Ice).
- **Card to the owner (spec).** The card is in `evidence/owner_card.md`, and the lane's OWNER_QUESTIONS.md mentions the item 5 times. It is not blocking and has not been answered.
- **Art.** Each claimed def points at a texture that exists in its mod.
  - Every PNG under `evidence/art/` and `evidence/art2/final/` is byte-identical to its installed copy under src/.../Textures. The summ great bone is installed under the def's own path, `SummGreatBone.png`.
  - None of the gift textures is a stand-in borrowed from another thing. Three are shared, all for good reason:
    - The lanternstone floor and wall share art with the natural lanternstone, which is the same material.
    - The repulsor hardpoint shares the Helix repulsor's art, which is the same device.
    - The solar still and sun lance own their art. The wringing still (a variant of the solar still) and the signal mirror borrow it from them, not the other way round.
  - I viewed the 96 ppc contact sheet and the glasswalk 2x2. Everything reads as what it claims to be. The glasswalk tiles with no visible seam, and the facings on the mast and the cask bay agree.

## Where the evidence is thin or flattering

- **No live play.** The README says so plainly. Nothing shows a gift placed, flown or working in a running game. That covers the mast's 16-cell lee, the cask bay's launch refusal, the drive core's range factor, the summ imprinting and the lanternstone glow on a deck. "Can stand on a deck" is checked offline against the engine's affordance rules, plus an effective-def load lint that passes. That suits an offline lane, but "worth landing for" is still the design judges' call, not play.
- **The art is shown in its best light.** The contact sheet shows each sprite alone on a flat backdrop, not on a deck next to vanilla things. The 48 ppc sheet partly makes up for that.
- **One small wording slip, in the evidence README only.** It says "20 pictures painted for the 14 stand-in gifts". The item itself correctly says 13 gifts plus the mast plus the retired lure awning. The text the owner sees (the item and the card) is consistent.
- **Process.** The 2026-11-03 owner note routed this item's design to the Designer. It was taken under Conductor authority instead, and the item says so openly. Option 4 on the card hands the owner that choice back. I record this as disclosed, not as a defect.

would show: yes
