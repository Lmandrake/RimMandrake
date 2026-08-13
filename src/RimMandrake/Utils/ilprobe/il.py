import struct, sys
exec(open('/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/4e327811-1bab-41a8-ad20-bf4aac6d1bed/scratchpad/meta_core.py').read())

# --- opcode table: op -> (name, operand kind) ---
# kinds: '' none, 'i1','u1','i2','i4','i8','r4','r8','tok','br1','br4','sw','var1','var2'
OPS = {
0x00:('nop',''),0x01:('break',''),0x02:('ldarg.0',''),0x03:('ldarg.1',''),0x04:('ldarg.2',''),0x05:('ldarg.3',''),
0x06:('ldloc.0',''),0x07:('ldloc.1',''),0x08:('ldloc.2',''),0x09:('ldloc.3',''),
0x0a:('stloc.0',''),0x0b:('stloc.1',''),0x0c:('stloc.2',''),0x0d:('stloc.3',''),
0x0e:('ldarg.s','var1'),0x0f:('ldarga.s','var1'),0x10:('starg.s','var1'),
0x11:('ldloc.s','var1'),0x12:('ldloca.s','var1'),0x13:('stloc.s','var1'),
0x14:('ldnull',''),0x15:('ldc.i4.m1',''),
0x16:('ldc.i4.0',''),0x17:('ldc.i4.1',''),0x18:('ldc.i4.2',''),0x19:('ldc.i4.3',''),0x1a:('ldc.i4.4',''),
0x1b:('ldc.i4.5',''),0x1c:('ldc.i4.6',''),0x1d:('ldc.i4.7',''),0x1e:('ldc.i4.8',''),
0x1f:('ldc.i4.s','i1'),0x20:('ldc.i4','i4'),0x21:('ldc.i8','i8'),0x22:('ldc.r4','r4'),0x23:('ldc.r8','r8'),
0x25:('dup',''),0x26:('pop',''),0x27:('jmp','tok'),0x28:('call','tok'),0x29:('calli','tok'),0x2a:('ret',''),
0x2b:('br.s','br1'),0x2c:('brfalse.s','br1'),0x2d:('brtrue.s','br1'),0x2e:('beq.s','br1'),0x2f:('bge.s','br1'),
0x30:('bgt.s','br1'),0x31:('ble.s','br1'),0x32:('blt.s','br1'),0x33:('bne.un.s','br1'),0x34:('bge.un.s','br1'),
0x35:('bgt.un.s','br1'),0x36:('ble.un.s','br1'),0x37:('blt.un.s','br1'),
0x38:('br','br4'),0x39:('brfalse','br4'),0x3a:('brtrue','br4'),0x3b:('beq','br4'),0x3c:('bge','br4'),
0x3d:('bgt','br4'),0x3e:('ble','br4'),0x3f:('blt','br4'),0x40:('bne.un','br4'),0x41:('bge.un','br4'),
0x42:('bgt.un','br4'),0x43:('ble.un','br4'),0x44:('blt.un','br4'),0x45:('switch','sw'),
0x46:('ldind.i1',''),0x47:('ldind.u1',''),0x48:('ldind.i2',''),0x49:('ldind.u2',''),0x4a:('ldind.i4',''),
0x4b:('ldind.u4',''),0x4c:('ldind.i8',''),0x4d:('ldind.i',''),0x4e:('ldind.r4',''),0x4f:('ldind.r8',''),
0x50:('ldind.ref',''),0x51:('stind.ref',''),0x52:('stind.i1',''),0x53:('stind.i2',''),0x54:('stind.i4',''),
0x55:('stind.i8',''),0x56:('stind.r4',''),0x57:('stind.r8',''),
0x58:('add',''),0x59:('sub',''),0x5a:('mul',''),0x5b:('div',''),0x5c:('div.un',''),0x5d:('rem',''),
0x5e:('rem.un',''),0x5f:('and',''),0x60:('or',''),0x61:('xor',''),0x62:('shl',''),0x63:('shr',''),
0x64:('shr.un',''),0x65:('neg',''),0x66:('not',''),
0x67:('conv.i1',''),0x68:('conv.i2',''),0x69:('conv.i4',''),0x6a:('conv.i8',''),0x6b:('conv.r4',''),
0x6c:('conv.r8',''),0x6d:('conv.u4',''),0x6e:('conv.u8',''),
0x6f:('callvirt','tok'),0x70:('cpobj','tok'),0x71:('ldobj','tok'),0x72:('ldstr','tok'),0x73:('newobj','tok'),
0x74:('castclass','tok'),0x75:('isinst','tok'),0x76:('conv.r.un',''),0x79:('unbox','tok'),0x7a:('throw',''),
0x7b:('ldfld','tok'),0x7c:('ldflda','tok'),0x7d:('stfld','tok'),0x7e:('ldsfld','tok'),0x7f:('ldsflda','tok'),
0x80:('stsfld','tok'),0x81:('stobj','tok'),
0x82:('conv.ovf.i1.un',''),0x83:('conv.ovf.i2.un',''),0x84:('conv.ovf.i4.un',''),0x85:('conv.ovf.i8.un',''),
0x86:('conv.ovf.u1.un',''),0x87:('conv.ovf.u2.un',''),0x88:('conv.ovf.u4.un',''),0x89:('conv.ovf.u8.un',''),
0x8a:('conv.ovf.i.un',''),0x8b:('conv.ovf.u.un',''),0x8c:('box','tok'),0x8d:('newarr','tok'),0x8e:('ldlen',''),
0x8f:('ldelema','tok'),0x90:('ldelem.i1',''),0x91:('ldelem.u1',''),0x92:('ldelem.i2',''),0x93:('ldelem.u2',''),
0x94:('ldelem.i4',''),0x95:('ldelem.u4',''),0x96:('ldelem.i8',''),0x97:('ldelem.i',''),0x98:('ldelem.r4',''),
0x99:('ldelem.r8',''),0x9a:('ldelem.ref',''),0x9b:('stelem.i',''),0x9c:('stelem.i1',''),0x9d:('stelem.i2',''),
0x9e:('stelem.i4',''),0x9f:('stelem.i8',''),0xa0:('stelem.r4',''),0xa1:('stelem.r8',''),0xa2:('stelem.ref',''),
0xa3:('ldelem','tok'),0xa4:('stelem','tok'),0xa5:('unbox.any','tok'),
0xb3:('conv.ovf.i1',''),0xb4:('conv.ovf.u1',''),0xb5:('conv.ovf.i2',''),0xb6:('conv.ovf.u2',''),
0xb7:('conv.ovf.i4',''),0xb8:('conv.ovf.u4',''),0xb9:('conv.ovf.i8',''),0xba:('conv.ovf.u8',''),
0xc2:('refanyval','tok'),0xc3:('ckfinite',''),0xc6:('mkrefany','tok'),0xd0:('ldtoken','tok'),
0xd1:('conv.u2',''),0xd2:('conv.u1',''),0xd3:('conv.i',''),0xd4:('conv.ovf.i',''),0xd5:('conv.ovf.u',''),
0xd6:('add.ovf',''),0xd7:('add.ovf.un',''),0xd8:('mul.ovf',''),0xd9:('mul.ovf.un',''),0xda:('sub.ovf',''),
0xdb:('sub.ovf.un',''),0xdc:('endfinally',''),0xdd:('leave','br4'),0xde:('leave.s','br1'),0xdf:('stind.i',''),
0xe0:('conv.u',''),
}
OPS2 = {
0x00:('arglist',''),0x01:('ceq',''),0x02:('cgt',''),0x03:('cgt.un',''),0x04:('clt',''),0x05:('clt.un',''),
0x06:('ldftn','tok'),0x07:('ldvirtftn','tok'),0x09:('ldarg','var2'),0x0a:('ldarga','var2'),0x0b:('starg','var2'),
0x0c:('ldloc','var2'),0x0d:('ldloca','var2'),0x0e:('stloc','var2'),0x0f:('localloc',''),0x11:('endfilter',''),
0x12:('unaligned.','u1'),0x13:('volatile.',''),0x14:('tail.',''),0x15:('initobj','tok'),
0x16:('constrained.','tok'),0x17:('cpblk',''),0x18:('initblk',''),0x1a:('rethrow',''),0x1c:('sizeof','tok'),
0x1d:('refanytype',''),0x1e:('readonly.',''),
}

# ---- token resolution ----
MEMBERREFPARENT = codedSz([0x02,0x01,0x1A,0x06,0x1B],3)
SCHEMA[0x07] = [idxSz(0x08)]
SCHEMA[0x08] = [2,2,sSz]
SCHEMA[0x09] = [idxSz(0x02), TYPEDEFORREF]
SCHEMA[0x0A] = [MEMBERREFPARENT, sSz, bSz]
cur = tables_start
offsets.clear()
for i in range(64):
    if i in rows:
        if i not in SCHEMA: break
        offsets[i] = cur
        cur += sum(SCHEMA[i]) * rows[i]

# owner maps
fieldowner = {}; methodowner = {}
for ti,(nm,ns,fl,ml,ext,fg) in enumerate(typedefs):
    nxt = typedefs[ti+1] if ti+1 < len(typedefs) else None
    fe = nxt[2] if nxt else rows[0x04]+1
    me = nxt[3] if nxt else rows[0x06]+1
    for f in range(fl,fe): fieldowner[f]=nm
    for m in range(ml,me): methodowner[m]=nm

def typename(coded, bits=2):
    tag = coded & ((1<<bits)-1); ri = coded >> bits
    if bits==2:
        if tag==0 and ri: return typedefs[ri-1][0]
        if tag==1 and ri: return s(readrow(0x01,ri)[1])
        return 'TypeSpec#%d'%ri
    return '?'

def tok(t):
    tbl = t >> 24; ri = t & 0xFFFFFF
    if tbl == 0x06 and ri:
        r = readrow(0x06, ri); return "%s::%s" % (methodowner.get(ri,'?'), s(r[3]))
    if tbl == 0x04 and ri:
        r = readrow(0x04, ri); return "%s::%s" % (fieldowner.get(ri,'?'), s(r[1]))
    if tbl == 0x0A and ri:
        r = readrow(0x0A, ri)
        cls = r[0]; ctag = cls & 7; cri = cls >> 3
        if ctag==0 and cri: cn = typedefs[cri-1][0]
        elif ctag==1 and cri: cn = s(readrow(0x01,cri)[1])
        elif ctag==4 and cri: cn = 'TypeSpec#%d'%cri
        else: cn = '?'
        return "%s::%s" % (cn, s(r[1]))
    if tbl == 0x02 and ri: return typedefs[ri-1][0]
    if tbl == 0x01 and ri: return s(readrow(0x01,ri)[1])
    if tbl == 0x70:
        b = streams['#US'][0] + ri
        v = d[b]
        if v & 0x80 == 0: ln=v; b+=1
        elif v & 0xC0 == 0x80: ln=((v&0x3F)<<8)|d[b+1]; b+=2
        else: ln=((v&0x1F)<<24)|(d[b+1]<<16)|(d[b+2]<<8)|d[b+3]; b+=4
        return '"%s"' % d[b:b+ln-1].decode('utf-16-le','replace')
    if tbl == 0x2B: return 'MethodSpec#%d' % ri
    return 'tok%08x' % t

def disasm(rva, label):
    o = r2o(rva)
    h = d[o]
    if (h & 3) == 2:
        size = h >> 2; body = o + 1; locals_ = 0
    else:
        flags = struct.unpack_from('<H', d, o)[0]
        hsz = (flags >> 12) * 4
        size = struct.unpack_from('<I', d, o+4)[0]
        body = o + hsz
    il = d[body:body+size]
    print("=" * 72)
    print("### %s   (IL %d bytes)" % (label, size))
    i = 0
    while i < len(il):
        st = i
        op = il[i]; i += 1
        if op == 0xfe:
            op2 = il[i]; i += 1
            name, kind = OPS2.get(op2, ('fe.%02x'%op2, ''))
        else:
            name, kind = OPS.get(op, ('.%02x'%op, ''))
        arg = ''
        if kind == 'tok':
            t = struct.unpack_from('<I', il, i)[0]; i += 4; arg = tok(t)
        elif kind == 'br1':
            v = struct.unpack_from('<b', il, i)[0]; i += 1; arg = 'IL_%04x' % (i+v)
        elif kind == 'br4':
            v = struct.unpack_from('<i', il, i)[0]; i += 4; arg = 'IL_%04x' % (i+v)
        elif kind == 'i1': arg = str(struct.unpack_from('<b', il, i)[0]); i += 1
        elif kind == 'u1' or kind == 'var1': arg = str(il[i]); i += 1
        elif kind == 'var2': arg = str(struct.unpack_from('<H', il, i)[0]); i += 2
        elif kind == 'i4': arg = str(struct.unpack_from('<i', il, i)[0]); i += 4
        elif kind == 'i8': arg = str(struct.unpack_from('<q', il, i)[0]); i += 8
        elif kind == 'r4': arg = str(struct.unpack_from('<f', il, i)[0]); i += 4
        elif kind == 'r8': arg = str(struct.unpack_from('<d', il, i)[0]); i += 8
        elif kind == 'sw':
            n = struct.unpack_from('<I', il, i)[0]; i += 4
            ts = [struct.unpack_from('<i', il, i+4*k)[0] for k in range(n)]; i += 4*n
            arg = ','.join('IL_%04x'%(i+x) for x in ts)
        print("  IL_%04x: %-16s %s" % (st, name, arg))

want = sys.argv[1]
mnames = sys.argv[2:]
for ti,(nm,ns,fl,ml,ext,fg) in enumerate(typedefs):
    if nm == want:
        nxt = typedefs[ti+1] if ti+1 < len(typedefs) else None
        me = nxt[3] if nxt else rows[0x06]+1
        for m in range(ml, me):
            r = readrow(0x06, m)
            if s(r[3]) in mnames and r[0]:
                disasm(r[0], "%s::%s" % (nm, s(r[3])))
