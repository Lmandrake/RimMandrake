# MessyConduit review round 2 log, 2026-10-04

- 14:05 start; reading docs
- 14:07 read docs+screens; T1 plan: one fallen-wire polyline (insulator->hang->lie->break tip) drawn per frame in span mat, ground layer prints only the fray; st.9 lamp moves inside the shed (conduit under wall); coordinator: modern brackets v2 requeued, use stand-in
- 14:10 T1 code: one-wire LayFallen + per-frame mesh, fan to measured insulators (table regen), selftest 420/420; st.9 lamp moved inside shed
- 14:13 T2: Binding.png+Mouth.png (make_hose_binding.py), DrawEnds wrap+sized fitting at both ends + joiners, open end = wrap+dark mouth, OpenEnd.png deleted; O6 B22 pixel/geometry check PASS (fitting/wrap max 0.95, wrap 1.40x hose)
- 14:15 T3: 9 v1 + modern_v2_east landed (modern v2 north/south pending); facings judged by plate side (east render has the wall WEST -> in-game east = mirrored render); writing wire_bracket_art.py
- 14:16 T3 wired: Scrapper/Industrial/Futuristic per-facing Graphic_Multi + measured insulator table (BracketGeometryTable), Modern stand-in; st.9 +3 spare brackets (E/W/N); offline 7/7. Starting T4
- 14:18 T4: probe now reports wantsOn/needsPowerOverlay/connectParent per power thing (net cmd) to settle stale-vs-real live; DLL built
- 14:18 committed 6ebc84361; deploying (modern v2 south not landed yet)
- 14:19 modern v2 landed: wired (north/south renders swapped, plate side), DLL rebuilt, deployed; launching
- 14:19 launched
- 14:20 review map built (23 s), Industrial
- 14:22 live st.9 Industrial: wire ends on bracket insulator; E/W spares on walls ok; inside N spare made a T-branch -> moved outside south wall
- 14:22 live st.10 Industrial: each cut half ONE wire from middle insulator down to the break, halves meet at the spark; spans fan to outer insulators
- 14:24 T4 MEASURED: st.8 SECOND lamp mast powerOn=false + needsPowerOverlay=true on a live net (first one on): vanilla PowerNetTick turns consumers on one per 200/n ticks; build paused too early -> human_review steps 600 ticks before freezing (staging defect, not mod). Hose fixes: bare fittings (stub cut), aged wrap tint, open-end wrap to the cut
- 14:25 live 4 looks st.9/10: brackets on walls in each look, wire lands on insulator; fallen wire one piece in each look. Rebuilding with hose+staging fixes
