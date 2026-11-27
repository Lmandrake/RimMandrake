#!/usr/bin/env python3
"""Sample who uses the CPU, memory and disk on one Linux (WSL) machine, by process and by systemd unit.

Item RIMMANDRAKE_FIND_LOAD_USERS_RM_TIMERS_ONLY_TEN_PERCENT (row 10 of one_page.md). One run, one machine, one hour.

  python3 load_sample.py --out DIR [--seconds 3600] [--every 5] [--win-ps1 PATH]

What it reads, every --every seconds:
  - the machine: /proc/stat (CPU jiffies), /proc/vmstat (page-ins, swap-ins), /proc/meminfo, /proc/loadavg;
  - each cgroup under /sys/fs/cgroup: cpu.stat usage_usec, memory.current, memory.swap.current, io.stat bytes;
  - each process: /proc/<pid>/stat (utime, stime, rss), /proc/<pid>/io (storage bytes), its cgroup and cmdline once.
A process or cgroup that ends between two samples loses its last interval: the report shows how much CPU the
per-process and per-cgroup sums cover against the machine's total, so the loss is measured, not hidden.
With --win-ps1 it also starts the Windows sampler (load_sample_win.ps1) through WSL interop for the same window.

Writes DIR/linux.json (the totals, per cgroup and per process) at the end, and the same file every 5 minutes as a
checkpoint (key "final": false), so a killed run still leaves its reading.
"""
import argparse, json, os, subprocess, sys, time

CG = "/sys/fs/cgroup"
HZ = os.sysconf("SC_CLK_TCK")
PAGE = os.sysconf("SC_PAGE_SIZE")


def read(p):
    try:
        with open(p) as f:
            return f.read()
    except OSError:
        return None


def machine():
    cpu = read("/proc/stat").split("\n", 1)[0].split()[1:]
    cpu = [int(x) for x in cpu]
    vm = {}
    for line in read("/proc/vmstat").splitlines():
        k, v = line.split()
        if k in ("pgpgin", "pgpgout", "pswpin", "pswpout", "pgmajfault"):
            vm[k] = int(v)
    mem = {}
    for line in read("/proc/meminfo").splitlines():
        k, v = line.split(":")
        if k in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree", "Cached", "Dirty"):
            mem[k] = int(v.split()[0]) * 1024
    load = float(read("/proc/loadavg").split()[0])
    # cpu fields: user nice system idle iowait irq softirq steal guest guest_nice
    busy = sum(cpu[:3]) + sum(cpu[5:8])
    return {"busy": busy, "total": sum(cpu[:8]), "iowait": cpu[4], "vm": vm, "mem": mem, "load": load}


def cgroups():
    out = {}
    for root, dirs, files in os.walk(CG):
        if "cpu.stat" not in files:
            continue
        rel = root[len(CG):] or "/"
        rec = {}
        s = read(root + "/cpu.stat")
        if s:
            for line in s.splitlines():
                k, v = line.split()
                if k == "usage_usec":
                    rec["cpu_us"] = int(v)
        m = read(root + "/memory.current")
        if m:
            rec["mem"] = int(m)
        sw = read(root + "/memory.swap.current")
        if sw:
            rec["swap"] = int(sw)
        io = read(root + "/io.stat")
        if io:
            rb = wb = 0
            for line in io.splitlines():
                for kv in line.split()[1:]:
                    k, _, v = kv.partition("=")
                    if k == "rbytes":
                        rb += int(v)
                    elif k == "wbytes":
                        wb += int(v)
            rec["rb"], rec["wb"] = rb, wb
        out[rel] = rec
    return out


def procs(known):
    """Return {(pid, start): (cpu_ticks, rss_bytes, read_bytes, write_bytes, reaped_child_ticks)}; fill `known` with identity once."""
    out = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        st = read(f"/proc/{name}/stat")
        if not st:
            continue
        r = st.rfind(")")
        comm = st[st.find("(") + 1:r]
        f = st[r + 2:].split()
        ticks = int(f[11]) + int(f[12])
        cticks = int(f[13]) + int(f[14])  # CPU of children that ended and were reaped by this process
        start = int(f[19])
        rss = int(f[21]) * PAGE
        rb = wb = None
        io = read(f"/proc/{name}/io")
        if io:
            d = dict(l.split(": ") for l in io.splitlines())
            rb, wb = int(d["read_bytes"]), int(d["write_bytes"])
        key = (int(name), start)
        if key not in known:
            cg = (read(f"/proc/{name}/cgroup") or "").strip().split("::", 1)[-1]
            cmd = (read(f"/proc/{name}/cmdline") or "").replace("\0", " ").strip()[:300]
            known[key] = {"pid": int(name), "comm": comm, "cmd": cmd, "cgroup": cg, "ppid": int(f[1])}
        out[key] = (ticks, rss, rb, wb, cticks)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=int, default=3600)
    ap.add_argument("--every", type=float, default=5.0)
    ap.add_argument("--win-ps1", default=None, help="Windows path of load_sample_win.ps1 to start beside this run")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    win = None
    if a.win_ps1:
        winout = subprocess.run(["wslpath", "-w", a.out], capture_output=True, text=True).stdout.strip()
        win = subprocess.Popen(["/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", "-NoProfile",
                                "-ExecutionPolicy", "Bypass", "-File", a.win_ps1, "-Out", winout + "\\win.jsonl",
                                "-Seconds", str(a.seconds), "-Every", "30"],
                               stdout=open(os.path.join(a.out, "win.stdout"), "w"), stderr=subprocess.STDOUT)
    t0 = time.time()
    m0 = machine()
    cg_first, cg_last = {}, {}
    cg_mem_max = {}
    known, p_first, p_last, p_rss_max = {}, {}, {}, {}
    series = []
    self_pid = os.getpid()
    last_ck = t0
    n = 0
    while True:
        now = time.time()
        m = machine()
        cgs = cgroups()
        for k, v in cgs.items():
            cg_first.setdefault(k, (now, v))
            cg_last[k] = (now, v)
            mm = cg_mem_max.setdefault(k, [0, 0])
            mm[0] = max(mm[0], v.get("mem", 0))
            mm[1] = max(mm[1], v.get("swap", 0))
        ps = procs(known)
        for k, v in ps.items():
            p_first.setdefault(k, (now, v))
            p_last[k] = (now, v)
            p_rss_max[k] = max(p_rss_max.get(k, 0), v[1])
        series.append({"t": round(now - t0, 1), "busy": m["busy"], "total": m["total"], "iowait": m["iowait"],
                       "load": m["load"], "avail": m["mem"]["MemAvailable"],
                       "swap_used": m["mem"]["SwapTotal"] - m["mem"]["SwapFree"], **m["vm"]})
        n += 1
        done = now - t0 >= a.seconds
        if done or now - last_ck >= 300:
            dump(a.out, t0, now, m0, m, cg_first, cg_last, cg_mem_max, known, p_first, p_last, p_rss_max, series,
                 n, self_pid, final=done)
            last_ck = now
        if done:
            break
        time.sleep(max(0.0, a.every - (time.time() - now)))
    if win:
        try:
            win.wait(timeout=600)
        except subprocess.TimeoutExpired:
            win.kill()


def dump(out, t0, t1, m0, m1, cg_first, cg_last, cg_mem_max, known, p_first, p_last, p_rss_max, series, n,
         self_pid, final):
    """Per cgroup: the delta between its first and last sight. A cgroup born after t0 counts from 0 (its whole use
    is inside the window). Per process the same, with ticks converted to seconds."""
    cg = {}
    for k, (tl, vl) in cg_last.items():
        tf, vf = cg_first[k]
        born_inside = tf > t0 + 1
        base = {} if born_inside else vf
        cg[k] = {"cpu_s": (vl.get("cpu_us", 0) - base.get("cpu_us", 0)) / 1e6,
                 "rb": vl.get("rb", 0) - base.get("rb", 0) if "rb" in vl else None,
                 "wb": vl.get("wb", 0) - base.get("wb", 0) if "wb" in vl else None,
                 "mem_max": cg_mem_max[k][0], "swap_max": cg_mem_max[k][1],
                 "mem_last": vl.get("mem"), "swap_last": vl.get("swap"),
                 "seen_s": round(tl - tf, 1), "born_inside": born_inside, "gone": tl < t1 - 1}
    pr = []
    for key, (tl, vl) in p_last.items():
        tf, vf = p_first[key]
        born_inside = tf > t0 + 1
        ticks = vl[0] - (0 if born_inside else vf[0])
        rb = None if vl[2] is None else vl[2] - (0 if born_inside or vf[2] is None else vf[2])
        wb = None if vl[3] is None else vl[3] - (0 if born_inside or vf[3] is None else vf[3])
        rec = dict(known[key])
        cticks = vl[4] - (0 if born_inside else vf[4])
        rec.update({"cpu_s": ticks / HZ, "child_cpu_s": cticks / HZ, "rb": rb, "wb": wb, "rss_max": p_rss_max[key], "seen_s": round(tl - tf, 1),
                    "born_inside": born_inside, "self": key[0] == self_pid})
        if rec["cpu_s"] > 0 or rec["child_cpu_s"] > 0 or rec["rss_max"] > 50e6 or (rb or 0) > 0:
            pr.append(rec)
    doc = {"final": final, "t0": t0, "t1": t1, "samples": n, "hz": HZ, "ncpu": os.cpu_count(),
           "machine": {"busy_s": (m1["busy"] - m0["busy"]) / HZ, "total_s": (m1["total"] - m0["total"]) / HZ,
                       "iowait_s": (m1["iowait"] - m0["iowait"]) / HZ,
                       "pgpgin_bytes": (m1["vm"]["pgpgin"] - m0["vm"]["pgpgin"]) * 1024,
                       "pgpgout_bytes": (m1["vm"]["pgpgout"] - m0["vm"]["pgpgout"]) * 1024,
                       "pswpin_pages": m1["vm"]["pswpin"] - m0["vm"]["pswpin"],
                       "pswpout_pages": m1["vm"]["pswpout"] - m0["vm"]["pswpout"],
                       "mem_total": m1["mem"]["MemTotal"]},
           "cgroups": cg, "procs": pr, "series": series}
    tmp = os.path.join(out, "linux.json.tmp")
    with open(tmp, "w") as f:
        json.dump(doc, f)
    os.replace(tmp, os.path.join(out, "linux.json"))


if __name__ == "__main__":
    sys.exit(main())
