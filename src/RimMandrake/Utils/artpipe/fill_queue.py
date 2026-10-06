#!/usr/bin/env python3
"""fill_queue.py — turn an art-list CSV/JSON into artpipe job files.

Reads rows describing art to (re)generate and writes one job JSON per row per
facing into `infrastructure/artpipe/pending/` (ART_PIPELINE_DAEMON_1,
deliverable 4) — the only writer of that directory a human is meant to run by
hand; the daemon's claim (atomic rename to `active/`) never touches it.

CSV columns (JSON: same keys; `facings` may be a JSON list there):
    id                 base id — one job file per facing gets "<id>_<facing>"
                       (bare "<id>" if facings is empty)
    rimflow_item_id    provenance — which ledger item this art serves
    prompt             the generation instruction
    canvas_w, canvas_h pixels the worker must generate at
    reference          optional — path to the existing sprite this reskins;
                       blank means new art, no --image on the worker.
                       VERIFIED to exist at filing time and stored ABSOLUTE
                       — a dangling reference is refused here rather than
                       surfacing later as a validate_sprite.py exit-2 the
                       daemon has to distinguish from a real art rejection.
    facings            optional — comma/semicolon-separated (CSV) or a list
                       (JSON); empty means one job named bare "<id>"
    style_notes        optional — free text, folded into the prompt
    priority           optional int, default 100 — LOWER claims sooner.
                       A blank CSV cell reads as '' (not a missing key) and
                       is treated the same as absent, not as int('').
    background         optional, default "transparent"
    channel            optional per-row override — "codex" or "gemini".
                       Every row otherwise gets --channel's value
                       (default "codex"); see GEMINI_WORKER_BACKEND_1.
    canon              optional — canon-library entry name under
                       design/RimStarWars/canon_references/; its
                       `## Visual brief` + `## Must show` are appended to
                       style_notes. A named entry with no brief is REFUSED.
    target_def         REQUIRED (ART_SUBJECT_RESOLVER_1) — the defName this
                       render is a picture of. A donor/original defName is
                       accepted and mapped to ours (it is kept as an
                       original). A row without one is REFUSED unless it
                       carries `no_subject: "<why>"` or the run passes
                       --no-subject "<why>" (templates, glyphs, fixtures).
    target_original    optional — the ORIGINAL name(s) (donor defName, canon
                       species), comma/semicolon-separated or a JSON list.
                       Owner, 2026-10-04: renders are named by their original
                       name as well as ours, so a rename never loses the
                       donor or canon reference. Known donor names for
                       target_def (rename comments, mlie maps) are added.
    target_texpath     optional — the texPath (no facing suffix) the art is
                       for; defaults to the def's body texPath when it has
                       exactly one (art/subject.py).
    install_to         optional — repo-relative PNG destination for
                       `artpipe_state.py collect --from-jobs`; "{facing}" is
                       substituted per job.
    derive_from        optional — id of a FINISHED sibling job (done manifest + _artsrc PNG); every facing
                       of the row is filed as an edit of that accepted render (same individual).
    owner_note         optional — the owner's verbatim note, carried onto the job as its own field so the
                       canon gate (canon_check.py) grades against it (wins over canon where they differ).
    canon_na           optional — Must-show lines (1-based numbers or exact texts; list, or "2;4;5" in CSV)
                       the canon gate marks n/a for this job and does not count; `canon_na_reason` says why.
                       Any OTHER unknown row field is WARNED about on stderr, never silently dropped.
    canon_reference    optional — image path(s) to attach as ANATOMY guidance.
                       Defaults to the canon-library entry's images when
                       art/subject.py resolves one for target_def (exact or
                       base species). Never `reference` — that arms
                       reskin-validate (same-pose pixel fidelity), which a
                       canon photo would always fail. The daemon attaches the
                       first image only when the job has no `reference` and no
                       `derive_from`; the job's prompt says how to use it.
    biome_register     optional — the subject's biome light/palette register
                       (from its biome sheet), prepended to style_notes.
                       A row with neither this nor `biome_neutral: true`
                       gets a warning.

ART_VERSION_WRANGLING_1 (owner, 2026-10-04): the retired "Heavy, clean black
outline" clause is scrubbed from prompt and style_notes with a warning, and a
row still mentioning "black outline"/"keyline" afterwards is REFUSED. The
house register (common.HOUSE_ART_REGISTER) is appended to style_notes of every
transparent-background job that does not already say "no outlines".

ARTPIPE_FACING_COHERENCE_1 §2 — DEFAULT ON, `--no-derive-facings` to disable:
a row whose `facings` include "east" files east as the fresh-generated
MASTER; its north/south jobs (if also requested) carry `derive_from:
"<id>_east"` and get derivation language prepended to their own prompt,
instead of being independent fresh prompts. A row that already names its
own `reference` is never also given `derive_from` — see common.load_job.

Refuses a duplicate job id — checked against pending/active/done/failed all
at once, so an id already claimed, finished or failed is exactly as
protected as one still waiting. The write itself goes to a tmp file first,
then `os.link()`s it into pending/ — the same exclusivity an O_EXCL create
would give, but without ever leaving a partially-written file sitting at
the real path if this process is killed mid-write (that used to be able to
permanently block the id: a corrupt file at `dest` is still a file `dest`
has, so id_taken() would refuse every future refile of it).

    python3 fill_queue.py --input art_list.csv
    python3 fill_queue.py --input art_list.json --dry-run
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "art"))
import artreg  # noqa: E402 — ART_REGEN_REGISTRY_1: sole writer of registry.jsonl

REQUIRED_ROW_FIELDS = ("id", "rimflow_item_id", "prompt", "canvas_w", "canvas_h")

# Every row field row_to_jobs/bind_subject reads. Anything else is WARNED about (never silently dropped).
KNOWN_ROW_FIELDS = frozenset(REQUIRED_ROW_FIELDS) | {
    "background", "biome_neutral", "biome_register", "canon", "canon_reference", "channel", "derive_from",
    "drawsize", "facings", "install_to", "no_subject", "oversize_reason", "priority", "reference",
    "style_notes", "target_def", "target_original", "target_texpath",
    "owner_note", "canon_na", "canon_na_reason"}


def _split_na(v):
    """canon_na cell -> list of ints / exact texts. A list passes through; a string splits on ';' or '|'
    (a bare '2,4,5' of digits splits on commas too, since line texts never look like that)."""
    if v in (None, ""):
        return []
    if isinstance(v, (list, tuple)):
        items = list(v)
    else:
        t = str(v).strip()
        items = re.split(r"[,;|]", t) if re.fullmatch(r"[\d\s,;|]+", t) else re.split(r"[;|]", t)
    out = []
    for x in items:
        if isinstance(x, str):
            x = x.strip()
            if not x:
                continue
            if x.isdigit():
                x = int(x)
        out.append(x)
    return out

# ARTPIPE_FACING_COHERENCE_1 §2: north/south are derivations of the accepted
# east master, not fresh prompts — "same individual, same palette, same
# edge treatment, same painted style, same scale, rotated to the view
# described below." Prepended to a derived job's own prompt; the per-facing
# view direction itself still comes from artpiped.build_job_prompt()'s
# existing stamp, unchanged.
DERIVE_PROMPT_PREFIX = (
    "Derive this facing from the attached accepted master render of the SAME "
    "creature: same individual, same palette, same edge treatment, same "
    "painted style, same scale — rotated to the view described below. Do "
    "not restyle. "
)

# Only these two facings derive from the master — the brief and the owner's
# ruling name north/south specifically (the east job IS the master); a row
# that also asks for "west" gets an independent, freshly-prompted west job,
# same as today.
_DERIVED_FACINGS = ("north", "south")
_MASTER_FACING = "east"


# ART_SUBJECT_RESOLVER_1: prepended to a job that carries canon_reference and
# no reference/derive_from, so the attached photo is read as anatomy guidance,
# never as an image to edit.
CANON_PROMPT_PREFIX = (
    "The attached image is a CANON REFERENCE of this species, not a sprite to "
    "edit: match its anatomy, proportions, limb count and colouring, but draw "
    "a NEW game sprite in the house style below — do not copy its pixels, "
    "background, lighting or camera framing. "
)


def _split_names(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    return [x.strip() for x in str(raw).replace(";", ",").split(",") if x.strip()]


def _world():
    """art/subject.World, built once per process (lazy: nothing is read until a row needs it)."""
    global _WORLD
    if _WORLD is None:
        import subject  # noqa: E402 — art/subject.py
        _WORLD = subject.World()
    return _WORLD


_WORLD = None


def bind_subject(row: dict, no_subject: str | None = None, world=None) -> dict:
    """The binding fields for a row's jobs (ART_SUBJECT_RESOLVER_1). Refuses a row with no target_def
    unless a no-subject reason is given. WORLD (art/subject.World) resolves originals, texPath and canon;
    None means 'use the default World'; False means 'resolve nothing, keep only what the row says'."""
    base_id = row.get("id", "?")
    target = str(row.get("target_def") or "").strip()
    why = str(row.get("no_subject") or no_subject or "").strip()
    if not target:
        if not why:
            raise ValueError(f"row {base_id!r} has no target_def — every render must name the defName it "
                             f"is a picture of (ART_SUBJECT_RESOLVER_1); give target_def, or no_subject "
                             f"/ --no-subject \"<why>\" for art that is no creature/plant/thing")
        return {"no_subject": why}
    originals = _split_names(row.get("target_original"))
    texpath = str(row.get("target_texpath") or "").strip() or None
    canon_slug, canon_imgs = None, _split_names(row.get("canon_reference"))
    w = _world() if world is None else world
    if w:
        import subject  # noqa: E402
        ours, orig = w.identify(target, originals)
        target, originals = ours, list(orig)
        if not texpath:
            tps = sorted(w.tex_by_def.get(target, ()))
            texpath = tps[0] if len(tps) == 1 else None
        c = subject.resolve_canon(target, w, originals)
        if c["match"] != "none":
            canon_slug = c["slug"]
            if not canon_imgs:
                canon_imgs = list(c["images"])
        elif target not in w.defs:
            print(f"  ⚠️  {base_id}: target_def {target!r} is not a ThingDef/PawnKindDef in src/ yet — "
                  f"filed anyway (a def may follow its art)", file=sys.stderr)
    if not canon_slug and str(row.get("canon") or "").strip():
        canon_slug = str(row["canon"]).strip()
        if not canon_imgs:
            d = common.CANON_ROOT / canon_slug
            canon_imgs = sorted(str(p) for p in d.iterdir() if p.suffix.lower() in
                                (".png", ".jpg", ".jpeg", ".webp") and not p.name.startswith("donor_")) \
                if d.is_dir() else []
    resolved = []
    for im in canon_imgs:
        ip = Path(im).expanduser()
        if not ip.is_absolute():
            ip = Path.cwd() / ip
        if not ip.is_file():
            raise ValueError(f"row {base_id!r} canon_reference does not exist: {ip}")
        resolved.append(str(ip.resolve()))
    out = {"target_def": target, "target_original": originals}
    if texpath:
        out["target_texpath"] = texpath
    if canon_slug:
        out["target_canon"] = canon_slug
    if resolved:
        out["canon_reference"] = resolved
    return out


class DuplicateJobId(ValueError):
    pass


def _split_facings(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(f).strip() for f in raw if str(f).strip()]
    raw = str(raw).strip()
    if not raw:
        return []
    return [f.strip() for f in raw.replace(";", ",").split(",") if f.strip()]


def load_rows(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            data = data.get("items") or data.get("rows") or []
        return list(data)
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def row_to_jobs(row: dict, default_channel: str = "codex",
                 derive_facings: bool = True, no_subject: str | None = None, world=None) -> list[dict]:
    missing = [f for f in REQUIRED_ROW_FIELDS if not row.get(f)]
    if missing:
        raise ValueError(f"row {row.get('id', '?')!r} missing {missing}")
    binding = bind_subject(row, no_subject=no_subject, world=world)
    # csv.DictReader keys a row's surplus cells under None; sorting str with None would crash the whole file
    unknown = sorted((str(k) for k in row if k not in KNOWN_ROW_FIELDS and row[k] not in (None, "")))
    if unknown:
        print(f"WARNING: row {row.get('id', '?')!r} has unknown field(s) {unknown} — NOT carried onto the job "
              f"(typo, or a field fill_queue does not support)", file=sys.stderr)

    # A per-row "channel" always wins over --channel, if the row bothers to
    # name one; otherwise every row in this invocation gets --channel's
    # value (default "codex").
    channel = str(row.get("channel") or default_channel).strip() or default_channel
    if channel not in ("codex", "gemini"):
        raise ValueError(f"row {row.get('id', '?')!r} has unknown channel "
                          f"{channel!r} — only 'codex' or 'gemini'")

    base_id = str(row["id"]).strip()
    facings = _split_facings(row.get("facings"))
    canvas = {"width": int(row["canvas_w"]), "height": int(row["canvas_h"])}

    # Sizing rule of thumb (ART_PAINTERLY_RESTORATION_1, owner, 2026-09-14):
    # canvas = drawSize×128, rounded up to the next power of two, floor 256 —
    # a starting point, not a refusal. The 2026-09-13 "stored resolution above
    # 128 changes nothing measurable" finding was measured at VANILLA zoom
    # tiers only (96/32/18 px); the owner is not convinced it holds at the
    # enhanced zoom levels in the current mod stack, so sizing errs GENEROUS
    # until re-measured — high resolution is fine "as long as the user will
    # actually see the resolution" (owner's words). This used to be a hard
    # REFUSAL past the ceiling without an 'oversize_reason' (owner-locked
    # 2026-09-13); that lock is reversed. Below 128 still warns (a decor
    # sprite may legitimately be small).
    # The actual arithmetic now lives once, in common.canvas_for_cells —
    # FLORA_LEGIBILITY_BAR_1 spec item 3 (this used to re-derive it inline).
    ds = float(row.get("drawsize") or 1.0)
    ceiling = common.canvas_for_cells(ds)
    if max(canvas["width"], canvas["height"]) > ceiling and not (row.get("oversize_reason") or "").strip():
        print(f"  ⚠️  {base_id}: canvas {canvas['width']}x{canvas['height']} exceeds the "
              f"drawSize×128 rule-of-thumb ceiling {ceiling} for drawsize {ds} — filing anyway "
              f"(ART_PAINTERLY_RESTORATION_1: advisory only, generous until re-measured at "
              f"modded zoom). Add an 'oversize_reason' to record why.",
              file=sys.stderr)
    if max(canvas["width"], canvas["height"]) < 128:
        print(f"  ⚠️  {base_id}: canvas {canvas['width']}x{canvas['height']} is under the 128 floor "
              f"— fine for decor, mud for a creature (64-stored measurably drops at 1:1).",
              file=sys.stderr)

    reference = row.get("reference") or None
    if reference:
        reference = str(reference).strip() or None
    if reference:
        # Stored ABSOLUTE, and verified to exist here at filing time rather
        # than left to fail inside the daemon later — a dangling reference
        # used to reach validate_sprite.py as a plain nonzero exit, which
        # the daemon folded into the same REJECT as a genuinely bad image
        # (fixed separately in artpiped.py's run_validator; this is the
        # OTHER half of that fix: catch it before the job is even filed).
        ref_path = Path(reference).expanduser()
        if not ref_path.is_absolute():
            ref_path = (Path.cwd() / ref_path)
        if not ref_path.is_file():
            raise ValueError(f"row {base_id!r} reference does not exist: {ref_path}")
        reference = str(ref_path.resolve())

    # csv.DictReader gives '' (not a missing key) for a blank cell, and
    # int('') raises — `row.get('priority') or 100` treats a blank cell the
    # same as an absent one instead of crashing the whole file.
    priority = int(row.get("priority") or 100)

    # ARTPIPE_FACING_COHERENCE_1 §2: a multi-facing row with an "east" facing
    # gets east as the fresh-generated MASTER; north/south (if also
    # requested) are filed as DERIVATIONS of it (`derive_from`) rather than
    # independent prompts — the mechanism the owner ruled and
    # `rimworld-sprite-facings/SKILL.md` already documents as owed. A row
    # with no "east" facing (or `--no-derive-facings`) files every facing
    # exactly as before, reference-less and independent.
    # A row that already names its own `reference` (a reskin) never also
    # gets `derive_from` stamped on top of it — common.load_job refuses a
    # job carrying both (they are different contracts; see its docstring).
    master_facing_present = derive_facings and _MASTER_FACING in facings and not reference
    master_job_id = f"{base_id}_{_MASTER_FACING}" if master_facing_present else None
    # Explicit row `derive_from` (a finished sibling job id): every facing of the row is an edit of THAT job's
    # accepted render — "regenerate east to match the accepted north" — overriding the east-master default.
    explicit_derive = str(row.get("derive_from") or "").strip() or None
    if explicit_derive:
        if reference:
            raise ValueError(f"row {base_id!r}: derive_from and reference are different contracts, not both")
        master_facing_present = False

    # ART_VERSION_WRANGLING_1: scrub the retired outline clause, fold in the
    # biome register and the canon-library brief.
    prompt, n_p = common.scrub_stale_outline(str(row["prompt"]))
    style, n_s = common.scrub_stale_outline(str(row.get("style_notes") or ""))
    if n_p or n_s:
        print(f"  ⚠️  {base_id}: removed {n_p + n_s} retired black-outline clause(s) "
              f"(ART_VERSION_WRANGLING_1)", file=sys.stderr)
    if common.has_stale_outline(prompt) or common.has_stale_outline(style):
        raise ValueError(f"row {base_id!r} still asks for an outline/keyline — outlines "
                          f"are retired (owner 2026-10-04, ART_VERSION_WRANGLING_1)")
    register = str(row.get("biome_register") or "").strip()
    if register:
        style = f"Biome register: {register}" + (f" {style}" if style else "")
    elif str(row.get("biome_neutral") or "").strip().lower() not in ("1", "true", "yes"):
        print(f"  ⚠️  {base_id}: no biome_register (and not biome_neutral) — the "
              f"subject will render without its biome's light and palette", file=sys.stderr)
    canon = str(row.get("canon") or "").strip()
    if canon:
        try:
            brief = common.canon_brief(canon)
        except (FileNotFoundError, OSError) as exc:
            raise ValueError(f"row {base_id!r} canon {canon!r}: {exc}")
        style = f"{style} {brief}".strip()
    # The house register rides in the job itself, not only in the daemon's
    # render-time prompt, so it holds whichever clone's daemon renders it.
    if (row.get("background") or "transparent") == "transparent" and \
            "no outlines" not in f"{prompt} {style}".lower():
        style = f"{style} {common.HOUSE_ART_REGISTER}".strip()

    jobs = []
    for facing in (facings or [None]):
        job_id = f"{base_id}_{facing}" if facing else base_id
        job = {
            "id": job_id,
            "rimflow_item_id": row["rimflow_item_id"],
            "reference": reference,
            "canvas": canvas,
            "drawsize": ds,
            "prompt": prompt,
            "style_notes": style,
            "priority": priority,
            "background": row.get("background") or "transparent",
            "channel": channel,
            "facing": facing,
            "facings": facings,
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        job.update(binding)
        if row.get("owner_note") not in (None, ""):
            on = row["owner_note"]
            if not isinstance(on, (str, list)):
                raise ValueError(f"row {base_id!r} owner_note must be a string")
            job["owner_note"] = on
        na = _split_na(row.get("canon_na"))
        if na:
            job["canon_na"] = na
            if str(row.get("canon_na_reason") or "").strip():
                job["canon_na_reason"] = str(row["canon_na_reason"]).strip()
        if row.get("install_to"):
            job["install_to"] = str(row["install_to"]).replace("{facing}", facing or "")
        if explicit_derive:
            job["derive_from"] = explicit_derive
            job["prompt"] = DERIVE_PROMPT_PREFIX + job["prompt"]
        elif master_facing_present and facing in _DERIVED_FACINGS:
            job["derive_from"] = master_job_id
            job["prompt"] = DERIVE_PROMPT_PREFIX + job["prompt"]
        elif job.get("canon_reference") and not reference:
            job["prompt"] = CANON_PROMPT_PREFIX + job["prompt"]
        jobs.append(job)
    return jobs


class InvalidJob(ValueError):
    """Generated job fails common.load_job — refused before filing."""


def write_job(job: dict, pending_dir: Path, active_dir: Path, done_dir: Path,
              failed_dir: Path, dry_run: bool) -> None:
    taken = common.id_taken(job["id"], pending_dir, active_dir, done_dir, failed_dir)
    if taken:
        raise DuplicateJobId(f"{job['id']} already exists at {taken}")

    # Run the daemon's own validation (common.load_job, incl. the facing-
    # contradiction check) BEFORE anything reaches pending/, so a bad prompt
    # is refused at filing instead of as bad_job_file days later.
    import tempfile
    with tempfile.TemporaryDirectory() as _td:
        _tmp = Path(_td) / f"{job['id']}.json"
        _tmp.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n")
        try:
            common.load_job(_tmp)
        except common.JobError as exc:
            raise InvalidJob(f"{job['id']} refused at filing (daemon would reject it): {exc}")

    dest = pending_dir / f"{job['id']}.json"
    if dry_run:
        print(f"would write {dest}")
        return

    # Write to a tmp name FIRST, fully, then os.link() it into place. A
    # direct O_EXCL create-and-write at `dest` itself leaves a PARTIALLY
    # WRITTEN file sitting at the real path if this process is killed
    # mid-write — and that corrupt file then blocks every future refile of
    # this id forever (id_taken() sees it and refuses, common.load_job()
    # can't parse it). os.link fails with FileExistsError if dest already
    # exists — the same exclusivity O_EXCL gave — but only after the
    # content is already complete and closed, so a crash between link and
    # cleanup can only ever leave a fully-valid dest.
    tmp = pending_dir / f".{job['id']}.json.tmp.{os.getpid()}.{time.time_ns()}"
    tmp.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n")
    try:
        os.link(tmp, dest)
    except FileExistsError:
        raise DuplicateJobId(f"{job['id']} already exists at {dest} "
                              f"(created concurrently by another filer)")
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
    print(f"filed {dest}")

    # ART_REGEN_REGISTRY_1: this row is the moment a target enters scope —
    # emit registered+queued through artreg. Best effort: a registry hiccup
    # must never block filing the actual job, which is this function's real
    # job. source = the rimflow item driving this row, same provenance this
    # module already required of every row.
    #
    # Only against the REAL queue (default dirs) — selftest_artpipe.py (and
    # any other caller pointed at a tempfile.TemporaryDirectory()) passes its
    # own pending_dir, which is how this guard tells a live filing from a
    # test fixture apart without either module knowing about the other.
    # Without it, every test run of fill_queue's own selftests would
    # permanently pollute the production registry.jsonl with fixture ids.
    if pending_dir == common.DEFAULT_PENDING:
        try:
            target = artreg.derive_target(job["id"], job.get("facing"))
            artreg.record_registered(target, source=job["rimflow_item_id"], by="fill_queue")
            artreg.record_queued(target, job["id"], notes="", by="fill_queue")
        except Exception as exc:
            print(f"fill_queue: WARNING artreg event emit failed for {job['id']}: {exc}",
                  file=sys.stderr)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", required=True, help="CSV or JSON art list")
    ap.add_argument("--pending-dir", type=Path, default=common.DEFAULT_PENDING)
    ap.add_argument("--active-dir", type=Path, default=common.DEFAULT_ACTIVE)
    ap.add_argument("--done-dir", type=Path, default=common.DEFAULT_DONE)
    ap.add_argument("--failed-dir", type=Path, default=common.DEFAULT_FAILED)
    ap.add_argument("--channel", choices=("codex", "gemini"), default="codex",
                     help="default channel for every row in this file — a row's own "
                          "'channel' column/field, if present, overrides this")
    ap.add_argument("--derive-facings", dest="derive_facings", action="store_true",
                     default=True,
                     help="(default) north/south facings derive from the accepted "
                          "east master (ARTPIPE_FACING_COHERENCE_1 §2) instead of "
                          "being prompted independently")
    ap.add_argument("--no-derive-facings", dest="derive_facings", action="store_false",
                     help="file every facing independently, reference-less — today's "
                          "pre-§2 behavior")
    ap.add_argument("--dry-run", action="store_true",
                     help="print what would be filed, write nothing")
    ap.add_argument("--no-subject", metavar="WHY", default=None,
                     help="file rows without target_def, recording WHY on each job "
                          "(templates, glyphs, fixtures) — ART_SUBJECT_RESOLVER_1")
    args = ap.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        print(f"ERROR no such input: {path}", file=sys.stderr)
        return 2

    if not args.dry_run:
        # fill_queue only ever writes pending/ — active/done/failed/ are read
        # here purely for the duplicate-id check, so only pending/ needs to
        # exist before we can write to it.
        for d in (args.pending_dir, args.active_dir, args.done_dir, args.failed_dir):
            d.mkdir(parents=True, exist_ok=True)

    rows = load_rows(path)
    filed, duplicates, errors = 0, [], []
    for row in rows:
        try:
            jobs = row_to_jobs(row, default_channel=args.channel,
                                derive_facings=args.derive_facings,
                                no_subject=args.no_subject)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for job in jobs:
            try:
                write_job(job, args.pending_dir, args.active_dir, args.done_dir,
                          args.failed_dir, args.dry_run)
                filed += 1
            except DuplicateJobId as exc:
                duplicates.append(str(exc))
            except InvalidJob as exc:
                errors.append(str(exc))

    for msg in errors:
        print(f"ERROR skipped row: {msg}", file=sys.stderr)
    for msg in duplicates:
        print(f"REFUSED duplicate: {msg}", file=sys.stderr)

    print(f"\n{filed} job(s) filed, {len(duplicates)} duplicate(s) refused, "
          f"{len(errors)} row error(s)")
    return 1 if (duplicates or errors) else 0


if __name__ == "__main__":
    sys.exit(main())
