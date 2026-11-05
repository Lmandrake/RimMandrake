#!/usr/bin/env python3
"""selftest_pump_station_ports_compiled.py -- RUN the production C# port rule, and bind the shipped DLL to it (offline).

HOSE_END_FIX_CELL_SHORT_OF_PORT: selftest_pump_station_ports.py checks a Python MIRROR of the port rule and only
regex-reads the C#; a blind check showed a mutant RM_PumpPortMath.SideOfPort (testing side 2 only) and a dx swap in
PortCell both stayed green, and that putting back the pre-fix DLL stayed green too. This box has no C# compiler, so:

  (a) RM_PumpPortMath.PortCell and SideOfPort are translated MECHANICALLY from the production .cs file into Python
      (a small statement/expression translator; any syntax it does not know is a FAIL, never a skip) and executed over
      every footprint 1..4 x 1..4 and the S5 scene cells: four distinct edge-adjacent ports, 1x1 = Position +
      FacingCell, every other ring cell -1, and the S5 east end (114,118) beside a 3x2 station at (112,118) -> side 1.
  (b) the shipped Assemblies/RimMandrakeFlowWorks.dll is the build of these sources: its sha256 equals the .srchash
      '# dll:' line, and the .srchash rows for Machinery/RM_PumpPortMath.cs and Hose/HosePorts.cs equal the sha256 of
      those files now (the stamp is written by src/Directory.Build.targets at build; dll_source_stamp.py is the
      git-blob version of the same check).
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
DLL = os.path.join(HERE, "Assemblies", "RimMandrakeFlowWorks.dll")
fails = []
ROT4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


class Untranslatable(Exception):
    pass


# ---------------------------------------------------------------- a tiny C# -> Python translator (int math only)
TOK = re.compile(r"\s*(?:(\d+)|([A-Za-z_]\w*)|(&&|\|\||==|!=|<=|>=|\+\+|--|\+=|-=|[-+*/%<>=!?:;,(){}]))")


def tokenize(s):
    out, i = [], 0
    s = s.rstrip()
    while i < len(s):
        m = TOK.match(s, i)
        if not m or m.end() == i:
            if s[i:].strip() == "":
                break
            raise Untranslatable("token at %r" % s[i:i + 20])
        out.append(m.group(1) or m.group(2) or m.group(3))
        i = m.end()
    return out


class P:
    def __init__(self, toks, outs, fnames):
        self.t, self.i, self.outs, self.fnames = toks, 0, outs, fnames

    def peek(self, k=0):
        return self.t[self.i + k] if self.i + k < len(self.t) else None

    def take(self, want=None):
        tok = self.peek()
        if tok is None or (want is not None and tok != want):
            raise Untranslatable("wanted %r got %r" % (want, tok))
        self.i += 1
        return tok

    # expressions: ternary > || > && > == != > < <= > >= > + - > * / % > unary > primary
    def expr(self):
        c = self.orx()
        if self.peek() == "?":
            self.take("?")
            a = self.expr()
            self.take(":")
            b = self.expr()
            return "(%s if %s else %s)" % (a, c, b)
        return c

    def binary(self, sub, ops):
        left = sub()
        while self.peek() in ops:
            op = self.take()
            right = sub()
            left = "(%s %s %s)" % (left, ops[op], right)
        return left

    def orx(self):
        return self.binary(self.andx, {"||": "or"})

    def andx(self):
        return self.binary(self.eqx, {"&&": "and"})

    def eqx(self):
        return self.binary(self.relx, {"==": "==", "!=": "!="})

    def relx(self):
        return self.binary(self.addx, {"<": "<", "<=": "<=", ">": ">", ">=": ">="})

    def addx(self):
        return self.binary(self.mulx, {"+": "+", "-": "-"})

    def mulx(self):
        return self.binary(self.unary, {"*": "*"})       # int / and % differ from Python on negatives: refuse them

    def unary(self):
        if self.peek() == "-":
            self.take()
            return "(-%s)" % self.unary()
        if self.peek() == "!":
            self.take()
            return "(not %s)" % self.unary()
        return self.primary()

    def primary(self):
        tok = self.take()
        if tok == "(":
            e = self.expr()
            self.take(")")
            return e
        if tok.isdigit():
            return tok
        if re.fullmatch(r"[A-Za-z_]\w*", tok) and tok not in ("true", "false", "null", "new", "out"):
            return tok
        raise Untranslatable("primary %r" % tok)

    # statements
    def block(self, ind):
        lines = []
        self.take("{")
        while self.peek() != "}":
            lines += self.stmt(ind)
        self.take("}")
        return lines or [ind + "pass"]

    def body(self, ind):
        return self.block(ind) if self.peek() == "{" else self.stmt(ind)

    def ret(self):
        if self.outs:
            return "return (%s)" % ", ".join(self.outs) + ("," if len(self.outs) == 1 else "")
        return "return"

    def stmt(self, ind):
        tok = self.peek()
        if tok == "if":
            self.take()
            self.take("(")
            c = self.expr()
            self.take(")")
            lines = [ind + "if %s:" % c] + self.body(ind + "    ")
            if self.peek() == "else":
                self.take()
                lines += [ind + "else:"] + self.body(ind + "    ")
            return lines
        if tok == "while":
            self.take()
            self.take("(")
            c = self.expr()
            self.take(")")
            return [ind + "while %s:" % c] + self.body(ind + "    ")
        if tok == "for":
            self.take()
            self.take("(")
            init = self.simple(ind)
            self.take(";")
            c = self.expr()
            self.take(";")
            inc = self.simple(ind + "    ")
            self.take(")")
            inner = self.body(ind + "    ")
            if any("continue" in ln for ln in inner):
                raise Untranslatable("continue inside for")
            return init + [ind + "while %s:" % c] + inner + inc
        if tok == "return":
            self.take()
            if self.peek() == ";":
                self.take(";")
                return [ind + self.ret()]
            e = self.expr()
            self.take(";")
            if self.outs:
                raise Untranslatable("value return with out params")
            return [ind + "return %s" % e]
        lines = self.simple(ind)
        self.take(";")
        return lines

    def simple(self, ind):
        """declaration, assignment, ++/--, or a call to a translated function with out args."""
        if self.peek() == "int":
            self.take()
        name = self.take()
        if not re.fullmatch(r"[A-Za-z_]\w*", name):
            raise Untranslatable("statement %r" % name)
        op = self.peek()
        if op in ("=", "+=", "-="):
            self.take()
            return [ind + "%s %s %s" % (name, op, self.expr())]
        if op in ("++", "--"):
            self.take()
            return [ind + "%s %s 1" % (name, "+=" if op == "++" else "-=")]
        if op == "(" and name in self.fnames:
            self.take("(")
            args, outs = [], []
            while True:
                if self.peek() == "out":
                    self.take("out")
                    if self.peek() == "int":
                        self.take()
                    outs.append(self.take())
                else:
                    args.append(self.expr())
                if self.peek() == ",":
                    self.take(",")
                    continue
                self.take(")")
                break
            call = "%s(%s)" % (name, ", ".join(args))
            if outs:
                return [ind + "%s = %s" % (", ".join(outs) + ("," if len(outs) == 1 else ""), call)]
            return [ind + call]
        raise Untranslatable("statement %s %r" % (name, op))


def method(cs, name):
    """(params, body) of `public static <ret> name(params) { body }`, the body found by brace matching."""
    m = re.search(r"public static (?:int|void|bool) %s\(([^)]*)\)\s*\{" % name, cs)
    if not m:
        raise Untranslatable("method %s not found" % name)
    depth, i = 1, m.end()
    while depth:
        if i >= len(cs):
            raise Untranslatable("unbalanced %s" % name)
        depth += {"{": 1, "}": -1}.get(cs[i], 0)
        i += 1
    return m.group(1), cs[m.end() - 1:i]


def translate(cs, names):
    py = []
    for name in names:
        params, body = method(cs, name)
        ins, outs = [], []
        for p in [p.strip() for p in params.split(",") if p.strip()]:
            parts = p.split()
            if parts[0] == "out" and parts[1:2] == ["int"] and len(parts) == 3:
                outs.append(parts[2])
            elif parts[0] == "int" and len(parts) == 2:
                ins.append(parts[1])
            else:
                raise Untranslatable("param %r" % p)
        p = P(tokenize(body), outs, set(names))
        lines = p.block("    ")
        if p.peek() is not None:
            raise Untranslatable("trailing tokens in %s" % name)
        py.append("def %s(%s):" % (name, ", ".join(ins)))
        py += ["    %s = None" % o for o in outs]
        py += lines
        if outs:
            py.append("    " + p.ret())
    return "\n".join(py) + "\n"


def run_csharp_rule(cs):
    src = translate(cs, ["PortCell", "SideOfPort"])
    env = {}
    exec(compile(src, "RM_PumpPortMath.cs(translated)", "exec"), env)
    return env["PortCell"], env["SideOfPort"], src


def position_of(min_x, min_z, w, h):
    return min_x + (w - 1) // 2, min_z + (h - 1) // 2


def sweep(port_cell, side_of_port):
    bad = []
    for w in range(1, 5):
        for h in range(1, 5):
            mx, mz = 10, 20
            px, pz = position_of(mx, mz, w, h)
            cells = {}
            for s in range(4):
                c = tuple(port_cell(mx, mz, w, h, px, pz, s))
                cells[c] = s
                inside = mx <= c[0] < mx + w and mz <= c[1] < mz + h
                touch = sum(1 for dx, dz in ROT4 if mx <= c[0] + dx < mx + w and mz <= c[1] + dz < mz + h)
                # side s's port lies OUT along side s: beyond the footprint edge in that direction
                dx, dz = ROT4[s]
                beyond = (dx == 1 and c[0] == mx + w) or (dx == -1 and c[0] == mx - 1) or \
                         (dz == 1 and c[1] == mz + h) or (dz == -1 and c[1] == mz - 1)
                if inside or touch != 1 or not beyond:
                    bad.append((w, h, s, c))
                if w == 1 and h == 1 and c != (px + dx, pz + dz):
                    bad.append((w, h, s, "1x1 not Position+FacingCell"))
            if len(cells) != 4:
                bad.append((w, h, "ports not distinct"))
            for x in range(mx - 2, mx + w + 2):
                for z in range(mz - 2, mz + h + 2):
                    want = cells.get((x, z), -1)
                    if side_of_port(mx, mz, w, h, px, pz, x, z) != want:
                        bad.append((w, h, (x, z), "SideOfPort != %d" % want))
    return bad


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    with open(os.path.join(SRC, "Machinery", "RM_PumpPortMath.cs"), encoding="utf-8") as f:
        cs = f.read()
    try:
        port_cell, side_of_port, _ = run_csharp_rule(cs)
    except (Untranslatable, SyntaxError) as e:
        check(False, "C# RM_PumpPortMath.PortCell/SideOfPort translate and run (%s)" % e)
        port_cell = None
    if port_cell:
        check(True, "C# RM_PumpPortMath.PortCell/SideOfPort translated from the production file and executed")
        bad = sweep(port_cell, side_of_port)
        check(not bad, "C# run: every footprint 1..4 x 1..4 has 4 distinct ports, one out along each side, 1x1 = "
              "Position + FacingCell, every other ring cell -1 (%s)" % (bad[:3] if bad else "16 footprints"))
        # S5: 3x2 station at (112,118) -> footprint x 111..113, z 118..119
        args = (111, 118, 3, 2, 112, 118)
        check(side_of_port(*args, 114, 118) == 1, "C# run S5: SideOfPort(111,118,3,2,112,118, 114,118) == 1 (east port)")
        check(tuple(port_cell(*args, 1)) == (114, 118), "C# run S5: PortCell(..., east) == (114,118)")
        got = {s: tuple(port_cell(*args, s)) for s in range(4)}
        check(got == {0: (112, 120), 1: (114, 118), 2: (112, 117), 3: (110, 118)},
              "C# run S5: the station's four ports N (112,120) E (114,118) S (112,117) W (110,118) (%s)" % got)
        check(side_of_port(*args, 114, 119) == -1 and side_of_port(*args, 114, 117) == -1,
              "C# run S5: the east side's other lane and the SE corner are no port")

    # (b) the shipped DLL is the build of these sources
    stamp_path = DLL + ".srchash"
    with open(stamp_path, encoding="utf-8") as f:
        stamp = f.read()
    m = re.search(r"^# dll: ([0-9a-f]{64})$", stamp, re.M)
    check(m is not None and m.group(1) == sha256(DLL),
          "DLL: RimMandrakeFlowWorks.dll bytes match its .srchash '# dll:' line")
    rows = dict((p, h) for h, p in re.findall(r"^([0-9a-f]{64}) (\S.*)$", stamp, re.M))
    for rel in ("Machinery/RM_PumpPortMath.cs", "Hose/HosePorts.cs"):
        check(rows.get(rel) == sha256(os.path.join(SRC, *rel.split("/"))),
              "DLL: .srchash records the current %s (the DLL was built from it)" % rel)

    print("selftest_pump_station_ports_compiled.py: %d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
