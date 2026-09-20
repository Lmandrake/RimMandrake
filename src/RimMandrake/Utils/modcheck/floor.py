"""modcheck.floor -- the Mod Settings toggle FLOOR.

Owner ruling 2026-09-12: a mod's Mod Settings toggles are the floor -- every
toggle has at least one covering component -- and the builder adds
components for complex functions beyond any toggle. The ceiling is open;
this module has no opinion on it, and enforces only the floor.

KNOWN GAP, recorded rather than papered over: as of 2026-09-12 most mods
(the pilot, `RimMandrake Pits`, included) have no Mod Settings at all yet --
that is `MOD_OPTIONS_RETROFIT_1`'s job, not this module's. Zero toggles is
not a floor violation here; it means every component in that mod's suite is
necessarily `beyond_toggle=True` until settings exist to cover.
"""


def uncovered(toggles, components):
    """`toggles`: iterable of Mod Settings toggle field names.
    `components`: iterable of {"toggle": name_or_None, "beyond_toggle": bool}
    dicts, one per registered component across every chain in a `Suite`.

    Returns the sorted list of toggle names with zero covering component.
    Empty means the floor is met. Never raises -- callers (a CLI, a runner)
    decide whether an uncovered toggle is fatal to a run.
    """
    covered = {c["toggle"] for c in components if c.get("toggle")}
    return sorted(set(toggles) - covered)


def uncovered_shows(must_show_ids, components):
    """The VISUAL floor -- owner ruling 2026-09-15, north_star_validation_spec.md
    section 3. Mirror of `uncovered` above: uncovered EXPERIENCE is as fatal as
    an uncovered settings toggle.

    `must_show_ids`: iterable of must-show ids from the mod's walk `## north
    star` section -- pass ONLY the ids of a VALIDATED section. A DRAFT section
    contributes nothing: it cannot fail a mod and cannot green one.
    `components`: the same component dicts, each optionally carrying "shows".

    Returns the sorted list of must-show ids no component claims. Empty means
    the visual floor is met. Never raises; the caller decides fatality.
    """
    claimed = set()
    for c in components:
        claimed.update(c.get("shows") or ())
    return sorted(set(must_show_ids) - claimed)


def orphan_shows(must_show_ids, components):
    """The reverse check: ids a component CLAIMS that the validated checklist
    does not define. A lint error, never a silent pass -- claiming to show
    something nobody asked for is the same defect class as a patch that matches
    nothing (CLAUDE.md, 'A patch that matches nothing logs nothing').

    Commonly means a must-show id was renamed and a `shows=` was left behind.
    Returns the sorted list of orphaned ids.
    """
    claimed = set()
    for c in components:
        claimed.update(c.get("shows") or ())
    return sorted(claimed - set(must_show_ids))


# --------------------------------------------------------------------------
# `modcheck floor --all` -- infrastructure/DETERMINISM_ASSESSMENT.md SS6 (C4).
#
# The triage nobody has run: one offline pass over every validation walk,
# joining walklint's subject/PNG facts to northstar's bar and runner's
# component coverage, so "44 bars bind, 0 covered" stops being a fact only a
# full re-derivation surfaces. Report only -- this module never refuses a
# run; `runner.refusal` already does that off the same functions.
# --------------------------------------------------------------------------
import re as _re

_S_STEP_RE = _re.compile(r"^\s*(?:#{1,6}\s*|\d+[.)]\s*|-\s*)?\[S\]")


def _subject_dir(lines):
    """The token after the walk's first `subject:` line, or "" if absent.
    Mirrors walklint.lint_walk's own extraction so the two never disagree."""
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("subject:"):
            rest = stripped.split(":", 1)[1].strip()
            return rest.split()[0] if rest.split() else ""
    return ""


def _png_count(repo_root, subject_token):
    """Every `*.png` under the subject folder, recursively. 0 if the folder
    does not exist -- never raises, since a bad subject is walklint's own
    BAD_SUBJECT finding, not this function's job to flag again."""
    import os
    base = os.path.join(repo_root, subject_token)
    if not os.path.isdir(base):
        return 0
    n = 0
    for _dirpath, _dirnames, filenames in os.walk(base):
        n += sum(1 for f in filenames if f.lower().endswith(".png"))
    return n


def triage(repo_root):
    """One row per validation walk. Returns (rows, footer).

    Each row: {mod, walk, subject_ok, png_count, has_s_step, ns_state,
    bars, covered, uncovered, verdict}.

    `covered`/`uncovered` come from the SAME join a live `run` would refuse
    on (`runner.visual_floor`, `floor.uncovered_shows`) -- called here for
    every mod instead of only the one under test. A mod whose folder or
    `validation.py` is missing simply contributes 0 components; that is a
    fact about coverage, not an error this function raises.
    """
    import os
    import northstar
    import runner
    import walklint

    walks = walklint.find_walks(repo_root)
    rows = []
    for path in walks:
        mod = os.path.splitext(os.path.basename(path))[0]
        text = open(path, "r", encoding="utf-8", errors="replace").read()
        lines = text.splitlines()

        subject_token = _subject_dir(lines)
        subject_ok = bool(subject_token) and os.path.isfile(
            os.path.join(repo_root, subject_token, "About", "About.xml"))
        png_count = _png_count(repo_root, subject_token) if subject_token else 0
        has_s_step = any(_S_STEP_RE.match(l) for l in lines)

        ns = northstar.parse(path)
        bars = list(ns["must_show"]) if ns["state"] == northstar.VALIDATED else []

        components = []
        try:
            mod_dir = runner.find_mod_dir(mod)
        except RuntimeError:
            mod_dir = None
        if mod_dir:
            try:
                suite = runner.load_validation(mod_dir)
                components = suite.components_declared()
            except Exception:
                components = []

        uncovered = uncovered_shows(bars, components) if bars else []
        covered_n = len(bars) - len(uncovered)

        if not bars:
            verdict = "no bar"
        elif not uncovered:
            verdict = "bar met"
        else:
            verdict = "REFUSED (uncovered)"

        rows.append({
            "mod": mod, "walk": True, "subject_ok": subject_ok,
            "png_count": png_count, "has_s_step": has_s_step,
            "ns_state": ns["state"], "bars": len(bars),
            "covered": covered_n, "uncovered": len(uncovered),
            "verdict": verdict,
        })

    ships_visual = sum(1 for r in rows if r["png_count"] >= 1)
    total_bars = sum(r["bars"] for r in rows)
    total_covered = sum(r["covered"] for r in rows)
    footer = ("%d mods ship visual surface; %d bars bind; %d are covered."
             % (ships_visual, total_bars, total_covered))
    return rows, footer


def format_triage(rows, footer):
    out = ["%-28s %-4s %-4s %5s %-3s %-9s %4s %7s %9s  %s"
          % ("mod", "walk", "subj", "PNGs", "[S]", "northstar", "bars",
             "covered", "uncovered", "verdict")]
    for r in rows:
        out.append("%-28s %-4s %-4s %5d %-3s %-9s %4d %7d %9d  %s" % (
            r["mod"], "yes", "ok" if r["subject_ok"] else "BAD",
            r["png_count"], "yes" if r["has_s_step"] else "-",
            r["ns_state"], r["bars"], r["covered"], r["uncovered"],
            r["verdict"]))
    out.append(footer)
    return "\n".join(out)
