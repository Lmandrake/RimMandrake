#!/usr/bin/env python3
"""tool_metadata.py - exact [Tool("jawa/...")] name extraction, two ways.

WHY THIS EXISTS
================
build.py used to byte-scan a compiled DLL for `jawa/[a-z_]{3,40}` after
naively decoding the WHOLE FILE as UTF-16LE and UTF-8 in turn. That is not
where a [Tool] attribute's name argument lives: the .NET compiler stores a
custom-attribute constructor argument as a length-prefixed UTF-8 SerString in
the assembly's #Blob metadata heap, addressed only through the
CustomAttribute table -- never as a free-floating string discoverable by
grepping raw bytes. The old dual-encoding trick was built for the #US heap
(UTF-16 string LITERALS), a different heap entirely; reinterpreting #Blob
content as UTF-16LE, or scanning raw bytes for a run of `[a-z_]` characters at
all, can truncate a real name at whatever byte the coincidental re-encoding
stops looking like a letter. That is exactly what happened live 2026-09-06:
`jawa/pawn_` was reported as a lost tool when it was really a prefix-truncated
read of a real, still-present name (BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1).

`tool_names_from_dll` reads the CustomAttribute table's Value column exactly:
for every row, decode the attribute blob's prolog and first fixed argument as
a SerString (ECMA-335 II.23.3) -- a packed length, then exactly that many
UTF-8 bytes, never a scan for "where do letters stop". No attempt is made to
resolve which .NET type each attribute belongs to (that needs a further
TypeRef/MemberRef walk this file does not do) -- harmless here because no
other custom attribute in this assembly takes a "jawa/..." string as its
first constructor argument, and a wrong guess can only ever produce a false
negative (garbage that fails the jawa/ prefix check), never a truncated
positive: the length used to slice the string always comes from the blob's
own length prefix, not from where a regex happens to stop matching.

`tool_names_from_source` answers the same question from the OTHER side: the
`[Tool("jawa/...")]` declarations in the .cs files this DLL compiles from.
Exact by construction, and repo-native -- it is literally what ships. The two
are meant to be compared as SETS (build.py's selftest does exactly that).
"""
import glob
import os
import re
import struct

TOOL_NAME_RE = re.compile(r'^jawa/[A-Za-z0-9_]+$')

# Coded-index target tables, ECMA-335 II.24.2.6. Only the row COUNTS of these
# tables matter here (to decide whether the coded index needs 2 or 4 bytes) --
# never their content or tag order.
_RESSCOPE = (0x00, 0x1A, 0x23, 0x01)                    # ResolutionScope, 2 bits
_TYPEDEFORREF = (0x02, 0x01, 0x1B)                      # TypeDefOrRef, 2 bits
_MEMBERREFPARENT = (0x02, 0x01, 0x1A, 0x06, 0x1B)       # MemberRefParent, 3 bits
_HASCONSTANT = (0x04, 0x08, 0x17)                       # HasConstant, 2 bits
_HASCUSTOMATTRIBUTE = (0x06, 0x04, 0x01, 0x02, 0x08, 0x09, 0x0A, 0x00, 0x0E,
                        0x17, 0x14, 0x11, 0x1A, 0x1B, 0x20, 0x23, 0x26, 0x27,
                        0x28, 0x2A, 0x2C, 0x2B)         # HasCustomAttribute, 5 bits
_CUSTOMATTRIBUTETYPE = (0x06, 0x0A)                     # CustomAttributeType, 3 bits


def _read_compressed(data, off):
    """ECMA-335 II.23.2 compressed unsigned integer. Returns (value, next_off)."""
    v = data[off]
    if v & 0x80 == 0:
        return v, off + 1
    if v & 0xC0 == 0x80:
        return ((v & 0x3F) << 8) | data[off + 1], off + 2
    return (((v & 0x1F) << 24) | (data[off + 1] << 16) |
            (data[off + 2] << 8) | data[off + 3]), off + 4


def tool_names_from_dll(path_or_bytes):
    """Every `jawa/...` string that is the first fixed constructor argument
    of a custom attribute in this DLL, read from the CustomAttribute table's
    Value blob -- byte-length-exact, never a heuristic scan. Returns a set.
    """
    data = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) \
        else open(path_or_bytes, "rb").read()

    pe = struct.unpack_from('<I', data, 0x3C)[0]
    if data[pe:pe + 4] != b'PE\0\0':
        raise ValueError("not a PE image")
    nsec = struct.unpack_from('<H', data, pe + 6)[0]
    optsz = struct.unpack_from('<H', data, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from('<H', data, opt)[0]
    pe32plus = magic == 0x20b
    ddoff = opt + (112 if pe32plus else 96)
    cli_rva, _cli_sz = struct.unpack_from('<II', data, ddoff + 14 * 8)
    so = opt + optsz
    secs = []
    for i in range(nsec):
        b = so + i * 40
        vsize, vaddr, rawsize, rawptr = struct.unpack_from('<IIII', data, b + 8)
        secs.append((vaddr, vsize, rawptr, rawsize))

    def rva_to_off(rva):
        for va, vs, rp, rs in secs:
            if va <= rva < va + max(vs, rs):
                return rp + (rva - va)
        raise ValueError("bad rva 0x%x" % rva)

    cli = rva_to_off(cli_rva)
    md_rva, _md_sz = struct.unpack_from('<II', data, cli + 8)
    md = rva_to_off(md_rva)
    if data[md:md + 4] != b'BSJB':
        raise ValueError("no metadata root at 0x%x" % md)

    verlen = struct.unpack_from('<I', data, md + 12)[0]
    p = md + 16 + verlen + 2  # skip version string, then Flags
    nstreams = struct.unpack_from('<H', data, p)[0]
    p += 2
    streams = {}
    for _ in range(nstreams):
        off, size = struct.unpack_from('<II', data, p)
        p += 8
        e = data.index(b'\0', p)
        name = data[p:e].decode('ascii')
        p = (e + 1 + 3) & ~3
        streams[name] = (md + off, size)

    if "#~" not in streams:
        raise ValueError("no #~ tables stream (uncompressed #- metadata, "
                          "not supported here)")
    blob_off = streams.get("#Blob", (None, 0))[0]

    t = streams["#~"][0]
    heapsizes = data[t + 6]
    valid, _sorted = struct.unpack_from('<QQ', data, t + 8)
    p = t + 24
    rows = {}
    for i in range(64):
        if valid >> i & 1:
            rows[i] = struct.unpack_from('<I', data, p)[0]
            p += 4
    tables_start = p

    sSz = 4 if heapsizes & 1 else 2
    gSz = 4 if heapsizes & 2 else 2
    bSz = 4 if heapsizes & 4 else 2

    def idx_sz(tbl):
        return 4 if rows.get(tbl, 0) >= 65536 else 2

    def coded_sz(tabs, bits):
        mx = max(rows.get(x, 0) for x in tabs)
        return 4 if mx >= (1 << (16 - bits)) else 2

    RESSCOPE = coded_sz(_RESSCOPE, 2)
    TYPEDEFORREF = coded_sz(_TYPEDEFORREF, 2)
    MEMBERREFPARENT = coded_sz(_MEMBERREFPARENT, 3)
    HASCONSTANT = coded_sz(_HASCONSTANT, 2)
    HASCUSTOMATTR = coded_sz(_HASCUSTOMATTRIBUTE, 5)
    CUSTOMATTRTYPE = coded_sz(_CUSTOMATTRIBUTETYPE, 3)

    # Row schemas (column byte-widths), table id -> columns. Only used to
    # WALK to the CustomAttribute table's start -- content is never read for
    # any table but CustomAttribute itself.
    SCHEMA = {
        0x00: [2, sSz, gSz, gSz, gSz],                      # Module
        0x01: [RESSCOPE, sSz, sSz],                         # TypeRef
        0x02: [4, sSz, sSz, TYPEDEFORREF,
               idx_sz(0x04), idx_sz(0x06)],                 # TypeDef
        0x03: [idx_sz(0x04)],                                # FieldPtr
        0x04: [2, sSz, bSz],                                 # Field
        0x05: [idx_sz(0x06)],                                # MethodPtr
        0x06: [4, 2, 2, sSz, bSz, idx_sz(0x08)],             # MethodDef
        0x07: [idx_sz(0x08)],                                # ParamPtr
        0x08: [2, 2, sSz],                                   # Param
        0x09: [idx_sz(0x02), TYPEDEFORREF],                  # InterfaceImpl
        0x0A: [MEMBERREFPARENT, sSz, bSz],                   # MemberRef
        0x0B: [2, HASCONSTANT, bSz],                         # Constant
        0x0C: [HASCUSTOMATTR, CUSTOMATTRTYPE, bSz],          # CustomAttribute
    }

    offsets = {}
    cur = tables_start
    for i in range(0x0D):
        if i in rows:
            if i not in SCHEMA:
                raise ValueError("unhandled metadata table 0x%02x with %d "
                                  "rows -- extend SCHEMA" % (i, rows[i]))
            offsets[i] = cur
            cur += sum(SCHEMA[i]) * rows[i]

    if 0x0C not in offsets:
        return set()  # no custom attributes at all

    ca_schema = SCHEMA[0x0C]
    ca_width = sum(ca_schema)
    ca_base = offsets[0x0C]
    n_ca = rows[0x0C]
    value_col_off = ca_schema[0] + ca_schema[1]  # skip Parent, Type
    value_col_w = ca_schema[2]

    names = set()
    for i in range(n_ca):
        row_base = ca_base + i * ca_width
        o = row_base + value_col_off
        if value_col_w == 2:
            value_idx = struct.unpack_from('<H', data, o)[0]
        elif value_col_w == 4:
            value_idx = struct.unpack_from('<I', data, o)[0]
        else:
            value_idx = int.from_bytes(data[o:o + value_col_w], 'little')
        if blob_off is None or value_idx == 0:
            continue
        try:
            blen, boff = _read_compressed(data, blob_off + value_idx)
            blob = data[boff:boff + blen]
            # Custom attribute blob: prolog 0x0001, then fixed args (II.23.3).
            if len(blob) < 3 or blob[0] != 0x01 or blob[1] != 0x00:
                continue
            if blob[2] == 0xFF:  # null string
                continue
            slen, soff = _read_compressed(blob, 2)
            if soff + slen > len(blob):
                continue
            name = blob[soff:soff + slen].decode('utf-8', 'strict')
        except (IndexError, UnicodeDecodeError):
            continue
        if TOOL_NAME_RE.match(name):
            names.add(name)
    return names


def tool_names_from_source(source_dir):
    """Every `[Tool("jawa/...")]` declaration in the .cs files in source_dir.

    Exact by construction: this is literally what the repo compiles from.
    Deliberately blind to `#if JAWA_GM_TOOLS` -- a name inside that region is
    reported the same as any other, because "does the source declare this" is
    a different question from "does this particular build include it", and
    conflating them is how the phantom-loss bug happened in the first place.
    """
    names = set()
    pat = re.compile(r'\[Tool\(\s*"(jawa/[A-Za-z0-9_]+)"')
    for path in sorted(glob.glob(os.path.join(source_dir, "*.cs"))):
        text = open(path, encoding="utf-8").read()
        names |= set(pat.findall(text))
    return names


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        sys.exit("usage: tool_metadata.py <dll-path-or-source-dir>")
    target = sys.argv[1]
    result = (tool_names_from_source(target) if os.path.isdir(target)
              else tool_names_from_dll(target))
    print(len(result))
    for n in sorted(result):
        print(n)
