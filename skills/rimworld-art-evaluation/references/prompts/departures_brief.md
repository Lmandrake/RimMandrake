<!-- version: departures_brief@v1 -->
# Task: write the required departures for an invented creature (text only, no images)

An invented RimWorld creature must read as ALIEN, never as a recoloured Earth animal (owner 2026-10-11: *"it
looks like a terran hippo with ash on its back. Much more alien please."*). A blunt rule "if you can name the Earth
animal, reject it" also rejects creatures whose own description names an Earth body (a frog-like toad, an
octopus-like swimmer). So each invented creature gets a short list of **required departures**: the visible
features that make it NOT its nearest Earth animal. A reviewer checks each one present/absent in the art.

From the def description below:
1. Name the Earth animal a painter would most likely default to (one or two words).
2. Say whether the description itself names that Earth body as the intended look (`earth_body_named`).
3. Write 3 to 5 departures: concrete, VISIBLE features taken from (or directly implied by) the description that a
   picture can show — body plan, limb count, a signature structure, skin, head shape. Never invent lore the
   description does not support; never list behaviour, smell, sound or temperature.
4. Body plan, if one of: walker, wall_clinger, serpentine, swimmer, flyer — else null.

Return exactly this JSON object (no prose, no code fence):

{"schema": "rm-art-eval/departures@v1", "subject": "<defName>", "nearest_earth_animal": "<word>",
 "earth_body_named": false, "departures": ["<visible feature>"], "body_plan": "<plan or null>"}
