#!/usr/bin/env python3
"""ilscan.py — read constants out of a .NET assembly with no disassembler.

WHY THIS EXISTS. On 2026-08-13 the gravship design turned on four numbers that
existed in no XML and no config file: Bigger Gravships is code-only and was
running at its compiled-in defaults. Nothing on this machine can disassemble IL —
ikdasm, monodis, ilspycmd and dotnet-ildasm are all absent and nothing may be
installed — so the values were read straight out of the PE/CLI metadata by this
script.

WHAT IT ESTABLISHED, and how it was checked: engine radius 25.90, extender radius
25.90, max extenders 8, max distance from engine 25.90. Validated end to end
because the same assembly stores the VANILLA values as `_LudeonDefault`
constants, and those came back as 18.90 / 16.90 — the published Odyssey numbers.
A parser that reproduces a known answer is trustworthy about the unknown one.

Independently confirmed afterwards by byte-pattern search: float32 25.9 packs to
`3333cf41` and occurs 10x; 34.0 and 30.0 (the values the design ASSUMED) occur
zero times anywhere in the assembly.

⚠️ TWO ENCODING TRAPS, both hit for real:
  * Metadata names — fields, methods, types — are UTF-8 in the #Strings heap.
  * String LITERALS are UTF-16 in the #US heap. An ASCII grep for a literal like
    `BG_GravEngine_MaxDistance` returns nothing while the string is plainly there.
Search both encodings before concluding something is absent.

⚠️ AND THE SCRIBE KEYS ARE NOT THE FIELD NAMES. The C# field is
`gravEngineMaxRadius`; the key RimWorld actually reads from the settings XML is
`BG_gravEngineMaxDistance`. Hand-authoring a config from field names alone
produces a file that loads silently as nothing.

USAGE
    python3 src/RimMandrake/Utils/ilscan.py <path-to.dll>

Written by a subagent during the 2026-08-13 investigation and moved into the repo
before a reboot, because /tmp is tmpfs and the same reboot pattern destroyed
another seat's work earlier the same day.
"""
import struct, sys

path = sys.argv[1]
data = open(path,'rb').read()

# --- PE ---
pe = struct.unpack_from('<I', data, 0x3C)[0]
assert data[pe:pe+4] == b'PE\0\0'
nsec = struct.unpack_from('<H', data, pe+6)[0]
optsz = struct.unpack_from('<H', data, pe+20)[0]
opt = pe+24
magic = struct.unpack_from('<H', data, opt)[0]
pe32plus = (magic == 0x20b)
ddoff = opt + (0x70 if not pe32plus else 0x70+16)
# data directories start: PE32 -> opt+96, PE32+ -> opt+112
ddoff = opt + (96 if not pe32plus else 112)
cli_rva, cli_sz = struct.unpack_from('<II', data, ddoff + 14*8)

sects = []
so = opt + optsz
for i in range(nsec):
    b = so + i*40
    name = data[b:b+8].rstrip(b'\0').decode()
    vsz, va, rsz, raw = struct.unpack_from('<IIII', data, b+8)
    sects.append((name, va, vsz, raw, rsz))

def r2o(rva):
    for name, va, vsz, raw, rsz in sects:
        if va <= rva < va + max(vsz, rsz):
            return raw + (rva - va)
    raise ValueError('bad rva %x' % rva)

cli = r2o(cli_rva)
md_rva, md_sz = struct.unpack_from('<II', data, cli+8)
md = r2o(md_rva)
assert data[md:md+4] == b'BSJB'
vlen = struct.unpack_from('<I', data, md+12)[0]
p = md + 16 + vlen
p += 2  # flags
nstreams = struct.unpack_from('<H', data, p)[0]; p += 2
streams = {}
for i in range(nstreams):
    off, size = struct.unpack_from('<II', data, p); p += 8
    e = data.index(b'\0', p)
    nm = data[p:e].decode()
    p = e + 1
    p = (p + 3) & ~3
    streams[nm] = (md+off, size)

strings_off, strings_sz = streams['#Strings']
def gstr(idx):
    e = data.index(b'\0', strings_off+idx)
    return data[strings_off+idx:e].decode('utf8')

tso, tsz = streams['#~']
heapsizes = data[tso+6]
str_w = 4 if heapsizes & 1 else 2
guid_w = 4 if heapsizes & 2 else 2
blob_w = 4 if heapsizes & 4 else 2
valid, sorted_ = struct.unpack_from('<QQ', data, tso+8)
q = tso + 24
rows = {}
for t in range(64):
    if valid >> t & 1:
        rows[t] = struct.unpack_from('<I', data, q)[0]; q += 4
tables_start = q

def simple_w(t):
    return 4 if rows.get(t,0) >= 65536 else 2

def coded_w(tags, bits):
    mx = max(rows.get(t,0) for t in tags)
    return 4 if mx >= (1 << (16-bits)) else 2

TypeDefOrRef = coded_w([0,1,27], 2)
ResolutionScope = coded_w([0,26,35,1], 2)

sizes = {}
sizes[0]  = 2 + str_w + 3*guid_w                                   # Module
sizes[1]  = ResolutionScope + 2*str_w                              # TypeRef
sizes[2]  = 4 + 2*str_w + TypeDefOrRef + simple_w(4) + simple_w(6) # TypeDef
sizes[3]  = simple_w(4)                                            # FieldPtr
sizes[4]  = 2 + str_w + blob_w                                     # Field

off = tables_start
for t in range(64):
    if t not in rows: continue
    if t == 4:
        field_off = off
        break
    off += rows[t]*sizes[t]
else:
    raise SystemExit('no Field table')

fw = sizes[4]
def field_name(idx):  # 1-based
    b = field_off + (idx-1)*fw + 2
    si = struct.unpack_from('<I' if str_w==4 else '<H', data, b)[0]
    return gstr(si)

print('Field rows:', rows[4])

# --- scan .text for ldc*/stsfld pairs ---
text = [s for s in sects if s[0].startswith('.text')][0]
_, tva, tvsz, traw, trsz = text
blob = data[traw:traw+trsz]

out = []
i = 0
n = len(blob)
while i < n - 9:
    op = blob[i]
    val = None; ln = 0
    if op == 0x22:      # ldc.r4
        val = struct.unpack_from('<f', blob, i+1)[0]; ln = 5
    elif op == 0x23:    # ldc.r8
        val = struct.unpack_from('<d', blob, i+1)[0]; ln = 9
    elif op == 0x20:    # ldc.i4
        val = struct.unpack_from('<i', blob, i+1)[0]; ln = 5
    elif op == 0x1F:    # ldc.i4.s
        val = struct.unpack_from('<b', blob, i+1)[0]; ln = 2
    elif 0x16 <= op <= 0x1E:  # ldc.i4.0 .. 8
        val = op - 0x16; ln = 1
    if val is not None and blob[i+ln] == 0x80:  # stsfld
        tok = struct.unpack_from('<I', blob, i+ln+1)[0]
        if tok >> 24 == 0x04:
            ridx = tok & 0xFFFFFF
            if 1 <= ridx <= rows[4]:
                out.append((traw+i, field_name(ridx), val))
                i += ln + 5
                continue
    i += 1

for o, nm, v in out:
    print('%08x  %-45s %s' % (o, nm, v))
