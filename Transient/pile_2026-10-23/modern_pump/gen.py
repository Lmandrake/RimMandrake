#!/usr/bin/env python3
"""MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY: raw Codex renders of Modern pump + sprinkler options (drafts only;
they replace art the owner kept, so nothing installs before his pick). Brief: design/RimMandrake/flowworks_modern_art_brief.md
Raws -> D:\\ClaudeWork\\rimmandrake\\modern_pump\\raw.   python3 gen.py <key> [<key>...]   (keys below)"""
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/mandrake/rm/foundry")
RAW = Path("/mnt/d/ClaudeWork/rimmandrake/modern_pump/raw")
TOOL = REPO / "skills/generating-images/scripts/codex_image.py"
LIVE_PUMP = REPO / "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Machinery/RM_LiquidPump.png"
LIVE_SPR = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Sprinkler/Industrial/RM_SprinklerHead.png"

TOPCAM = ("Seen from DIRECTLY ABOVE (pure top-down orthographic plan view), light from the top-left. Bold, simple shapes "
          "with a thin dark outline and strong value contrast so it still reads when shrunk to 48 pixels. Crisp painterly "
          "RimWorld-mod sprite style. One object only, centred, on a fully transparent background (real alpha), no ground "
          "shadow, no scenery, no text, no logo.")
PUMP_LAYOUT = ("The attached image shows ONLY the LAYOUT to keep: a compact pump body in the centre of a square canvas with "
               "four short pipe ports pointing exactly left, right, up and down, each port ending at the same distance from "
               "the centre as in the attached image and as wide as in the attached image. Keep that layout and footprint, "
               "but REDRAW THE OBJECT COMPLETELY as a real modern product - a different shape and material, not a recolour. ")
SPR_LAYOUT = ("The attached image shows ONLY the LAYOUT to keep: a sprinkler head standing on a short riser whose foot is a "
              "saddle clamp sitting on a horizontal pipe, drawn from a high three-quarter camera (about 35 degrees above "
              "horizontal, round parts are ellipses about half as tall as wide, top faces visible). Keep the same size, "
              "camera and foot clamp position, but REDRAW THE HEAD COMPLETELY as a real modern irrigation product - a "
              "different shape and material, not a recolour. ")
JOBS = {
    "pumpA": (LIVE_PUMP, PUMP_LAYOUT +
              "A modern thermoplastic utility / shallow-well jet pump seen from above: a round charcoal-black composite "
              "motor housing with a ribbed fan cowl and a small square pressure-switch box, sitting on a moulded light-grey "
              "glass-filled-plastic pump body with soft rounded edges; the four ports are grey PVC pipe stubs each with a "
              "chunky hexagonal true-union nut (moulded plastic, no bolted flanges, no rivets). Satin plastic sheen, "
              "colours charcoal, light grey and a little brass on one drain plug. " + TOPCAM),
    "pumpB": (LIVE_PUMP, PUMP_LAYOUT +
              "A modern pool / booster pump seen from above: a dark slate-grey moulded thermoplastic housing, in its centre "
              "a large round CLEAR polycarbonate strainer lid with a black screw ring, the white mesh strainer basket visible "
              "through it; the four ports are white PVC pipe stubs with grey true-union nuts. Rounded rotomoulded forms, "
              "soft satin sheen, no rivets, no bolts, no rust. A small rectangular label patch with no readable text. " + TOPCAM),
    "pumpC": (LIVE_PUMP, PUMP_LAYOUT +
              "A modern brushed stainless-steel booster pump seen from above: a round satin stainless pump casing with a "
              "flat dark-blue powder-coated motor end-cap and a small round pressure gauge, on a compact stainless base; the "
              "four ports are polished stainless pipe stubs each ending in a sanitary tri-clamp ferrule with a slim hinged "
              "clamp ring (no bolted flanges). Clean machined surfaces, a few crisp highlights, no rust. " + TOPCAM),
    "sprA": (LIVE_SPR, SPR_LAYOUT +
             "A modern black plastic pop-up gear-drive rotor sprinkler (like a Rain Bird or Hunter rotor): a round black "
             "moulded body with a dark-green rubber cover cap and a small nozzle turret, on a short grey PVC riser with a "
             "grey moulded saddle clamp on the pipe. Satin plastic, no rust, no rivets. " +
             "Crisp painterly RimWorld-mod sprite style, thin dark outline, centred, on a fully transparent background, "
             "no ground shadow, no scenery, no text."),
    "sprB": (LIVE_SPR, SPR_LAYOUT +
             "A modern impact sprinkler (brass-and-black 'rain bird' impact head): a compact brass body with a black "
             "spring-loaded swinging arm and a long nozzle tube pointing out to one side, on a short black poly riser "
             "with a black moulded saddle clamp on the pipe. Clean modern finish, no rust. " +
             "Crisp painterly RimWorld-mod sprite style, thin dark outline, centred, on a fully transparent background, "
             "no ground shadow, no scenery, no text."),
    "sprC": (LIVE_SPR, SPR_LAYOUT +
             "A modern farm micro-sprinkler / rotating spinner head on a stake riser: a small light-blue and white "
             "injection-moulded plastic spinner cap with a clear dome deflector, on a slim black poly riser tube with a "
             "light-grey moulded saddle clamp on the pipe. Satin plastic, no rust, no metal bolts. " +
             "Crisp painterly RimWorld-mod sprite style, thin dark outline, centred, on a fully transparent background, "
             "no ground shadow, no scenery, no text."),
}

# v2 redraws after the outside judge (judge_v1.json): B read as a basket strainer (M1), C showed a bolted cap (M2)
FIX = {
    "pumpB2": (RAW / "pumpB.png",
               "Edit this top-down pump sprite. Keep the four white PVC ports with grey union nuts exactly where they are, "
               "the canvas, the plan-view camera and the slate-grey moulded thermoplastic housing. Change the centre: make it "
               "read clearly as a PUMP, not a strainer - shrink the clear strainer lid to a small round window near the top "
               "edge of the housing, and give the middle of the housing a big round dark-grey ribbed MOTOR cowl with cooling "
               "fins and a small rectangular grey pressure-switch box with a little dial beside it. Smooth rotomoulded plastic, "
               "no bolts, no rivets. Fully transparent background, no ground shadow. " + TOPCAM),
    "pumpC2": (RAW / "pumpC.png",
               "Edit this top-down pump sprite. Keep the four stainless ports with tri-clamp ferrules and hinged clamp rings "
               "exactly where they are, the brushed stainless round casing, the gauge, the canvas and the plan-view camera. "
               "Replace the bolted blue cover in the middle with a SMOOTH seamless dark-blue powder-coated motor housing: a "
               "round domed motor with fine cooling fins radiating out and a flush fan grille, NO bolt heads, NO screws, no "
               "rivets anywhere. Fully transparent background, no ground shadow. " + TOPCAM),
}
JOBS.update(FIX)

if __name__ == "__main__":
    for i, key in enumerate(sys.argv[1:]):
        ref, prompt = JOBS[key]
        home = Path(f"/mnt/d/ClaudeWork/rimmandrake/modern_pump/codex_{key}")
        cmd = [sys.executable, str(TOOL), "edit", "--image", str(ref), "--prompt", prompt,
               "--out", str(RAW / f"{key}.png"), "--codex-home", str(home), "--timeout", "900", "--force"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(key, r.returncode, (r.stdout + r.stderr).strip().splitlines()[-3:])
