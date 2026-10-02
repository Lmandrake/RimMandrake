# WEBWORK_FELLED_NOON_RITE_1 — The Felled Noon, for Sh'kaar: fell the tallest tree at high noon and stand bare-headed in the hole

Caused by `WEBWORK_SCORING_SITTING_1` (turn 1). Campaign tier, `mandrake.rut.rites` (found rite). Design:
`design/Jawa/worldbuilding/biomes/webwork_bedazzle_review_2026-10-02.md` §6 R1, §8. Ruling: **The Felled
Noon, for Sh'kaar** (decision taken by question card 2026-10-02 07:17 PDT). Register:
`design/Jawa/salvation_rites_2026-10-01.md` B10 (row added) and §(d) for the found-rite machinery.

Grounding: the Webwork is the one place on the planet where the hungry sun protects you (the owners die in
it). Sh'kaar is fed by exposure; here exposure is safety, and the rite holds both. With this rite Sh'kaar
carries four found rites (the Snuffing, the Anvil Gift, the Shade Tithe, the Felled Noon): at the cap.

## spec

**God: Sh'kaar** (the hungry sun; never "evil"). Kind: feeding. One `GameComponent_Ninefold.ApplyDelta(
God.Shkaar, <sized by outcome quality>, "The Felled Noon")` per performance, the call shape of
`SUMP_SINKING_RITE_BUILD_1`.

1. **Found / learned.** Inscription `RUT_FelledNoonStump`: a great kollavane stump in a ring of old sun,
   the cut face carved with a sun-mark, a ring of bleached ollathrix legs at the edge of the light where
   something waited and burned (`CompStudiable`). Placed on Webwork maps by a map GenStep with a chance
   (never worldgen). Rubbing → the Rites tab's "found rites" row → `RUT_ResearchMod_GrantRite` adds the
   precept, per §(d). Performable after on any map with a living tree.
2. **Asks.**
   - **Target:** the tallest living tree on the map (largest grown tree by def size then growth; a
     `RitualObligationTargetFilter` picks it, the player cannot pick a lesser one). No tree, no rite.
   - **The felling:** participants cut it by hand (the vanilla cut-plant job, no tool requirement beyond
     vanilla) as the ritual's first stage.
   - **At the hour of highest sun.** On a map with a day cycle, the start window is the middle of the
     day (vanilla `DayPercent` about 0.45 to 0.55, a Mod Settings width). 🔴 On a pinned-sun map
     (`RM_MapComponent_PinnedSun` active: Ash'karr's dayside has no night) there is no hour: the gate is
     the sun's elevation at or above the biome's overhead threshold, so on a high-sun tile the rite may
     start whenever, and on a low-sun tile it cannot start at all. BENCH's reading of "high noon" on a
     world with a fixed sun; whether Webwork maps run a pinned sun is UNMEASURED, read it first.
   - **The standing:** participants then stand **bare-headed in the hole the fall leaves** for the rest of
     the rite: they doff head-layer apparel at the start (restored after), and their duty cells are the
     cells whose shade the felled tree was casting, now `ShadeAt` 0. A participant who steps into shade
     before the end lowers quality; one who flees (mental break, downed) leaves the rite.
3. **The owners gather.** On any map with ollathrix (the Webwork), the web feels the fall: every awake
   `RM_Ollathrix` gets a lord duty to go to the nearest shaded cell bordering the sun-hole (`ShadeAt` at or
   above the scald threshold, `WEBWORK_HEAT_SHADE_BUILD_1`) and pace there for the rite's length. They are
   **not pacified and nothing is bargained** (sheet ban 2: no truce): they stay hostile wild animals and
   take anyone who steps back into the shade. The sun is the only thing between them; the scald does the
   rest. Dormant ollathrix wake by the existing `CompWakeUpDormant` path only if a participant is in range,
   as today.
4. **Risk (the point).** Standing unshaded in an overhead-heat biome is vanilla heatstroke (no new
   hediff); on the Webwork it is also a ring of predators at arm's length.
5. **Outcomes: cohesion only.** Shared memories by quality (attendance, how many stood to the end, no one
   stepped back). Sh'kaar's pleasure is told by the Narrator and shows only as events and odds, never a
   buff, hediff or stat.
6. **Readable signs.** The stump left where the tree stood (vanilla stump), the sun-hole (the shade grid
   recomputes and the hole reads as sun), the owners pacing the shade line, the letter naming who stood.
7. **Mod Settings:** on/off; noon window width; the gathering on/off; inscription chance.

Depends on: `SALVATION_RITES_UNIFICATION_1` (found-rite machinery, `RUT_ResearchMod_GrantRite`),
`WEBWORK_HEAT_SHADE_BUILD_1` (the scald reads the shade grid, so the shade line is real; the heat kind makes
the standing dangerous). Art: `infrastructure/artpipe/art_lists/webwork_turn1_2026-10-02.csv`
(`RUT_FelledNoonStump`).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded as cases in `src/RimUtinni/Rites/validation.py`:
- Studying `RUT_FelledNoonStump` to completion: the found-rites row lists the Felled Noon and the precept
  is granted.
- Target: on a map with three trees of differing size, the ritual's target is the largest; on a map with
  none, the rite reports unavailable with a reason line.
- Gate: with a day cycle and `DayPercent` 0.2 the start is refused with a reason; at 0.5 it is allowed.
  With a pinned sun above the overhead threshold it is allowed; below, refused.
- After the felling stage: the target tree is destroyed, a stump exists at its cell, and the participants'
  duty cells all read `ShadeAt` 0; each participant holds no head-layer apparel during the standing and
  holds it again after.
- On a Webwork test map with three awake `RM_Ollathrix`: during the rite each ollathrix's lord duty is the
  gathering, each stands on a cell with `ShadeAt` ≥ the scald threshold within N cells of the sun-hole,
  and none is pacified (faction and hostility unchanged); after the rite their duty is cleared.
- Ninefold holds one Sh'kaar delta tagged "The Felled Noon"; no new hediff or stat on any participant.
- Each Mod Settings toggle off removes exactly its effect.
