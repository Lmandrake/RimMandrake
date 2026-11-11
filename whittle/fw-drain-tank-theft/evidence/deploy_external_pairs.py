"""Plan/apply only the published integration pairs at their catalogued shipping paths.

The full compose plan is preserved. Its unrelated art/biome drift is excluded.
Use the shipping deploy module's hold and copy routines; change no definitions.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
mirror = Path('/mnt/d/Luke/dev/RimMandrake')
game = Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods')
sys.path.insert(0, str(mirror / 'src/RimMandrake/Utils'))
import deploy_custom_mods as deploy
import biomes_compose

mode = sys.argv[1]
assert mode in ('plan', 'apply')
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

publication = json.loads((here / 'external_publication.json').read_text())
catalog = json.loads((here / 'external_catalog.json').read_text())
backup = json.loads((here / 'external_deployment_backup.json').read_text())
assert (mirror / 'MIRROR_HEAD').read_text().split()[0] == publication['sha']
subprocess.run(['git', 'merge-base', '--is-ancestor', publication['sha'], 'origin/main'], cwd=root, check=True)
full_plan = (here / 'deploy_external_plan_stdout.txt').read_text()
assert '2 target(s): clean' in full_plan
holds = deploy.load_holds()
manifest = biomes_compose.load_manifest(str(mirror / 'src'))
entry = next(e for e in biomes_compose.composed_entries(manifest) if e['source'] == 'Cauldron')
assert biomes_compose.folded_sources(str(mirror / 'src'))['Cauldron'] == ('RimMandrake.Biomes', 'Cauldron')
rows = []
for mod, pair in catalog['pairs'].items():
    source_dir = mirror / 'src/RimMandrake' / mod
    dest_dir = game / ('RimMandrake.Biomes' if mod == 'Cauldron' else mod)
    if mod == 'Cauldron':
        dest_dir /= biomes_compose.dest_rel(entry)
    dll = Path(pair['artifact']).name
    for suffix in ('', '.srchash'):
        rel = 'Assemblies/' + dll + suffix
        source = source_dir / rel
        target = dest_dir / rel
        repo = str(Path(pair['artifact']).relative_to(root)) + suffix
        expected = publication['inputs'][repo]
        assert sha(source) == sha(root / repo) == expected
        assert not deploy.hold_for(holds, mod + '/' + rel)
        assert not deploy.hold_for(holds, str(target.relative_to(game)))
        prior = backup['files'][str(target)]
        assert sha(prior['backup']) == prior['backup_sha256']
        assert sha(target) == prior['before_sha256']
        rows.append(dict(source=str(source), target=str(target), relative=rel,
                         source_dir=str(source_dir), dest_dir=str(dest_dir),
                         before_sha256=sha(target), published_sha256=expected))

# Preserve the deployed contents of every unrelated drift path in the full plan.
unrelated = {}
owner = None
selected = {row['target'] for row in rows}
for line in full_plan.splitlines():
    if line.startswith('RimMandrake.Biomes ') or line.startswith('LuminousPigment '):
        owner = line.split()[0]
    match = re.match(r'^    [~+\-]  (.*?)(?:   \(|$)', line)
    if owner and match:
        path = game / owner / match[1]
        if str(path) not in selected:
            unrelated[str(path)] = sha(path) if path.is_file() else None

plan = dict(time=time.time(), publication=publication['sha'], files=rows,
            full_plan_sha256=sha(here / 'deploy_external_plan_stdout.txt'),
            unrelated_drift_before_sha256=unrelated,
            scope='Four DLL/stamp files only; no definitions, art, settings shell, mod list or saves')
if mode == 'plan':
    target = here / 'deploy_external_pairs_plan.json'
    assert not target.exists()
    target.write_text(json.dumps(plan, indent=2) + '\n')
    print(json.dumps(plan, indent=2))
else:
    prior_plan = json.loads((here / 'deploy_external_pairs_plan.json').read_text())
    assert prior_plan['files'] == rows
    assert prior_plan['unrelated_drift_before_sha256'] == unrelated
    sys.path.insert(0, str(root / 'src/RimMandrake'))
    from rimflow import model
    assert model.read_shared_bridge()['holder'] == 'CODEX_ARCHMAGI_FWDRAIN'
    measurement = subprocess.check_output(['./game'], cwd=root, text=True)
    assert 'NOT RUNNING' in measurement
    for row in rows:
        copied, refused, failed = deploy.copy(row['source_dir'], row['dest_dir'], [row['relative']])
        assert copied == 1 and not refused and not failed, row
        assert sha(row['target']) == row['published_sha256']
    for path, expected in unrelated.items():
        assert (sha(path) if Path(path).is_file() else None) == expected, path
    target = here / 'external_deployment_readback.json'
    assert not target.exists()
    plan.update(status='PASS', applied_files=4, game_measurement=measurement,
                unrelated_drift_preserved=True, backups_retained=True)
    target.write_text(json.dumps(plan, indent=2) + '\n')
    print('PASS: four published integration files deployed and byte verified;', len(unrelated), 'unrelated drift paths unchanged')
