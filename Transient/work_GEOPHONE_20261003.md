# GEOPHONE work 2026-10-03
- claimed+started STILLSAND_GEOPHONE_1.
- Query reused: RM_CompSandSwim.Submerged (public, CreatureBehaviors) + RM_WeatherSenseExtension.On(map).drownsRumble (gale drowns the rumble, geophone hears nothing either).
- Drazzik's lie: RM_CompDrumLure pawns (hidden lurers) are read as a rumble the same way, no flag distinguishing them (CreatureBehaviors gates: drumLureEnabled).
- Marker: 8-way compass bearing + size class from BodySize (small <1, medium <2.5, large). No distance, no species. Shown as inspect lines and, while selected, a drawn line along the rounded bearing (length by class); a message on a new reading, rate-limited.
- Building RM_Geophone 1x1, no power, radius 20 default (setting 8-40). Settings on RM_GlassChainSettings: geophoneEnabled, geophoneRadius.
- Art: artpipe done RM_Geophone.png in _artsrc; reuse into Textures/Things/Building/Production/. No new jobs.
