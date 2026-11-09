"""Round 5: one wide crop of the research bench (r3_35 showed only its south edge). python.exe ralph/live/r5_bench.py"""
import os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import gss_stage as G  # noqa: E402
B = G.RL.LiveBridge()
B.call("jawa/clear_ui", all=True)
r = B.call("rimworld/screenshot_cell_rect", x=170, z=99, width=8, height=8, paddingCells=0,
           fileName="r5_bench_%s" % time.strftime("%H%M%S"), rootSize=5.0)
print("SHOT", r.get("filePath") or r.get("path"))
