# RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS

Save `FLOWWORKS_OWNER_REVIEW_20261115_1349_COVERED.rws` (Saves folder; 63 labelled stations, every one captured and looked
at: `design/concepts/FlowWorks/version/in_game/visit_1/screenshots/stations_1..4.jpg`). Four looks no bar decides; each
needs a judge's or his eye, and none was changed:
1. Gate rows (stations 7-16): a dry 1-notch canal (`RM_Channel_Empty`) draws as a light grey stone-lined strip that reads more
   like a low wall than a dug channel.
2. Shallows (stations 21, 22): 5 m of water reads a brighter, more saturated blue than 2 m.
3. bars_dry (stations 41-46): a colonist standing in a dry 0.5 m hole and in an 8 m hole draw alike at this zoom (state reads
   say the draw offset follows depth: plot_H_depth_ladder PASS).
4. Station 32 (bleed well): at sheet scale the hose end appears to stop a little short of the tap fitting; a closer capture
   is owed before calling it a gap.
Also seen: a small grey round thing on the floor of station 49's 2 m ladder pit; get_cells_info lists no Thing there
(it does not list pawns), so presumed a wild animal in the pit, unproven.
Caught and fixed before this save: the two "concealed pit" stations (54, 63) had one plank lid on the centre of a 3x3 pit, so
the pit showed plainly; `owner_review_stage.py` now lids every square.

Acceptance test: none, taste (a judge's or his verdict per question).
