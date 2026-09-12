# SOURCES — dungeon & experience-design corpus (DUNGEON_DESIGN_RESEARCH_1)

Annotated, load-bearing sources only. Grouped by what they are FOR. Each entry:
URL · credibility · what to mine it for. Gathered 2026-09-11; web sources decay —
re-verify a URL before citing it in a shipping doc.

## Dungeon topology & structure

1. **Xandering (Jaquaying) the Dungeon** — Justin Alexander, The Alexandrian.
   https://thealexandrian.net/wordpress/13085/roleplaying-games/xandering-the-dungeon
   (techniques list in Part 2: https://thealexandrian.net/wordpress/13103/roleplaying-games/xandering-the-dungeon-part-2-xandering-techniques)
   The most-cited essay series on non-linear dungeon topology; 15 years of OSR practice built on it.
   Mine for: the 12 named techniques (loops, multiple entrances, discontinuous level
   connections, midpoint entry, sub-levels, secret paths…). Direct input to any vault layout.

2. **Cyclic Dungeon Generation (Unexplored)** — Joris Dormans; write-ups:
   https://www.gamedeveloper.com/design/unexplored-s-secret-cyclic-dungeon-generation-
   and https://www.boristhebrave.com/2021/04/10/dungeon-generation-in-unexplored/
   and the tabletop distillation https://sersavictory.itch.io/cyclic-dungeon-generation
   Shipped-game proof that LOOPS, not trees, are the primitive of good dungeon flow;
   catalogs cycle types (lock-and-key, hidden shortcut, foreshadow-then-payoff, danger loop).
   Mine for: the cycle-pattern vocabulary — usable as a hand-authoring checklist even though
   we never generate procedurally.

3. **Lock and Key Dungeons** — Boris the Brave.
   https://www.boristhebrave.com/2021/02/27/lock-and-key-dungeons/
   Rigorous synthesis of lock-key graph theory over Zelda-style dungeons.
   Mine for: formal lock/key graph notation; how key-before-lock ordering constrains layout.

4. **Boss Keys** — Mark Brown (Game Maker's Toolkit), YouTube series; overview:
   https://roomescapeartist.com/2017/09/10/boss-keys-analysis-zelda-dungeons/
   Every Zelda dungeon mapped as a lock-key diagram; the de-facto standard visual language
   for dungeon linearity analysis. Mine for: the diagram method itself (our linearity metric),
   and per-dungeon verdicts on what made each feel good or rote.

5. **Five Room Dungeon** — Johnn Four, Roleplaying Tips.
   https://www.roleplayingtips.com/5-room-dungeons/ (variants: https://gnomestew.com/the-nine-forms-of-the-five-room-dungeon/)
   20-year-proven minimal adventure skeleton (guardian / puzzle / red herring / climax / twist).
   Mine for: the smallest complete dungeon shape — right-sized for a quest-site map.

6. **Skyrim's Modular Level Design** — Joel Burgess & Nathan Purkeypile, GDC 2013 transcript.
   http://blog.joelburgess.com/2013/04/skyrims-modular-level-design-gdc-2013.html
   First-party AAA practice from the studio that shipped 150+ dungeons.
   Mine for: kit-based authoring discipline, the loop-back-to-entrance exit convention,
   pacing a dungeon for a 20–40 minute visit.

## Celebrated maps (primary analyses)

7. **Recursive Unlocking: Resident Evil's map design with data visualization** — Chris's
   Survival Horror Quest. https://horror.dreamdawn.com/?p=81213
   Rare QUANTIFIED map analysis (116 rooms, visit counts, unlock graph of Spencer Mansion).
   Mine for: the hub-with-deepening-wings template and "most rooms visited ~2×" as a
   backtracking benchmark.

8. **Undead Burg** — The Level Design Book case study.
   https://book.leveldesignbook.com/studies/sp/undead-burg
   (supporting: https://www.pcgamesn.com/dark-souls-remastered/undead-burg-level-design-verticality)
   Canonical modern analysis of critical-path + side-loop + shortcut-unlock structure.
   Mine for: the "forcibly bend a straight path into a circle" rule; shortcut-as-reward.

9. **Grognardia: 30 Greatest D&D Adventures** — James Maliszewski.
   http://grognardia.blogspot.com/2008/09/30-greatest-d-adventures-of-all-time.html
   Respected OSR historian; consensus roster of tabletop dungeon canon (Caverns of Thracia,
   Tomb of Horrors, Ravenloft, Temple of Elemental Evil). Mine for: which modules to study
   and why each earned its place.

10. **Zelda dungeon rankings/analyses** — e.g. https://www.denofgeek.com/games/best-legend-of-zelda-dungeons-ever-ranked/
    and https://hyruleuniversity.wordpress.com/2017/11/04/dungeon-design-in-the-wind-waker/
    Enthusiast-grade but convergent: the same dungeons (Eagle's Tower, Stone Tower, Forest
    Temple) top every list for the same structural reasons. Mine for: the specific mechanisms
    each is celebrated for (map-restructuring, inversion, hub-and-spoke).

11. **Dungeon Generation in Diablo 1** — Boris the Brave.
    https://www.boristhebrave.com/2019/07/14/dungeon-generation-in-diablo-1/
    Mine for: what room/corridor grammar reads as "dungeon" on a square tile grid at all.

## Roguelike design literature

12. **Brian Walker on Brogue** — Roguelike Celebration 2018 talk
    https://www.youtube.com/watch?v=Uo9-IcHhq_w and Eggplant podcast ep. 18
    https://eggplant.show/18-exploring-brogue-with-brian-walker
    The most design-literate solo roguelike dev; Brogue's lever-gated guardian vaults are
    the genre's cleanest risk-for-loot rooms. Mine for: "machines" (self-contained puzzle/
    reward rooms), terrain-as-systemic-threat, elegance-by-subtraction.

13. **Dungeon Crawl Stone Soup design philosophy** — DCSS manual, philosophy section.
    https://github.com/crawl/crawl/blob/master/crawl-ref/docs/crawl_manual.rst
    A living, 20-year-enforced anti-tedium constitution: "meaningful decisions (no
    no-brainers)", "avoidance of grinding (no scumming)". Mine for: the tedium metric —
    any low-risk/high-time/some-reward loop is a design bug, stated as policy.

14. **RogueBasin** — https://www.roguebasin.com/ — community wiki of 30 years of roguelike
    design articles. Mine for: encounter/level design articles when a specific mechanism
    needs precedent; treat individual articles as variable quality.

## Pacing, encounters, drama

15. **The AI Systems of Left 4 Dead** — Michael Booth, Valve, GDC 2009 slides (primary).
    https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
    THE reference for measured dramatic pacing: per-player intensity estimate, peak→relax
    cycle, "structured unpredictability". Mine for: the intensity model itself — it is
    directly computable from RimWorld combat events.

16. **Level Up! / beat charts** — Scott Rogers; summary:
    https://www.gamedeveloper.com/design/beat-chart-game-designer-s-best-friend
    Standard industry planning artifact. Mine for: the beat-chart format (columns per beat:
    location, threat, reward, intensity) to spec each dungeon before building.

17. **Single Player Level Design Pacing and Gameplay Beats** — Pete Ellis (Guerrilla), 3 parts.
    https://www.worldofleveldesign.com/categories/wold-members-tutorials/peteellis/level-design-pacing-gameplay-beats-part1.php
    Working-designer method for intensity graphs (time on X, intensity on Y, rising peaks,
    troughs mandatory). Mine for: the plotting method our review sheets can copy.

18. **The Level Design Book — Pacing** — https://book.leveldesignbook.com/process/preproduction/pacing
    Best free synthesis: beats, pulse/accent/rest/motif/syncopation, teach-test-twist,
    intensity ≠ difficulty. Mine for: vocabulary + the rule "avoid maximum-intensity finales".

19. **Embracing Push Forward Combat in DOOM** — Loudy & Campbell, id Software, GDC 2018.
    https://www.gdcvault.com/play/1024940/Embracing-Push-Forward-Combat-in
    Mine for: enemy ROLE archetypes composing an encounter, lock-in arena set-pieces,
    incentives that pull players forward instead of turtling — the direct antidote to
    RimWorld's turtle/killbox instinct inside a dungeon.

20. **Darkest Dungeon: A Design Postmortem** — Chris Bourassa & Tyler Sigman, GDC 2016.
    https://gdcvault.com/play/1023089/Darkest-Dungeon-A-Design
    Corridor-node expedition structure, stress as a second health bar, punishing-but-fair
    tone management. Mine for: expedition rhythm (hall → room → camp) and how horror tone
    survives repetition.

21. **Environmental storytelling** — Worch & Smith, "What Happened Here?", GDC 2010.
    Slides: http://www.worch.com/files/gdc/What_Happened_Here_Web_Notes_Small.pdf
    (also GDC Vault: https://gdcvault.com/play/1012647/What-Happened-Here-Environmental)
    The founding talk on staged-space narrative. Mine for: vignette grammar — the
    Rakata-tyranny reveal must be READ from scenes, not told in letters.

## Playability & experience metrics (academic)

22. **GameFlow: a model for evaluating player enjoyment in games** — Sweetser & Wyeth 2005.
    https://dl.acm.org/doi/10.1145/1077246.1077253
    (detailed-heuristics revision: https://eprints.qut.edu.au/58216/15/JournCT-GameFlow.pdf)
    2300+ citations; the standard flow-based evaluation rubric (8 elements, per-element
    criteria). Mine for: the expert-review checklist our metrics file operationalizes.

23. **Game Experience Questionnaire (GEQ)** — IJsselsteijn, de Kort, Poels, TU Eindhoven.
    https://pure.tue.nl/ws/files/21666907/Game_Experience_Questionnaire_English.pdf
    Most-used post-play questionnaire (7 components incl. Tension, Challenge, Immersion;
    has a short in-game version). Caveat: later validation work
    (https://www.sciencedirect.com/science/article/abs/pii/S1071581918302337) questions its
    factor structure — use as structured prompts, not as a psychometric instrument.

24. **HEP / PLAY playability heuristics** — Desurvire et al., CHI 2004 / HCII 2009.
    https://dl.acm.org/doi/10.1145/985921.986102 and
    https://dl.acm.org/doi/10.1007/978-3-642-02774-1_60
    Heuristic evaluation catalogs (game play, skill development, immersion, usability)
    validated against shipped-game reception. Mine for: prototype-stage review questions —
    usable on a paper map before anything is built.

25. **MDA: A Formal Approach to Game Design** — Hunicke, LeBlanc, Zubek, 2004.
    https://users.cs.northwestern.edu/~hunicke/MDA.pdf
    The mechanics→dynamics→aesthetics lens plus the 8 "kinds of fun" taxonomy.
    Mine for: the aesthetics checklist (which funs does this dungeon serve?) and the
    designer-builds-bottom-up / player-meets-top-down inversion.

26. **Telemetry & automated playtesting** —
    https://salivity.github.io/game-development/article/using-telemetry-heatmaps-to-analyze-player-behavior
    plus PaceMaker (pacing tool, https://arxiv.org/pdf/2408.15001) and AI-director
    evaluation (https://arxiv.org/pdf/2410.03733). Mine for: death/pathing heatmaps,
    time-to-complete distributions, agent-based difficulty estimation — all reproducible
    through our bridge with scripted crews.

## Tedium & friction

27. **Busywork is not Fun** — Tadhg Kelly, What Games Are.
    https://www.whatgamesare.com/2011/06/busywork-is-not-fun-design.html
    Sharp definition: busywork = time-between-meaningful-actions inflated to fake engagement.
    Mine for: the busywork test applied to hauling/walking inside a dungeon map.

28. **Rub the Right Way: Applying Friction in Game Design** — Scree Games.
    https://screegames.com/2024/04/02/rub-the-right-way-applying-friction-in-game-design/
    The counterweight: friction is a tool (deliberate slowness = dread, weight); the sin is
    UNCHOSEN friction. Mine for: distinguishing tension-friction from tedium-friction.

## RimWorld-native precedent

29. **RimWorld Anomaly underground maps** — official wiki + Ludeon dev blog.
    https://rimworldwiki.com/wiki/Labyrinth and https://rimworldwiki.com/wiki/Undercave
    and https://ludeon.com/blog/2024/04/integrating-anomaly-more-with-the-rest-of-the-game/
    First-party proof of dungeons ON THIS ENGINE: pocket-map entry, loot-vs-extraction
    tension, and the undercave's post-boss 10-hour collapse timer (a shipped, tested
    "leave now" mechanic). Mine for: what the engine already supports and how players
    received it.

30. **RimWorld Defense tactics / killbox corpus** — https://rimworldwiki.com/wiki/Defense_tactics
    Community-documented AI pathing exploitation (funneling, path-of-least-resistance).
    Mine for: the INVERSE problem — a dungeon garrison faces the same player who kills
    raids by funneling; every defensive trick players use is an exploit our dungeons must
    anticipate (or deliberately permit).
