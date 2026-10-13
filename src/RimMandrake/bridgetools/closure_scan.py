#!/usr/bin/env python3
"""closure_scan.py - refuse a companion DLL whose SHARED lambda cache names an optional mod's type.

WHY (measured live 2026-10-13, COMPANION_STATIC_LAMBDAS_UNBLOCK_WITHOUT_GSS)
The C# compiler puts every NON-capturing lambda of a class into one nested class `<>c`, with a
static field per lambda caching its delegate (`<>9__12_0 : Func<LaidPiece,bool>`). The [Tool]
methods are one `partial class JawaBenchTerrainTools` split over ~100 files, so they all share
ONE `JawaBenchTerrainTools+<>c`. Mono resolves a class's field types when it first loads the
class; if one field's delegate type names a type from a mod that is not loaded (GimmeSomeSlack
on the minimal list), the whole `<>c` throws TypeLoadException and EVERY tool that uses any
static lambda dies with capability.sdk_mismatch - jawa/time_clock, jawa/debug_settings,
jawa/map_info... none of which touch GSS.

THE RULE THIS ENFORCES
No field of the shared class itself or of its `<>c` may name a type from an OPTIONAL assembly
(anything referenced that is not the game, Unity, Harmony, the BCL or the bridge SDK). Lambdas
over an optional mod's types belong in their own class (`GssLambdas`-style holder or a nested
class of the playtest), whose `<>c` loads only when that mod's tools run.

Only FIELDS are checked: that is the class-load mechanism measured. A capturing lambda's
display class is per-method and loads only when its own tool runs, so it is out of scope.

USAGE
  python3 closure_scan.py <dll>         # exit 0 clean, 1 offenders listed, 2 cannot read
"""
import sys

SHARED_CLASS = "JawaBenchTerrainTools"

# Assemblies that are always present wherever the companion loads. Everything else the DLL
# references is an optional mod and must not appear in the shared class's field types.
CORE_ASSEMBLIES = {"mscorlib", "netstandard", "System", "System.Core", "System.Xml", "System.Xml.Linq",
                   "System.Data", "System.Runtime", "System.Numerics", "System.Drawing",
                   "Assembly-CSharp", "0Harmony", "RimBridgeServer.Sdk", "NAudio", "Unity.TextMeshPro"}


def is_core(asm):
    return asm in CORE_ASSEMBLIES or asm.startswith("UnityEngine") or asm.startswith("System.") \
        or asm.startswith("Microsoft.")


def _uncompress(b, i):
    x = b[i]
    if x & 0x80 == 0:
        return x, i + 1
    if x & 0xC0 == 0x80:
        return ((x & 0x3F) << 8) | b[i + 1], i + 2
    return ((x & 0x1F) << 24) | (b[i + 1] << 16) | (b[i + 2] << 8) | b[i + 3], i + 4


def parse_type(b, i, out):
    """Walk one Type in a signature blob (ECMA-335 II.23.2.12); append every TypeDefOrRef token
    (tag, row) to out. Returns the index after the type."""
    et = b[i]; i += 1
    if et in (0x1F, 0x20):                      # CMOD_REQD / CMOD_OPT TypeDefOrRef Type
        tok, i = _uncompress(b, i); out.append((tok & 3, tok >> 2))
        return parse_type(b, i, out)
    if et == 0x45:                              # PINNED
        return parse_type(b, i, out)
    if et <= 0x0E or et in (0x16, 0x18, 0x19, 0x1C):
        return i
    if et in (0x0F, 0x10, 0x1D):                # PTR, BYREF, SZARRAY
        return parse_type(b, i, out)
    if et in (0x11, 0x12):                      # VALUETYPE / CLASS TypeDefOrRef
        tok, i = _uncompress(b, i); out.append((tok & 3, tok >> 2))
        return i
    if et in (0x13, 0x1E):                      # VAR / MVAR number
        _, i = _uncompress(b, i)
        return i
    if et == 0x15:                              # GENERICINST (CLASS|VALUETYPE) TypeDefOrRef n Type*
        i += 1
        tok, i = _uncompress(b, i); out.append((tok & 3, tok >> 2))
        n, i = _uncompress(b, i)
        for _ in range(n):
            i = parse_type(b, i, out)
        return i
    if et == 0x14:                              # ARRAY Type rank nsizes sizes* nlo lo*
        i = parse_type(b, i, out)
        _, i = _uncompress(b, i)
        ns, i = _uncompress(b, i)
        for _ in range(ns):
            _, i = _uncompress(b, i)
        nl, i = _uncompress(b, i)
        for _ in range(nl):
            _, i = _uncompress(b, i)
        return i
    if et == 0x1B:                              # FNPTR MethodDefSig/MethodRefSig
        i += 1                                  # calling convention (generic fnptrs do not occur)
        n, i = _uncompress(b, i)
        for _ in range(n + 1):
            i = parse_type(b, i, out)
        return i
    raise ValueError("unknown element type 0x%02x" % et)


def field_type_tokens(sig):
    b = bytes(sig)
    if not b or b[0] != 0x06:
        raise ValueError("not a field signature")
    out = []
    parse_type(b, 1, out)
    return out


class Meta:
    def __init__(self, path):
        import dnfile
        self.pe = dnfile.dnPE(path)
        self.md = self.pe.net.mdtables

    @staticmethod
    def _s(x):
        return str(x) if x is not None else ""

    def typeref_assembly(self, row_index, depth=0):
        """1-based TypeRef row -> (assembly name, full type name)."""
        tr = self.md.TypeRef[row_index - 1]
        name = (self._s(tr.TypeNamespace) + "." if self._s(tr.TypeNamespace) else "") + self._s(tr.TypeName)
        scope = tr.ResolutionScope
        tbl = scope.table.name if scope is not None and scope.table is not None else None
        if tbl == "AssemblyRef":
            return self._s(self.md.AssemblyRef[scope.row_index - 1].Name), name
        if tbl == "TypeRef" and depth < 8:      # nested type: its outer type's scope decides
            asm, outer = self.typeref_assembly(scope.row_index, depth + 1)
            return asm, outer + "+" + name
        return "<self>", name

    def typespec_tokens(self, row_index):
        out = []
        parse_type(bytes(self.md.TypeSpec[row_index - 1].Signature), 0, out)
        return out

    def optional_refs(self, tokens, depth=0):
        """Every (assembly, type) an optional assembly contributes to these tokens."""
        bad = []
        for tag, row in tokens:
            if tag == 1:
                asm, nm = self.typeref_assembly(row)
                if asm != "<self>" and not is_core(asm):
                    bad.append((asm, nm))
            elif tag == 2 and depth < 8:
                bad += self.optional_refs(self.typespec_tokens(row), depth + 1)
        return bad

    def type_fields(self, td_index):
        """1-based TypeDef row -> the Field rows it owns."""
        return [f.row for f in (self.md.TypeDef[td_index - 1].FieldList or [])]

    def nested_of(self, enclosing_index):
        r = []
        for nc in self.md.NestedClass or []:
            if nc.EnclosingClass.row_index == enclosing_index:
                r.append(nc.NestedClass.row_index)
        return r


def scan(path, shared=SHARED_CLASS):
    """Return (offenders, checked_fields). offender = (owner type, field, assembly, type)."""
    m = Meta(path)
    shared_idx = [k for k, td in enumerate(m.md.TypeDef, 1) if str(td.TypeName) == shared]
    if not shared_idx:
        raise RuntimeError("class %s not found in %s" % (shared, path))
    owners = []
    for si in shared_idx:
        owners.append((shared, si))
        for ni in m.nested_of(si):
            if str(m.md.TypeDef[ni - 1].TypeName) == "<>c":
                owners.append((shared + "+<>c", ni))
    offenders, checked = [], 0
    for label, idx in owners:
        for f in m.type_fields(idx):
            checked += 1
            for asm, tn in m.optional_refs(field_type_tokens(f.Signature.value)):
                offenders.append((label, str(f.Name), asm, tn))
    return offenders, checked, len(owners)


def main(argv):
    if len(argv) != 2:
        print(__doc__); return 2
    try:
        offenders, checked, owners = scan(argv[1])
    except Exception as e:  # noqa: BLE001 - an unreadable DLL is a refusal, not a pass
        print("closure_scan: CANNOT READ %s: %s" % (argv[1], e)); return 2
    if checked == 0:
        print("closure_scan: UNMEASURED - 0 fields seen on the shared class; the instrument is blind"); return 2
    if offenders:
        print("closure_scan: %d field(s) in the shared %s / its <>c name an OPTIONAL mod's type - every tool "
              "using a static lambda dies when that mod is absent:" % (len(offenders), SHARED_CLASS))
        for o in offenders:
            print("  %-28s %-24s %s :: %s" % o)
        print("fix: move those lambdas into their own class, or make them capture a local.")
        return 1
    print("closure_scan: clean - %d fields on %d shared types, none names an optional mod's type" % (checked, owners))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
