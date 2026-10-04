"""shipped_defs.py -- "every def this mod ships is live, and says what its XML says" as one reusable chain.

Many PARTIAL rows in design/RimMandrake/northstar_coverage_audit_2026-10-03.md read "N defs only sampled" or
"X of Y defs unasserted". This closes that class without a hand-kept list: it parses the mod's OWN Defs/ folder
(so a def added later is covered with no script edit) and reads every non-abstract def back through
`jawa/get_defs` (defs as ONE STRING `Type/name;Type/name`, chunked; the tool's own success/notFound/foundCount
are read, never a substring of the payload -- CLAUDE.md's get_defs trap).

Use from a validation.py:

    from modcheck import shipped_defs
    shipped_defs.add_chain(suite, __file__, fields_by_type={"RecipeDef": ("label", "workAmount")},
                           sanity=("RSW_SaltCuredRation_Meat",), min_count=20)

Two components: `every_shipped_def_is_loaded` (none in notFound; the parse found the sanity names and at least
`min_count` defs, so a blind parse cannot pass) and `shipped_scalar_fields_match_xml` (for each def, every field
in `fields_by_type[type]` -- default `label` -- that its XML authors as a plain leaf is compared to the live
value: numbers numerically, bools case-blind). A value a Patches/ operation changes on purpose will read as drift;
name it in `skip` as "DefName.field".

MayRequire / MayRequireAnyOf on a top-level def: the game drops that def when the named mod is inactive, so a
missing guarded def is not by itself a loss. Guarded defs are grouped by their guard (DLC guards --
ludeon.rimworld.* -- count as required: every DLC is a hard prerequisite, owner 2026-09-26). A group with ALL its
defs loaded passes, a group with NONE loaded is reported as "guard <pkg> inactive" (skipped, not a pass of those
defs), and a group PARTLY loaded fails: the guard was satisfied, so the missing ones were really lost.
"""
import os
import xml.etree.ElementTree as ET

from modcheck import ExpectationFailed

CHUNK = 40
DEFAULT_FIELDS = ("label",)


def guard_of(el):
    """The def's own load guard, lowercased ('' when none, or when it only names DLCs)."""
    g = (el.get("MayRequire") or "").strip()
    any_of = (el.get("MayRequireAnyOf") or "").strip()
    parts = [x.strip().lower() for x in g.split(",") if x.strip()]
    parts = [x for x in parts if not x.startswith("ludeon.rimworld")]
    out = ",".join(sorted(parts))
    if any_of:
        alts = [x.strip().lower() for x in any_of.split(",") if x.strip()]
        if not any(a.startswith("ludeon.rimworld") for a in alts):
            out = (out + ";" if out else "") + "anyof:" + ",".join(sorted(alts))
    return out


def guards(mod_dir):
    """{(defType, defName): guard} for every non-abstract def carrying a non-DLC MayRequire(AnyOf)."""
    return {(ty, n): g for ty, n, _l, g in parse(mod_dir, with_guard=True) if g}


def parse(mod_dir, with_guard=False):
    """[(defType, defName, {leafTag: text})] for every non-abstract def under <mod_dir>/Defs (sorted walk);
    with_guard=True appends guard_of(def) as a 4th item."""
    out = []
    root_dir = os.path.join(mod_dir, "Defs")
    for root, dirs, files in os.walk(root_dir):
        dirs.sort()
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            try:
                top = ET.parse(os.path.join(root, fn)).getroot()
            except ET.ParseError as ex:
                raise ExpectationFailed("%s does not parse: %s" % (os.path.join(root, fn), ex))
            for el in top:
                if not isinstance(el.tag, str) or el.get("Abstract", "").lower() == "true":
                    continue
                name = (el.findtext("defName") or "").strip()
                if not name:
                    continue
                leaf = {}
                for c in el:
                    v = (c.text or "").strip()
                    if isinstance(c.tag, str) and len(c) == 0 and v:
                        leaf[c.tag] = v
                out.append((el.tag, name, leaf, guard_of(el)) if with_guard else (el.tag, name, leaf))
    return out


def same_value(expect, got):
    """XML text vs a live readback: numbers numerically, bools case-blind, everything else exactly."""
    if got is None or isinstance(got, (dict, list)):
        return False
    a, b = str(expect).strip(), str(got).strip()
    try:
        fa, fb = float(a), float(b)
        return abs(fa - fb) <= 1e-4 * max(1.0, abs(fa))
    except ValueError:
        pass
    if a.lower() in ("true", "false"):
        return a.lower() == b.lower()
    return a == b


def _get_defs(t, specs, fields):
    rows, missing = {}, []
    for i in range(0, len(specs), CHUNK):
        chunk = specs[i:i + CHUNK]
        r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields=",".join(fields), deep=False)
        if not _live(t):
            return {}, []
        if not isinstance(r, dict) or not r.get("success"):
            raise ExpectationFailed("get_defs(%d defs) failed: %r" % (len(chunk), r))
        nf = list(r.get("notFound") or [])
        if r.get("foundCount") is not None and r.get("foundCount") + len(nf) != len(chunk):
            raise ExpectationFailed("get_defs foundCount %r + notFound %d != %d requested" % (
                r.get("foundCount"), len(nf), len(chunk)))
        missing.extend(nf)
        for row in r.get("defs") or []:
            rows[row.get("defName")] = row
    return rows, missing


def classify_missing(defs, guard, missing):
    """(lost, groups). `missing` is get_defs' notFound list ('Type/name' or bare name). An unguarded missing
    def is lost; a guarded one is lost only when another def under the SAME guard did load.
    groups = {guard: (loaded, total)}."""
    miss = set()
    for m in missing:
        m = str(m)
        miss.add(m.split("/", 1)[1] if "/" in m else m)
    groups = {}
    for (ty, n), g in guard.items():
        have, total = groups.get(g, (0, 0))
        groups[g] = (have + (0 if n in miss else 1), total + 1)
    lost = []
    for ty, n, _l in defs:
        if n not in miss:
            continue
        g = guard.get((ty, n))
        if not g or groups[g][0] > 0:
            lost.append("%s/%s" % (ty, n) + (" (guard %s satisfied by its siblings)" % g if g else ""))
    return lost, groups


def _live(t):
    return t.session is not None and not t.upstream_failed


def add_chain(suite, validation_file, fields_by_type=None, sanity=(), min_count=1, skip=(),
              name="every_shipped_def_reads_back"):
    """Register the two-component readback chain on `suite` for the mod folder holding `validation_file`."""
    mod_dir = os.path.dirname(os.path.abspath(validation_file))
    fields_by_type = dict(fields_by_type or {})
    skip = set(skip)

    def chain(t):
        defs = parse(mod_dir)
        guard = guards(mod_dir)
        absent = set()          # guarded defs whose whole guard group is inactive: not compared

        with t.component("every_shipped_def_is_loaded", beyond_toggle=True):
            names = set(n for _ty, n, _l in defs)
            blind = [s for s in sanity if s not in names]
            if blind or len(defs) < min_count:
                raise ExpectationFailed("the Defs/ parse is blind: %d defs (need >= %d), sanity names missing %s" % (
                    len(defs), min_count, blind))
            _rows, missing = _get_defs(t, ["%s/%s" % (ty, n) for ty, n, _l in defs], ("defName",))
            lost, groups = classify_missing(defs, guard, missing)
            for g, (have, total) in groups.items():
                if have == 0:
                    absent |= {n for (ty, n), gg in guard.items() if gg == g}
            if lost:
                raise ExpectationFailed("%d of %d shipped defs are not loaded by the game: %s" % (
                    len(lost), len(defs), lost[:20]))
            inactive = sorted(g for g, (have, _t) in groups.items() if have == 0)
            if inactive and _live(t):
                print("every_shipped_def_is_loaded: guarded defs skipped, guard inactive: %s" % inactive)

        with t.component("shipped_scalar_fields_match_xml", beyond_toggle=True):
            bad, compared = [], 0
            by_type = {}
            for ty, n, leaf in defs:
                by_type.setdefault(ty, []).append((n, leaf))
            for ty in sorted(by_type):
                fields = tuple(fields_by_type.get(ty, DEFAULT_FIELDS))
                rows, _missing = _get_defs(t, ["%s/%s" % (ty, n) for n, _l in by_type[ty]], fields)
                if not _live(t):
                    continue
                for n, leaf in by_type[ty]:
                    if n in absent:
                        continue
                    live = (rows.get(n) or {}).get("fields") or {}
                    for f in fields:
                        if f not in leaf or ("%s.%s" % (n, f)) in skip:
                            continue
                        compared += 1
                        if not same_value(leaf[f], live.get(f)):
                            bad.append("%s.%s: xml %r, live %r" % (n, f, leaf[f], live.get(f)))
            if _live(t):
                if compared == 0:
                    raise ExpectationFailed("compared no field at all: the readback asserts nothing")
                if bad:
                    raise ExpectationFailed("%d of %d shipped fields drift from the XML (a patch or another mod "
                                            "overriding?): %s" % (len(bad), compared, "; ".join(bad[:15])))

    chain.__name__ = name
    chain.__doc__ = ("Every non-abstract def in this mod's Defs/ is loaded live, and its authored scalar fields "
                     "(%s) read back equal to the XML." % (fields_by_type or {"*": DEFAULT_FIELDS}))
    suite.chain(name)(chain)
    return chain
