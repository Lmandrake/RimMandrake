"""Offline checks for modern_fittings_live.py (MODERN_FITTINGS_PROBE_FAUCET_NEVER_SEEN). No bridge, no game.
The whole script runs against FakeBridge, a toy map that models only what the rows read (each thing's drawn path from its
style, MatchPipeUnder copying the pipe's look onto a new head, the span strung by ProofLinkPoles, a screenshot file).
The Modern scene must exit 0; a head whose look-match is broken (Modern only after an explicit style) FAILS; a pipe or pole
that never took its Modern style is a staging fault (UNMEASURED, never a head/span FAIL); an unstrung span and a screenshot with no file must each NOT exit 0.
The candidates must be swapped in: the overlay mod (ModernFittingsCandidates) not running, loaded before FlowWorks, or running
with bytes that are not cand_r3's each makes CANDIDATES_SWAPPED_IN FAIL and the run exit 1. Also checks the overlay mod in the
repo carries exactly the candidate bytes at the Modern texPaths and loads after FlowWorks, and the
files the rows promise exist in the repo: the Modern faucet, sprinkler and PipeSpan textures, the four StyleDefs, the
spanTexPath contract, and the C# methods the script calls."""
import os
import hashlib
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modern_fittings_live as M  # noqa: E402

FW = os.path.normpath(os.path.join(HERE, ".."))
fails = []


def check(name, ok, got=""):
    print("%-4s  %-66s %s" % ("ok" if ok else "FAIL", name, str(got)[:160]))
    if not ok:
        fails.append(name)


LOOKS = {"RM_UniversalPipe": "UniversalPipe/{look}/UniversalPipe_Atlas", "RM_PipeFaucet": "Faucet/{look}/RM_PipeFaucet",
         "RM_SprinklerHead": "Sprinkler/{look}/RM_SprinklerHead", "RM_PipePole": "PipePole/{look}/PipePole"}


class FakeV:
    @staticmethod
    def _wait_playing(B, leave_s=0):
        return True, {}

    @staticmethod
    def site_calm(B):
        return {"calm": True}

    @staticmethod
    def prepare_site(B, rect, rows, rid):
        rows.append({"id": rid, "status": "PASS"})


class FakeBridge:
    FAULTS = ("no_overlay", "overlay_first", "overlay_stale", "pipe_unstyled", "pole_unstyled", "no_match", "unstrung", "no_shot", "uniform_shot")

    def __init__(self, faults, tmp):
        self.f, self.tmp, self.things, self.n, self.strung = set(faults), tmp, {}, 0, False

    def _rect(self, s):
        x, z, w, h = (int(v) for v in s.split(","))
        return x, z, w, h

    def _style_look(self, t):
        return (t.get("style") or "_Scrapper").rsplit("_", 1)[1]

    def call(self, tool, **k):
        k.pop("_answer", None)
        if tool == "jawa/running_mods":
            folder = os.path.join(self.tmp, "Mods", "ModernFittingsCandidates")
            for tex, cand in M.CANDIDATES.items():
                dst = os.path.join(folder, "Textures", *(M.TEX + tex + ".png").split("/"))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                src = os.path.join(FW, "Textures", *(M.TEX + tex + ".png").split("/")) if "overlay_stale" in self.f \
                    else os.path.join(M.CAND_DIR, cand)
                shutil.copyfile(src, dst)
            mods = [{"loadOrder": 0, "packageId": "Ludeon.RimWorld", "folder": "x"},
                    {"loadOrder": 6, "packageId": "mandrake.rm.flowworks", "folder": "y"}]
            if "no_overlay" not in self.f:
                mods.append({"loadOrder": 3 if "overlay_first" in self.f else 8, "packageId": M.OVERLAY, "folder": folder})
            return {"success": True, "mods": mods, "packageIds": [m["packageId"] for m in mods]}
        if tool == "jawa/build_batch":
            for op in k["ops"].split(";"):
                d, c = op.split(":")
                x, z = (int(v) for v in c.split(","))
                self.n += 1
                t = {"id": "Thing_%s%d" % (d, self.n), "def": d, "cell": (x, z), "style": None}
                if d in M.HEADS and "no_match" not in self.f:       # SpawnSetup: RM_SprinklerLook.MatchPipeUnder
                    pipe = next((p for p in self.things.values() if p["def"] == "RM_UniversalPipe" and p["cell"] == (x, z)), None)
                    if pipe and pipe["style"]:
                        t["style"] = d + "_" + self._style_look(pipe)
                self.things[t["id"]] = t
            return {"success": True}
        if tool == "jawa/set_thing_props":
            t = self.things.get(k["thing"])
            if t is None:
                return {"success": False}
            if not (t["def"] == "RM_UniversalPipe" and "pipe_unstyled" in self.f
                    or t["def"] == "RM_PipePole" and "pole_unstyled" in self.f):
                t["style"] = k["style"]
            return {"success": True, "styleDefAfter": t["style"]}
        if tool == "jawa/thing_graphic":
            x, z, w, h = self._rect(k["rect"])
            want = set(k["defs"].split(","))
            rows = [{"id": t["id"], "defName": t["def"], "cell": list(t["cell"]), "badTex": False,
                     "resolvedPath": M.TEX + LOOKS[t["def"]].format(look=self._style_look(t))}
                    for t in self.things.values()
                    if t["def"] in want and x <= t["cell"][0] < x + w and z <= t["cell"][1] < z + h]
            return {"success": True, "things": rows, "isCompleteList": True}
        if tool == "jawa/static_call" and k.get("method") == "ProofLinkPoles":
            self.strung = "unstrung" not in self.f
            return {"success": True, "result": "LINK verdict=Ok strung=%s spans=%d" % (self.strung, int(self.strung))}
        if tool == "rimworld/screenshot_cell_rect":
            if "no_shot" in self.f:
                return {"success": True, "path": os.path.join(self.tmp, "missing.png")}
            from PIL import Image
            im = Image.new("RGB", (40, 20), (90, 70, 50))
            if "uniform_shot" not in self.f:
                im.putpixel((5, 5), (250, 250, 250))
            p = os.path.join(self.tmp, k["fileName"] + ".png")
            im.save(p)
            return {"success": True, "path": p}
        return {"success": True}


class A:
    origin, fresh_map = "140,140", False


def scenario(faults):
    with tempfile.TemporaryDirectory() as tmp:
        a = A()
        a.out_dir = os.path.join(tmp, "out")
        B = FakeBridge(faults, tmp)
        code = M.run(B, FakeV, a)
        import json
        res = json.load(open(next(os.path.join(a.out_dir, f) for f in os.listdir(a.out_dir) if f.startswith("result_"))))
        man = os.path.isfile(os.path.join(a.out_dir, "captures.json"))
        return code, {r["id"]: r["status"] for r in res["rows"]}, man


code, rows, man = scenario([])
check("Modern scene: exit 0", code == 0, (code, rows))
check("Modern scene: five rows, all PASS", sorted(rows) == sorted(["CANDIDATES_SWAPPED_IN", "FAUCET_DRAWS_MODERN", "SPRINKLER_DRAWS_MODERN",
      "SPAN_STRUNG_MODERN", "CAPTURE_WRITTEN"]) and set(rows.values()) == {"PASS"}, rows)
check("Modern scene: captures.json written for the art pipeline", man)
for fault, what in (("no_overlay", "candidate overlay not in the running load"),
                    ("overlay_first", "candidate overlay loaded BEFORE FlowWorks (FlowWorks' art wins)"),
                    ("overlay_stale", "running overlay holds the installed art, not the candidates")):
    code, rows, _ = scenario([fault])
    check("%s: CANDIDATES FAIL, exit 1" % what, code == 1 and rows.get("CANDIDATES_SWAPPED_IN") == "FAIL", (code, rows))
code, rows, _ = scenario(["pipe_unstyled"])
check("pipe that never took the Modern style: staging UNMEASURED (2), not a head FAIL", code == 2
      and rows.get("FAUCET_DRAWS_MODERN") == "UNMEASURED", (code, rows))
code, rows, _ = scenario(["pole_unstyled"])
check("pole that never took the Modern style: SPAN UNMEASURED (2)", code == 2 and rows.get("SPAN_STRUNG_MODERN") == "UNMEASURED", (code, rows))
code, rows, _ = scenario(["no_match"])
check("look-match broken (Modern only by explicit style): head rows FAIL", code == 1
      and rows.get("FAUCET_DRAWS_MODERN") == "FAIL" == rows.get("SPRINKLER_DRAWS_MODERN"), (code, rows))
code, rows, _ = scenario(["unstrung"])
check("no span between the poles: SPAN FAIL, exit 1", code == 1 and rows.get("SPAN_STRUNG_MODERN") == "FAIL", (code, rows))
code, rows, _ = scenario(["no_shot"])
check("screenshot with no file: CAPTURE not PASS, exit not 0", code != 0 and rows.get("CAPTURE_WRITTEN") == "UNMEASURED", (code, rows))
code, rows, _ = scenario(["uniform_shot"])
check("uniform (blank) screenshot: CAPTURE not PASS", code != 0 and rows.get("CAPTURE_WRITTEN") == "UNMEASURED", (code, rows))
check("v_head: no row is UNMEASURED, never PASS", M.v_head("RM_PipeFaucet", None, True)[0] == "UNMEASURED")
check("v_head: BadTex FAILS", M.v_head("RM_PipeFaucet", {"badTex": True, "resolvedPath": M.WANT["RM_PipeFaucet"]}, True)[0] == "FAIL")
check("local(): a Windows screenshot path opens from WSL", M.local(r"D:\a\b.png") == "/mnt/d/a/b.png" or os.name == "nt")

# the files the rows promise
TEXD = os.path.join(FW, "Textures")
for p in (M.WANT["RM_PipeFaucet"], M.WANT["RM_SprinklerHead"], M.SPAN_TEX, M.POLE_MODERN + "PipePole"):
    check("installed texture %s.png" % p, os.path.isfile(os.path.join(TEXD, p + ".png")))
# the candidates are swapped in by the overlay mod: its bytes ARE cand_r3, they differ from the installed art, it loads after FW
OVL = os.path.normpath(os.path.join(FW, "..", "ModernFittingsCandidates"))
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None  # noqa: E731
for tex, cand in M.CANDIDATES.items():
    rel = (M.TEX + tex + ".png").split("/")
    c, o, i = h(os.path.join(M.CAND_DIR, cand)), h(os.path.join(OVL, "Textures", *rel)), h(os.path.join(TEXD, *rel))
    check("overlay %s is the candidate %s" % (tex, cand), c is not None and o == c, (c and c[:10], o and o[:10]))
    check("candidate %s differs from the installed art (a swap is visible)" % cand, c is not None and c != i)
ovl_tex = sorted(os.path.relpath(os.path.join(r, f), os.path.join(OVL, "Textures")).replace(os.sep, "/")
                 for r, _, fs in os.walk(os.path.join(OVL, "Textures")) for f in fs)
check("overlay carries only the three candidates", ovl_tex == sorted(M.TEX + t + ".png" for t in M.CANDIDATES), ovl_tex)
about = open(os.path.join(OVL, "About", "About.xml"), encoding="utf-8").read() if os.path.isfile(os.path.join(OVL, "About", "About.xml")) else ""
check("overlay About: packageId %s, loadAfter FlowWorks" % M.OVERLAY, "<packageId>%s</packageId>" % M.OVERLAY in about
      and re.search(r"<loadAfter>.*<li>%s</li>.*</loadAfter>" % re.escape(M.FLOWWORKS), about, re.S) is not None)
proofs = os.path.join(M.REPO, "infrastructure", "state", "live_proofs", M.ITEM + ".txt")
lm = [l for l in open(proofs, encoding="utf-8").read().splitlines() if l.startswith("live-mods:")]
check("live_proofs live-mods loads the overlay", bool(lm) and "ModernFittingsCandidates" in lm[0], lm)
# GAMEENV_FIX_PROOFSITE_87D091F9_ITEMS_WAIT: the proof met the main menu; its site line stages a quicktest map first
SITE = "live-site A1: python.exe src/RimMandrake/Utils/live_site.py --game"
check("live_proofs holds the --game site line", SITE in open(proofs, encoding="utf-8").read().splitlines())
sys.path.insert(0, os.path.join(M.REPO, "src", "RimMandrake", "rimflow"))
import relentless_live  # noqa: E402
check("the lane accepts that site command", relentless_live.refused_site(SITE.split(": ", 1)[1]) is None)

defs = ""
for root, _, files in os.walk(os.path.join(FW, "Defs")):
    for f in files:
        if f.endswith(".xml"):
            defs += open(os.path.join(root, f), encoding="utf-8").read()
for sd in M.STYLE.values():
    check("ThingStyleDef %s exists" % sd, "<defName>%s</defName>" % sd in defs)
check("RM_PipePoles.xml spanTexPath is PipePole/{look}/PipeSpan",
      "<spanTexPath>RimMandrake/FlowWorks/PipePole/{look}/PipeSpan</spanTexPath>" in defs)
src = ""
for root, _, files in os.walk(os.path.join(FW, "Source")):
    for f in files:
        if f.endswith(".cs"):
            src += open(os.path.join(root, f), encoding="utf-8").read()
check("RM_LineProofs.ProofLinkPoles exists", re.search(r"public static string ProofLinkPoles\(string", src) is not None)
check("heads print their own Graphic (RM_PipeSeat.Print: onPipe.Graphic)", "Graphic g = onPipe.Graphic;" in src)
check("faucet SpawnSetup calls MatchPipeUnder", "RM_SprinklerLook.MatchPipeUnder(this)" in src)

print("\n%d FAIL" % len(fails) if fails else "\nALL OK")
sys.exit(1 if fails else 0)
