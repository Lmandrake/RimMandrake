# MessyConduit human-review build log 2026-10-04

- 12:11 start: skeleton
- 12:14 label tool written (JawaBenchReviewLabels.cs), building
- 12:14 companion deployed + game relaunched
- 12:16 layout designed; writing human_review.py
- 12:19 human_review.py --plan: layout ok, keysheet written
- 12:19:33 fresh quicktest map
- 12:19:45 calm world set (peaceful=True, pawns in region [])
- 12:19:52 region cleared
- 12:19:56 built: {'Granite/None': '15/15', 'Wall/player': '26/26', 'PowerConduit/hostile': '2/2', 'PowerConduit/player': '84/84', 'Battery/hostile': '1/1', 'Battery/player': '13/13', 'WoodFiredGenerator/player': '1/1', 'PowerSwitch/player': '1/1', 'SolarGenerator/player': '2/2', 'RM_AerialMast/player': '8/8', 'RM_AerialLampMast/player': '2/2', 'RM_AerialWallBracket/player': '1/1', 'RM_HoseReel/player': '4/4', 'Heater/player': '6/6', 'RM_PowerTapClamp/player': '1/1', 'StandingLamp/player': '13/13'}
- 12:20:03 stations built; hose states {12: {'state': 'Flat', 'blend': 0, 'couplings': 3, 'pathLen': 15.55}, 13: {'state': 'Filling', 'blend': 0.4667, 'couplings': 4, 'pathLen': 15.55}, 14: {'state': 'Plump', 'blend': 1, 'couplings': 3, 'pathLen': 15.55}, 15: {'state': 'Plump', 'blend': 1, 'couplings': 5, 'pathLen': 25.8661}}
- 12:20:03 labels: added 21, refused []
- 12:20:03 DONE in 30.2s; notes: none
- 12:20 live build DONE 30 s, notes none; screenshot pass
- 12:21 labels legible at stations 4, 9, 10 (OS shots review_4/10.bmp); short subs added
- 12:21 live map final (labels re-pinned, camera on station 1); docs next
- 12:24 docs written (northstar_human_review.md, debug_process §6b/6c, walk ## extended); status.py excludes human_review.py (hash stays 49214331977a, GREEN); committing
- 12:24 published bb00640ee (label tool)
