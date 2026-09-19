# TEXT_LORE_LOAD_CENSUS_1 — how much text does this game owe us?

Owner, 2026-09-11 (verbatim intent): estimate the entire "text lore load" we
should be tracking for the whole game — *"Item descriptions. Secrets obtained
from inside dungeons. Situational reaction text. Event descriptions. Character
descriptions. Biome descriptions. Scenario welcome. God statements and
reactions. Faction descriptions. Conversation text. Search the game and look
for all the places text belong and we probably need to own it. Renaming to our
lore. Expand until you have a complete inventory then store this as a report."*
Then generation tickets where lore is known, design tickets where it isn't.
*"The lore continues to grow, so some triage of what is likely to change is
important so highly variable sections get deferred until lockdown."*

## Rulings (owner cards, 2026-09-11)
1. **Scope: everything the player can read** — donor-mod text included,
   triaged by exposure — *"but it's also the non scenario text that some mods
   need when used outside our scenario based on vanilla. That too."* So the
   inventory tracks BOTH campaign text AND tier-generic variants: RM_ text
   must read vanilla-clean anywhere, RSW_ text Star-Wars-generic, only RUT_
   may be Ash'karr-specific (NAMING_SCHEME grammar applied to prose).
2. **Lockdown triage: frozen sheet or owner ruling = locked** — generate its
   text now. Anything still draft/proposed defers until its details freeze.
3. **Oracle text counts in**: the in-game LLM's persona/prompt packs (god
   statements and reactions, conversations) are part of the tracked lore
   load, spec'd alongside static text.

## spec
1. **Inventory** (fanout ran 2026-09-11 from BENCH, four lanes): (A) every
   engine text surface (def types + fields + C#-hardcoded letters/alerts,
   grammar vs static); (B) our three tiers' current text state (present /
   missing / placeholder / donor residue / tier-grammar violations); (C)
   donor-stack exposure counts from the def dump (measure-instrumented,
   blind spots marked UNMEASURED, ours/donor/vanilla split); (D) design-side
   narrative systems and their LOCKED/DRAFT status.
2. **The report**: compose lanes into one document — the complete inventory,
   per-category counts (MEASURED/UNMEASURED discipline), exposure triage,
   lockdown status, and a total load estimate (entries and rough words).
   Committed in design/Jawa/ (anyone-later, not Transient); candidate hub
   tab later (DASHBOARD_HUB_ARTIFACT_1).
3. **Ticket generation from the report**: per category, file either a
   generation ticket (lore LOCKED — write the text) or a design ticket (lore
   not up to the challenge — the gap named). Deferred-until-lockdown rows are
   listed IN the report with what must freeze first — not silently dropped.

## verify
- [ ] The report exists, committed, with every category carrying a
      MEASURED/UNMEASURED count and a LOCKED/DRAFT/DEFERRED status.
- [ ] Every LOCKED category has a filed generation or design ticket named in
      the report; every DEFERRED row names its lockdown dependency.
- [ ] Tier-generic variant work (ruling 1) appears as its own tracked rows.

## criteria
The owner can read one report and know: how much text the game owes, what can
be written today, what waits and on what, and what it will take.
