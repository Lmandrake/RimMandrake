## spec
📄 **The whole thing lives in two files — do not re-derive any of it:**
  `design/Jawa/bridge/LIVING_NPC_TEMPLATES.md`   36 templates + architecture
  `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md`  the wider ~95-tool roster

THE CONCEPT, owner's words: *"the pawns for this tool are sentient, named and well
detailed. They have homes (they go to sleep at night), they eat when hungry, they
may even 'tend' nearby structures (dwell near farms if present, dwell indoors for
long periods then go on walks outside)... a peasant at home, a farmer at a
worksite, a military fortification that has patrolling soldiers, an inward-dwelling
commander, and prisoners that are given food to survive, pets and associated
animals, hunters that hunt, etc. Go a bit crazy with these options."*

⭐ **THE HEADLINE: most of this is nearly free.** `LordJob_DefendPoint` already
gives pawns that eat, sleep, socialise, wander and do work jobs around a point,
with ONE toil and ZERO transitions - nothing can turn them hostile on their own.
Total new code for everything except farming: **1 LordJob, 1 LordToil, 1 JobGiver,
2 DutyDef XML, 1 setup utility. No Harmony.**

🔴 **THE ONE THING THAT IS NOT FREE — FARMING.** Blocked three independent ways:
only 7 shipped WorkGiverDefs carry `nonColonistsCanDo` and **all seven are
construction or repair**; `WorkGiver_GrowerHarvest.ShouldSkip` returns true for
**any lorded pawn, even a colonist**; and `WorkGiver_Grower` reads player-only
zone data, so an NPC farm yields no work cells at all.
⇒ CHECK's recommendation, DECIDE's call: **reframe "tends the farm" as "dwells
near it and repairs it", which is FREE.** Real farming roughly doubles the surface
and pulls in Harmony. ⚠️ Note this hits the owner's own "farmer at a worksite"
template - it is the one named start that does not come cheap.

🔴 **A SAVE-CORRUPTION TRAP DECIDE SHOULD RULE ON.** `Lord.ExposeData_StateGraph`
serialises toils by **POSITIONAL INDEX** and re-runs `CreateGraph()` on load, so
changing a LordJob's toil ORDER silently corrupts existing saves. This revises
CHECK's own earlier `LordJob_Patrol` ring proposal: a transition graph is fine for
a patrol that never gets re-tuned, but anything we expect to iterate on should be
ONE toil walking a waypoint index it owns and scribes.

⚠️ **A GAMEPLAY PROBLEM, NOT A BUG:** non-player pawns ignore player forbid flags
entirely, so these NPCs **will walk into a player stockpile and eat the colony's
meals**. Mitigate with their own food inside the radius, or accept it. DECIDE's call.

THREE STRUCTURAL CALLS CHECK WOULD MAKE, offered as recommendations only:
1. **Templates are CONTAINERS, not leaves** - a garrison holds a commander holds a
   cell block. Parent stamps structures and reserves sub-rects.
2. **`decay` (0-1 ruin dial) is the highest-value single parameter** - it turns
   every template into its own ruined variant for free. Worth more than ten more
   templates.
3. **`hostility: conditional`** (neutral until provoked) is what makes these read
   as inhabited rather than placed. Without it every template is a combat encounter.
Plus: **named pawns should be the EXCEPTION** - one per template, rest generated.

🔗 **TWO THINGS THIS WOULD INCIDENTALLY UNBLOCK**, both already in the repo:
* `bridge-cannot-order-a-melee-attack-3f8c21` (V2_DREAMS) - the lightsaber swing
  frame cannot be staged because *"spawned hostiles have no lord"*; a real raid
  plus 5,600 stepped ticks produced no engagement. Spawning WITH a lord is exactly
  this tool.
* **The Tusken water raid** (V2_DREAMS) - steal-and-withdraw needs a custom
  behaviour, and that entry already says *"Vanilla's LordJob layer is where it
  would have to be built."* Same layer, same skill, built once.

PROVING ORDER CHECK SUGGESTS: **1 Peasant Hearth** (trivial) -> **4 Farmstead**
(proves day/night) -> **7 Waystation Fort** (proves the patrol) -> **15 Fed
Prisoners** (proves guest status + the feeding loop) -> **22 Sandcrawler Crew**
(the set-piece, and the one that is most this campaign).

## verify
EMPTY - nothing to verify until DECIDE has cut the list.

## criteria
EMPTY - DECIDE sets the pass condition when it rules on scope. CHECK will not
invent one, and will not start building until it does.

## notes
**from:** CHECK, 2026-08-19, **at the owner's direct instruction in session.** He asked for
it to be specced into DECIDE's queue "to be a very rich tool for storytelling",
and closed with *"It's for DECIDE to further expand or contract the concept."*
🔑 **DECIDE OWNS EVERY SCOPE CALL HERE.** CHECK wrote it only because CHECK holds
the engine facts; nothing below is a decision, it is a menu with prices on it.

**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready — for DECIDE

━━━ 🔴 OWNER'S ANSWERS, 2026-08-19 Q/A. Captured verbatim before they are lost ━━━

**1. SCOPE — 🔴 REVERSED BY THE OWNER, 2026-08-20.** *"Please ship the Inhabited spec to
BUILD for actual v1 construction, we have spare time tonight."* ⇒ **The code is v1 and is
being built now**, filed as the eight `INHABITED_*` / `CAST_ROSTER_*` items in
`infrastructure/state/queue/BUILD.md`. The design in `design/Jawa/bridge/INHABITED_DESIGN.md`
is unchanged and its §7 open questions are now BLOCKING — see `INHABITED_OPEN_QUESTIONS_1`
below, which is DECIDE's own debt.
⚠️ Still true, and not reversed by this: **nothing here blocks worldgen** — an `Inhabited`
place is a `WorldObject` stamped onto a finished planet, not a worldgen input — and
🔴 **farming stays NOT ATTEMPTED** (§2.1, blocked three ways in the shipped engine).

~~*"v1 for the DESIGN, v2 for the code."* ⇒ The templates, routes and casts are authored NOW
as design, so the hand-built world is built as though the people will arrive; the code that
animates them is v2. Nothing blocks worldgen and nothing has to be retrofitted. ⛔ Do not
file BUILD items for the code.~~
⛔ **DEAD — superseded 2026-08-20.** Struck in place, not deleted: "do not file BUILD items
for the code" is a live instruction a later reader would act on.

**2. THE WORLD REMEMBERS — world-level state.** The refinery crew flees and the tile is
marked; the next visit finds the place empty, looted, or squatted. ⇒ This is the load-bearing
choice and everything else bends around it. RimWorld discards a map when the player leaves,
so the state cannot live on the map.

**3. TRADE IS THREE LAYERS, and the owner expanded past what was offered.** Verbatim:
*"they have a little 'oil shop' they officially offer for their faction, but you can also
talk to individuals to buy/sell their personal inventory (very little silver of course),
and I also love that some faction lords may sell their own people to you right there. Or
buy yours, and then they stay!"*
  a. **faction stock** — the official shop, a `TraderKindDef` on the place
  b. **personal inventory** — any individual can be traded with, tiny silver
  c. ⭐ **PEOPLE, both directions** — a lord may sell you their own, or BUY yours,
     **and the bought pawn STAYS WITH THE CAST.** ⇒ cast membership is MUTABLE THROUGH
     TRADE, which means the roster is persistent state, not a spawn list. This is the
     single most demanding requirement in the whole concept.

**4. CAST DEPTH — all four taken:** daily ROUTE · ROLES within a cast · RELATIONSHIPS and
names · ANIMALS and property they defend.
  ⭐ **Everyone gets a name.** Owner: *"I think everyone deserves a name and at least some
  backstory, it can just be more generic for the 'lessers.'"* ⇒ named is the RULE, not the
  exception — CHECK's "one named pawn per template, rest generated" is **overturned**.
  Backstory DEPTH tiers; naming does not.
  🔴 **And his question back, which is a design ruling in disguise:** *"But are there really
  little people in the world? Remember we're playing Jawa..."* ⇒ see the ruling below.

**5. MOD NAME** — the concept is to ship as an independent mod. Naming in progress.

━━━ 🔴 ROUND 2 OF THE Q/A, 2026-08-19. Four more rulings ━━━

**6. STATE LIVES IN A `WorldObject` PER INHABITED PLACE.** Not a dictionary. It already
survives save/load, already carries a faction, already holds a pawn list, and ⭐ **it draws
on the world map** — so an inhabited place is visible from orbit before the player lands,
and the world map becomes a census. After a raid the same object reads *abandoned*.

**7. EVERY PERSON IS DOCUMENTED DEEPLY. NOBODY IS FLAT.** Owner: *"I want ALL of the people
documented deeply... it matters."* ⛔ The tier CHECK proposed (one named pawn, rest
generated) and the tier DECIDE proposed (deep for leaders, shallow for drudges) are BOTH
overturned. What varies is REGISTER, never depth.
🔑 **And the reason is the campaign's own point.** The owner: *"But are there really little
people in the world? Remember we're playing Jawa..."* ⇒ A Jawa clan is exactly who every
other faction calls an extra. A system that renders other people's crowds as anonymous
spawns asserts the hierarchy this campaign exists to look at from below. **No anonymous
pawns anywhere in the system.** It also pays off mechanically: buying a person only lands
as a decision if that person is someone.

**8. THE METHOD IS A POOL, NOT A BOOK.** ~300 people is a book of prose; instead author
**150–250 tagged fragments** — backstories, traits, tics, grudges, job-specific miseries —
keyed by role and faction, and let the generator combine them. Every pawn deep and
specific, authoring bounded. The writing effort goes into fragments, which is where it is
easiest to write well.

**9. 🔴 THE TONAL BRIEF, and it corrects DECIDE's framing rather than choosing from it.**
DECIDE offered "comic drudges under a grave world". The owner's answer, verbatim:
> *"There should be heartbreaking cases, hilarious examples, bizarre characters, utterly
> boring dweebs... they should not just be 'real people' with complexity, but
> **theatrically interesting**. One or two of them should be REALLY strange and
> interesting, while the rest are just the bizarre background that Star Wars usually has.
> We're recreating the **traditional Star Wars movie feel**, not the dark gritty
> Andor-type stuff. This isn't a WW2 recreation, it's a living breathing impossibly sci-fi
> world with **contradictory ethics living side by side in a way that seems utterly
> ridiculous and yet entrancing**."*

⇒ **THE CANTINA PRINCIPLE.** Not comedy versus gravity — *all registers at once, none of
them ironic*. Four registers to tag the fragment pool with: **heartbreaking · hilarious ·
bizarre · utterly boring**. "Utterly boring dweeb" is a REGISTER, deliberately dull people
are part of the texture, and they are still documented deeply.
⭐ **Distribution rule: one or two REALLY strange standouts per cast; the rest is bizarre
background.** A cast where everyone is remarkable has nobody remarkable in it.
⛔ **Not Andor.** No grit-as-seriousness. The world is impossible and cheerful about it.

**10. TIME — FROZEN UNTIL VISITED.** A roster changes only through the player's actions.
⇒ every change in the world is legibly the player's doing, which suits a hand-made frozen
planet, and it removes the risk of a beloved NPC dying offscreen to a dice roll.

━━━ 🔴 ROUND 3, 2026-08-19. The mechanic that ties it together ━━━

**11. FATE IS `RESIDENT` BY DEFAULT — flight is CAUSED, never a timer.** Owner: *"if they
flee it's because they must because you threatened them... and faction lowers from it. Not
a timer."* ⇒ The `LordJob_TradeWithColony` visitor arc is demoted from template to one FATE
among several. Three causes of flight, all player-caused or player-adjacent:
  a. **threat** — you menaced them. **Goodwill drops with it**, and today's ruling applies:
     hostile at −75, and hysteresis means it only ENDS at 0. No cheap apology.
  b. ⭐ **ARRIVAL** — *"hostile factions on the map might immediately declare flight when a
     giant gravship comes out of the sky, that's very reasonable."* The gravship is a
     PRESENCE in the world, not just transport. Some casts break at the sight of it.
  c. **hunger** — the larder empties, *"they try stealing from the player perhaps"*, and
     THEN they go. ⇒ the shipped forbid-flag hole (non-player pawns ignore player forbid
     flags and will raid a colony stockpile) stops being a defect and becomes **the warning
     shot before departure**.

**12. THE DEAD ARE SIMPLY GONE.** Owner: *"those who die when you aren't watching are
simply... forgotten. Lost. Very Star Wars actually. They are 'eaten and forgotten.'"*
⇒ No death record, no memorial, no ledger. **The absence IS the memory.** It also falls out
of the architecture for free: survivors return to the roster and the dead do not.

**13. ⭐⭐ RECURRING CHARACTERS — the best idea in the concept, and it is new.** Owner:
*"I really like that you might start recognizing returning characters for the various
factions from who you met on a map one day. 'Wasn't that guy working a refinery awhile
ago?'"*
⇒ **A DISPLACED POOL.** People who lose their place — fled, burned out, sold, abandoned —
are not destroyed. They go into a per-faction pool of the placeless. **When any cast is
next instantiated, it draws from that pool BEFORE generating anyone new.**
  · The world redistributes instead of only emptying.
  · Player actions ripple: raid one Hutt refinery, meet those survivors at the next one —
    carrying RimWorld's own memory of what you did to them, for free.
  · 🔑 **It does not violate "frozen until visited"**: redistribution happens at cast
    INSTANTIATION, i.e. when a map generates, never on a background tick. Still entirely
    event-driven by the player.
  · ⚠️ It requires the roster to hold REAL `Pawn` objects, which `ThingOwner<Pawn>` on a
    `WorldObject` already does — the `Caravan` pattern. A record-based roster could not do
    this at all.

**14. FOOD STOCKS ARE EXPOSED AND RAIDABLE — confirmed.** Owner: *"I like that their food
stocks are exposed. Very realistic."* A place that cannot feed its cast is not a place yet.
Since NPCs cannot farm (three shipped walls), sustenance is PRESENT rather than produced,
and it is visible, stealable and destroyable. Burn the granary and they leave — that is
FATE:flee firing for a reason the player caused.

━━━ 🔴 ROUND 4, 2026-08-19. Drift needs a reason, and the loop closes on the player ━━━

**15. CROSS-FACTION DRIFT: POSSIBLE, RARE, AND IT MUST CARRY A STORY.** Owner: *"Drift
between factions should be possible but rare and have a story... a reason. Enslavement.
Escape from their old owner. A lost battle."*
⇒ **A displaced person carries a REASON, and the reason is what licenses a faction change.**
Drift is never random; it is narratively caused and the player can read the cause.

| reason | may change faction? |
|---|---|
| **Enslaved** | ✅ yes — to the new owner's faction. Ties to `Slavery_Acceptable` and the Jawa-trader / Hutt-keeper split |
| **Escaped an owner** | ✅ yes — to factionless, or to whoever shelters them |
| **Lost a battle** | ✅ yes — absorbed by the victor |
| **Sold by the player** | ✅ yes — to the buyer's cast. This is the owner's own sale mechanic |
| **Fled a threat** | ⛔ no — stays in faction, resurfaces at another of its sites |
| **Starved out** | ⛔ no — same |

**16. ⭐⭐ THE LOOP CLOSES ON THE PLAYER — and this is the emotional keystone of the whole
system.** Owner: *"I love the recruitment story... it makes beggars suddenly much more
heartwrenching when they're the people you destroyed the livelihoods of recently."*
⇒ **The displaced pool feeds THREE consumers, not one:**
  1. **new casts** — the recurring-character effect (round 3)
  2. ⭐ **BEGGARS AND REFUGEES AT THE PLAYER'S OWN COLONY.** `GiveQuest_Beggars`
     ("beggars arrive") ships in this build. Draw its pawns from the displaced pool and
     **the beggars at your gate are the people whose livelihood you burned down last
     month.** The game already tells you their name and their history; it does not need to
     tell you whose fault it is.
  3. **recruitment** — you can hire out of the same pool. *"I burned down his refinery and
     now he works for me"* is the most Star Wars sentence this system can produce.
⇒ 🔑 **The design has no morality system, no karma meter and no reputation number for this,
and it must not grow one.** The consequence is delivered entirely by RimWorld's existing
name, backstory and memory systems plus the player's own recognition. That is why it works.
