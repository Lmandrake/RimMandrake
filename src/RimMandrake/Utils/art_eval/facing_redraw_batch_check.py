#!/usr/bin/env python3
"""Proof for FACING_AUDIT_BUILD_REDRAW_BATCH: is every FAIL set of the 2026-10-26 facing audit resolved?

  facing_redraw_batch_check.py [--batch DIR] [--repo ROOT] [--list]

A row (auditrows/manifest.json, entries carrying a `group`) is RESOLVED when the batch state
(DIR/batch/state.json) marks its subject
  ACCEPT   and every judged facing file is byte-identical (sha256) to the one texture under
           ROOT/src/**/Textures/<target_texpath>_<facing>.png, or that file is a later recorded art
           install over it (the art ledger's `live` events chain the current sha back, via `prev`, to the
           accepted one: a later rescale/reseat pass is a descendant, not a loss); a whole set whose
           west was live is also checked against the mirror of the accepted east (pixels, or the same
           ledger chain from the west installed with it), or
  ESCALATE with an `escalated_to` item id (round cap reached; the set left this batch for that item).
  RETIRED  its def (`def` in the manifest) is no longer a <defName> anywhere under ROOT/src AND no
           <texPath> under ROOT/src ends in the row's texture name (pruned; a def renamed or moved to
           another mod keeps the texture name, so it stays a row, checked at the file it now uses).
Anything else is OPEN. Exit 0 only when no row is OPEN or BROKEN; exit 1 otherwise; 2 on a bad input.
Manifest entries with `skip` are other items' sets and are reported, never counted.
"""
import argparse
import glob
import hashlib
import json
import re
import sys
from pathlib import Path

TAG = re.compile(r'_(?:s\d+)?r(\d+)(_(?:ns|n|s))?$')
DEFAULT_BATCH = '/mnt/d/ClaudeWork/rimmandrake/facing_backlog_20261026'


def subj_of(rid):
    s = rid[len('arteval_'):]
    m = TAG.search(s)
    return s[:m.start()] + (m.group(2) or '') if m else s


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tex(repo, texpath, facing):
    return glob.glob(str(repo / 'src' / '**' / 'Textures' / f'{texpath}_{facing}.png'), recursive=True)


def mirror_equal(east_png, west_png):
    from PIL import Image, ImageChops
    a = Image.open(east_png).convert('RGBA').transpose(Image.FLIP_LEFT_RIGHT)
    b = Image.open(west_png).convert('RGBA')
    return a.size == b.size and ImageChops.difference(a, b).getbbox() is None


def live_chains(repo):
    """{repo-relative texture path: {sha: prev}} from the art ledger's `live` events."""
    sys.path.insert(0, str(repo / 'src/RimMandrake/Utils/art'))
    import artledger
    ch = {}
    for ev in artledger.read_events():
        if ev.get('type') == 'live' and ev.get('mod') and ev.get('rel') and ev.get('sha'):
            ch.setdefault(f"{ev['mod']}/Textures/{ev['rel']}", {}).setdefault(ev['sha'], ev.get('prev'))
    return ch


def descends(chains, repo, path, cur, want):
    """True when the ledger chains `cur` back to `want`: first at this exact path, then across every
    recorded path with the same file name (a texture moved between mods keeps its name)."""
    rel = str(Path(path).resolve().relative_to(repo.resolve()))
    name = Path(rel).name
    for m in (chains.get(rel, {}), {k: v for p, c in chains.items() if Path(p).name == name for k, v in c.items()}):
        seen, c = set(), cur
        while c and c not in seen:
            if c == want:
                return True
            seen.add(c)
            c = m.get(c)
    return False


def find_tex(repo, texpath, facing, mod):
    """The one texture file for this slot: the row's path; else (moved) the same file name anywhere
    under src; among several, the one in the mod the batch installed into."""
    hits = tex(repo, texpath, facing) or glob.glob(
        str(repo / 'src' / '**' / 'Textures' / '**' / f'{Path(texpath).name}_{facing}.png'), recursive=True)
    if len(hits) > 1 and mod:
        hits = [h for h in hits if f'/{mod}/Textures/' in h] or hits
    return hits


def check_row(repo, v, west_live, chains, mod=None):
    """Return (status, detail)."""
    done = v.get('done')
    if done in ('ESCALATE', 'ESCALATED'):   # drv.py regen writes ESCALATED at the cap
        return ('ESCALATE', v.get('escalated_to', '')) if v.get('escalated_to') else ('BROKEN', 'ESCALATE without escalated_to')
    if done != 'ACCEPT':
        return 'OPEN', f"r{v.get('round')} {v['row']['id']}"
    texpath = v['row']['target_texpath']
    judged = v.get('judged') or {}
    want = set(v['row']['facings'])
    if not want <= set(judged):
        return 'BROKEN', f'judged lacks {sorted(want - set(judged))}'
    for f in sorted(want):
        hits = find_tex(repo, texpath, f, mod)
        if len(hits) != 1:
            return 'BROKEN', f'{f}: {len(hits)} texture files for {texpath}'
        cur, want = sha(hits[0]), sha(judged[f])
        if cur != want and not descends(chains, repo, hits[0], cur, want):
            return 'BROKEN', f'{f}: installed {hits[0]} differs from accepted {judged[f]}'
    if v.get('kind') == 'whole' and west_live:
        hits = find_tex(repo, texpath, 'west', mod)
        wm = Path(judged['east']).parent / 'west_mirrored.png'
        if len(hits) != 1 or not (mirror_equal(judged['east'], hits[0]) or
                                  (wm.is_file() and descends(chains, repo, hits[0], sha(hits[0]), sha(wm)))):
            return 'BROKEN', 'west is not the mirror of the accepted east'
    return 'ACCEPT', v.get('installed', '')


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', default=DEFAULT_BATCH)
    ap.add_argument('--repo', default=str(Path(__file__).resolve().parents[4]))
    ap.add_argument('--list', action='store_true', help='print every row, not only the unresolved ones')
    a = ap.parse_args(argv)
    b, repo = Path(a.batch), Path(a.repo)
    try:
        man = json.loads((b / 'auditrows/manifest.json').read_text())
        state = json.loads((b / 'batch/state.json').read_text())
        revert = json.loads((b / 'batch/revert/manifest.json').read_text())
    except (OSError, ValueError) as e:
        print(f'UNMEASURED: cannot read the batch: {e}')
        return 2
    rows = [m for m in man if m.get('group') and m.get('id')]
    skips = [m for m in man if m.get('skip')]
    if not rows:
        print('UNMEASURED: manifest holds no rows')
        return 2
    west_live = {m['subject'] for m in revert if m.get('facing') == 'west' and m.get('live')}
    inst_mod = {m['subject']: m['mod'].rsplit('/', 1)[-1] for m in revert if m.get('mod')}
    chains = live_chains(repo)
    defnames, texnames = set(), set()
    for x in glob.glob(str(repo / 'src' / '**' / '*.xml'), recursive=True):
        t = Path(x).read_text(errors='replace')
        defnames.update(re.findall(r'<defName>\s*([^<\s]+)\s*</defName>', t))
        texnames.update(p.rsplit('/', 1)[-1] for p in re.findall(r'<texPath>\s*([^<\s]+)\s*</texPath>', t))
    if len(defnames) < 1000:
        print(f'UNMEASURED: only {len(defnames)} defNames under {repo}/src')
        return 2
    counts, bad = {}, []
    for m in rows:
        k = subj_of(m['id'])
        v = state.get(k)
        texname = (v or {}).get('row', {}).get('target_texpath', '').rsplit('/', 1)[-1]
        if v is None:
            rp = b / 'auditrows' / f"{m['group']}.json"
            r0 = next((r for r in json.loads(rp.read_text()) if r.get('id') == m['id']), {}) if rp.is_file() else {}
            texname = r0.get('target_texpath', '').rsplit('/', 1)[-1]
        if m['def'] not in defnames and texname not in texnames:
            st, det = 'RETIRED', f"{m['def']} is no defName under src"
        else:
            st, det = ('OPEN', 'not started') if v is None else check_row(repo, v, k in west_live, chains, inst_mod.get(k))
        counts[st] = counts.get(st, 0) + 1
        if st in ('OPEN', 'BROKEN') or a.list:
            bad.append(f'{st:8} {m["cls"]} {m["group"]:22} {k}  {det}')
    for line in bad:
        print(line)
    print(f'rows {len(rows)} (+{len(skips)} skipped, other items): ' +
          ' '.join(f'{k}={counts[k]}' for k in sorted(counts)))
    ok = not counts.get('OPEN') and not counts.get('BROKEN')
    print('RESOLVED' if ok else 'NOT RESOLVED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
