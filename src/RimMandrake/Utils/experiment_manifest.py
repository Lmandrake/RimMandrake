#!/usr/bin/env python3
r"""experiment_manifest.py -- freeze the inputs of a measurement run, and refuse to call it complete if any moved.

    python3 src/RimMandrake/Utils/experiment_manifest.py record  TPS_OVERHEAD --cell C0 --save "Saves\bland.rws" --fixture bland_world
    python3 src/RimMandrake/Utils/experiment_manifest.py verify  TPS_OVERHEAD --cell C0      # at the END of the cell
    python3 src/RimMandrake/Utils/experiment_manifest.py record  TPS_OVERHEAD --cell C1 ...  # next cell (after restart)
    python3 src/RimMandrake/Utils/experiment_manifest.py complete TPS_OVERHEAD               # refuses unless all hold
    python3 src/RimMandrake/Utils/experiment_manifest.py show    TPS_OVERHEAD

WHY (GPT review rank 1, Transient/foundry_bridge_system_review_gpt_20261010.md sections 5.3 and 7; prediction 1 of
bridge_debugging_system.md section 5.2, score 144): the C0-C5 overhead experiment compares cells that must differ in
ONE declared thing -- the collector toggles. A companion redeployed mid-protocol, a Steam update to RimBridgeServer,
a mod list re-sorted, a settings file touched, or the save overwritten makes the comparison meaningless, and nothing
on the screen says so. This records every frozen input when a cell STARTS, re-reads them when it ENDS, and makes
`complete` refuse unless:
  1. every required cell (default C0..C5) was recorded AND verified unchanged at its end;
  2. every cell's inputs equal C0's, except the keys that cell declares as its variable (default: `collectors`);
  3. the newest preflight report (preflight.py) has no FAIL, and was written after... nothing: it must exist;
  4. no required safety item is still open in the ledger (default TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS, the
     recorder Harmony-safety FAIL GPT section 2.3 says blocks the affected hooks; --safety-item adds more,
     --no-safety-item removes the default only with --reason, which is recorded).

FROZEN INPUTS (key: what)
  companion   deployed JawaBench.BridgeTools.dll sha + its build id, and the repo artifact sha
  modlist     the live ModsConfig.xml activeMods: count, ordered digest
  mod_dlls    sha of every DLL under the game's local Mods folder (our deployed assemblies)
  deps        RimBridgeServer assemblies + version, Harmony, Assembly-CSharp (preflight.dependency_fingerprint)
  settings    sha of every Config\Mod_*.xml (mod settings) and Prefs.xml
  saves       sha + size of each --save given (relative to the RimWorld user folder, or absolute)
  fixture     the --fixture string (and its file sha when it names a file)
  collectors  JawaBench\tps\tps_settings.json + awareness_settings.json contents, and the Windows scheduled tasks
              whose name contains "Observer" (state), i.e. the TPS observer / health observer
  client      repo HEAD and whether the tree is dirty

Records live in infrastructure/state/experiments/<EXP>.json (anyone-later: commit it with the results).
Exit codes: 0 ok, 1 refused / changed, 3 usage.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
STORE = os.path.join(REPO, 'infrastructure', 'state', 'experiments')
DEFAULT_CELLS = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5']
DEFAULT_SAFETY = ['TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS']
KEYS = ('companion', 'modlist', 'mod_dlls', 'deps', 'settings', 'saves', 'fixture', 'collectors', 'client')


def _sha(path, n=16):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:n]


def _digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def capture(saves=(), fixture=None):
    """Every frozen input, as plain data. Each sub-capture that cannot be read records {'unreadable': why}, which can
    never equal a readable value, so ignorance is never mistaken for 'unchanged'."""
    import game_paths as gp
    import preflight as pf
    out = {}

    def guard(key, fn):
        try:
            out[key] = fn()
        except Exception as e:                                  # noqa: BLE001
            out[key] = {'unreadable': '%s: %s' % (type(e).__name__, str(e)[:160])}

    def companion():
        return {'game_sha': _sha(pf.COMPANION_GAME), 'game_build': pf.informational_build(pf.COMPANION_GAME),
                'repo_sha': _sha(pf.COMPANION_REPO) if os.path.isfile(pf.COMPANION_REPO) else None}

    def modlist():
        ids = pf.active_ids(gp.MODS_CONFIG)
        return {'count': len(ids), 'ordered_digest': _digest(ids)}

    def mod_dlls():
        fs = sorted(glob.glob(os.path.join(gp.LOCAL_MODS, '*', '**', '*.dll'), recursive=True))
        return {'count': len(fs), 'digest': _digest([[os.path.relpath(f, gp.LOCAL_MODS), _sha(f)] for f in fs])}

    def settings():
        cfg = os.path.join(gp.LOCALLOW, 'Config')
        fs = sorted(glob.glob(os.path.join(cfg, 'Mod_*.xml'))) + [os.path.join(cfg, 'Prefs.xml')]
        return {os.path.basename(f): _sha(f) for f in fs if os.path.isfile(f)}

    def saves_():
        res = {}
        for s in saves:
            p = s if os.path.isabs(s) else os.path.join(gp.LOCALLOW, s.replace('\\', os.sep))
            res[s] = {'sha': _sha(p), 'size': os.path.getsize(p)} if os.path.isfile(p) else {'unreadable': 'missing'}
        return res

    def fixture_():
        if not fixture:
            return None
        p = fixture if os.path.isabs(fixture) else os.path.join(REPO, fixture)
        return {'name': fixture, 'sha': _sha(p) if os.path.isfile(p) else None}

    def collectors():
        d = os.path.join(gp.LOCALLOW, 'JawaBench', 'tps')
        res = {}
        for f in ('tps_settings.json', 'awareness_settings.json'):
            p = os.path.join(d, f)
            res[f] = json.load(open(p, encoding='utf-8-sig')) if os.path.isfile(p) else 'absent (defaults)'
        res['tasks'] = observer_tasks()
        return res

    def client():
        head = subprocess.run(['git', '-C', REPO, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(['git', '-C', REPO, 'status', '--porcelain', '--untracked-files=no', '--', 'src'],
                               capture_output=True, text=True).stdout.strip()
        return {'head': head[:12], 'src_dirty': bool(dirty)}

    guard('companion', companion)
    guard('modlist', modlist)
    guard('mod_dlls', mod_dlls)
    guard('deps', pf.dependency_fingerprint)
    guard('settings', settings)
    guard('saves', saves_)
    guard('fixture', fixture_)
    guard('collectors', collectors)
    guard('client', client)
    return out


def observer_tasks():
    try:
        o = subprocess.run(['schtasks.exe', '/Query', '/FO', 'CSV', '/NH'], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return {'unreadable': str(e)[:100]}
    res = {}
    for ln in o.stdout.replace('\r', '').splitlines():
        cols = [c.strip('"') for c in ln.split('","')]
        if cols and 'observer' in cols[0].lower():
            res[cols[0].strip('"')] = cols[-1].strip('"') if len(cols) > 2 else '?'
    return res


def diff(a, b, ignore=()):
    """Keys whose values differ (ignoring `ignore`)."""
    return sorted(k for k in set(a) | set(b) if k not in ignore and a.get(k) != b.get(k))


def path_of(exp):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', exp):
        raise SystemExit('bad experiment name %r' % exp)
    return os.path.join(STORE, exp + '.json')


def load(exp):
    p = path_of(exp)
    return json.load(open(p)) if os.path.exists(p) else {'experiment': exp, 'cells': {}, 'events': []}


def save(exp, data):
    os.makedirs(STORE, exist_ok=True)
    tmp = path_of(exp) + '.tmp'
    json.dump(data, open(tmp, 'w'), indent=1, sort_keys=True)
    os.replace(tmp, path_of(exp))


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def cmd_record(a, cap=capture):
    data = load(a.experiment)
    if a.cell in data['cells'] and not a.rerecord:
        print('REFUSED: cell %s already recorded at %s (a re-run is a new cell; --rerecord discards the old record)'
              % (a.cell, data['cells'][a.cell]['recorded']))
        return 1
    inputs = cap(saves=a.save or [], fixture=a.fixture)
    unread = [k for k, v in inputs.items() if isinstance(v, dict) and 'unreadable' in v]
    variable = a.variable or (['collectors'] if a.cell != 'C0' else [])
    data['cells'][a.cell] = {'recorded': now(), 'inputs': inputs, 'variable': variable, 'verified': None,
                             'note': a.note or ''}
    data['events'].append({'at': now(), 'event': 'record', 'cell': a.cell})
    if 'C0' in data['cells'] and a.cell != 'C0':
        moved = diff(data['cells']['C0']['inputs'], inputs, ignore=variable)
        if moved:
            data['cells'][a.cell]['start_mismatch'] = moved
            save(a.experiment, data)
            print('RECORDED %s, but it ALREADY differs from C0 in %s (declared variable %s): this cell cannot count'
                  % (a.cell, moved, variable))
            return 1
    save(a.experiment, data)
    print('RECORDED %s/%s: %s%s' % (a.experiment, a.cell, ', '.join('%s=%s' % (k, _digest(inputs[k])[:8]) for k in KEYS),
                                     ('  UNREADABLE: %s' % unread) if unread else ''))
    return 1 if unread else 0


def cmd_verify(a, cap=capture):
    data = load(a.experiment)
    cell = data['cells'].get(a.cell)
    if not cell:
        print('REFUSED: no record for cell %s' % a.cell)
        return 1
    saves = list((cell['inputs'].get('saves') or {}).keys()) if isinstance(cell['inputs'].get('saves'), dict) else []
    fx = (cell['inputs'].get('fixture') or {}).get('name') if isinstance(cell['inputs'].get('fixture'), dict) else None
    cur = cap(saves=saves, fixture=fx)
    moved = diff(cell['inputs'], cur, ignore=a.mutable or ())
    cell['verified'] = {'at': now(), 'ok': not moved, 'moved': moved}
    data['events'].append({'at': now(), 'event': 'verify', 'cell': a.cell, 'ok': not moved, 'moved': moved})
    save(a.experiment, data)
    if moved:
        print('CHANGED during %s: %s -- the cell is void; re-run it from a restart' % (a.cell, moved))
        for k in moved:
            print('  %s: %s -> %s' % (k, json.dumps(cell['inputs'].get(k), sort_keys=True)[:200],
                                      json.dumps(cur.get(k), sort_keys=True)[:200]))
        return 1
    print('VERIFIED %s/%s: every frozen input unchanged since %s' % (a.experiment, a.cell, cell['recorded']))
    return 0


def item_state(item):
    """Ledger state of an item, or None when unknown."""
    try:
        o = subprocess.run(['python3', os.path.join(REPO, 'src', 'RimMandrake', 'rimflow', 'cli.py'), 'show', item],
                           capture_output=True, text=True, timeout=60, cwd=REPO)
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r'^\S+\s+(\w+)', o.stdout.strip()) if o.returncode == 0 else None
    return m.group(1) if m else None


def cmd_complete(a, state_of=item_state, last_report=None):
    import preflight as pf
    data = load(a.experiment)
    cells = a.cells.split(',') if a.cells else DEFAULT_CELLS
    why = []
    c0 = data['cells'].get(cells[0])
    for c in cells:
        cell = data['cells'].get(c)
        if not cell:
            why.append('%s never recorded' % c)
            continue
        if not cell.get('verified') or not cell['verified'].get('ok'):
            why.append('%s not verified unchanged at its end (%s)' % (c, (cell.get('verified') or {}).get('moved', 'no verify')))
        if c0 and c != cells[0]:
            moved = diff(c0['inputs'], cell['inputs'], ignore=cell.get('variable') or [])
            if moved:
                why.append('%s differs from %s outside its declared variable %s: %s' % (c, cells[0], cell.get('variable'), moved))
        unread = [k for k, v in cell['inputs'].items() if isinstance(v, dict) and 'unreadable' in v]
        if unread:
            why.append('%s has unreadable inputs %s (unknown is never unchanged)' % (c, unread))
    rep_p = last_report or pf.LAST_REPORT
    try:
        rep = json.load(open(rep_p))
        fails = [r['id'] + ' ' + r['name'] for r in rep['rows'] if r['status'] == 'FAIL']
        if fails:
            why.append('latest preflight (%s, %s) has FAIL: %s' % (rep['when'], rep['mode'], fails))
    except (OSError, ValueError, KeyError):
        why.append('no preflight report at %s (run preflight.py)' % rep_p)
    safety = [s for s in DEFAULT_SAFETY if not (a.no_safety_item and s in a.no_safety_item)] + (a.safety_item or [])
    if a.no_safety_item and not a.reason:
        print('REFUSED: --no-safety-item needs --reason (it is recorded)')
        return 3
    for s in safety:
        st = state_of(s)
        if st is None:
            why.append('safety item %s: state unknown (not in the ledger?) -- unknown is not done' % s)
        elif st not in ('done', 'closed', 'validated'):
            why.append('required safety FAIL still open: %s is %s' % (s, st))
    data['events'].append({'at': now(), 'event': 'complete', 'ok': not why, 'why': why,
                           'waived': a.no_safety_item or [], 'reason': a.reason or ''})
    save(a.experiment, data)
    if why:
        print('REFUSED: %s cannot be marked complete:' % a.experiment)
        for w in why:
            print('  - ' + w)
        return 1
    data['complete'] = now()
    save(a.experiment, data)
    print('COMPLETE %s: %d cells frozen, verified, comparable; preflight clean; safety items done' % (
        a.experiment, len(cells)))
    return 0


def cmd_show(a):
    data = load(a.experiment)
    for c, cell in sorted(data['cells'].items()):
        v = cell.get('verified') or {}
        print('%-4s recorded %s  variable=%s  verified=%s %s' % (c, cell['recorded'], cell.get('variable'),
                                                               v.get('ok'), v.get('moved') or ''))
    print('complete: %s' % data.get('complete'))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('record')
    r.add_argument('experiment')
    r.add_argument('--cell', required=True)
    r.add_argument('--variable', action='append', choices=KEYS, help='input key this cell may change vs C0 '
                   '(default collectors for every cell but C0)')
    r.add_argument('--save', action='append', help='save file to freeze (relative to the RimWorld user folder)')
    r.add_argument('--fixture')
    r.add_argument('--note')
    r.add_argument('--rerecord', action='store_true')
    v = sub.add_parser('verify')
    v.add_argument('experiment')
    v.add_argument('--cell', required=True)
    v.add_argument('--mutable', action='append', choices=KEYS, help='a key allowed to move DURING the cell (rare)')
    c = sub.add_parser('complete')
    c.add_argument('experiment')
    c.add_argument('--cells', help='comma list, first is the reference (default C0..C5)')
    c.add_argument('--safety-item', action='append')
    c.add_argument('--no-safety-item', action='append')
    c.add_argument('--reason')
    s = sub.add_parser('show')
    s.add_argument('experiment')
    a = ap.parse_args(argv)
    return {'record': cmd_record, 'verify': cmd_verify, 'complete': cmd_complete, 'show': cmd_show}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
