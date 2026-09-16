"""modcheck.northstar -- read a mod's `## north star` section from its
validation walk, and decide whether it is a BAR or merely a DRAFT.

Owner rulings 2026-09-15 (design/RimMandrake/north_star_validation_spec.md):

  - the unit is one whole MOD;
  - the section lives inside the mod's existing walk file, not a new artifact;
  - `## must show` is agent-distilled from the owner's vision prose, and is NOT
    a bar until he validates it;
  - validation is recorded as a content HASH, so any later edit to the section
    silently reverts it to DRAFT. That property is the whole point: his
    judgement cannot be quietly rewritten by a later agent.

The hash covers the `## north star` SECTION only, not the whole walk file, so
an agent updating `## must be true` or the walk steps does not invalidate his
validation. It deliberately EXCLUDES the `state:` and `validated-hash:` header
lines -- otherwise recording the hash would change the thing being hashed.
"""

import hashlib
import os
import re

DRAFT = "DRAFT"
VALIDATED = "VALIDATED"

_SECTION = "## north star"
# A must-show line: `- [ ] \`some_id\` -- prose`. The checkbox may be ticked.
_MUST_SHOW_LINE = re.compile(r"^\s*-\s*\[[ xX]\]\s*`([A-Za-z0-9_]+)`")


def _walk_path(repo_root, tier, mod):
    return os.path.join(repo_root, "design", "validation_walks", tier,
                        "%s.md" % mod)


def find_walk(repo_root, mod):
    """The walk file for `mod`, searched across the three tier directories.
    Returns the path, or None if the mod has no walk. Never guesses a tier."""
    base = os.path.join(repo_root, "design", "validation_walks")
    if not os.path.isdir(base):
        return None
    for tier in sorted(os.listdir(base)):
        p = _walk_path(repo_root, tier, mod)
        if os.path.isfile(p):
            return p
    return None


def _section_lines(text):
    """The lines of the `## north star` section, exclusive of its own heading
    and stopping at the next `## ` heading. Empty list when absent."""
    out = []
    inside = False
    for line in text.splitlines():
        if line.strip().lower() == _SECTION:
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside:
            out.append(line)
    return out


def _canonical(lines):
    """The bytes the hash covers. Drops the two header fields (whose values
    change AS a result of validating) and normalises trailing whitespace, so a
    reflow that changes no words does not invalidate his validation."""
    canon = []
    for line in lines:
        stripped = line.rstrip()
        low = stripped.strip().lower()
        if low.startswith("state:") or low.startswith("validated-hash:"):
            continue
        # A blank line is not a claim, so no arrangement of them can change
        # what he validated. Dropping them outright (rather than collapsing
        # runs) is what makes any reflow free -- inserting ONE blank line is
        # as cosmetic as inserting three, and an earlier version that only
        # collapsed runs charged him a re-validation for it.
        if not stripped.strip():
            continue
        canon.append(stripped)
    return "\n".join(canon).strip().encode("utf-8")


def content_hash(lines):
    return hashlib.sha256(_canonical(lines)).hexdigest()


def parse(path):
    """Read one walk file's north star.

    Returns a dict:
      present        bool -- is there a `## north star` section at all
      declared_state DRAFT | VALIDATED, as WRITTEN in the file (untrusted)
      recorded_hash  the `validated-hash:` value in the file, or ""
      current_hash   the hash of the section as it stands on disk
      must_show      list of must-show ids, in file order
      state          the EFFECTIVE state -- VALIDATED only when the declared
                     state says so AND the recorded hash matches disk
      reason         why it is not VALIDATED, when it is not

    A missing section is `present=False, state=DRAFT, must_show=[]`, which the
    floor treats as "no visual bar for this mod" -- exactly today's behaviour.
    """
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    lines = _section_lines(text)
    if not lines:
        return {"present": False, "declared_state": DRAFT, "recorded_hash": "",
                "current_hash": "", "must_show": [], "state": DRAFT,
                "reason": "no `## north star` section in %s" % path}

    declared = DRAFT
    recorded = ""
    for line in lines:
        s = line.strip()
        low = s.lower()
        if low.startswith("state:"):
            declared = s.split(":", 1)[1].strip().upper() or DRAFT
        elif low.startswith("validated-hash:"):
            recorded = s.split(":", 1)[1].strip()

    must_show = []
    for line in lines:
        m = _MUST_SHOW_LINE.match(line)
        if m and m.group(1) not in must_show:
            must_show.append(m.group(1))

    current = content_hash(lines)

    if declared != VALIDATED:
        state, reason = DRAFT, "state: is %s, not VALIDATED" % declared
    elif not recorded:
        state, reason = DRAFT, "declared VALIDATED but carries no validated-hash"
    elif recorded != current:
        state = DRAFT
        reason = ("section edited since validation -- recorded %s, on disk %s"
                  % (recorded[:12], current[:12]))
    else:
        state, reason = VALIDATED, ""

    return {"present": True, "declared_state": declared,
            "recorded_hash": recorded, "current_hash": current,
            "must_show": must_show, "state": state, "reason": reason}


def bar_for(path):
    """The must-show ids that actually BIND for this mod: its validated ids, or
    an empty list. The one function a floor check should call -- it cannot
    accidentally enforce a DRAFT, because a DRAFT returns nothing."""
    ns = parse(path)
    return list(ns["must_show"]) if ns["state"] == VALIDATED else []


def record_validation(path):
    """Write `state: VALIDATED` and the current hash into the walk file.

    OWNER-AUTHORISED ONLY -- the caller is responsible for having his word; this
    function does not check, exactly as `code_review_status.py mark-clean` does
    not re-review the file. Returns the hash written.
    """
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    lines = _section_lines(text)
    if not lines:
        raise ValueError("no `## north star` section in %s" % path)
    new_hash = content_hash(lines)

    out, inside, done_state, done_hash = [], False, False, False
    for line in text.splitlines():
        if line.strip().lower() == _SECTION:
            inside = True
            out.append(line)
            continue
        if inside and line.startswith("## "):
            inside = False
        if inside:
            low = line.strip().lower()
            if low.startswith("state:") and not done_state:
                out.append("state: %s" % VALIDATED)
                done_state = True
                continue
            if low.startswith("validated-hash:") and not done_hash:
                out.append("validated-hash: %s" % new_hash)
                done_hash = True
                continue
        out.append(line)

    if not (done_state and done_hash):
        raise ValueError(
            "%s's north star lacks a `state:` and/or `validated-hash:` header "
            "line -- add both (blank) before validating" % path)

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + ("\n" if text.endswith("\n") else ""))
    return new_hash
