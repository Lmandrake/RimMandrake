#!/usr/bin/env python3
"""live_a1_check.py -- MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG clause A1, the parts live_def_check.py cannot read.

Read-only, two bridge calls; the caller holds the bridge lock. Exit 0 PASS, 1 FAIL, 2 UNMEASURED.

1. The RUNNING list (jawa/running_mods) holds mandrake.rm.mineshaft and mandrake.rsw.armoury, and neither retired id
   (cain.mineshaft, leutiankane.mines2patchouterrim).
2. The Armoury assembly the game LOADED is the committed gate-free build: exactly one AppDomain JawaArmoury, claimed by
   the Armoury alone, whose MVID equals the MVID read from the committed DLL's own metadata. The file sha256 alone is not
   enough (the tool hashes the file NOW, and a redeploy after launch changes the file, not the loaded code). The committed
   DLL must carry no retired gate type name (GATE below), and its .srchash "# dll:" line must equal its bytes.
3. The shaft's bill SET: the generator's rule (validation.py replay) re-run over the newest DefDump capture's mineable
   rocks, restricted to the rocks that resolve in the running game. Every rock the rule bills has its RM_MineShaft_<rock>
   RecipeDef; every rock it does not bill (policy-barred, or a product an earlier rock already covers) has none.
   Sanity: steel and gold must be billed and the two vanilla barred rocks must resolve, else "nothing leaked" means nothing.

--selftest: offline; mutant replies for each clause must go red, and the pre-retirement DLL (97cbd8cb^, which still held
the gate) must be refused as the loaded assembly.
"""
import glob
import hashlib
import json
import os
import struct
import subprocess
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import validation as V            # noqa: E402  (the rule's constants and policy reader)
import live_def_check as L        # noqa: E402  (bridge seam and get_defs format)

PASS, FAIL, UNMEASURED = 0, 1, 2
NEEDS = ("mandrake.rm.mineshaft", "mandrake.rsw.armoury")
RETIRED = ("cain.mineshaft", "leutiankane.mines2patchouterrim")
ARMOURY_PID = "mandrake.rsw.armoury"
ASM = "JawaArmoury"
DLL = os.path.join(REPO, "src", "RimStarWars", "Armoury", "Assemblies", "JawaArmoury.dll")
GATE = b"MineShaftCanonGate"
PRE_RETIRE = "97cbd8cb4b83208e1649d1f04f383ef00d4dda5f^"


# ---------- ECMA-335 MVID ----------
def mvid(data):
    """The Module table's Mvid GUID, as .NET prints it (lower case, dashed). ValueError when the bytes are not a CLI PE."""
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("no PE signature")
    nsec, optsz = struct.unpack_from("<H", data, pe + 6)[0], struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    dd = opt + (96 if magic == 0x10B else 112)
    cli_rva = struct.unpack_from("<I", data, dd + 14 * 8)[0]
    secs = [struct.unpack_from("<IIII", data, opt + optsz + 40 * i + 8) for i in range(nsec)]

    def off(rva):
        for vsize, va, rawsz, raw in secs:
            if va <= rva < va + max(vsize, rawsz):
                return rva - va + raw
        raise ValueError("rva %#x in no section" % rva)
    if not cli_rva:
        raise ValueError("no CLI header")
    md = off(struct.unpack_from("<I", data, off(cli_rva) + 8)[0])
    if struct.unpack_from("<I", data, md)[0] != 0x424A5342:
        raise ValueError("no metadata signature")
    vlen = struct.unpack_from("<I", data, md + 12)[0]
    p = md + 16 + vlen
    nstreams = struct.unpack_from("<H", data, p + 2)[0]
    p += 4
    streams = {}
    for _ in range(nstreams):
        o, s = struct.unpack_from("<II", data, p)
        p += 8
        e = data.index(b"\0", p)
        streams[data[p:e].decode("ascii")] = (md + o, s)
        p = (e + 4) & ~3
    t, _ = streams.get("#~") or streams["#-"]
    heaps = data[t + 6]
    valid = struct.unpack_from("<Q", data, t + 8)[0]
    if not valid & 1:
        raise ValueError("no Module table")
    rows = t + 24 + 4 * bin(valid).count("1")       # first table's first row (Module is table 0)
    sidx = 4 if heaps & 1 else 2
    gidx = 4 if heaps & 2 else 2
    g = struct.unpack_from("<I" if gidx == 4 else "<H", data, rows + 2 + sidx)[0]
    gh, gs = streams["#GUID"]
    if not 1 <= g <= gs // 16:
        raise ValueError("Mvid index %d outside #GUID" % g)
    return str(uuid.UUID(bytes_le=bytes(data[gh + 16 * (g - 1):gh + 16 * g])))


def srchash_dll_line(path):
    for line in open(path, encoding="utf-8"):
        if line.startswith("# dll:"):
            return line.split(":", 1)[1].strip()
    return None


def committed_build(dll_bytes, srchash_line):
    """-> (mvid or None, problems) about the committed DLL alone."""
    bad = []
    if GATE in dll_bytes:
        bad.append("FAIL: the committed JawaArmoury.dll still names %s" % GATE.decode())
    if srchash_line != hashlib.sha256(dll_bytes).hexdigest():
        bad.append("FAIL: JawaArmoury.dll.srchash '# dll:' %r is not the committed DLL's sha256" % srchash_line)
    try:
        return mvid(dll_bytes), bad
    except (ValueError, KeyError, struct.error, IndexError) as e:
        return None, bad + ["UNMEASURED: the committed DLL's MVID could not be read: %s" % e]


# ---------- judges (pure) ----------
def judge_mods(reply, want_mvid):
    """-> (code, lines) over a jawa/running_mods reply."""
    if not isinstance(reply, dict) or not isinstance(reply.get("packageIds"), list):
        return UNMEASURED, ["UNMEASURED: running_mods gave no packageIds list"]
    ids = {str(p).lower() for p in reply["packageIds"]}
    if not ids:
        return UNMEASURED, ["UNMEASURED: running_mods listed no mod"]
    bad, lines = [], []
    for p in NEEDS:
        if p not in ids:
            bad.append("UNMEASURED: the running load lacks %s (A1 is about a list holding it)" % p)
    for p in RETIRED:
        if p in ids:
            bad.append("FAIL: retired %s is on the RUNNING list" % p)
    a = reply.get("assembly")
    m = a.get("matches") if isinstance(a, dict) else None
    if not isinstance(m, list):
        bad.append("UNMEASURED: running_mods gave no assembly record for %s" % ASM)
    elif len(m) != 1:
        bad.append("FAIL: %d AppDomain assemblies named %s (a duplicate copy, or none loaded)" % (len(m), ASM))
    else:
        r = m[0] if isinstance(m[0], dict) else {}
        if r.get("claimedBy") != [ARMOURY_PID]:
            bad.append("FAIL: %s claimed by %r, not the Armoury alone" % (ASM, r.get("claimedBy")))
        got = str(r.get("mvid") or "").lower()
        if not want_mvid:
            bad.append("UNMEASURED: no committed MVID to compare")
        elif got != want_mvid:
            bad.append("FAIL: the loaded %s MVID %s is not the committed gate-free build's %s (stale deploy, or "
                       "redeployed after launch)" % (ASM, got or "?", want_mvid))
        else:
            lines.append("loaded %s is the committed build (MVID %s, from %s)" % (ASM, got, r.get("location")))
    lines.append("running list: %d mods, has %s, lacks %s" % (len(ids), ", ".join(NEEDS), ", ".join(RETIRED)))
    return _code(bad), bad or lines


def capture_rocks(capdir):
    """The rule's ordered eligible rocks from a capture: [(rock, product)] (validation.replay's sort, verbatim)."""
    T = json.load(open(os.path.join(capdir, "ThingDef.json"), encoding="utf-8"))["defs"]
    rocks = []
    for t in T:
        f = t.get("fields") or {}
        b = f.get("building") or {}
        if not f.get("mineable") or not b.get("mineableThing"):
            continue
        res, nat = bool(b.get("isResourceRock")), bool(b.get("isNaturalRock"))
        if not (res or (V.DEFAULTS["stoneBills"] and nat)):
            continue
        rocks.append((0 if res else 1, 0 if (b.get("mineableScatterCommonality") or 0) > 0 else 1,
                      -(b.get("mineableScatterCommonality") or 0), 0, t["defName"], b["mineableThing"]))
    rocks.sort()
    return [(r[4], r[5]) for r in rocks]


def expected_bills(rocks, live, banned):
    """The rule over the rocks that resolve live: the set of rocks that get a bill."""
    out, covered = set(), set()
    for rock, product in rocks:
        if rock not in live or product in banned:
            continue
        if product in covered:
            continue
        covered.add(product)
        out.add(rock)
    return out


def judge_bills(rocks, banned, reply):
    if not isinstance(reply, dict) or not isinstance(reply.get("defs"), list):
        return UNMEASURED, ["UNMEASURED: get_defs gave no defs list"]
    found = {}
    for d in reply["defs"]:
        if isinstance(d, dict) and isinstance(d.get("requested"), str) and isinstance(d.get("found"), bool):
            if found.get(d["requested"], d["found"]) != d["found"]:
                return UNMEASURED, ["UNMEASURED: two records for %s disagree" % d["requested"]]
            found[d["requested"]] = d["found"]
    keys = [k for r, _ in rocks for k in ("ThingDef/" + r, "RecipeDef/" + V.PREFIX + r)]
    missing = [k for k in keys if k not in found]
    if missing:
        return UNMEASURED, ["UNMEASURED: get_defs never answered %d key(s), e.g. %s" % (len(missing), missing[:3])]
    live = {r for r, _ in rocks if found["ThingDef/" + r]}
    want = expected_bills(rocks, live, banned)
    bad = []
    for r in V.MUST_BILL:
        if r not in want:
            bad.append("UNMEASURED: sanity rock %s does not resolve or is not billed by the rule" % r)
    for r in V.BARRED_ROCKS:
        if r not in live:
            bad.append("UNMEASURED: sanity barred rock %s does not resolve live, so its absent bill proves nothing" % r)
    for r, product in rocks:
        has = found["RecipeDef/" + V.PREFIX + r]
        if r in want and not has:
            bad.append("FAIL: rock %s (-> %s) should have bill %s%s, it does not resolve" % (r, product, V.PREFIX, r))
        elif r not in want and has:
            why = ("its product %s is barred" % product if product in banned else
                   "its rock is not loaded (stale capture?)" if r not in live else
                   "an earlier rock already covers %s" % product)
            bad.append("FAIL: bill %s%s exists, but %s" % (V.PREFIX, r, why))
    nb = len([r for r, p in rocks if r in live and p in banned])
    return _code(bad), bad or ["bill set matches the rule: %d live rock(s) of %d captured, %d bill(s), %d barred rock(s) "
                               "with none" % (len(live), len(rocks), len(want), nb)]


def _code(bad):
    if any(b.startswith("FAIL") for b in bad):
        return FAIL
    return UNMEASURED if bad else PASS


def banned_products():
    return set(V.policy_products(V.BASE_POLICY)) | set(V.policy_products(V.CANON_POLICY))


def newest_capture():
    caps = sorted(glob.glob(os.path.join(V.CAPTURES, "*", "defs")))
    return caps[-1] if caps else None


# ---------- live ----------
def main(timeout=60):
    data = open(DLL, "rb").read()
    want, bad = committed_build(data, srchash_dll_line(DLL + ".srchash"))
    codes, out = [_code(bad)], list(bad)
    reply, why = L._bridge("jawa/running_mods", {"details": False, "assembly": ASM}, timeout)
    c, lines = judge_mods(reply, want) if reply is not None else (UNMEASURED, ["UNMEASURED: running_mods: %s" % why])
    codes.append(c)
    out += lines
    cap = newest_capture()
    if not cap:
        codes.append(UNMEASURED)
        out.append("UNMEASURED: no DefDump capture to replay the rule over")
    else:
        rocks = capture_rocks(cap)
        keys = [k for r, _ in rocks for k in ("ThingDef/" + r, "RecipeDef/" + V.PREFIX + r)]
        reply, why = L.call_get_defs(keys, timeout)
        c, lines = judge_bills(rocks, banned_products(), reply) if reply is not None else (
            UNMEASURED, ["UNMEASURED: get_defs: %s" % why])
        codes.append(c)
        out += ["capture %s" % os.path.basename(os.path.dirname(cap))] + lines
    code = FAIL if FAIL in codes else UNMEASURED if UNMEASURED in codes else PASS
    print("\n".join(out))
    print({PASS: "VERDICT PASS", FAIL: "VERDICT FAIL", UNMEASURED: "VERDICT UNMEASURED"}[code])
    return code


# ---------- offline self-test ----------
def selftest():
    fails = []

    def expect(name, got, want):
        if got != want:
            fails.append("%s: got %s, want %s" % (name, got, want))

    data = open(DLL, "rb").read()
    good_mvid, bad = committed_build(data, srchash_dll_line(DLL + ".srchash"))
    expect("committed DLL is gate-free and stamped", bad, [])
    if not good_mvid or len(good_mvid) != 36:
        fails.append("committed DLL MVID unreadable: %r" % good_mvid)
    old = subprocess.run(["git", "-C", REPO, "show", PRE_RETIRE + ":src/RimStarWars/Armoury/Assemblies/JawaArmoury.dll"],
                         capture_output=True, timeout=60).stdout
    old_mvid, old_bad = committed_build(old, hashlib.sha256(old).hexdigest()) if old else (None, ["no old DLL"])
    expect("pre-retirement DLL names the gate (probe can see)", any("still names" in b for b in old_bad), True)
    if not old_mvid or old_mvid == good_mvid:
        fails.append("pre-retirement MVID %r should be readable and differ from %r" % (old_mvid, good_mvid))
    expect("srchash mismatch goes red", _code(committed_build(data, "0" * 64)[1]), FAIL)

    ids = ["ludeon.rimworld", "brrainz.harmony"] + list(NEEDS)
    asm = lambda mv, claim=(ARMOURY_PID,), n=1: {"name": ASM, "matchCount": n, "matches": [
        {"location": "X", "mvid": mv, "claimedBy": list(claim)}] * n}
    good = {"packageIds": ids, "assembly": asm(good_mvid)}
    expect("mods: good", judge_mods(good, good_mvid)[0], PASS)
    for p in RETIRED:
        expect("mods: %s on list" % p, judge_mods(dict(good, packageIds=ids + [p]), good_mvid)[0], FAIL)
    expect("mods: stale gate DLL loaded", judge_mods(dict(good, assembly=asm(old_mvid)), good_mvid)[0], FAIL)
    expect("mods: duplicate assembly", judge_mods(dict(good, assembly=asm(good_mvid, n=2)), good_mvid)[0], FAIL)
    expect("mods: claimed twice", judge_mods(dict(good, assembly=asm(good_mvid, (ARMOURY_PID, "x"))), good_mvid)[0], FAIL)
    expect("mods: shaft absent", judge_mods(dict(good, packageIds=ids[:-2] + [ARMOURY_PID]), good_mvid)[0], UNMEASURED)
    expect("mods: no assembly", judge_mods({"packageIds": ids}, good_mvid)[0], UNMEASURED)

    cap = newest_capture()
    if not cap:
        fails.append("no DefDump capture: the bill judge cannot be exercised")
    else:
        rocks, banned = capture_rocks(cap), banned_products()
        live = {r for r, _ in rocks}
        want = expected_bills(rocks, live, banned)

        def reply(drop_rock=(), bill_extra=(), bill_drop=()):
            d = []
            for r, _ in rocks:
                d.append({"requested": "ThingDef/" + r, "found": r not in drop_rock})
                d.append({"requested": "RecipeDef/" + V.PREFIX + r,
                          "found": (r in want or r in bill_extra) and r not in bill_drop})
            return {"defs": d}
        expect("bills: good", judge_bills(rocks, banned, reply())[0], PASS)
        expect("bills: steel bill missing", judge_bills(rocks, banned, reply(bill_drop=("MineableSteel",)))[0], FAIL)
        other = sorted(want - set(V.MUST_BILL))[0]
        expect("bills: one ordinary bill missing", judge_bills(rocks, banned, reply(bill_drop=(other,)))[0], FAIL)
        for r in sorted(r for r, p in rocks if p in banned):
            expect("bills: barred %s billed" % r, judge_bills(rocks, banned, reply(bill_extra=(r,)))[0], FAIL)
        dup = [r for r, p in rocks if r not in want and p not in banned]
        if dup:
            expect("bills: covered-product %s billed" % dup[0], judge_bills(rocks, banned, reply(bill_extra=dup[:1]))[0], FAIL)
        expect("bills: vanilla barred rock unloaded", judge_bills(rocks, banned, reply(drop_rock=V.BARRED_ROCKS[:1]))[0],
               UNMEASURED)
        expect("bills: unanswered key", judge_bills(rocks, banned, {"defs": reply()["defs"][2:]})[0], UNMEASURED)
        expect("rule: steel billed", "MineableSteel" in want, True)
        expect("rule: barred never billed", any(p in banned for r, p in rocks if r in want), False)
    for f in fails:
        print("SELFTEST FAIL " + f)
    print("SELFTEST %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)))
    return PASS if not fails else FAIL


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv[1:] else main())
