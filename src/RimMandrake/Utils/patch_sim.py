"""patch_sim.py -- a SMALL offline PatchOperation simulator for static checks (not the engine).

Supports Sequence, Conditional, Add (append/prepend into the matched node), Replace, Remove, with the xpath subset
`/Defs/Type[child="x"]/child`, `/Defs//tag[text()="n"]`, `.../li[text()="x"]`. Anything else raises, so an unsupported
patch is UNMEASURED rather than silently passing. Honors <success>Always</success>. Merge defs with `merge_defs`.
"""
import copy
import re
import xml.etree.ElementTree as ET


def merge_defs(paths):
    root = ET.Element("Defs")
    for p in paths:
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        if r.tag == "Defs":
            root.extend(list(r))
    return root


def _xp(xp):
    xp = xp.strip()
    if not xp.startswith("/Defs"):
        raise ValueError("unsupported xpath (must start /Defs): " + xp)
    x = "." + xp[len("/Defs"):]
    x = re.sub(r'\[text\(\)="([^"]*)"\]', r"[.='\1']", x)
    x = re.sub(r'\[([A-Za-z_]+)="([^"]*)"\]', r"[\1='\2']", x)
    if re.search(r"\band\b|\bor\b|\[\d|contains\(|starts-with\(|\|", x):
        raise ValueError("unsupported xpath form: " + xp)
    return x


def _find(root, xp):
    return root.findall(_xp(xp))


def _parents(root):
    return {c: p for p in root.iter() for c in p}


def apply(op, root):
    cls = op.get("Class", "")
    always = (op.findtext("success") or "").strip() == "Always"
    if cls == "PatchOperationSequence":
        ok = True
        for sub in op.findall("operations/li"):
            if not apply(sub, root):
                ok = False
                break
        return ok or always
    if cls == "PatchOperationConditional":
        hit = bool(_find(root, op.findtext("xpath")))
        branch = op.find("match" if hit else "nomatch")
        return apply(branch, root) if branch is not None else True
    xp = op.findtext("xpath")
    nodes = _find(root, xp)
    if cls == "PatchOperationRemove":
        par = _parents(root)
        for n in nodes:
            par[n].remove(n)
        return bool(nodes) or always
    if cls in ("PatchOperationReplace", "PatchOperationAdd"):
        val = op.find("value")
        if cls == "PatchOperationAdd" and op.findtext("order") == "Prepend":
            raise ValueError("Prepend unsupported")
        par = _parents(root)
        for n in nodes:
            if cls == "PatchOperationAdd":
                for v in val:
                    n.append(copy.deepcopy(v))
            else:
                p = par[n]
                i = list(p).index(n)
                p.remove(n)
                for k, v in enumerate(val):
                    p.insert(i + k, copy.deepcopy(v))
        return bool(nodes) or always
    raise ValueError("unsupported op class " + cls)


def apply_patch_file(path, root):
    for op in ET.parse(path).getroot().findall("Operation"):
        apply(op, root)
    return root
