#!/usr/bin/env python3
"""Blind lane 1, cycle 5 (judge-1794890427): the Python half. Reads the shipped settings (RM_KnockbackMod.cs), the per-type
patch (Patches/RM_Knockback_DamageDefs.xml), the proof build gate (proof_build_gate.py) and the proof scenes' entry points
(RM_KnockbackProof*.cs against scenes.json), from the bars alone. One JSON row per line on stdout.
    python3 BlindLane1.py [--mod-root <dir>] [--scenes <scenes.json>]"""
import argparse, glob, importlib.util, io, json, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))


def row(id_, bars, kind, ok, cases, detail):
    v = "INFO" if ok is None else ("PASS" if ok else "FAIL")
    print(json.dumps({"id": id_, "bars": bars, "kind": kind, "verdict": v, "cases": cases, "detail": detail}))


def val(s):
    s = s.strip().rstrip("f")
    if s in ("true", "false"):
        return s == "true"
    return float(s)


def settings(mod):
    src = open(os.path.join(mod, "Source/RM_KnockbackMod.cs"), encoding="utf-8-sig").read()
    fields = {m.group(2): val(m.group(3)) for m in re.finditer(r"public static (bool|float|int) (\w+) = ([^;]+);", src)
              if m.group(2) not in ("Settings",)}
    # only the settings class (the extension's instance fields are not static)
    scribe = {m.group(1): val(m.group(2)) for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "\w+", ([^)]+)\);', src)}
    reset = {m.group(1): val(m.group(2)) for m in re.finditer(r"RimMandrakeExplosiveKnockbackSettings\.(\w+) = ([^;]+);", src)}
    keys = {m.group(1): m.group(2) for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', src)}
    sliders = {}
    for m in re.finditer(r"(\w+) = (?:\(int\))?(?:Mathf\.Round\()?(?:Mathf\.Max\(\w+, Mathf\.Round\()?list\.Slider\((\w+), ([\d.]+)f, ([\d.]+)f\)", src):
        sliders[m.group(2)] = (float(m.group(3)), float(m.group(4)))
    checkboxes = set(re.findall(r'CheckboxLabeled\("[^"]*", ref (\w+)', src))
    return src, fields, scribe, reset, keys, sliders, checkboxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod-root", default=os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback"))
    ap.add_argument("--scenes", default=os.path.join(REPO, "design/concepts/ExplosiveKnockback/scenes.json"))
    a = ap.parse_args()
    mod = a.mod_root

    # ---------- shipped settings: one default, saved under its own key, inside its slider, reset to it ----------
    src, fields, scribe, reset, keys, sliders, checkboxes = settings(mod)
    bad = []
    for k, v in fields.items():
        if k not in scribe:
            bad.append("%s not saved" % k)
        elif scribe[k] != v:
            bad.append("%s saved default %s != field %s" % (k, scribe[k], v))
        if k not in reset:
            bad.append("%s not reset" % k)
        elif reset[k] != v:
            bad.append("%s reset %s != field %s" % (k, reset[k], v))
        if k in keys and keys[k] != k:
            bad.append("%s saved under key %s" % (k, keys[k]))
    for k in scribe:
        if k not in fields:
            bad.append("saved %s has no field" % k)
    for k, (lo, hi) in sliders.items():
        if k in fields and not (lo <= fields[k] <= hi):
            bad.append("%s default %s outside slider %s-%s" % (k, fields[k], lo, hi))
    unshown = sorted(k for k in fields if k not in sliders and k not in checkboxes)
    row("S_SETTINGS_ONE_DEFAULT_EACH", ["inv_settings", "settings_scale_and_switch"], "fixed", not bad, len(fields) * 4,
        ("FAILED: " + "; ".join(bad[:8])) if bad else "%d settings: field default = saved default = Reset() value, own key, inside its slider; on the page as slider or checkbox: all but %s" % (len(fields), unshown))
    removed = [w for w in ("maxThrowsPerExplosion", "maxItemThrowsPerMapTick", "immuneBodySize") if re.search(r"\b%s\b" % w, src)]
    row("S_REMOVED_CAP_SETTINGS_GONE", ["settings_scale_and_switch", "every_good_moves", "inv_caps"], "fixed", not removed, 3,
        "the 40-throw cap, the per-tick drop and the body-size setting are absent from the settings file" if not removed else "still present: %s" % removed)
    # every new part has its own switch (the leaf's list)
    parts = {"goods in the air": "flyingGoods", "closed guard": "closedContainerGuard", "container shove": "shoveClosedContainers",
             "sealed crates counted closed": "vanillaCratesClosed", "heavy knock": "heavyGoodsKnock", "gas chain": "gasChain",
             "fire at half": "fireAtHalf", "blast power from damage": "blastPowerFromDamage", "master": "enabled"}
    miss = [p for p, f in parts.items() if f not in checkboxes or fields.get(f) is not True]
    row("S_EVERY_PART_HAS_A_SWITCH_ON_BY_DEFAULT", ["settings_scale_and_switch", "inv_settings"], "fixed", not miss, len(parts),
        "every part the leaf names has a checkbox, on by default: %s" % sorted(parts.values()) if not miss else "missing or off: %s" % miss)
    hr = sliders.get("heavyGoodsDamageMax")
    row("I_LANDING_STUN_MIN_MAX_INDEPENDENT", ["settings_scale_and_switch"], "info", None, 1,
        "landingStunMin and landingStunMax are two independent 0-300 sliders (the heavy damage max is clamped to its min, the stun max is not): lane 2 must read how the game side draws a stun when min > max")

    # ---------- per-type values ----------
    p = ET.parse(os.path.join(mod, "Patches/RM_Knockback_DamageDefs.xml"))
    tuned = {}
    for op in p.getroot().iter("Operation"):
        xp = op.findtext("xpath") or ""
        m = re.search(r'defName="(\w+)"', xp)
        f = op.find(".//force")
        if m and f is not None:
            tuned[m.group(1)] = float(f.text)
    want = {"Bomb": 1.0, "Flame": 0.5, "EMP": 0.0, "Smoke": 0.0, "Extinguish": 0.0, "ToxGas": 0.0}
    diff = {k: (tuned.get(k), v) for k, v in want.items() if tuned.get(k) != v}
    row("S_DAMAGE_TYPES_PATCHED_AS_RULED", ["every_harmful_blast_throws", "inv_which_blasts", "only_explosions_throw"], "fixed", not diff, len(want),
        "Bomb 1.0, Flame 0.5, EMP/Smoke/Extinguish/ToxGas 0 (Stun is harmsHealth false, never reached by the unpatched default): %s" % tuned if not diff else "differs (have, want): %s" % diff)
    extra = sorted(set(tuned) - set(want))
    row("I_OTHER_TUNED_TYPES", ["every_harmful_blast_throws"], "info", None, 1, "types tuned beyond the ruling: %s" % (extra or "none"))

    # ---------- proof build gate ----------
    spec = importlib.util.spec_from_file_location("pbg", os.path.join(mod, "proof_build_gate.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    cases, bad = 0, []
    rel = {"error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}
    for resp, want_rel in [(rel, True), ({"result": "STAGED calibration"}, False), ("Type not found: SomethingElse", False),
                           ({"result": "PASS RM_KnockbackProof calibration"}, False), (None, False), ({"e": ["Type not found", "RM_KnockbackProof"]}, True)]:
        cases += 1
        if g.is_release_answer(resp) != want_rel:
            bad.append("is_release_answer(%r) != %s" % (resp, want_rel))
    out = io.StringIO()
    cases += 1
    try:
        g.require_proof_build(rel, out=out)
        bad.append("release answer did not exit")
    except SystemExit as e:
        if e.code != 3:
            bad.append("exit %r not 3" % e.code)
        if "PROOF BUILD REQUIRED" not in out.getvalue() or "RmProofs=true" not in out.getvalue():
            bad.append("message lacks the rebuild command")
    cases += 1
    ok_resp = {"result": "STAGED calibration"}
    try:
        if g.require_proof_build(ok_resp) is not ok_resp:
            bad.append("a proof-build answer is not returned unchanged")
    except SystemExit:
        bad.append("a proof-build answer exited")
    row("P_PROOF_GATE_REFUSES_RELEASE", ["inv_proof_scenes"], "fixed", not bad, cases,
        "; ".join(bad) if bad else "a release DLL's 'Type not found ... RM_KnockbackProof' exits 3 with the rebuild command; any other answer passes through unchanged")

    # ---------- the proof scenes: every scenes.json entry point is a staged scene with a verdict ----------
    proof = ""
    for f in sorted(glob.glob(os.path.join(mod, "Source/RM_KnockbackProof*.cs"))):
        proof += open(f, encoding="utf-8-sig").read() + "\n"
    m = re.search(r"SceneNames\s*=\s*\{(.*?)\};", proof, re.S)
    names = re.findall(r'"(\w+)"', m.group(1)) if m else []
    cases_ = set(re.findall(r'case "(\w+)":', proof))
    sc = json.load(open(a.scenes))
    entries = []
    for group in ("scenes", "showcases", "coverage_rest"):
        for s in sc.get(group) or []:
            if isinstance(s, dict) and s.get("entry_point"):
                entries.append((s.get("id"), s["entry_point"]))
    eps, unknown = [], []
    for sid, ep in entries:
        path, _, name = str(ep).partition("::")
        eps.append((sid, name))
        if not os.path.exists(os.path.join(REPO, path)):
            unknown.append((sid, "missing file " + path))
        elif path.endswith("RM_KnockbackProof.cs") and name not in names:
            unknown.append((sid, name))
    nocase = sorted(n for n in names if n not in cases_)
    row("P_SCENE_ENTRY_POINTS_STAGED", ["inv_proof_scenes"], "fixed", not unknown and not nocase and bool(names), len(eps) + len(names),
        ("%d scenes.json entry-point tokens all in SceneNames (%d), each scene has a Build case" % (len(eps), len(names))) if not unknown and not nocase
        else "entry points not in SceneNames: %s; SceneNames without a case: %s" % (unknown[:12], nocase[:12]))
    dup = sorted({n for n in names if names.count(n) > 1})
    row("P_SCENE_NAMES_UNIQUE", ["inv_proof_scenes"], "fixed", not dup, len(names), "no scene name listed twice" if not dup else "listed twice: %s" % dup)
    # every staged scene sets a verdict and the verdict reads a recorded outcome (a scene with no verdict cannot fail)
    # consecutive case labels share one body (C# fall-through): group them
    labels = list(re.finditer(r'case "(\w+)":', proof))
    noverdict, i = [], 0
    while i < len(labels):
        group = [labels[i]]
        while i + 1 < len(labels) and re.sub(r"//[^\n]*", "", proof[labels[i].end():labels[i + 1].start()]).strip() in ("", "{"):
            i += 1
            group.append(labels[i])
        end = labels[i + 1].start() if i + 1 < len(labels) else len(proof)
        body = proof[group[-1].end():end]
        if not ("verdict" in body or re.search(r"return \w+\(s\)", body) or "return \"" in body):
            noverdict += [g.group(1) for g in group if g.group(1) in names]
        i += 1
    row("P_EVERY_SCENE_HAS_A_VERDICT", ["inv_proof_scenes"], "fixed", not noverdict, len(names),
        "every scene's Build case sets a verdict or hands off to a builder" if not noverdict else "no verdict: %s" % noverdict[:12])


main()
