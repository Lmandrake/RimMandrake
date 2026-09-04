import os, struct, sys
# Same dead-scratchpad breakage il.py had; resolve the sibling instead.
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'meta_core.py')).read())

MEMBERREFPARENT = codedSz([0x02,0x01,0x1A,0x06,0x1B],3)
HASCONSTANT = codedSz([0x04,0x08,0x17],2)
SCHEMA[0x07]=[idxSz(0x08)]; SCHEMA[0x08]=[2,2,sSz]
SCHEMA[0x09]=[idxSz(0x02), TYPEDEFORREF]
SCHEMA[0x0A]=[MEMBERREFPARENT, sSz, bSz]
SCHEMA[0x0B]=[1,1,HASCONSTANT,bSz]
cur = tables_start; offsets.clear()
for i in range(64):
    if i in rows:
        if i not in SCHEMA: break
        offsets[i]=cur; cur += sum(SCHEMA[i])*rows[i]

# build field-row -> constant value
# 🔴 The Constant table's Type byte says whether the blob is signed or
# unsigned (I1/I2/I4/I8 = 0x04/0x06/0x08/0x0a vs U1/U2/U4/U8 =
# 0x05/0x07/0x09/0x0b). Decoding everything as signed silently flips any
# unsigned/flags enum member with the high bit set -- verified live against
# Assembly-CSharp.dll: CellConnection.NorthWest read -128 instead of 128,
# GasTypeMask.DeadlifeDust read -16777216 instead of 4278190080 (0xFF000000).
UNSIGNED_CONST_TYPES = {0x02, 0x03, 0x05, 0x07, 0x09, 0x0b}  # bool, char, u1, u2, u4, u8
consts = {}
for i in range(1, rows.get(0x0B,0)+1):
    ty, pad, parent, val = readrow(0x0B, i)
    tag = parent & 3; ri = parent >> 2
    if tag == 0:  # Field
        b = blob(val)
        signed = ty not in UNSIGNED_CONST_TYPES
        consts[ri] = int.from_bytes(b, 'little', signed=signed) if b else None

want = sys.argv[1]
for ti,(nm,ns,fl,ml,ext,fg) in enumerate(typedefs):
    if nm == want:
        nxt = typedefs[ti+1] if ti+1 < len(typedefs) else None
        fe = nxt[2] if nxt else rows[0x04]+1
        print("ENUM %s.%s" % (ns, nm))
        for f in range(fl, fe):
            ff, fnI, fsI = readrow(0x04, f)
            if ff & 0x10:  # static
                print("  %-32s = %s" % (s(fnI), consts.get(f)))
