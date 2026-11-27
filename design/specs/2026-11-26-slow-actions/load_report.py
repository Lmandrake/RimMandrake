#!/usr/bin/env python3
"""Read one load_sample.py run and print the tables of load_users.md.

  python3 load_report.py DIR

DIR holds linux.json and win.jsonl (load_sample.py), and two files read on the same machine at the end:
  timers.txt   `systemctl --user list-timers --all --no-legend` (which services a timer starts)
  journal.txt  `journalctl --user --since <t0> --until <t1> -o cat | grep -E ': Consumed |^Started run-'` (systemd's own CPU per run)
Item RIMMANDRAKE_FIND_LOAD_USERS_RM_TIMERS_ONLY_TEN_PERCENT.
"""
import collections, json, os, re, sys

APP = "/user.slice/user-1000.slice/user@1000.service/app.slice/"
SEATS = "/user.slice/user-1000.slice/user@1000.service/claude.slice/"
UNIT = re.compile(r"^(?P<u>[\w@.\-\\:]+?)\.(service|scope|slice)$")


def timer_units(path):
    out = set()
    if os.path.exists(path):
        for line in open(path):
            m = re.findall(r"(\S+\.timer)\s+(\S+\.service)", line)
            for t, s in m:
                out.add(s)
    return out


def klass(cg, timers):
    """The class of one cgroup path, and the unit it names."""
    if cg == "/":
        return "kernel threads (the root cgroup's own)", "/"
    if cg == APP.rstrip("/"):
        return "user units that began and ended between two samples", "app.slice"
    if cg.startswith(APP):
        unit = cg[len(APP):].split("/")[0]
        if unit in timers:
            return "rm timer" if unit.startswith("rm-") else "other timer", unit
        if unit.startswith("rm-detached-"):
            return "rm helper run (detached)", unit
        if unit.startswith("load-census"):
            return "this sample", unit
        if unit.startswith("rm-"):
            return "rm service, no timer", unit
        return "other user service", unit
    if cg.startswith(SEATS):
        # claude.slice/claude-seats.slice/claude-seat-<SEAT>-<rest>.scope/{seat,claude-code-bash}: the model process
        # ("seat") and its tool commands ("claude-code-bash"). A detached helper's scope names its rm-detached unit.
        parts = cg[len(SEATS):].split("/")
        scope = parts[1] if len(parts) > 1 else ""
        part = parts[2] if len(parts) > 2 else ""
        tail = {"seat": ", model process", "claude-code-bash": ", tool commands"}.get(part, "")
        if "-rm-detached-" in scope:
            return "rm helper run (detached)" + tail, scope
        if scope.startswith("claude-seat-"):
            seat = scope[len("claude-seat-"):].rsplit("-", 1)[0]
            return f"Claude window, seat {seat}" + tail, scope
        return "claude.slice, between scopes", "claude.slice"
    if "/session-" in cg:
        return "login session (ssh or wsl shell)", cg.split("/")[-1]
    if cg.startswith("/system.slice"):
        return "system service", (cg.split("/") + [""])[2] or "system.slice"
    if cg.startswith("/init.scope"):
        return "WSL init", "init.scope"
    return "other", cg


def children(cgs):
    kids = collections.defaultdict(list)
    for k in cgs:
        if k == "/":
            continue
        parent = k.rsplit("/", 1)[0] or "/"
        kids[parent].append(k)
    return kids


def fmt_h(s):
    return f"{s / 3600:.2f}"


def main():
    d = sys.argv[1]
    L = json.load(open(os.path.join(d, "linux.json")))
    timers = timer_units(os.path.join(d, "timers.txt"))
    span = L["t1"] - L["t0"]
    ncpu = L["ncpu"]
    M = L["machine"]
    cgs = L["cgroups"]
    kids = children(cgs)
    print(f"## Linux (WSL) machine: {span / 60:.1f} min, {L['samples']} samples, {ncpu} CPUs, final={L['final']}")
    print(f"- CPU busy {M['busy_s'] / 3600:.2f} core-hours of {M['total_s'] / 3600:.2f} "
          f"({100 * M['busy_s'] / M['total_s']:.0f}%); iowait {M['iowait_s'] / 3600:.2f} core-hours")
    print(f"- page-ins (storage reads) {M['pgpgin_bytes'] / 1e9:.1f} GB ({M['pgpgin_bytes'] / span / 1e6:.0f} MB/s mean); "
          f"page-outs {M['pgpgout_bytes'] / 1e9:.1f} GB; swap-ins {M['pswpin_pages'] * 4096 / 1e9:.2f} GB, "
          f"swap-outs {M['pswpout_pages'] * 4096 / 1e9:.2f} GB; RAM {M['mem_total'] / 1e9:.1f} GB")
    ser = L["series"]
    if ser:
        sw = [s["swap_used"] for s in ser]
        av = [s["avail"] for s in ser]
        ld = [s["load"] for s in ser]
        print(f"- swap in use {min(sw) / 1e9:.1f} to {max(sw) / 1e9:.1f} GB; MemAvailable {min(av) / 1e9:.1f} to "
              f"{max(av) / 1e9:.1f} GB; load average {min(ld):.0f} to {max(ld):.0f}")
    # Per cgroup: own CPU = its total less its children's seen totals. A leaf is its own.
    own = {}
    for k, v in cgs.items():
        own[k] = v["cpu_s"] - sum(cgs[c]["cpu_s"] for c in kids.get(k, []))
    # Leaf units: group at unit level (a unit cgroup and all below it).
    by_unit = collections.defaultdict(lambda: {"cpu": 0.0, "mem": 0, "swap": 0, "class": ""})
    for k, v in cgs.items():
        c, unit = klass(k, timers)
        # a cgroup counts once: its own share
        u = by_unit[(c, unit)]
        u["cpu"] += own[k]
        u["class"] = c
    # memory: take the max at the unit's top cgroup
    for k, v in cgs.items():
        c, unit = klass(k, timers)
        if k.split("/")[-1] == unit:
            u = by_unit[(c, unit)]
            u["mem"] = max(u["mem"], v["mem_max"])
            u["swap"] = max(u["swap"], v["swap_max"])
    by_class = collections.defaultdict(float)
    for (c, unit), u in by_unit.items():
        by_class[c] += u["cpu"]
    total = M["busy_s"]
    print("\n### CPU by class of unit (core-hours in the window; share of busy CPU)\n")
    print("| class | core-hours | share |")
    print("|---|---|---|")
    for c, s in sorted(by_class.items(), key=lambda x: -x[1]):
        print(f"| {c} | {fmt_h(s)} | {100 * s / total:.1f}% |")
    print(f"| (machine busy, from /proc/stat) | {fmt_h(total)} | 100% |")
    print("\n### The 25 units that used the most CPU\n")
    print("| unit | class | core-hours | memory max GB | swap max GB |")
    print("|---|---|---|---|---|")
    for (c, unit), u in sorted(by_unit.items(), key=lambda x: -x[1]["cpu"])[:25]:
        print(f"| `{unit}` | {c} | {fmt_h(u['cpu'])} | {u['mem'] / 1e9:.2f} | {u['swap'] / 1e9:.2f} |")
    # Claude scopes: one row per window or helper run, model process and tool commands apart
    sc = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0, 0, False])
    for k, v in cgs.items():
        if not k.startswith(SEATS):
            continue
        parts = k[len(SEATS):].split("/")
        if len(parts) < 2:
            continue
        r = sc[parts[1]]
        part = parts[2] if len(parts) > 2 else ""
        if part == "seat":
            r[0] += v["cpu_s"]
        elif part == "claude-code-bash":
            r[1] += v["cpu_s"]
        elif part == "":
            r[2] += v["cpu_s"]
            r[3] = v["mem_max"]
            r[4] = v["swap_max"]
            r[5] = v["born_inside"]
    print("\n### Claude scopes: each window and each detached helper run (core-hours; memory includes page cache)\n")
    print("| scope | model process | tool commands | whole scope | memory max GB | swap max GB | began inside the window |")
    print("|---|---|---|---|---|---|---|")
    for name, r in sorted(sc.items(), key=lambda x: -x[1][2]):
        short = name.replace("claude-seat-", "").replace(".scope", "")
        print(f"| `{short}` | {fmt_h(r[0])} | {fmt_h(r[1])} | {fmt_h(r[2])} | {r[3] / 1e9:.2f} | {r[4] / 1e9:.2f} | {r[5]} |")
    ap_tot = cgs.get(APP.rstrip("/"), {}).get("cpu_s", 0)
    cl_tot = cgs.get(SEATS.rstrip("/"), {}).get("cpu_s", 0)
    print(f"\nExact totals of the long-lived slices: app.slice (every systemd user unit, timers included) "
          f"{fmt_h(ap_tot)} core-hours; claude-seats.slice (every Claude window and helper) {fmt_h(cl_tot)} core-hours; "
          f"root cgroup's own (kernel threads) {fmt_h(own.get('/', 0))} core-hours.")
    # helper runs and timers counted as one line each
    print(f"\nrm timer units seen: {sum(1 for (cc, _u) in by_unit if cc == 'rm timer')}")
    # memory now, by class
    print("\n### Memory at the last sample, by class (GB, cgroup memory.current; swap is memory.swap.current)\n")
    mem_c = collections.defaultdict(lambda: [0, 0])
    for k, v in cgs.items():
        c, unit = klass(k, timers)
        if v.get("gone"):
            continue
        if k.split("/")[-1] == unit and not unit.endswith(".slice") and unit != "/":
            c = c.replace(", model process", "").replace(", tool commands", "")
            mem_c[c][0] += v.get("mem_last") or 0
            mem_c[c][1] += v.get("swap_last") or 0
    print("| class | memory GB | swap GB |")
    print("|---|---|---|")
    for c, (m, s) in sorted(mem_c.items(), key=lambda x: -x[1][0]):
        print(f"| {c} | {m / 1e9:.2f} | {s / 1e9:.2f} |")
    # processes
    procs = L["procs"]
    psum = sum(p["cpu_s"] for p in procs)
    print(f"\n### Processes: {len(procs)} seen; their own CPU sums to {fmt_h(psum)} core-hours, "
          f"{100 * psum / total:.0f}% of busy (the rest ran between samples)\n")
    def pname(p):
        cmd = p["cmd"].split()
        if p["comm"].startswith("python") and len(cmd) > 1:
            arg = next((a for a in cmd[1:] if not a.startswith("-")), cmd[1])
            return "python " + os.path.basename(arg)
        if p["comm"] == "git" and len(cmd) > 1:
            sub = next((a for a in cmd[1:] if not a.startswith("-") and "=" not in a), "?")
            return "git " + sub
        return p["comm"]
    by_name = collections.defaultdict(lambda: [0.0, 0, 0, 0.0])
    for p in procs:
        r = by_name[pname(p)]
        r[0] += p["cpu_s"]
        r[1] += 1
        r[2] += p["rb"] or 0
        r[3] += p.get("child_cpu_s", 0)
    print("| process (name, script or git verb) | CPU core-hours | runs seen | storage reads GB | CPU of its ended children, core-hours |")
    print("|---|---|---|---|---|")
    for n, r in sorted(by_name.items(), key=lambda x: -x[1][0])[:30]:
        print(f"| `{n}` | {fmt_h(r[0])} | {r[1]} | {r[2] / 1e9:.2f} | {fmt_h(r[3])} |")
    rb_tot = sum(p["rb"] or 0 for p in procs)
    print(f"\n### Storage reads by process: {rb_tot / 1e9:.1f} GB attributed of {M['pgpgin_bytes'] / 1e9:.1f} GB page-ins\n")
    print("| process | storage reads GB | runs seen |")
    print("|---|---|---|")
    for n, r in sorted(by_name.items(), key=lambda x: -x[1][2])[:20]:
        print(f"| `{n}` | {r[2] / 1e9:.2f} | {r[1]} |")
    print("\n### Storage reads by class of unit (from the processes' cgroups)\n")
    rb_c = collections.defaultdict(int)
    for p in procs:
        rb_c[klass(p["cgroup"], timers)[0]] += p["rb"] or 0
    print("| class | storage reads GB |")
    print("|---|---|")
    for c, b in sorted(rb_c.items(), key=lambda x: -x[1]):
        print(f"| {c} | {b / 1e9:.2f} |")
    print("\n### The 15 largest resident processes (max RSS GB)\n")
    print("| process | cgroup class | RSS max GB | seen min |")
    print("|---|---|---|---|")
    for p in sorted(procs, key=lambda p: -p["rss_max"])[:15]:
        print(f"| `{pname(p)}` | {klass(p['cgroup'], timers)[0]} | {p['rss_max'] / 1e9:.2f} | {p['seen_s'] / 60:.0f} |")
    # journal cross-check
    jp = os.path.join(d, "journal.txt")
    if os.path.exists(jp):
        journal(jp, timers)
    wp = os.path.join(d, "win.jsonl")
    if os.path.exists(wp):
        win(wp)


def journal(jp, timers):
    """systemd's own `Consumed` line for each unit run that ended in the window. A run that began before the window
    counts whole. A `run-p<pid>-i<n>.scope` (systemd-run --scope) is named by the command its `Started` line shows."""
    rx = re.compile(r"^(\S+?): Consumed (?:(\d+)h )?(?:(\d+)min )?([\d.]+)(ms|s) CPU time")
    st = re.compile(r"^Started (run-\S+?\.scope) - \[systemd-run\] (.*)$")
    cmd_of = {}
    jc = collections.defaultdict(lambda: [0, 0.0])
    ju = collections.defaultdict(lambda: [0, 0.0, ""])
    for line in open(jp):
        line = line.strip()
        m = st.match(line)
        if m:
            cmd_of[m.group(1)] = m.group(2)
            continue
        m = rx.match(line)
        if not m:
            continue
        h, mi, v, unit = m.group(2), m.group(3), float(m.group(4)), m.group(5)
        sec = (int(h or 0) * 3600 + int(mi or 0) * 60) + (v / 1000 if unit == "ms" else v)
        name = m.group(1)
        if name.startswith("claude-seat-"):
            cls = klass(SEATS + "claude-seats.slice/" + name, timers)[0]
        elif name.startswith("run-"):
            w = cmd_of.get(name, "?").split()
            where = w[2] if len(w) > 2 and w[1] == "-C" else ""
            cls = "systemd-run scope: " + os.path.basename(w[0]) + (" " + w[3] if where else "") + (
                " in " + where if where else "")
        else:
            cls = klass(APP + name, timers)[0]
        jc[cls][0] += 1
        jc[cls][1] += sec
        key = re.sub(r"\d{6,}", "N", re.sub(r"-p\d+-i\d+", "-*", name))
        ju[key][0] += 1
        ju[key][1] += sec
        ju[key][2] = cls
    print("\n### systemd's own CPU per finished unit run in the window (journal `Consumed` lines)\n")
    print("| class | runs ended | CPU core-hours |")
    print("|---|---|---|")
    for c, (n, sec) in sorted(jc.items(), key=lambda x: -x[1][1]):
        print(f"| {c} | {n} | {fmt_h(sec)} |")
    print("\n| unit (numbers folded to N) | class | runs ended | CPU core-hours |")
    print("|---|---|---|---|")
    for k, (n, sec, c) in sorted(ju.items(), key=lambda x: -x[1][1])[:25]:
        print(f"| `{k}` | {c} | {n} | {fmt_h(sec)} |")


def win(path):
    lines = [json.loads(l) for l in open(path, encoding="utf-8-sig") if l.strip()]
    if len(lines) < 2:
        print("\nWindows: fewer than 2 samples: UNMEASURED")
        return
    span = lines[-1]["t"] - lines[0]["t"]
    first, last, names, ws_max, pv_max, paths = {}, {}, {}, {}, {}, {}
    for ln in lines:
        for p in ln["ps"]:
            k = p["k"]
            first.setdefault(k, (ln["t"], p))
            last[k] = (ln["t"], p)
            names[k] = p["n"]
            ws_max[k] = max(ws_max.get(k, 0), p["ws"])
            pv_max[k] = max(pv_max.get(k, 0), p["pv"])
            if p.get("p"):
                paths[k] = p["p"]
    t0 = lines[0]["t"]
    by = collections.defaultdict(lambda: [0.0, 0, 0, 0, 0, 0])
    for k, (tl, pl) in last.items():
        tf, pf = first[k]
        base = pf if tf <= t0 else {"c": 0, "r": 0, "w": 0}
        n = names[k]
        if n.lower().startswith("rimworld"):
            n += " (" + (paths.get(k, "?").split("\\")[-3] if paths.get(k) else "?") + ")"
        r = by[n]
        r[0] += (pl["c"] - base["c"]) / 1e7
        r[1] += 1
        r[2] += pl["r"] - base["r"]
        r[3] += pl["w"] - base["w"]
        r[4] = max(r[4], ws_max[k])
        r[5] = max(r[5], pv_max[k])
    tots = collections.defaultdict(list)
    for ln in lines:
        for kk, v in ln["tot"].items():
            tots[kk.split("\\", 3)[-1]].append(v)
    print(f"\n## Windows host: {span / 60:.1f} min, {len(lines)} samples\n")
    for kk, vs in tots.items():
        if isinstance(vs[0], (int, float)):
            print(f"- {kk}: mean {sum(vs) / len(vs):,.1f}, min {min(vs):,.1f}, max {max(vs):,.1f}")
    allcpu = sum(r[0] for r in by.values() if True)
    idle = by.get("System Idle Process", [0])[0]
    print(f"- process CPU sum {allcpu / 3600:.2f} core-hours, of it System Idle {idle / 3600:.2f}")
    print("\n| Windows process | CPU core-hours | instances | I/O read GB | I/O write GB | working set max GB | private max GB |")
    print("|---|---|---|---|---|---|---|")
    for n, r in sorted(by.items(), key=lambda x: -x[1][0])[:30]:
        if n == "System Idle Process":
            continue
        print(f"| `{n}` | {r[0] / 3600:.2f} | {r[1]} | {r[2] / 1e9:.2f} | {r[3] / 1e9:.2f} | {r[4] / 1e9:.2f} | {r[5] / 1e9:.2f} |")
    print("\n| Windows process, by I/O read | I/O read GB | CPU core-hours |")
    print("|---|---|---|")
    for n, r in sorted(by.items(), key=lambda x: -x[1][2])[:12]:
        print(f"| `{n}` | {r[2] / 1e9:.2f} | {r[0] / 3600:.2f} |")
    print("\n| Windows process, by private memory | private max GB | working set max GB |")
    print("|---|---|---|")
    for n, r in sorted(by.items(), key=lambda x: -x[1][5])[:12]:
        print(f"| `{n}` | {r[5] / 1e9:.2f} | {r[4] / 1e9:.2f} |")


if __name__ == "__main__":
    main()
