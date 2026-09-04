#!/usr/bin/env python3
r"""research_manifest_validate.py - the offline research-manifest validator.

Builds the 7 checks named in `design/Jawa/research_tree_taxonomy.md` section 4,
run BEFORE the research-normalization runtime pass ever touches a live game.
RESEARCH_VALIDATOR_BUILD_1.

    python3 src/RimMandrake/Utils/research_manifest_validate.py <manifest.csv|.json>
    python3 src/RimMandrake/Utils/research_manifest_validate.py --help

WHAT IT CHECKS, IN ORDER (taxonomy doc's own list, each with its false-pass named)
-----------------------------------------------------------------------------
  1. Orphan check       - every row resolves to a live def; a row's UNLOCKS are
                           checked against the live dump AND the Cherry Picker
                           cut list (cuts.py, never a 9th regex). Flags dead rows
                           (all unlocks cut) and WARNS on an empty unlock cache
                           unless it is on the 22-row allowlist the taxonomy doc
                           names as expected, not a bug.
  2. Prereq resolution  - no prereq (or hidden_prereq) names a project that is
                           cut, merged away, or absent from both the manifest
                           and the live dump.
  3. Band conformance   - cost inside the tier's cost band; live techLevel
                           matches the tier's techLevel mapping.
  4. One-chain-per-form - within a `form` group, the rows still alive after
                           normalization (fate keep/reflavor/untouched) must
                           form ONE prereq-connected chain, not several.
  5. Coverage           - manifest row count == live ResearchProjectDef count,
                           MEASURED off the SAME capture the manifest declares
                           it was built against (a fingerprint mismatch refuses,
                           same as the mod-set check below).
  6. Cycle check        - walks the prereq graph. Refuses to crash on the one
                           genuine vanilla self-loop already shipped
                           (`RimFridge_PowerFactorSetting` requires itself) -
                           reports it as a known quirk, not a manifest defect -
                           and FAILS on any other cycle, which the manifest
                           would have introduced.
  7. Co-writer awareness- confirms the dump being validated is the RESOLVED,
                           post-patch state (Research Reinvented rewrites
                           prereqs/techprints at load) by checking vanilla
                           `Electricity` for RR's own stamp. A dump missing the
                           stamp is raw/pre-patch XML and would produce a report
                           that fights RR at load.

🔴 READ THE LIVE DUMP, NOT MOD XML - same ruling as weapon_tag_audit.py and
apparel_tag_audit.py (owner, 2026-08-19). This tool REFUSES to run when the
dump's mod set does not match the live `ModsConfig.xml`, same as those two.
`--anyway` downgrades that to a loud warning, same flag, same meaning.

`ResearchProjectDef.json` is ~4 MB for ~520 rows - nowhere near the 316 MB
`ThingDef.json` that made `dump_projection.py`'s sqlite path worth building, so
this reads the JSON directly. If that ever stops being true, project through
`dump_projection.py` instead of hand-rolling a second reader.

CUTS COME FROM `cherrypicker.py`, NEVER A NEW REGEX - the dump is captured
BEFORE Cherry Picker removes anything, so a cut research project's unlocks are
still sitting in the dump looking alive. `cherrypicker.load()` is the one
reader; this script imports it rather than reopening the settings file.

THE MANIFEST DOES NOT EXIST YET (RESEARCH_MANIFEST_DRAFT_1, a separate item) -
this validator defines the two accepted file shapes so that item has a target
to write to:

  CSV  (a single optional leading `#`-comment line, then a header row):
      # fingerprint=<16-hex> modCount=<n> capturedUtc=<iso8601>
      defName,source_mod,fate,tab,tier,cost,prereqs,hidden_prereqs,source_gate,form,theology,merge_target,note
      Foo,SomeMod,keep,Armory,T2,2400,Bar;Baz,,,blaster,drip,,
    `prereqs`/`hidden_prereqs` are `;`-separated defNames; empty means none.
    `fate` in {keep, cut, merge, reflavor, untouched}, per taxonomy section 3.

  JSON (one object, `meta` optional but the same fingerprint fields):
      {"meta": {"fingerprint": "...", "modCount": 586, "capturedUtc": "..."},
       "rows": [{"defName": "Foo", "source_mod": "SomeMod", "fate": "keep",
                 "tab": "Armory", "tier": "T2", "cost": 2400,
                 "prereqs": ["Bar", "Baz"], "hidden_prereqs": [],
                 "source_gate": "", "form": "blaster", "theology": "drip",
                 "merge_target": "", "note": ""}]}

The leading `# fingerprint=...` / `meta.fingerprint` line is how check 5 proves
BOTH sides (manifest, dump) describe the same mod set - never mix a stale dump
with a fresh manifest. Missing it downgrades that half of check 5 to a WARN,
because there is nothing to compare it against, not because it is fine.

ASSUMPTIONS MADE WHERE THE DOC DOES NOT SPELL OUT A NUMBER (flagged here and in
the build's report; change them in `TIER_COST_BANDS` / `TIER_TECHLEVELS` /
`EMPTY_CACHE_ALLOWLIST_*` below, nowhere else):

  * Cost bands are the owner's 2026-08-31 ruling (taxonomy section 7) verbatim:
    T0 <=600 / T1 600-1600 / T2 1600-3000 / T3 3000-5000 / T4 5000+. The T0/T1
    seam at exactly 600 is put on the T0 side (`<= 600`); nothing in the doc
    says which side owns the boundary.
  * techLevel mapping: T0 -> {Neolithic, Medieval, Industrial} ("Neolithic-early
    Industrial"), T1 -> {Industrial}, T2 -> {Industrial} ("late Industrial" is
    not a distinct vanilla enum value, so T1 and T2 share the same allowed set
    and are told apart by cost band only), T3 -> {Spacer}, T4 -> {Ultra,
    Archotech}.
  * The 22-row empty-cache allowlist: `research_tree_prep.md` section 1 names
    10 explicit defNames plus a 10-row `DP_RGive*` pattern (20 total) and says
    "etc." for the rest. The remaining ~2 are not enumerable from any doc this
    tool could find. Anything empty-cache and NOT on the 20-name list gets a
    WARN, never a silent pass - the doc's own "lies by trusting an empty
    cache" is exactly the failure mode a silent allowlist-everything would
    reintroduce.
  * Half-orphans (Mortars-class: a shell unlock surviving next to a cut
    turret) are NOT auto-detected. That needs cross-referencing what consumes
    each surviving unlock (ammo -> turret, recipe -> product), which is
    genuinely bespoke per unlock category. This tool instead WARNs on every
    PARTIAL cut (some but not all unlocks cut) so a human can look, and says so.
  * A prereq naming a `fate: merge` project is treated the same as naming a
    `fate: cut` one (FAIL) - the doc does not say whether a merged project's
    defName is expected to keep functioning as a research node afterward, and
    treating it as gone is the safer of the two readings.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from game_paths import DEF_DUMP, MODS_CONFIG          # noqa: E402
import cherrypicker                                    # noqa: E402
import refresh                                          # noqa: E402

DUMP = Path(DEF_DUMP)
FATES = {"keep", "cut", "merge", "reflavor", "untouched"}
SURVIVING_FATES = {"keep", "reflavor", "untouched"}     # still a live tree node

# --- section 2 + section 7 of the taxonomy doc, made concrete -----------
TIER_TECHLEVELS = {
    # "Animal" is VFE Tribals' own C#-added era below Neolithic; its code stamps
    # the value post-load, so no XML patch can override it (measured 2026-09-04:
    # the retag's replace-or-add ops applied and the live value stayed Animal).
    # T0 is the floor tier, so pre-Neolithic belongs in it.
    "T0": {"Animal", "Neolithic", "Medieval", "Industrial"},
    "T1": {"Industrial"},
    "T2": {"Industrial"},
    "T3": {"Spacer"},
    "T4": {"Ultra", "Archotech"},
}
# (lo, hi): lo is EXCLUSIVE except T0 (0..hi inclusive), hi is INCLUSIVE except
# T4 (lo exclusive, no ceiling). See the docstring's "ASSUMPTIONS" for the seam.
TIER_COST_BANDS = {
    "T0": (0, 600),
    "T1": (600, 1600),
    "T2": (1600, 3000),
    "T3": (3000, 5000),
    "T4": (5000, None),
}

# research_tree_prep.md section 1, "22 more empty-cache rows, confirmed alive" -
# the 10 it names outright plus the 10-row DP_RGive* pattern it names as a group.
# See the module docstring: the remaining ~2 are the doc's own "etc." and are
# deliberately NOT here.
EMPTY_CACHE_ALLOWLIST = {
    "Bioregeneration", "Archogenetics", "BlissLobotomy", "GhoulInfusion",
    "ComplexClothing", "VFET_Mining", "ResearchDrillTurretEfficientDrilling",
    "RimFridge_PowerFactorSetting", "VFEP_WarcasketRemoval",
    "OuterRim_DroidEnergySys",
    # +8 verified 2026-09-04 (prep doc section 1, "+8 more"): prereq hubs,
    # stat/hyperlink/C#-mechanism rows, and the three MM ship rows reflavored
    # into The Utinni (empty caches by design, alive by ruling).
    "RR_BasicFoodPrep", "RR_LateralThinking",
    "ResearchMobileMineralSonarEnhancedScan", "ScuttlebugsBiology",
    "RimAI_Subspace_Gravitic_Penetration",
    "MM_Research_AncientShipDesigns", "MM_Research_CWShipDesigns",
    "MM_Research_EmpireShipDesigns",
}
EMPTY_CACHE_ALLOWLIST_PREFIXES = ("DP_RGive",)

# The one genuine vanilla self-loop the taxonomy doc names by defName -
# reported, never treated as a manifest-introduced defect.
KNOWN_SELF_LOOP = "RimFridge_PowerFactorSetting"

FAIL, WARN, INFO = "FAIL", "WARN", "INFO"


class Issue:
    __slots__ = ("level", "check", "defname", "msg")

    def __init__(self, level, check, defname, msg):
        self.level, self.check, self.defname, self.msg = level, check, defname, msg

    def line(self):
        who = ("[%s] " % self.defname) if self.defname else ""
        return "   %-4s %s%s" % (self.level, who, self.msg)


# --------------------------------------------------------------------- dump

def load_research_dump(dump=DUMP):
    """{defName: fields} for every live ResearchProjectDef, and the raw list."""
    p = dump / "defs" / "ResearchProjectDef.json"
    if not p.is_file():
        sys.exit("no ResearchProjectDef.json at %s - the game must write a dump first" % p)
    data = json.loads(p.read_text(encoding="utf-8"))["defs"]
    index = {d["defName"]: d.get("fields") or {} for d in data}
    return index, data


def check_modlist(man_path, anyway):
    """🔴 Same proviso as weapon_tag_audit.py / apparel_tag_audit.py: a dump from
    a different mod set describes a different game, so every check below would
    quietly be about a game nobody is running."""
    man = json.loads(Path(man_path).read_text(encoding="utf-8"))
    try:
        live = {li.text.strip().lower() for li in ET.parse(MODS_CONFIG).getroot()
                .find("activeMods") if li.text}
    except Exception as e:
        print("!! cannot read ModsConfig.xml (%s) - cannot verify the dump matches" % e)
        return man, None
    n = man.get("modCount")
    if n != len(live):
        msg = ("dump modCount %s != %d active mods in ModsConfig.xml.\n"
               "   The dump describes a DIFFERENT mod set, so every check below would be\n"
               "   about a game you are not running. Regenerate the dump under the list you\n"
               "   intend to ship, or pass --anyway to see the report as PROVISIONAL."
               % (n, len(live)))
        if not anyway:
            sys.exit("REFUSING: " + msg)
        print("⚠️  PROVISIONAL: " + msg + "\n")
    else:
        print("dump matches the live list: %d mods, captured %s"
              % (n, man.get("capturedUtc", "?")))
    # `live` above IS this same set, from the same parse of the same file - a second
    # ET.parse(MODS_CONFIG) here reread and rebuilt it for no reason.
    return man, live


# ---------------------------------------------------------------- manifest

_REQUIRED_COLS = ("defName", "source_mod", "fate", "tab", "tier", "cost")
_LIST_COLS = ("prereqs", "hidden_prereqs")
_ALL_COLS = ("defName", "source_mod", "fate", "tab", "tier", "cost", "prereqs",
             "hidden_prereqs", "source_gate", "form", "theology",
             "merge_target", "note",
             # schema v2 (canon_reintegration_plan.md F2, 2026-09-04):
             "access", "holder", "stage_gate", "live")


def _normalize_row(raw, list_sep=";"):
    r = {k: raw.get(k, "") for k in _ALL_COLS}
    for k in _LIST_COLS:
        v = raw.get(k) or []
        if isinstance(v, str):
            v = [x.strip() for x in v.split(list_sep) if x.strip()]
        r[k] = list(v)
    cost = raw.get("cost")
    try:
        r["cost"] = int(cost) if cost not in (None, "") else None
    except (TypeError, ValueError):
        r["cost"] = None
    r["fate"] = (raw.get("fate") or "").strip()
    # schema v2: rows for defs not yet in the live game (a deployed mod pending
    # its restart, or a planned-but-unauthored def) declare it. Default "yes"
    # keeps every v1 manifest and fixture behaving unchanged.
    r["live"] = (raw.get("live") or "yes").strip() or "yes"
    r["tier"] = (raw.get("tier") or "").strip().upper()
    r["defName"] = (raw.get("defName") or "").strip()
    return r


def load_manifest(path):
    """-> (rows, meta). `meta` carries the declared source-capture fingerprint,
    or {} when the manifest does not declare one (check 5 downgrades to a WARN)."""
    p = Path(path)
    meta = {}
    if p.suffix.lower() == ".json":
        doc = json.loads(p.read_text(encoding="utf-8"))
        meta = doc.get("meta") or {}
        rows = [_normalize_row(r) for r in doc.get("rows", [])]
        return rows, meta
    # CSV: one optional leading "# key=val key=val" comment line, then the header.
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].lstrip().startswith("#"):
        for tok in lines[0].lstrip("#").split():
            if "=" in tok:
                k, _, v = tok.partition("=")
                meta[k.strip()] = v.strip()
        body = "\n".join(lines[1:])
    else:
        body = text
    reader = csv.DictReader(io.StringIO(body))
    missing = [c for c in _REQUIRED_COLS if c not in (reader.fieldnames or [])]
    if missing:
        sys.exit("manifest CSV is missing required column(s): %s" % ", ".join(missing))
    rows = [_normalize_row(r) for r in reader]
    return rows, meta


def validate_shape(rows):
    """Structural sanity that has to hold before any of the 7 checks can run."""
    issues = []
    seen = {}
    for r in rows:
        if not r["defName"]:
            issues.append(Issue(FAIL, "shape", None, "row with no defName"))
            continue
        if r["defName"] in seen:
            issues.append(Issue(FAIL, "shape", r["defName"],
                                 "duplicate manifest row (defName appears twice)"))
        seen[r["defName"]] = r
        if r["fate"] not in FATES:
            issues.append(Issue(FAIL, "shape", r["defName"],
                                 "fate '%s' is not one of %s" % (r["fate"], sorted(FATES))))
        if r["fate"] != "cut" and r["tier"] not in TIER_COST_BANDS:
            issues.append(Issue(FAIL, "shape", r["defName"],
                                 "tier '%s' is not one of %s" % (r["tier"], sorted(TIER_COST_BANDS))))
    return issues


# --------------------------------------------------------------- check 1

def check_orphans(rows, live, cuts):
    issues = []
    by_name = {r["defName"]: r for r in rows}
    for r in rows:
        if r.get("live", "yes") != "yes":
            continue          # not in the running game yet; coverage INFO-lists it
        dn = r["defName"]
        exists = dn in live
        # 🔴 TYPED, not cut_name(): the row's type is KNOWN here, and the
        # any-type match reported ThingDef/GravForge as a cut RESEARCH project
        # twice (RESEARCH_MANIFEST_DRAFT_1 item 1, and again 2026-09-04).
        # cut_name() stays correct below for unlocks, whose types are unknown.
        cut_as_def = cuts.cut("ResearchProjectDef", dn)
        if r["fate"] == "merge":
            # A merge donor DIES into its target at execution (migration rule 4:
            # the cut wave removes it via Cherry Picker). Absent-and-cut is the
            # executed state, not a dead reference; the target's own liveness is
            # checked below. Present-and-uncut just means pre-execution.
            if not exists and cut_as_def:
                issues.append(Issue(INFO, "orphan", dn,
                                     "merge donor executed: absent from the live game and "
                                     "on the cut list, died into '%s'" % r["merge_target"]))
            elif not exists:
                issues.append(Issue(FAIL, "orphan", dn,
                                     "merge donor is absent from the live game but NOT on "
                                     "the cut list - it vanished by some other route"))
        elif r["fate"] != "cut":
            if not exists:
                issues.append(Issue(FAIL, "orphan", dn,
                                     "manifest row does not resolve to any live "
                                     "ResearchProjectDef, and fate is '%s' not 'cut' - "
                                     "dead reference (taxonomy contract 1: every row "
                                     "must resolve to a live def)" % r["fate"]))
                continue
            if cut_as_def:
                issues.append(Issue(FAIL, "orphan", dn,
                                     "the PROJECT ITSELF is on the Cherry Picker cut "
                                     "list, but manifest fate is '%s' not 'cut'" % r["fate"]))
        if r["fate"] in SURVIVING_FATES and exists:
            cache = live[dn].get("cachedUnlockedDefs") or []
            if not cache:
                allowed = dn in EMPTY_CACHE_ALLOWLIST or dn.startswith(EMPTY_CACHE_ALLOWLIST_PREFIXES)
                if not allowed:
                    issues.append(Issue(WARN, "orphan", dn,
                                         "empty unlock cache and NOT on the confirmed-alive "
                                         "allowlist - cachedUnlockedDefs misses mechanism-only "
                                         "unlocks (biosculpter cycles, surgery ops, quest "
                                         "starts); verify by hand against description + "
                                         "descriptionHyperlinks before trusting this row"))
            else:
                live_unlocks = [u for u in cache if not cuts.cut_name(u)]
                cut_ct = len(cache) - len(live_unlocks)
                if not live_unlocks:
                    issues.append(Issue(FAIL, "orphan", dn,
                                         "DEAD: all %d unlock(s) are on the cut list (%s)"
                                         % (len(cache), ", ".join(cache[:6]))))
                elif cut_ct:
                    issues.append(Issue(WARN, "orphan", dn,
                                         "partial-cut: %d of %d unlocks cut - check by hand "
                                         "for a Mortars-class half-orphan (a surviving unlock "
                                         "with nothing left to use it); this validator cannot "
                                         "cross-reference ammo/fixture relationships"
                                         % (cut_ct, len(cache))))
        if r["fate"] == "merge":
            mt = r["merge_target"]
            if not mt:
                issues.append(Issue(FAIL, "orphan", dn,
                                     "fate=merge with no merge_target - the loser's unlocks "
                                     "would be orphaned by our own normalization (migration "
                                     "rule 4)"))
            elif mt in by_name and by_name[mt]["fate"] not in SURVIVING_FATES:
                issues.append(Issue(FAIL, "orphan", dn,
                                     "merge_target '%s' is itself fate='%s' - not a valid "
                                     "survivor to re-point unlocks onto" % (mt, by_name[mt]["fate"])))
            elif mt not in by_name and (mt not in live or cuts.cut_name(mt)):
                issues.append(Issue(FAIL, "orphan", dn,
                                     "merge_target '%s' is absent from the manifest and not "
                                     "a live, uncut def either" % mt))
    return issues


# --------------------------------------------------------------- check 2

def check_prereqs(rows, live, cuts):
    issues = []
    by_name = {r["defName"]: r for r in rows}
    for r in rows:
        if r["fate"] == "cut":
            continue
        for col in ("prereqs", "hidden_prereqs"):
            for p in r[col]:
                if p in by_name:
                    pf = by_name[p]["fate"]
                    if pf == "cut":
                        issues.append(Issue(FAIL, "prereq", r["defName"],
                                             "%s '%s' is marked fate=cut in the manifest"
                                             % (col, p)))
                    elif pf == "merge":
                        issues.append(Issue(FAIL, "prereq", r["defName"],
                                             "%s '%s' is marked fate=merge (dissolves into "
                                             "'%s') - repoint onto the survivor"
                                             % (col, p, by_name[p]["merge_target"] or "?")))
                elif p in live:
                    if cuts.cut_name(p):
                        issues.append(Issue(FAIL, "prereq", r["defName"],
                                             "%s '%s' has no manifest row AND is on the "
                                             "Cherry Picker cut list" % (col, p)))
                    else:
                        issues.append(Issue(WARN, "prereq", r["defName"],
                                             "%s '%s' has no manifest row of its own - "
                                             "coverage gap (every live ResearchProjectDef "
                                             "needs a row, taxonomy section 3)" % (col, p)))
                else:
                    issues.append(Issue(FAIL, "prereq", r["defName"],
                                         "%s '%s' is neither a manifest row nor a live def "
                                         "- absent project" % (col, p)))
    return issues


# --------------------------------------------------------------- check 3

def _band_ok(tier, cost):
    lo, hi = TIER_COST_BANDS[tier]
    if cost is None:
        return False
    if tier == "T0":
        return 0 <= cost <= hi
    if hi is None:
        return cost > lo
    return lo < cost <= hi


def _band_desc(tier):
    lo, hi = TIER_COST_BANDS[tier]
    return ("<= %d" % hi) if tier == "T0" else ("> %d" % lo) if hi is None else "%d-%d" % (lo, hi)


def check_bands(rows, live):
    issues = []
    for r in rows:
        if r["fate"] == "cut" or r["tier"] not in TIER_COST_BANDS:
            continue
        dn, tier, cost = r["defName"], r["tier"], r["cost"]
        if not _band_ok(tier, cost):
            issues.append(Issue(FAIL, "band", dn,
                                 "cost %s is outside %s's band (%s)"
                                 % (cost if cost is not None else "?", tier, _band_desc(tier))))
        fields = live.get(dn)
        if fields is None:
            issues.append(Issue(INFO, "band", dn,
                                 "techLevel not checked - row does not resolve to a live "
                                 "def (see orphan check)"))
            continue
        tl = fields.get("techLevel")
        allowed = TIER_TECHLEVELS[tier]
        if tl not in allowed:
            issues.append(Issue(FAIL, "band", dn,
                                 "live techLevel '%s' is not in %s's mapping %s"
                                 % (tl, tier, sorted(allowed))))
    return issues


# --------------------------------------------------------------- check 4

def check_one_chain_per_form(rows):
    issues = []
    by_form = {}
    for r in rows:
        if r["fate"] in SURVIVING_FATES and r["form"]:
            by_form.setdefault(r["form"], []).append(r)
    for form, members in by_form.items():
        names = {r["defName"] for r in members}
        by_name = {r["defName"]: r for r in members}
        parent = {n: n for n in names}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for r in members:
            for col in ("prereqs", "hidden_prereqs"):
                for p in r[col]:
                    if p in names:
                        union(r["defName"], p)
        components = {}
        for n in names:
            components.setdefault(find(n), []).append(n)
        if len(components) > 1:
            chains = sorted((sorted(v) for v in components.values()), key=lambda v: v[0])
            issues.append(Issue(FAIL, "one-chain-per-form", None,
                                 "form '%s' retains %d separate research chains after "
                                 "normalization (one survivor chain per form is required): %s"
                                 % (form, len(chains),
                                    "  |  ".join(", ".join(c) for c in chains))))
    return issues


# --------------------------------------------------------------- check 5

def check_coverage(rows, live, manifest_meta, dump_fp):
    issues = []
    pending = [r for r in rows if r.get("live", "yes") != "yes"]
    for r in pending:
        issues.append(Issue(INFO, "coverage", r["defName"],
                             "excluded from the coverage equality: live=%s "
                             "(a def the dump cannot hold yet)" % r["live"]))
    rows = [r for r in rows if r.get("live", "yes") == "yes"]
    # Two-sided, execution-aware (2026-09-04, post cut wave): rows whose fate
    # is cut/merge are EXPECTED ABSENT; surviving rows are EXPECTED PRESENT.
    # Equality of raw counts stopped meaning coverage the moment the cut wave
    # shipped - a cut row still live, or a survivor missing, is what a
    # coverage failure actually is.
    expect_present = [r for r in rows if r["fate"] in SURVIVING_FATES]
    expect_absent = [r for r in rows if r["fate"] in ("cut", "merge")]
    missing = [r["defName"] for r in expect_present if r["defName"] not in live]
    lingering = [r["defName"] for r in expect_absent if r["defName"] in live]
    unmapped = [n for n in live
                if n not in {r["defName"] for r in rows}
                and not any(p.get("defName") == n for p in pending)]
    for n in missing[:15]:
        issues.append(Issue(FAIL, "coverage", n,
                             "surviving manifest row is ABSENT from the live game"))
    for n in lingering[:15]:
        issues.append(Issue(FAIL, "coverage", n,
                             "fate=%s row is STILL LIVE - the cut wave missed it"
                             % next(r["fate"] for r in expect_absent if r["defName"] == n)))
    for n in unmapped[:15]:
        issues.append(Issue(FAIL, "coverage", n,
                             "live ResearchProjectDef has NO manifest row - coverage must "
                             "be EXACT ('untouched' is a legal fate but must be WRITTEN; "
                             "absent is not legal)"))
    if not (missing or lingering or unmapped):
        issues.append(Issue(INFO, "coverage", None,
                             "coverage exact: %d surviving rows all present, %d cut/merge "
                             "rows all absent, %d live defs all mapped"
                             % (len(expect_present), len(expect_absent), len(live))))
    mf = manifest_meta.get("fingerprint")
    if not mf:
        issues.append(Issue(WARN, "coverage", None,
                             "manifest does not declare the capture fingerprint it was built "
                             "against ('# fingerprint=...' / meta.fingerprint) - coverage "
                             "cannot be proven to be against the SAME capture as this dump"))
    elif mf != dump_fp.get("hash"):
        issues.append(Issue(FAIL, "coverage", None,
                             "manifest declares fingerprint %s, live dump is %s (modCount "
                             "%s vs %s) - comparing two different mod-set captures"
                             % (mf, dump_fp.get("hash"), manifest_meta.get("modCount"),
                                dump_fp.get("modCount"))))
    else:
        issues.append(Issue(INFO, "coverage", None,
                             "fingerprint verified: manifest and live dump agree (%s, %s mods)"
                             % (mf, dump_fp.get("modCount"))))
    return issues


# --------------------------------------------------------------- check 6

def check_cycles(rows):
    graph = {r["defName"]: list(r["prereqs"]) + list(r["hidden_prereqs"])
             for r in rows if r["fate"] != "cut"}
    return _cycle_issues(graph)


def _cycle_issues(graph):
    issues = []
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    reported = set()

    def dfs(node, stack):
        color[node] = GRAY
        stack.append(node)
        for nxt in graph.get(node, []):
            if nxt not in graph:
                continue
            c = color.get(nxt, WHITE)
            if c == WHITE:
                dfs(nxt, stack)
            elif c == GRAY:
                idx = stack.index(nxt)
                cyc = tuple(stack[idx:])
                key = frozenset(cyc)
                if key not in reported:
                    reported.add(key)
                    if len(cyc) == 1 and cyc[0] == KNOWN_SELF_LOOP:
                        issues.append(Issue(INFO, "cycle", cyc[0],
                                             "known vanilla self-loop (requires itself) - "
                                             "documented in research_tree_taxonomy.md section "
                                             "4, reported, not treated as a manifest defect"))
                    else:
                        issues.append(Issue(FAIL, "cycle", None,
                                             "prereq cycle: %s" % " -> ".join(cyc + (cyc[0],))))
        stack.pop()
        color[node] = BLACK

    for n in list(graph):
        if color[n] == WHITE:
            dfs(n, [])
    return issues


# --------------------------------------------------------------- check 7

def check_resolved_dump(live, active_ids):
    issues = []
    if active_ids is None:
        issues.append(Issue(WARN, "co-writer", None,
                             "could not read ModsConfig.xml - resolved-dump signature check "
                             "skipped"))
        return issues
    if "petetimessix.researchreinvented" not in active_ids:
        issues.append(Issue(INFO, "co-writer", None,
                             "Research Reinvented is not active in the live mod list - "
                             "resolved-dump signature has nothing to confirm against"))
        return issues
    elec = live.get("Electricity")
    if elec is None:
        issues.append(Issue(WARN, "co-writer", None,
                             "vanilla 'Electricity' ResearchProjectDef not found in the dump "
                             "- cannot confirm the dump is the resolved, post-patch state"))
        return issues
    # techprintCount on vanilla projects is Configurable Techprints'
    # (com.makeitso.configurabletechprints) stamp, NOT Research Reinvented's:
    # neither RR DLL references the field (settled 2026-09-01). RR's own
    # signature is the RR_ prerequisite it splices in.
    tp = elec.get("techprintCount") or 0
    prereqs = elec.get("prerequisites") or []
    if any(str(p).startswith("RR_") for p in prereqs):
        issues.append(Issue(INFO, "co-writer", "Electricity",
                             "resolved-dump signature confirmed: prereqs=%s (RR's splice); "
                             "techprintCount=%d is Configurable Techprints', if active"
                             % (prereqs, tp)))
    else:
        issues.append(Issue(FAIL, "co-writer", "Electricity",
                             "prereqs=%s - Research Reinvented's RR_ splice is NOT visible "
                             "here. This dump looks RAW/PRE-PATCH; validating against it "
                             "would produce a report that fights RR at load "
                             "(taxonomy section 4, 'co-writer awareness')" % (prereqs,)))
    return issues


# ------------------------------------------------------------ --inventory
# No manifest exists yet for some captures (RESEARCH_MANIFEST_DRAFT_1 may be
# stale or absent). This mode runs the dump/cherrypicker-only half of the 7
# checks directly off the LIVE inventory - useful on its own, and proves the
# two readers (dump JSON, cherrypicker.py) work before any manifest exists.

def inventory_graph(live):
    """{defName: prereqs+hidden_prereqs} for EVERY live def - the cycle check
    needs no manifest, only the dump's own prerequisite fields."""
    graph = {}
    for dn, fields in live.items():
        graph[dn] = list(fields.get("prerequisites") or []) + \
                    list(fields.get("hiddenPrerequisites") or [])
    return graph


def inventory_orphans(live, cuts):
    """Orphan/half-orphan scan against the live inventory alone (no manifest
    rows to read a `fate` off of - every def is implicitly 'still in the
    tree' until a manifest says otherwise)."""
    issues = []
    for dn, fields in live.items():
        if cuts.cut_name(dn):
            issues.append(Issue(INFO, "orphan", dn,
                                 "the PROJECT ITSELF is on the Cherry Picker cut list "
                                 "(still present in the dump - dump is pre-cut)"))
            continue
        cache = fields.get("cachedUnlockedDefs") or []
        if not cache:
            allowed = dn in EMPTY_CACHE_ALLOWLIST or dn.startswith(EMPTY_CACHE_ALLOWLIST_PREFIXES)
            if not allowed:
                issues.append(Issue(WARN, "orphan", dn,
                                     "empty unlock cache and NOT on the confirmed-alive "
                                     "allowlist - verify by hand (see research_tree_prep.md "
                                     "section 1) before calling this row dead or alive"))
            continue
        live_unlocks = [u for u in cache if not cuts.cut_name(u)]
        cut_ct = len(cache) - len(live_unlocks)
        if not live_unlocks:
            issues.append(Issue(FAIL, "orphan", dn,
                                 "DEAD: all %d unlock(s) are on the cut list (%s)"
                                 % (len(cache), ", ".join(cache[:6]))))
        elif cut_ct:
            issues.append(Issue(WARN, "orphan", dn,
                                 "partial-cut: %d of %d unlocks cut - possible Mortars-class "
                                 "half-orphan, check by hand" % (cut_ct, len(cache))))
    return issues


def run_inventory(dump, cherrypicker_choice, anyway):
    """--inventory: report the live ResearchProjectDef inventory plus the
    cycle/orphan/co-writer checks that need no manifest. Always exits 0 -
    this mode is a report, not a pass/fail gate."""
    man_path = dump / "manifest.json"
    if not man_path.is_file():
        sys.exit("no manifest.json at %s - not a def-dump capture" % dump)
    man, active_ids = check_modlist(man_path, anyway)

    cuts = (cherrypicker.from_log() if cherrypicker_choice == "log"
            else cherrypicker.load(cherrypicker_choice))
    print(cuts.provenance())

    live, _ = load_research_dump(dump)
    dump_fp = refresh.dump_fingerprint(str(dump)) or {}

    print("\nMEASURED: %d live ResearchProjectDef (capture %s, %s mods, %s)"
          % (len(live), dump_fp.get("hash", "UNMEASURED"),
             dump_fp.get("modCount", man.get("modCount", "?")),
             dump_fp.get("capturedUtc", man.get("capturedUtc", "?"))))

    cycle_issues_all = _cycle_issues(inventory_graph(live))
    known_loops = [i for i in cycle_issues_all if i.level == INFO]
    cyc = report("cycle check (inventory)  ", cycle_issues_all)
    orph = report("orphan check (inventory) ", inventory_orphans(live, cuts))
    report("co-writer awareness      ", check_resolved_dump(live, active_ids))

    print("\nHEADLINE: %d ResearchProjectDef · %d cycle(s) found (%d known self-loop, "
          "%d other) · %d dead orphan(s) found from the inventory scan alone"
          % (len(live), len(cyc) + len(known_loops), len(known_loops), len(cyc), len(orph)))
    print("(no manifest was supplied - coverage/band/prereq/one-chain-per-form checks need "
          "a manifest row per def; run without --inventory once one exists)")
    return 0


# ---------------------------------------------------------------- report

CHECKS = [
    ("1  orphan check          ", None),
    ("2  prereq resolution     ", None),
    ("3  band conformance      ", None),
    ("4  one-chain-per-form    ", None),
    ("5  coverage              ", None),
    ("6  self-loop / cycle     ", None),
    ("7  co-writer awareness   ", None),
]


def report(name, issues):
    fails = [i for i in issues if i.level == FAIL]
    warns = [i for i in issues if i.level == WARN]
    infos = [i for i in issues if i.level == INFO]
    tag = "FAIL" if fails else ("WARN" if warns else "pass")
    print("\nCHECK %s [%s]  (%d fail, %d warn, %d info)"
          % (name, tag, len(fails), len(warns), len(infos)))
    for i in fails + warns + infos:
        print(i.line())
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", nargs="?", default=None,
                     help="path to the manifest .csv or .json (omit with --inventory)")
    ap.add_argument("--inventory", action="store_true",
                     help="no manifest: report the live ResearchProjectDef inventory plus "
                          "the cycle/orphan/co-writer checks that don't need one")
    ap.add_argument("--dump", default=str(DUMP), help="override the def-dump capture dir")
    ap.add_argument("--anyway", action="store_true",
                     help="report even though the dump does not match the live mod list "
                          "(or a manifest/dump fingerprint mismatch)")
    ap.add_argument("--cherrypicker", choices=("auto", "live", "ratified", "log"),
                     default="auto", help="which Cherry Picker cut list to read (default: auto)")
    a = ap.parse_args()

    dump = Path(a.dump)
    if a.inventory or a.manifest is None:
        if a.manifest is not None:
            print("(--inventory given with a manifest path - ignoring the manifest)")
        return run_inventory(dump, a.cherrypicker, a.anyway)

    man_path = dump / "manifest.json"
    if not man_path.is_file():
        sys.exit("no manifest.json at %s - not a def-dump capture" % dump)
    man, active_ids = check_modlist(man_path, a.anyway)

    cuts = (cherrypicker.from_log() if a.cherrypicker == "log"
            else cherrypicker.load(a.cherrypicker))
    print(cuts.provenance())

    live, _ = load_research_dump(dump)
    dump_fp = refresh.dump_fingerprint(str(dump)) or {}
    if not dump_fp:
        print("⚠️  could not compute a dump fingerprint (refresh.dump_fingerprint) - "
              "check 5's fingerprint half will read UNVERIFIED")

    rows, manifest_meta = load_manifest(a.manifest)
    print("manifest: %s (%d rows)" % (a.manifest, len(rows)))

    shape_issues = validate_shape(rows)
    if any(i.level == FAIL for i in shape_issues):
        report("0  manifest shape         ", shape_issues)
        sys.exit("\nREFUSING: manifest fails basic shape checks (see CHECK 0 above) - "
                 "fix these before the 7 taxonomy checks can mean anything.")

    all_fails = []
    all_fails += report("1  orphan check          ", check_orphans(rows, live, cuts))
    all_fails += report("2  prereq resolution     ", check_prereqs(rows, live, cuts))
    all_fails += report("3  band conformance      ", check_bands(rows, live))
    all_fails += report("4  one-chain-per-form    ", check_one_chain_per_form(rows))
    all_fails += report("5  coverage              ", check_coverage(rows, live, manifest_meta, dump_fp))
    all_fails += report("6  self-loop / cycle     ", check_cycles(rows))
    all_fails += report("7  co-writer awareness   ", check_resolved_dump(live, active_ids))

    print("\n%s: %d FAIL across the 7 checks%s"
          % ("FAIL" if all_fails else "PASS", len(all_fails),
             " (WARN/INFO do not block, review them anyway)" if not all_fails else ""))
    return 1 if all_fails else 0


if __name__ == "__main__":
    sys.exit(main())
