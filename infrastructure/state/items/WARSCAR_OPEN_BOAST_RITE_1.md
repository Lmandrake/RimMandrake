# WARSCAR_OPEN_BOAST_RITE_1 — The Open Boast, for Ozzik: declare an ambition, answer with the colony's name, and let the war hear it

Caused by `GREENTIDE_SCORING_SITTING_1` (turn 1). Campaign tier, `mandrake.rut.rites` (found rite), found in
the **Warscar**. Design: `design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` §5
idea 4 (GPT, "Ozzik's Open Boast"), §8. Register: `design/Jawa/salvation_rites_2026-10-01.md` B11 (row
added) and §(d).

Ruling, owner, typed 2026-10-02: *"Use first and third. First can be here. Build it outside the ship and
let it be taken.  Works better the better the room. The third works on another map that doesn’t have one
for this god yet. Likely one with open sight lines."* The third is the Open Boast. Its home, decision taken
by question card 2026-10-02 07:52 PDT: **the Warscar** (no Ozzik rite yet; open sight lines across the old
battlefield's slag terraces and craters). Pitched on the card as *"each member declares an ambition and
the colony shouts its name; days later a warned enemy may come to answer the boast. Once per colony."*,
and chosen in that form.

⚠️ Ozzik's found-rite count with this rite and the Ceded Room is **five**, one over the four-rite cap
(register B11 note); recorded for the owner, nothing cut.

## spec

**God: Ozzik** (pride and grief; his dangerous encouragement of ambition is never villainy). Kind:
feeding (pride fed by a public boast). One `GameComponent_Ninefold.ApplyDelta(God.Ozzik, <sized by outcome
quality>, "The Open Boast")` per performance, the call shape of `SUMP_SINKING_RITE_BUILD_1`.

1. **Found / learned.** Inscription `RUT_OpenBoastRostrum`: on a slag terrace with a long open view over
   the old killing ground, a broken reviewing rostrum of scorched plate, its rail gouged over and over
   with names and claims of greatness that contradict each other, every one of them louder than the last,
   none of them answered by anyone still alive. Placed on Warscar maps by a map GenStep with a chance,
   preferring a cell with long clear sight lines (high ground, no roof, few blocking things within a wide
   radius; first value: the cell with the most unblocked cells within 30 among the candidates sampled).
   Never worldgen. It targets `BiomeDef/RM_Warscar` (the frozen twin `RUT_Scarlands` is retired at the
   repaint). Rubbing (`CompStudiable`) → the Rites tab's "found rites" row → `RUT_ResearchMod_GrantRite`
   adds the precept, per §(d). Performable after on any map.
2. **Asks.** A gathering at a spot the player picks, indoors or out. Each participant in turn declares an
   ambition (a short generated line from a rule pack: a goal phrased in the colony's voice), and the whole
   congregation answers with the colony's name. Vanilla ritual roles: a speaker and the congregation; no
   material cost.
3. **The war hears it.** On a good-enough outcome, the rite records the boast in a saved
   `RUT_GameComponent_OpenBoast` (date, participants, their lines) and **may** queue a challenge: a
   hostile raid from an existing hostile faction (never a new faction), arriving in a window some days
   later (Mod Settings, default 3 to 6 days, chance default about 0.6). The **warning comes first**: a
   letter when the challenge is queued, naming the faction and the arrival window, so the player can
   prepare. The raid arrives through vanilla raid machinery (points by the storyteller's normal curve, a
   modest bonus by outcome quality); its arrival letter quotes one participant's boast back.
4. **Once per colony.** After a completed performance the precept's ritual reports unavailable forever in
   that colony, with a reason line ("the colony has already given the war its name"). A failed or
   interrupted performance does not spend it.
5. **Outcomes: cohesion only.** Shared memories by quality. Ozzik's pleasure is told by the Narrator
   (*"Ozzik has carried your small names farther than you intended"*) and shows only as events (the
   challenge) and odds, never a buff, hediff or stat. The challenge is the risk, not a punishment.
6. **Readable signs:** the rostrum's crowded rail on the map, the permanent record of the participants'
   words (an inspect page on the component or a tale), the warning letter with its window, the raiders
   arriving normally.
7. **Mod Settings:** on/off; challenge chance; arrival window; raid points bonus; inscription chance.

Collision check (review §5): unlike the Sump's Price for Mob'Unloo it invites a hostile answer rather than
holding a faction off; unlike the Pyrelands' Struck Glass it makes a lasting public notoriety, not an
instant catastrophe. No other Ozzik rite is a public declaration.

Depends on: `SALVATION_RITES_UNIFICATION_1` (found-rite machinery, `RUT_ResearchMod_GrantRite`). Related,
not duplicated: the Warscar's other pitched rites (the Deserter's Welcome, Ohm; the Vindication Walk,
Ta'Baa; register B7) are unaffected. Art: `infrastructure/artpipe/art_lists/greentide_turn1_2026-10-02.csv`
(`RUT_OpenBoastRostrum`).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded as cases in `src/RimUtinni/Rites/validation.py`:
- Forcing the GenStep on a test Warscar map spawns one `RUT_OpenBoastRostrum`; with chance 0 none. A
  planet/world read shows no change.
- Studying it to completion: the found-rites row lists the Open Boast and the precept is granted.
- With the challenge chance forced to 1: after a completed performance, `RUT_GameComponent_OpenBoast` holds
  one record with every participant's line; one warning letter exists naming a faction that is hostile to
  the player at that moment; a queued incident exists with a fire tick inside the configured window.
  Simulating to the fire tick spawns a raid lord of that faction.
- With the chance forced to 0: the record exists, no letter, no queued incident.
- A second performance is refused with the reason line; an interrupted first performance leaves the rite
  available.
- Ninefold holds one Ozzik delta tagged "The Open Boast"; no new hediff or stat on any participant.
- Each Mod Settings toggle off removes exactly its effect.
