#!/usr/bin/env python3
"""Validate skill folders: structure, wiring, and — the valuable part — that every
`jawa/<tool>` name mentioned anywhere in a skill actually EXISTS in the companion source.

Written 2026-08-19 after a fresh-eyes review found `jawa/world_objects_add` documented in
`rimbridge/references/world-authoring.md`. That tool has never existed. It was invented by
the same skill that tells you never to type a tool name you did not just read — which is
precisely why this check is worth its keep.

    python3 skills/validate_skills.py                # all skills
    python3 skills/validate_skills.py rimbridge ...  # named ones
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = "/mnt/d/Luke/dev/Rimworld/src/RimMandrake/bridgetools/JawaBench.BridgeTools"

# Documentation legitimately contains a glob and a teaching placeholder.
ALLOWED_NONTOOLS = {"jawa/world_", "jawa/thing_do", "jawa/set_"}

def real_tools():
    got = set()
    if not os.path.isdir(SRC):
        return None
    for f in os.listdir(SRC):
        if f.endswith(".cs"):
            got |= set(re.findall(r'"(jawa/[a-z_]+)"',
                                  open(os.path.join(SRC, f), encoding="utf-8").read()))
    return got

def main():
    targets = sys.argv[1:] or sorted(
        d for d in os.listdir(ROOT)
        if os.path.isdir(os.path.join(ROOT, d))
        and os.path.isfile(os.path.join(ROOT, d, "SKILL.md")))
    tools = real_tools()
    issues = []
    def add(sk, sev, msg): issues.append((sev, sk, msg))

    for sk in targets:
        d = os.path.join(ROOT, sk); p = os.path.join(d, "SKILL.md")
        raw = open(p, encoding="utf-8").read()
        if not raw.startswith("---"):
            add(sk, "ERROR", "no YAML frontmatter"); continue
        end = raw.find("\n---", 3)
        fm, body = raw[3:end], raw[end+4:]

        name = re.search(r"^name:\s*(.+)$", fm, re.M)
        desc = re.search(r"^description:\s*(.+(?:\n(?!\w+:).*)*)$", fm, re.M)
        if not name or name.group(1).strip() != sk:
            add(sk, "ERROR", "frontmatter name != directory name")
        words = 0
        if not desc:
            add(sk, "ERROR", "no description — this is the trigger mechanism")
        else:
            dt = " ".join(desc.group(1).split()); words = len(dt.split())
            if words < 25: add(sk, "WARN", "description thin (%d words)" % words)
            if "use " not in dt.lower(): add(sk, "WARN", "description has no 'Use when' clause")

        bl = len(body.splitlines())
        if bl > 500: add(sk, "WARN", "SKILL.md body %d lines (>500) — consider splitting" % bl)

        # reference wiring. A fully-qualified skills/<other>/references/x.md is a
        # legitimate CROSS-skill link, so only count bare own-skill pointers.
        refdir = os.path.join(d, "references")
        on_disk = {f for f in os.listdir(refdir) if f.endswith(".md")} if os.path.isdir(refdir) else set()
        mentioned = set(re.findall(r"(?<!/)\breferences/([A-Za-z0-9._-]+\.md)", raw))
        # ...an absolute path to our own reference counts...
        mentioned |= {os.path.basename(m) for m in
                      re.findall(r"skills/%s/references/([A-Za-z0-9._-]+\.md)" % re.escape(sk), raw)}
        # ...so does a BARE filename in a routing table (`├ traps-art.md`)...
        mentioned |= {f for f in on_disk if f in raw}
        # ...and so does a glob (`references/traps-*.md`).
        for g in re.findall(r"references/([A-Za-z0-9._-]*)\*([A-Za-z0-9._-]*\.md)", raw):
            pre, suf = g
            mentioned |= {f for f in on_disk if f.startswith(pre) and f.endswith(suf)}
        for m in mentioned - on_disk:
            add(sk, "ERROR", "points at references/%s which does not exist" % m)
        for o in on_disk - mentioned:
            add(sk, "WARN", "references/%s is never pointed at" % o)

        # ⭐ the check that earns this script its place
        if tools is not None:
            for root, _, fs in os.walk(d):
                for f in fs:
                    if not f.endswith(".md"): continue
                    fp = os.path.join(root, f)
                    txt = open(fp, encoding="utf-8", errors="replace").read()
                    for t in set("jawa/" + m for m in re.findall(r"\bjawa/([a-z_]{3,})", txt)):
                        if t not in tools and t not in ALLOWED_NONTOOLS:
                            add(sk, "ERROR", "%s names '%s' which is NOT a real tool"
                                % (os.path.relpath(fp, d), t))

        print("%-26s body=%4d  refs=%2d  desc=%3d words" % (sk, bl, len(on_disk), words))

    print()
    if tools is not None:
        print("companion source declares %d jawa/ tools" % len(tools))
    for sev in ("ERROR", "WARN"):
        got = [i for i in issues if i[0] == sev]
        print("%s (%d)" % (sev, len(got)))
        for _, sk, msg in got:
            print("   %-26s %s" % (sk, msg))
    return 1 if any(i[0] == "ERROR" for i in issues) else 0

if __name__ == "__main__":
    sys.exit(main())
