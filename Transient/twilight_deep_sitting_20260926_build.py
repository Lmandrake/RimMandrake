#!/usr/bin/env python3
"""Pre-fill generator for the Twilight Deep ruling sitting (2026-09-26).

Harvests every open question from the two design documents that closed today:
  design/Jawa/worldbuilding/biomes/the_twilight_deep_content_2026-09-26.md   (C)
  design/Jawa/worldbuilding/biomes/the_twilight_deep_bedazzle_2026-09-26.md  (B)

TWO generators, deliberately (review-sheets skill §7):
  --sheet      rebuilds the HTML.  ALWAYS SAFE; renders from the decisions file.
  --decisions  rebuilds the pre-fill.  DESTRUCTIVE once the owner has ruled — it is
               gated on --i-know-this-overwrites-the-owners-decisions and refuses
               outright if the file carries the sidecar's own savedBy/writeCount stamp.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.expanduser(
    "~/.claude/skills/review-sheets/assets/sheet_template.html")
SHEET = os.path.join(HERE, "twilight_deep_sitting_2026-09-26.html")
DECISIONS = os.path.join(HERE, "twilight_deep_sitting_2026-09-26.decisions.json")
DECISIONS_NAME = os.path.basename(DECISIONS)

C = "content pass §"          # the_twilight_deep_content_2026-09-26.md
B = "marquee pass §"          # the_twilight_deep_bedazzle_2026-09-26.md

# ── the rows ─────────────────────────────────────────────────────────────────────────
# Each row: id, label, group, effect (one-line consequence, also the search text),
#           question (plain language, no defNames unless the name IS the question),
#           options [{k, text, rec}], prefill, chips {source, cost, ban, conflict, gating}
#           contested (defensible both ways / the two docs disagree)

G_GATE = "1 · Decide these first — they change the other answers"
G_CONF = "2 · Where the two documents disagree"
G_RIVR = "3 · The river that carries you"
G_FARM = "4 · Farming, cages and the grown light"
G_LIFE = "5 · Creatures, plants and the catch"
G_WHAL = "6 · The gardener and its passing"
G_DEEP = "7 · The Deepwater and their permits"
G_SETS = "8 · Settings"

ROWS = [

# ══ 1 · GATING ══════════════════════════════════════════════════════════════════════
dict(
  id="floor_persistence", group=G_GATE,
  label="Does a sea floor stay yours between dives?",
  effect="A measured engine defect: one gravship can currently only ever visit ONE sea floor. "
         "Your answer picks the fix, and decides whether anything built under the sea survives.",
  question=(
    "When your gravship opens a dive hatch and your people go down, the sea floor they arrive on is "
    "a map the game makes once and then remembers. It remembers it by the <b>hatch</b>, not by the "
    "place. So a ship that dives the Twilight, flies to the Grey Sea and dives again arrives back on "
    "its <i>Twilight</i> floor. That is a real defect, measured out of the engine today and already "
    "filed. Fixing it means first saying what a sea floor <i>is</i>."),
  options=[
    dict(k="a", rec=True, text=(
      "<b>One floor per sea, kept forever.</b> The hatch remembers a separate floor for each sea you "
      "have visited, and everything you built down there — a kelp plot, a claim buoy, a mooring the "
      "Deepwater granted you — is still standing next time. <i>Costs a small-to-medium piece of new "
      "code: the hatch has to keep a little register of which floor belongs to which place.</i>")),
    dict(k="b", text=(
      "<b>A fresh floor every dive.</b> The old one is thrown away when the ship launches. Cheapest "
      "possible fix and the bug can never come back — but nothing under the sea survives, which "
      "deletes skylight tenancy (the headline idea), the kelp farm, the sea-pen and every mooring or "
      "lamp the Compact could ever grant you. <i>Near-zero cost.</i>")),
    dict(k="c", text=(
      "<b>One ship, one sea, for good.</b> The ship's first dive picks its ocean and it can never dive "
      "another. <i>Cheapest of all, and the most limiting thing in the list.</i>")),
  ],
  prefill="a",
  chips=dict(source=f"{B}6 Q8, {B}2", cost="A: small–medium C#. B/C: near-zero.",
             gating="Decides whether ANY build-under-the-sea idea can exist, and the fix shape for the "
                    "filed defect SEADIVEHATCH_CACHES_FIRST_SEA_FLOOR_1."),
),

dict(
  id="canopy_name", group=G_GATE,
  label="What is the living ceiling called?",
  effect="You already ruled the ceiling stays and stops being mold. The NAME is still open — and about "
         "eleven pieces of shipped prose wait on it.",
  question=(
    "You have ruled that the ceiling stays and that the word <i>mold</i> goes: it is a living canopy in "
    "lustrous blue-green. It still needs a name, and the name has to carry into roughly eleven pieces of "
    "writing that already ship — the ocean's own description, four creature descriptions, six catch "
    "items, and the frozen sheet. The proposal is <b>the oolune</b>: one organism shore to shore, seen "
    "from below as a living stained-glass ceiling — translucent blue-green, veined gold where the sunset "
    "strikes it, thick and opaque where it is old, thin and luminous where it is new, its skylights "
    "rimmed pale the way a wound in kelp is rimmed pale. The Deepwater call it <i>the lid</i>. What it "
    "sheds is <i>veil-fall</i>, and the word every description reaches for is <i>veil</i> — never "
    "<i>mat</i>, never <i>mold</i>."),
  options=[
    dict(k="a", rec=True, text="<b>Oolune, and the veil vocabulary.</b> The eleven rewrites go ahead as one pass."),
    dict(k="b", text="<b>Keep the look, change the word.</b> Type your name in the box; the rewrites wait for it."),
    dict(k="c", text="<b>Keep the name, change what the Deepwater call it</b> (“the lid” / “veil-fall”). Type theirs."),
    dict(k="d", text="<b>Keep the name and the look, but the description should read differently.</b> Say how."),
  ],
  prefill="a",
  chips=dict(source=f"{C}2.1, {C}10.2-1, {C}11 Q1",
             cost="No code. About eleven prose rewrites across shipped defs, one pass.",
             gating="Eleven shipped descriptions and an edit to the frozen sheet wait on the word."),
),

dict(
  id="top_three", group=G_GATE,
  label="Do the three headline ideas stand, in that order?",
  effect="Sets the build queue for the whole ocean and decides which shared plumbing gets paid for first.",
  question=(
    "Seven big ideas were designed for this ocean and three were picked to build first. "
    "<b>(1) Skylight tenancy</b> — you never own a golden shaft of light, you hold one until the ceiling "
    "drifts and closes it; the lit ground beneath is the only fast-growing, fish-crowded ground on the "
    "floor. <b>(2) The Compact's permits</b> — the Deepwater do not sell you the Deep, they admit you to "
    "it one right at a time and can take each one back. <b>(3) The Ark Seed</b> — carry a breeding pair "
    "of the last living sea home in a tank and keep it alive. The fourth idea, <b>living light</b> (a "
    "glowing creature kept in a tank, nearly free because the pigment mod already ships the tank), is "
    "the swap-in if the Ark Seed turns out expensive."),
  options=[
    dict(k="a", rec=True, text="<b>All three, in that order.</b> Tenancy and permits pay for most of the rest."),
    dict(k="b", text="<b>Tenancy and permits first; living light third.</b> The Ark Seed waits until its one "
                     "unmeasured engine question has been read."),
    dict(k="c", text="<b>A different three.</b> Say which in the box — the other four are the dry river as a "
                     "travel lane, the gardener's events, living light, and the Compact's charts and ledgers."),
    dict(k="d", text="<b>Tenancy and permits only for now.</b> Nothing third; revisit when those two are in."),
  ],
  prefill="a",
  chips=dict(source=f"{B}0, {B}6 Q9",
             cost="1 small–medium · 2 medium · 3 medium–high with an unmeasured engine gate · 4 small.",
             gating="Decides the build queue and what shared machinery gets built once."),
),

dict(
  id="seaweed_cut", group=G_GATE,
  label="Fourteen seaweeds were drawn; you asked for twelve.",
  effect="Which two go. Sets the flora build list.",
  question=(
    "Fourteen seaweed analogs were designed deliberately so that two could be cut. What each one is "
    "<i>for</i>:<br>"
    "<b>oruvell</b> — the kelp proper: food fronds and the wet lattice-timber the Deepwater build with; "
    "grows only in the light shafts.<br>"
    "<b>ghallowyn</b> — a hollow fluted pillar, the timber tree; so slow-growing that a stand of them is "
    "a family's generational wealth, and a dead one is what they stand their lamps and chimneys in.<br>"
    "<b>hoolimbre</b> — ropes of glowing bladders; harvest one and you have a torch that lasts days.<br>"
    "<b>noothelm</b> — one lantern bulb on a stalk, and it is sowable: you can plant light.<br>"
    "<b>sennefan</b> — a sail-fan; gives sea-silk cloth, and a field of them all facing one way shows a "
    "diver which way the current runs.<br>"
    "<b>ummarel</b> — rafts drifting under the ceiling that sweep shadows across the floor; on the floor "
    "itself it appears only as sunk waterlogged tangles.<br>"
    "<b>waelune</b> — a glowing weed-ball that rolls along the floor and piles up against walls.<br>"
    "<b>thessmoss</b> — grazing turf for the herbivores; it stops dead at the river's stake-line, which "
    "is itself a safety tell.<br>"
    "<b>murrgrave</b> — lace that grows only on the richest ground, so finding it is finding where to "
    "plant.<br>"
    "<b>vaalstone</b> — a glassy crust that makes the whole floor under a shaft glitter; scraped, it is "
    "the green pigment the Compact draw their charts in.<br>"
    "<b>skirroth</b> — tangle-rope that slows you down and gives net-cord.<br>"
    "<b>illuvane</b> — the herbal-medicine plant, the hospital ward's stock.<br>"
    "<b>sarrowhisk</b> — bait; the fish are visibly thickest where it grows.<br>"
    "<b>quellith</b> — the one that stings."),
  options=[
    dict(k="a", rec=True, text="<b>Cut ummarel and ghallowyn.</b> Ummarel's floor form is thin (a sunk tangle "
                               "and nothing else), and ghallowyn's timber folds into the oruvell."),
    dict(k="b", text="<b>Keep all fourteen.</b> Twelve was a floor, not a ceiling."),
    dict(k="c", text="<b>Cut two others.</b> Name them in the box."),
    dict(k="d", text="<b>Cut more than two.</b> Name them."),
  ],
  prefill="a",
  chips=dict(source=f"{C}3, {C}11 Q5", cost="Each plant is about one def and one piece of art. No code.",
             gating="Sets the flora build list (build steps 4, 5, 10 and 15)."),
),

# ══ 2 · CONFLICTS ═══════════════════════════════════════════════════════════════════
dict(
  id="growing_light", group=G_CONF, contested=True,
  label="Can you farm your own sunlight — and does that kill the skylight?",
  effect="CONFLICT. One document makes holding a shaft of light the headline idea; the other invents a "
         "lamp you grow that 'frees the player from the skylight economy'. Both cannot be fully true.",
  question=(
    "The content pass says plants grow only where there is light, so the golden shafts are the only good "
    "farmland — which is precisely what makes a shaft worth holding. It then adds the <b>sun-sphere</b>: "
    "a glass ball of glowing micro-organisms you grow yourself until it is bright as day, and its own "
    "text says it <i>“frees the player from the skylight economy”</i>. The marquee pass, written "
    "the same day and without knowing about the sun-sphere, makes holding a shaft the number-one idea in "
    "the ocean and the thing the Deepwater meter you on. <b>If a farmed lamp equals a skylight, the shaft "
    "stops being worth holding</b> — and with it goes the reason the Compact has any leverage."),
  options=[
    dict(k="a", rec=True, text=(
      "<b>Light gates growing; the sun-sphere is real daylight but dear and late.</b> Two techprints sold "
      "only by the Compact, a real feed cost, and it lights a small area — so it frees a homestead, never "
      "a farm. The shaft stays the good ground.")),
    dict(k="b", text=(
      "<b>The sun-sphere is dimmer than a shaft.</b> It keeps plants alive and slow; only real skylight "
      "gives full growth. The cleanest protection of the tenancy idea, and the weaker half of a nice toy.")),
    dict(k="c", text=(
      "<b>Farmed light equals a skylight.</b> Simplest and most generous to the player; the tenancy idea "
      "then has to earn its place on fishing and beauty alone.")),
    dict(k="d", text="<b>No sun-sphere.</b> Cut it and keep the ocean's light entirely in the ceiling's gift."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.2 vs {B}3.1 / {B}0",
             cost="The sphere is a planter def plus the base game's sun-lamp glow. A and B differ only by "
                  "a number. No new code either way.",
             conflict="content §13.2 (written later) undercuts marquee §3.1 (ranked #1)."),
),

dict(
  id="fishing_where", group=G_CONF, contested=True,
  label="Where can you actually fish?",
  effect="CONFLICT. One document says fishing happens only in the lit columns; the other puts the "
         "second-richest fishing on a river weir, outside any shaft.",
  question=(
    "The content pass says fishing happens only in the lit water columns — <i>“nets in the light "
    "columns”</i> is the frozen sheet's own phrase, and it is another reason a shaft is worth "
    "holding. The marquee pass gives the river <b>weirs</b>: the Deepwater drop a bundle in the channel "
    "upstream and collect it at a weir on a bank-eddy downstream, and it calls a fishing zone on a weir "
    "<i>“the biome's second-richest fishing after the wells”</i>. That is fishing well outside "
    "any shaft."),
  options=[
    dict(k="a", rec=True, text="<b>Shafts only.</b> One rule, easy to learn, and it protects the shaft's "
                               "value. The weir stays — as freight, not fishing."),
    dict(k="b", text="<b>Shafts and weirs.</b> Two fishing grounds with different characters: the shaft is "
                     "yours and temporary, the weir is the Compact's and needs their leave. Costs one more "
                     "building and making a bank-eddy hold water."),
    dict(k="c", text="<b>Fish anywhere there is water.</b> Simplest, and the shaft loses one of its two "
                     "reasons to exist."),
  ],
  prefill="a",
  chips=dict(source=f"{C}11 Q9 / {C}10.2-7 vs {B}3.5",
             cost="A: nothing beyond what is planned. B: the weir building plus water on a bank-eddy.",
             conflict="content §11 Q9 vs marquee §3.5."),
),

dict(
  id="living_decor_neglect", group=G_CONF, contested=True,
  label="Does a picked plant you take home stay alive on its own?",
  effect="CONFLICT. Your word was 'easily' — so one document makes living decor immortal. The other "
         "document's organising law for this whole ocean is that nothing here keeps itself.",
  question=(
    "You said underwater plants stay alive after you pick them, so you can decorate with a living plant "
    "<i>easily</i>. The content pass takes that at its word: a luminous vine laid along a wall never dies, "
    "needs nothing, and glows forever — no fuel bill, in any room, a thousand cells from any water. The "
    "marquee pass's organising rule for this entire ocean is the opposite: <i>“every reward here is "
    "alive, renewable, expiring or relational — something you keep only while you keep it”</i>, with "
    "the explicit test <i>“if a reward survives in a stockpile with nobody tending it, it belongs to "
    "the Grey Sea, not here.”</i> A vine that lives forever untended fails that test outright."),
  options=[
    dict(k="a", rec=True, text="<b>Never dies.</b> Your word was <i>easily</i>; a living cutting is a sealed "
                               "organism that simply keeps. The marquee pass's rule bends here."),
    dict(k="b", text="<b>Never dies, but it goes dark.</b> In a room with no light the luminous ones dim to "
                     "plain green — still alive, still beautiful, no longer a lamp. Keeps <i>easily</i> and "
                     "keeps a reason to go back down. <i>This is the reconciliation the conflict suggests; "
                     "nobody has proposed it as a position.</i>"),
    dict(k="c", text="<b>It needs light or water.</b> Living decor dies from real neglect, like the glow tank "
                     "does. Honest to the marquee rule, harshest to play, and furthest from your word."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.3 / {C}13.7 Q15 vs {B}1",
             cost="A: none, pure XML. B: a small condition on the glow. C: reuse the tank's existing "
                  "vitality behaviour on a building.",
             conflict="content §13.3's position fails marquee §1's stated test for this biome."),
),

# ══ 3 · THE RIVER ═══════════════════════════════════════════════════════════════════
dict(
  id="river_lane", group=G_RIVR, contested=True,
  label="May a colonist ride the current on purpose?",
  effect="You ruled the channels carry you. Open: whether that is a ROAD players use, or a HAZARD they "
         "avoid. The wide reading is outside hard ban 3's plain wording.",
  question=(
    "You have ruled that the channels look like dry riverbeds but the denser water in them still carries "
    "a pawn along. What is still open is whether that is a <b>road</b> or a <b>hazard</b>. The frozen "
    "sheet's hard ban 3 says: <i>“no swimmable river — entering a bottom channel means sinking with "
    "it; harvest and travel happen on the banks.”</i> If the current is a road, players will use it "
    "as free one-way freight across the floor — which is exactly what the Deepwater do. If it is only a "
    "hazard, the identical code runs and nobody chooses it."),
  options=[
    dict(k="a", rec=True, text=(
      "<b>Hazard only — inside the ban's wording.</b> Things dropped in are carried, so the Compact's "
      "freight trick works and you can copy it by hand; but a colonist who steps in is <i>swept</i>, never "
      "travelling, and never routes through a channel on purpose.")),
    dict(k="b", text=(
      "<b>A real lane.</b> A colonist can deliberately ride a channel one way across the floor. The better "
      "experience, outside the ban's plain words, and it needs the ban amended at this sitting.")),
    dict(k="c", text=(
      "<b>Freight only; pawns cannot enter at all.</b> Safest, and it throws away the moment where someone "
      "steps on dry-looking mud and is carried thirty cells away.")),
  ],
  prefill="a",
  chips=dict(source=f"{B}5.1 / {B}6 Q1, {C}2.2",
             cost="Identical code either way — a flow grid and a component that moves things one cell at a "
                  "time. What changes is what the pathfinder is allowed to plan.",
             ban="Hard ban 3 — option B breaks its plain wording and needs it amended."),
),

dict(
  id="river_sink", group=G_RIVR,
  label="What happens to a colonist carried to the end?",
  effect="Ban 3's words are 'sinking with it'. Is that a body you can go and fetch, or a colonist lost?",
  question=(
    "Every channel ends in a sink. Hard ban 3's words are <i>“sinking with it”</i>. The question "
    "is whether that means a body someone can go down the bank and carry out, or a colonist who is simply "
    "gone."),
  options=[
    dict(k="a", rec=True, text=(
      "<b>Recoverable and dangerous.</b> They are dumped in the sink basin with a worsening condition — "
      "cold-and-drowning shaped, movement falling — and somebody has to come and carry them out. They can "
      "still die if nobody comes. A harsher setting for players who want death. <i>This matches the ruling "
      "you already gave for the Grey Sea's encasement.</i>")),
    dict(k="b", text=(
      "<b>Lost.</b> Carried past the last eddy and gone. Simplest to build and the strongest lesson; also "
      "the one that turns one bad pathfinding afternoon into a dead colonist.")),
    dict(k="c", text=(
      "<b>Harmless.</b> They wash up on the bank downstream, wet and annoyed. Cheapest, and the river stops "
      "being the thing the frozen sheet says it is.")),
  ],
  prefill="a",
  chips=dict(source=f"{C}2.2 / {C}11 Q2",
             cost="A: one injury type plus a rescue that can chase a moving pawn. B and C: less."),
),

dict(
  id="river_build_order", group=G_RIVR,
  label="Build the river's LOOK before its danger?",
  effect="Splits the one genuinely expensive mechanism in this ocean into a cheap visible half and a "
         "costly half.",
  question=(
    "The current is the only genuinely new movement system here — a medium piece of code touching "
    "pathfinding, hauling, downed pawns, animals and saving. The part that makes it <i>look</i> like a "
    "river is cheap and is the part you actually asked to see: banked braided mud, fertile bank silt, the "
    "Deepwater's lamp-stakes every eight cells marking exactly where the pushing starts, and litter "
    "visibly skating along the bed so you can see the floor is moving."),
  options=[
    dict(k="a", rec=True, text="<b>Terrain, banks and tells first; the current second</b> — and never ship "
                               "the riverbed without at least the stake-line to warn people."),
    dict(k="b", text="<b>Both together.</b> One thing lands, later, complete."),
    dict(k="c", text="<b>Current first.</b> The dressing can follow."),
  ],
  prefill="a",
  chips=dict(source=f"{C}10.2-3, {C}2.2",
             cost="A splits one medium item into a cheap visible half and an expensive half."),
),

# ══ 4 · FARMING ═════════════════════════════════════════════════════════════════════
dict(
  id="cage_chain", group=G_FARM,
  label="The cage's chain — anchored down, or hung from above?",
  effect="Decides where a floating farm may be placed. Same picture from directly overhead either way.",
  question=(
    "You described floating cube or sphere cages with a chain leading down to a tether. That reads two "
    "ways: a cage that <b>floats and is chained down</b> to an anchor on the sea floor, or a cage "
    "<b>hung on a chain from a float</b> on the surface far above. Seen from directly overhead, which is "
    "how the game is drawn, the picture is identical."),
  options=[
    dict(k="a", rec=True, text="<b>Chained down to a floor anchor.</b> A cage can then sit above anything at "
                               "all — above the river channel you cannot farm, above a kelp stand, above a "
                               "house — because it only needs somewhere to put the anchor."),
    dict(k="b", text="<b>Hung from a surface float.</b> Truer to the words, and it means a cage can only hang "
                     "where open water runs all the way up — fewer places, and the ceiling is in the way."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.1 / {C}13.7 Q13", cost="Same def either way; art and placement rules differ."),
),

dict(
  id="cage_passable", group=G_FARM,
  label="Do your people walk underneath a cage?",
  effect="The floating farm costs no floor space only if pawns can walk under it. That is slightly odd "
         "to look at in a top-down game.",
  question=(
    "The whole reason you liked floating farms is that they do not use up floor space. For that to be "
    "true in a top-down game the cage has to be drawn <i>above</i> your people, so a colonist walks "
    "underneath it and stands under the crop to tend it. The cell keeps every other use — walk it, haul "
    "across it, run a path through it — you just cannot put a second building there."),
  options=[
    dict(k="a", rec=True, text="<b>Walk under it.</b> It is the whole point of your sentence. A setting for "
                               "players who find it odd."),
    dict(k="b", text="<b>It occupies its cells, like hydroponics.</b> Nothing looks strange, and the cage "
                     "becomes an ordinary planter with a chain drawn on it."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.1 / {C}13.7 Q14", cost="Both pure XML."),
),

dict(
  id="sunsphere_feed", group=G_FARM,
  label="Does the sun-sphere run on power, or does it eat?",
  effect="Decides whether a sea-floor farm needs a generator down there, or whether your fishery feeds "
         "your light and your light feeds your farm.",
  question=(
    "The sun-sphere is a ball of glowing micro-organisms you grow until it is bright as day — you watch "
    "your light get brighter as it matures. Its smaller sibling, the pigment tank that already ships, "
    "runs on electricity and dies when the power lapses."),
  options=[
    dict(k="a", rec=True, text=(
      "<b>Fed, not powered.</b> You put raw floor food into it — gathered ceiling-fall, or any raw fish. "
      "Starved, it dims over days and dies back to a husk you can re-seed, rather than snapping off. So "
      "your fishery feeds your light and your light feeds your farm: one loop, and no power cable under "
      "the sea.")),
    dict(k="b", text="<b>Powered, like the glow tank.</b> Consistent with the thing it is descended from, "
                     "and it means every sea-floor farm needs a generator beside it."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.2 / {C}13.7 Q16",
             cost="A: the base game's refuelling behaviour plus a dimming curve. B: already-shipped behaviour."),
),

dict(
  id="techprints", group=G_FARM,
  label="Must you buy Deepwater technology before you can build it?",
  effect="Makes the cages and the sun-sphere read as THEIR engineering rather than yours.",
  question=(
    "The cages, the tethers and the sun-sphere are meant to read as Deepwater engineering — the thing a "
    "diver sees working at their houses and cannot build. The base game's own mechanism for that is a "
    "<b>techprint</b>: a document you must buy before the research will unlock. The proposal is one print "
    "for tethering and two for the sun-sphere, because the sphere is the thing that frees you from needing "
    "their skylights and they know it — both sold only by the Compact."),
  options=[
    dict(k="a", rec=True, text="<b>Yes — Compact-only sellers, one print for the cages, two for the sphere.</b>"),
    dict(k="b", text="<b>Compact-only, one print each.</b> Less friction, and the sphere stops being the dear one."),
    dict(k="c", text="<b>No techprints; research it yourself.</b> Then it stops being <i>their</i> technology."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.5 / {C}13.7 Q19",
             cost="Pure XML; the Compact-only seller is a small patch on their trader stock."),
),

# ══ 5 · CREATURES, PLANTS, CATCH ════════════════════════════════════════════════════
dict(
  id="two_shoals", group=G_LIFE,
  label="Two silver shoal fish, one niche.",
  effect="They read as one creature under two names. Split them by light, or fold them into one?",
  question=(
    "Two silver shoal fish occupy the same niche. One is catch-only and carries the older, richer writing "
    "— <i>“the silver of the Twilight”</i>. The other was built with a real body two days ago — "
    "<i>“seen as a shoal, never as an individual”</i>. As written they are one creature wearing "
    "two names."),
  options=[
    dict(k="a", rec=True, text=(
      "<b>Keep both, split by light.</b> One is the <i>lit</i> shoal of the golden shafts — blue-white, and "
      "it flashes. The other is the <i>dark</i> shoal of the water between — dull silver, no glow, and it "
      "is what the predator hunts. Two halves of one floor, and it makes the predator's description true.")),
    dict(k="b", text="<b>One shoal.</b> The built body takes the better name; one fish, one word."),
  ],
  prefill="a",
  chips=dict(source=f"{C}10.2-4 / {C}11 Q3", cost="A: one extra body and spawn entry. B: a rename."),
),

dict(
  id="waelune", group=G_LIFE,
  label="The rolling glowing weed-ball — plant or animal?",
  effect="A plant cannot move in this engine. Either it teleports quietly every few days, or it is a "
         "slow harmless creature.",
  question=(
    "The waelune is a glowing weed-ball, fist- to cushion-sized, that rolls along the floor with the "
    "current and piles up in drifts against towers and house walls. A floor with waelune on it has moving "
    "lights on it. But a plant cannot move in this engine."),
  options=[
    dict(k="a", rec=True, text=(
      "<b>A creature.</b> Slow, tame, unafraid — it genuinely rolls, it rides the channels as a native "
      "species that the current does not hurt, it gives the Deepwater children something to chase, and "
      "carried home it is the pet that is a lamp.")),
    dict(k="b", text="<b>A plant that quietly teleports</b> a few cells downstream every few days. Cheaper, "
                     "and it will look like a bug the first time somebody watches one."),
  ],
  prefill="a",
  chips=dict(source=f"{C}3.7 / {C}11 Q11", cost="A: one race and spawn entry, no code."),
),

dict(
  id="clinging_layer", group=G_LIFE,
  label="Six tiny creatures living on the plants — right number?",
  effect="The 'lots of little things' layer. Six rows on the roster, each nearly free.",
  question=(
    "Six tiny creatures were designed to live on the plants themselves — the sort of thing you only notice "
    "when it moves: one in the glowing bladders, one on the sail-fans, one in the tangle-rope, one in the "
    "lace on the rich ground, and so on. Four of them are also things you can catch and eat."),
  options=[
    dict(k="a", rec=True, text="<b>Six.</b> They are tiny, and half of them are invisible until they move."),
    dict(k="b", text="<b>Fewer.</b> Say how many in the box."),
    dict(k="c", text="<b>More.</b> Say what else should be down there."),
  ],
  prefill="a",
  chips=dict(source=f"{C}4 / {C}11 Q6",
             cost="One creature each plus four catch items. No code; they share one seeding rule."),
),

dict(
  id="unlimited_fishing", group=G_LIFE,
  label="'Prolific and unlimited' — in practice, or literally?",
  effect="Literally unlimited makes this sea different in kind from the Grey and the Scald, where the "
         "catch is finite.",
  question=(
    "You said fishing here is prolific and unlimited. There are two readings. <b>Unlimited in practice</b> "
    "means a very high population and fast regrowth: you will never fish it out by playing normally, but "
    "the number is real and someone determined could. <b>Literally unlimited</b> means the sea never "
    "depletes at all — which needs a patch, and makes this ocean different in kind from the Grey and the "
    "Scald, where the catch runs down."),
  options=[
    dict(k="a", rec=True, text="<b>Unlimited in practice by default</b>; the literal version behind a setting "
                               "for anyone who wants it."),
    dict(k="b", text="<b>Literally unlimited, shipped.</b> This is the one sea that is alive, and you meant it."),
  ],
  prefill="a",
  chips=dict(source=f"{C}5 / {C}11 Q4", cost="A: numbers. B: a small patch on the fishing model."),
),

dict(
  id="hazard_plant", group=G_LIFE,
  label="One plant that hurts, in a pretty ocean.",
  effect="The quellith. Low damage. The Grey Sea owns 'everything here can kill you'.",
  question=(
    "One plant on this floor hurts you: a hanging curtain of translucent blue-green tissue threaded with "
    "fine white stinging lines. Beautiful, low damage, and the shelter of one small fish that is immune to "
    "it and gets netted along with it. The argument for exactly one is that this is a pretty ocean, and "
    "the Grey Sea already owns <i>everything here can kill you</i>."),
  options=[
    dict(k="a", rec=True, text="<b>One hazard plant, low damage.</b>"),
    dict(k="b", text="<b>None.</b> The little fish then loses its shelter and moves into the tangle-rope instead."),
    dict(k="c", text="<b>More than one.</b> Say what else should bite."),
  ],
  prefill="a",
  chips=dict(source=f"{C}3.14 / {C}10.2-8",
             cost="Reuses a contact-damage behaviour that already ships. No code."),
),

# ══ 6 · THE GARDENER ════════════════════════════════════════════════════════════════
dict(
  id="whale_sequence", group=G_WHAL,
  label="The gardener's passing — the five-beat sequence.",
  effect="Your whole description written out as a timed hour-long event. The drawn moving shadow is the "
         "one separate, art-led piece.",
  question=(
    "You described the whale's shadow leading to eerie booming sounds and little light, animals freaking "
    "out, then raining detritus and glowing barnacles like gems, and the whole ecosystem going into "
    "overdrive eating them. Written out as a timed sequence about an hour long:<br>"
    "<b>1 — the booming.</b> Slow calls through the ceiling and a neutral letter: the gardener is "
    "overhead.<br>"
    "<b>2 — little light.</b> Every skylight dims to a fifth and the whole floor darkens, so the "
    "creatures' own glow is suddenly all the light there is.<br>"
    "<b>3 — animals freak out.</b> Shoals scatter, the grazers bolt, the predator goes to ground, the "
    "clingers vanish into their hosts. The Deepwater stand outside and watch.<br>"
    "<b>4 — the rain.</b> For about a minute and a half things fall through the shafts: sheets of "
    "ceiling-fall, thumb-sized biting parasites shaken off its hide, and fist-sized barnacles with "
    "glowing gems in them.<br>"
    "<b>5 — overdrive.</b> Every animal on the floor goes into a feeding frenzy and eats the fallen, fast "
    "— so hauling the barnacles before the ecosystem does is a race. And for that hour the floor's "
    "predator hunts things it never normally would, your people included if they are standing in the dark "
    "between shafts.<br>"
    "All of it runs on machinery the base game already has. The one separate piece is the moving shadow "
    "actually <i>drawn</i> across the floor, which is art-led and wants your eyes on a mockup."),
  options=[
    dict(k="a", rec=True, text="<b>Build the five beats now; the drawn moving shadow later</b>, after a "
                               "mockup you watch."),
    dict(k="b", text="<b>All five beats and the drawn shadow together.</b> One landing, later."),
    dict(k="c", text="<b>Trim it.</b> Say which beats to keep in the box."),
    dict(k="d", text="<b>The simple version only</b> — it goes dark and a letter arrives."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.4, {C}11 Q7, {B}3.6",
             cost="A: one incident, one condition, one frenzy effect, and a falling-things route that must "
                  "be read out of the base game before it is written. Small–medium. The drawn shadow is "
                  "art plus a small overlay."),
),

dict(
  id="whale_label", group=G_WHAL,
  label="Is it the lanternwhale or the Twilight Gardener?",
  effect="The creature already ships under one name; every design document calls it the other.",
  question=(
    "The creature already ships as the <b>lanternwhale</b> — moss-shrouded, trailing blue lantern "
    "tendrils, and <i>“it does not notice you; that is the whole of its character, until you make "
    "it.”</i> The roster asks for a <i>Twilight Gardener</i> label instead, and every design document "
    "calls it <i>the gardener</i>."),
  options=[
    dict(k="a", rec=True, text="<b>Both.</b> The animal stays <i>lanternwhale</i>; the Deepwater call it "
                               "<i>the gardener</i>; the description carries both, which is how a real "
                               "creature gets two names."),
    dict(k="b", text="<b>Rename it the Twilight Gardener.</b>"),
    dict(k="c", text="<b>Something else.</b> Type it."),
  ],
  prefill="a",
  chips=dict(source=f"{C}10.2-9", cost="A label edit."),
),

dict(
  id="gardener_agency", group=G_WHAL,
  label="Does the gardener open and close the skylights itself?",
  effect="Turns the shaft's expiry from a hidden timer into something with a visible cause — at the cost "
         "of giving a placid animal real agency.",
  question=(
    "Under the ruled canopy the gardener's job is to tend the living ceiling. The design goes further: "
    "when it grazes overhead a new skylight <b>opens</b> beneath it, and when it patches a tear one "
    "<b>closes</b> — perhaps the one you were farming under. So a shaft's expiry stops being a hidden "
    "timer and becomes something with a cause you can watch pass over your head. The argument against is "
    "that this is a great deal of agency for an animal the frozen sheet calls placid and indifferent."),
  options=[
    dict(k="a", rec=True, text="<b>Keep it.</b> It is precisely the frozen sheet's own line that the "
                               "gardener decides which skylights exist."),
    dict(k="b", text="<b>It only closes wells, never opens them.</b> New wells drift open on their own; the "
                     "gardener is the thing that takes them away."),
    dict(k="c", text="<b>It does neither.</b> The ceiling drifts on its own clock and the gardener is "
                     "scenery that keeps the ban true."),
  ],
  prefill="a",
  chips=dict(source=f"{C}10.2-11, {B}3.6",
             cost="Same component either way; A wires two events into it.",
             ban="Touches hard ban 2 (no roof without the gardener) — option A strengthens the pairing."),
),

dict(
  id="gardener_studiable", group=G_WHAL,
  label="Can the gardener be studied rather than touched?",
  effect="A reward for patience in a biome whose keeper wants to be left alone — and the only free route "
         "to knowledge the Compact otherwise sells.",
  question=(
    "A patient researcher could learn the gardener's ways simply by watching it — where it grazes, which "
    "lanes it crushes flat beneath it — using a study mechanic the base game already has. That would be a "
    "reward for leaving something alone, in an ocean whose keeper wants exactly that, and it would be the "
    "only way to learn the gardener's lanes without buying a chart from the Deepwater."),
  options=[
    dict(k="a", rec=True, text="<b>Yes, and it is the only free route</b> to that knowledge."),
    dict(k="b", text="<b>Yes, but smaller.</b> Study gives research progress, not the lanes; the chart stays "
                     "the only way to see them."),
    dict(k="c", text="<b>No.</b> Charts are the Compact's to sell, and that is the point of them."),
  ],
  prefill="a",
  chips=dict(source=f"{B}3.6 / {B}6 Q6", cost="An already-shipped behaviour plus a small unlock. Small."),
),

dict(
  id="dead_gardener", group=G_WHAL, contested=True,
  label="If a player kills the last gardener, what happens?",
  effect="The only irreversible act available in this ocean — and the row where hard ban 2 gets its "
         "reading.",
  question=(
    "If a player kills the last gardener, what happens? The design deliberately does <i>not</i> collapse "
    "the ceiling — that would delete the biome. Instead the skylights simply stop opening: the ones that "
    "exist close over the years and no new ones ever come, so the floor's light only shrinks from that day "
    "on, permanently, across the whole save. Hard ban 2 says no story removes the giant and leaves the mat "
    "standing. The design reads that ban as forbidding a <i>convenient</i> separation — kill the giant, "
    "keep the sea — and reads an irreversible slow ruin as its opposite. You may read it the other way."),
  options=[
    dict(k="a", rec=True, text=(
      "<b>Slow ruin.</b> The wells stop opening forever, and every permit the Deepwater ever gave you is "
      "void — you killed the thing they keep the sea for. The only irreversible act in this ocean.")),
    dict(k="b", text="<b>It cannot be killed, or it comes back.</b> The ban is then never tested, and the sea "
                     "has no tragedy available in it."),
    dict(k="c", text="<b>Something else.</b> Type it — including a stricter reading of ban 2 if you have one."),
  ],
  prefill="a",
  chips=dict(source=f"{B}5.3 / {B}6 Q3",
             cost="A world-level flag, a hook on its death, and the skylight component reading the flag. Small.",
             ban="Hard ban 2 — this row is where that ban gets its reading."),
),

dict(
  id="rain_parasites", group=G_WHAL,
  label="Do the falling parasites bite your people?",
  effect="Decides whether the whale's rain is something you take cover from, or pure spectacle and loot.",
  question=(
    "During the gardener's passing, thumb-sized biting parasites shaken off its hide rain down through the "
    "shafts and live about a day. Do they bite your colonists too, or only the animals?"),
  options=[
    dict(k="a", rec=True, text="<b>Colonists too</b> — a minor itch-and-ache injury any doctor cures. Not "
                               "lethal, not a plot. The rain should be a thing you stand out of."),
    dict(k="b", text="<b>Animals only.</b> The rain is then pure spectacle and free loot, with no reason to "
                     "take cover."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.4 / {C}13.7 Q17", cost="Same creature; one flag."),
),

dict(
  id="orrilith_gems", group=G_WHAL,
  label="The gems that fall off the whale — what are they for?",
  effect="The only gem in this ocean, and it comes off an animal rather than out of a mine. Making it a "
         "material pulls against the designed absence of mineral wealth.",
  question=(
    "The barnacles that fall off the gardener are fist-sized shells with glowing bits in them like gems. "
    "Shelled at a crafting spot they give the only gem in this ocean — and it comes off an animal, not out "
    "of a mine, which is what keeps the biome's deliberate absence of mineral wealth intact. A pass leaves "
    "a dozen, and most get eaten by the frenzy before you can haul them."),
  options=[
    dict(k="a", rec=True, text="<b>A trade good and a decorative inlay, nothing more.</b> The moment a gem is "
                               "a crafting material, somebody asks where the mine is."),
    dict(k="b", text="<b>A real material too</b> — usable in building and crafting. More useful, and it pulls "
                     "against the 'nothing to dig here' premise the whole ocean is built on."),
  ],
  prefill="a",
  chips=dict(source=f"{C}13.4 / {C}13.7 Q18", cost="A: an item and a recipe. B: the same plus material "
                                                   "properties and balancing."),
),

# ══ 7 · THE DEEPWATER ═══════════════════════════════════════════════════════════════
dict(
  id="skylight_rights", group=G_DEEP,
  label="What happens if you claim a shaft of light without leave?",
  effect="The sanction on the headline mechanic. The Deepwater never raid anyone — so the punishment has "
         "to be a refusal.",
  question=(
    "Holding a shaft of light is the headline idea: you moor a claim buoy under a golden column and the "
    "ground beneath it is the only fast-growing, fish-crowded ground on the floor — until the ceiling "
    "drifts, the light walks away, and your plot goes dim. The Deepwater meter those rights. What happens "
    "if you hold one without their leave?"),
  options=[
    dict(k="a", rec=True, text=(
      "<b>Goodwill only.</b> Every day an unlicensed buoy stands, their opinion of you drops. They never "
      "raid — they do not raid anyone — they simply stop opening doors. And the claim itself expires with "
      "the shaft: a licence must never be able to hold a well open.")),
    dict(k="b", text="<b>Goodwill, and they quietly take the buoy down.</b> A visible consequence with no "
                     "violence in it."),
    dict(k="c", text="<b>No sanction.</b> Claiming a shaft is between you and the ceiling."),
  ],
  prefill="a",
  chips=dict(source=f"{C}8.1 / {C}11 Q8, {B}3.1 / {B}5.5",
             cost="A small check on the buoy; no new system.",
             ban="Serves hard ban 4 (the Deepwater never turn hostile) and hard ban 5 (no permanent skylight)."),
),

dict(
  id="permit_system", group=G_DEEP,
  label="How the Deepwater's permits work — and whose they are.",
  effect="Eight rights, numbered differently in the two documents, need to become one ladder. And a title "
         "in this engine belongs to a PAWN, not to the colony.",
  question=(
    "The Deepwater's only lever on you is admission and price. The rights on offer: <b>dock rights</b> "
    "(open your hatch over their water without offence, and shelter at one of their moorings) · "
    "<b>air</b> (a line to your mooring, so your stay is not bounded by the ship's own supply) · "
    "<b>lamplight</b> (they string lamps along your bank — real light between shafts) · <b>charts</b> "
    "(where the light is right now, and where the gardener's lanes run) · <b>the ward</b> (your wounded "
    "treated by their medic — the only friendly doctor under the sea on a planet where every other faction "
    "is a raid) · <b>the Sharing</b> (their ceremonial water-gift) · <b>tethering</b> (the right to build "
    "their floating cages) · <b>the ark-key</b> (breeding stock may leave the sea). That is eight, and the "
    "two documents count them differently, so they have to become one numbered ladder. The machinery on "
    "offer is the base game's noble-title system, which is just data and can carry a faction's own ladder "
    "without touching the Empire's. Its quirk: <b>a title belongs to one colonist, not to the colony.</b>"),
  options=[
    dict(k="a", rec=True, text=(
      "<b>Their own ladder on the base game's title system, held per colonist.</b> Four ranks, guest up to "
      "ark-keeper's friend. A named person carries your standing with them, and can die in a raid.")),
    dict(k="b", text="<b>The same rights, held colony-wide.</b> Loses the stake — a colony flag is a "
                     "checkbox — and costs about the same either way."),
    dict(k="c", text="<b>Our own permit system from scratch.</b> Full control, more code, no reason yet."),
  ],
  prefill="a",
  chips=dict(source=f"{B}3.2 / {B}6 Q4, {C}13.5",
             cost="Medium: the ladder in XML, four to six small permit effects, and one hook that strips "
                  "ranks when you lose their goodwill. Either way the eight rights become one list.",
             ban="Hard ban 4 holds: revoking a permit is a refusal, not hostility. No warden ever raises a hand."),
),

dict(
  id="ark_key", group=G_DEEP,
  label="Who holds the highest permit?",
  effect="The right that gates taking living breeding stock out of the sea. A person who can die, or a "
         "colony flag.",
  question=(
    "The highest right — permission to take living breeding stock out of the sea — is the one that gates "
    "the Ark Seed. Held by a person, or by the colony?"),
  options=[
    dict(k="a", rec=True, text="<b>A person.</b> A named ark-friend who can be killed is a stake."),
    dict(k="b", text="<b>The colony.</b> Safer, duller, and it cannot be lost by bad luck."),
  ],
  prefill="a",
  chips=dict(source=f"{B}6 Q5", cost="Either; one field."),
),

dict(
  id="the_sharing", group=G_DEEP,
  label="Does the Deepwater's charity reach your colony?",
  effect="The most surprising thing the water monopolists can do — and what makes losing their goodwill "
         "actually hurt.",
  question=(
    "One of the Deepwater runs <b>the Sharing</b> — a ceremonial water-gift to anyone who arrives in need. "
    "On a desert planet, from the people who hold the water monopoly, that is the most surprising thing "
    "they can do. Does it reach your colony, or only people who turn up at their door?"),
  options=[
    dict(k="a", rec=True, text="<b>A permit carries it to you.</b> In a drought, a standing capped water "
                               "grant arrives. It is what makes losing their goodwill actually hurt."),
    dict(k="b", text="<b>At their Hold only.</b> You must go there. Purer to the ceremony, and it never "
                     "touches your base."),
  ],
  prefill="a",
  chips=dict(source=f"{B}3.2 / {B}6 Q7",
             cost="A depends on a carried liquid being haulable — unmeasured, and already owed elsewhere."),
),

dict(
  id="ark_seed", group=G_DEEP, contested=True,
  label="May the last living sea live in a tank on the dayside?",
  effect="The strongest single reward in either document, and the one that brushes the setting's premise "
         "that everything ordinary survives ONLY here.",
  question=(
    "Carry a breeding pair of sea creatures up through the hatch in a tank, install them at home in a "
    "brine basin, feed them on kelp, and if they live your home map gets a fishery — of the only ordinary "
    "fish left in the world. On a planet whose premise is that nothing grows, that is the strongest single "
    "reward in either document, and the thing a player tells someone about. It also brushes the premise: "
    "the frozen sheet says everything ordinary that survives anywhere survives <i>only here</i>, and the "
    "terminator-sea canon says nothing crosses between seas. The defence is that a pen is an aquarium, not "
    "a sea — small, artificial, dependent, revocable — and if it dies it leaves nothing behind."),
  options=[
    dict(k="a", rec=True, text="<b>Yes, as an aquarium and never a wild population.</b> Nothing escapes a pen "
                               "into any map's water, and a pen that dies leaves nothing behind."),
    dict(k="b", text="<b>No.</b> The premise is the premise; the last sea stays the last sea."),
    dict(k="c", text="<b>Yes, but as a larder only.</b> You bring food home, not living fish — no fishery on "
                     "the home map. Much cheaper and much less of a story."),
  ],
  prefill="a",
  chips=dict(source=f"{B}3.3 / {B}5.2 / {B}6 Q2",
             cost="Medium–high, and it rests on one engine question nobody has measured: where the fishing "
                  "system reads which species a body of water holds. Do not trust the price until that is read.",
             ban="Strains the frozen sheet's §5 and terminator-sea canon — 'everything ordinary survives only here'."),
),

dict(
  id="deepwater_houses", group=G_DEEP,
  label="The bottom-dwellings — per place, and whose people?",
  effect="The frozen sheet already ruled the houses in. Three shapes left: per-tile or biome-wide, new "
         "people or the Hold's, and whether the proposed roles stand.",
  question=(
    "Their dwellings stand on the sea floor, lamplit, on the river banks — the frozen sheet already ruled "
    "that in, and their twenty-five-person surface Hold is already written, hospital ward and all. Three "
    "small shapes are left. Are the bottom-houses a thing that exists <b>per place you dive</b>, so each "
    "sea tile has its own, or <b>one population</b> shared across the whole ocean? Is the bottom cast "
    "<b>newly written people</b> (six to eight) or <b>the Hold's existing twenty-five coming down</b>? And "
    "do the proposed roles stand as a starting sheet for your own prose?"),
  options=[
    dict(k="a", rec=True, text="<b>Per place · a new bottom cast of six to eight · the proposed roles as your "
                               "starting point.</b> The Hold is a surface seat and its people have surface hooks."),
    dict(k="b", text="<b>Per place, but the Hold's people descend.</b> No new prose owed, and the surface and "
                     "the floor share one cast."),
    dict(k="c", text="<b>One population for the whole ocean.</b> Simpler, and every dive meets the same "
                     "neighbours wherever you go."),
    dict(k="d", text="<b>Mixed.</b> Say which parts in the box."),
  ],
  prefill="a",
  chips=dict(source=f"{C}9 / {C}10.2-10 / {C}11 Q10",
             cost="A place archetype, a house-placing step, a per-place component, three or four buildings, "
                  "and six to eight character write-ups."),
),

# ══ 8 · SETTINGS ════════════════════════════════════════════════════════════════════
dict(
  id="mod_settings", group=G_SETS,
  label="The settings screen — the whole proposed set.",
  effect="Every mod ships one. Each toggle below is a branch already in the design; defaults are exactly "
         "what ships.",
  question=(
    "Every mod ships a real settings screen. Proposed for this one: <b>the current</b> on/off, its "
    "strength, what the sink does to a carried colonist, and the first-entry warning · <b>creature glow</b> "
    "on / hosts only / off · <b>skylight drift</b> on/off · <b>the gardener's passing</b> on/off, with rain "
    "density, frenzy strength, and whether the parasites bite people · <b>fishing</b> unlimited in practice "
    "or literally · <b>Deepwater houses</b> on/off · <b>how dense the clinging layer is</b> · <b>tethered "
    "cages</b> on/off and whether you can walk under them · <b>living decor needs light</b> (off by "
    "default) · <b>how long the sun-sphere survives being starved</b>. Defaults are exactly what ships."),
  options=[
    dict(k="a", rec=True, text="<b>All of them, defaults as shipped.</b>"),
    dict(k="b", text="<b>Fewer.</b> Say which to drop — every toggle is a branch somebody has to maintain."),
    dict(k="c", text="<b>More.</b> Say what else should be adjustable."),
  ],
  prefill="a",
  chips=dict(source=f"{C}11 Q12, {C}13 (four more proposed)",
             cost="One settings screen; each toggle is a branch the design already has."),
),
]

CONFIG = {
  "sheetId": "twilight_deep_sitting_20260926",
  "title": "The Twilight Deep — ruling sitting",
  "subtitle": "33 open questions harvested from the two design passes that closed 2026-09-26",
  "briefHtml": """
<p><b>Two design documents for the Twilight Deep closed today</b>, written in parallel by different
agents. Between them they left 45 open calls; de-duplicated they are the 33 rows below. Every row
names which document and section it came from, so your answer can be written back to the right place.</p>

<p><b>You already ruled two things today. They are not re-asked here:</b></p>
<ul>
<li><b>The ceiling stays, reskinned.</b> The mechanism is unchanged — skylights are holes in it, they
drift and expire, the ceiling gardens hang from it, the gardener tends it — but <i>mold</i> is gone and
it is a living canopy in lustrous blue-green. Only its <b>name</b> is still open (row 2).</li>
<li><b>The underwater rivers still carry you.</b> They look like dry riverbeds; the denser water moves a
pawn along them. Hard ban 3 stays live as a real mechanism. Only the <b>sink's outcome</b> and whether a
pawn may ride one <i>on purpose</i> are still open (rows 8 and 9).</li>
</ul>

<p><b>Every row starts UNANSWERED — nothing here is pre-decided.</b> On each row one option is marked
<span style="color:#5ac37f">◀ BENCH position</span>: that is our proposal, never your answer, and the
counter at the top will keep saying <i>33 left</i> until you have actually ruled. <b>On every row
BENCH's position is option A</b>, so <kbd>Shift</kbd>+<kbd>1</kbd> accepts a whole group in one
keystroke — eight keystrokes clears the sheet — and you then go back and change the ones you disagree
with.</p>

<p><b>Controls.</b> <kbd>1</kbd>–<kbd>4</kbd> pick A/B/C/D · <kbd>5</kbd> is <i>my own answer</i> ·
<kbd>6</kbd> parks a row for later · <kbd>n</kbd> jumps into the note box · <kbd>g</kbd> jumps to the
next unanswered row · <kbd>Shift</kbd>+a number rules a whole group. <b>Anything you type in a note box
overrides the option and is the only text that counts as your words</b> — a clicked option is our
sentence, and gets recorded as a decision taken by question card, never as a quote.</p>

<p><b>Marks on a row.</b> <span style="color:#e8b64c">◆ contested</span> means the two documents
genuinely disagree or the call is defensible both ways. A <b>ban</b> chip names which of the six hard
bans the row strains. A <b>cost</b> chip is on every row where something has to be built; <b>treat any
row whose cost mentions <i>unmeasured</i> as unpriced</b> — the number is not trustworthy until someone
reads the engine.</p>

<p><b>Nothing here is filed and no design document was changed to build this page.</b> Rows you leave
untouched are not rulings and will be brought back.</p>
""",
  "criterion":
    "Ordered by what a ruling UNBLOCKS: the four rows at the top change other rows' answers or change what "
    "gets built at all; groups 2–8 are by subject. That ranks leverage, not importance — it cannot tell you "
    "which of these you actually care about, and a row you feel strongly about sitting at #29 means the "
    "ordering was wrong, not your feeling.",
  "invented": [
    "The organising law for this whole ocean — “every reward here is alive, renewable, expiring or "
    "relational; if a reward survives in a stockpile with nobody tending it, it belongs to the Grey Sea” "
    "— was written by an agent today, not asked for. It is the entire basis of the conflict in row 7, so if "
    "you reject the law, row 7 dissolves rather than needing an answer.",
    "“The oolune” and the veil / the lid / veil-fall vocabulary (row 2) is an invented proposal, "
    "not a name you gave.",
    "“The sun-sphere frees the player from the skylight economy” (row 5) is a consequence one "
    "document invented for itself, and it is what undercuts the other document's number-one idea.",
    "Splitting the two silver shoals by light (row 15) is an invented reconciliation of two defs that "
    "collided; neither description asks for it.",
    "The gardener OPENING new skylights (row 22) goes beyond the frozen sheet, which says it keeps them "
    "open. Closing them is the sheet's; opening them is ours.",
    "Every timing in the whale's five-beat sequence (row 20) is a placeholder invented to be judged by "
    "watching, not a measured number.",
    "“Permits lapse in reverse order, highest first” (row 28) is an invented revocation rule.",
  ],
  "posture": {
    "mode": "ruling sitting — default UNANSWERED",
    "explain":
      "Nothing on this page is decided until you touch it. Every row's `decision` is EMPTY on arrival; "
      "BENCH's own position is stored alongside it as `prefill` and shown on the row as a proposal, "
      "never as your answer. A row you never touch stays unanswered in the file and comes back. Typed "
      "notes override the option and are the only thing that counts as your words.",
  },
  "options": [
    {"key": "a",     "label": "A",             "hotkey": "1", "color": "#5ac37f", "counts": "in"},
    {"key": "b",     "label": "B",             "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
    {"key": "c",     "label": "C",             "hotkey": "3", "color": "#e8b64c", "counts": "in"},
    {"key": "d",     "label": "D",             "hotkey": "4", "color": "#b48ce0", "counts": "in"},
    {"key": "own",   "label": "my own answer", "hotkey": "5", "color": "#cfe3ff", "counts": "in"},
    {"key": "later", "label": "park it",       "hotkey": "6", "color": "#98a2b3", "counts": "out"},
  ],
  "groupLabel": "group",
  "media": False,
  "decisionsFile": DECISIONS_NAME,
  "decisionsPath": DECISIONS,
  "sheetPath": SHEET,
}

RENDER = r"""
<script id="RENDER">
window.itemBody = it => {
  const chip = (cls, k, v) => `<span class="mark ${cls}"><b>${esc(k)}</b> ${esc(v)}</span>`;
  const chips = [];
  const c = it.chips || {};
  if (c.gating)   chips.push(`<span class="mark contested"><b>gating</b> ${esc(c.gating)}</span>`);
  if (c.conflict) chips.push(`<span class="mark contested"><b>conflict</b> ${esc(c.conflict)}</span>`);
  if (c.ban)      chips.push(`<span class="mark inferred"><b>ban</b> ${esc(c.ban)}</span>`);
  if (c.cost)     chips.push(chip('absent', 'cost', c.cost));
  if (c.source)   chips.push(chip('absent', 'from', c.source));

  const opts = (it.options || []).map(o => {
    const letter = o.k === 'own' ? '✒' : o.k === 'later' ? '⏸' : o.k.toUpperCase();
    return `<div class="qopt${o.rec ? ' rec' : ''}">`
         + `<span class="qk">${esc(letter)}</span>`
         + `<span class="qt">${o.text}${o.rec ? ' <span class="recmark">◀ BENCH position</span>' : ''}</span>`
         + `</div>`;
  }).join('');

  return `<div class="qbody"><div class="qq">${it.question || ''}</div>`
       + `<div class="qopts">${opts}</div>`
       + (chips.length ? `<div class="qchips">${chips.join('')}</div>` : '')
       + `<div class="qhint">Pick a letter, or type your own answer in the note box — typed text wins.</div>`
       + `</div>`;
};
</script>
<style>
.qbody{margin-top:2px}
.qq{font-size:13.5px;line-height:1.55;margin-bottom:9px;max-width:92ch}
.qopts{display:flex;flex-direction:column;gap:5px;margin-bottom:8px}
.qopt{display:flex;gap:9px;align-items:flex-start;background:#0f1216;border:1px solid #232830;
  border-radius:5px;padding:6px 9px;font-size:12.8px;line-height:1.5;max-width:100ch}
.qopt.rec{border-color:#3d5a3f;background:#0e1510}
.qk{flex:0 0 20px;text-align:center;font-weight:700;color:#ffb454;font-family:ui-monospace,monospace}
.qopt.rec .qk{color:#5ac37f}
.qt{flex:1 1 auto;color:#d6d3cf}
.recmark{color:#5ac37f;font-size:11px;white-space:nowrap}
.qchips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:5px}
.qchips .mark{max-width:none;white-space:normal;text-align:left;line-height:1.4}
.qhint{color:#6d7684;font-size:11px}
</style>
"""


def build_sheet() -> None:
    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()

    cfg_json = json.dumps(CONFIG, indent=2, ensure_ascii=False)
    items_json = json.dumps(ROWS, indent=1, ensure_ascii=False)

    start = html.index('<script id="CONFIG" type="application/json">')
    end = html.index("</script>", start) + len("</script>")
    html = (html[:start]
            + '<script id="CONFIG" type="application/json">\n' + cfg_json + "\n</script>"
            + html[end:])

    start = html.index('<script id="ITEMS" type="application/json">')
    end = html.index("</script>", start) + len("</script>")
    html = (html[:start]
            + '<script id="ITEMS" type="application/json">\n' + items_json + "\n</script>"
            + html[end:])

    # FILL IN #3 — injected as a LIVE script OUTSIDE the template's commented example block.
    # Filling the commented one in place leaves the renderer as inert text (skill, 2026-09-15).
    marker = "<script>\n\"use strict\";"
    assert marker in html, "template's main script block moved"
    html = html.replace(marker, RENDER + "\n" + marker, 1)

    with open(SHEET, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"sheet   -> {SHEET}  ({len(ROWS)} rows)")


def build_decisions(force: bool) -> None:
    if os.path.exists(DECISIONS):
        with open(DECISIONS, encoding="utf-8") as fh:
            cur = json.load(fh)
        # The unforgeable stamp: only the sidecar writes these.
        ruled = cur.get("savedBy") or cur.get("writeCount") or \
            (cur.get("reviewStatus") or {}).get("state") == "ruled"
        if ruled:
            sys.exit("REFUSED: that decisions file carries the sheet's own save stamp — "
                     "regenerating it would overwrite the owner's rulings with our guesses.")
        if not force:
            sys.exit("REFUSED: a decisions file already exists. Pass "
                     "--i-know-this-overwrites-the-owners-decisions if you really mean it.")

    doc = {
        "posture": CONFIG["posture"]["mode"],
        "postureExplain": CONFIG["posture"]["explain"],
        "criterion": CONFIG["criterion"],
        "invented": CONFIG["invented"],
        "generatedBy": f"{os.path.basename(__file__)} (agent pre-fill, 2026-09-26)",
        "reviewStatus": {
            "state": "prefill",
            "by": None,
            "at": None,
            "evidence": "Generated by the pre-fill generator; no sidecar save stamp present. "
                        "Every row carries a `prefill` (BENCH's proposal, shown on the page as "
                        "◀ BENCH position) and an EMPTY `decision`, deliberately: an "
                        "unanswered row must never read as a ruling. A row is answered only once "
                        "`decision` is non-empty AND this file carries the sidecar's savedBy / "
                        "writeCount stamp.",
        },
        "decisions": {
            r["id"]: {"decision": "", "prefill": r["prefill"], "note": ""}
            for r in ROWS
        },
    }
    with open(DECISIONS, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    print(f"prefill -> {DECISIONS}  ({len(ROWS)} rows, state=prefill)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet", action="store_true", help="rebuild the HTML (always safe)")
    ap.add_argument("--decisions", action="store_true", help="rebuild the pre-fill (destructive)")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions",
                    dest="force", action="store_true")
    a = ap.parse_args()
    if not (a.sheet or a.decisions):
        ap.error("pick --sheet and/or --decisions")
    ids = [r["id"] for r in ROWS]
    assert len(ids) == len(set(ids)), "duplicate row id"
    if a.decisions:
        build_decisions(a.force)
    if a.sheet:
        build_sheet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
