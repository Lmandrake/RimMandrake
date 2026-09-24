# FORCE_DISTURBANCE_REFLAVOR_1 — psychic storms become disturbances in the Force

Owner directive, typed 2026-09-24: "Make a ticket in the background to convert
the psychic assault storms event that frequent rimworld sound be converted to
disturbances in the force in rim star wars."

## spec

The vanilla psychic event family — psychic drone (the planetary/map condition
in both sexes), psychic soothe, the psychic-ship crash chain, and any DLC
psychic-storm conditions active in our list — get reflavored as **disturbances
in the Force** at the **RimStarWars tier** (`RSW_`, `mandrake.rsw.*`; per the
tier grammar this is Star Wars flavour usable by any Star Wars scenario, NOT
campaign-specific — the Utinni layer only adds campaign-specific text if any).

- Rename/retext by patch, not by replacing the incident defs: labels, letter
  text, condition descriptions, alert strings. Mechanics unchanged — this is
  flavour, not a rebalance.
- Survey first: enumerate every live incident/condition def whose label or
  text says "psychic" (vanilla + DLC + donors in the active list) before
  patching; patch what the campaign will actually see.
- Wording direction: a drone is "a disturbance in the Force" pressing on
  minds; a soothe is the Force at peace; a psychic ship is a dark-side
  artifact. Draft text goes past the owner (BENCH card) before shipping —
  flavour text he will read constantly.

## Watch out

- `PatchOperationConditional`/`FindMod` return true on no match — a text patch
  that misses its xpath fails silently. Validate with validate_patch.py
  against both --defs and --live.
- Psychic sensitivity stats/hediffs keep their names ("psychically deaf" etc.)
  unless the owner rules wider — scope creep here touches Biotech genes and
  Royalty psycasts; this ticket is the STORM/EVENT family only.
- Donor mods may carry their own psychic events; a vanilla-only xpath sweep
  undercounts what the player sees.

## verify

Every surveyed psychic storm/condition event shows Force-flavoured label +
letter text in a live quicktest; no vanilla "psychic drone" string reaches the
player from the patched set.

## criteria

Owner has seen and approved the replacement text; mechanics measurably
unchanged (same incident defs fire, same conditions apply).
