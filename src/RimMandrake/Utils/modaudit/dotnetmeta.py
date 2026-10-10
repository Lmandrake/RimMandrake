#!/usr/bin/env python3
"""modaudit/dotnetmeta.py - top-level type names ("Namespace.Type") from a .NET assembly's metadata TypeDef table.

Pure over bytes; stdlib only; selftested. Reads the ECMA-335 tables, never greps strings, so a type name is a type
this assembly DEFINES (not one it references). Nested types and <Module> are skipped. Returns [] for a non-.NET or
malformed file (callers must treat [] as "no types read", not "defines nothing" when the file is a managed DLL).
"""
import struct

# ECMA-335 II.22 table ids
T_MODULE, T_TYPEREF, T_TYPEDEF, T_FIELD, T_METHOD = 0x00, 0x01, 0x02, 0x04, 0x06
T_MODULEREF, T_TYPESPEC, T_ASSEMBLYREF = 0x1A, 0x1B, 0x23


def _rva_to_off(rva, sections):
    for va, vsz, raw, rawsz in sections:
        if va <= rva < va + max(vsz, rawsz):
            return rva - va + raw
    return None


def type_names(blob):
    try:
        return _type_names(blob)
    except (struct.error, IndexError, ValueError, TypeError):
        return []


def _type_names(b):
    if b[:2] != b"MZ":
        return []
    pe = struct.unpack_from("<I", b, 0x3C)[0]
    if b[pe:pe + 4] != b"PE\0\0":
        return []
    nsec = struct.unpack_from("<H", b, pe + 6)[0]
    optsz = struct.unpack_from("<H", b, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from("<H", b, opt)[0]
    dd = opt + (96 if magic == 0x10B else 112)
    cli_rva, cli_sz = struct.unpack_from("<II", b, dd + 14 * 8)
    if not cli_rva:
        return []
    sections = []
    st = opt + optsz
    for i in range(nsec):
        o = st + 40 * i
        vsz, va, rawsz, raw = struct.unpack_from("<IIII", b, o + 8)
        sections.append((va, vsz, raw, rawsz))
    cli = _rva_to_off(cli_rva, sections)
    md_rva = struct.unpack_from("<I", b, cli + 8)[0]
    md = _rva_to_off(md_rva, sections)
    if struct.unpack_from("<I", b, md)[0] != 0x424A5342:
        return []
    vlen = struct.unpack_from("<I", b, md + 12)[0]
    p = md + 16 + vlen
    nstreams = struct.unpack_from("<H", b, p + 2)[0]
    p += 4
    streams = {}
    for _ in range(nstreams):
        off, size = struct.unpack_from("<II", b, p)
        p += 8
        e = b.index(b"\0", p)
        name = b[p:e].decode("ascii", "replace")
        p = (e + 1 + 3) & ~3
        streams[name] = (md + off, size)
    tbl = streams.get("#~") or streams.get("#-")
    strs = streams.get("#Strings")
    if not tbl or not strs:
        return []
    t = tbl[0]
    heap = b[t + 6]
    valid = struct.unpack_from("<Q", b, t + 8)[0]
    q = t + 24
    rows = {}
    for i in range(64):
        if valid >> i & 1:
            rows[i] = struct.unpack_from("<I", b, q)[0]
            q += 4
    if heap & 0x40:
        q += 4
    ssz = 4 if heap & 1 else 2
    gsz = 4 if heap & 2 else 2

    def idx(tid):
        return 4 if rows.get(tid, 0) >= 0x10000 else 2

    def coded(tids, bits):
        return 4 if max(rows.get(x, 0) for x in tids) >= (1 << (16 - bits)) else 2
    module_row = 2 + ssz + 3 * gsz
    typeref_row = coded((T_MODULE, T_MODULEREF, T_ASSEMBLYREF, T_TYPEREF), 2) + 2 * ssz
    extends = coded((T_TYPEDEF, T_TYPEREF, T_TYPESPEC), 2)
    typedef_row = 4 + 2 * ssz + extends + idx(T_FIELD) + idx(T_METHOD)
    q += module_row * rows.get(T_MODULE, 0) + typeref_row * rows.get(T_TYPEREF, 0)
    sbase = strs[0]

    def rd_str(o):
        e = b.index(b"\0", sbase + o)
        return b[sbase + o:e].decode("utf-8", "replace")

    def rd_idx(o, sz):
        return struct.unpack_from("<I" if sz == 4 else "<H", b, o)[0]
    out = []
    for i in range(rows.get(T_TYPEDEF, 0)):
        o = q + i * typedef_row
        flags = struct.unpack_from("<I", b, o)[0]
        name = rd_str(rd_idx(o + 4, ssz))
        ns = rd_str(rd_idx(o + 4 + ssz, ssz))
        if (flags & 0x7) >= 2 or name == "<Module>" or name.startswith("<"):
            continue                                    # nested type, or compiler-generated
        out.append(("%s.%s" % (ns, name)) if ns else name)
    return out
