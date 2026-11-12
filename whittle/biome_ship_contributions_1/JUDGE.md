# Blind judge: BIOME_SHIP_CONTRIBUTIONS_1 (round 2)

Judge: claude-opus-5-5, fresh, 2026-11-11. Read: STATEMENT.md, NOTES.md, the item file (spec/verify/criteria), every
file in evidence/ (all art viewed), and the defs behind several rows. Not read: DONE.md, BROADEN.md, earlier JUDGE text.
Reran: `python3 src/RimMandrake/Utils/ship_contributions.py` (exit 0, 24/24 PASS, matches ship_contributions_run.txt
line for line) and `python3 src/RimMandrake/Utils/selftest_ship_contributions.py` (PASS, 12 false lists each fail).

## The one statement line, split into what the item asks

"done as the item says, shown by fresh evidence": **false**. Its parts:

1. *Every shipped biome mod has at least one ship-buildable contribution* (verify): **true, offline only.** The checker
   reads the 24 biomes from Biomes.compose.json, reads the deck affordances from Odyssey's Substructure def, and
   checks placeWorkers, designation and bringAlongOnGravship; I reran it and got the same 24 PASS. effective_def_lint
   ends VERDICT PASS. Nothing was placed, flown or used in a game. A live check that builds a few rows on a deck and
   flies them would settle it fully.
2. *The list matches what the mods actually ship* (verify): **true for the defs; the prose is spot-checked only.**
   Every named def exists and passes. Rows I checked against their defs hold: pattern hull is CompSelfhealHitpoints
   ticksPerHeal 500, so 120 HP a day; the drive core is a CompProperties_GravshipFacility with a GravshipRange stat part;
   the sun-sphere glows (radius 6) and its C# says crops are lit through the vanilla glow grid. That the sun-sphere
   actually grows crops is cannot tell (needs a live light reading next to a grower).
3. *Sweep the set so every biome's gift is distinct and worth landing for* (spec): **cannot tell, leaning false.**
   The rows are distinct in function: the duplicate heaters are gone, and the two water machines and three hull items
   each have a different purpose. But the criterion is "the gravship becomes a scrapbook of everywhere it has been",
   and at least 11 of the 24 gifts still use borrowed or vanilla art (the defs say so): Wastes = the vanilla shelf,
   Leaning Scrub = the vanilla moisture pump, Cauldron = RM_LiquidTap, Terminal = RM_GlowTank, Warscar = the old-line
   turret base, Webwork = the web anchor, Weeping Stones = the corroded condenser, Abyss (every texture), Fever Wood (one
   flat-colour PNG), Long Shade (tinted tent), Sump tar vault (flat fill), Forge door (vanilla simple door). On a deck
   these look like other things, so the scrapbook does not show yet. Art may belong to other items, but neither the list
   nor the card says it is owed.
4. *Card the matrix to the owner* (spec): **false.** A card exists (evidence/owner_card.md), but it states a fact
   that is wrong. It marks **Weeping Stones "(your ruling)"**. The owner ruled the walking-condenser giant and its quests
   (OWNER.jsonl, WEEPINGSTONES_SCORING_SITTING_1, 2026-10-02: "I love (1)..."). He never chose the condenser plant as
   that biome's ship gift, and the item table's own source cell cites only the mod's text ("WeepingStones mod (its own
   text)"). The Abyss row has the same kind of source and is correctly marked *delegated*. The card would tell the
   owner he decided something he did not. The card also says nothing about the placeholder art in point 3, though that
   bears on its recommended option 1 ("every biome has a distinct, buildable gift").

## Evidence that is stale or flattering
- evidence/art/RM_SpunstoneHull.png is NOT the shipped texture: it differs from
  src/RimMandrake/TheForge/Textures/.../RM_SpunstoneHull.png and is the older atlas, which has a visible seam at every
  cell. The wallsim beside it does show the repo version (no seams). The verdict_spunstone_r2.md file judged an r2
  file that is not in evidence/. RM_SpunstoneParts.xml still has its header "PLACEHOLDER ART: ... the hull the vanilla
  ...", which is now false for the hull.
- The art shown is the five new or repainted textures, which are the best-looking of the set. The borrowed-art majority
  is not shown anywhere. Pattern hull: the "live pattern metal" cyan lines cannot be seen in the wallsim, so the
  self-mending fiction does not come across visually.
- Everything is offline (the README says so honestly). Nothing shows a gift doing its job.

## What would turn this to yes
- Fix the Weeping Stones label in the card (and in the table's source cell) to *delegated*.
- Add one line to the card and the list naming the gifts that still use borrowed or placeholder art, and the items
  that owe that art.
- Put the shipped spunstone atlas in evidence/art and fix the stale header in RM_SpunstoneParts.xml.

would show: no
