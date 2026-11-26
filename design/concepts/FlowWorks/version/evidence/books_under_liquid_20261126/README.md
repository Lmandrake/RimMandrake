# Books and minified goods under liquid, ArchBig, 2026-11-26

RIMMANDRAKE_COVER_BOOKS_UNDER_LIQUID_NOVEL_READS_THROUGH_TAR (fix 142a6d77b3: a book is drawn realtime, so the
realtime gate hides it). Three 3x3 pits dug 3 m on ArchBig's test map (FlowWorks on its 26-mod list): left 1.5 m of tar
poured with RM_GodLiquid.Pour (paused at once, so the tar stands as a plus before it levels), middle dry, right 1.5 m of
water. A Novel in each pit's centre; 30 steel in each top-left corner.

`books_minified_control.png` (jawa/artboard_capture, 64 px a square):
- the Novel: crisp when dry, faded under water, not drawn under tar (list_things reads the Novel at 121,121);
- a minified armchair and end table on tar squares (122,121 and 121,120): not drawn;
- the control, a minified armchair on the tar pit's dry corner (122,122): drawn crisp, so the render is live.
