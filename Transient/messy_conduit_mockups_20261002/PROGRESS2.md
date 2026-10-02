# PROGRESS2 — nodal cord redesign (FOUNDRY helper, 2026-10-02)

- [x] read design doc + renderer
- [x] nodal planner (graph.py/nodal.py)
- [x] renders 07_*
- [x] selftests
- [x] design doc rewrite
- [x] delete load mock-ups, README

## log
- 12:20 skeleton written
- 12:25 read doc+renderer; scene.nodal_scene + gap_scene added; writing nodal.py
- 12:28 nodal.py written; reduction verified (18 nodes, 13 cord + 3 hidden edges); first render
- 12:30 first 07 jawa + debug render read: works. Coordinator added tricky-config scope (08_tricky_*); adding slack cap, water, tangles, needless spurs, wall terminals
- 12:36 07 look tuned (slack 1.4-2.4, extra 7-16 cells, loops 0.35/cell, heaps 0.8): loopy, matches 06 character. Writing tricky.py (08 gallery)
- 12:39 tricky pass 1 reviewed; fixes: lattice closure, spur-vs-gap scene, bolt only across one break, face hole, bigger strips
- 12:42 08 tricky gallery rendered into Transient (5 PNG); rendering 07 set
- 12:44 07 set (6 PNG) rendered and reviewed; all 08 reviewed. Next: selftest, delete load mock-ups, README, design doc
- 12:46 selftest 44/44 (nodal: census, connected-only, gap, geometry, determinism, tricky rules); load.py + 05_load_* deleted; overview re-rendered
- 12:46 READMEs updated; writing design doc §8.12/8.13 rewrite
- 12:47 measured: nodal 18 cords/4055 pts/0.23 s vs per-cell 25 strands/8178 pts/0.35 s (same scene, Python); lattice 45 cords -> 4 + 1 heap
- 12:52 design doc rewritten (§5-§8: nodal model §8.2, tricky §8.7, effort/verdict §8.10, art §8.11); refs renumbered; final re-render
- 12:54 DONE: 6x 07 + 5x 08 PNG reviewed, selftest 44/44, doc + READMEs updated. Nothing committed (helper brief forbids git writes).
