#!/usr/bin/env python3
# selftest-timeout: 540
"""Every JawaBench Harmony hook is on HOOKS.md and follows the hook laws (BRIDGE_HOOKS_HARDEN_REENTRANT_AND_FAULTY).

    python3 src/RimMandrake/bridgetools/selftest_bridge_hooks.py           static audit + C# units (needs dotnet.exe)
    python3 src/RimMandrake/bridgetools/selftest_bridge_hooks.py --no-cs   static audit only (explicit; walled checker)

1. TABLE vs SOURCE: every file under JawaBench.BridgeTools with a `.Patch(` call is a row of bridgetools/HOOKS.md,
   its `.Patch(` count equals the row's `sites`, every hook named on the row exists in that file, and every hook
   method the file hands Harmony by name (nameof/GetMethod "...Pre/Post/Fin/Prefix/Postfix/Finalizer") is on the row.
2. RULES per hook, read from its source body: c contained (try/catch, or an expression body calling one helper that
   is), ro `bool __runOriginal` in the signature, th a thread check, or an orphan-safe state read, vf a void
   finalizer, gate a deliberate fail-closed refusal (no rule checked). Tightened (blind check, gen 3): c also refuses
   any call left OUTSIDE every try unless it is a guard (Admit/Commit/OnMain/Interlocked), a same-file contained helper
   or a cross-file helper that calls nothing; ro also needs __runOriginal READ and handed to every Commit(; th also needs
   every Admit(/TryEnter( handed a real main-thread test (OnMain()), not a constant. Every row's proof file exists; a `::T_X*`
   proof names at least one unit that exists.
3. The instrument can see: MUTANTS rewrite the real source text in memory (drop __runOriginal, strip a try, make a
   finalizer return a value, add an unlisted patch site) and each must turn the audit red.
4. Without --no-cs: TpsMathSelfTest is built via winbuild and run in unit mode ("U"); every T_Recorder*, T_Guard*
   and T_Writer* unit must print ok. No dotnet.exe = FAIL (UNMEASURED), never a pass on half the evidence.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(HERE, "JawaBench.BridgeTools")
TABLE = os.path.join(HERE, "HOOKS.md")
HOOK_NAME = re.compile(r'(?:nameof\(|GetMethod\(")([A-Z][A-Za-z0-9]*(?:Pre|Post|Fin|Prefix|Postfix|Finalizer))\b')
ROW = re.compile(r"^\|\s*`(JawaBench[A-Za-z0-9]*\.cs)`\s*\|\s*(\d+)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$")
HOOK_TOK = re.compile(r"([A-Za-z0-9]+)\[([a-z,]+)\]")
THREAD = re.compile(r"OnMain\(|MainThreadId|Admit\(|TryEnter\(|IsInMainThread")
ORPHAN = re.compile(r"\.Valid\b|Commit\(|\.Exit\(|==\s*0\)\s*(?:\{[^}]*\}|return)|<=\s*0\)\s*return|==\s*int\.MinValue|if\s*\(\s*__state\s*\)|"
                    r"if\s*\(\s*s\s*==\s*0\s*\)|__state\s*!=\s*null|__state\s*==\s*null|\.Pop\(")
RULES = {"c", "ro", "th", "or", "vf", "gate"}


def read_sources():
    out = {}
    for n in sorted(os.listdir(SRC)):
        if n.endswith(".cs"):
            with open(os.path.join(SRC, n), encoding="utf-8-sig") as f:
                out[n] = f.read()
    return out


def read_table(text):
    rows = {}
    for ln in text.splitlines():
        m = ROW.match(ln)
        if not m:
            continue
        hooks = HOOK_TOK.findall(m.group(6))
        rows[m.group(1)] = {"sites": int(m.group(2)), "install": m.group(3).strip(), "default": m.group(4).strip(),
                            "hooks": [(h, set(r.split(","))) for h, r in hooks], "proof": m.group(7).strip()}
    return rows


def method_text(src, name):
    """(signature, body) of the static method `name`; body is the {...} block or the => expression."""
    m = re.search(r"static\s+[\w<>\[\],. ?]+\s+" + re.escape(name) + r"\s*\(", src)
    if not m:
        return None, None
    i, depth = m.end(), 1
    while i < len(src) and depth:                       # the parameter list (may hold parentheses)
        depth += {"(": 1, ")": -1}.get(src[i], 0)
        i += 1
    sig = src[m.start():i]
    j = i
    while j < len(src) and src[j] in " \t\r\n":
        j += 1
    if src.startswith("=>", j):
        k = src.index(";", j)
        return sig, src[j:k + 1]
    if j >= len(src) or src[j] != "{":
        return sig, ""
    depth, k = 0, j
    while k < len(src):
        c = src[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return sig, src[j:k + 1]
        k += 1
    return sig, src[j:]


def contained(src, body, depth=0):
    if re.search(r"\btry\b", body) and re.search(r"\bcatch\b", body):
        return True
    if depth >= 1:
        return False
    bare = body.strip()
    if bare.startswith("=>") or bare.count(";") <= 2:   # a one-line delegation: the helper must be contained
        calls = [c for c in re.findall(r"\b([A-Z][A-Za-z0-9]*)\s*\(", body) if c not in ("Exception",)]
        for c in calls:
            _, hb = method_text(src, c)
            if hb and contained(src, hb, depth + 1):
                return True
        # a body that only reads flags/returns and calls nothing can't throw beyond the game's own state
        if not calls and not re.search(r"\.\w+\s*\(", body) and not re.search(r"\[|\bnew\b", body):
            return True
    return False


GUARD_CALLS = {"Admit", "Commit", "OnMain", "TryEnter", "Interlocked.Increment", "Interlocked.Decrement",
               "Interlocked.Add", "Interlocked.Exchange", "Interlocked.CompareExchange", "Stopwatch.GetTimestamp"}
KEYWORDS = {"if", "while", "for", "foreach", "switch", "catch", "return", "nameof", "typeof", "using", "lock", "sizeof",
            "default", "when"}


def scrub(code):
    """Comments and string literals blanked, so a word in prose is never read as a call."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r'@?"(?:\\.|[^"\\])*"', '""', code)


def _brace_end(s, j):
    d = 0
    for k in range(j, len(s)):
        if s[k] == "{":
            d += 1
        elif s[k] == "}":
            d -= 1
            if d == 0:
                return k
    return len(s) - 1


def outside_try(body):
    """The body with every try { } and its catch/finally blocks cut out: what runs unprotected."""
    out, i = [], 0
    while True:
        m = re.compile(r"\btry\s*\{").search(body, i)
        if not m:
            out.append(body[i:])
            return "".join(out)
        out.append(body[i:m.start()])
        k = _brace_end(body, m.end() - 1) + 1
        while True:
            m2 = re.compile(r"\s*(?:catch\b\s*(?:\([^)]*\))?\s*(?:when\s*\([^)]*\)\s*)?|finally\s*)\{").match(body, k)
            if not m2:
                break
            k = _brace_end(body, m2.end() - 1) + 1
        i = k


def calls_in(code):
    """Called names, qualified as written (`G.Admit`, `JawaBenchVitals.OnKill`, `Begin`)."""
    return [c for c in re.findall(r"(?<![\w.])([A-Za-z_][\w.]*)\s*\(", code) if c.split(".")[-1] not in KEYWORDS]


def is_guard(call):
    return call in GUARD_CALLS or call.split(".")[-1] in ("Admit", "Commit", "OnMain", "TryEnter")


def unprotected_calls(fn, sources, body):
    """Calls a hook makes outside any try that are not proven harmless. A same-file helper is harmless when its own
    body is contained or calls only guards; a helper in another file only when its whole body calls nothing (a throw
    from anywhere else would surface as the patched game method's own exception)."""
    bad = []
    for c in calls_in(outside_try(scrub(body))):
        if is_guard(c):
            continue
        parts = c.split(".")
        if len(parts) == 1:
            _, hb = method_text(sources[fn], c)
            if hb is not None and (contained(sources[fn], hb) or all(is_guard(x) for x in calls_in(scrub(hb)))):
                continue
        elif len(parts) == 2 and parts[0] not in ("this", "base"):
            hb = None
            for other in sources.values():
                if re.search(r"\bclass\s+" + re.escape(parts[0]) + r"\b", other):
                    _, hb = method_text(other, parts[1])
                    break
            if hb is not None and not calls_in(scrub(hb)) and not re.search(r"\bnew\b|\[", hb):
                continue
        bad.append(c)
    return bad


def orphan_safe_helper(src, body):
    """A hook that hands __state to a same-file helper (RootFinalizer -> RootFinalizerCore, so the helper's early
    returns cannot skip the hook's own tail) is orphan-safe when that helper's body reads __state orphan-safely."""
    for c in calls_in(scrub(body)):
        if "." in c or not re.search(re.escape(c) + r"\s*\(\s*__state\b", body):
            continue
        _, hb = method_text(src, c)
        if hb is not None and ORPHAN.search(hb):
            return True
    return False


def audit(sources, table_text):
    fails = []
    rows = read_table(table_text)
    if not rows:
        return ["HOOKS.md: no table rows parsed (instrument blind)"]
    for fn, src in sources.items():
        n = len(re.findall(r"\.Patch\(", src))
        if not n:
            continue
        row = rows.get(fn)
        if row is None:
            fails.append("%s: %d .Patch( site(s) but no HOOKS.md row" % (fn, n))
            continue
        if row["sites"] != n:
            fails.append("%s: HOOKS.md says %d sites, source has %d" % (fn, row["sites"], n))
        listed = {h for h, _ in row["hooks"]}
        for h in sorted(set(HOOK_NAME.findall(src)) - listed):
            sig, _ = method_text(src, h)
            if sig is not None:          # a hook method of this file handed to Harmony by name, not on the row
                fails.append("%s: hook %s is patched but not on HOOKS.md" % (fn, h))
        for h, rules in row["hooks"]:
            bad = rules - RULES
            if bad:
                fails.append("%s.%s: unknown rule(s) %s" % (fn, h, sorted(bad)))
            sig, body = method_text(src, h)
            if sig is None:
                fails.append("%s.%s: listed on HOOKS.md, no such static method" % (fn, h))
                continue
            if "gate" in rules:
                continue
            if "c" in rules and not contained(src, body):
                fails.append("%s.%s: body not contained (no try/catch)" % (fn, h))
            if "c" in rules:
                for c in unprotected_calls(fn, sources, body):
                    fails.append("%s.%s: call %s( runs outside any try (its throw replaces the game's result)" % (fn, h, c))
            sb = scrub(body)
            if "ro" in rules and not re.search(r"\bbool\s+__runOriginal\b", sig):
                fails.append("%s.%s: postfix lacks bool __runOriginal (records a skipped original)" % (fn, h))
            if "ro" in rules and not re.search(r"\b__runOriginal\b", sb):
                fails.append("%s.%s: __runOriginal is taken but never read (a skipped original is recorded)" % (fn, h))
            if "ro" in rules:
                for a in re.findall(r"\bCommit\(\s*[^,()]+,\s*([^)]*)\)", sb):
                    if a.strip() != "__runOriginal":
                        fails.append("%s.%s: Commit( is handed %s, not __runOriginal" % (fn, h, a.strip()))
            if "th" in rules and not THREAD.search(body):
                fails.append("%s.%s: no thread check before recorder state" % (fn, h))
            if "th" in rules:
                for a in re.findall(r"\b(?:Admit|TryEnter)\(\s*([^,]*),", sb):
                    a = a.strip()
                    local = re.fullmatch(r"[a-z_]\w*", a) and re.search(r"\b" + a + r"\s*=\s*OnMain\(\)", sb)
                    if not (re.search(r"OnMain\(\)|MainThreadId|IsInMainThread", a) or local):
                        fails.append("%s.%s: thread gate handed %s, not a main-thread test" % (fn, h, a.strip()))
            if "or" in rules and not ORPHAN.search(body) and not orphan_safe_helper(src, body):
                fails.append("%s.%s: no orphan-safe read of __state (skipped prefix / late install)" % (fn, h))
            if "vf" in rules and not re.match(r"static\s+void\b", sig):
                fails.append("%s.%s: finalizer is not void (would swallow or replace the game's exception)" % (fn, h))
    for fn, row in rows.items():
        if fn not in sources:
            fails.append("HOOKS.md row %s: no such file" % fn)
        if row["install"].startswith("startup") and row["default"].startswith("on") and not row["proof"]:
            fails.append("%s: always-on hook with no proof (unproven always-on hooks stay off)" % fn)
        for path, unit in re.findall(r"`([A-Za-z0-9_/.]+\.(?:cs|py))(?:::(T_[A-Za-z0-9_]*)\*?)?`", row["proof"]):
            p = os.path.join(HERE, path)
            if not os.path.exists(p):
                fails.append("%s: proof %s does not exist" % (fn, path))
            elif unit and unit not in open(p, encoding="utf-8").read():
                fails.append("%s: proof %s names %s*, no such unit" % (fn, path, unit))
    return fails


MUTANTS = [
    ("RootFinalizer stops handing __state to its orphan-safe helper", "JawaBenchTpsSampler.cs",
     "RootFinalizerCore(__state, __exception);", "RootFinalizerCore(default(JawaBenchHookGuard.Scope), __exception);"),
    ("drop __runOriginal from TakeDamagePostfix", "JawaBenchSituationalTools.cs",
     ", DamageWorker.DamageResult __result, bool __runOriginal)", ", DamageWorker.DamageResult __result)"),
    ("strip the thread check from SplitPrefix", "JawaBenchSituationalTools.cs",
     "if (!GSplit.Admit(OnMain(), out __state)) return;", "__state = default(JawaBenchHookGuard.Scope); __state.Valid = true;"),
    ("strip the orphan check from MapCompTimer.Fin", "JawaBenchMapCompTiming.cs",
     "if (__state == 0) { Interlocked.Increment(ref Orphans); return; }", ""),
    ("finalizer returns a value", "JawaBenchSituationalTools.cs",
     "private static void DestroyFin(Exception __exception) => Threw(GDestroy, __exception);",
     "private static Exception DestroyFin(Exception __exception) => null;"),
    ("uncontained GameCompTimer.Fin", "JawaBenchGameCompTiming.cs",
     'catch (Exception e) { Fault("fin", e); }', ""),
    ("KillPostfix calls Vitals.OnKill bare (outside a try)", "JawaBenchSituationalTools.cs",
     "try { if (__instance != null && __instance.Dead) JawaBenchVitals.OnKill(__instance, dinfo, exactCulprit); }\n"
     "            catch (Exception ex) { NoteError(GKill, \"kill-vitals\", ex); }",
     "if (__instance != null && __instance.Dead) JawaBenchVitals.OnKill(__instance, dinfo, exactCulprit);"),
    ("TakeDamagePostfix commits true, ignoring __runOriginal", "JawaBenchSituationalTools.cs",
     "GDamage.Commit(sc, __runOriginal)", "GDamage.Commit(sc, true)"),
    ("AbsorbPostfix commits true, ignoring __runOriginal", "JawaBenchSituationalTools.cs",
     "GAbsorb.Commit(__state, __runOriginal)", "GAbsorb.Commit(__state, true)"),
    ("TakeDamagePostfix admits true, not OnMain()", "JawaBenchSituationalTools.cs",
     "GDamage.Admit(OnMain(), out var sc)", "GDamage.Admit(true, out var sc)"),
    ("SplitPrefix admits true, not OnMain()", "JawaBenchSituationalTools.cs",
     "GSplit.Admit(OnMain(), out __state)", "GSplit.Admit(true, out __state)"),
    ("Sampler RootPrefix gates on a constant, not its OnMain() local", "JawaBenchTpsSampler.cs",
     "GRoot.TryEnter(main, out __state)", "GRoot.TryEnter(true, out __state)"),
    ("an unlisted patch site", "JawaBenchHudLease.cs", "internal static void Install()",
     "static void Extra(Harmony h){ h.Patch(null); }\n        internal static void Install()"),
]


def run_mutants(sources, table_text):
    """A mutant is caught only by a failure the unmutated tree does not have (never by a red baseline)."""
    fails = []
    base = set(audit(sources, table_text))
    for name, fn, old, new in MUTANTS:
        src = sources.get(fn, "")
        if old not in src:
            fails.append("mutant '%s': anchor gone from %s (update MUTANTS)" % (name, fn))
            continue
        if fn == "JawaBenchGameCompTiming.cs":          # strip the try as well as its catch
            src2 = src.replace(old, new).replace(
                "            try\n            {\n                if (Depth > 0) Depth--;\n                if (s < 0 || __instance == null || Core == null) return;",
                "            {\n                if (Depth > 0) Depth--;\n                if (s < 0 || __instance == null || Core == null) return;")
        else:
            src2 = src.replace(old, new)
        got = set(audit(dict(sources, **{fn: src2}), table_text)) - base
        if not got:
            fails.append("mutant '%s' SURVIVED the audit" % name)
    return fails


def cs_units():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    import winbuild
    if not any(os.path.exists(c) for c in ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]):
        return ["C# units UNMEASURED: no dotnet.exe on this machine (pass --no-cs to accept the static audit alone)"]
    proj = os.path.join(HERE, "TpsMathSelfTest")
    with winbuild.exclusive("TpsMathSelfTest"):   # the stage is shared with selftest_tps_record's seam build
        rc, rec = winbuild.stage_build(os.path.join(proj, "TpsMathSelfTest.csproj"), stage_name="TpsMathSelfTest")
        if rc:
            return ["TpsMathSelfTest build FAILED (rc %s)" % rc]
        dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\TpsMathSelfTest.dll"
        p = subprocess.run([winbuild.dotnet_exe(), dll], input="U\n", capture_output=True, text=True,
                           cwd="/mnt/d/Luke/dev", timeout=400)
    units = [ln.strip() for ln in p.stdout.splitlines() if ln.startswith("U ") and not ln.startswith("U-count")]
    mine = [u for u in units if re.match(r"U (Recorder|Guard|Writer)", u)]
    fails = [u for u in mine if not u.endswith(" ok")]
    want = {"RecorderForeignThreadRejectedBeforeState", "RecorderReentrantCallsStandAlone",
            "RecorderSkippedOriginalRecordsNothing", "RecorderSkippedPrefixIsOrphanNotZero",
            "RecorderGameExceptionCountedNotSwallowed", "RecorderOwnFaultCountedRecorderStaysOn",
            "WriterFaultNeverBlocksEnqueue"}
    seen = {u.split()[1] for u in mine}
    fails += ["C# unit %s did not run" % w for w in sorted(want - seen)]
    print("C# units: %d hook/writer units, %d ok" % (len(mine), len(mine) - len([u for u in mine if not u.endswith(" ok")])))
    return fails


def main(argv):
    sources = read_sources()
    with open(TABLE, encoding="utf-8") as f:
        table_text = f.read()
    fails = audit(sources, table_text)
    rows = read_table(table_text)
    nhooks = sum(len(r["hooks"]) for r in rows.values())
    sites = sum(len(re.findall(r"\.Patch\(", s)) for s in sources.values())
    print("static audit: %d files with patch sites, %d sites, %d table rows, %d hooks" %
          (sum(1 for s in sources.values() if ".Patch(" in s), sites, len(rows), nhooks))
    if sites == 0 or nhooks == 0:
        fails.append("instrument blind: zero patch sites or zero hooks parsed")
    mf = run_mutants(sources, table_text)
    print("mutants: %d/%d caught" % (len(MUTANTS) - len(mf), len(MUTANTS)))
    fails += mf
    if "--no-cs" not in argv:
        fails += cs_units()
    for f in fails:
        print("FAIL", f)
    print("RESULT", "FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
