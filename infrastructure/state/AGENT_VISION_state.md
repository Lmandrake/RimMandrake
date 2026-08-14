# AGENT_VISION_state.md — where VISION is

**Cross-session address:** `uds:/run/user/1000/cc-socks/212269.sock`
_(Session started 2026-08-13, the seat's first. Address read from this session's
own parent PID — re-check after any CLI restart.)_

Identity: injected by `src/RimMandrake/Utils/set_agent_window.sh VISION`.
Queue: `infrastructure/state/queue/VISION.md`. I own
`design/Jawa/worldbuilding/` and that queue; nobody else edits either.

---

## 0. What this seat is for, in one line

**I ask "does the player ever notice this, and is it fun?"** I specify; CREATE
builds. A spec that leaves CREATE guessing is not finished.

## 1. 🔴 The one thing outstanding

**Did the Configure Factions page get ticked, and is there a screenshot?**
Asked of the owner; unanswered at time of writing. A map exists, so **the page is
spent either way** — it is seen once per worldgen and cannot be revisited. Without
an image we can never check `WORLDGEN_FACTION_CHECKLIST.md` against what actually
happened, and **the Fallen Dominion's name is generated, so no grep will ever
find it.** If the list went by unticked, the world has Yautja clans, Norse
kingdoms and troll factions in it and only a regeneration fixes that.

## 2. What this session decided — the owner's rulings, all landed

| # | ruling | where it lives |
|---|---|---|
| 1 | **ONE permanent enemy.** Junkers demoted to hostile-but-bribable | `faction_roster_v2.md` |
| 2 | **No Imperial Droid Army.** Two Empires: planetside aristocratic + Galactic. The **Galactic Empire pursues the ship** | `gravship_pursuer_mechanism.md` header |
| 3 | ⭐ **The Fallen Dominion is the design, not a defect** — disgraced local aristocracy welded into the Empire, hunting us to earn its way back | `WORLDGEN_FACTION_CHECKLIST.md` R3 |
| 4 | ⭐ **Space towers are the Empire's surface access.** Hutts pay to cut them; **retaliation is the cost** — kills the dependency on the unbuilt Heat gauge | `orbital_towers_and_the_sky_ladder.md` |
| 5 | **Sky ladder shape:** 3–5 authored backbone towers with a real ending, plus repeatable side towers for loot | same file |
| 6 | **Force users are NPC-only, permanently.** The saber is the trophy, not the class | `force_users_build_spec.md` |
| 7 | ⭐ **Water:** differential thirst · defended natural sources · expensive player-built purification · **v2 bottle currency, silver rare** | `water_doctrine.md` |
| 8 | **Lasers are the ship's own legacy armoury**, not a weapon pack. Salvaged tier circulates; full tier is ours alone | `ship_legacy_armoury.md` |

## 3. Queue state — what I closed

**Closed:** V4, V5 (stale roster data) · V6, V-new 1+2 (owner rulings) · V8
(*Sector Director* is canon) · V11 (**Space Tower: KEEP, both kill conditions
cleared**) · V13-CREATE (ship tile cap 4,800 → 6,632) · **V1, V2, V3** — the
roster's last three either/ors:

- **V1** — Homestead has **no random raid draw at all**; hostility is
  event-driven only, which is also the only vehicle its Jedi raid-leader has.
- **V2** — the Covenant of Free Wells is **abstract theist**, one deity: *the
  water that was withdrawn*, pairing with the `Guilty` meme it already carries.
- **V3** — **Geonosian is a xenotype, not a race** (three exist in the dump, no
  race version). Took `OuterRim_Geonosian` so the precept names the xenotype its
  own pawnkinds actually roll.

**Still open:** V7 (the antagonist is live-unverified) · V9 (roster stages 3–4)
· V10 (doc correction) · V13-PROJECT (rebel gear re-cast) · V14 (RimTunes) ·
V15 (broken-infrastructure mod).

## 4. What I owe, and to whom

| owed | to | state |
|---|---|---|
| The water audit's **W-rulings applied INTO the twelve dossiers** — they currently live only in `water_doctrine.md` | v2 authoring | **written, not yet merged into the roster** |
| Junker Scrap-Warrens water doctrine — still assumes universal thirst | v2 | open, rewrite when faction 12 is authored |
| A look at a live **Imperial raid** — does the antagonist look like the antagonist? | myself | wants the bridge; asked, not granted |
| `fixedName` patch so the Dominion keeps its name across worlds | CREATE, later | needs the generated name first |

## 5. Standing rules I set this session, so peers can hold me to them

- **Every quest we author must be OFFERABLE while the clan is aboard the ship.**
  The offer and the site are different layers. Vanilla stays unswept — its gate
  blocks the Accept button, is legible, and reads as *come down to take work*.
- **Dangling references: scenery orphans accepted, dead-end quests refused.** A
  quest the player can accept and cannot finish is the failure that gets blamed
  on us; an absent faction is never missed.
- **Author few pools, deep.** Variation beats volume — a tag-linked dungeon pool
  gives a different run for free; thirty hand-made dungeons is a campaign nobody
  finished building.

## 6. My characteristic failure mode, written down so peers can call it

**Specifying beyond what anyone will build.** Spec ~78%, build ~10%. **Finishing
one thing to buildable beats adding a twelfth dossier.** This session went the
right way — two v1 rows moved because CREATE got strings and a premise instead of
another document — and the pull is always the other direction.
