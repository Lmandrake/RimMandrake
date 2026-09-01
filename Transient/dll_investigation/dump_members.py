import dnfile, sys

path = sys.argv[1]
targets = set(sys.argv[2:])
pe = dnfile.dnPE(path)
md = pe.net.mdtables

typedefs = md.TypeDef.rows

def type_full_name(td):
    ns = td.TypeNamespace.value if td.TypeNamespace else ""
    name = td.TypeName.value if td.TypeName else ""
    return f"{ns}.{name}" if ns else name

def resolve_type_from_token(tok):
    try:
        table_name = tok.table.name
        row = tok.row
        if table_name == "TypeDef":
            return type_full_name(row)
        elif table_name == "TypeRef":
            ns = row.TypeNamespace.value if row.TypeNamespace else ""
            name = row.TypeName.value if row.TypeName else ""
            return f"{ns}.{name}" if ns else name
        else:
            return str(tok)
    except Exception as e:
        return f"<?{e}>"

for i, td in enumerate(typedefs):
    full = type_full_name(td)
    if full not in targets:
        continue
    base = ""
    if td.Extends is not None and td.Extends.table is not None:
        base = resolve_type_from_token(td.Extends)
    print(f"=== {full}  (extends {base}) ===")
    for fi in td.FieldList:
        f = fi.row
        fl = f.Flags
        access = "public" if fl.fdPublic else ("private" if fl.fdPrivate else ("family" if fl.fdFamily else "?"))
        static = "static" if fl.fdStatic else "instance"
        print(f"  FIELD  {access:8s} {static:8s} {f.Name.value}")
    for mi in td.MethodList:
        m = mi.row
        fl = m.Flags
        access = "public" if fl.mdPublic else ("private" if fl.mdPrivate else ("family" if fl.mdFamily else "?"))
        static = "static" if fl.mdStatic else "instance"
        # param names
        params = []
        try:
            for p in m.ParamList:
                pr = p.row
                if pr.Name:
                    params.append(pr.Name.value)
        except Exception:
            pass
        print(f"  METHOD {access:8s} {static:8s} {m.Name.value}({', '.join(params)})")
