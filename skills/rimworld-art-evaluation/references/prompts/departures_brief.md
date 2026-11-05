<!-- version: departures_brief@v3 -->
# Task: write the required departures for an invented creature or plant (text only, no images)

An invented RimWorld creature must read as ALIEN, never as a recoloured Earth animal (owner 2026-10-11: *"it
looks like a terran hippo with ash on its back. Much more alien please."*). A blunt rule "if you can name the Earth
animal, reject it" also rejects subjects whose own description names an Earth body (a frog-like toad, an
octopus-like swimmer, a plant described as "a fern" or "a moss"). So each invented creature or plant gets a short list of **required departures**: the visible
features that make it NOT its nearest Earth animal. A reviewer checks each one present/absent in the art, and a
missing departure sends the art back to be redrawn, so **a departure the description does not state is a false
rejection**.

From the def description below:
1. Name the Earth animal or plant a painter would most likely default to (one or two words).
2. Say whether the description itself names that Earth body or plant kind as the intended look (`earth_body_named`: true for "a deep-green fern", false for "a hound-sized reptile").
3. Write 0 to 5 departures. Each is a VISIBLE feature the description STATES, with `quote`: the exact words of the
   description that state it, copied character for character (a few words to one clause). A departure whose quote
   is not in the description is discarded by code.
   - State only what the quote says. Do not add a colour, texture, glow, crack, size, count, pose, setting or
     ground cover the quote does not give ("charred ash-grey cracked scales" from "a snake of the ash" is invented;
     "half-buried in ash" is staging, never a departure).
   - Never list behaviour, habitat, smell, sound, temperature, venom effect or lore, even when the description
     states them: a picture cannot show them.
   - Fewer is right when the description says little that is visible. An empty list is a valid answer.
4. Body plan, if one of: walker, wall_clinger, serpentine, swimmer, flyer — else null (always null for plants).

Return exactly this JSON object (no prose, no code fence):

{"schema": "rm-art-eval/departures@v2", "subject": "<defName>", "nearest_earth_animal": "<word>",
 "earth_body_named": false, "departures": [{"feature": "<visible feature>", "quote": "<exact words from the description>"}],
 "body_plan": "<plan or null>"}
