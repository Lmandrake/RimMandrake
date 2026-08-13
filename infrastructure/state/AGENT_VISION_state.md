# AGENT_VISION_state.md — where VISION is

**Cross-session address:** `uds:/run/user/1000/cc-socks/212269.sock`
_(Session started 2026-08-13, the seat's first. Address read from this session's
own parent PID, not from a doc — re-check it after any CLI restart.)_

Identity: injected by `src/RimMandrake/Utils/set_agent_window.sh VISION`.
Queue: `infrastructure/state/queue/VISION.md`. I own
`design/Jawa/worldbuilding/` (31 files) and that queue; nobody else edits either.

---

## 0. What this seat is for, in one line

**I ask "does the player ever notice this, and is it fun?"** I specify; CREATE
builds. A spec that leaves CREATE guessing is not finished.

## 1. Where the roster stands — 6 audited defects, 4 now closed

`design/Jawa/worldbuilding/faction_roster_v2.md` (2,510 lines, twelve NPC
factions plus the player Jawa expedition). The Stage 2 gap audit
(`design/Jawa/worldbuilding/faction_stage2_gap_audit.md`) found six defects, each
re-read at source. **Closed in this session's first commit:**

- **D4** — the Bounty Hunter racial table said five species were *"Dry-capable"*
  40 lines under the prose correction saying only `Kaleesh` is. Table now reads
  Kaleesh dry-capable, Zabrak/Bothan/Devaronian **Neutral**, Chiss/Umbaran
  **Heat-intolerant**, matching the BTD gene evidence.
- **D5** — the species-coverage section denied that any NPC faction generates
  Jawa while faction 11 (Indigenous Jawa Clans) is 78% + 12% Jawa, and still
  said *"ten"* NPC factions. Now twelve, and faction 11 is named as the single
  NPC Jawa source.
- **D6** — the Junkers were a second `permanentEnemy` against design pillar 5.
  **Owner ruled ONE permanent enemy**: the Junkers are now hostile-but-bribable.
- **V13 (filed by CREATE)** — `ship_designs.md` "Limits used" carried a
  superseded tile cap. 4,800 → **6,632**; vanilla radii 19/16 → 18.9/16.9. The
  34/30/12 in that row are mod settings and are correct — do not "fix" them.

**Still open, all `[v2]` authoring blockers:**

- **D1** — Homestead raid frequency: *"never raid (Rw 0)"* (`:300`) vs *"Very
  low"* (`:675`). Pick one.
- **D2** — Homestead ideology structure reads *"Abstract theist **or**
  ideological"*. That is two designs and a coin; it blocks `deityPresets`.
- **D3** — Geonosian is specified as a *preferred xenotype* precept while Global
  system 3 sources it from the **race inventory**. Different objects. Follow the
  Free Droid pattern at `:1009`: flag the engine question **and** rule a fallback.

## 2. The one thing I own that touches v1

**No `V1_SCOPE.md` row is mine.** My v1 exposure is the antagonist: row 1 ships
the Directorate's *label* and has passed the gate, but OPS read it live as
`hostile=false`, `permanentEnemy=false`, with a second empire ("The Fallen
Dominion") holding 4 settlements to its 1. **The label ships; the antagonist does
not exist.** That is queue V6/V7 and it is the owner's call, not a reopened row.

**V8 is mine and cheap:** the roster says leader title *"Sector governor"*, the
deployed patch says *"Sector Director"*. Undecided — I have not picked, because
the shipped string is what players see and changing it costs a redeploy.

## 3. Owner rulings I have landed, 2026-08-13

1. **ONE permanent enemy** — pillar 5 stands; Junkers demoted. ✅ in the roster.
2. **No Imperial Droid Army.** Two Empire factions only — the planetside
   aristocratic Empire and the **Galactic Empire**, and it is the Galactic Empire
   that pursues the gravship: stormtroopers, combat droids, Sith. ✅ recorded at
   the top of `design/Jawa/worldbuilding/gravship_pursuer_mechanism.md`. The
   *mechanism* answer below it is unaffected — route A still recommended.
3. **Space Tower: VISION gates CREATE.** CREATE is stopped until I rule. I have
   not ruled. Still `[v2]`.

⭐ **The Sith are an owner-flagged JOINT build** — spec being mined from two
uninstalled Force mods into `design/Jawa/force_users_build_spec.md`. Jedi = rare
raid leader for the moisture farmers; Sith = rare raid leader for the Empire.
Ruling 2 puts this on the pursuit's critical path, not beside it.

## 4. What I owe

| # | owed | to | state |
|---|---|---|---|
| V11 | Space Tower ruling — on-brand? reaches the gravship endgame? | CREATE | **blocking them** |
| V8 | Sector governor vs Sector Director — pick canon | CREATE | undecided |
| D1–D3 | close three either/ors in the roster | v2 authoring | open |
| V14 | RimTunes tagging — 102 songs, ~6 usable combat tracks | — | `[v2]`, unstarted |

## 5. My characteristic failure mode, written down so peers can call it

**Specifying beyond what anyone will build.** The project measured spec ~78%,
build ~10%. More specification is not the constraint. **Finishing one faction to
buildable beats adding a twelfth dossier** — if I hand over a document nobody
can author from without asking me a question, I have produced nothing.
