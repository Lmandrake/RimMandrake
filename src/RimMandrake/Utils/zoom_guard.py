#!/usr/bin/env python3
"""The camera-zoom invariant for every mod list we write (ZOOM_MOD_ENFORCE_NOT_JUST_ONE_DOOR).

Owner 2026-10-04: "We need the extra camera zoom mod to be in ALL DEBUG SETS". Owner 2026-11-03: the advanced zoom
is always in the mod lists where the human sits with Conductor. Either zoom mod satisfies it -- ray1203.simplecamerasetting
or brrainz.cameraplus -- and the two conflict, so we never add one on top of the other.

Doors that write the live ModsConfig.xml all call this: modlist_swap (swap, enable), modset_builder.write_config,
modcheck.runner.compose_test_list. modset_builder.resolve_tier keeps its own tier-level add (and `no_zoom`).
`./game up|loading` refuses/repairs at launch via check_live (game -> rimflow game).
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ZOOM = "ray1203.simplecamerasetting"
CAMERAPLUS = "brrainz.cameraplus"
SATISFIES = (ZOOM, CAMERAPLUS)
_LI = re.compile(r"<li>\s*([^<]+?)\s*</li>")


def active_ids(xml_text):
    m = re.search(r"<activeMods>(.*?)</activeMods>", xml_text, re.S)
    return [x for x in _LI.findall(m.group(1))] if m else []


def has_zoom(ids):
    low = {i.lower() for i in ids}
    return any(z in low for z in SATISFIES)


def zoom_installed():
    """True when the zoom mod's folder is on this machine (workshop, local Mods or DLC dir)."""
    from game_paths import WORKSHOP, LOCAL_MODS
    for base in (WORKSHOP, LOCAL_MODS):
        if not os.path.isdir(base):
            continue
        for d in os.listdir(base):
            about = os.path.join(base, d, "About", "About.xml")
            try:
                with open(about, encoding="utf-8-sig", errors="replace") as f:
                    if ZOOM in f.read().lower():
                        return True
            except OSError:
                continue
    return False


def with_zoom(ids, installed=None):
    """ids with the zoom mod placed right after Harmony when neither zoom mod is present. `installed` (bool or
    callable) defaults to a disk probe. Raises RuntimeError when it is needed and not installed: a list without
    any zoom must not be written quietly."""
    ids = list(ids)
    if has_zoom(ids):
        return ids
    ok = zoom_installed() if installed is None else (installed() if callable(installed) else installed)
    if not ok:
        raise RuntimeError("no zoom mod in the list and %s is not installed -- refusing to write a list the owner "
                           "cannot zoom in" % ZOOM)
    at = next((i + 1 for i, x in enumerate(ids) if x.lower() == "brrainz.harmony"), len(ids))
    ids.insert(at, ZOOM)
    return ids


def fix_text(xml_text, installed=None):
    """xml_text with the zoom mod inserted when missing (same bytes otherwise)."""
    ids = active_ids(xml_text)
    if has_zoom(ids):
        return xml_text
    new = with_zoom(ids, installed)
    anchor = re.search(r"<li>\s*brrainz\.harmony\s*</li>", xml_text, re.I)
    li = "<li>%s</li>" % ZOOM
    if anchor:
        return xml_text[:anchor.end()] + li + xml_text[anchor.end():]
    assert new
    return xml_text.replace("</activeMods>", "    %s\n  </activeMods>" % li, 1)


def enforce_file(path, installed=None):
    """Make the list at `path` carry a zoom mod, in place, atomically. -> True when it wrote."""
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")
    fixed = fix_text(text, installed)
    if fixed == text:
        return False
    tmp = path + ".zoom.tmp"
    with open(tmp, "wb") as f:
        f.write(fixed.encode("utf-8"))
    os.replace(tmp, path)
    return True


def check_live(repair=False, installed=None):
    """-> None when the live list has a zoom mod, else a message; with repair=True the mod is added and the
    message says so (None never; returns 'added ...'). Used at ./game up|loading."""
    from game_paths import MODS_CONFIG
    try:
        with open(MODS_CONFIG, encoding="utf-8") as f:
            ids = active_ids(f.read())
    except OSError as e:
        return "live ModsConfig.xml unreadable: %s" % e
    if has_zoom(ids):
        return None
    if repair:
        try:
            enforce_file(MODS_CONFIG, installed)
            return "added %s to the live ModsConfig.xml (neither zoom mod was listed)" % ZOOM
        except RuntimeError as e:
            return "REFUSED: %s" % e
    return "REFUSED: the live ModsConfig.xml has neither %s nor %s" % SATISFIES[::1]


if __name__ == "__main__":
    r = check_live(repair="--repair" in sys.argv)
    print(r or "zoom ok")
    sys.exit(0 if (r is None or r.startswith("added")) else 1)
