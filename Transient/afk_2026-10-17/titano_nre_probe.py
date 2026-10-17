"""Which step starts the BreadthFirstTraverse NRE flood? python.exe, after a fresh map."""
import sys, os, json, time, re
sys.path.insert(0, os.path.join("src","RimMandrake","GelatinousSlime","northstar"))
import titanoslime_gates as T
LOG = os.path.join(os.environ["USERPROFILE"], "AppData","LocalLow","Ludeon Studios","RimWorld by Ludeon Studios","Player.log")
def n():
    return sum(1 for l in open(LOG, encoding="utf-8", errors="replace") if "Exception in BreadthFirstTraverse" in l or "Root level exception" in l)
g = T.G(); S = {}
T.preflight(g, S, True)
steps = sys.argv[1].split(",") if len(sys.argv) > 1 else ["base","spawn","mass12","saveload"]
x, z = S["cx"] + int(time.time()) % 40 - 20, S["cz"] + 30
pid = None
for st in steps:
    if st == "spawn":
        pid = g.spawn(T.KIND, x, z)[0]; g.proof("ProofSetMass", pid, 0)
    elif st == "mass4":
        g.proof("ProofSetMass", pid, 4)
    elif st == "mass12":
        g.proof("ProofSetMass", pid, 12)
    elif st == "mass28":
        g.proof("ProofSetMass", pid, 28)
    elif st == "fightuntil":
        for rep in range(4):
            xx = x - 40 + rep * 25
            sl = g.spawn(T.KIND, xx, z)[0]; g.proof("ProofSetMass", sl, 0)
            cols = g.spawn("Colonist", xx + 1, z, faction="player", count=4)
            for c in cols: g.call("jawa/set_draft", pawnId=c, drafted=True, fireAtWill=True)
            g.call("jawa/damage", damageDef="Blunt", amount=2, thingId=sl, instigatorId=cols[0])
            done = False
            for k in range(30):
                a0 = n(); g.ticks(120); b0 = n()
                r = g.read(sl)
                if int(r.get("held", 0)) > 0:
                    print("rep %d swallow at %d; NRE during that step +%d" % (rep, (k + 1) * 120, b0 - a0)); done = True; break
                if r.get("downed") == "True": print("rep %d downed" % rep); break
            if done: pid = sl; break
    elif st == "absorb":
        c = g.spawn("Colonist", x + 2, z, faction="player")[0]
        print(g.proof("ProofEngulf", pid, c)[:40])
        for k in range(45):
            a0 = n(); g.ticks(120); b0 = n()
            r = g.read(pid)
            if int(r.get("held", 0)) == 0:
                print("held cleared at %d; NRE that step +%d; victim %s" % ((k + 1) * 120, b0 - a0, g.proof("ProofFind", re.sub(r"\D", "", c))[:300])); break
    elif st == "spawn5":
        ids = g.spawn(T.KIND, x - 20, z, count=5); print([g.read(i)["stage"] for i in ids])
    elif st == "engulf":
        c = g.spawn("Colonist", x + 2, z, faction="player")[0]
        print(g.proof("ProofEngulf", pid, c)[:60])
    elif st == "engulfmuff":
        c = g.spawn("Muffalo", x + 2, z)[0]
        print(g.proof("ProofEngulf", pid, c)[:60])
    elif st == "down":
        g.ok("jawa/pawn_force_incapacitate", pawn=pid, action="downed")
    elif st == "vanish":
        g.ok("jawa/pawn_force_incapacitate", pawn=pid, action="vanish"); pid = None
    elif st == "fight":
        cols = g.spawn("Colonist", x + 1, z, faction="player", count=4)
        for c in cols: g.call("jawa/set_draft", pawnId=c, drafted=True, fireAtWill=True)
        g.call("jawa/damage", damageDef="Blunt", amount=2, thingId=pid, instigatorId=cols[0])
    elif st == "saveload":
        g.ok("rimworld/save_game", saveName="RM_titano_nreprobe")
        g.call("rimworld/load_game_ready", saveName="RM_titano_nreprobe")
        for _ in range(60):
            time.sleep(3)
            r = g.call("rimworld/step_game_ticks", ticks=60, pauseFirst=True, timeoutMs=60000)
            if r.get("success") is True and r.get("advancedTicks", 0) >= 60: break
    a = n(); g.ticks(900); b = n()
    print("STEP %-9s NRE lines before %d after 900 ticks %d (+%d)%s" % (st, a, b, b - a,
          "" if not pid else " | " + g.proof("ProofRead", pid)[:120]), flush=True)
