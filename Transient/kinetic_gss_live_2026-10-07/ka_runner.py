"""Kinetic Arms live scenes (+ EK pit scenes) on the full list. Run under python.exe from the repo root.
Same Stage/step/Verdict protocol as ExplosiveKnockback/knockback_runner.py; KA's proof has no Clear/Journal."""
import datetime, json, os, re, sys
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint

KA = "RimMandrake.KineticArms.RM_KineticArmsProof"
EK = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"


def call(b, typ, method, arg):
    r = b.call("jawa/static_call", {"type": typ, "method": method, "args": arg}, check=False)
    if isinstance(r, dict):
        if r.get("success") is False:
            return "ERROR static_call %s" % json.dumps(r)[:300]
        return str(r.get("result", r.get("value", r)))
    return str(r)


def main():
    only = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] else None
    ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 90  # a throw lands in ~20 ticks; unarmed hostiles walk off after landing
    host, port, token = resolve_endpoint()
    out = os.path.join(REPO, "Transient", "kinetic_arms_live_2026-10-07")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "run_%s.jsonl" % datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
    rows = []
    with RimBridge(host=host, port=port, token=token, timeout=600.0) as b:
        plan = []
        ka_names = call(b, KA, "Names", "x")
        print("KA scenes:", ka_names)
        plan += [(KA, s) for s in ka_names.split(" ")[0].split(",") if s]
        ek_names = call(b, EK, "Names", "x")
        print("EK scenes:", ek_names)
        plan += [(EK, s) for s in ("pit_colonist", "pit_enemy") if s in ek_names]
        if only:
            plan = [p for p in plan if p[1] in only]
        n_ka = sum(1 for p in plan if p[0] == KA)
        n_ek = len(plan) - n_ka
        org = {KA: call(b, KA, "Origins", str(max(n_ka, 1))).split(";"), EK: call(b, EK, "Origins", str(max(n_ek, 1))).split(";")}
        print("origins", {k.split(".")[-1]: v[:3] for k, v in org.items()})
        call(b, KA, "Settings", "reset"); call(b, EK, "Settings", "reset"); call(b, EK, "Clear", "x")
        idx = {KA: 0, EK: 0}
        for typ, name in plan:
            o = org[typ][idx[typ] % len(org[typ])]; idx[typ] += 1
            call(b, EK, "Clear", "x")  # per scene, so a failing row carries only its own journal
            staged = call(b, typ, "Stage", "%s,%s" % (name, o))
            if not staged.startswith("STAGED"):
                st = staged.split(" ", 1)[0]
                rows.append({"proof": typ.split(".")[1], "scene": name, "status": st, "detail": staged, "origin": o})
                print("%-22s %s" % (name, staged[:240])); continue
            m = re.search(r"ticks=(\d+)", staged) if len(sys.argv) <= 2 else None  # scene's own budget unless forced
            b.call("rimworld/step_game_ticks", {"ticks": int(m.group(1)) if m else ticks}, check=False)
            v = call(b, typ, "Verdict", name)
            row = {"proof": typ.split(".")[1], "scene": name, "status": v.split(" ", 1)[0], "detail": v, "origin": o}
            if row["status"] != "PASS":
                row["journal"] = call(b, EK, "Journal", "40")
            rows.append(row)
            print("%-22s %s" % (name, v[:240]))
        call(b, KA, "Settings", "reset"); call(b, EK, "Settings", "reset")
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    from collections import Counter
    print("SUMMARY", dict(Counter(r["status"] for r in rows)), "->", path)


if __name__ == "__main__":
    main()
