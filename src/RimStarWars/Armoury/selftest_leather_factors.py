#!/usr/bin/env python3
"""selftest_leather_factors.py -- LEATHERFACTORS_FIX_KEEP_OWN_STATS, L0.

Armour_Leather.xml used to Replace each hide's WHOLE <stuffProps><statFactors> with our five factors, wiping the hide's
own MaxHitPoints / Flammability (Leather_Thrumbo MaxHitPoints 2.0 -> 1.3 inherited; VAEWaste_ToxicLeather lost
Flammability 2). The ops now set the five factors one child at a time (gen_armour_patch.children_xml).

Rows:
  1. form: every statFactors op in the shipped file is byte-identical to children_xml() for its def and values, and
     there are at least 80 of them (instrument sanity: 84 at the fix);
  2. function: a small PatchOperation applier (Sequence / Conditional / FindMod / Replace / Add, the classes the file
     uses) runs the WHOLE shipped file over a synthetic Defs document holding every targeted def -- half with their own
     statFactors (MaxHitPoints 2.0, Flammability 2.0, Beauty 8) and half with none -- and every hide must keep its own
     MaxHitPoints and Flammability, carry exactly the five factors at the patch's values, and hold one statFactors
     node with no duplicate child; applying the file twice changes nothing (idempotent);
  3. planted breaks: the old whole-block Replace, and a per-child Replace turned into an Add, must each redden row 2.

Run bare: python3 src/RimStarWars/Armoury/selftest_leather_factors.py   (exit 0 = clean)
"""
import ast
import copy
import os
import re
import sys

from lxml import etree as E

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "Source", "gen_armour_patch.py")
PATCH = os.path.join(HERE, "Patches", "Armour_Leather.xml")
FACTORS = ("ArmorRating_Sharp", "ArmorRating_Blunt", "ArmorRating_Heat", "Beauty", "Comfort")
FAILS = []
PARSER = E.XMLParser(remove_blank_text=True)   # whitespace tails would make the idempotence compare noisy


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def children_xml():
    """The generator's emitter, lifted by AST (the generator runs its whole pipeline at import)."""
    src = open(GEN, encoding="utf-8").read()
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "children_xml")
    ns = {"NL": "\n"}
    exec(compile(ast.Module([fn], []), GEN, "exec"), ns)
    return ns["children_xml"]


# ---------------------------------------------------------------- a minimal PatchOperation applier
def _value_nodes(op):
    v = op.find("value")
    return [c for c in v if isinstance(c.tag, str)] if v is not None else []


def apply_op(op, doc):
    """True on success, like PatchOperation.ApplyWorker. Unknown classes raise: the test must not pass blind."""
    cls = op.get("Class")
    if cls == "PatchOperationSequence":
        return all(apply_op(li, doc) for li in op.find("operations") if isinstance(li.tag, str))
    if cls == "PatchOperationFindMod":
        m = op.find("match")                   # every mod present
        return apply_op(m, doc) if m is not None else True
    if cls == "PatchOperationConditional":
        hit = bool(doc.xpath(op.findtext("xpath")))
        branch = op.find("match" if hit else "nomatch")
        return apply_op(branch, doc) if branch is not None else hit
    if cls in ("PatchOperationReplace", "PatchOperationAdd"):
        targets = doc.xpath(op.findtext("xpath"))
        for t in targets:
            if cls == "PatchOperationAdd":
                for n in _value_nodes(op):
                    t.append(copy.deepcopy(n))
            else:
                parent = t.getparent()
                i = parent.index(t)
                parent.remove(t)
                for k, n in enumerate(_value_nodes(op)):
                    parent.insert(i + k, copy.deepcopy(n))
        return bool(targets)
    raise ValueError("applier does not know " + str(cls))


def apply_file(root, doc):
    return all(apply_op(op, doc) for op in root if isinstance(op.tag, str) and op.tag == "Operation")


# ---------------------------------------------------------------- rows
def shipped_ops(text):
    """(defName, [(factor, value)]) for every per-child statFactors op, read off the text."""
    out = []
    for m in re.finditer(r'<xpath>/Defs/ThingDef\[defName="([^"]+)"\]/stuffProps/statFactors</xpath>\n\s*'
                         r'<match Class="PatchOperationSequence">(.*?)</operations>', text, re.S):
        out.append((m.group(1), re.findall(r"<value><(\w+)>([^<]+)</\1></value>", m.group(2))[::2]))
    return out


def form_problems(text, emit):
    probs = []
    n_ops = len(re.findall(r'<xpath>/Defs/ThingDef\[defName="[^"]+"\]/stuffProps/statFactors</xpath>\n'
                           r'\s*<match Class="PatchOperation', text))
    ops = shipped_ops(text)
    if len(ops) != n_ops:
        probs.append("%d statFactors ops, only %d in the per-child form" % (n_ops, len(ops)))
    for dn, items in ops:
        if tuple(n for n, _ in items) != FACTORS:
            probs.append("%s sets %s" % (dn, [n for n, _ in items]))
            continue
        body = emit('/Defs/ThingDef[defName="%s"]/stuffProps' % dn, "statFactors", items)
        inner = "\n".join(body.split("\n")[1:-2])          # without the <li ...> / </li> shell (wrapped ops reuse it)
        if inner not in text:
            probs.append("%s: op text differs from children_xml" % dn)
    return probs, len(ops)


def synthetic_defs(names):
    doc = E.fromstring("<Defs/>")
    for k, dn in enumerate(sorted(set(names))):
        td = E.SubElement(doc, "ThingDef")
        E.SubElement(td, "defName").text = dn
        sp = E.SubElement(td, "stuffProps")
        if k % 2 == 0:
            sf = E.SubElement(sp, "statFactors")
            for tag, v in (("MaxHitPoints", "2.0"), ("Flammability", "2.0"), ("Beauty", "8")):
                E.SubElement(sf, tag).text = v
    return doc


def function_problems(root, ops):
    probs = []
    want = {}
    for dn, items in ops:
        want[dn] = dict(items)                           # the three co-declared hides carry equal values twice
    doc = synthetic_defs(want)
    had_own = {td.findtext("defName") for td in doc if td.find("stuffProps/statFactors") is not None}
    apply_file(root, doc)
    first = E.tostring(doc)
    for td in doc:
        dn = td.findtext("defName")
        sfs = td.findall("stuffProps/statFactors")
        if len(sfs) != 1:
            probs.append("%s has %d statFactors nodes" % (dn, len(sfs)))
            continue
        tags = [c.tag for c in sfs[0]]
        if len(tags) != len(set(tags)):
            probs.append("%s has duplicate factors %s" % (dn, tags))
        for f in FACTORS:
            if sfs[0].findtext(f) != want[dn][f]:
                probs.append("%s %s = %s, patch says %s" % (dn, f, sfs[0].findtext(f), want[dn][f]))
        if dn in had_own:
            for f in ("MaxHitPoints", "Flammability"):
                if sfs[0].findtext(f) != "2.0":
                    probs.append("%s lost its own %s" % (dn, f))
    apply_file(root, doc)
    if E.tostring(doc) != first:
        probs.append("applying the file twice changed the defs (not idempotent)")
    if not had_own or len(had_own) == len(want):
        probs.append("instrument: synthetic defs did not mix own/absent statFactors")
    return probs


def main():
    text = open(PATCH, encoding="utf-8").read()
    emit = children_xml()
    probs, n = form_problems(text, emit)
    check("form: every statFactors op is children_xml's per-child form", not probs, "; ".join(probs[:5]))
    check("form: instrument sees the ops (>= 80)", n >= 80, "saw %d" % n)
    ops = shipped_ops(text)
    root = E.fromstring(text.encode("utf-8"), PARSER)
    probs = function_problems(root, ops)
    check("function: shipped file keeps every hide's own MaxHitPoints/Flammability, sets the 5, idempotent",
          not probs, "; ".join(probs[:5]))

    # planted break 1: the old whole-block Replace on one hide that has its own stats.
    dn, items = ops[0]
    old = ('<Operation Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="%s"]/stuffProps/statFactors</xpath>'
           "<value><statFactors>%s</statFactors></value></Operation>"
           % (dn, "".join("<%s>%s</%s>" % (f, v, f) for f, v in items)))
    broken = copy.deepcopy(root)
    broken.append(E.fromstring(old))
    got = function_problems(broken, ops)
    check("break caught: whole-block Replace wipes a hide's own stats", any("lost its own" in p for p in got),
          "stayed clean")
    # planted break 2: the per-child Replace turned into an Add (the existing factor keeps its old value).
    swapped = text.replace('<match Class="PatchOperationReplace">\n                  <xpath>/Defs/ThingDef[defName="%s"]'
                           % dn, '<match Class="PatchOperationAdd">\n                  <xpath>/Defs/ThingDef[defName="%s"]'
                           % dn, 1)
    assert swapped != text
    got = function_problems(E.fromstring(swapped.encode("utf-8"), PARSER), ops)
    check("break caught: per-child Add where the factor exists leaves the old value", bool(got), "stayed clean")
    print("RESULT", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
