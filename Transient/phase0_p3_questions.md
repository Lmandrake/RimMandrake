# Phase 0 P3: Alpha Animals code-rider creatures, questions for the owner (2026-10-15)

Step P3 of `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md` §0.5.4. These are the creatures whose Alpha Animals
defs run on the donor's own C# (`AlphaBehavioursAndEvents.dll`) and still sit on a shipping (`RM_`) roster.
Done without asking (each def's header comment says what was kept, swapped and dropped):

| creature | biome | what was done |
|---|---|---|
| thunderbeast (`RM_Thunderbeast`) | Blue Desert | ported; flashstorm on death is our code; its static-arc attack and shock horn are ours. **Its temperature range was wrong**: the donor range (-10..61 °C) never overlapped the Blue Desert, so it could never spawn. It now uses the natives' cold range, which matches your description ("the same cold hydrocarbon chemistry"). |
| blistered bulloo (`RM_InfectedAerofleet`) | Contagion | ported; acid burst on death is our code |
| zhool (`RM_OcularJelly`) | Contagion | ported, one fixed picture (see Q1, Q2) |
| greater bulloo (`RM_ColossalAerofleet`) | The Forge | ported, one fixed picture (see Q1); keeps its gel and its fission into small bulloos |
| lastvine (`RM_Mantrap`) | Miasma | ported; **rears up**: it draws the calm closed pod at rest and the open thorn-ringed maw while it hunts, fights or has something close, as your Miasma sheet note asked. Our own small render code, with a Mod Settings switch. |

Art: every one of these already has a render of ours (none reuses donor pixels). They need installing at our own path
and your look on the Phase 0 sheet (O1): greater bulloo `gapall_AA_ColossalAerofleet_v1`, blistered bulloo
`enact_d3c59886_infectedaerofleet_v1` (your "redo"), zhool `gapall_AA_OcularJelly_v1` (your "B"), lastvine
`miasma_lastvine_calm_v1` + `miasma_lastvine_reared_v1` (not seen by you yet). Until they are installed, those four rows
stay tied to Alpha Animals and would disappear if it were removed first.

---

## Q1. The twitching tentacles: greater bulloo and zhool

On the donor-code sheet (2026-10-09) you picked "Rebuild behaviour" for these two (and the lastvine). The behaviour is
their tentacles twitching. The base game can do that twitch with no code of ours, but only if each tentacle is a
**separate small picture** drawn over a body that has no tentacles. Every picture of ours draws the tentacles as part
of one whole-body image. The lastvine got its rebuild a different way (calm and reared pictures).

- **A. One fixed picture, no twitch (what is in place now).** Uses the art you already picked. Nothing more to make.
  They look still in game.
- **B. Twitching tentacles.** We make new art for each: a body without tentacles, plus 3 or 4 tentacle pictures, all
  facings (about 15 to 20 renders per creature). The twitch then runs on the game's own system. Your picked art is
  replaced, and it needs another sitting.
- **C. Only the zhool twitches** (it is small and close to the ground, so the twitch shows); the greater bulloo stays
  one picture.
- Something else (write in).

## Q2. The zhool's red haze

Your description says the zhool "breathes out a faint reddish haze that turns whatever plant it touches into something
that shares its own strange flesh." That haze was Alpha Animals' own code (a gas that converts plants), so it is gone
from our port. The description still says it.

- **A. Rebuild it in our code.** The zhool leaves a faint red haze; plants inside it slowly turn into one of the
  Contagion's own flesh-plants. Needs a choice of which plants it makes (I would propose the Contagion's ocular flora).
  Small C# job.
- **B. Haze only, no conversion.** A red haze drifts around it as a look, using the game's own gas. The description
  loses the "turns plants" part.
- **C. Drop it.** No haze; I rewrite the description without it.
- Something else (write in).

## Q3. The crescendo anole's replacement (The Forge)

On the donor-code sheet you picked **"Cut & replace with new cast"** for the crescendo anole (the small lizard that
swells into a brute when it fights). It is still on The Forge roster at 0.5 as the donor creature, so it disappears
from The Forge when Alpha Animals is removed, leaving its slot (small ground animal) empty.

- **A. I draft two or three new Forge creatures for that slot**, with descriptions and a first render each, and you
  pick one on the Phase 0 sheet. Adds one row group to that sitting.
- **B. Leave the slot empty.** The Forge roster is one creature shorter.
- **C. Keep the anole after all, as a plain lizard that never swells** (port plain). The thing that made it worth
  having is gone.
- Something else (write in).

## Q4. The ondrukka's replacement (Miasma)

You also picked **"Cut & replace"** for the black swarmling, which your Miasma sheet renamed the **ondrukka** ("Picture
good, rewrite the description please and rename"). Its point was turning into a cocoon of another mod's hive
(VFE Insectoids 2), which is why it was cut. The Wasteland's copy was already replaced (`RM_SootGristleswarm`). The
Miasma row (0.5, vermin) still names the donor creature, so it disappears with Alpha Animals.

- **A. Keep the ondrukka as our own creature without the cocoon.** Your name and your picked picture stay; I rewrite
  the description so they are just grubs that swarm in the leaf-rot. It is no longer "the young of something larger."
- **B. A new Miasma vermin creature** for the slot. I draft two or three and you pick on the Phase 0 sheet.
- **C. Fill the slot with an existing Miasma creature's weight** (no new creature).
- Something else (write in).

---

Not asked, recorded: the five Alpha Animals goo/amoeba/spore creatures with code (green, red goo; small and large
amoeba; red spore) are only on the frozen `RUT_` campaign rosters, which are deleted at the one-time paint, so they are
not ported. The Explosive Growth rupture list still names `AA_RedGoo` (`RM_ExplosiveGrowthRoster.xml`); it is looked
up with a silent-fail lookup, so with Alpha Animals gone the rupture simply spawns zhools only. (The Contagion's own
red-goo host is already ours, `RM_BloodyMess`.)
