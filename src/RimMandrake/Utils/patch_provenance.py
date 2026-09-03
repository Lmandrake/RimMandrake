"""Stop the generators from reading their own output back as input.

THE FAILURE THIS EXISTS TO PREVENT

The live dump is the post-patch truth, which is exactly why it is worth having
-- and exactly why it is dangerous as a generator INPUT. Once our own mods are
in the load list, the dump contains our writes. A generator that maps
"old value -> new value" then reads its own new value as the old one:

    2026-08-11, gen_armoury_patch.py, lightsabers
      first run : live power 28  -> band -> 99      (correct)
      re-run    : live power 99  -> clamped to the top of SOURCE_RANGE
                                 -> factor ~1.0 applied to raw 28 -> 34
                  i.e. re-running the generator SILENTLY REVERTS the weapon it
                  had already retuned, and does it without an error anywhere.

Clamping does not save you. A source range makes the mapping idempotent under
ROSTER change (add a mod, existing values hold still); it does nothing about
feeding the function its own output, which is a different property entirely.

THE RULE THIS MODULE ENCODES

    Structure may come from the live dump.  Values may not, wherever we write.

  * STRUCTURE -- which defs exist, which tools they ended up with, what class a
    thing is. Only the live dump knows this: other mods inject nodes through
    PatchOperations that no amount of offline inheritance-resolving will show.
  * VALUES used as an anchor -- must come from a source we do not write to:
    the mod's raw XML offline, or the recorded original from the last time we
    changed it. Never from live at an xpath our own patches touch.

WHAT YOU GET

    status = guard(D_DUMP, "gen_armoury_patch")   # prints a banner, warns loudly
    ours   = OurWrites()                          # what our mods write, and where
    value, src = ours.baseline(xpath, live_value)  # the anchor you may safely use

`baseline` returns live_value untouched when we do not write there. When we do,
it returns the recorded pre-patch original instead, so a re-run reproduces the
first run exactly. When we write there and no original was ever recorded, it
returns (None, "unknown") -- a generator must treat that as "skip, do not
guess", which is the only safe answer.

WHERE THE ORIGINALS COME FROM

A ledger at observed/2026-08-13/inventory/patch_ledger.json, written by the generators as they
emit. For patches generated before the ledger existed, bootstrap() recovers the
originals from the "X : 15 -> 26" comments the generators already wrote next to
every operation. Comments are a poor database, so they are used ONCE to seed the
ledger and never consulted again.
"""
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CUSTOM = os.path.join(ROOT, "src")
LEDGER = os.path.join(ROOT, "observed", "2026-08-13",
                      "inventory", "patch_ledger.json")

# "<!-- RSW_Mid_Blue_Blaster_Bolt : 15 -> 26 -->"
# "<!-- Force_LightsaberBase / point : 28 -> 99 -->"
# "<!-- MA_ClawSaber / blade AP 0.24 -> 0.00 -->"
# "<!-- AG_Forsaken_Hood [powered] ArmorRating_Sharp -> 1.40 -->"   (no original)
_ARROW = re.compile(r"(-?\d+(?:\.\d+)?)\s*->\s*(-?\d+(?:\.\d+)?)\s*$")
_TOKEN = re.compile(r"<!--(.*?)-->|<xpath>(.*?)</xpath>", re.S)


def our_package_ids():
    """packageId -> mod folder name, read from our own About.xml files.

    Discovered, never hardcoded: a hardcoded list is wrong the day someone adds
    a mod, and being wrong here means silently trusting contaminated values.

    Walked at any depth under CUSTOM, not assumed to sit one level down: mods
    live at src/<Tier>/<Mod>/About/About.xml under the three-tier layout, and a
    fixed one-level scan found zero of them -- which made every "contaminated"
    check silently read PRISTINE.
    """
    out = {}
    if not os.path.isdir(CUSTOM):
        return out
    for dirpath, _dirnames, _filenames in os.walk(CUSTOM):
        about = os.path.join(dirpath, "About", "About.xml")
        if not os.path.isfile(about):
            continue
        try:
            pid = ET.parse(about).getroot().findtext("packageId")
        except ET.ParseError:
            continue
        if pid:
            out[pid.strip().lower()] = os.path.basename(dirpath)
    return out


def _patch_files():
    """Every *.xml under any Patches/ directory anywhere under CUSTOM.

    Walked, not assumed to sit one level down: mods live at
    src/<Tier>/<Mod>/Patches under the three-tier layout, and a fixed-depth
    scan found none of them -- silently making every xpath in the repo read
    as "we do not write here".
    """
    if not os.path.isdir(CUSTOM):
        return
    for dirpath, _dirnames, filenames in os.walk(CUSTOM):
        if os.path.basename(dirpath) != "Patches":
            continue
        for fn in sorted(filenames):
            if fn.endswith(".xml"):
                yield os.path.join(dirpath, fn)


class DumpStatus(object):
    """What a live dump is safe to be used for."""

    def __init__(self, path, exists, captured, mod_count, ours):
        self.path = path
        self.exists = exists
        self.captured = captured
        self.mod_count = mod_count
        self.ours = ours              # our packageIds present in the dump

    @property
    def contaminated(self):
        """True when the dump was captured with our own mods loaded.

        Not a defect -- it is the normal, desirable state, and the dump is still
        the only source of post-patch structure. It means only that VALUES at
        xpaths we write must come from the ledger instead.
        """
        return bool(self.ours)

    def banner(self, what):
        if not self.exists:
            return ["no live dump at %s" % self.path,
                    "%s: structure falls back to offline; injected nodes invisible" % what]
        head = "live dump %s | %d mods | %s" % (self.captured, self.mod_count, what)
        if not self.contaminated:
            return [head, "PRISTINE: none of our mods were loaded; live values are anchors"]
        return [head,
                "CONTAMINATED by our own mods: %s" % ", ".join(sorted(self.ours)),
                "structure OK to read; VALUES at our xpaths must come from the ledger"]


def dump_status(dump_dir):
    man = os.path.join(dump_dir, "manifest.json")
    if not os.path.isfile(man):
        return DumpStatus(dump_dir, False, None, 0, [])
    with io.open(man, encoding="utf-8") as fh:
        m = json.load(fh)
    ours = our_package_ids()
    present = [x["packageId"] for x in (m.get("mods") or [])
               if (x.get("packageId") or "").lower() in ours]
    return DumpStatus(dump_dir, True, m.get("capturedUtc"),
                      m.get("modCount") or 0, present)


def guard(dump_dir, what):
    """Print the dump's provenance up front. Call this before reading a dump.

    Printing is the point. The 2026-08-11 near-miss was not caused by anyone
    deciding the dump was clean -- it was caused by nobody asking.
    """
    st = dump_status(dump_dir)
    for line in st.banner(what):
        print("  [dump] %s" % line)
    return st


class OurWrites(object):
    """Every xpath our generated patches write, and the original where known.

    The patch files are their own manifest of what we touch: an xpath appearing
    in one of them is, by definition, a place the live dump can no longer be
    trusted for a value.
    """

    def __init__(self, ledger=None):
        self.by_xpath = {}            # xpath -> {"file","value"}
        self._scan()
        self.originals = dict(ledger if ledger is not None else load_ledger())

    def _scan(self):
        for path in _patch_files():
            try:
                root = ET.parse(path).getroot()
            except ET.ParseError:
                continue
            for xp in root.iter("xpath"):
                if xp.text:
                    self.by_xpath.setdefault(
                        xp.text.strip(), {"file": os.path.relpath(path, CUSTOM)})

    def writes(self, xpath):
        return xpath in self.by_xpath

    def baseline(self, xpath, live_value):
        """The value a generator may safely use as its 'old' anchor.

        Returns (value, source) where source is one of:
          "live"     we do not write here; the dump is authoritative
          "ledger"   we do write here; this is the recorded pre-patch original
          "unknown"  we write here and no original was recorded -- SKIP the def
                     rather than guessing. Guessing is how 99 became 34.
        """
        if not self.writes(xpath):
            return live_value, "live"
        if xpath in self.originals:
            return self.originals[xpath], "ledger"
        return None, "unknown"


# ------------------------------------------------------------------ ledger
def load_ledger():
    if not os.path.isfile(LEDGER):
        return {}
    with io.open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh).get("originals", {})


def save_ledger(originals, note=""):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with io.open(LEDGER, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "_": "Pre-patch originals, keyed by xpath. Written by the generators "
                 "so a re-run anchors on the value the mod author shipped, not "
                 "on our own previous output. See src/RimMandrake/Utils/patch_provenance.py.",
            "note": note,
            "count": len(originals),
            "originals": dict(sorted(originals.items())),
        }, indent=1, sort_keys=False))
        fh.write("\n")


class Recorder(object):
    """Collects originals during a generator run; merges rather than replaces.

    Merge, never overwrite: the first recording of an xpath is the only one made
    against pristine data. A later run sees our own value and would poison the
    ledger with it -- which is the very failure this module exists to stop.
    """

    def __init__(self):
        self.originals = dict(load_ledger())
        self.added = 0

    def record(self, xpath, original):
        if original is None or xpath in self.originals:
            return
        self.originals[xpath] = original
        self.added += 1

    def save(self, note=""):
        save_ledger(self.originals, note)
        print("  ledger: %d originals (%d new) -> %s"
              % (len(self.originals), self.added,
                 os.path.relpath(LEDGER, ROOT)))


def bootstrap():
    """Seed the ledger from the 'old -> new' comments already in our patches.

    One-shot recovery for patches generated before the ledger existed. Each
    operation was emitted with a comment recording the value it replaced, so the
    originals are on disk -- just in the worst possible database. Read once,
    written to the ledger, never consulted again.
    """
    rec = Recorder()
    for path in _patch_files():
        with io.open(path, encoding="utf-8") as fh:
            text = fh.read()
        # Pair each comment with the first <xpath> that follows it. Scanned as
        # a single sequential token stream, not a combined comment+xpath
        # regex: that combined form let an EARLIER non-arrow comment (e.g.
        # every file's header) swallow the very next operation's own
        # comment+xpath as unmatched filler text, silently dropping the first
        # entry of every generated patch file.
        pending = None
        for m in _TOKEN.finditer(text):
            comment, xpath = m.group(1), m.group(2)
            if xpath is not None:
                if pending is not None:
                    rec.record(xpath.strip(), pending)
                pending = None
                continue
            arrow = _ARROW.search(comment.strip())
            pending = float(arrow.group(1)) if arrow else None
    rec.save("bootstrapped from generated patch comments")
    return rec


# ------------------------------------------------------------------ selftest
def _selftest():
    ok = 0

    ids = our_package_ids()
    assert ids, "found no packageIds under custom_patches"
    assert all(k == k.lower() for k in ids), "packageIds must be normalised"
    ok += 1

    w = OurWrites(ledger={"/a/b": 15.0})
    assert w.baseline("/a/b", 26.0) == (26.0, "live") or w.writes("/a/b"), \
        "an xpath we do not write must pass live through"
    ok += 1

    # The core contract, stated as a test so it cannot rot.
    class Fake(OurWrites):
        def __init__(self):
            self.by_xpath = {"/mine": {"file": "x"}}
            self.originals = {"/mine": 28.0}
    f = Fake()
    assert f.baseline("/mine", 99.0) == (28.0, "ledger"), \
        "must return the recorded original, NOT our own live value"
    assert f.baseline("/theirs", 26.0) == (26.0, "live")
    f.originals = {}
    assert f.baseline("/mine", 99.0) == (None, "unknown"), \
        "unrecorded + ours must be unknown, never a guess"
    ok += 1

    r = Recorder()
    before = dict(r.originals)
    r.originals = {"/x": 1.0}
    r.record("/x", 999.0)
    assert r.originals["/x"] == 1.0, "record() must never overwrite an original"
    r.originals = before
    ok += 1

    st = DumpStatus("p", True, "t", 5, [])
    assert not st.contaminated
    assert DumpStatus("p", True, "t", 5, ["mandrake.x"]).contaminated
    ok += 1

    print("patch_provenance selftest: %d groups OK" % ok)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    elif "--bootstrap" in sys.argv:
        bootstrap()
    else:
        from refresh import D_DUMP
        st = guard(D_DUMP, "status")
        w = OurWrites()
        print("  our mods      : %s" % ", ".join(sorted(our_package_ids())))
        print("  xpaths we write: %d" % len(w.by_xpath))
        print("  originals known: %d" % len(w.originals))
        unknown = [x for x in w.by_xpath if x not in w.originals]
        # Most operations write a CONSTANT (an armour tier, a leather profile, a
        # damage category, an interaction string). Those never need an original:
        # nothing is mapped from the previous value, so re-running cannot drift.
        # Only a generator that computes new-from-old is at risk, and it says so
        # itself by reporting an "unknown" anchor and skipping the def.
        print("  no original    : %d (expected: operations writing a constant "
              "need no anchor)" % len(unknown))
        print("  a generator that needs one and lacks it will SKIP the def and "
              "tell you to run --bootstrap")
