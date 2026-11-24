<!-- version: departures_brief@v3 -->
# Task: write the required departures for an invented creature or plant (text only, no images)

An invented RimWorld creature must read as ALIEN, never as a recoloured Earth animal (owner 2026-10-11: *"it
looks like a terran hippo with ash on its back. Much more alien please."*). A blunt rule, "if you can name the Earth
animal, reject it", also rejects subjects whose own description names an Earth body. Examples: a frog-like toad, an
octopus-like swimmer, a plant described as "a fern" or "a moss".

So each invented creature or plant gets a short list of **required departures**. A departure is a visible feature that
makes the subject NOT its nearest Earth animal. A reviewer checks each departure of a creature in the art: present or
absent. A missing departure sends the art back to be redrawn. So **a departure the description does not state is a
false rejection**.

Work from the def description below:
1. Name the Earth animal or plant that a painter would most likely default to (one or two words).
2. Say whether the description itself names that Earth body or plant kind as the intended look. Put
   the answer in `earth_body_named`: true for "a deep-green fern", false for "a hound-sized reptile".
3. Write 0 to 5 departures. Each departure is a VISIBLE feature that the description STATES. Each departure has a
   `quote`: the exact words of the description that state the feature (a few words to one clause). Copy the words
   character for character. If the quote is not in the description, code discards the departure.
   - State only what the quote says. Add no colour, texture, glow, crack, size, count, pose, setting or ground cover
     that the quote does not give. Two wrong examples:
     - "charred ash-grey cracked scales" from "a snake of the ash" is invented;
     - "half-buried in ash" is staging, never a departure.
   - Never list behaviour, habitat, smell, sound, temperature, venom effect or lore, even when the description
     states them. A picture cannot show them.
   - When the description says little that is visible, a shorter list is right. An empty list is a valid answer.
4. Give the body plan: walker, wall_clinger, serpentine, swimmer or flyer. If none of these fits, give null. For a
   plant, always give null.

Return exactly this JSON object (no prose, no code fence):

{"schema": "rm-art-eval/departures@v2", "subject": "<defName>", "nearest_earth_animal": "<word>",
 "earth_body_named": false, "departures": [{"feature": "<visible feature>", "quote": "<exact words from the description>"}],
 "body_plan": "<plan or null>"}
