import struct, sys

DLL = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll"
d = open(DLL, 'rb').read()

# --- PE parse ---
pe = struct.unpack_from('<I', d, 0x3C)[0]
assert d[pe:pe+4] == b'PE\0\0'
nsec = struct.unpack_from('<H', d, pe+6)[0]
optsz = struct.unpack_from('<H', d, pe+20)[0]
opt = pe+24
magic = struct.unpack_from('<H', d, opt)[0]
pe32plus = (magic == 0x20b)
ddoff = opt + (112 if pe32plus else 96)
# DataDirectory[14] = CLI header
cli_rva, cli_sz = struct.unpack_from('<II', d, ddoff + 14*8)
secs = []
so = opt + optsz
for i in range(nsec):
    b = so + i*40
    name = d[b:b+8].rstrip(b'\0').decode()
    vsize, vaddr, rawsize, rawptr = struct.unpack_from('<IIII', d, b+8)
    secs.append((name, vaddr, vsize, rawptr, rawsize))

def r2o(rva):
    for name, va, vs, rp, rs in secs:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    raise ValueError("bad rva %x" % rva)

cli = r2o(cli_rva)
md_rva, md_sz = struct.unpack_from('<II', d, cli+8)
md = r2o(md_rva)
assert d[md:md+4] == b'BSJB', d[md:md+4]
verlen = struct.unpack_from('<I', d, md+12)[0]
p = md + 16 + verlen
p += 2  # flags
nstreams = struct.unpack_from('<H', d, p)[0]; p += 2
streams = {}
for i in range(nstreams):
    off, size = struct.unpack_from('<II', d, p); p += 8
    e = d.index(b'\0', p)
    nm = d[p:e].decode()
    p = e + 1
    p = (p + 3) & ~3
    streams[nm] = (md + off, size)

STR = streams['#Strings']
BLOB = streams.get('#Blob')
TBL = streams['#~']

t = TBL[0]
heapsizes = d[t+6]
valid, sorted_ = struct.unpack_from('<QQ', d, t+8)
p = t + 24
rows = {}
for i in range(64):
    if valid >> i & 1:
        rows[i] = struct.unpack_from('<I', d, p)[0]; p += 4
tables_start = p

sSz = 4 if heapsizes & 1 else 2
gSz = 4 if heapsizes & 2 else 2
bSz = 4 if heapsizes & 4 else 2

def idxSz(tbl):
    return 4 if rows.get(tbl, 0) >= 65536 else 2

def codedSz(tabs, bits):
    mx = max(rows.get(x, 0) for x in tabs)
    return 4 if mx >= (1 << (16 - bits)) else 2

RESSCOPE = codedSz([0x00, 0x1A, 0x23, 0x01], 2)
TYPEDEFORREF = codedSz([0x02, 0x01, 0x1B], 2)

SCHEMA = {
    0x00: [2, sSz, gSz, gSz, gSz],
    0x01: [RESSCOPE, sSz, sSz],
    0x02: [4, sSz, sSz, TYPEDEFORREF, idxSz(0x04), idxSz(0x06)],
    0x03: [idxSz(0x04)],
    0x04: [2, sSz, bSz],
    0x05: [idxSz(0x06)],
    0x06: [4, 2, 2, sSz, bSz, idxSz(0x08)],
}

offsets = {}
cur = tables_start
for i in range(64):
    if i in rows:
        if i not in SCHEMA:
            break
        offsets[i] = cur
        cur += sum(SCHEMA[i]) * rows[i]

def readrow(tbl, n):  # n is 1-based
    sch = SCHEMA[tbl]
    base = offsets[tbl] + (n - 1) * sum(sch)
    out = []
    o = base
    for w in sch:
        if w == 2: out.append(struct.unpack_from('<H', d, o)[0])
        elif w == 4: out.append(struct.unpack_from('<I', d, o)[0])
        else: out.append(int.from_bytes(d[o:o+w], 'little'))
        o += w
    return out

def s(idx):
    b = STR[0] + idx
    e = d.index(b'\0', b)
    return d[b:e].decode('utf-8', 'replace')

def blob(idx):
    b = BLOB[0] + idx
    v = d[b]
    if v & 0x80 == 0: ln = v; b += 1
    elif v & 0xC0 == 0x80: ln = ((v & 0x3F) << 8) | d[b+1]; b += 2
    else: ln = ((v & 0x1F) << 24) | (d[b+1] << 16) | (d[b+2] << 8) | d[b+3]; b += 4
    return d[b:b+ln]

# --- find types ---
ntd = rows[0x02]
typedefs = []
for i in range(1, ntd + 1):
    flags, nameI, nsI, ext, fl, ml = readrow(0x02, i)
    typedefs.append((s(nameI), s(nsI), fl, ml, ext, flags))

ELEM = {0x02:'bool',0x03:'char',0x04:'sbyte',0x05:'byte',0x06:'short',0x07:'ushort',
        0x08:'int',0x09:'uint',0x0a:'long',0x0b:'ulong',0x0c:'float',0x0d:'double',
        0x0e:'string',0x11:'valuetype',0x12:'class',0x15:'generic',0x1d:'array',0x1c:'object'}

def fieldtype(sig):
    # 0x06 CALLCONV_FIELD then type
    i = 1
    while i < len(sig) and sig[i] in (0x1f, 0x20):  # cmod
        i += 2
    if i >= len(sig): return '?'
    e = sig[i]
    if e in (0x11, 0x12):
        # decode TypeDefOrRef coded index (compressed)
        j = i + 1
        v = sig[j]
        if v & 0x80 == 0: ci = v; j += 1
        elif v & 0xC0 == 0x80: ci = ((v & 0x3F) << 8) | sig[j+1]; j += 2
        else: ci = ((v & 0x1F) << 24) | (sig[j+1] << 16) | (sig[j+2] << 8) | sig[j+3]; j += 4
        tag = ci & 3; ri = ci >> 2
        # ri==0 is a null coded-index row (no type) -- ri<=len(typedefs)
        # let it through and silently returned typedefs[-1], the LAST type
        # in the whole assembly, as a plausible-looking wrong answer.
        if tag == 0 and 0 < ri <= len(typedefs): return typedefs[ri-1][0]
        if tag == 1:
            fl, nI, nsI = readrow(0x01, ri)[0], readrow(0x01, ri)[1], readrow(0x01, ri)[2]
            return s(nI)
        return 'typespec'
    if e == 0x1d:
        return fieldtype(b'\x06' + sig[i+1:]) + '[]'
    if e == 0x15:
        # generic inst: 0x15 <class|valuetype> <typedeforref> argcount args...
        inner = fieldtype(b'\x06' + sig[i+1:])
        return inner + '<...>'
    return ELEM.get(e, 'elem0x%02x' % e)

