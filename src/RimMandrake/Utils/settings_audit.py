#!/usr/bin/env python3
"""settings_audit.py - OFFLINE audit of SettingsKit mod-settings screens (MOD_OPTIONS_RETROFIT_1).
Per csproj under src/**/Source: (1) Mod subclass + SettingsKit use, (2) settings/Mod .cs files present in the
compile set (EnableDefaultCompileItems=false trap), (3) committed DLL .srchash vs source (dll_source_stamp.py),
(4) label keys: kit uses literal strings, so reports Translate() use only, (5) defaults: field initialiser vs
Scribe_Values.Look default argument, (6) master switches (SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST): a screen that draws a
master switch but declares no SettingDependencies is NOTED (its dependents cannot grey); one that declares them must
compile SettingsKitMasters*.cs (FAIL). Per-setting classification is selftest_settings_screens.py's job. Offline only: proves nothing about the live game.
Usage: settings_audit.py [--root REPO] [--out FILE] [--json]"""
import argparse, glob, os, re, subprocess, sys, json
import xml.etree.ElementTree as ET

def strip_ns(t): return t.split('}')[-1]

def compile_set(csproj):
    d = os.path.dirname(csproj)
    root = ET.parse(csproj).getroot()
    props = {}
    for pg in root.iter():
        if strip_ns(pg.tag) == 'EnableDefaultCompileItems' and pg.text: props['edci'] = pg.text.strip().lower()
    edci_false = props.get('edci') == 'false'
    files = set()
    removes = []
    if not edci_false:
        for p in glob.glob(os.path.join(d, '**', '*.cs'), recursive=True):
            rel = os.path.relpath(p, d).replace('\\', '/')
            if rel.startswith(('obj/', 'bin/')): continue
            files.add(os.path.normpath(p))
    for el in root.iter():
        if strip_ns(el.tag) == 'Compile':
            inc = el.get('Include'); rem = el.get('Remove')
            if inc:
                pat = os.path.normpath(os.path.join(d, inc.replace('\\', '/')))
                for p in (glob.glob(pat, recursive=True) if any(c in pat for c in '*?') else [pat]):
                    files.add(os.path.normpath(p))
            if rem: removes.append(os.path.normpath(os.path.join(d, rem.replace('\\', '/'))))
    for r in removes:
        files = {f for f in files if f != r}
    return edci_false, files

def read(p):
    try: return open(p, encoding='utf-8-sig', errors='replace').read()
    except OSError: return ''

def defaults_check(text):
    """Pair `public static T name = init;` with Scribe_Values.Look(ref name, "key", default)."""
    inits = {}
    for m in re.finditer(r'public\s+static\s+(?:bool|float|int)\s+(\w+)\s*=\s*([^;]+);', text):
        inits[m.group(1)] = m.group(2).strip().rstrip('f').rstrip('F')
    # A Scribe default that differs from the initialiser on purpose is a MIGRATION SENTINEL (the key is absent from an old file, so the
    # loader sees it and migrates). The source declares it next to the Look: `// settings-audit: sentinel <name>`; only a NEGATIVE
    # scribe default qualifies (a real value is never negative here), so the marker cannot hide an ordinary drift.
    sentinels = set(re.findall(r'settings-audit:\s*sentinel\s+(\w+)', text))
    bad, n = [], 0
    for m in re.finditer(r'Scribe_Values\.Look\(\s*ref\s+(\w+)\s*,\s*"[^"]*"\s*,\s*([^,)]+)', text):
        name, dflt = m.group(1), m.group(2).strip().rstrip('f').rstrip('F')
        if name in inits:
            a, b = inits[name], dflt
            if not re.fullmatch(r'-?[\d.]+|true|false', a) or not re.fullmatch(r'-?[\d.]+|true|false', b):
                continue  # not determinable statically
            if name in sentinels and re.fullmatch(r'-[\d.]+', b):
                n += 1
                continue
            n += 1
            try: same = float(a) == float(b)
            except ValueError: same = a.lower() == b.lower()
            if not same: bad.append(f'{name}: init {inits[name]} vs scribe default {dflt}')
    return n, bad

def stamp_status(root):
    r = subprocess.run([sys.executable, os.path.join(root, 'src/RimMandrake/Utils/dll_source_stamp.py'), 'check'],
                       cwd=root, capture_output=True, text=True)
    st, cur = {}, None
    for line in r.stdout.splitlines():
        if line.startswith(('MATCH ', 'MISMATCH ', 'STAMP_MISSING ')):
            k, p = line.split(' ', 1); st[p.strip()] = [k]; cur = p.strip()
        elif cur and line.strip(): st[cur].append(line.strip())
    return st

def project_stamps(stamps, rel_dir, csproj_text):
    """The committed-DLL stamps (dll_source_stamp.py paths) that belong to the csproj in `rel_dir` (repo-relative). The mod
    root is the folder above its Source/ (a csproj in Source/<Sub>/, as in a multi-assembly mod, used to look in Source/Assemblies/,
    found nothing and only NOTED "no committed DLL stamp", so a stale DLL there could never FAIL check (3)); without a Source/
    segment, the csproj folder's parent as before. Narrowed to the csproj's <AssemblyName>.dll when that matches a stamp."""
    parts = rel_dir.replace('\\', '/').split('/')
    mod_root = '/'.join(parts[:parts.index('Source')]) if 'Source' in parts else os.path.dirname(rel_dir)
    mine = [p for p in stamps if p.startswith(mod_root + '/') and '/Assemblies/' in p[len(mod_root):]]
    m = re.search(r'<AssemblyName>\s*([^<\s]+)\s*</AssemblyName>', csproj_text or '')
    named = [p for p in mine if m and os.path.basename(p) == m.group(1) + '.dll']
    return named or mine

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=None); ap.add_argument('--out'); ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    root = a.root or subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True, cwd=os.path.dirname(os.path.abspath(__file__))).strip()
    stamps = stamp_status(root)
    rows = []
    for cs in sorted(glob.glob(os.path.join(root, 'src', '**', '*.csproj'), recursive=True)):
        if '/obj/' in cs or '/_Shared/' in cs: continue
        d = os.path.dirname(cs)
        srcs = [p for p in glob.glob(os.path.join(d, '**', '*.cs'), recursive=True) if '/obj/' not in p and '/bin/' not in p]
        texts = {p: read(p) for p in srcs}
        has_kit_anywhere = any('SettingsKit' in t for t in texts.values())
        settings_files = [p for p, t in texts.items() if re.search(r':\s*ModSettings\b', t) or re.search(r'class\s+\w+\s*:\s*Mod\b', t)]
        edci_false, cset = compile_set(cs)
        rel = os.path.relpath(cs, root)
        mod = os.path.relpath(d, os.path.join(root, 'src')).split(os.sep)
        modname = '/'.join(mod[:-1]) if mod[-1] == 'Source' else '/'.join(mod)
        r = dict(mod=modname, csproj=rel, has_settings=bool(settings_files), kit=has_kit_anywhere, fails=[], notes=[])
        if not settings_files:
            r['status'] = 'NO_SETTINGS'; rows.append(r); continue
        in_set = [p for p in settings_files if os.path.normpath(p) in cset]
        if not in_set: r['fails'].append('(1) no Mod/ModSettings class is in the compile set')
        if not any(re.search(r'class\s+\w+\s*:\s*Mod\b', texts[p]) for p in in_set):
            par = os.path.dirname(d)
            sib = any(re.search(r'class\s+\w+\s*:\s*Mod\b', read(p)) for p in glob.glob(os.path.join(par, '**', '*.cs'), recursive=True))
            if sib: r['notes'].append('settings-only assembly; Mod subclass lives in a sibling assembly of the same mod')
            else: r['fails'].append('(1) no Mod subclass compiled')
        for p in settings_files:
            if os.path.normpath(p) not in cset:
                r['fails'].append(f'(2) not compiled: {os.path.relpath(p, d)}')
        if not any('SettingsKit' in texts[p] for p in settings_files) and not has_kit_anywhere:
            r['notes'].append('no SettingsKit use (bespoke screen)')
        if has_kit_anywhere and edci_false:
            for kf in ('SettingsKitCore.cs', 'SettingsKitDrawer.cs'):
                if not any(os.path.basename(c) == kf for c in cset):
                    if any('SettingsKit' in texts[p] for p in settings_files): r['fails'].append(f'(2) kit file {kf} not in compile set')
        declares = any('SettingDependencies' in texts[p] and '.Declare(' in texts[p] for p in settings_files)
        draws_master = any(re.search(r'\(master switch\)|"Mod enabled"|Master switch for', texts[p]) for p in settings_files)
        r['masters'] = 'declared' if declares else ('UNDECLARED' if draws_master else '-')
        if declares and edci_false:
            for kf in ('SettingsKitMasters.cs', 'SettingsKitMastersDrawer.cs'):
                if not any(os.path.basename(c) == kf for c in cset): r['fails'].append(f'(6) masters kit file {kf} not in compile set')
        if draws_master and not declares:
            r['notes'].append('(6) draws a master switch but declares no SettingDependencies: its dependents cannot grey')
        proj_stamp = project_stamps(stamps, os.path.relpath(d, root), read(cs))
        if not proj_stamp: r['notes'].append('(3) no committed DLL stamp')
        for p in proj_stamp:
            if stamps[p][0] != 'MATCH': r['fails'].append(f'(3) {stamps[p][0]} {p} ' + '; '.join(stamps[p][1:3]))
        tr = sum(texts[p].count('.Translate(') + texts[p].count('"Translate"') for p in settings_files)
        r['translate_uses'] = tr
        n = 0
        for p in settings_files:
            k, bad = defaults_check(texts[p]); n += k
            for b in bad: r['fails'].append('(5) default mismatch ' + b)
        r['defaults_checked'] = n
        r['status'] = 'FAIL' if r['fails'] else 'OK'
        rows.append(r)
    withs = [r for r in rows if r['has_settings']]
    out = []
    out.append('# Settings audit (offline, static)\n')
    out.append('Offline static audit of SettingsKit screens. NOT live verification: no screen has been opened in the game.\n')
    out.append(f'- csproj scanned: {len(rows)}; with a Mod/ModSettings class: {len(withs)}; using SettingsKit: {sum(1 for r in withs if r["kit"])}')
    out.append(f'- OK: {sum(1 for r in withs if r["status"]=="OK")}; FAIL: {sum(1 for r in withs if r["status"]=="FAIL")}')
    out.append(f'- check (6) master switches: declared {sum(1 for r in withs if r.get("masters")=="declared")}; drawn but undeclared (dependents cannot grey) {sum(1 for r in withs if r.get("masters")=="UNDECLARED")}')
    for c in ('(1)', '(2)', '(3)', '(5)', '(6)'):
        out.append(f'- failing check {c}: {sum(1 for r in withs if any(f.startswith(c) for f in r["fails"]))}')
    out.append(f'- check (4) label keys: kit screens use literal English strings; mods calling Translate(): {sum(1 for r in withs if r.get("translate_uses"))} (no translation keys required by the kit)')
    out.append(f'- check (5) pairs compared (field initialiser vs Scribe default): {sum(r.get("defaults_checked",0) for r in withs)}')
    out.append('\n## Failures\n\n| mod | csproj | failures |\n|---|---|---|')
    for r in withs:
        if r['fails']: out.append(f'| {r["mod"]} | {r["csproj"]} | {" ; ".join(r["fails"])} |')
    out.append('\n## All mods with settings\n\n| mod | status | kit | masters | defaults pairs | notes |\n|---|---|---|---|---|---|')
    for r in withs: out.append(f'| {r["mod"]} | {r["status"]} | {r["kit"]} | {r.get("masters","-")} | {r.get("defaults_checked",0)} | {"; ".join(r["notes"])} |')
    # sanity probe
    probe = [r for r in withs if r['mod'].endswith('ShipMemory')]
    out.append(f'\n## Sanity probe\n\nShipMemory (known to have a SettingsKit screen) found: {bool(probe) and probe[0]["kit"]}')
    txt = '\n'.join(out) + '\n'
    if a.out: open(a.out, 'w').write(txt)
    else: print(txt)
    if not (probe and probe[0]['kit']): print('SANITY PROBE FAILED', file=sys.stderr); return 2
    return 0
if __name__ == '__main__': sys.exit(main())
