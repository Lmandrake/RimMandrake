"""fwb.py -- the Artisan loop's own small bridge helper for game A on SteveDesktop (run with python.exe from the repo root).

  python.exe ralph/live/fwb.py tools [filter]          list tool names (and the schema of each one matching filter)
  python.exe ralph/live/fwb.py call <tool> '<json>'    one call, reply printed as JSON
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
NS = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "northstar")
for _p in (UTILS, NS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import validation_core as V  # noqa: E402

OUT = os.path.join(REPO, "Transient", "ralph_fw")


class FW(V.Bridge):
    def tools(self):
        r = self.S.request("tools/list", {}) if hasattr(self.S, "request") else None
        return r

    def step(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    def shot(self, name, x, z, w, h, root=None, pad=1):
        """A unique-named screenshot of a cell rect. Returns the repo-relative png path the game wrote (on Steve)."""
        kw = dict(x=x, z=z, width=w, height=h, fileName="%s_%s" % (name, time.strftime("%H%M%S")))
        if root:
            kw["rootSize"] = root
        if pad is not None:
            kw["paddingCells"] = pad
        self.call("jawa/clear_ui", all=True)
        r = self.call("rimworld/screenshot_cell_rect", **kw) or {}
        return r


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    B = FW()
    if sys.argv[1] == "tools":
        flt = sys.argv[2] if len(sys.argv) > 2 else None
        r = B.S.list_tools() if hasattr(B.S, "list_tools") else B.tools()
        tl = r.get("tools") if isinstance(r, dict) else r
        for t in tl or []:
            n = t.get("name") if isinstance(t, dict) else str(t)
            if flt and flt not in n:
                continue
            if flt:
                print(n, json.dumps(t.get("inputSchema") or t.get("parameters") or {}, default=str)[:1500])
                print("   ", (t.get("description") or "")[:600])
            else:
                print(n)
    elif sys.argv[1] == "shot":   # shot <name> x z w h [rootSize]
        a = sys.argv[2:]
        r = B.shot(a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4]), root=float(a[5]) if len(a) > 5 else None)
        print(json.dumps({k: r.get(k) for k in ("success", "filePath", "path", "imagePath", "width", "height", "message")
                          if k in r} or r, default=str)[:3000])
    elif sys.argv[1] == "call":
        kw = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(B.call(sys.argv[2], **kw), indent=1, default=str)[:20000])


if __name__ == "__main__":
    main()
