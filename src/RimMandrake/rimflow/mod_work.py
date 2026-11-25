#!/usr/bin/env python3
"""mod_work.py: is this ticket the work of one mod? The one rule that keeps mod tickets off the Workshop Pipeline.

Item RIMMANDRAKE_KEEP_MOD_TICKETS_OFF_LIST_PIPELINE_HUGETHINGS_WENT_TO_CODEX; page
design/specs/2026-11-23-list-dispatch/boundary.md (promise a-mod-ticket-is-not-the-list-pipelines); selftest
selftest_list_dispatch.py. Why: measured 2026-11-24, the Codex lane built two HugeThings tickets (home mod:HugeThings),
because HugeThings has no version folder and the page counted its tickets as work that is not mod work. CLAUDE.md
§Mods keep their own state: the open work of a mod stays with that mod, and the Maturation Pipeline works it.

    of(item, mods, prose=None) -> {"mod": <folder> or None, "why": <words>, "unreadable": <cause> or None}

The rule, in order:
  1. a home that cannot be read (not a {home: "<kind>:<name>"} record)  -> could not look: the ticket is not launched;
  2. a home mod:<folder>                                              -> the work of that mod;
  3. any other home (pipeline:, game:, machine:)                      -> not mod work (the home is the decision);
  4. no home, or unplaced: the repo paths in its title, check and prose. Each one inside one mod's folder
     (src/<Tier>/<Mod>/ or design/concepts/<Mod>/), and no path outside it -> the work of that mod. A path outside
     every mod (rimflow, Utils, design/specs, ...) or paths in two mods -> not mod work: a pipeline ticket that names a
     mod as its example stays in the Workshop Pipeline. A mod named only by a word, with no path, stays too.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
# a repo path in prose, either slash; the first two segments after the root are enough to place it
PATH_RX = re.compile(r"(?<![\w.-])(src|design|infrastructure|skills|world|observed|tools)[/\\]([\w.-]+)(?:[/\\]([\w.-]+))?")


def mods():
    """-> the set of mod folder names: every shipping folder (control.mod_folders) and every concept folder
    (control.known_mods). Raises when neither can be read: an empty set would class every ticket as list work."""
    import control as C
    out = set(C.mod_folders()) | set(C.known_mods())
    if not out:
        raise RuntimeError("no mod folder could be read (control.mod_folders and control.known_mods are empty)")
    return out


def prose_of(iid, items_dir=None):
    """-> (the item's prose text or "", None) or (None, the cause). A missing file is no prose, not a fault."""
    if not iid:
        return "", None
    if items_dir is None:
        import model as M
        items_dir = M.ITEMS
    p = os.path.join(items_dir, str(iid) + ".md")
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read(), None
    except FileNotFoundError:
        return "", None
    except OSError as e:
        return None, "its prose %s could not be read (%s: %s)" % (p, type(e).__name__, e)


def _g(o, k):
    return o.get(k) if isinstance(o, dict) else getattr(o, k, None)


def place(path_match, modset):
    """-> the mod a path is inside, or None when it is outside every mod."""
    root, a, b = path_match
    if root == "src" and a in TIERS and b in modset:
        return b
    if root == "design" and a == "concepts" and b in modset:
        return b
    return None


def of(item, modset, prose=""):
    """-> {"mod", "why", "unreadable"} for one ledger item (model.Item or dict). Pure over its inputs.
    prose: the item's prose text, "" for none, None when it could not be read."""
    home = _g(item, "home")
    if home is not None:
        h = home.get("home") if isinstance(home, dict) else None
        kind, _c, name = str(h).partition(":") if isinstance(h, str) else (None, None, None)
        if not isinstance(h, str) or (h != "unplaced" and (not kind or not name)):
            return {"mod": None, "why": "could not look: its home %r cannot be read" % (home,),
                    "unreadable": "its home %r is not a {home: <kind>:<name>} record" % (home,)}
        if kind == "mod":
            return {"mod": name, "why": "its home is mod:%s" % name, "unreadable": None}
        if h != "unplaced":
            return {"mod": None, "why": "its home is %s" % h, "unreadable": None}
    if prose is None:
        return {"mod": None, "why": "could not look: its prose could not be read",
                "unreadable": "its prose could not be read"}
    text = " ".join(str(x or "") for x in (_g(item, "title"), _g(item, "effect"), prose))
    inside, outside = set(), []
    for m in PATH_RX.findall(text):
        mod = place(m, modset)
        if mod:
            inside.add(mod)
        else:
            outside.append("/".join(x for x in m if x))
    if len(inside) == 1 and not outside:
        mod = next(iter(inside))
        return {"mod": mod, "why": "every repo path it names is inside the mod folder %s" % mod, "unreadable": None}
    if inside and outside:
        why = "it names %s and a path outside the mod (%s)" % (", ".join(sorted(inside)), outside[0])
    elif len(inside) > 1:
        why = "its paths lie in %d mods (%s)" % (len(inside), ", ".join(sorted(inside)))
    else:
        why = "no home and no path inside one mod"
    return {"mod": None, "why": why, "unreadable": None}


def status(r):
    """-> the status line of a ticket that is not the Workshop Pipeline's, or None when it is."""
    if not isinstance(r, dict):
        return None
    if r.get("unreadable"):
        return "could not look whether it is mod work: %s; nothing launches it" % r["unreadable"]
    if r.get("mod"):
        return "waits for the Maturation Pipeline run of %s (%s); the Workshop Pipeline does not work it" % (r["mod"], r["why"])
    return None


def reading(item, modset, items_dir=None):
    """-> of(item) with its prose read from disk."""
    prose, cause = prose_of(_g(item, "id"), items_dir)
    r = of(item, modset, prose)
    if prose is None and cause and r.get("unreadable"):
        r["unreadable"] = cause
    return r
