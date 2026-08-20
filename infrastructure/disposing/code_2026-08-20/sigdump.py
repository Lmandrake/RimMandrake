#!/usr/bin/env python3
"""Dump full method signatures (types + param names) for a type in Assembly-CSharp.dll."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # sibling meta_core; never a scratchpad path
import meta_core as M

d = M.d
rows = M.rows
SCHEMA = M.SCHEMA
offsets = M.offsets

# Param table (0x08): Flags(2), Sequence(2), Name(string)
PARAM_SCHEMA = [2, 2, M.sSz]
param_base = offsets[0x06] + sum(SCHEMA[0x06]) * rows[0x06]
nparam = rows.get(0x08, 0)

def param_row(n):  # 1-based
    o = param_base + (n - 1) * sum(PARAM_SCHEMA)
    flags = struct.unpack_from('<H', d, o)[0]
    seq = struct.unpack_from('<H', d, o + 2)[0]
    nm = int.from_bytes(d[o+4:o+4+M.sSz], 'little')
    return flags, seq, M.s(nm)

def cint(sig, i):
    v = sig[i]
    if v & 0x80 == 0: return v, i+1
    if v & 0xC0 == 0x80: return ((v & 0x3F) << 8) | sig[i+1], i+2
    return ((v & 0x1F) << 24) | (sig[i+1] << 16) | (sig[i+2] << 8) | sig[i+3], i+4

def typedeforref(ci):
    tag = ci & 3; ri = ci >> 2
    if tag == 0 and ri <= len(M.typedefs): return M.typedefs[ri-1][0]
    if tag == 1:
        r = M.readrow(0x01, ri); return M.s(r[1])
    return 'typespec#%d' % ri

def ptype(sig, i):
    while i < len(sig) and sig[i] in (0x1f, 0x20):
        _, i = cint(sig, i+1)
    e = sig[i]; i += 1
    if e in (0x11, 0x12):
        ci, i = cint(sig, i)
        return typedeforref(ci), i
    if e == 0x10:  # BYREF
        t, i = ptype(sig, i); return t + '&', i
    if e == 0x45:  # PINNED? not typical
        return ptype(sig, i)
    if e == 0x1d:  # SZARRAY
        t, i = ptype(sig, i); return t + '[]', i
    if e == 0x0f:  # PTR
        t, i = ptype(sig, i); return t + '*', i
    if e == 0x15:  # GENERICINST
        base, i = ptype(sig, i)
        n, i = cint(sig, i)
        args = []
        for _ in range(n):
            a, i = ptype(sig, i); args.append(a)
        return '%s<%s>' % (base.split('`')[0], ', '.join(args)), i
    if e == 0x13:  # VAR
        n, i = cint(sig, i); return '!%d' % n, i
    if e == 0x1e:  # MVAR
        n, i = cint(sig, i); return '!!%d' % n, i
    if e == 0x14:  # ARRAY
        t, i = ptype(sig, i)
        rank, i = cint(sig, i)
        ns, i = cint(sig, i)
        for _ in range(ns): _, i = cint(sig, i)
        nl, i = cint(sig, i)
        for _ in range(nl): _, i = cint(sig, i)
        return t + '[' + ','*(rank-1) + ']', i
    if e == 0x01: return 'void', i
    return M.ELEM.get(e, 'elem0x%02x' % e), i

def methodsig(sig):
    i = 0
    cc = sig[i]; i += 1
    gen = 0
    if cc & 0x10:
        gen, i = cint(sig, i)
    n, i = cint(sig, i)
    ret, i = ptype(sig, i)
    ps = []
    for _ in range(n):
        if i < len(sig) and sig[i] == 0x41:  # SENTINEL
            i += 1
        t, i = ptype(sig, i)
        ps.append(t)
    return ret, ps, gen, (cc & 0x20) != 0

targets = sys.argv[1:]
for ti, (nm, ns, fl, ml, ext, flags) in enumerate(M.typedefs):
    if nm not in targets: continue
    print("=" * 70)
    print("TYPE %s.%s" % (ns, nm))
    # method range
    nextml = M.typedefs[ti+1][3] if ti + 1 < len(M.typedefs) else rows[0x06] + 1
    for mi in range(ml, nextml):
        rva, implflags, mflags, nameI, sigI, plist = M.readrow(0x06, mi)
        mname = M.s(nameI)
        sig = M.blob(sigI)
        try:
            ret, ps, gen, hasthis = methodsig(sig)
        except Exception as ex:
            print("  ?? %s (sig parse fail %s)" % (mname, ex)); continue
        # param names
        nextpl = M.readrow(0x06, mi+1)[5] if mi + 1 <= rows[0x06] - 1 else nparam + 1
        if mi + 1 <= rows[0x06]:
            nextpl = M.readrow(0x06, mi+1)[5]
        else:
            nextpl = nparam + 1
        pnames = {}
        for pi in range(plist, min(nextpl, nparam + 1)):
            pf, seq, pn = param_row(pi)
            pnames[seq] = pn
        args = ", ".join("%s %s" % (ps[k], pnames.get(k+1, "arg%d" % k)) for k in range(len(ps)))
        vis = ['privscope','private','famandassem','assem','family','famorassem','public'][mflags & 7]
        st = 'static ' if mflags & 0x10 else ''
        print("  [%s] %s%s %s(%s)   rva=0x%x" % (vis, st, ret, mname, args, rva))
