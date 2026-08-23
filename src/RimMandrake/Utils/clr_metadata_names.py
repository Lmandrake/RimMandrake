"""clr_metadata_names.py — list every name in a .NET assembly's #Strings metadata heap.

    python3 src/RimMandrake/Utils/clr_metadata_names.py <assembly.dll>            # every name
    python3 src/RimMandrake/Utils/clr_metadata_names.py <assembly.dll> <substr>   # matches only

🔴 **THIS IS THE INSTRUMENT `CLAUDE.md` SAYS IS MISSING.** Its note reads: *"`strings -a -el` on
an assembly is NOT a census… Measured against the companion DLL it found 16 of 115 tool names —
.NET keeps attribute strings in metadata blobs a byte scan never reaches."*

**The reason, and it is simple:** `strings -a -el` scans for UTF-16 runs; the `#Strings` heap is
packed **null-terminated UTF-8** inside the CLI metadata blob. This walks PE → CLI header →
metadata root → `#Strings` and reads it properly, so it returns the WHOLE name table.

⭐ **So this one CAN prove a name is absent**, which `strings` never could. Validated 2026-08-23
against `Inhabited.dll`: every field its shipped XML provably uses — `traits`, `skills`, `weapon`,
`apparel`, `items`, `chassis` — is present, and so is the type `CharacterDef`. An instrument that
cannot find a known answer must not be trusted for an unknown one, so check that first.

⚠️ **WHAT IT PROVES, EXACTLY — and the limit matters.** `#Strings` holds the names of types,
fields, methods AND of members this assembly REFERENCES in others. So:
  ✅ a name ABSENT here is absent from the assembly entirely — that is a real negative;
  ⛔ a name PRESENT here is NOT proof this assembly declares it. `hediffs` and `xenotype` are
     also RimWorld's own member names, so finding them proves a reference, not a field.
🔑 Use it to KILL a hypothesis cheaply. Confirming one still needs the declaring type read.

⚠️ **Written by DECIDE while sizing `CAST_MASK_AS_GENE_1`, and left here for BUILD to keep, move
or fold into `measuring-large-artifacts`.** Tooling is not DECIDE's to own; it is committed rather
than left in a scratchpad because a scratchpad does not survive a reboot.
"""
import struct, sys

def u16(b,o): return struct.unpack_from('<H', b, o)[0]
def u32(b,o): return struct.unpack_from('<I', b, o)[0]

def strings_heap(path):
    b = open(path,'rb').read()
    pe = u32(b, 0x3C)
    assert b[pe:pe+4] == b'PE\0\0', 'not a PE'
    nsec = u16(b, pe+6); optsz = u16(b, pe+20)
    opt = pe+24
    magic = u16(b, opt)
    ddir = opt + (96 if magic == 0x10b else 112)
    cli_rva = u32(b, ddir + 14*8)
    sec = pe+24+optsz
    secs = []
    for i in range(nsec):
        s = sec + i*40
        secs.append((u32(b,s+12), u32(b,s+8), u32(b,s+20)))  # vaddr, vsize, praw
    def r2o(rva):
        for va, vs, praw in secs:
            if va <= rva < va+max(vs,1)+0x1000: return praw + (rva-va)
        raise ValueError('rva %x unmapped' % rva)
    cli = r2o(cli_rva)
    md = r2o(u32(b, cli+8))
    assert b[md:md+4] == b'BSJB', 'no metadata root'
    vlen = u32(b, md+12)
    p = md+16+vlen+4                      # skip version, flags
    nstreams = u16(b, p-2)
    for _ in range(nstreams):
        off, size = u32(b,p), u32(b,p+4)
        p += 8
        name = b''
        while b[p] != 0: name += bytes([b[p]]); p += 1
        p = (p+4) & ~3
        if name == b'#Strings':
            return b[md+off: md+off+size]
    raise ValueError('no #Strings heap')

h = strings_heap(sys.argv[1])
names = sorted({s.decode('utf-8','replace') for s in h.split(b'\0') if s})
if len(sys.argv) > 2:
    q = sys.argv[2].lower()
    hits = [n for n in names if q in n.lower()]
    print(f"{len(names)} names in #Strings; {len(hits)} match {sys.argv[2]!r}")
    for n in hits: print('  ', n)
else:
    print(f"{len(names)} names")
    for n in names: print(n)
