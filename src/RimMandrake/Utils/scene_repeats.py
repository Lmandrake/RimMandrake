#!/usr/bin/env python3
"""scene_repeats - stamp a scene again: repeats of one plan on fresh stamps, copies side by side as one cluster, the reset digest.

Item RIMMANDRAKE_BUILD_STAMP_AGAIN_REPEATS_WITH_RESET_DIGEST (Bridge v2, 02_needs_design.md §8 "Fast repeats for kind B and kind C",
shapes 2 and 3; 05_build_design.md decisions 8 and 12). Page: design/specs/2026-11-23-bridge-v2/boundary.md §STAMP AGAIN.
Tests: src/RimMandrake/Utils/selftest_scene_repeats.py.

Pure: no game, no bridge. A scene script keeps one Series for one plan and tells it what each stamp read back:

    series = Series("sc_rescue", claim="<claim hash>", build="<sha>", plan="<plan sha>", distance=4)
    for copy in range(n):
        st = s.stage(cast=..., station=series.station_request((9, 9)))       # the scene library gives the station
        series.stamp(station_digest(blocks, rect), mod_digests(s), rect=rect, cluster=c)   # Stop when the reset is not clean
    ... s.run(...) ...
    series.ended(launch, outcome=..., opportunity=True, exposures=3, receipt=..., cells={alias: [cells seen]})
    lines = series.ledger_lines(receipt_marks)       # run lines for scene_verdicts.add_run

What a stamp resets is what the scene's data stages. What it does not reset (world pawns, a mod's static counters, caches) is
what the reset digest watches: the station's read-back digest and each of our mods' [RMDigest] hook, compared with the first
stamp. A difference stops the repeat. A digest that could not be read is never equal. From time to time the same scene runs in
a fresh process; its first stamp is compared with this series' first stamp, and a difference joins the list of what a stamp
does not reset.
"""
import hashlib
import json
import math

STAMP, COPY, REPLAY = "stamp", "copy", "replay"      # how a launch was started; a replay is never a sample
# the read-back fields that carry identity or an absolute place, never the staged state (JawaBenchStageReadBack: ids are never digested)
PLACE_KEYS = frozenset(("id", "cell", "position", "pos", "x", "z", "thingId"))
NO_HOOK = "no digest hook"              # jawa/mod_hooks list: a mod that declares no per-scene state
FRESH_EVERY_COUNT = 10    # launches between two fresh-process comparisons. Danger: state that no digest sees colours every later launch. No measured rate yet (02_needs_design.md §8 "from time to time")


class Refused(Exception):
    """A request that the series cannot serve. `name` is the refusal, `why` says what would serve it."""

    def __init__(self, name, why):
        super().__init__("%s: %s" % (name, why))
        self.name, self.why = name, why


class Stop(Refused):
    """The repeat stops: the start state of this stamp is not the first stamp's. `diffs` names each part and both values."""

    def __init__(self, name, why, diffs=()):
        super().__init__(name, why)
        self.diffs = list(diffs)


def _h(lines):
    return hashlib.sha256("\n".join(sorted(lines)).encode("utf-8")).hexdigest()[:16]


def station_digest(blocks, rect):
    """-> (digest, None) of what a stamp made on a station, relative to the station's corner, or (None, why) when the blocks do not
    show all of it. `blocks` are the readBack blocks of the stamp's staging calls (and of its clean). Ids and absolute cells are
    left out, so two copies at different stations of one plan give one digest. A block that made more rows than it lists cannot
    be digested here: the companion lists at most 50 (StageReadBack.ListedWrong)."""
    ox, oz = int(rect[0]), int(rect[1])
    lines = []
    for i, b in enumerate(blocks):
        if not isinstance(b, dict) or not isinstance(b.get("made"), list):
            return None, "block %d has no made list" % i
        if int(b.get("rows") or 0) > len(b["made"]):
            return None, "block %d of %s made %s rows and lists %d" % (i, b.get("tool"), b.get("rows"), len(b["made"]))
        if int(b.get("leftBlocking") or 0) + int(b.get("leftKept") or 0) > len(b.get("left") or []):
            return None, "block %d of %s left more things than it lists" % (i, b.get("tool"))
        for r in b["made"]:
            got = {k: v for k, v in sorted((r.get("got") or {}).items()) if k not in PLACE_KEYS}
            lines.append("made|%s|%s,%s|%s" % (r.get("op"), int(r.get("x", 0)) - ox, int(r.get("z", 0)) - oz,
                                                json.dumps(got, sort_keys=True)))
        for l in b.get("left") or []:
            lines.append("left|%s,%s|%s|%s" % (int(l.get("x", 0)) - ox, int(l.get("z", 0)) - oz, l.get("def"), l.get("blocking")))
        lines.append("wrong|%d" % int(b.get("rowsWrong") or 0))
    return _h(lines), None


def mod_digests(rows):
    """-> {mod: digest | NO_HOOK | None} from the `digests` rows of `jawa/mod_hooks action=digest` (JawaBenchModHooks.cs: each
    `mod`, `digest`, `proven`, `why`). None: the hook is there and its digest cannot be trusted (unproven, threw, or no value), so
    it is never equal to anything."""
    out = {}
    for r in rows or []:
        m = r.get("mod")
        if not m:
            continue
        if r.get("digest") is None and r.get("why") == NO_HOOK:
            out[m] = NO_HOOK
        elif r.get("proven") is True and isinstance(r.get("digest"), str) and not r.get("why"):
            out[m] = r["digest"]
        else:
            out[m] = None
    return out


def _diffs(ref, now):
    """The parts of a start state that differ: [(part, first stamp, now)]. A part that could not be read differs."""
    out = []
    if ref["station"] is None or now["station"] is None or ref["station"] != now["station"]:
        out.append(("station", ref["station"], now["station"]))
    for m in sorted(set(ref["mods"]) | set(now["mods"])):
        a, b = ref["mods"].get(m, "absent"), now["mods"].get(m, "absent")
        if a is None or b is None or a != b:
            out.append(("mod " + m, a, b))
    return out


class Series(object):
    """The repeats of one plan of one scene on one build. Every stamp is a launch; a launch whose start state is the first stamp's
    is a sample when it ends; copies that share one stretch of ticks are one cluster, so one sample (scene_verdicts folds them)."""

    def __init__(self, scene, claim, build, plan, map_wide=False, distance=0, fresh_every_count=FRESH_EVERY_COUNT, series_id=None):
        for k, v in (("scene", scene), ("claim", claim), ("build", build), ("plan", plan)):
            if not isinstance(v, str) or not v.strip():
                raise Refused("BAD_ARGS", "a series names its %s" % k)
        if not isinstance(distance, int) or distance < 0 or not isinstance(fresh_every_count, int) or fresh_every_count < 1:
            raise Refused("BAD_ARGS", "distance is a count of cells (0 or more), fresh_every_count a count of launches (1 or more)")
        self.scene, self.claim, self.build, self.plan = scene, claim, build, plan
        self.map_wide, self.distance, self.fresh_every_count = bool(map_wide), distance, fresh_every_count
        self.id = series_id or _h([scene, claim, build, plan])[:8]
        self.launches, self.first, self.stopped = [], None, None
        self.clusters = {}              # cluster id -> [launch numbers]
        self.fresh_at = 0               # the launch count at the last fresh-process comparison
        self.not_reset = []             # lines: what a stamp did not reset, found by a fresh-process comparison

    # ---- copies side by side
    def station_request(self, size):
        """The station request of one copy: its margin keeps `distance` cells between any two copies (each is grown by its own)."""
        return {"size": tuple(size), "margin": int(math.ceil(self.distance / 2.0))}

    def cluster(self):
        """A new cluster id for copies that share one stretch of ticks. A map-wide scene may not share a map."""
        if self.map_wide:
            raise Refused("MAP_WIDE_NO_COPIES", "scene %s is map-wide: its copies would share one map-wide state and spoil each other; "
                          "stamp it again one at a time, or on a fresh small map" % self.scene)
        c = "%s.c%d" % (self.id, len(self.clusters) + 1)
        self.clusters[c] = []
        return c

    # ---- one stamp
    def stamp(self, station, mods, rect, cluster=None, replay_of=None):
        """Record one stamp: its station digest (from station_digest: (digest, why)) and its mods' digests (from mod_digests).
        -> the launch. Raises Stop when the start state differs from the first stamp's, and refuses every stamp after a stop."""
        if self.stopped:
            raise Stop("STOPPED", "the repeat stopped at launch %d (%s): find what the stamp did not reset, then start a new series"
                       % (self.stopped["launch"], self.stopped["why"]), self.stopped["diffs"])
        if cluster is not None and cluster not in self.clusters:
            raise Refused("UNKNOWN_CLUSTER", "cluster %r was not opened by this series (series.cluster())" % (cluster,))
        dig, why = station if isinstance(station, tuple) else (station, None)
        n = len(self.launches) + 1
        how = REPLAY if replay_of else (COPY if cluster else STAMP)
        launch = {"launch": n, "series": self.id, "plan": self.plan, "how": how, "cluster": cluster, "replay_of": replay_of,
                  "rect": tuple(rect), "start": {"station": dig, "mods": dict(mods or {})}, "station_why": why,
                  "fresh_overdue": n - self.fresh_at > self.fresh_every_count, "state": "staged", "sample": None}
        self.launches.append(launch)
        if cluster is not None:
            self.clusters[cluster].append(n)
        if self.first is None:
            unread = [p for p, v in [("station", dig)] + [("mod " + m, v) for m, v in sorted(launch["start"]["mods"].items())] if v is None]
            if unread:
                self._stop(launch, "RESET_UNVERIFIED", "the first stamp's %s could not be read (%s): no later stamp can be compared "
                           "with it" % (", ".join(unread), why or "the mod's digest is unproven or threw"),
                           [(p, None, None) for p in unread])
            self.first = launch["start"]
            return launch
        d = _diffs(self.first, launch["start"])
        if d:
            unread = [p for p, a, b in d if a is None or b is None]
            name = "RESET_UNVERIFIED" if unread and len(unread) == len(d) else "RESET_DIGEST_DIFFERS"
            self._stop(launch, name, "launch %d does not start from the first stamp's state: %s" % (
                n, "; ".join("%s first %s, now %s" % (p, a, b) for p, a, b in d)), d)
        return launch

    def _stop(self, launch, name, why, diffs):
        launch["state"] = "stopped"
        self.stopped = {"launch": launch["launch"], "name": name, "why": why, "diffs": diffs}
        raise Stop(name, why, diffs)

    # ---- the end of a launch
    def ended(self, launch, outcome, opportunity, exposures=0, receipt=None, cells=None):
        """The launch ran: its outcome (one of the seven), whether its valid opportunity arose, how many exposures to the suspected
        trigger it had, its receipt hash, and the cells where each cast alias of this copy was seen (for the cross-talk check)."""
        if launch.get("state") != "staged":
            raise Refused("NOT_STAGED", "launch %s is %s: only a staged launch ends" % (launch.get("launch"), launch.get("state")))
        if not isinstance(exposures, int) or exposures < 0:
            raise Refused("BAD_ARGS", "exposures is a count, 0 or more")
        launch.update(state="ended", outcome=outcome, opportunity=bool(opportunity), exposures=exposures, receipt=receipt,
                      cells={k: [tuple(c) for c in v] for k, v in (cells or {}).items()})
        launch["sample"] = launch["how"] != REPLAY
        return launch

    def crosstalk(self, cluster):
        """-> BREACH lines: a cast member of one copy seen on another copy's station or its margin. Each copy it touches is spoiled
        (its outcome reads UNRESOLVED on its ledger line): the copies were not apart."""
        members = [self.launches[n - 1] for n in self.clusters.get(cluster, [])]
        m = int(math.ceil(self.distance / 2.0))
        out = []
        for a in members:
            for b in members:
                if a is b:
                    continue
                x, z, w, h = b["rect"]
                for alias, cells in (a.get("cells") or {}).items():
                    hit = [c for c in cells if x - m <= c[0] < x + w + m and z - m <= c[1] < z + h + m]
                    if hit:
                        out.append("BREACH: %s of launch %d was at %s, on launch %d's station %s (margin %d)" % (
                            alias, a["launch"], hit[0], b["launch"], b["rect"], m))
                        a["breach"] = b["breach"] = True
        return out

    # ---- the fresh-process comparison
    def fresh_due(self):
        """True when `fresh_every_count` launches ran since the last fresh-process comparison."""
        return len(self.launches) - self.fresh_at >= self.fresh_every_count

    def fresh(self, station, mods, where):
        """The same plan's first stamp in a fresh process (`where`: the game and the process start). -> the lines added to the list of
        what a stamp does not reset. A difference also stops the series: its stamps did not start from a fresh state."""
        if self.first is None:
            raise Refused("NO_FIRST_STAMP", "the series has no first stamp to compare a fresh process with")
        dig = station[0] if isinstance(station, tuple) else station
        d = _diffs(self.first, {"station": dig, "mods": dict(mods or {})})
        self.fresh_at = len(self.launches)
        added = ["%s: a stamp in a warm process read %s, the fresh process (%s) read %s (scene %s, plan %s)" % (p, a, where, b, self.scene,
                                                                                                             self.plan) for p, a, b in d]
        self.not_reset += added
        if d and not self.stopped:
            self.stopped = {"launch": len(self.launches), "name": "STAMP_NOT_FRESH", "why": "; ".join(added), "diffs": d}
        return added

    # ---- the counts and the ledger
    def counts(self):
        """Launches, valid opportunities and exposures, kept apart; samples counts a cluster once."""
        ended = [l for l in self.launches if l["state"] == "ended"]
        samples = [l for l in ended if l["sample"] and not l["cluster"]]
        return {"launches": len(self.launches), "opportunities": sum(1 for l in ended if l["opportunity"]),
                "exposures": sum(l["exposures"] for l in ended), "samples": len(samples) + len({l["cluster"] for l in ended
                                                                                             if l["sample"] and l["cluster"]}),
                "clusters": len([c for c, ns in self.clusters.items() if ns]), "stopped": bool(self.stopped)}

    def ledger_lines(self, marks):
        """-> run lines for scene_verdicts.add_run, one per ended launch. `marks`: {launch: the receipt's marks (overlay, tainted, arm,
        compared, build_kind, map_kind)}; a mark the receipt does not give is left out, so the ledger counts the run for no bar."""
        out = []
        for l in self.launches:
            if l["state"] != "ended":
                continue
            line = {"run": "%s.%d" % (self.id, l["launch"]), "scene": self.scene, "claim": self.claim, "build": self.build,
                    "outcome": "UNRESOLVED" if l.get("breach") else l["outcome"], "receipt": l["receipt"] or "",
                    "series": self.id, "plan": self.plan, "launch": l["launch"], "how": l["how"], "opportunity": l["opportunity"],
                    "exposures": l["exposures"], "fresh_overdue": l["fresh_overdue"]}
            if l["cluster"]:
                line["cluster"] = l["cluster"]
            if l["replay_of"]:
                line["replay_of"] = l["replay_of"]
            if l.get("breach"):
                line["spoiled_by"] = "cross-talk between copies of cluster %s" % l["cluster"]
            line.update((marks or {}).get(l["launch"]) or {})
            out.append(line)
        return out


def read_mod_digests(s):
    """Live: the digests of our mods now, through `jawa/mod_hooks action=digest` (05_build_design.md decision 8). -> mod_digests()."""
    r = s.raw("jawa/mod_hooks", action="digest", scope="")
    if not isinstance(r, dict) or r.get("success") is not True or not isinstance(r.get("digests"), list):
        raise Refused("COULD_NOT_LOOK", "jawa/mod_hooks digest gave no digests: %s" % (str(r)[:200],))
    return mod_digests(r["digests"])
