import dnfile, struct, sys

path = sys.argv[1]
pe = dnfile.dnPE(path)
md = pe.net.mdtables

def type_full_name(td):
    ns = td.TypeNamespace.value if td.TypeNamespace else ""
    nm = td.TypeName.value
    return f"{ns}.{nm}" if ns else nm

def resolve_token(tok):
    table = (tok >> 24) & 0xFF
    row = tok & 0x00FFFFFF
    try:
        if table == 0x06:  # MethodDef
            m = md.MethodDef.rows[row-1]
            return f"[MethodDef #{row}] {m.Name.value}"
        elif table == 0x0A:  # MemberRef
            mr = md.MemberRef.rows[row-1]
            cls = mr.Class
            try:
                crow = cls.row
                cname = crow.TypeName.value
            except Exception:
                cname = "?"
            return f"[MemberRef #{row}] {cname}::{mr.Name.value}"
        elif table == 0x04:  # Field
            f = md.Field.rows[row-1]
            return f"[Field #{row}] {f.Name.value}"
        elif table == 0x01:  # TypeRef
            t = md.TypeRef.rows[row-1]
            ns = t.TypeNamespace.value if t.TypeNamespace else ""
            return f"[TypeRef #{row}] {ns}.{t.TypeName.value}"
        elif table == 0x02:  # TypeDef
            t = md.TypeDef.rows[row-1]
            return f"[TypeDef #{row}] {type_full_name(t)}"
        elif table == 0x0B:  # TypeSpec
            return f"[TypeSpec #{row}]"
        elif table == 0x70:  # String (user string heap) - table id 0x70
            return f"[UserString token 0x{tok:08x}]"
        else:
            return f"[tok 0x{tok:08x}]"
    except Exception as e:
        return f"[tok 0x{tok:08x} err {e}]"

# opcode table: name -> operand size ('' none, 'i1','i4','i8','r4','r8','tok','switch','var(i1)','var(i4)')
ONE_BYTE = {
0x00:('nop',0),0x01:('break',0),
0x02:('ldarg.0',0),0x03:('ldarg.1',0),0x04:('ldarg.2',0),0x05:('ldarg.3',0),
0x06:('ldloc.0',0),0x07:('ldloc.1',0),0x08:('ldloc.2',0),0x09:('ldloc.3',0),
0x0A:('stloc.0',0),0x0B:('stloc.1',0),0x0C:('stloc.2',0),0x0D:('stloc.3',0),
0x0E:('ldarg.s',1),0x0F:('ldarga.s',1),0x10:('starg.s',1),0x11:('ldloc.s',1),
0x12:('ldloca.s',1),0x13:('stloc.s',1),0x14:('ldnull',0),
0x15:('ldc.i4.m1',0),0x16:('ldc.i4.0',0),0x17:('ldc.i4.1',0),0x18:('ldc.i4.2',0),
0x19:('ldc.i4.3',0),0x1A:('ldc.i4.4',0),0x1B:('ldc.i4.5',0),0x1C:('ldc.i4.6',0),
0x1D:('ldc.i4.7',0),0x1E:('ldc.i4.8',0),0x1F:('ldc.i4.s',1),0x20:('ldc.i4',4),
0x21:('ldc.i8',8),0x22:('ldc.r4',4),0x23:('ldc.r8',8),
0x25:('dup',0),0x26:('pop',0),
0x27:('jmp','tok'),0x28:('call','tok'),0x29:('calli','tok'),0x2A:('ret',0),
0x2B:('br.s',1),0x2C:('brfalse.s',1),0x2D:('brtrue.s',1),0x2E:('beq.s',1),
0x2F:('bge.s',1),0x30:('bgt.s',1),0x31:('ble.s',1),0x32:('blt.s',1),
0x33:('bne.un.s',1),0x34:('bge.un.s',1),0x35:('bgt.un.s',1),0x36:('ble.un.s',1),
0x37:('blt.un.s',1),0x38:('br',4),0x39:('brfalse',4),0x3A:('brtrue',4),
0x3B:('beq',4),0x3C:('bge',4),0x3D:('bgt',4),0x3E:('ble',4),0x3F:('blt',4),
0x40:('bne.un',4),0x45:('switch','switch'),
0x46:('ldind.i1',0),0x47:('ldind.u1',0),0x58:('add',0),0x59:('sub',0),
0x5A:('mul',0),0x5D:('rem',0),
0x67:('conv.i8',0),0x69:('conv.r8',0),
0x6F:('callvirt','tok'),0x70:('cpobj','tok'),0x71:('ldobj','tok'),
0x72:('ldstr',4),0x73:('newobj','tok'),0x74:('castclass','tok'),0x75:('isinst','tok'),
0x79:('unbox','tok'),0x7A:('throw',0),
0x7B:('ldfld','tok'),0x7C:('ldflda','tok'),0x7D:('stfld','tok'),
0x7E:('ldsfld','tok'),0x7F:('ldsflda','tok'),0x80:('stsfld','tok'),
0x8C:('box','tok'),0x8D:('newarr','tok'),0x8E:('ldlen',0),
0xA3:('ldelem','tok'),0xA5:('unbox.any','tok'),
0xD2:('conv.u4',0),0xD3:('conv.i8_alt',0),
0x65:('neg',0),
}

TWO_BYTE = {
0x01:('ceq',0),0x02:('cgt',0),0x03:('cgt.un',0),0x04:('clt',0),0x05:('clt.un',0),
0x06:('ldftn','tok'),0x07:('ldvirtftn','tok'),
0x09:('ldarg',2),0x0A:('ldarga',2),0x0B:('starg',2),0x0C:('ldloc',2),
0x0D:('ldloca',2),0x0E:('localloc',0),0x16:('initobj','tok'),
0x1E:('endfilter',0),
}

def get_method_body(rva):
    header = pe.get_data(rva, 1)[0]
    flag = header & 0x3
    local_var_sig = None
    if flag == 0x2:
        code_size = header >> 2
        code = pe.get_data(rva+1, code_size)
    else:
        hdr = pe.get_data(rva, 12)
        flags_size = struct.unpack('<H', hdr[0:2])[0]
        header_size_words = (flags_size >> 12) & 0xF
        code_size = struct.unpack('<I', hdr[4:8])[0]
        offset = header_size_words * 4
        code = pe.get_data(rva+offset, code_size)
    return code

def disasm(code):
    i = 0
    out = []
    n = len(code)
    while i < n:
        start = i
        b = code[i]; i += 1
        if b == 0xFE:
            b2 = code[i]; i += 1
            name, opsize = TWO_BYTE.get(b2, (f'unk.fe.{b2:02x}',0))
        else:
            name, opsize = ONE_BYTE.get(b, (f'unk.{b:02x}',0))
        operand_str = ''
        if opsize == 'tok':
            tok = struct.unpack('<I', code[i:i+4])[0]; i+=4
            operand_str = resolve_token(tok)
        elif opsize == 'switch':
            cnt = struct.unpack('<I', code[i:i+4])[0]; i+=4
            i += 4*cnt
            operand_str = f'(switch {cnt} targets)'
        elif isinstance(opsize,int) and opsize>0:
            raw = code[i:i+opsize]; i+=opsize
            if opsize==1:
                val = struct.unpack('<b', raw)[0]
            elif opsize==2:
                val = struct.unpack('<H', raw)[0]
            elif opsize==4:
                val = struct.unpack('<i', raw)[0]
            elif opsize==8:
                val = struct.unpack('<q', raw)[0]
            operand_str = str(val)
        out.append(f'IL_{start:04x}: {name} {operand_str}')
    return out

if __name__ == '__main__':
    type_name = sys.argv[2]
    method_name = sys.argv[3]
    for t in md.TypeDef.rows:
        if t.TypeName.value != type_name:
            continue
        for mi in t.MethodList:
            m = mi.row
            if m.Name.value == method_name and m.Rva:
                code = get_method_body(m.Rva)
                print(f'=== {type_name}.{method_name} ===')
                for line in disasm(code):
                    print(line)
