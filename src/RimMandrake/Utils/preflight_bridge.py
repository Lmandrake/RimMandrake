#!/usr/bin/env python3
r"""preflight_bridge.py -- the ordered, fail-fast pre-flight before a cold load (offline) and for the first five live minutes.

    python3 src/RimMandrake/Utils/preflight_bridge.py --tier full            # offline, before launch: GREEN / NO-GO
    python3 src/RimMandrake/Utils/preflight_bridge.py --tier minimal --purpose menu
    python3 src/RimMandrake/Utils/preflight_bridge.py --tier full --live     # after launch, read-only, files + OS only
    ... [--modset <modset_builder tier>] [--deep] [--all] [--json out.json] [--seat FOUNDRY]

WHY. Every row of bridge_debugging_system.md section 4 that cost hours (MODLIST, STALE, CONTENT load killers, HANG
wedgers) was knowable before the 15-minute cold load was spent. GPT's review (Transient/
foundry_bridge_system_review_gpt_20261010.md section 3) gives the order; this is the one implementation of it.
Reuse, not a parallel system: run_identity (deploy fingerprint), effective_def_lint (patched-tree load killers),
check_load (running list from RimDefDump's manifest), launch_gate (missing types), belt_watchdog (wedgers).

CONTRACT
  * Every check prints PASS / FAIL / UNMEASURED / UNSUPPORTED, its cost, and a reason. "Could not ask" is
    UNMEASURED, never PASS.
  * Checks run CHEAPEST first. A FAIL of a required check stops the run (fail-fast) unless --all; the rest print
    SKIPPED and count as UNMEASURED.
  * Exit code: 0 GREEN, 1 any FAIL, 2 no FAIL but a REQUIRED check is UNMEASURED/SKIPPED (not GREEN), 3 usage.
  * GREEN only when no FAIL and no required check is UNMEASURED.
  * Read-only, with ONE declared write: the current Player.log is copied into the archive (--no-archive to skip),
    because the next launch truncates it and it is the only record of the previous run.
  * Never takes the bridge, never launches/kills the game, never writes ModsConfig.xml.

INTENDED LIST, first that exists: `--modset <modset_builder tier>`; modmanifest's
infrastructure/state/modlists/manifest.<TIER>.json; the committed snapshot ModsConfig.FULL.LATEST.xml /
ModsConfig.MINIMAL.xml. Never inferred from what is deployed.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
import game_paths as gp  # noqa: E402

MODLISTS = os.path.join(REPO, 'infrastructure', 'state', 'modlists')
TIER_FILES = {'full': 'ModsConfig.FULL.LATEST.xml', 'minimal': 'ModsConfig.MINIMAL.xml'}
BRIDGE_FILE = os.path.join(REPO, 'infrastructure', 'state', 'BRIDGE')
COMPANION_REPO = os.path.join(REPO, 'src', 'RimMandrake', 'bridgetools', 'artifacts', 'BridgeTools', 'JawaBench',
                              'JawaBench.BridgeTools.dll')
COMPANION_GAME = gp.resolve(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll',
                            '/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/BridgeTools/JawaBench/JawaBench.BridgeTools.dll')
# by platform, NOT gp.resolve: resolve falls back to the Windows spelling when the WSL path does not exist YET, and
# os.makedirs('D:\\...') under WSL then creates a literal directory of that name in the cwd
SCRATCH = rm_win("scratch", "preflight") if os.name == 'nt' else rm_str("scratch", "preflight")
LOG_ARCHIVE = os.path.join(SCRATCH, 'playerlogs')
DEP_BASELINE = os.path.join(REPO, 'infrastructure', 'state', 'preflight', 'dependency_baseline.json')
LAST_REPORT = os.path.join(SCRATCH, 'last_preflight.json')
TOOL_SCHEMAS = os.path.join(HERE, 'northstar_driver', 'tool_schemas.json')
COMPANION_SRC = os.path.join(REPO, 'src', 'RimMandrake', 'bridgetools', 'JawaBench.BridgeTools')
RBS_WORKSHOP = '3727949765'
HARMONY_WORKSHOP = '2009463077'

# packageId -> why it is refused for a purpose. Kept beside belt_watchdog.KNOWN_LOOPS (the log-side twin).
WEDGERS = {
    'mlie.nwnrealfogofwar': ({'test'}, 'RealFoW IndexOutOfRange every Update after bland_world destroys ruins on a '
                             'second map: the game wedges, every step_game_ticks fails (bridge_debugging_system #61)'),
}
RESET_MARKERS = ('Resetting mods config', 'Recovered from incompatible or corrupted mods')


# ------------------------------------------------------------------------------------------------- the framework
class Result:
    def __init__(self, status, reason, evidence=None):
        assert status in ('PASS', 'FAIL', 'UNMEASURED', 'UNSUPPORTED', 'SKIPPED')
        self.status, self.reason, self.evidence = status, reason, evidence or {}


def PASS(r, **e): return Result('PASS', r, e)          # noqa: E704
def FAIL(r, **e): return Result('FAIL', r, e)          # noqa: E704
def UNM(r, **e): return Result('UNMEASURED', r, e)     # noqa: E704
def UNSUP(r, **e): return Result('UNSUPPORTED', r, e)  # noqa: E704


class Check:
    def __init__(self, cid, name, cost_s, required, fn, prevents=''):
        self.cid, self.name, self.cost_s, self.required, self.fn, self.prevents = cid, name, cost_s, required, fn, prevents


def _flush_print(*a, **k):
    print(*a, flush=True, **k)       # a killed run must still show what it reached (piped stdout is block-buffered)


def run_checks(checks, ctx, fail_fast=True, out=_flush_print):
    rows, stop = [], None
    for c in sorted(checks, key=lambda c: (c.cost_s, c.cid)):
        if stop:
            res = Result('SKIPPED', 'fail-fast after %s' % stop)
            dt = 0.0
        else:
            t0 = time.time()
            try:
                res = c.fn(ctx)
            except Exception as e:                             # noqa: BLE001 -- a crashed check is ignorance
                res = UNM('check raised %s: %s' % (type(e).__name__, str(e)[:200]))
            dt = time.time() - t0
        rows.append({'id': c.cid, 'name': c.name, 'required': c.required, 'status': res.status, 'reason': res.reason,
                     'cost_est_s': c.cost_s, 'took_s': round(dt, 2), 'prevents': c.prevents, 'evidence': res.evidence})
        out('%-10s %-4s %-24s %s %6.1fs  %s' % (res.status, c.cid, c.name, 'req' if c.required else 'opt', dt,
                                                 res.reason))
        if fail_fast and res.status == 'FAIL' and c.required and not stop:
            stop = c.cid
    return rows


def verdict(rows):
    if any(r['status'] == 'FAIL' for r in rows):
        return 'NO-GO', 1
    if any(r['required'] and r['status'] in ('UNMEASURED', 'SKIPPED') for r in rows):
        return 'NOT-GREEN', 2
    return 'GREEN', 0


# ------------------------------------------------------------------------------------------------------ helpers
def sha256(path, n=None):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()[:n] if n else h.hexdigest()


def active_ids(path):
    root = ET.parse(path).getroot()
    am = root.find('activeMods')
    return [(li.text or '').strip().lower() for li in (am if am is not None else []) if (li.text or '').strip()]


def intended(ctx):
    """(ordered ids, source label) -- modmanifest first, then --modset, then the committed snapshot."""
    if ctx.get('modset'):
        import modset_builder as mb
        ids, missing, refusals = mb.resolve_tier(ctx['modset'], mb.scan())
        return [x.lower() for x in ids], 'modset_builder tier %s' % ctx['modset']
    try:
        import modmanifest                                    # MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH
        m, p = modmanifest.load_manifest(ctx['tier'].upper())
        return [x.lower() for x in m['ids']], 'manifest.%s.json' % ctx['tier'].upper()
    except Exception:                                         # absent manifest / module: the committed snapshot
        pass
    f = TIER_FILES.get(ctx['tier'])
    if not f:
        raise ValueError('tier %s needs --modset' % ctx['tier'])
    return active_ids(os.path.join(MODLISTS, f)), 'snapshot %s' % f


def win_processes(name='RimWorldWin64.exe'):
    """[(pid, start_utc_epoch|None)] or None when the OS cannot be asked. tasklist answers presence (exit 0 with or
    without a match); powershell adds the start time only when there is a process (Get-Process with no match exits 1,
    which read as 'could not ask')."""
    try:
        t = subprocess.run(['tasklist.exe', '/FI', 'IMAGENAME eq %s' % name, '/FO', 'CSV', '/NH'], capture_output=True,
                           text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if t.returncode != 0:
        return None
    pids = [int(c[1]) for c in (ln.replace('"', '').split(',') for ln in t.stdout.replace('\r', '').splitlines())
            if len(c) > 1 and c[0].lower() == name.lower() and c[1].isdigit()]
    if not pids:
        return []
    try:
        out = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                              "Get-Process -Name %s -ErrorAction SilentlyContinue | ForEach-Object { \"$($_.Id) "
                              "$([int][double]::Parse((Get-Date $_.StartTime.ToUniversalTime() -UFormat %%s)))\" }"
                              % name.replace('.exe', '')],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return [(p, None) for p in pids]
    procs = []
    for ln in out.stdout.replace('\r', '').splitlines():
        parts = ln.split()
        if parts and parts[0].isdigit():
            procs.append((int(parts[0]), int(parts[1]) if len(parts) > 1 and parts[1].lstrip('-').isdigit() else None))
    return procs


def read_log(path=None):
    path = path or gp.PLAYER_LOG
    with open(path, encoding='utf-8', errors='replace') as fh:
        return fh.read()


def informational_build(dll):
    """The 40-hex git sha the SDK stamps into AssemblyInformationalVersion ('<ver>+<sha>'), first 12 chars."""
    with open(dll, 'rb') as fh:
        data = fh.read()
    m = re.search(rb'\d+\.\d+\.\d+(?:\.\d+)?\+([0-9a-f]{40})', data)
    return m.group(1).decode()[:12] if m else None


# ------------------------------------------------------------------------------------------------ offline checks
def c_game_down(ctx):
    procs = win_processes()
    if procs is None:
        return UNM('could not ask Windows for RimWorldWin64 (powershell failed); log age is NOT proof of absence')
    ctx['procs'] = procs
    if len(procs) > 1:
        return FAIL('%d RimWorldWin64 processes: %s' % (len(procs), procs))
    if ctx['live']:
        return PASS('1 process (attach)', procs=procs) if procs else FAIL('--live but no RimWorldWin64 process')
    return PASS('no RimWorldWin64 process') if not procs else FAIL(
        'game is UP (pid %s); a cold-launch preflight needs it down -- use --live to attach' % procs[0][0])


def c_bridge_lease(ctx):
    try:
        line = [ln for ln in open(BRIDGE_FILE, encoding='utf-8') if ln.strip() and not ln.startswith('#')][0].strip()
    except (OSError, IndexError):
        return UNM('cannot read %s' % BRIDGE_FILE)
    if line.startswith('FREE'):
        return PASS(line + (' -- take it before launching: rimflow bridge take --for "<what>"' if not ctx['live'] else ''))
    parts = line.split()
    holder = parts[1] if parts[0].upper() == 'HELD' and len(parts) > 1 else parts[0]
    if holder.upper().startswith(ctx['seat'].upper()):
        return PASS('held by this seat: ' + line)
    return FAIL('held by another seat: %s (rimflow bridge who; do offline work)' % line)


def c_disk(ctx):
    need = {'C': 20, 'D': 10}
    bad, got = [], {}
    for drv, root in (('C', gp.resolve('C:\\', '/mnt/c')), ('D', gp.resolve('D:\\', '/mnt/d'))):
        try:
            free = shutil.disk_usage(root).free / 2 ** 30
        except OSError:
            return UNM('cannot stat %s:' % drv)
        got[drv] = round(free, 1)
        if free < need[drv]:
            bad.append('%s: %.1f GB < %d GB' % (drv, free, need[drv]))
    return FAIL('; '.join(bad), free_gb=got) if bad else PASS('free GB %s' % got, free_gb=got)


def c_modsconfig(ctx):
    want, src = intended(ctx)
    ctx['want'], ctx['want_src'] = want, src
    try:
        have = active_ids(gp.MODS_CONFIG)
    except (OSError, ET.ParseError) as e:
        return UNM('cannot parse live ModsConfig.xml: %s' % e)
    ctx['have'] = have
    if have == want:
        return PASS('ModsConfig == %s (%d mods, ordered)' % (src, len(want)))
    ws, hs = set(want), set(have)
    miss, extra = [p for p in want if p not in hs], [p for p in have if p not in ws]
    core = ' -- looks like a Core-only RESET' if len(have) <= 8 else ''
    if not miss and not extra:
        first = next(i for i, (a, b) in enumerate(zip(want, have)) if a != b)
        return FAIL('same %d mods, DIFFERENT ORDER (first at #%d: want %s, have %s)' % (len(want), first, want[first],
                                                                                          have[first]))
    return FAIL('ModsConfig (%d) != %s (%d): %d missing %s, %d extra %s%s' % (
        len(have), src, len(want), len(miss), miss[:6], len(extra), extra[:6], core), missing=miss, extra=extra)


def c_list_sane(ctx):
    want = ctx.get('want') or intended(ctx)[0]
    import effective_def_lint as edl
    members = edl.composed_members()
    bad = [p for p in want if p in members]
    dup = sorted({p for p in want if want.count(p) > 1})
    idx = installed_index()
    absent = [p for p in want if p not in idx and not p.startswith('ludeon.')]
    msgs = []
    if bad:
        msgs.append('composed members listed (no runtime packageId): %s' % bad)
    if dup:
        msgs.append('duplicates %s' % dup)
    if absent:
        msgs.append('not installed %s' % absent)
    if msgs:
        return FAIL('; '.join(msgs), members=bad, duplicates=dup, absent=absent)
    if not members:
        return UNM('Biomes.compose.json unreadable: member check not done')
    return PASS('%d ids, none composed/duplicate/uninstalled' % len(want))


def c_ship_coverage(ctx):
    if ctx['tier'] != 'full':
        return PASS('not the full tier: a test list is deliberately partial')
    try:
        import modmanifest
        ours, folded = modmanifest.shipping_ids()
    except Exception as e:                                    # noqa: BLE001
        return UNSUP('modmanifest.shipping_ids unavailable: %s' % e)
    gap = modmanifest.shipping_gap(ctx.get('want') or intended(ctx)[0], ours, folded)
    if gap['absent'] or gap['folded_but_listed']:
        return FAIL('%d mods we build are absent from the intended list %s; %d folded members listed %s' % (
            len(gap['absent']), gap['absent'][:8], len(gap['folded_but_listed']), gap['folded_but_listed'][:4]), **gap)
    return PASS('every mod we build is on the list')


_IDX = {}


def about_id(mod_dir):
    """The mod's OWN packageId: the root element's child, parsed. A regex takes the first <packageId> in the file,
    which is often a modDependencies entry (brrainz.harmony) -- that read 'sarg.alphabiomes' as not installed."""
    try:
        root = ET.parse(os.path.join(mod_dir, 'About', 'About.xml')).getroot()
    except (OSError, ET.ParseError):
        return None
    v = (root.findtext('packageId') or '').strip().lower()
    return v or None


def installed_index():
    if not _IDX:
        for root in (gp.LOCAL_MODS, gp.WORKSHOP):
            try:
                names = os.listdir(root)
            except OSError:
                continue
            for d in names:
                pid = about_id(os.path.join(root, d))
                if pid:
                    _IDX.setdefault(pid, os.path.join(root, d))
    return _IDX


def c_wedgers(ctx):
    want = ctx.get('want') or intended(ctx)[0]
    hits = [(p, why) for p, (purposes, why) in WEDGERS.items() if p in want and ctx['purpose'] in purposes]
    if hits:
        return FAIL('; '.join('%s on a %s run: %s' % (p, ctx['purpose'], w) for p, w in hits))
    present = [p for p in WEDGERS if p in want]
    return PASS('no known wedger for purpose %s%s' % (ctx['purpose'], (' (present but allowed: %s)' % present)
                                                       if present else ''))


def c_player_log(ctx):
    if not os.path.isfile(gp.PLAYER_LOG):
        return PASS('no Player.log to preserve')
    sha = sha256(gp.PLAYER_LOG, 12)
    stamp = time.strftime('%Y%m%dT%H%M%S', time.gmtime(os.path.getmtime(gp.PLAYER_LOG)))
    dst = os.path.join(LOG_ARCHIVE, 'Player_%s_%s.log' % (stamp, sha))
    if os.path.exists(dst):
        return PASS('already archived: %s' % dst, archive=dst)
    if ctx['no_archive']:
        return UNM('not archived (--no-archive); the next launch truncates it')
    os.makedirs(LOG_ARCHIVE, exist_ok=True)
    shutil.copy2(gp.PLAYER_LOG, dst)
    return PASS('archived %s' % dst, archive=dst) if sha256(dst, 12) == sha else FAIL('archive copy hash differs')


def c_companion(ctx):
    if not os.path.isfile(COMPANION_REPO):
        return UNM('no repo companion artifact %s' % COMPANION_REPO)
    if not os.path.isfile(COMPANION_GAME):
        return FAIL('companion not deployed: %s' % COMPANION_GAME)
    r, g = sha256(COMPANION_REPO), sha256(COMPANION_GAME)
    rb, gb = informational_build(COMPANION_REPO), informational_build(COMPANION_GAME)
    ctx['companion'] = {'repo_sha': r, 'game_sha': g, 'repo_build': rb, 'game_build': gb}
    side = COMPANION_REPO + '.srchash'
    note = '' if os.path.isfile(side) else ' (no .srchash beside the repo artifact: source provenance unproven)'
    if r != g:
        return FAIL('deployed companion %s (build %s) != repo artifact %s (build %s)%s' % (g[:12], gb, r[:12], rb, note),
                    **ctx['companion'])
    return PASS('deployed == repo %s (build %s)%s' % (r[:12], rb, note), **ctx['companion'])


def dependency_fingerprint():
    fp = {}
    rbs = os.path.join(gp.WORKSHOP, RBS_WORKSHOP)
    for f in sorted(glob.glob(os.path.join(rbs, '1.6', 'Assemblies', '*.dll'))) + \
            [os.path.join(gp.WORKSHOP, HARMONY_WORKSHOP, 'Current', 'Assemblies', '0Harmony.dll'),
             os.path.join(gp.GAME_DATA, '..', 'RimWorldWin64_Data', 'Managed', 'Assembly-CSharp.dll')]:
        if os.path.isfile(f):
            fp[os.path.basename(f)] = sha256(f, 16)
    man = os.path.join(rbs, 'About', 'Manifest.xml')
    if os.path.isfile(man):
        m = re.search(r'<version>([^<]+)', open(man, encoding='utf-8-sig', errors='replace').read())
        fp['RimBridgeServer.version'] = m.group(1) if m else '?'
    return fp


def c_deps(ctx):
    fp = dependency_fingerprint()
    ctx['deps'] = fp
    if len([k for k in fp if k.endswith('.dll')]) < 3:
        return UNM('found only %s -- RBS/Harmony/game assemblies not where expected' % sorted(fp))
    if ctx['accept_deps']:
        os.makedirs(os.path.dirname(DEP_BASELINE), exist_ok=True)
        json.dump({'recorded': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'fp': fp}, open(DEP_BASELINE, 'w'),
                  indent=1, sort_keys=True)
        return PASS('baseline written (%d entries): %s' % (len(fp), DEP_BASELINE))
    try:
        base = json.load(open(DEP_BASELINE))['fp']
    except (OSError, ValueError, KeyError):
        return UNM('no dependency baseline yet (--accept-deps after a green load records one)', fp=fp)
    diff = sorted(k for k in set(fp) | set(base) if fp.get(k) != base.get(k))
    return FAIL('changed since the baseline: %s (Steam auto-update? runs are not comparable)' % diff, fp=fp) if diff \
        else PASS('RBS %s, Harmony, game assemblies unchanged since baseline' % fp.get('RimBridgeServer.version'))


def c_lint_fresh(ctx):
    try:
        snap = json.load(open(TOOL_SCHEMAS))
    except (OSError, ValueError):
        return UNM('cannot read %s' % TOOL_SCHEMAS)
    names = set()
    if isinstance(snap, dict):
        names = set(snap.get('tools', snap).keys()) if isinstance(snap.get('tools', snap), dict) else \
            {t.get('name') for t in snap.get('tools', []) if isinstance(t, dict)}
    elif isinstance(snap, list):
        names = {t.get('name') for t in snap if isinstance(t, dict)}
    declared = set()
    for p in glob.glob(os.path.join(COMPANION_SRC, '*.cs')):
        declared |= {n for n in re.findall(r'\[Tool\(\s*"([^"]+)"', open(p, encoding='utf-8-sig', errors='replace').read())
                     if '...' not in n and '<' not in n}           # doc-comment placeholders like [Tool("jawa/...")]
    if not declared or not names:
        return UNM('declared %d / snapshot %d tool names: cannot compare' % (len(declared), len(names)))
    missing = sorted(declared - names)
    age_d = (time.time() - os.path.getmtime(TOOL_SCHEMAS)) / 86400
    if missing:
        return FAIL('%d companion tools declared in C# but absent from the lint snapshot (%.1f d old): %s' % (
            len(missing), age_d, missing[:8]), missing=missing)
    return PASS('lint snapshot covers all %d declared tools (%.1f d old)' % (len(declared), age_d))


def c_src_killers(ctx):
    import effective_def_lint as edl
    rep = edl.Report()
    edl.check_src(rep)
    bad = rep.failed()
    detail = {n: [f['def'] for f in c['findings'] if f['sev'] in ('crash', 'error')][:5] for n, c in rep.checks.items()}
    return FAIL('repo load killers: %s' % {n: detail[n] for n in bad}) if bad else PASS(
        'BiomeWorker .Rivers, abstract Alert leaves, csproj Compile Include: clean')


def c_def_lint(ctx):
    """The patched-tree lint. Cached by content; a miss costs ~1-5 min, run only with --deep."""
    want_src = ctx.get('want_src', '')
    if want_src.startswith('snapshot'):
        mc = os.path.join(MODLISTS, TIER_FILES.get(ctx['tier'], ''))
    elif want_src.startswith('manifest.'):
        mc = os.path.join(MODLISTS, want_src)
    else:                                                       # --modset: the lint needs a file; lint what the
        mc = gp.MODS_CONFIG                                     # next load will actually read
    if not os.path.isfile(mc):
        return UNM('no list file to lint: %s' % mc)
    rel = os.path.relpath(mc, REPO) if mc.startswith(REPO) else None
    out_json = os.path.join(SCRATCH, 'effective_def_lint_last.json')
    os.makedirs(SCRATCH, exist_ok=True)
    if sys.platform.startswith('linux') and shutil.which('python.exe') and rel:
        win_json = rm_win("scratch", "preflight", "effective_def_lint_last.json")
        cmd = ['python.exe', 'src/RimMandrake/Utils/effective_def_lint.py', rel.replace(os.sep, '/'), '--json', win_json]
    else:
        cmd = [sys.executable, os.path.join(HERE, 'effective_def_lint.py'), mc, '--json', out_json]
    if not ctx['deep']:
        cmd.append('--cache-only')
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1500)
    except subprocess.TimeoutExpired:
        return UNM('effective_def_lint timed out (25 min)')
    if p.returncode == 4 and 'CACHE-MISS' in p.stdout:
        return UNM('effective_def_lint has no cached result for this exact content; run with --deep (~1-5 min)')
    try:
        rep = json.load(open(out_json))
    except (OSError, ValueError):
        return UNM('effective_def_lint wrote no report (exit %s): %s' % (p.returncode, (p.stderr or p.stdout)[-300:]))
    crash = [(n, f['mod'], f['def'], f['detail'][:120]) for n, c in rep['checks'].items() for f in c['findings']
             if f['sev'] == 'crash']
    failed = [n for n, c in rep['checks'].items() if c['status'] == 'FAIL']
    unsup = [n for n, c in rep['checks'].items() if c['status'] == 'UNSUPPORTED']
    summary = '%s; cache %s; unsupported scope: %s' % (rep['meta'].get('modlist'), rep['meta'].get('cache', '?')[:4],
                                                      unsup)
    if crash:
        return FAIL('%d LOAD-CRASH findings (%s): first %s | %s' % (len(crash), sorted({c[0] for c in crash}), crash[0],
                                                                   summary), crash=crash[:30], failed=failed)
    if failed:
        return FAIL('no crash path, but error findings in %s | %s' % (failed, summary), failed=failed)
    return PASS('clean | ' + summary)


# --------------------------------------------------------------------------------------------------- live checks
def c_live_identity(ctx):
    procs = ctx.get('procs') or win_processes()
    if not procs:
        return UNM('no RimWorldWin64 process to attach to')
    pid, start = procs[0]
    try:
        log = read_log()
        mtime = os.path.getmtime(gp.PLAYER_LOG)
    except OSError as e:
        return UNM('cannot read Player.log: %s' % e)
    ctx['log'] = log
    tok = re.search(r'\[RimBridge\]\s*Bridge token:', log)
    port = re.search(r'\[RimBridge\].*?on port\s+(\d+)', log)
    if start and mtime < start:
        return FAIL('Player.log last written before pid %s started: it is the PREVIOUS run (row 39)' % pid)
    if not tok:
        return UNM('no "Bridge token:" in the current Player.log yet (still loading?)')
    listen = None
    if port:
        try:
            o = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                                'Get-NetTCPConnection -State Listen -LocalPort %s -ErrorAction SilentlyContinue | '
                                'Select-Object -ExpandProperty OwningProcess' % port.group(1)],
                               capture_output=True, text=True, timeout=30)
            listen = [int(x) for x in o.stdout.split() if x.isdigit()]
        except (OSError, subprocess.SubprocessError):
            listen = None
    if listen is None:
        return UNM('token present for pid %s, but the listener on port %s could not be read' % (
            pid, port.group(1) if port else '?'))
    if pid not in listen:
        return FAIL('port %s is held by pid %s, not RimWorld pid %s' % (port.group(1), listen, pid))
    return PASS('pid %s started %s, token in its log, listening on %s' % (
        pid, time.strftime('%H:%M:%SZ', time.gmtime(start)) if start else '?', port.group(1)))


def c_live_reset(ctx):
    log = ctx.get('log') or read_log()
    hits = [m for m in RESET_MARKERS if m in log]
    n = len(active_ids(gp.MODS_CONFIG))
    if hits:
        return FAIL('Core-only RESET in this run: %s; ModsConfig now %d mods. Read the FIRST exception.' % (hits, n))
    return PASS('no reset marker; ModsConfig %d mods' % n)


def c_live_first_exception(ctx):
    log = ctx.get('log') or read_log()
    from modcheck import launch_gate
    g = launch_gate.scan(log)
    first = None
    for ln in log.splitlines():
        if re.search(r'Exception|Could not find type named|Config error in', ln):
            first = ln.strip()[:220]
            break
    ce = len(re.findall(r'^Config error in', log, re.M))
    ev = {'first_exception': first, 'config_errors': ce, 'missing_types': g['missing_types']}
    if g['missing_types']:
        return FAIL('%d missing RimMandrake types (stale DLL?): %s | first: %s' % (len(g['missing_types']),
                                                                                g['missing_types'][:5], first), **ev)
    if not g['probe']:
        return UNM('launch_gate probe line absent: %s' % g['problems'], **ev)
    return PASS('no missing types; %d Config errors; first exception: %s' % (ce, first), **ev)


def c_live_mods(ctx):
    import check_load
    r = check_load.evaluate()
    if r.get('absent'):
        return UNM('no %s: RimDefDump did not write its manifest (yet)' % r['absent'])
    procs = ctx.get('procs') or win_processes() or []   # --live never runs O01, so ctx may lack procs
    if procs and procs[0][1] and os.path.getmtime(check_load.MANIFEST) < procs[0][1]:
        return UNM('DefDump manifest predates this process: it describes a previous load')
    want = ctx.get('want') or intended(ctx)[0]
    if r['got'] != want:
        miss = [p for p in want if p not in set(r['got'])]
        extra = [p for p in r['got'] if p not in set(want)]
        return FAIL('running list (%d) != intended (%d): missing %s extra %s%s' % (
            len(r['got']), len(want), miss[:6], extra[:6], ' (same set, other ORDER)' if not miss and not extra else ''))
    return PASS('running list == intended, ordered (%d mods)' % len(want))


def c_live_companion(ctx):
    log = ctx.get('log') or read_log()
    m = re.search(r'\[JawaBench\] ready: (\d+) tools, build (\S+)', log)
    if not m:
        return UNM('no "[JawaBench] ready:" line in the current log')
    want = (ctx.get('companion') or {}).get('repo_build') or informational_build(COMPANION_REPO)
    if want and m.group(2)[:12] != want:
        return FAIL('live companion build %s != repo artifact build %s' % (m.group(2), want))
    return PASS('live companion %s tools, build %s' % (m.group(1), m.group(2)))


def c_live_tps(ctx):
    log = ctx.get('log') or read_log()
    m = re.search(r'\[JawaBench\] TPS sampler installed \(([^)]+)\)', log)
    if m:
        return PASS('TPS record autostarted (%s)' % m.group(1)) if m.group(1) == 'bridge-registration' else FAIL(
            'TPS record started by %s, not at bridge registration (autostart broken: prediction 33)' % m.group(1))
    if '[JawaBench] TPS sampler OFF' in log:
        return UNM('TPS sampler switched OFF by tps_settings.json')
    if '[JawaBench] TPS sampler NOT installed' in log:
        return FAIL('TPS sampler NOT installed (see the Warning line)')
    return UNM('no TPS sampler line yet')


def c_live_awareness(ctx):
    log = ctx.get('log') or read_log()
    m = re.search(r'\[JawaBench\] map awareness: (\S+) by (\S+)[^\n]*', log)
    if not m:
        return UNM('no "[JawaBench] map awareness:" line (companion without awareness, or not initialised)')
    st = m.group(1).lower()
    if any(x in st for x in ('fail', 'error', 'partial')):
        return FAIL(m.group(0)[:200])
    return PASS(m.group(0)[:200])


# ---------------------------------------------------------------------------------------------------- registry
OFFLINE = [
    Check('O01', 'game_down', 2, True, c_game_down, '#21 two processes, #39 old log'),
    Check('O02', 'bridge_lease', 0.1, True, c_bridge_lease, '#22 #50 two drivers'),
    Check('O03', 'disk_space', 0.2, True, c_disk, 'O05'),
    Check('O04', 'modsconfig_intent', 0.5, True, c_modsconfig, '#19 #47 #54 wrong list'),
    Check('O05', 'list_sane', 1.5, True, c_list_sane, '#58 #80 member ids'),
    Check('O06', 'ship_coverage', 0.3, False, c_ship_coverage, 'P-a 14 missing'),
    Check('O07', 'known_wedgers', 0.1, True, c_wedgers, '#61 RealFoW'),
    Check('O08', 'player_log_archive', 1, True, c_player_log, '#26 stale log generation'),
    Check('O09', 'companion_match', 1, True, c_companion, '#51 #57 stale DLL, P-c'),
    Check('O10', 'dependency_fp', 2, False, c_deps, 'prediction 14/18'),
    Check('O11', 'bridge_lint_fresh', 1, False, c_lint_fresh, 'P-d'),
    Check('O12', 'src_load_killers', 1, True, c_src_killers, '#33 alert leaf, BiomeWorker rivers'),
    Check('O13', 'deploy_match', 60, True, lambda ctx: c_deploy(ctx), '#31 #46 #52 #57 deploy drift'),
    Check('O14', 'effective_def_lint', 30, True, c_def_lint, '#24 #30 #36 #37 #41 #53 #66 load killers'),
]
LIVE = [
    Check('L01', 'live_identity', 3, True, c_live_identity, '#39 previous log'),
    Check('L02', 'live_core_reset', 0.5, True, c_live_reset, '#30 #32 #36 #37'),
    Check('L03', 'live_first_exception', 1, True, c_live_first_exception, '#57 missing types'),
    Check('L04', 'live_mods_ordered', 1, True, c_live_mods, '#19 #54'),
    Check('L05', 'live_companion', 0.3, True, c_live_companion, 'prediction 9'),
    Check('L06', 'live_tps_autostart', 0.3, False, c_live_tps, 'prediction 33'),
    Check('L07', 'live_awareness_init', 0.3, False, c_live_awareness, 'prediction 6'),
]


def _tree_sha(root, exclude):
    """{rel: sha256} of every file under root (dirs in `exclude` skipped). Byte-exact, like filecmp shallow=False."""
    out = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in exclude]
        for f in fn:
            full = os.path.join(dp, f)
            try:
                out[os.path.relpath(full, root).replace(os.sep, '/')] = sha256(full, 20)
            except OSError:
                out[os.path.relpath(full, root).replace(os.sep, '/')] = 'unreadable'
    return out


def _win(path):
    m = re.match(r'^/mnt/([a-z])/(.*)$', path)
    return ('%s:\\%s' % (m.group(1).upper(), m.group(2).replace('/', '\\'))) if m else path


def deployed_trees(dirs, exclude):
    """{dir: {rel: sha}} for deployed mod folders. Under WSL the walk is delegated to Windows python.exe (NTFS
    natively; the same walk over drvfs took >14 min for ~110 mods); in-process otherwise."""
    if not (sys.platform.startswith('linux') and shutil.which('python.exe')):
        return {d: (_tree_sha(d, exclude) if os.path.isdir(d) else None) for d in dirs}
    req = os.path.join(SCRATCH, 'emit_req.json')
    os.makedirs(SCRATCH, exist_ok=True)
    json.dump({'dirs': [_win(d) for d in dirs], 'exclude': sorted(exclude)}, open(req, 'w'))
    p = subprocess.run(['python.exe', 'src/RimMandrake/Utils/preflight_bridge.py', '--emit-trees', _win(req)],
                       cwd=REPO, capture_output=True, text=True, timeout=1200)
    if p.returncode != 0:
        raise RuntimeError('python.exe tree walk failed: %s' % (p.stderr or p.stdout)[-300:])
    got = json.loads(p.stdout)
    return {d: got.get(_win(d)) for d in dirs}


def c_deploy(ctx):
    """Every mandrake mod on the intended list: repo == the game's Mods copy, byte-exact per shippable file (sha),
    with DEPLOY_HOLD.txt honoured and the composed RimMandrake.Biomes built once and compared whole. The deploy tool's
    own tree()/shippable()/holds decide what counts, so this cannot disagree with its plan about what ships."""
    import deploy_custom_mods as dm
    want = set(ctx.get('want') or intended(ctx)[0])
    holds = dm.load_holds()
    pairs = []                                                 # (deploy name, src dir, holds)
    for mod, d in dm.mod_dirs().items():
        if about_id(d) in want:
            pairs.append((mod, d, holds))
    cleanup = None
    try:
        if 'mandrake.rm.biomes' in want:
            import biomes_compose
            cname, csrc, extra = biomes_compose.build(dm.SRC_ROOT, dm.tree, holds, log=lambda *a, **k: None)
            cleanup = os.path.dirname(csrc)
            pairs.append((cname, csrc, holds + extra))
        if not pairs:
            return UNM('no repo mod maps onto the intended list (sanity: expected dozens)')
        dsts = [os.path.join(dm.LOCAL_MODS, name) for name, _, _ in pairs]
        trees = deployed_trees(dsts, dm.EXCLUDE_DIRS)
        drift, nfiles = [], 0
        for (name, src, hl), dst in zip(pairs, dsts):
            d_all = trees.get(dst)
            if d_all is None:
                drift.append('%s(not deployed)' % name)
                continue
            s_rels = dm.tree(src)
            s_all = {r.replace(os.sep, '/'): sha256(os.path.join(src, r), 20) for r in s_rels}
            d_all = {r: v for r, v in d_all.items() if dm.shippable(r.replace('/', os.sep))}
            held = {r for r, _h in dm.split_held(hl, name, sorted(set(s_all) | set(d_all)))[1]}
            keys = (set(s_all) | set(d_all)) - held
            bad = sorted(r for r in keys if s_all.get(r) != d_all.get(r))
            nfiles += len(keys)
            if bad:
                drift.append('%s(%d: %s)' % (name, len(bad), bad[:3]))
        if drift:
            return FAIL('%d of %d mods (%d files) differ from the deployed copy: %s' % (len(drift), len(pairs), nfiles, drift[:6]),
                        drift=drift)
        return PASS('%d mods, %d files: deployed == repo byte for byte' % (len(pairs), nfiles))
    finally:
        if cleanup:
            shutil.rmtree(cleanup, ignore_errors=True)


def emit_trees(req_path):
    """--emit-trees: the Windows-side half of deployed_trees (run by python.exe)."""
    req = json.load(open(req_path))
    ex = set(req['exclude'])
    print(json.dumps({d: (_tree_sha(d, ex) if os.path.isdir(d) else None) for d in req['dirs']}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--tier', default='full', help='full | minimal | quicktest (quicktest needs --modset)')
    ap.add_argument('--modset', help='a modset_builder tier name as the intended list')
    ap.add_argument('--purpose', default='test', choices=('test', 'campaign', 'menu', 'review'),
                    help='test = bland-world/suite run (wedgers refused); campaign/menu/review relax that')
    ap.add_argument('--live', action='store_true', help='attach: first-five-minutes checks on the running game')
    ap.add_argument('--deep', action='store_true', help='allow the patched-tree lint to run on a cache miss')
    ap.add_argument('--all', action='store_true', help='no fail-fast: run every check')
    ap.add_argument('--no-archive', action='store_true')
    ap.add_argument('--accept-deps', action='store_true', help='record the dependency fingerprint as the baseline')
    ap.add_argument('--seat', default=os.environ.get('RIMFLOW_SEAT', 'FOUNDRY'))
    ap.add_argument('--only', help='comma list of check ids or names')
    ap.add_argument('--json')
    ap.add_argument('--emit-trees', help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.emit_trees:
        return emit_trees(a.emit_trees)
    if a.tier == 'quicktest' and not a.modset:
        a.modset = None
        a.tier = 'minimal'
    ctx = {'tier': a.tier, 'modset': a.modset, 'purpose': a.purpose, 'live': a.live, 'deep': a.deep,
           'no_archive': a.no_archive, 'accept_deps': a.accept_deps, 'seat': a.seat}
    checks = [c for c in OFFLINE if not (a.live and c.cid in ('O08',))]
    if a.live:
        checks = [c for c in checks if c.cid in ('O01', 'O02', 'O04', 'O09')] + LIVE
        for c in checks:
            if c.cid == 'O04':
                c.required = False        # live: ModsConfig is the NEXT load's list; L04 judges the running one
    if a.only:
        keep = set(a.only.split(','))
        checks = [c for c in checks if c.cid in keep or c.name in keep]
    print('preflight %s tier=%s purpose=%s seat=%s %s' % ('LIVE' if a.live else 'OFFLINE', a.tier, a.purpose, a.seat,
                                                         time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
    rows = run_checks(checks, ctx, fail_fast=not a.all)
    v, code = verdict(rows)
    print('VERDICT %s%s' % (v, (' ' + ','.join(r['id'] for r in rows if r['status'] == 'FAIL' or (
        r['required'] and r['status'] in ('UNMEASURED', 'SKIPPED')))) if code else ''))
    report = {'when': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'mode': 'live' if a.live else 'offline',
              'tier': a.tier, 'modset': a.modset, 'purpose': a.purpose, 'verdict': v, 'rows': rows}
    for p in filter(None, [a.json, LAST_REPORT]):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
            json.dump(report, open(p, 'w'), indent=1, default=str)
        except OSError:
            pass
    return code


if __name__ == '__main__':
    sys.exit(main())
