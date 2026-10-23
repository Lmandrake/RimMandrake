#!/usr/bin/env python3
"""Race art-eval prompt VARIANTS against owner-ruled rows (skill `rimworld-art-evaluation`,
references/prompt_variants_2026-10-23.md).

Owner, 2026-10-23: *"Periodically evaluate your own art evaluation prompts to question if there are alternative
prompts to consider or even compare different ones in parallel to see which work well."*

A variant is an OVERLAY directory holding only the changed `references/` files (prompts/*.md, templates/*.md), each
with its own `<!-- version -->` / `"version"` tag; race.py lays it over a copy of the live references/ and the runner
reads that copy through ART_EVAL_REFS. `incumbent`
names the live references/ directory.

    python3 race.py run   --race <tag> --rows <rows.jsonl>... --variant incumbent --variant <name>=<dir> \
                          [--family opus|gpt] [--shards 3] [--budget 540]
    python3 race.py score --race <tag> --rows <rows.jsonl>...         # the comparison table (markdown)

`run` is resumable: each (variant, family, shard) is one runner run id `race_<tag>_<variant>_<family>_s<k>`; a
re-run skips decided subjects, and shards still busy at --budget seconds are killed (their in-flight subject is
redone next call). Rows are regression rows: {"pilot": "DEF:LETTER[:LIVING]"} or {"spec": "<repo path>"}, plus
"expect": ACCEPT|NOT_ACCEPT. A race judges each picture on its own: a catch's `depends_on` is dropped (the living
animal's verdict is code, not prompt), and the regen prompt-edit call is skipped (a deterministic stand-in).

`--family gpt` runs the first pass on GPT (gpt_consult.py, images attached) with the same prompt files, so the same
variant can be compared across model families. Everything is a --test run: no rounds, no delegated verdicts, no jobs.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cards as C  # noqa: E402
import policy as P  # noqa: E402

ROOT = P.ROOT
STATE = ROOT / "infrastructure/state/art_eval"
NOT_ACCEPT = {"REGEN", "ESCALATE", "REGEN_AFTER_SOURCE"}


def load_rows(paths: list) -> list:
    rows = []
    for p in paths:
        for line in Path(p).read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def spec_of(row: dict) -> dict:
    s = C.pilot_spec(row["pilot"]) if row.get("pilot") else json.loads((ROOT / row["spec"]).read_text())
    s.pop("depends_on", None)
    s["owner_kept"] = False                 # a race judges the picture, never the kept-art routing
    return s


def key_of(row: dict) -> str:
    return row.get("pilot") or Path(row["spec"]).stem


def run_id(race: str, variant: str, family: str, k: int) -> str:
    return f"race_{race}_{variant}_{family}_s{k}"


# ------------------------------------------------------------------ shard worker (a subprocess)
def worker(race: str, variant: str, family: str, k: int, shards: int, rows_paths: list):
    import runner as R
    rows = load_rows(rows_paths)
    mine = [r for i, r in enumerate(rows) if i % shards == k]
    specs = []
    for r in mine:
        s = spec_of(r)
        s["subject"] = s["subject"] + ("__" + s["candidate"] if s.get("candidate") else "")   # one row per picture
        specs.append(s)

    class RaceReviewers(R.Reviewers):
        def regen(self, prompt, work):
            return "", {"skipped": "race: regen prompt edit not called"}

        if family == "gpt":
            def opus(self, prompt, card_dir):
                imgs = [card_dir / f for f in R.image_list(json.loads((card_dir / "card.json").read_text()))][:8]
                p = ("NOTE: you have no file tools. The images listed under \"Images\" are ATTACHED to this message "
                     "in that order (at most 8); wherever the task says Read them, look at the attachments.\n\n" + prompt)
                work = card_dir / "gpt_first"; work.mkdir(exist_ok=True)
                text, meta = R.call_gpt(p, imgs, work)
                meta["models_reported"] = [meta.get("model_reported")]
                return text, meta

    R.run(specs, run_id(race, variant, family, k), rev=RaceReviewers(), test=True)


# ------------------------------------------------------------------ run
def merged_refs(race: str, name: str, overlay: Path) -> Path:
    """The live references/ with the variant's OVERLAY files (only the changed ones) copied over it, under the
    agent storage root. Each overlay file must carry a version tag that differs from the live file's."""
    import shutil
    import runner as R
    if not overlay.is_dir():
        raise SystemExit(f"variant {name}: no overlay dir {overlay}")
    dst = R.storage_root() / "race_variants" / race / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(P.SKILL / "references", dst)
    n = 0
    for f in overlay.rglob("*.md"):
        rel = f.relative_to(overlay)
        live = P.SKILL / "references" / rel
        if live.is_file() and P.prompt_version(live)["tag"] == P.prompt_version(f)["tag"]:
            raise SystemExit(f"variant {name}: {rel} keeps the live version tag — give it its own")
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst / rel); n += 1
    if not n:
        raise SystemExit(f"variant {name}: overlay {overlay} holds no .md file")
    return dst


def cmd_run(a):
    variants = []
    for v in a.variant:
        name, _, d = v.partition("=")
        if name != "incumbent" and not d:
            raise SystemExit(f"variant {v!r}: give name=<references dir>")
        variants.append((name, merged_refs(a.race, name, Path(d)) if d else ""))
    procs = []
    for name, d in variants:
        env = dict(os.environ)
        env.pop("ART_EVAL_REFS", None)
        if d:
            env["ART_EVAL_REFS"] = str(Path(d).resolve())
        for k in range(a.shards):
            cmd = [sys.executable, __file__, "_worker", a.race, name, a.family, str(k), str(a.shards)] + a.rows
            procs.append((f"{name}/{a.family}/s{k}", subprocess.Popen(cmd, env=env, cwd=str(HERE), start_new_session=True)))
    t0 = time.time()
    while time.time() - t0 < a.budget and any(p.poll() is None for _, p in procs):
        time.sleep(5)
    killed = []
    for tag, p in procs:
        if p.poll() is None:
            os.killpg(p.pid, signal.SIGTERM)
            killed.append(tag)
    print(f"race {a.race}: {len(procs) - len(killed)}/{len(procs)} shards finished in {round(time.time() - t0)}s"
          + (f"; killed at budget (resume by re-running): {killed}" if killed else ""))


# ------------------------------------------------------------------ score
def decisions(races: str) -> dict:
    """{(variant, family): {row key: record}} across every shard of the race(s). `races` may be comma-separated:
    a later race's record for the same row replaces an earlier one (a re-run after a card fix)."""
    out = {}
    for race in races.split(","):
        for (vf, recs) in _decisions_one(race).items():
            out.setdefault(vf, {}).update(recs)
    return out


def _decisions_one(race: str) -> dict:
    out = {}
    for f in sorted((STATE / "runs").glob(f"race_{race}_*/decisions.jsonl")):
        variant, family = f.parent.name[len(f"race_{race}_"):].rsplit("_s", 1)[0].rsplit("_", 1)
        for line in f.read_text().splitlines():
            r = json.loads(line)
            out.setdefault((variant, family), {})[r["subject"].replace("__", ":", 1)] = r
    return out


def cost(rec: dict) -> tuple[float, float, int]:
    """(Opus/Claude USD as reported by the CLI, model seconds, GPT calls). GPT runs on a subscription: no USD."""
    usd = secs = 0.0
    for metas in (rec.get("models") or {}).values():
        for m in (metas if isinstance(metas, list) else [metas]):
            if m:
                usd += float(m.get("cost_usd") or 0)
                secs += float(m.get("seconds") or 0)
    gpt = len((rec.get("models") or {}).get("gpt") or [])
    return usd, secs, gpt


def score(race: str, rows: list) -> tuple[str, dict]:
    dec = decisions(race)
    # a row's key is DEF:LETTER (pilot) or the spec's subject:candidate
    keyed = []
    for r in rows:
        s = spec_of(r)
        keyed.append((f"{s['subject']}:{s.get('candidate')}" if s.get("candidate") else s["subject"], r, s["template"]))
    table, stats = [], {}
    head = ("| variant | family | n judged | agree | **false accepts** | false rejects | holds/errors | missing | "
            "Opus $ | model s |")
    table += [head, "|" + "---|" * 10]
    for (variant, family), recs in sorted(dec.items()):
        st = {"n": 0, "agree": 0, "fa": [], "fr": [], "hold": [], "missing": [], "usd": 0.0, "secs": 0.0,
              "by_template": {}}
        for key, r, tpl in keyed:
            rec = recs.get(key)
            bt = st["by_template"].setdefault(tpl, {"n": 0, "agree": 0, "fa": 0, "fr": 0})
            if rec is None:
                st["missing"].append(key); continue
            u, s_, _ = cost(rec)
            st["usd"] += u; st["secs"] += s_
            d = rec["decision"]
            if d not in NOT_ACCEPT and d != "ACCEPT":
                st["hold"].append(f"{key}={d}"); continue
            st["n"] += 1; bt["n"] += 1
            got_accept = d == "ACCEPT"
            want_accept = r["expect"] == "ACCEPT"
            if got_accept == want_accept:
                st["agree"] += 1; bt["agree"] += 1
            elif got_accept:
                st["fa"].append(key); bt["fa"] += 1
            else:
                st["fr"].append(key); bt["fr"] += 1
        stats[f"{variant}/{family}"] = st
        table.append(f"| {variant} | {family} | {st['n']} | {st['agree']} | **{len(st['fa'])}** | {len(st['fr'])} | "
                     f"{len(st['hold'])} | {len(st['missing'])} | {st['usd']:.2f} | {round(st['secs'])} |")
    table += ["", "| variant/family | template | n | agree | false accepts | false rejects |", "|---|---|---|---|---|---|"]
    for vf, st in stats.items():
        for tpl, bt in sorted(st["by_template"].items()):
            table.append(f"| {vf} | {tpl} | {bt['n']} | {bt['agree']} | {bt['fa']} | {bt['fr']} |")
    table += ["", "Errors per variant/family:"]
    for vf, st in stats.items():
        table.append(f"- **{vf}** — false accepts {st['fa'] or 'none'}; false rejects {st['fr'] or 'none'}"
                     + (f"; holds {st['hold']}" if st["hold"] else "") + (f"; missing {st['missing']}" if st["missing"] else ""))
    return "\n".join(table) + "\n", stats


def cmd_score(a):
    rows = load_rows(a.rows)
    md, stats = score(a.race, rows)
    print(md)
    if a.out:
        Path(a.out).write_text(json.dumps(stats, indent=1))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "_worker":
        race, variant, family, k, shards, *rows = argv[1:]
        worker(race, variant, family, int(k), int(shards), rows)
        return 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--race", required=True)
    r.add_argument("--rows", nargs="+", required=True)
    r.add_argument("--variant", action="append", required=True, help="incumbent | name=<overlay dir of changed references/ files>")
    r.add_argument("--family", choices=("opus", "gpt"), default="opus")
    r.add_argument("--shards", type=int, default=3)
    r.add_argument("--budget", type=int, default=540, help="seconds before busy shards are killed (resumable)")
    s = sub.add_parser("score")
    s.add_argument("--race", required=True, help="race tag, or tags comma-separated (later ones override)")
    s.add_argument("--rows", nargs="+", required=True)
    s.add_argument("--out")
    a = ap.parse_args(argv)
    return cmd_run(a) if a.cmd == "run" else cmd_score(a)


if __name__ == "__main__":
    sys.exit(main())
