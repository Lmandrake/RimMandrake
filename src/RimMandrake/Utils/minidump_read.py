#!/usr/bin/env python3
"""Read a Windows x64 minidump offline, in plain Python (no dbghelp, no Windows): the threads, each one's
instruction and stack pointer, the module list, and a heuristic stack scan resolved against module export tables.

Written for the health_minidump.py utility spike (MINIDUMP_PROVE_SPIKE_BEFORE_THE_KILL): a dump is only worth
taking before a kill if someone can read it later on any machine.

    python3 src/RimMandrake/Utils/minidump_read.py <dump.dmp> [--pe <dll>...] [--thread TID]

  * Symbols are module EXPORTS only (no PDBs): `ntdll.dll!NtWaitForSingleObject+0x14`. Pass `--pe` copies of the
    DLLs taken from the dumped machine; a copy is used only when its PE TimeDateStamp and SizeOfImage match the
    dump's module entry, so a DLL from another Windows build never names a frame.
  * The stack scan lists every 8-byte stack slot that points into a module's image: return-address CANDIDATES, not an
    unwound call stack (stale slots appear). The top frame (RIP) is exact.
  * Managed (Mono JIT) frames point into no module and print as bare addresses: a dump of RimWorld names the native
    wait, not the C# method that waits.
"""
import argparse
import bisect
import os
import struct
import sys

THREAD_LIST, MODULE_LIST, MEMORY_LIST, SYSTEM_INFO, THREAD_INFO_LIST, MEMORY64_LIST = 3, 4, 5, 7, 17, 9
CTX_RSP, CTX_RIP = 0x98, 0xF8          # offsets in the AMD64 CONTEXT record


class DumpError(ValueError):
    pass


def _u(fmt, b, off):
    try:
        return struct.unpack_from(fmt, b, off)
    except struct.error as e:
        raise DumpError("truncated at 0x%x (%s): %s" % (off, fmt, e))


def _mdstring(b, rva):
    (n,) = _u("<I", b, rva)
    return b[rva + 4: rva + 4 + n].decode("utf-16-le", "replace")


def read(path_or_bytes):
    """-> dict(threads=[...], modules=[...], memory=[(start, bytes)], streams=[types], arch=int|None)."""
    b = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) else open(path_or_bytes, "rb").read()
    if len(b) < 32 or b[:4] != b"MDMP":
        raise DumpError("not a minidump (no MDMP signature)")
    _sig, _ver, nstreams, dir_rva = _u("<4sIII", b, 0)
    streams = {}
    for i in range(nstreams):
        st, size, rva = _u("<III", b, dir_rva + 12 * i)
        if st:
            streams[st] = (size, rva)
    out = {"streams": sorted(streams), "threads": [], "modules": [], "memory": [], "arch": None, "size": len(b)}
    if SYSTEM_INFO in streams:
        (out["arch"],) = _u("<H", b, streams[SYSTEM_INFO][1])
        if out["arch"] != 9:
            raise DumpError("processor architecture %d is not AMD64 (9): context offsets would be wrong" % out["arch"])
    if MODULE_LIST in streams:
        rva = streams[MODULE_LIST][1]
        (n,) = _u("<I", b, rva)
        for i in range(n):
            o = rva + 4 + 108 * i
            base, size, _cks, stamp, name_rva = _u("<QIIII", b, o)
            out["modules"].append({"base": base, "size": size, "stamp": stamp, "path": _mdstring(b, name_rva),
                                   "name": _mdstring(b, name_rva).replace("/", "\\").split("\\")[-1]})
    if MEMORY_LIST in streams:
        rva = streams[MEMORY_LIST][1]
        (n,) = _u("<I", b, rva)
        for i in range(n):
            start, dsize, drva = _u("<QII", b, rva + 4 + 16 * i)
            out["memory"].append((start, b[drva: drva + dsize]))
    infos = {}
    if THREAD_INFO_LIST in streams:
        rva = streams[THREAD_INFO_LIST][1]
        hsize, esize, n = _u("<III", b, rva)
        for i in range(n):
            o = rva + hsize + esize * i
            tid, flags, err, _exit = _u("<IIII", b, o)
            create, _exitt, ktime, utime, start = _u("<QQQQQ", b, o + 16)
            infos[tid] = {"dumpFlags": flags, "dumpError": err, "createTime": create, "kernelTime": ktime,
                          "userTime": utime, "startAddress": start}
    if THREAD_LIST in streams:
        rva = streams[THREAD_LIST][1]
        (n,) = _u("<I", b, rva)
        for i in range(n):
            o = rva + 4 + 48 * i
            tid, suspend, _pc, _pr, teb, st_start, st_size, st_rva, ctx_size, ctx_rva = _u("<IIIIQQIIII", b, o)
            ctx = b[ctx_rva: ctx_rva + ctx_size]
            rip = rsp = None
            if len(ctx) >= CTX_RIP + 8:
                (rsp,) = _u("<Q", ctx, CTX_RSP)
                (rip,) = _u("<Q", ctx, CTX_RIP)
            t = {"tid": tid, "suspendCount": suspend, "teb": teb, "rip": rip, "rsp": rsp,
                 "stackStart": st_start, "stack": b[st_rva: st_rva + st_size]}
            t.update(infos.get(tid, {}))
            out["threads"].append(t)
    return out


# ------------------------------------------------------------------------------------------- PE export tables
def pe_exports(path_or_bytes):
    """-> (timestamp, size_of_image, [(rva, name)] sorted by rva). Named exports only; forwarders skipped."""
    b = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) else open(path_or_bytes, "rb").read()
    if b[:2] != b"MZ":
        raise DumpError("not a PE file")
    (pe,) = _u("<I", b, 0x3C)
    if b[pe:pe + 4] != b"PE\0\0":
        raise DumpError("no PE signature")
    _mach, nsect, stamp = _u("<HHI", b, pe + 4)
    (opt_size,) = _u("<H", b, pe + 20)
    opt = pe + 24
    (magic,) = _u("<H", b, opt)
    if magic != 0x20B:
        raise DumpError("not PE32+")
    (size_of_image,) = _u("<I", b, opt + 56)
    exp_rva, exp_size = _u("<II", b, opt + 112)
    sects = []
    for i in range(nsect):
        s = opt + opt_size + 40 * i
        vsize, va, rawsize, rawptr = _u("<IIII", b, s + 8)
        sects.append((va, max(vsize, rawsize), rawptr))

    def off(rva):
        for va, sz, raw in sects:
            if va <= rva < va + sz:
                return raw + rva - va
        raise DumpError("rva 0x%x in no section" % rva)

    syms = []
    if exp_rva:
        e = off(exp_rva)
        nfuncs, nnames, funcs, names, ords = _u("<IIIII", b, e + 20)
        for i in range(nnames):
            (name_rva,) = _u("<I", b, off(names) + 4 * i)
            (ordinal,) = _u("<H", b, off(ords) + 2 * i)
            (frva,) = _u("<I", b, off(funcs) + 4 * ordinal)
            if exp_rva <= frva < exp_rva + exp_size:
                continue                                    # forwarder string, not code
            n0 = off(name_rva)
            syms.append((frva, b[n0: b.index(b"\0", n0)].decode("ascii", "replace")))
    syms.sort()
    return stamp, size_of_image, syms


class Symbolizer:
    def __init__(self, dump, pe_paths=()):
        self.mods = sorted(dump["modules"], key=lambda m: m["base"])
        self.bases = [m["base"] for m in self.mods]
        self.exports = {}                # lower module name -> (rvas, names)
        self.rejected = {}
        for p in pe_paths:
            stamp, soi, syms = pe_exports(p)
            name = os.path.basename(p).lower()
            m = next((m for m in self.mods if m["name"].lower() == name), None)
            if m is None:
                self.rejected[name] = "not loaded in the dump"
            elif (m["stamp"], m["size"]) != (stamp, soi):
                self.rejected[name] = "PE stamp/size %x/%x != dump %x/%x" % (stamp, soi, m["stamp"], m["size"])
            else:
                first = {}
                for r, n in syms:            # aliases share an address (NtX/ZwX): keep the first, so names are stable
                    first.setdefault(r, n)
                rv = sorted(first)
                self.exports[name] = (rv, [first[r] for r in rv])

    def module(self, addr):
        i = bisect.bisect_right(self.bases, addr) - 1
        if i >= 0 and addr < self.mods[i]["base"] + self.mods[i]["size"]:
            return self.mods[i]
        return None

    def name(self, addr):
        """'mod!Export+0xN' / 'mod+0xRVA' / None when the address is in no module."""
        m = self.module(addr)
        if m is None:
            return None
        rva = addr - m["base"]
        ex = self.exports.get(m["name"].lower())
        if ex:
            i = bisect.bisect_right(ex[0], rva) - 1
            if i >= 0:
                return "%s!%s+0x%x" % (m["name"], ex[1][i], rva - ex[0][i])
        return "%s+0x%x" % (m["name"], rva)


def stack_scan(thread, sym, limit=64):
    """Return-address candidates: stack slots from RSP upward that point into a module image."""
    st, base, rsp = thread["stack"], thread["stackStart"], thread["rsp"] or thread["stackStart"]
    out = []
    for o in range(max(rsp - base, 0) & ~7, len(st) - 7, 8):
        (v,) = struct.unpack_from("<Q", st, o)
        n = sym.name(v)
        if n:
            out.append(n)
            if len(out) >= limit:
                break
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="read a minidump offline: threads, top frames, stack scan")
    ap.add_argument("dump")
    ap.add_argument("--pe", nargs="*", default=[], help="DLL copies from the dumped machine (exports)")
    ap.add_argument("--thread", type=int, default=None, help="scan only this thread id")
    ap.add_argument("--depth", type=int, default=12)
    a = ap.parse_args(argv)
    d = read(a.dump)
    sym = Symbolizer(d, a.pe)
    print("%s: %d bytes, %d threads, %d modules, streams %s" % (a.dump, d["size"], len(d["threads"]), len(d["modules"]), d["streams"]))
    for n, why in sym.rejected.items():
        print("  --pe %s ignored: %s" % (n, why))
    for t in d["threads"]:
        if a.thread is not None and t["tid"] != a.thread:
            continue
        print("thread %d  rip %s" % (t["tid"], sym.name(t["rip"]) or ("0x%x" % (t["rip"] or 0))))
        for f in stack_scan(t, sym, a.depth):
            print("    ? %s" % f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
