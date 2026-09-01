import dnfile, sys

path = sys.argv[1]
pe = dnfile.dnPE(path)
md = pe.net.mdtables

typedefs = md.TypeDef.rows if md.TypeDef else []
for i, td in enumerate(typedefs):
    ns = td.TypeNamespace.value if td.TypeNamespace else ""
    name = td.TypeName.value if td.TypeName else ""
    full = f"{ns}.{name}" if ns else name
    print(f"TYPE[{i}] {full}")
