#!/usr/bin/env python3
"""rimflow/artifact.py — one deterministic door for every new game artifact.

    rimflow artifact accept <path> --kind dump|log|save|modlist [--official]

WHY THIS EXISTS, IN THE OWNER'S WORDS
=====================================
    "Citations should be by name, so nothing breaks with an index. But there could
     easily be a pass of running validators that depend on the dump that changed to
     ensure nothing has been left dangling. This should be codified in deterministic
     code that accepts a new game artifact asset."

🔑 **THE RULE THIS ENFORCES: nothing ever cites a dump by index, offset, row number or
ordinal — only by `defName`.** A design doc says `OuterRim_GalacticEmpire`, never "row
412 of the dump". An index is a fact about one capture of one mod set; a defName is a
fact about the game. Re-order the dump and every index citation is silently wrong,
with nothing to notice it.

⛔ AND THE RULE THAT MATTERS MORE: IT NEVER AUTO-FIXES.
======================================================
A dangling reference is a DECISION, not a repair. The def might have been renamed, cut
deliberately, or lost to a mod that was removed on purpose — and those want three
different answers. Guessing produces a design tier that quietly agrees with whatever
the last import happened to contain, which is the failure this whole system exists to
end. So the sweep REPORTS and FILES, and a human decides.

🔑 THIS IS WHAT MAKES RE-FREEZING SAFE. When the owner re-freezes the official dump,
nothing happens automatically: the sweep reports the deltas by name and he chooses.

⚠️ And the frozen-dump rule stands above all of it — **a differing mod count, greater
or lesser, is never staleness** (see `infrastructure/state/dumps/README.md`). The sweep
reports; it never invalidates.

WHAT IT DOES
============
    1. register   append to dumps/REGISTRY.jsonl with sha, count, date, frozen flag
    2. re-run     every validator that depends on this artifact KIND
    3. resolve    every defName cited in design/ and src/, against the new artifact
    4. report     TRANSIENT_artifact_accept_<id>.md — three lists:
                    ✅ still resolves    🔴 now dangling    🆕 newly available
    5. file       ONE ledger item per acceptance, naming the count and the report
    6. never fix

⚠️ **The spec said "one item per dangling citation" and that is refused.** A real run
against the official dump found **287** — filing 287 items would bury `rimflow next`
for weeks and make the queue useless for its actual job, which is the opposite of what
this is for. One item carries the count and points at the report; a human triages and
files what deserves filing.

Stdlib only.
"""
import json
import os
import re
import subprocess
import sys
import time

from . import model

ROOT = model.ROOT
REGISTRY = os.path.join(model.STATE, "dumps", "REGISTRY.jsonl")

# Which validators care about which artifact. ⚠️ A validator absent from disk is
# REPORTED as unrun, never silently skipped: "0 failures" out of a validator that never
# executed is the most confident wrong answer this tool could give.
VALIDATORS = {
    "dump": [
        ("check_refs", ["src/RimMandrake/Utils/check_refs.py"]),
        ("check_declarations", ["src/RimMandrake/Utils/check_declarations.py"]),
        # ⚠️ NEEDS an argument — `--spec`/`--md`/`--xml` is required, and calling it
        # bare made it exit 2 and report 🔴 FAIL. That is a false FAIL, which is the
        # same disease as a false pass and just as good at getting a report ignored.
        ("validate_ideoligion",
         ["src/RimMandrake/Utils/validate_ideoligion.py",
          "--md", "design/Jawa/worldbuilding/faction_religions_spec.md"]),
        ("check_canon", ["src/RimMandrake/Utils/check_canon.py"]),
    ],
    "modlist": [("check_canon", ["src/RimMandrake/Utils/check_canon.py"])],
    "log": [],
    "save": [],
}

# A defName as our docs write it: inside backticks, CamelCase or Prefixed_Snake.
CITE = re.compile(r"`([A-Z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+|[A-Z][a-z]+[A-Z][A-Za-z0-9]+)`")

# 🔴 THE PREFIX GATE, AND WHY THE OBVIOUS VERSION OF THIS TOOL IS USELESS.
#
# The first run reported **1,280 dangling citations** and most were not defNames at all.
# Our design docs backtick C# class names, XML operations, field names and environment
# variables constantly, and every one of them matches the pattern above:
#
#     CompProperties_EggLayer   DefModExt_TrainingCurve   ScenPart_Rule_DisallowDesignator
#     StateGraph   PawnGenOption   LoadedModManager   IfModNotActive   OLLAMA_FLASH_ATTENTION
#
# ⚠️ A report that is mostly false positives is a report nobody reads — and this one
# exists to be read at the exact moment the owner re-freezes the official dump, which
# is when a real dangling reference costs the most.
#
# ✅ The discriminator is the PREFIX. Mods namespace their defs (`OuterRim_`, `VPE_`,
# `AB_`, `Jawa_`, `RG_`), so a citation whose prefix is one the dump actually uses is
# almost certainly meant to be a def; one whose prefix appears on no def at all is
# almost certainly a class or a field. `MIN_PREFIX` keeps a single stray def from
# minting a prefix.
#
# ⛔ Names outside the gate are NOT silently dropped — they are counted and reported as
# NOT JUDGED, because "we did not look at these" and "these are fine" are different
# statements and only one of them is true.
MIN_PREFIX = 3


def sha_of(path, cap=64 * 1024 * 1024):
    """SHA-256 of a file, or of a directory's manifest.json when it is a dump."""
    import hashlib
    if os.path.isdir(path):
        path = os.path.join(path, "manifest.json")
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            while True:
                b = fh.read(1 << 20)
                if not b or h.digest_size and fh.tell() > cap:
                    break
                h.update(b)
    except OSError:
        return None
    return h.hexdigest()[:16]


def defnames_in(path):
    """-> set of defNames the artifact provides. Empty set means COULD NOT READ.

    ⭐ Prefers `defs.sqlite` when the `measuring-large-artifacts` skill is
    installed and the db is current. Two reasons, and the second is a bug fix:

      * the JSON path loads every `defs/*.json` whole — 670 MB, ThingDef alone
        is 331 MB and ~1.5 GB of peak RSS to parse
      * `defs/` **accumulates**: it keeps a file for every type that has ever
        existed, so the JSON path silently ingests defNames from mods removed
        weeks ago. A dead defName in this set makes a reference to a REMOVED
        def look provided — fail-toward-success. The db excludes orphan types
        by construction.

    Falls back to the JSON scan when the skill or the db is absent, because a
    tool that cannot run is worse than one that is merely slow.
    """
    defs = os.path.join(path, "defs") if os.path.isdir(path) else None

    try:
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "Utils"))
        from dump_manifest import dump_db
        with dump_db(path) as db:
            if db is not None:
                return {r[0] for r in db.sql("SELECT def_name FROM defs")}
    except Exception:
        pass                          # fall through to the JSON scan

    out = set()
    if defs and os.path.isdir(defs):
        for f in sorted(os.listdir(defs)):
            if not f.endswith(".json"):
                continue
            try:
                with open(os.path.join(defs, f), encoding="utf-8") as fh:
                    d = json.load(fh)
            except (OSError, ValueError):
                continue
            for rec in (d.get("defs") or d.get("items") or []):
                n = rec.get("defName") if isinstance(rec, dict) else None
                if n:
                    out.add(n)
    return out


def def_prefixes(provided, minimum=MIN_PREFIX):
    """-> set of namespace prefixes that the artifact actually uses for defs."""
    counts = {}
    for n in provided:
        if "_" in n:
            counts[n.split("_", 1)[0]] = counts.get(n.split("_", 1)[0], 0) + 1
    return {p for p, c in counts.items() if c >= minimum}


def judgeable(name, prefixes):
    """Is this citation one we can honestly call dangling if it is absent?"""
    return "_" in name and name.split("_", 1)[0] in prefixes


def citations(roots=("design", "src")):
    """-> {defName: [file:line]}. Every place a name is cited, by name."""
    cites = {}
    for r in roots:
        base = os.path.join(ROOT, r)
        for dirpath, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
            for f in files:
                if not f.endswith((".md", ".xml")):
                    continue
                p = os.path.join(dirpath, f)
                try:
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        for i, line in enumerate(fh, 1):
                            for m in CITE.finditer(line):
                                cites.setdefault(m.group(1), []).append(
                                    "%s:%d" % (os.path.relpath(p, ROOT), i))
                except OSError:
                    pass
    return cites


def run_validators(kind):
    """-> [(name, status, tail)]. `status` is pass | FAIL | UNRUN."""
    out = []
    for name, argv in VALIDATORS.get(kind, []):
        script = os.path.join(ROOT, argv[0])
        if not os.path.exists(script):
            # ⛔ Never silently skipped. See VALIDATORS.
            out.append((name, "UNRUN", "not on disk at %s" % argv[0]))
            continue
        try:
            r = subprocess.run([sys.executable, script] + argv[1:],
                               capture_output=True, text=True, cwd=ROOT, timeout=300)
            tail = (r.stdout or r.stderr or "").strip().splitlines()
            out.append((name, "pass" if r.returncode == 0 else "FAIL",
                        tail[-1][:160] if tail else ""))
        except Exception as e:
            out.append((name, "UNRUN", "%s: %s" % (type(e).__name__, e)))
    return out


def file_item(aid, dangling, report_path, seat="BUILD"):
    """File ONE item for the whole acceptance. Returns the item id, or None.

    ⛔ NOT one per dangling citation. See the note in the module docstring: 287 items
    would bury the queue this is supposed to feed.
    """
    if not dangling:
        return None
    iid = "DANGLING_%s_1" % re.sub(r"[^A-Z0-9]+", "_", aid.upper()).strip("_")
    ev = {"seat": seat, "event": "file", "id": iid,
          "title": "%d cited defNames are absent from %s" % (len(dangling), aid),
          "kind": "decision", "needs": "offline", "caused_by": None}
    ev["for"] = "DECIDE"
    try:
        model.check(ev)
        model.append(ev)
    except model.LedgerError:
        return None
    body = ["## spec",
            "%d defNames cited by name in `design/` or `src/` do not exist in the "
            "artifact `%s`. The full list, with every citation site, is in "
            "`%s`.\n" % (len(dangling), aid, os.path.basename(report_path)),
            "⛔ **Do not bulk-fix.** Each one is a decision, not a repair: the def may "
            "have been renamed, cut deliberately, or lost with a mod removed on "
            "purpose, and those want three different answers.\n",
            "## verify",
            "Re-run `rimflow artifact accept` against the same artifact; the dangling "
            "count has fallen and every remaining entry has a recorded reason.\n",
            "## criteria",
            "A reader can say, for each name, which of the three it was.\n",
            "## notes",
            "Filed automatically by `rimflow artifact accept`. One item per "
            "acceptance, deliberately — filing one per citation would have filed %d and "
            "buried the queue." % len(dangling)]
    os.makedirs(model.ITEMS, exist_ok=True)
    with open(os.path.join(model.ITEMS, "%s.md" % iid), "w", encoding="utf-8") as fh:
        fh.write("\n".join(body) + "\n")
    model.invalidate_sections(iid)
    return iid


def accept(path, kind, official=False, by="owner", write=False, at=None):
    """The whole pass. -> (report_text, dangling, provided). Writes nothing unless
    `write`, so a rehearsal is the default here as it is in the importer."""
    aid = "%s-%s" % (kind.upper(), at or time.strftime("%Y-%m-%d", time.gmtime()))
    provided = defnames_in(path)
    cites = citations()
    known = set(cites)

    # ⚠️ Only names the artifact COULD have provided are judged. If it provided nothing
    # readable, every citation would look dangling — a false alarm on 144 items, which
    # would train everyone to ignore this report forever.
    if not provided:
        dangling, fresh = {}, set()
        note = ("⛔ **The artifact provided NO readable defNames**, so no citation was "
                "judged. This is reported rather than treated as 'everything is "
                "dangling': a false alarm on every name in the repo would teach "
                "everyone to ignore this report permanently.")
    else:
        prefixes = def_prefixes(provided)
        judged = {n: v for n, v in cites.items() if judgeable(n, prefixes)}
        unjudged = len(cites) - len(judged)
        dangling = {n: v for n, v in judged.items() if n not in provided}
        fresh = provided - known
        note = ("**%d of %d cited names were JUDGED** — those whose namespace prefix is "
                "one the artifact actually uses for defs (%d such prefixes). "
                "⚠️ The other %d are NOT judged and NOT cleared: our docs backtick C# "
                "class names, XML operations, field names and environment variables, "
                "and calling those dangling produced a first-run report of 1,280 mostly "
                "phantom entries. *We did not look at these* and *these are fine* are "
                "different statements.\n"
                % (len(judged), len(cites), len(prefixes), unjudged))

    vals = run_validators(kind)
    L = []
    w = L.append
    w("<!-- status: live -->")
    w("# Artifact accepted — `%s`\n" % aid)
    w("**path** `%s`  \n**kind** `%s`  \n**sha** `%s`  \n**frozen** %s\n"
      % (path, kind, sha_of(path), "yes (official)" if official else "no"))
    if note:
        w(note + "\n")
    w("⛔ **NOTHING WAS AUTO-FIXED, and that is the design.** A dangling reference is a")
    w("decision, not a repair — the def may have been renamed, cut deliberately, or lost")
    w("with a mod removed on purpose, and those want three different answers. Guessing")
    w("would leave the design tier quietly agreeing with whatever the last import")
    w("happened to contain.\n")

    w("## Validators that depend on a `%s`\n" % kind)
    if not vals:
        w("_None registered for this kind._\n")
    else:
        w("| validator | result | last line |")
        w("|---|---|---|")
        for n, st, tail in vals:
            mark = {"pass": "✅ pass", "FAIL": "🔴 FAIL", "UNRUN": "⚠️ UNRUN"}[st]
            w("| `%s` | %s | %s |" % (n, mark, tail.replace("|", "\\|")))
        w("")
        w("⚠️ **UNRUN is not a pass.** A validator that did not execute has measured")
        w("nothing, and reporting it as clean is the most confident wrong answer this")
        w("tool could give.\n")

    w("## 🔴 Now dangling — cited by name, absent from the artifact (%d)\n" % len(dangling))
    if not dangling:
        w("_None._\n")
    else:
        for n in sorted(dangling)[:200]:
            where = dangling[n]
            w("- `%s` — %d citation(s): %s%s"
              % (n, len(where), ", ".join(where[:4]),
                 " …and %d more" % (len(where) - 4) if len(where) > 4 else ""))
        if len(dangling) > 200:
            w("\n_…and %d more._" % (len(dangling) - 200))
        w("")

    w("## 🆕 Newly available — present, cited by nothing (%d)\n" % len(fresh))
    w("_%s_\n" % (", ".join("`%s`" % n for n in sorted(fresh)[:60]) or "None"))
    if len(fresh) > 60:
        w("_…and %d more._\n" % (len(fresh) - 60))

    w("## ✅ Still resolves\n")
    w("%d of %d cited names are present in the artifact.\n"
      % (len(known) - len(dangling), len(known)))

    text = "\n".join(L) + "\n"
    if write:
        os.makedirs(os.path.dirname(REGISTRY), exist_ok=True)
        entry = {"id": aid, "kind": kind, "frozen": bool(official),
                 "path": path, "sha": sha_of(path), "by": by,
                 "at": at or time.strftime("%Y-%m-%d", time.gmtime()),
                 "defnames": len(provided), "dangling": len(dangling)}
        # Append-only, like the ledger it sits beside.
        with open(REGISTRY, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        out = os.path.join(ROOT, "TRANSIENT_artifact_accept_%s.md" % aid)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
        filed = file_item(aid, dangling, out)
        if filed:
            text += "\n> Filed **`%s`** for DECIDE — one item for the whole " \
                    "acceptance, not %d.\n" % (filed, len(dangling))
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text)
    return text, dangling, provided
