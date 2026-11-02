#!/usr/bin/env python3
"""ExplosiveGrowth's ExposeData shares ONE `tmpKeys` working list across five dictionaries (EGROWTH_SAVELOAD_PROVE_DICT_SCRIBE_SHARE).

`RM_MapComponent_ExplosiveGrowth.ExposeData` passes the same `ref tmpKeys` to soakUntil, suppressedUntil, ashUntil, charges
and rainUsed, and the same `ref tmpInts` to four of them. Is that safe across a save/load? This test answers offline:

1. PASS MODEL. A transcription of RimWorld 1.6 `Verse.Scribe_Collections.Look<K,V>(ref dict, label, keyMode, valueMode,
   ref keysWorkingList, ref valuesWorkingList, ...)` and the `Look<T>(ref list, ...)` it calls (decompiled 1.6,
   `Verse/Scribe_Collections.cs`). The facts the model rests on:
     * Saving and LoadingVars assign FRESH working lists on every call (`keysWorkingList = new List<K>()`);
     * a dictionary with no Reference key/value is BUILT in LoadingVars, right after its own lists load
       (`(!flag && Scribe.mode == LoadSaveMode.LoadingVars) -> BuildDictionary`);
     * ResolvingCrossRefs touches a Value or Deep list not at all (Deep elements register themselves for later passes);
       a Reference list is replaced by `TakeResolvedRefList`, and a Reference dictionary is built THEN, from whatever
       the working-list fields hold at that moment;
     * PostLoadInit only clears and nulls the working lists; the dictionary keeps its own entries.
   The call sequence is PARSED from the shipped ExposeData, run through Saving -> LoadingVars -> ResolvingCrossRefs ->
   PostLoadInit with the shared refs, and every collection must come back equal to what was saved.
2. GUARD. A working list shared by two or more calls must never meet `LookMode.Reference`: that moves the build to
   ResolvingCrossRefs, where the shared list holds only the LAST dictionary's keys.
3. SANITY PROBE. The same run with soakUntil's values switched to `LookMode.Reference` MUST corrupt a dictionary in the
   model and MUST trip the guard, so a pass means the instrument can see.
4. ENGINE PIN. When the decompiled 1.6 source is on this machine, the lines the model rests on are checked in it.

    python3 src/RimMandrake/Utils/selftest_explosivegrowth_scribe_share.py

The live counterpart is ExplosiveGrowth/validation.py chain `scribe_round_trip` (save, load, re-save: identical node).
"""
import copy
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMP = os.path.join(os.path.dirname(HERE), "ExplosiveGrowth", "Source", "RM_MapComponent_ExplosiveGrowth.cs")
DECOMP = os.environ.get("RW16_DECOMP", "/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all")
ENGINE_LINES = [   # Verse/Scribe_Collections.cs, Look<K,V> with working lists
    "keysWorkingList = new List<K>();",
    "valuesWorkingList = new List<V>();",
    "bool flag = keyLookMode == LookMode.Reference || valueLookMode == LookMode.Reference;",
    "if ((flag && Scribe.mode == LoadSaveMode.ResolvingCrossRefs) || (!flag && Scribe.mode == LoadSaveMode.LoadingVars))",
    "BuildDictionary(dict, keysWorkingList, valuesWorkingList, label, logNullErrors);",
    "list = Scribe.loader.crossRefs.TakeResolvedRefList<T>(\"\");",
]

SAVING, LOADING, RESOLVING, POSTLOAD = "Saving", "LoadingVars", "ResolvingCrossRefs", "PostLoadInit"

DICT_CALL = re.compile(r"Scribe_Collections\.Look\(ref ([\w.]+), \"(\w+)\", LookMode\.(\w+), LookMode\.(\w+), "
                       r"ref (\w+), ref (\w+)\)")
LIST_CALL = re.compile(r"Scribe_Collections\.Look\(ref ([\w.]+), \"(\w+)\", LookMode\.(\w+)\)")


def parse_calls(text):
    """The Scribe_Collections calls of ExposeData, in order: dict(kind, field, label, modes, wl)."""
    m = re.search(r"public override void ExposeData\(\)\s*\{(.*?)\n        \}", text, re.S)
    if not m:
        raise SystemExit("FAIL: ExposeData not found in %s" % COMP)
    calls = []
    for line in m.group(1).splitlines():
        d = DICT_CALL.search(line)
        if d:
            calls.append({"kind": "dict", "field": d.group(1), "label": d.group(2), "kmode": d.group(3),
                          "vmode": d.group(4), "kwl": d.group(5), "vwl": d.group(6)})
            continue
        l = LIST_CALL.search(line)
        if l:
            calls.append({"kind": "list", "field": l.group(1), "label": l.group(2), "mode": l.group(3)})
        elif "Scribe_Collections.Look" in line:
            raise SystemExit("FAIL: a Scribe_Collections call this test cannot parse: %s" % line.strip())
    return calls


class Ref(object):
    """A Reference-mode element: a load id that resolves back to its object in ResolvingCrossRefs."""
    def __init__(self, obj):
        self.obj = obj


class Scribe(object):
    """The model. `doc` is the save document: label -> stored payload. `fields` is the component's state; `refs` the
    crossRefs registry (a FIFO of id lists, as RegisterLoadIDListReadFromXml / TakeResolvedRefList use it)."""

    def __init__(self):
        self.doc, self.mode, self.refq = {}, None, []

    def look_list(self, lst, path, mode):
        if self.mode == SAVING:
            self.doc[path] = None if lst is None else [Ref(x) if mode == "Reference" else copy.deepcopy(x) for x in lst]
            return lst
        if self.mode == LOADING:
            stored = self.doc.get(path)
            if stored is None:
                if mode == "Reference":
                    self.refq.append(None)
                return None
            if mode == "Reference":
                self.refq.append([r.obj for r in stored])
                return lst            # LoadingVars leaves a Reference list alone; it is replaced in ResolvingCrossRefs
            return [copy.deepcopy(x) for x in stored]
        if self.mode == RESOLVING and mode == "Reference":
            got = self.refq.pop(0)
            return None if got is None else list(got)
        return lst                    # Value / Deep: nothing in the later passes

    def look_dict(self, st, c):
        """Look<K,V>(ref dict, label, km, vm, ref kwl, ref vwl). st: the component's fields (dict, kwl, vwl live there)."""
        d, label = st[c["field"]], c["label"]
        if self.mode == SAVING and d is None:
            self.doc[label] = "IsNull"
            return
        if self.mode == SAVING:
            self.doc[label] = "node"
        if self.mode == LOADING:
            if label not in self.doc:          # node absent: dict = null
                st[c["field"]] = None
                return
            d = st[c["field"]] = None if self.doc[label] == "IsNull" else {}
        if self.mode in (SAVING, LOADING):
            st[c["kwl"]], st[c["vwl"]] = [], []
            if self.mode == SAVING:
                for k, v in d.items():
                    st[c["kwl"]].append(k)
                    st[c["vwl"]].append(v)
        if self.mode == SAVING or d is not None:
            st[c["kwl"]] = self.look_list(st[c["kwl"]], label + "/keys", c["kmode"])
            st[c["vwl"]] = self.look_list(st[c["vwl"]], label + "/values", c["vmode"])
        if self.mode == SAVING:
            st[c["kwl"]] = st[c["vwl"]] = None
        ref = "Reference" in (c["kmode"], c["vmode"])
        if (ref and self.mode == RESOLVING) or (not ref and self.mode == LOADING):
            if d is not None:
                ks, vs = st[c["kwl"]], st[c["vwl"]]
                if ks is None or vs is None:
                    return
                for i in range(min(len(ks), len(vs))):
                    if ks[i] is not None and ks[i] not in d:
                        d[ks[i]] = vs[i]
        if self.mode == POSTLOAD:
            st[c["kwl"]] = st[c["vwl"]] = None

    def expose(self, st, calls):
        for c in calls:
            if c["kind"] == "dict":
                self.look_dict(st, c)
            else:
                st[c["field"]] = self.look_list(st[c["field"]], c["label"], c["mode"])


def populated(calls):
    """Distinct, non-overlapping content per collection, so a mix-up cannot hide behind equal data."""
    st, n = {}, 3
    for i, c in enumerate(calls):
        if c["kind"] == "dict":
            st[c["field"]] = {("cell", i, j): ("val", c["label"], j) for j in range(n)}
            st.setdefault(c["kwl"], None)
            st.setdefault(c["vwl"], None)
            n += 2                     # every dictionary a different size
        else:
            st[c["field"]] = [("zone", c["label"], j) for j in range(2)]
    return st


def round_trip(calls):
    """Save `populated(calls)`, load it into a fresh component; returns (saved, loaded) collections by field."""
    st = populated(calls)
    saved = {c["field"]: copy.deepcopy(st[c["field"]]) for c in calls}
    sc = Scribe()
    sc.mode = SAVING
    sc.expose(st, calls)
    fresh = {k: None for k in st}      # working lists start null on a new component; collections are reassigned
    for mode in (LOADING, RESOLVING, POSTLOAD):
        sc.mode = mode
        sc.expose(fresh, calls)
    return saved, {c["field"]: fresh[c["field"]] for c in calls}


def guard(calls):
    """Working lists shared by 2+ calls that meet LookMode.Reference: [(list, labels)]."""
    users = {}
    for c in calls:
        if c["kind"] == "dict":
            for wl in (c["kwl"], c["vwl"]):
                users.setdefault(wl, []).append(c)
    return [(wl, [c["label"] for c in cs]) for wl, cs in sorted(users.items())
            if len(cs) > 1 and any("Reference" in (c["kmode"], c["vmode"]) for c in cs)]


def diffs(saved, loaded):
    return sorted(f for f in saved if saved[f] != loaded[f])


def main():
    calls = parse_calls(open(COMP, encoding="utf-8").read())
    dicts = [c for c in calls if c["kind"] == "dict"]
    bad = []
    shared = sorted({c["kwl"] for c in dicts if sum(1 for o in dicts if o["kwl"] == c["kwl"]) > 1})
    print("parsed %d Scribe_Collections calls (%d dictionaries); shared key working lists: %s"
          % (len(calls), len(dicts), ", ".join(shared) or "none"))
    if len(dicts) < 2 or not shared:
        bad.append("the parse found no shared working list; the subject of this test is gone or the parser is blind")

    saved, loaded = round_trip(calls)
    if diffs(saved, loaded):
        bad.append("pass model: shipped ExposeData does not round-trip %s" % diffs(saved, loaded))
    else:
        print("pass model: every collection round-trips (%s)"
              % ", ".join("%s=%d" % (f.split(".")[-1], len(saved[f])) for f in saved))
    g = guard(calls)
    if g:
        bad.append("guard: a shared working list meets LookMode.Reference: %r" % g)
    else:
        print("guard: no shared working list meets LookMode.Reference")

    # sanity probe: the instrument must see the hazard it guards against
    probe = copy.deepcopy(calls)
    first = next(c for c in probe if c["kind"] == "dict")
    first["vmode"] = "Reference"
    ps, pl = round_trip(probe)
    if not diffs(ps, pl):
        bad.append("sanity probe: %s values as Reference still round-tripped in the model; the model cannot see the hazard"
                   % first["label"])
    elif not guard(probe):
        bad.append("sanity probe: the guard did not flag %s values as Reference" % first["label"])
    else:
        print("sanity probe: %s values as Reference corrupts %s and trips the guard" % (first["label"], diffs(ps, pl)))

    src = os.path.join(DECOMP, "Verse", "Scribe_Collections.cs")
    if os.path.exists(src):
        text = open(src, encoding="utf-8", errors="replace").read()
        missing = [l for l in ENGINE_LINES if l not in text]
        if missing:
            bad.append("engine pin: the decompiled 1.6 source no longer holds %r" % missing)
        else:
            print("engine pin: %d model lines found in %s" % (len(ENGINE_LINES), src))
    else:
        print("engine pin: unchecked (no decompiled source at %s)" % src)

    for b in bad:
        print("FAIL: " + b)
    print("PASS" if not bad else "FAIL (%d)" % len(bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
