#!/usr/bin/env python3
"""Round 3 offline checks over a shape-lab world and its laid output.

    python3 ralph/live/lab_r3_checks.py WORLD.json LAID.json \
        [--tex TEXTURES_DIR] [--json OUT] [--dist]

Every count must be zero.

Existing checks:
  side_entry, uncovered, wall_no_plug, dead_end, undrawn, baked_stub

New checks:
  parent_no_cord  machine has connectParent but no hookup/link; legacy dumps count 0
  lead_device  device connection at a strip that is not socket-seated
  loose_plug   side-view machine plug lacking a cord end or machine seating
  double_cord  more than one strand end assigned to a plug fitting
  wall_vanish  strand end in/against blocked geometry without an allowed fitting
  wall_cross   three consecutive vertices in one blocked non-door cell, away from wall fittings
  wall_via_socket  wall-connected strand whose other end uses a socket-seated PlugTop
  kink         strand failing any curvature, saw-tooth, or V-turn threshold
  lamp_reversal  untied consumer PlugTop exit turning >100 degrees in its first
                 cell, heading >25 degrees off the decal at arc 0.3, or backward
  lamp_base    consumer cord end >0.12 cell from its lamp base or on the bulb side;
               legacy lamp IDs optionally come from Transient/lab/ba/lamps.json

Distances are in cells. Angles in JSON are radians.

--dist prints per-strand measurements and percentile distributions, including
unflagged strands. It does not change thresholds or exit-status behavior.

The kink thresholds below are provisional: calibrate them against the FULL
baseline with --dist. A first-point/last-point/count sample cannot measure bends.
Only baked() imports PIL/numpy.
"""
import argparse, glob, json, math, os, sys
import bisect

STRIP_HEADS, STRIP_HEAD_Z, STRIP_LEAD = [-0.328, -0.128, 0.065, 0.264], -0.049, (0.39, -0.05)
PLUGTOP_REACH = 0.1445
ARM_TUCK = 0.40

LAMP_BASE_DEFS = {
    "StandingLamp", "StandingLampColored", "Morbid_StandingLamp",
    "Rustic_StandingLamp", "Spikecore_StandingLamp", "Techist_StandingLamp",
    "Totemic_StandingLamp", "TorchLamp", "Morbid_TorchLamp",
    "Rustic_TorchLamp", "Spikecore_TorchLamp", "Totemic_TorchLamp",
    "BuildTorchLamp",
}

# Fitting-placement conventions inferred from the supplied laid sample.
# Local +X is (cos(angle), sin(angle)).
#
# Machine Plug:
#   strand end = decal centre + 0.25 * scale * local +X
#   art head   = decal centre + 0.46 * scale * local +X
#
# These are endpoint placement conventions, not a claim that art +X is its boot.
# The renderer can terminate a strand under the fitting's opaque pixels.
PLUG_CORD_X = 0.25
PLUG_HEAD_X = 0.46
PLUGTOP_REFERENCE_SCALE = 0.343
WALL_PAST_FACE_DEPTH = 0.03     # CordBuilder.PastFaceDepth, in cells
WALL_FACE_MARGIN = 0.01        # WallMount.FaceMargin, in cells

FIT_END_TOL = 0.065
SOCKET_CENTRE_TOL = 0.025
STRIP_CONNECTION_PAD = 0.20
LEAD_END_TOL = 0.10
MACHINE_HEAD_PAD = 0.08
LAMP_HEAD_PAD = 0.02            # require the lamp's plug head to be under it
WALL_PAIR_HEAD_TOL = 0.12
WALL_PAIR_ANGLE_COS = 0.97
WALL_END_PAD = 0.06             # also catches endpoints on wall corners/faces
FRAY_END_TOL = 0.08

# Kink thresholds: provisional until the full baseline has been measured.
KINK_END_IGNORE = 0.35
KINK_SAMPLE_STEP = 0.025
KINK_HALF_WINDOWS = (0.08, 0.16, 0.24)
KINK_MIN_RADIUS = 0.10          # fail when effective radius is smaller

SAW_HALF_WINDOW = 0.10
SAW_NOISE_DEG = 7.5
SAW_MAX_SEPARATION = 0.45
SAW_MIN_OPPOSITE_DEG = 25.0     # weaker of two opposite bend peaks

V_TANGENT_HALF_WINDOW = 0.04
V_MAX_ARC = 0.60
V_MAX_TURN_DEG = 160.0           # fail when signed heading change exceeds this

# CableTie marks the crossing of an intentional strain-relief loop.
# Recover its two visits on this strand; exempt that arc, not a nearby disc.
TIED_LOOP_REACH = 0.40
TIED_LOOP_VISIT_TOL = 0.05
TIED_LOOP_ARC_PAD = 0.08
KINK_FRAY_RADIUS_IGNORE = 2.5


def rot(x, z, a):
    return x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)


def strip_pt(d, x, z):
    _, px, pz, a, s = d[:5]
    ax, az = math.cos(a), math.sin(a)
    sx, sz = -az, ax                     # V2.Perp
    return px + ax * x * s + sx * z * s, pz + az * x * s + sz * z * s


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def piece_name(p, pi):
    label = p.get("name") or p.get("id")
    route = f"{p['a']} -> {p['b']}"
    return f"piece[{pi}]" + (f" {label}" if label is not None else "") + f" {route}"


def xy_text(p):
    return f"({p[0]:.3f},{p[1]:.3f})"


def validate_laid(L):
    """Reject trimmed samples before the unchanged existing checks see them."""
    for pi, p in enumerate(L["pieces"]):
        for si, strand in enumerate(p["strands"]):
            for vi, v in enumerate(strand):
                if (not isinstance(v, (list, tuple)) or len(v) < 2
                        or any(isinstance(t, bool) or not isinstance(t, (int, float))
                               or not math.isfinite(t) for t in v[:2])):
                    raise ValueError(
                        f"piece[{pi}] strand[{si}] vertex[{vi}] is not a finite "
                        "[x,z] point. Supply the full laid polyline; the trimmed "
                        "[first_point,last_point,count] sample is not runnable input."
                    )


def box_distance(p, x, z, w, h):
    dx = max(x - p[0], 0.0, p[0] - (x + w))
    dz = max(z - p[1], 0.0, p[1] - (z + h))
    return math.hypot(dx, dz)


def machine_distance(p, m):
    return box_distance(p, m["x"], m["z"], m["w"], m["h"])


def local_axis_point(d, x):
    return d[1] + math.cos(d[3]) * x, d[2] + math.sin(d[3]) * x


def wall_cord_seat(d):
    # EntryDecal/OutletDecal centre = face + into * (margin + depth / 2).
    # PastFace/Overrun end = face + into * 0.03.
    # These depths are cells, independent of the decal's across scale.
    into_z = math.sin(d[3])
    depth = 0.32 if into_z > 0.5 else 0.06 if into_z < -0.5 else 0.10
    return local_axis_point(
        d, WALL_PAST_FACE_DEPTH - WALL_FACE_MARGIN - depth / 2.0
    )


def plugtop_cord(d):
    # PLUGTOP_REACH is already in cells at the reference decal scale.
    return local_axis_point(
        d, PLUGTOP_REACH * d[4] / PLUGTOP_REFERENCE_SCALE
    )


def unique_decals(L):
    """Deduplicate repeated fitting declarations, preserving piece ownership."""
    result, lookup = [], {}
    for pi, p in enumerate(L["pieces"]):
        for d in p["decals"]:
            key = (
                d[0], round(d[1], 6), round(d[2], 6),
                round(math.cos(d[3]), 6), round(math.sin(d[3]), 6),
                round(d[4], 6),
            )
            if key not in lookup:
                lookup[key] = len(result)
                result.append({"d": d, "pieces": set()})
            result[lookup[key]]["pieces"].add(pi)
    return result


def name_kinds(nm, machines):
    exact = [m for m in machines if m["id"] == nm]
    if exact:
        return {int(m["kind"]) for m in exact}
    prefix = nm.split(":", 1)[0].lower()
    return {
        "source": {0},
        "battery": {1},
        # The sample calls device branches "consumer"; allow lamp ownership too.
        "consumer": {2, 3},
        "lamp": {3},
        "transmitter": {4},
    }.get(prefix, set())


def intended_machines(piece_indices, L, machines):
    """Prefer explicit machine identities/cells; otherwise constrain by kind."""
    exact, kinds = [], set()
    for pi in piece_indices:
        p = L["pieces"][pi]
        for nm in (p["a"], p["b"]):
            nk = name_kinds(nm, machines)
            kinds.update(nk)
            explicit = [m for m in machines if m["id"] == nm]
            if explicit:
                exact.extend(explicit)
                continue
            if not nk or ":" not in nm:
                continue
            try:
                fields = nm.split(":", 1)[1].split(",")
                if len(fields) != 2:
                    continue
                x, z = (float(v) for v in fields)
            except ValueError:
                continue
            exact.extend(
                m for m in machines
                if int(m["kind"]) in nk and m["x"] == x and m["z"] == z
            )
    if exact:
        return exact
    if kinds:
        return [m for m in machines if int(m["kind"]) in kinds]
    return machines


def bend_angle(u, v):
    if math.hypot(*u) < 1e-10 or math.hypot(*v) < 1e-10:
        return None
    return math.atan2(u[0] * v[1] - u[1] * v[0],
                      u[0] * v[0] + u[1] * v[1])


def strand_metrics(strand, cable_ties=(), fray_ends=(False, False)):
    """Measure geometry using physical arc length, not vertex counts.

    Effective radius at s and half-window h:
        h / abs(turn between chords [s-h,s] and [s,s+h])

    This recovers R on a circular arc and remains finite at a sharp reversal.
    Multiple fixed windows expose both narrow bends and broader hairpins.

    Saw value:
        maximum weaker peak of opposite signed bends within the stated arc gap.

    V value:
        maximum absolute signed change of smoothed tangent heading over ANY
        subinterval of at most V_MAX_ARC. Tangents are unwrapped incrementally.
        Intervals crossing an authored CableTie loop are exempt.
        Tied-loop support is also excluded from radius and saw measurements.
        A matching fray exempts only its final 2.5 cells from radius measurement.
    """
    points = []
    for v in strand:
        q = (float(v[0]), float(v[1]))
        if not points or dist(points[-1], q) > 1e-10:
            points.append(q)

    arc = [0.0]
    for a, b in zip(points, points[1:]):
        arc.append(arc[-1] + dist(a, b))
    total = arc[-1] if points else 0.0
    lo, hi = KINK_END_IGNORE, total - KINK_END_IGNORE

    m = {
        "length": total, "vertices": len(strand),
        "curvature": 0.0, "radius": math.inf, "radius_at": None,
        "saw_deg": 0.0, "saw_at": None, "saw_gap": 0.0,
        "v_deg": 0.0, "v_at": None, "v_arc": 0.0,
        "radius_samples": 0, "tangent_samples": 0,
    }
    if len(points) < 2 or hi <= lo:
        return m

    def at(s):
        s = min(total, max(0.0, s))
        i = min(len(points) - 2, max(0, bisect.bisect_right(arc, s) - 1))
        t = (s - arc[i]) / (arc[i + 1] - arc[i])
        return (points[i][0] + t * (points[i + 1][0] - points[i][0]),
                points[i][1] + t * (points[i + 1][1] - points[i][1]))

    tied_ranges = []
    for tie in cable_ties:
        visits = []
        for i, (a, b) in enumerate(zip(points, points[1:])):
            dx, dz = b[0] - a[0], b[1] - a[1]
            dd = dx * dx + dz * dz
            u = max(0.0, min(1.0, (
                (tie[0] - a[0]) * dx + (tie[1] - a[1]) * dz
            ) / dd))
            q = (a[0] + u * dx, a[1] + u * dz)
            gap = dist(q, tie)
            if gap > TIED_LOOP_VISIT_TOL:
                continue
            s = arc[i] + u * (arc[i + 1] - arc[i])
            if (visits and s - visits[-1][2]
                    <= 2 * TIED_LOOP_VISIT_TOL + KINK_SAMPLE_STEP):
                best_s, best_gap, _ = visits[-1]
                if gap < best_gap:
                    best_s, best_gap = s, gap
                visits[-1] = (best_s, best_gap, s)
            else:
                visits.append((s, gap, s))
        for a, b in zip(visits, visits[1:]):
            sa, sb = a[0], b[0]
            if not 0.20 <= sb - sa <= 2.5:
                continue
            support = [at(sa), at(sb)] + [
                q for q, s in zip(points, arc) if sa < s < sb
            ]
            if all(dist(q, tie) <= TIED_LOOP_REACH for q in support):
                tied_ranges.append((sa, sb))

    def tied_span(a, b):
        return any(
            a <= end + TIED_LOOP_ARC_PAD
            and b >= start - TIED_LOOP_ARC_PAD
            for start, end in tied_ranges
        )

    n = max(1, int(math.ceil((hi - lo) / KINK_SAMPLE_STEP)))
    positions = [lo + (hi - lo) * i / n for i in range(n + 1)]

    def turn_at(s, h):
        if (s - h < lo - 1e-9 or s + h > hi + 1e-9
                or tied_span(s - h, s + h)):
            return None
        a, b, c = at(s - h), at(s), at(s + h)
        return bend_angle((b[0] - a[0], b[1] - a[1]),
                          (c[0] - b[0], c[1] - b[1]))

    for s in positions:
        if ((fray_ends[0] and s <= KINK_FRAY_RADIUS_IGNORE)
                or (fray_ends[1] and total - s <= KINK_FRAY_RADIUS_IGNORE)):
            continue
        for h in KINK_HALF_WINDOWS:
            angle = turn_at(s, h)
            if angle is None:
                continue
            m["radius_samples"] += 1
            curvature = abs(angle) / h
            if curvature > m["curvature"]:
                m["curvature"] = curvature
                m["radius"] = 1.0 / curvature
                m["radius_at"] = at(s)

    # Condense adjacent same-sign bend samples into lobes. This avoids treating
    # every densely sampled vertex as a separate saw tooth.
    lobes = []
    for s in positions:
        angle = turn_at(s, SAW_HALF_WINDOW)
        if angle is None:
            continue
        degrees = math.degrees(angle)
        if abs(degrees) < SAW_NOISE_DEG:
            continue
        sign = 1 if degrees > 0 else -1
        if (lobes and lobes[-1]["sign"] == sign
                and s - lobes[-1]["last"] <= SAW_MAX_SEPARATION):
            lobe = lobes[-1]
            lobe["last"] = s
            if abs(degrees) > lobe["peak"]:
                lobe["peak"], lobe["s"] = abs(degrees), s
        else:
            lobes.append({
                "sign": sign, "peak": abs(degrees), "s": s, "last": s
            })

    for i, a in enumerate(lobes):
        for b in lobes[i + 1:]:
            gap = b["s"] - a["s"]
            if gap > SAW_MAX_SEPARATION:
                # Peak positions are ordered because lobes occupy disjoint runs.
                break
            if (a["sign"] == b["sign"]
                    or tied_span(a["s"] - SAW_HALF_WINDOW,
                                 b["s"] + SAW_HALF_WINDOW)):
                continue
            value = min(a["peak"], b["peak"])
            if value > m["saw_deg"]:
                m["saw_deg"] = value
                m["saw_gap"] = gap
                m["saw_at"] = at((a["s"] + b["s"]) / 2.0)

    tangents = []
    h = V_TANGENT_HALF_WINDOW
    for s in positions:
        if (s - h < lo - 1e-9 or s + h > hi + 1e-9
                or tied_span(s - h, s + h)):
            continue
        a, b = at(s - h), at(s + h)
        vector = (b[0] - a[0], b[1] - a[1])
        if math.hypot(*vector) > 1e-10:
            tangents.append((s, vector))
    m["tangent_samples"] = len(tangents)

    if tangents:
        headings = [0.0]
        for a, b in zip(tangents, tangents[1:]):
            angle = bend_angle(a[1], b[1])
            headings.append(headings[-1] + (angle if angle is not None else 0.0))

        def tied_loop_turn(i, j):
            return tied_span(tangents[i][0] - h, tangents[j][0] + h)

        first = 0
        for j, (sj, _) in enumerate(tangents):
            while sj - tangents[first][0] > V_MAX_ARC + 1e-9:
                first += 1
            for i in range(first, j):
                value = math.degrees(abs(headings[j] - headings[i]))
                if tied_loop_turn(i, j):
                    continue
                if value > m["v_deg"]:
                    si = tangents[i][0]
                    m["v_deg"] = value
                    m["v_arc"] = sj - si
                    m["v_at"] = at((si + sj) / 2.0)
    return m


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return None
    x = (len(ordered) - 1) * fraction
    i = int(math.floor(x))
    j = min(i + 1, len(ordered) - 1)
    return ordered[i] + (ordered[j] - ordered[i]) * (x - i)


def kink_checks(L, dist_mode):
    count, msgs, records = 0, [], []
    for pi, p in enumerate(L["pieces"]):
        cable_ties = [
            (d[1], d[2]) for d in p["decals"] if d[0] == "CableTie"
        ]
        frays = [
            (d[1], d[2]) for d in p["decals"]
            if d[0] in ("FrayLive", "FrayDead")
        ]
        for si, strand in enumerate(p["strands"]):
            if len(strand) < 2:
                continue
            fray_ends = tuple(
                any(dist(point, fray) <= FRAY_END_TOL for fray in frays)
                for point in (strand[0], strand[-1])
            )
            m = strand_metrics(strand, cable_ties, fray_ends)
            label = f"{piece_name(p, pi)} strand[{si}]"
            records.append((label, m))
            reasons = []
            if m["radius"] < KINK_MIN_RADIUS:
                reasons.append(
                    f"radius={m['radius']:.4f}<{KINK_MIN_RADIUS:.3f} cell "
                    f"at {xy_text(m['radius_at'])} "
                    f"(curvature={m['curvature']:.3f}/cell)"
                )
            if m["saw_deg"] >= SAW_MIN_OPPOSITE_DEG:
                reasons.append(
                    f"saw={m['saw_deg']:.2f}>={SAW_MIN_OPPOSITE_DEG:.1f} deg "
                    f"at {xy_text(m['saw_at'])}, "
                    f"opposite-peak gap={m['saw_gap']:.3f} cell"
                )
            if m["v_deg"] > V_MAX_TURN_DEG:
                reasons.append(
                    f"V-turn={m['v_deg']:.2f}>{V_MAX_TURN_DEG:.1f} deg "
                    f"in {m['v_arc']:.3f} cell at {xy_text(m['v_at'])}"
                )
            if reasons:
                count += 1
                msgs.append(
                    f"kink {label}: " + "; ".join(reasons)
                    + f"; length={m['length']:.3f}, vertices={m['vertices']}"
                )

    if dist_mode:
        msgs.append(
            "dist thresholds: "
            f"radius<{KINK_MIN_RADIUS:.3f} cell; "
            f"saw>={SAW_MIN_OPPOSITE_DEG:.1f} deg within "
            f"{SAW_MAX_SEPARATION:.3f} cell; "
            f"V-turn>{V_MAX_TURN_DEG:.1f} deg within {V_MAX_ARC:.3f} cell; "
            f"end-ignore={KINK_END_IGNORE:.3f} cell"
        )
        for label, m in records:
            radius = "inf" if math.isinf(m["radius"]) else f"{m['radius']:.4f}"
            location = (
                xy_text(m["radius_at"]) if m["radius_at"] is not None else "-"
            )
            msgs.append(
                f"dist strand {label}: length={m['length']:.3f} "
                f"kappa_max={m['curvature']:.4f}/cell "
                f"radius_min={radius} at {location}; "
                f"saw_max={m['saw_deg']:.2f} deg "
                f"at {xy_text(m['saw_at']) if m['saw_at'] else '-'}; "
                f"V_max={m['v_deg']:.2f} deg "
                f"at {xy_text(m['v_at']) if m['v_at'] else '-'}; "
                f"radius_samples={m['radius_samples']} "
                f"tangent_samples={m['tangent_samples']}"
            )

        # Quantiles are over one maximum per measured strand, not over vertices.
        groups = (
            ("kappa_max /cell", [
                m["curvature"] for _, m in records if m["radius_samples"]
            ]),
            ("saw_max deg", [
                m["saw_deg"] for _, m in records if m["radius_samples"]
            ]),
            ("V_max deg", [
                m["v_deg"] for _, m in records if m["tangent_samples"] >= 2
            ]),
        )
        for title, values in groups:
            summary = " ".join(
                f"p{int(q * 100):02d}={percentile(values, q):.4f}"
                for q in (0, .5, .75, .9, .95, .99, 1)
            ) if values else "no measurable strands"
            msgs.append(f"dist {title}: n={len(values)} {summary}")

        short = sum(m["radius_samples"] == 0 for _, m in records)
        msgs.append(
            f"dist coverage: strands={len(records)}, "
            f"without radius support after end trimming={short}"
        )
    return count, msgs


def consumer_machine_indices(piece, machines):
    """Resolve consumer ownership by machine identity, footprint, or hookup."""
    result = set()
    for name in (piece["a"], piece["b"]):
        if not name.startswith("consumer:"):
            continue
        candidates = [
            mi for mi, m in enumerate(machines)
            if int(m["kind"]) in (2, 3)
        ]
        exact = [mi for mi in candidates if machines[mi]["id"] == name]
        if exact:
            result.update(exact)
            continue
        try:
            fields = name.split(":", 1)[1].split(",")
            cell = tuple(int(value) for value in fields)
            if len(cell) != 2:
                continue
        except ValueError:
            continue
        x, z = cell
        result.update(
            mi for mi in candidates
            if (
                machines[mi]["x"] <= x < machines[mi]["x"] + machines[mi]["w"]
                and machines[mi]["z"] <= z < machines[mi]["z"] + machines[mi]["h"]
            ) or any(tuple(h[:2]) == cell for h in machines[mi].get("hookups", []))
        )
    return result


def lamp_reversal_checks(W, L, records):
    """Check PlugTop ends on consumer pieces with no CableTie decal.

    Use the original first-cell arc window and thresholds, excluding segments
    touching points hidden inside the piece's own consumer machine footprint.
    Do not bridge excluded points when measuring turns.
    The heading measurement uses the segment containing arc 0.3 (the final
    segment when the strand is shorter). Tied loops are deliberate.
    Count each failing strand once, reporting both ends when necessary.
    """
    tops = [r for r in records if r["d"][0] == "PlugTop"]
    count, msgs = 0, []
    for pi, p in enumerate(L["pieces"]):
        if not (p["a"].startswith("consumer:")
                or p["b"].startswith("consumer:")):
            continue
        if any(d[0] == "CableTie" for d in p["decals"]):
            continue
        own = [
            W["machines"][mi]
            for mi in consumer_machine_indices(p, W["machines"])
        ]

        def hidden(point):
            return any(
                m["x"] <= point[0] < m["x"] + m["w"]
                and m["z"] <= point[1] < m["z"] + m["h"]
                for m in own
            )

        for si, strand in enumerate(p["strands"]):
            if len(strand) < 2:
                continue
            reasons = []
            for side, vertices in (
                    ("first", strand), ("last", list(reversed(strand)))):
                possible = [
                    (dist(vertices[0], plugtop_cord(r["d"])), r["d"])
                    for r in tops if pi in r["pieces"]
                    and dist(vertices[0], plugtop_cord(r["d"])) <= FIT_END_TOL
                ]
                if not possible:
                    continue
                _, decal = min(possible, key=lambda item: item[0])
                axis = (math.cos(decal[3]), math.sin(decal[3]))
                run, turn, heading = 0.0, 0.0, 0.0
                initial, previous, back_at = None, None, None
                for a, b in zip(vertices, vertices[1:]):
                    if run >= 1.0:
                        break
                    vector = (b[0] - a[0], b[1] - a[1])
                    length = math.hypot(*vector)
                    if length <= 1e-10:
                        continue
                    if hidden(a) or hidden(b):
                        previous = None
                        run += length
                        continue
                    tangent = (vector[0] / length, vector[1] / length)
                    if initial is None:
                        initial = tangent
                    if previous is not None:
                        turn += abs(bend_angle(previous, tangent))
                    if run <= 0.3:
                        heading = abs(math.degrees(bend_angle(axis, tangent)))
                    if (back_at is None
                            and tangent[0] * initial[0]
                            + tangent[1] * initial[1] < 0):
                        back_at = run
                    previous = tangent
                    run += length
                if initial is None:
                    continue
                failures = []
                degrees = math.degrees(turn)
                if degrees > 100.0:
                    failures.append(
                        f"absolute turn={degrees:.2f}>100 deg"
                    )
                if heading > 25.0:
                    failures.append(
                        f"heading at arc {min(0.3, run):.3f}="
                        f"{heading:.2f}>25 deg off decal"
                    )
                if back_at is not None:
                    failures.append(
                        f"tangent dot initial<0 at arc {back_at:.3f}"
                    )
                if failures:
                    reasons.append(
                        f"{side} PlugTop at "
                        f"{xy_text((decal[1], decal[2]))}, "
                        f"decal heading={decal[3]:.4f} rad: "
                        + "; ".join(failures)
                    )
            if reasons:
                count += 1
                msgs.append(
                    f"lamp_reversal {piece_name(p, pi)} strand[{si}]: "
                    + " | ".join(reasons)
                )
    return count, msgs


def lamp_base_checks(W, L):
    """Check one nearest strand end per consumer piece and machine.

    Search all strands against the base target, including dive continuations.
    A selected end farther than 0.4 cell from the centroid is not a lamp end.
    The legacy ID file alone never labels a machine unless it is a 1x1
    consumer with exactly one assigned piece.
    """
    machines = W.get("machines", [])
    has_defs = any("def" in m for m in machines)
    has_offsets = any(float(m.get("baseDz", 0)) != 0 for m in machines)
    legacy_ids = set()
    legacy_present = False
    if not has_defs:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "Transient", "lab", "ba", "lamps.json",
        )
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                ids = json.load(f)
            if not isinstance(ids, list):
                raise ValueError("Transient/lab/ba/lamps.json must be a list of machine ids")
            legacy_ids = {str(value) for value in ids}
            legacy_present = True
        elif not has_offsets:
            return 0, ["lamp_base: no lamp data"]

    def centroid(m):
        return m["x"] + m["w"] / 2.0, m["z"] + m["h"] / 2.0

    owned = [[] for _ in machines]
    for pi, p in enumerate(L["pieces"]):
        ends = [
            (si, side, tuple(point[:2]))
            for si, strand in enumerate(p["strands"]) if len(strand) >= 2
            for side, point in (("first", strand[0]), ("last", strand[-1]))
        ]
        if not ends:
            continue
        for mi in sorted(consumer_machine_indices(p, machines)):
            m = machines[mi]
            cx, cz = centroid(m)
            dz = float(m.get("baseDz", 0))
            if dz == 0 and m.get("def") in LAMP_BASE_DEFS:
                dz = -0.25
            if (dz == 0 and not has_defs and legacy_present
                    and str(m["id"]) in legacy_ids
                    and int(m["kind"]) == 2 and m["w"] == 1 and m["h"] == 1):
                dz = -0.25
            target = (cx, cz + dz)
            si, side, point = min(
                ends, key=lambda end: dist(end[2], target)
            )
            if dist(point, (cx, cz)) > 0.4 + 1e-9:
                continue
            owned[mi].append((pi, si, side, point))

    count, msgs = 0, []
    for mi, m in enumerate(machines):
        # Feet and wall homes have separate, intentional endpoint rules.
        if m.get("foot", False) or m.get("home") is not None:
            continue
        dz = float(m.get("baseDz", 0))
        if dz == 0 and m.get("def") in LAMP_BASE_DEFS:
            dz = -0.25
        if (dz == 0 and not has_defs and legacy_present
                and str(m["id"]) in legacy_ids
                and int(m["kind"]) == 2 and m["w"] == 1 and m["h"] == 1
                and len(owned[mi]) == 1):
            dz = -0.25
        if dz == 0:
            continue
        cx, cz = centroid(m)
        target = (cx, cz + dz)
        for pi, si, side, point in owned[mi]:
            gap = dist(point, target)
            failures = []
            if gap > 0.12 + 1e-9:
                failures.append(f"base gap={gap:.3f}>0.120 cell")
            if point[1] > cz - 0.1 + 1e-9:
                failures.append(
                    f"bulb-side z={point[1]:.3f}>{cz - 0.1:.3f}"
                )
            if failures:
                count += 1
                msgs.append(
                    f"lamp_base {piece_name(L['pieces'][pi], pi)} "
                    f"strand[{si}] {side}: machine {m['id']} "
                    f"end={xy_text(point)}, base={xy_text(target)}; "
                    + "; ".join(failures)
                )
    return count, msgs


def wall_cross_checks(W, L, records):
    blocked = {(b[0], b[1]) for b in W["blocked"]}
    doors = {tuple(d[:2]) for d in W.get("doors", [])}
    plates = [
        (r["d"][1], r["d"][2]) for r in records
        if r["d"][0] in ("StubWall", "WallOutlet")
    ]
    count, msgs = 0, []
    for pi, p in enumerate(L["pieces"]):
        for si, strand in enumerate(p["strands"]):
            previous, run, start = None, 0, 0
            longest, best_start, best_end, best_cell = 0, 0, 0, None
            for vi, v in enumerate(strand):
                point = tuple(v[:2])
                cell = (math.floor(point[0]), math.floor(point[1]))
                bad = (
                    cell in blocked and cell not in doors
                    and not any(dist(point, q) <= 0.25 for q in plates)
                )
                if bad:
                    if cell == previous:
                        run += 1
                    else:
                        run, start = 1, vi
                    if run > longest:
                        longest = run
                        best_start, best_end, best_cell = start, vi, cell
                    previous = cell
                else:
                    previous, run = None, 0
            if longest >= 3:
                count += 1
                msgs.append(
                    f"wall_cross {piece_name(p, pi)} strand[{si}]: "
                    f"{longest} consecutive vertices in blocked cell "
                    f"{best_cell}, vertices[{best_start}..{best_end}], "
                    f"{xy_text(strand[best_start])} -> "
                    f"{xy_text(strand[best_end])}"
                )
    return count, msgs


def new_checks(W, L, dist_mode=False):
    counts = {
        "lead_device": 0, "loose_plug": 0,
        "double_cord": 0, "wall_vanish": 0, "wall_cross": 0, "kink": 0,
        "wall_via_socket": 0, "lamp_reversal": 0, "lamp_base": 0,
    }
    msgs = []
    machines = W["machines"]
    records = unique_decals(L)

    ends = []
    piece_ends = [[] for _ in L["pieces"]]
    for pi, p in enumerate(L["pieces"]):
        for si, strand in enumerate(p["strands"]):
            if len(strand) < 2:
                continue
            for side, point in (("first", strand[0]), ("last", strand[-1])):
                ei = len(ends)
                ends.append({
                    "xy": tuple(point[:2]), "pi": pi, "si": si, "side": side
                })
                piece_ends[pi].append(ei)

    def end_label(ei):
        e = ends[ei]
        return (
            f"{piece_name(L['pieces'][e['pi']], e['pi'])} "
            f"strand[{e['si']}] {e['side']}"
        )

    # Match separately emitted wall Plug decals to their WallOutlet assemblies.
    # An assembly gets one endpoint counter, not one counter per overlapping decal.
    wall_records = [r for r in records if r["d"][0] == "WallOutlet"]
    paired_plugs = set()
    wall_has_plug = set()
    for ri, r in enumerate(records):
        d = r["d"]
        if d[0] != "Plug":
            continue
        head = local_axis_point(d, PLUG_HEAD_X * d[4])
        possible = []
        for wi, wr in enumerate(wall_records):
            wd = wr["d"]
            if not (r["pieces"] & wr["pieces"]):
                continue
            if math.cos(d[3] - wd[3]) < WALL_PAIR_ANGLE_COS:
                continue
            gap = dist(head, (wd[1], wd[2]))
            if gap <= WALL_PAIR_HEAD_TOL:
                possible.append((gap, wi))
        if possible:
            _, wi = min(possible)
            paired_plugs.add(ri)
            wall_has_plug.add(wi)

    fittings = []
    for ri, r in enumerate(records):
        d = r["d"]
        kind = d[0]
        if kind == "Plug" and ri not in paired_plugs:
            point = local_axis_point(d, PLUG_CORD_X * d[4])
        elif kind == "PlugTop":
            point = plugtop_cord(d)
        elif kind == "WallOutlet":
            point = wall_cord_seat(d)
        else:
            continue
        fittings.append({
            "d": d, "xy": point, "pieces": r["pieces"],
            "ends": [], "record": ri,
        })

    # Assign each actual strand end to at most one fitting. Nearby sockets do not
    # all claim the same end merely because their tolerance circles overlap.
    for ei, e in enumerate(ends):
        possible = [
            (dist(e["xy"], f["xy"]), fi)
            for fi, f in enumerate(fittings)
            if dist(e["xy"], f["xy"]) <= FIT_END_TOL
        ]
        if possible:
            _, fi = min(possible)
            fittings[fi]["ends"].append(ei)

    for f in fittings:
        if len(f["ends"]) > 1:
            counts["double_cord"] += 1
            msgs.append(
                f"double_cord {f['d'][0]} at "
                f"{xy_text((f['d'][1], f['d'][2]))}, "
                f"cord point {xy_text(f['xy'])}: "
                f"{len(f['ends'])} strand ends; "
                + "; ".join(end_label(ei) for ei in f["ends"])
            )

    # Only unmatched side-view Plugs are machine fittings. Wall-seated Plugs were
    # consumed by the assembly matching above.
    for f in fittings:
        d = f["d"]
        if d[0] != "Plug":
            continue
        head = local_axis_point(d, PLUG_HEAD_X * d[4])
        candidates = intended_machines(f["pieces"], L, machines)
        machine = min(
            candidates, key=lambda m: machine_distance(head, m), default=None
        )
        reasons = []
        if not f["ends"]:
            nearest = min(
                (dist(f["xy"], e["xy"]) for e in ends), default=math.inf
            )
            reasons.append(
                f"no strand end at cord point {xy_text(f['xy'])}; "
                f"nearest end={nearest:.3f} cell, tolerance={FIT_END_TOL:.3f}"
            )
        if machine is None:
            reasons.append(f"head {xy_text(head)} has no candidate machine")
        else:
            gap = machine_distance(head, machine)
            pad = LAMP_HEAD_PAD if int(machine["kind"]) == 3 else MACHINE_HEAD_PAD
            if gap > pad:
                reasons.append(
                    f"head {xy_text(head)} is {gap:.3f} cell outside "
                    f"machine {machine['id']} kind={machine['kind']} "
                    f"rect=({machine['x']},{machine['z']},"
                    f"{machine['w']},{machine['h']}), allowance={pad:.3f}"
                )
        if reasons:
            counts["loose_plug"] += 1
            owners = "; ".join(
                piece_name(L["pieces"][pi], pi) for pi in sorted(f["pieces"])
            )
            msgs.append(
                f"loose_plug at {xy_text((d[1], d[2]))}: "
                + "; ".join(reasons) + "; " + owners
            )

    # A direct device branch must arrive at a socket-seated PlugTop.
    # A valid socket fit takes precedence over proximity to the captive lead:
    # the final socket and lead can be close after rotation/scaling.
    strips = [
        r["d"] for r in records
        if r["d"][0] in ("PowerStrip", "PowerStripDark")
    ]
    top_fittings = [f for f in fittings if f["d"][0] == "PlugTop"]

    # A wall feed must use the strip's captive lead. Match both ends of the
    # SAME strand, and require the PlugTop centre to lie on an actual socket.
    # The strand meets the PlugTop's boot, not its socket-centred decal origin.
    wall_points = [
        (r["d"], wall_cord_seat(r["d"])) for r in records
        if r["d"][0] in ("WallOutlet", "StubWall")
    ]
    seated_tops = [
        (f, st, k)
        for f in top_fittings
        for st in strips
        for k, hx in enumerate(STRIP_HEADS)
        if dist(
            (f["d"][1], f["d"][2]),
            strip_pt(st, hx, STRIP_HEAD_Z),
        ) <= SOCKET_CENTRE_TOL
    ]
    for pi, p in enumerate(L["pieces"]):
        for si, strand in enumerate(p["strands"]):
            if len(strand) < 2:
                continue
            for wall_end, strip_end in (
                    (strand[0], strand[-1]), (strand[-1], strand[0])):
                wall_match = next(
                    (q for q in wall_points
                     if dist(wall_end, q[1]) <= FIT_END_TOL), None
                )
                socket_match = next(
                    (q for q in seated_tops
                     if dist(strip_end, q[0]["xy"]) <= FIT_END_TOL), None
                )
                if wall_match is None or socket_match is None:
                    continue
                wd, wall_point = wall_match
                fitting, st, k = socket_match
                lead = strip_pt(st, *STRIP_LEAD)
                counts["wall_via_socket"] += 1
                msgs.append(
                    f"wall_via_socket {piece_name(p, pi)} strand[{si}]: "
                    f"{wd[0]} cord point {xy_text(wall_point)} -> "
                    f"strip socket[{k}] PlugTop at "
                    f"{xy_text((fitting['d'][1], fitting['d'][2]))}; "
                    f"strip end={xy_text(strip_end)}, "
                    f"captive lead={xy_text(lead)}, "
                    f"lead gap={dist(strip_end, lead):.3f}"
                )
                break                       # count each strand once

    for pi, p in enumerate(L["pieces"]):
        kinds = name_kinds(p["a"], machines) | name_kinds(p["b"], machines)
        if not (kinds & {2, 3}):
            continue
        for st in strips:
            if abs(st[4]) < 1e-10:
                continue
            lead = strip_pt(st, *STRIP_LEAD)
            sockets = [strip_pt(st, hx, STRIP_HEAD_Z) for hx in STRIP_HEADS]
            socket_tops = [
                f for f in top_fittings
                if any(
                    dist((f["d"][1], f["d"][2]), sk) <= SOCKET_CENTRE_TOL
                    for sk in sockets
                )
            ]
            anchors = [lead] + [f["xy"] for f in socket_tops]
            possible = []
            for ei in piece_ends[pi]:
                e = ends[ei]["xy"]
                ux, uz = e[0] - st[1], e[1] - st[2]
                lx = (ux * math.cos(st[3]) + uz * math.sin(st[3])) / st[4]
                lz = (-ux * math.sin(st[3]) + uz * math.cos(st[3])) / st[4]
                edge_gap = math.hypot(
                    max(abs(lx) - .45, 0.0),
                    max(abs(lz) - .09, 0.0),
                ) * abs(st[4])
                if edge_gap <= STRIP_CONNECTION_PAD:
                    possible.append((
                        min(dist(e, a) for a in anchors), ei
                    ))
            if not possible:
                continue
            # One device-to-strip connection per piece/strip. Wall-separated
            # fragments in that piece must not count as additional connections.
            _, ei = min(possible)
            if any(ei in f["ends"] for f in socket_tops):
                continue

            e = ends[ei]["xy"]
            lead_gap = dist(e, lead)
            nearest_socket = min(range(len(sockets)), key=lambda k: dist(e, sockets[k]))
            reason = (
                "device uses captive lead/end cap"
                if lead_gap <= LEAD_END_TOL
                else "device connection is not a socket-seated PlugTop"
            )
            counts["lead_device"] += 1
            msgs.append(
                f"lead_device {end_label(ei)} at {xy_text(e)}: {reason}; "
                f"strip centre={xy_text((st[1], st[2]))}, "
                f"angle={st[3]:.4f}, scale={st[4]:.4f}; "
                f"lead={xy_text(lead)}, lead gap={lead_gap:.3f}; "
                f"nearest socket[{nearest_socket}]="
                f"{xy_text(sockets[nearest_socket])}"
            )

    # Unlike dead_end, a bare wall face is not an explanation.
    blocked = {(b[0], b[1]) for b in W["blocked"]}
    allowed_wall_points = []
    for r in records:
        d = r["d"]
        if d[0] in ("WallOutlet", "StubWall"):
            allowed_wall_points.append((
                wall_cord_seat(d), FIT_END_TOL, d[0]
            ))
        elif d[0] in ("FrayLive", "FrayDead"):
            allowed_wall_points.append((
                (d[1], d[2]), FRAY_END_TOL, d[0]
            ))

    for ei, e in enumerate(ends):
        point = e["xy"]
        hit = []
        for x in range(math.floor(point[0] - WALL_END_PAD),
                       math.floor(point[0] + WALL_END_PAD) + 1):
            for z in range(math.floor(point[1] - WALL_END_PAD),
                           math.floor(point[1] + WALL_END_PAD) + 1):
                if (x, z) in blocked:
                    gap = box_distance(point, x, z, 1, 1)
                    if gap <= WALL_END_PAD + 1e-9:
                        hit.append((x, z, gap))
        if not hit:
            continue
        if any(dist(point, q) <= tolerance
               for q, tolerance, _ in allowed_wall_points):
            continue
        counts["wall_vanish"] += 1
        nearest = min(
            ((dist(point, q), kind, q)
             for q, _, kind in allowed_wall_points),
            default=None,
        )
        detail = (
            f"; nearest allowed fitting={nearest[1]} "
            f"at {xy_text(nearest[2])}, gap={nearest[0]:.3f}"
            if nearest is not None else "; no allowed fittings"
        )
        msgs.append(
            f"wall_vanish {end_label(ei)} at {xy_text(point)}: "
            f"blocked cells="
            + ",".join(f"({x},{z};gap={gap:.3f})" for x, z, gap in hit)
            + detail
        )

    counts["wall_cross"], cross_msgs = wall_cross_checks(W, L, records)
    msgs.extend(cross_msgs)
    counts["lamp_reversal"], reversal_msgs = lamp_reversal_checks(W, L, records)
    msgs.extend(reversal_msgs)
    counts["lamp_base"], base_msgs = lamp_base_checks(W, L)
    msgs.extend(base_msgs)
    counts["kink"], kink_msgs = kink_checks(L, dist_mode)
    msgs.extend(kink_msgs)
    return counts, msgs


def parent_no_cord(W):
    rows = W.get("machines", []) + W.get("unhooked", [])
    if not W.get("connectParentData", False) and not any(
            "connectParent" in m for m in rows):
        return 0, ["no connectParent data"]
    msgs, seen = [], set()
    for m in rows:
        if m.get("connectParent") is None or m.get("parentDraw") == "PatchCable":
            continue
        if (m.get("hookups") or m.get("links")
                or m.get("hasHookup", False) or m.get("hasLink", False)):
            continue
        if m["id"] in seen:
            continue
        seen.add(m["id"])
        msgs.append(
            f"parent_no_cord {m['id']} "
            f"rect=({m['x']},{m['z']},{m['w']},{m['h']}) "
            f"connectParent={m['connectParent']}: no hookup/link"
        )
    return len(msgs), msgs


def lab_checks(W, L, dist_mode=False):
    validate_laid(L)
    parent_count, msgs = parent_no_cord(W)
    out = {"parent_no_cord": parent_count}
    decals = [d for p in L["pieces"] for d in p["decals"]]
    ends = []
    for p in L["pieces"]:
        for s in p["strands"]:
            if len(s) >= 2:
                ends.append(tuple(s[0][:2])); ends.append(tuple(s[-1][:2]))
    strips = [d for d in decals if d[0] in ("PowerStrip", "PowerStripDark")]
    # side_entry: a side-view plug whose head (art +0.46) pushes into a strip's outline (+0.05): plugged into the strip's edge
    side = 0
    for d in decals:
        if d[0] != "Plug":
            continue
        hx, hz = d[1] + math.cos(d[3]) * 0.46 * d[4], d[2] + math.sin(d[3]) * 0.46 * d[4]
        if any(m["x"] <= hx <= m["x"] + m["w"] and m["z"] <= hz <= m["z"] + m["h"] for m in W["machines"]):
            continue                      # a machine's own plug, drawn under its building
        for st in strips:
            ux, uz = hx - st[1], hz - st[2]
            al = ux * math.cos(st[3]) + uz * math.sin(st[3]); ac = -ux * math.sin(st[3]) + uz * math.cos(st[3])
            if abs(al) <= 0.45 * st[4] + 0.05 and abs(ac) <= 0.09 * st[4] + 0.05:
                side += 1; msgs.append(f"side_entry plug at ({d[1]:.2f},{d[2]:.2f})"); break
    out["side_entry"] = side
    # uncovered: an occupied socket (a cord end within 0.18 of it, not on the lead) with no PlugTop centred on it
    unc = 0
    tops = [d for d in decals if d[0] == "PlugTop"]
    for st in strips:
        lead = strip_pt(st, *STRIP_LEAD)
        for k, hx in enumerate(STRIP_HEADS):
            sk = strip_pt(st, hx, STRIP_HEAD_Z)
            occ = [e for e in ends if dist(e, sk) < 0.18 and dist(e, lead) > 0.05]
            if not occ:
                continue
            if not any(dist((t[1], t[2]), sk) < 0.02 for t in tops):
                unc += 1; msgs.append(f"uncovered socket {k} of strip at ({st[1]:.2f},{st[2]:.2f})")
    out["uncovered"] = unc
    # wall_no_plug: a strip-look wall stub drawn with the hole plate
    strip_cells = {tuple(c) for c in W.get("strips", [])}
    wnp = 0
    for p in L["pieces"]:
        for nm in (p["a"], p["b"]):
            if not nm.startswith("stub_wall:"):
                continue
            x, z = (int(v) for v in nm.split(":")[1].split(","))
            if (x, z) not in strip_cells:
                continue
            if any(d[0] in ("FrayLive", "FrayDead") for d in p["decals"]):
                continue                      # a cut wall terminal hangs loose by design
            near = [d for d in p["decals"] if d[0] in ("StubWall", "WallOutlet") and abs(d[1] - (x + 0.5)) < 1.2 and abs(d[2] - (z + 0.5)) < 1.2]
            if not any(d[0] == "WallOutlet" for d in near):
                wnp += 1; msgs.append(f"wall_no_plug at {nm}")
    out["wall_no_plug"] = wnp
    # dead_end
    mach = W["machines"]
    blocked = {(b[0], b[1]) for b in W["blocked"]}

    def explained(e, i):
        if any(m["x"] - 0.15 <= e[0] <= m["x"] + m["w"] + 0.15 and m["z"] - 0.15 <= e[1] <= m["z"] + m["h"] + 0.15 for m in mach):
            return True
        if (math.floor(e[0]), math.floor(e[1])) in blocked or any((math.floor(e[0] + dx), math.floor(e[1] + dz)) in blocked for dx, dz in ((0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1))):
            return True
        for d in decals:
            if dist(e, (d[1], d[2])) <= 0.5 * d[4] + 0.12:
                return True
        return any(j != i and dist(e, f) < 0.05 for j, f in enumerate(ends))
    dead = [e for i, e in enumerate(ends) if not explained(e, i)]
    out["dead_end"] = len(dead)
    msgs += [f"dead_end at ({e[0]:.2f},{e[1]:.2f})" for e in dead[:20]]
    # undrawn transmitters
    def touch(a, b):
        ox = a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]; oz = a["z"] < b["z"] + b["h"] and b["z"] < a["z"] + a["h"]
        tx = a["x"] + a["w"] == b["x"] or b["x"] + b["w"] == a["x"]; tz = a["z"] + a["h"] == b["z"] or b["z"] + b["h"] == a["z"]
        return (oz and tx) or (ox and tz)
    ts = [m for m in mach if m["id"].startswith("t")]
    fed = [m for m in ts if not m["hookups"] and not m.get("links") and any(o is not m and (o["hookups"] or o.get("links")) and touch(m, o) for o in ts)]
    und = 0
    for m in fed:
        if not any(m["x"] - 0.2 <= e[0] <= m["x"] + m["w"] + 0.2 and m["z"] - 0.2 <= e[1] <= m["z"] + m["h"] + 0.2 for e in ends):
            und += 1; msgs.append(f"undrawn transmitter {m['id']} at {m['x']},{m['z']}")
    out["undrawn"] = und

    extra, extra_msgs = new_checks(W, L, dist_mode)
    out.update(extra)
    msgs.extend(extra_msgs)
    return out, msgs


def baked(tex):
    from PIL import Image
    import numpy as np
    bad, msgs = 0, []
    for p in sorted(glob.glob(os.path.join(tex, "**", "*.png"), recursive=True)):
        n = os.path.basename(p)[:-4]
        if n not in ("Plug", "StubWall", "StubRock", "Junction_T", "Junction_X", "Junction_Tape", "Junction_Tin"):
            continue
        a = np.array(Image.open(p).convert("RGBA"))[..., 3] > 100
        H, Wd = a.shape
        if n == "Plug":
            hit = a[:, : int(0.15 * Wd)].sum()              # behind the boot, where the code's cord runs in
        elif n in ("StubWall", "StubRock"):
            hit = a[:, : int(0.06 * Wd)].sum()              # the cord side (art -X): the plate / rim never reaches the canvas edge
        else:
            cy = H / 2 + (0.152 * H if n in ("Junction_T", "Junction_Tape") else 0)   # the T's arms meet above the centre (TapeAnchorZ, art +Z = up)
            cy = H / 2 - 0.152 * H if n in ("Junction_T", "Junction_Tape") else H / 2
            r = (ARM_TUCK + 0.04) * Wd
            yy, xx = np.mgrid[0:H, 0:Wd]
            hit = (a & (np.hypot(xx - Wd / 2, yy - cy) > r)).sum()
        if hit > 0:
            bad += 1; msgs.append(f"baked_stub {os.path.relpath(p, tex)}: {int(hit)} px")
    return bad, msgs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("world"); ap.add_argument("laid")
    ap.add_argument("--tex"); ap.add_argument("--json")
    ap.add_argument(
        "--dist", action="store_true",
        help="print per-strand bend measurements and percentile distributions",
    )
    a = ap.parse_args()
    try:
        with open(a.world, encoding="utf-8") as f:
            W = json.load(f)
        with open(a.laid, encoding="utf-8") as f:
            L = json.load(f)
        out, msgs = lab_checks(W, L, a.dist)
    except ValueError as exc:
        ap.error(str(exc))
    if a.tex:
        out["baked_stub"], m2 = baked(a.tex); msgs += m2
    print(" ".join(f"{k}={v}" for k, v in out.items()))
    # Do not truncate: every flagged strand and all --dist records must print.
    for m in msgs:
        print("  " + m)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"counts": out, "msgs": msgs}, f, indent=1)
    sys.exit(1 if any(out.values()) else 0)
