## the ask — split into two items on the owner's ruling

Owner, 2026-09-07: *"Let's make two items out of this. A validated string of
automated functionality that can be tested that walks through most of its
behavior, and then a human-executable exploration that verifies to a human
interaction level everything looks ok."*

**This item is the FIRST half: author the automated walk.** The human half is
`MOD_HUMAN_EXPLORATION_PASS_1`.

⭐ **And the owner's insight that shapes both:** *"validating THAT as a human
could be a GREAT way to confirm the actual functionality actually! I love this.
Test driven development at last."* — the validation plan is itself the
specification of what each mod is FOR. Reviewing the plan is a way of checking
the mod, before anything runs.

## timing — ruled

**Write NOW, run later.** Owner: *"we can write them now, understanding they may
evolve as we actually grow the algorithms themselves and discover limitations and
new user preferences. But we can start with a validation plan right now, yes."*

Authoring is offline and needs no game. The campaign itself belongs in the next
v1 phase, after the art sheets and normalization.
⚠️ **These lines WILL evolve.** They are a starting plan, not a contract — revise
them as the systems grow rather than treating a stale line as a failure.

## scope — MEASURED 2026-09-07, and it is ALL of them

| | count |
|---|---:|
| our mods in `src/` | **76** |
| active in the live list | 50 |
| active, no third-party deps → testable on the bare minimal list | 33 |
| active, needs one donor mod added to the list | 17 |
| **built but NOT active** | **26** |

🔴 **All 76 are in scope. Owner, 2026-09-07: *"We are shipping everything, or else
abandoning it."*** The inactive 26 (incl. `WeatherSuite`, `VaultDungeons`) get
switched on for their own minimal-list load. There is no parked tier — a mod is
either shipping or retired, and this pass is where that is decided.

## what to author, per mod

One entry per mod: **what must be true, and the exact check that shows it** —
a `Player.log` string, a def read-back, a bridge call, or a named on-screen
sighting. Worked shapes:

- **Cuisine** — a campaign meal def exists; a pawn can cook one; it is edible.
- **Pits** — a pit spawns on a quicktest map; a pawn can fall in; it can be exited.
- **Droids** — a droid pawnkind spawns in its faction; its recipes resolve; a
  restraining bolt applies.
- **Water types / liquid biomes** — each terrain exists; a pawn entering behaves
  as the type says.

🔑 Prefer checks a script can run unattended, so the campaign is execution rather
than judgement. Anything genuinely visual belongs in the human pass instead.

## why this is cheap

A minimal-list cold load is **~22 s** (against ~15 min on the full 599). One mod
per load keeps attribution perfect and still costs minutes, not hours.

## relationship to the dashboard
Feeds `PROJECT_MATURITY_DASHBOARD_1`: passing a mod's automated walk is what
promotes it toward `checked-out` on the FUNCTION axis. ⛔ Per that item's standing
constraint, **this must never become a gate on ordinary work** — it is a campaign
entered deliberately, never a per-check-in tax.
