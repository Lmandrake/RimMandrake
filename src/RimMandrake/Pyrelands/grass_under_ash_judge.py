"""The blind judge's half of sc_grass_seen_under_ash (grass_under_ash_live.py writes the manifest).

  prepare <manifest>          per pair: copies G's and B's captures to blind_<regime>/A.png and B.png in a random order,
                              and writes the order to key_<regime>.json beside the manifest (never inside the blind folder).
                              Prints the judge's question. A fresh rm-judge (opus) is shown only the blind folder.
  score <manifest> <regime> <answer.json>
                              answer.json: {"grass_image": "A"|"B"|"both"|"neither", "A_grass": true|false,
                              "B_grass": true|false, "why": "..."}. Prints each check (worst value, limit, cases) and the
                              pair's verdict: PASS when the judge picks G and reads grass in G and none in B.
Exit 0 PASS, 1 FAIL, 2 unusable input.
"""
import json
import os
import random
import shutil
import sys

QUESTION = ("Two captures of a RimWorld map, A and B, each a patch of open ground after an ash fall. Look at each image. "
            "1) Does image A show standing grass (blades or tufts of plants), yes or no? 2) Does image B? 3) Which image "
            "shows standing grass: A, B, both or neither? Answer as JSON: {\"A_grass\": true|false, \"B_grass\": "
            "true|false, \"grass_image\": \"A\"|\"B\"|\"both\"|\"neither\", \"why\": \"<one line per image>\"}")


def wsl_path(p):
    """D:\\x\\y -> /mnt/d/x/y off Windows; other paths as given."""
    if os.name != "nt" and isinstance(p, str) and len(p) > 2 and p[1] == ":":
        return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    return p


def load(manifest):
    with open(manifest, encoding="utf-8") as f:
        return json.load(f)


def prepare(manifest, rng=None):
    rng = rng or random.SystemRandom()
    m = load(manifest)
    base = os.path.dirname(os.path.abspath(manifest))
    out = []
    for pair in m.get("pairs") or []:
        reg = pair["regime"]
        g, b = wsl_path(pair.get("shotG")), wsl_path(pair.get("shotB"))
        if not g or not b or not os.path.isfile(g) or not os.path.isfile(b):
            print("prepare %s: capture missing (%r, %r)" % (reg, g, b))
            continue
        g_letter = rng.choice("AB")
        blind = os.path.join(base, "blind_%s" % reg)
        os.makedirs(blind, exist_ok=True)
        shutil.copyfile(g, os.path.join(blind, "%s.png" % g_letter))
        shutil.copyfile(b, os.path.join(blind, "%s.png" % ("B" if g_letter == "A" else "A")))
        with open(os.path.join(base, "key_%s.json" % reg), "w", encoding="utf-8") as f:
            json.dump({"regime": reg, "G": g_letter, "valid": pair.get("valid")}, f)
        out.append((reg, blind, pair.get("valid")))
        print("prepare %s: %s (valid opportunity %r)" % (reg, blind, pair.get("valid")))
    print("QUESTION: " + QUESTION)
    return out


def verdict(answer, g_letter):
    """Pure. (the judge's answer, the letter G was copied to) -> (ok, rows). ok None is an unusable answer."""
    b_letter = "B" if g_letter == "A" else "A"
    try:
        pick = str(answer["grass_image"]).strip()
        g_grass = bool(answer["%s_grass" % g_letter])
        b_grass = bool(answer["%s_grass" % b_letter])
    except (KeyError, TypeError):
        return None, [{"check": "answer readable", "ok": False, "worst": repr(answer)[:120], "limit": "the JSON asked",
                       "cases": 1}]
    rows = [{"check": "the judge picks G as the frame with grass", "ok": pick == g_letter, "worst": pick,
             "limit": g_letter, "cases": 1},
            {"check": "grass read in G (else: grass hidden under the ash)", "ok": g_grass, "worst": g_grass,
             "limit": True, "cases": 1},
            {"check": "no grass read in B (else: grass drawn where the list shows none)", "ok": not b_grass,
             "worst": b_grass, "limit": False, "cases": 1}]
    return all(r["ok"] for r in rows), rows


def score(manifest, regime, answer_path):
    base = os.path.dirname(os.path.abspath(manifest))
    with open(os.path.join(base, "key_%s.json" % regime), encoding="utf-8") as f:
        key = json.load(f)
    with open(answer_path, encoding="utf-8") as f:
        answer = json.load(f)
    ok, rows = verdict(answer, key["G"])
    for r in rows:
        print("[gsua-judge] %s: %s: %s worst=%r limit=%r cases=%d" % (regime, r["check"], "ok" if r["ok"] else "NOT",
                                                                      r["worst"], r["limit"], r["cases"]))
    v = "UNUSABLE" if ok is None else ("PASS" if ok else "FAIL")
    if key.get("valid") is not True and ok is not None:
        v = "UNMEASURED (no valid opportunity; the judge read %s)" % ("PASS" if ok else "FAIL")
    print("[gsua-judge] %s verdict: %s (G was %s)" % (regime, v, key["G"]))
    return 2 if ok is None else (0 if ok else 1)


def main(argv):
    if len(argv) >= 2 and argv[0] == "prepare":
        prepare(argv[1])
        return 0
    if len(argv) >= 4 and argv[0] == "score":
        return score(argv[1], argv[2], argv[3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
