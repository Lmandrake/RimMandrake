#!/usr/bin/env python3
"""first_touch.py - The first item to name a mod with no Designer pass on record waits for one (owner, 2026-11-03).

*"the first time an item names a mod, it gets a deep Designer pass to read out its code/spec, expand the spec and
validation strategies, certifies it with the user/clarifies confusion, then writes it all out for Relentless."*

Relentless asks `hold()` before an item reaches a worker (the pool and the lease). An item that names a mod (the mods
`Effects.item_mods` finds: id, title, src/ paths in its prose) is held while any of those mods has no pass on record,
and the pass it needs is owed: Relentless files it once, `needs=owner`, for the Designer's sitting with him.

A mod's pass is ON RECORD when its pass item is closed `done`, or when `design/concepts/<Folder>/tree.json` passes
`concept_tree.gate` (a certified tree is a deeper pass than this one asks for). Its pass item is the one named in
`designer_passes.json` (the four recent mods the owner named, filed by hand) or else `<FOLDER>_DESIGN_FIRST_TOUCH`.

Not held: a pass item itself (it is the pass), and an item a worker already started (state past `ready`): it was
taken before the mod's first touch was ruled on, and pulling a worker off mid-build helps nobody.

  status [<Tier/Folder>...]   which mods have a pass on record, which are owed and under which item (read-only)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PASSES_FILE = os.path.join(HERE, "designer_passes.json")
SUFFIX = "_DESIGN_FIRST_TOUCH"
NAME_CAP = 44       # rimflow namecheck's cap
UNSTARTED = ("proposed", "ready")   # a worker has not taken it yet: first touch still holds
DONE = ("done",)


def load_passes(path=None):
    with open(path or PASSES_FILE, encoding="utf-8") as f:
        return json.load(f)


def pass_map(repo, passes):
    """{"Tier/Folder": pass item} for the mods filed by hand: `mods` directly, `compose` for every member of a composed
    mod (Baroque Biomes is one pass over its members). A compose file that cannot be read maps nothing: its members then
    owe their own generated pass, which is louder than silently passing them."""
    out = dict(passes.get("mods") or {})
    for rel, item in (passes.get("compose") or {}).items():
        tier = rel.split("/")[1] if rel.count("/") >= 2 else "RimMandrake"
        try:
            with open(os.path.join(repo, rel), encoding="utf-8") as f:
                entries = json.load(f).get("entries") or []
        except (OSError, ValueError):
            continue
        for e in entries:
            src = isinstance(e, dict) and e.get("source")
            if src:
                out.setdefault("%s/%s" % (tier, src), item)
    return out


def pass_item_id(mod):
    """The generated pass id: SUBJECT (the folder, upper, alphanumerics only) + `_DESIGN_FIRST_TOUCH`, inside the cap."""
    subject = re.sub(r"[^A-Za-z0-9]", "", mod.split("/")[-1]).upper()
    return subject[:NAME_CAP - len(SUFFIX)] + SUFFIX


def pass_items(mapping):
    return set(mapping.values())


def is_pass_item(item, mapping):
    return item in pass_items(mapping) or item.endswith(SUFFIX)


def tree_gates(repo, mod):
    """True when the mod's own concept tree passes the gate. Absent or unreadable: False (no pass from it)."""
    d = os.path.join(repo, "design", "concepts", mod.split("/")[-1])
    if not os.path.isfile(os.path.join(d, "tree.json")):
        return False
    try:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import concept_tree
        return not concept_tree.gate(d, repo)[0]
    except Exception:  # noqa: BLE001  a gate that cannot read gives no pass: this door fails shut
        return False


def on_record(repo, mod, mapping, state_of, tree=tree_gates):
    """(True, pass id) when the mod's pass is on record, else (False, pass id). `state_of(id)` -> ledger state or None."""
    pid = mapping.get(mod) or pass_item_id(mod)
    return (state_of(pid) in DONE or tree(repo, mod)), pid


def hold(repo, item, mods, state_of, mapping, tree=tree_gates):
    """(why, owed): why this item may not reach a worker yet (None: it may), and [(mod, pass id)] whose pass item has
    never been filed. Pure but for the tree read; `state_of` answers from the caller's own ledger replay."""
    if not mods or is_pass_item(item, mapping):
        return None, []
    st = state_of(item)
    if st is not None and st not in UNSTARTED:
        return None, []
    missing, owed = [], []
    for m in sorted(mods):
        ok, pid = on_record(repo, m, mapping, state_of, tree)
        if ok:
            continue
        missing.append("%s (pass %s, %s)" % (m, pid, state_of(pid) or "not filed"))
        if state_of(pid) is None and pid == pass_item_id(m):    # a hand-filed id is the owner's to file, never ours
            owed.append((m, pid))
    if not missing:
        return None, []
    return ("%s names a mod with no Designer pass on record: %s" % (item, "; ".join(missing))), owed


def pass_title(mod):
    return ("Designer deep pass on %s (first touch): read its code and spec, expand the spec and validation strategies "
            "(site prep and controls per scene), certify with the owner, write it out for Relentless as build items"
            % mod.split("/")[-1])


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] != "status":
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    if os.path.dirname(HERE) not in sys.path:
        sys.path.insert(0, os.path.dirname(HERE))
    from rimflow import model
    w = model.replay(model.read())

    def state_of(i):
        it = w.items.get(i)
        return getattr(it, "state", None) if it else None
    mapping = pass_map(REPO, load_passes())
    mods = argv[1:] or sorted(mapping)
    for m in mods:
        ok, pid = on_record(REPO, m, mapping, state_of)
        print("%-40s %-8s %s (%s)" % (m, "ON-RECORD" if ok else "OWED", pid, state_of(pid) or "not filed"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
