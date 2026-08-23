## ✅ ANSWERED — the map stands, so nothing here was ever dead, 2026-08-23

**Owner, asked directly whether the hand-remake was still happening: "the current map stands."**

🔑 **That dissolves this item's premise rather than answering its table.** Every question below
is framed as *"measurement of the dead paint — or a target the new world must hit?"* There is no
new world. **Ash'karr as painted IS the v1 planet**, including today's nightside layering, so
every planet value is a LIVE description of the world we are shipping. None of them is a record
of something replaced.

⛔ **`planet.status` STAYS `remaking`, and that is not an oversight.** The owner's own four-step
sequence, recorded in `canon.yml`, makes **the freeze a SAVEGAME**: map → port-survival proof
through the live bridge → factions, leader names and ideoligions correct at initiation → save the
game. **Step 1 is now settled; steps 2–4 have not happened.** Writing `frozen` would assert a
saved world that does not exist, so the planet rules stay ADVISORY — but their reports are now
*meaningful* instead of misleading, because they compare against the live planet.

### What was actually wrong, measured 2026-08-23

⭐ **Six of the seven values in the table below needed NOTHING**, and the table itself was the
stale part:

| the table says | measured / read today |
|---|---|
| `water` 8.14% | ⛔ **canon has not said 8.14 since 2026-08-22.** It reads 5.19% liquid / **6.46% incl-ice**, re-measured, and my own count of the CSV agrees exactly at 6.46%. |
| `tiles` 21872 | ✅ unchanged and correct |
| `terminator` +14 °C | ✅ already reconciled in canon: ruled +14, realised median **+13.0** after the 5.5 °C/km lapse. My measurement of arc 88–92 returns +13.0. Both true. |
| `habitable_ring_arc` [40, 57] | ✅ **not a conflict, and canon already says so**: *"a DESIGN band, not a settlement census… Do not 'correct' one against the other."* I measured settlements at arc 19…116 and did NOT file it. |
| `axis` arc | ✅ durable — how the mod evaluates its curve |
| `lake` keep | ✅ The Scald exists (312 tiles, arc ≤ 82) and still defends it |
| `settlements` 72 | 🔴 **the one genuinely stale value — now 120.** Corrected in canon with its own `superseded:` entry. |

⚠️ **`72` is superseded by MEASUREMENT, not by a ruling** — it was a correct count of this same
world before the settlement passes of 2026-08-22/23. It is not a dead world's number and must not
be filed beside the `37` and `66` entries as though it were.

---

## Spec

The owner told REP on 2026-08-22: *"I am working with DECIDE to remake the planet an
entirely different way, so there is no current frozen world."*

`infrastructure/state/canon.yml` now carries **`planet.status: remaking`**, and
`check_canon.py` downgrades every planet-derived rule to **advisory** while it reads that
— reported, never blocking. **Nothing was deleted.** The old numbers stay as the record of
what Ash'karr-as-painted was.

**Your call, and only yours: which of these are properties of THE PLANET (dead with it)
and which are DESIGN RULINGS that carry to any world we build?**

| canon rule | value | the question |
|---|---|---|
| `water` | 8.14%, 1780 of 21872 tiles | measurement of the dead paint — or is 8.14% a target the new world must hit? |
| `tiles` | 21872 | subdivision 7. Does the new planet use the same grid? |
| `settlements` | 72 | a count of the dead paint, or a design target? |
| `axis` | arc, not latitude | ⭐ **probably durable** — it is how the MOD evaluates its curve, not a fact about our paint |
| `terminator` | +14 °C | the owner's **ruled** endpoints. A ruling survives its world unless he says otherwise |
| `lake` | keep | depends on The Scald existing. If the new world has no Scald, the def has no defender |
| `habitable_ring_arc` | `[40, 57]` | 🔴 **ruled by the owner 2026-08-21**, not measured. Does the ruling carry? |

⛔ **Not planet-derived and still enforced, deliberately:** `factions` (13), `bestiary`
(108), `modlist_undated`. Do not suspend these — they are about the roster, a document
and the mod list, none of which the remake touches.

## Watch out

- 🔴 **The suspension is the only reason you can write the remake at all.**
  `block_canon_contradiction.py` moved from the commit to the **WRITE** on 2026-08-22, so
  before this change a doc stating the new planet's water percentage was refused
  mid-sentence, citing the dead world's. If you ever set `planet.status` back to `frozen`
  while still drafting, that returns.
- ⚠️ **`canon.yml`'s `as_of` still reads 2026-08-20 and its `accepted_on` / `accepted_by`
  still describe the superseded world.** Left untouched on purpose — they are that
  world's record, not claims about the current one. Decide whether they should be moved
  under a `superseded_world:` key rather than edited in place.
- 🔑 **Nine-plus docs already carry your `WORLD_ADOPTED_AUTHORING_OPEN_1` banner**
  superseding `WORLD_FROZEN_RETHINK_PLANET_1`. That banner says *adopted, authoring open* —
  which is **not** the same as *there is no frozen world and we are rebuilding it
  differently*. A seat reading it will still think the shape is settled.
- ⚠️ **`world/ASHKARR_WORLDMAP_*.csv` and `design/Jawa/worldbuilding/the_one_map.md`
  describe the dead world**, and `the_one_map.md` is cited as the visual target by
  `CLAUDE.md`. Nothing enforces them, but seats read them as current.
- ⛔ **Do not treat this item as permission to change canon values.** Suspending
  enforcement was REP's call because it was blocking you; deciding what the new world's
  numbers ARE is yours and the owner's.

## Verify

`python3 src/RimMandrake/Utils/check_canon.py --list` names every suspended rule and
prints the restore condition. `python3 src/RimMandrake/Utils/check_canon.py design/`
reports planet contradictions as advisory and still fails on a faction-count error.

## Criteria

Each row above is marked **carries** or **dies with the old world** in `canon.yml`, with a
one-line `_src` saying which and why. When a new world is frozen, `planet.status` returns
to `frozen` and the surviving rules bite again.
