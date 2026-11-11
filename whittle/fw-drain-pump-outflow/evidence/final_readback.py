"""Fresh read-only identity/readback after real proof; no suite rerun or status rewriting."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(name):
    return json.loads((here / name).read_text())

test = read('final-live-fixture/selftest_receipt.json')
assert test['returncode'] == 0 and test['source_test_hashes_unchanged']
changed = [rel for rel, digest in test['sha256_after'].items() if sha(root / rel) != digest]
assert not changed, changed
source = root / 'src/RimMandrake/FlowWorks/Source'
dll = root / 'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'
stamp = Path(str(dll) + '.srchash')
lines = stamp.read_text().splitlines()
assert '# dll: ' + sha(dll) in lines, 'DLL stamp pair mismatch'
stamp_mismatch = []
for line in lines:
    if line.startswith('#') or not line.strip():
        continue
    digest, rel = line.split(' ', 1)
    if sha(source / rel) != digest:
        stamp_mismatch.append(rel)
assert not stamp_mismatch, stamp_mismatch
publish = (here / 'publish_driver_stdout.txt').read_text()
shas = re.findall(r'PUBLISHED ([0-9a-f]{40})', publish)
assert shas, 'no exact PUBLISHED SHA'
published = shas[-1]
subprocess.run(['git', 'merge-base', '--is-ancestor', published, 'origin/main'], cwd=root, check=True)
deployed = Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/FlowWorks/Assemblies')
assert sha(deployed / dll.name) == sha(dll) and sha(deployed / stamp.name) == sha(stamp)
scene = read('live-attempt2/live_scene.json')
drive = read('live-attempt2/live_drive.json')
assert scene['status'] == drive['status'] == 'PASS' and drive['both_locks_free']
assert scene['identity']['mvidMatchesFile'] and scene['identity']['assemblyFileSha256'] == sha(dll)
assert scene['restore']['status'] == 'PASS' and scene['restore']['rect'] == scene['baseline_rect']
assert not scene['changed_existing_saves'] and scene['protected_before'] == scene['protected_after']
assembly = Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll')
assert sha(assembly) == read('reference_provenance.json')['assembly_sha256']
record = dict(time=time.time(), published_sha=published, published_is_ancestor_of_origin_main=True,
    source_inputs_unchanged_from_final_suite=True, checked_inputs=len(test['sha256_after']),
    production_source_sha256=sha(source / 'LiquidTypes/Building_LiquidPump.cs'),
    dll_sha256=sha(dll), stamp_sha256=sha(stamp), stamp_sources_match=True, deployed_pair_matches=True,
    loaded_mvid_and_file_identity=scene['identity'],
    final_suite=read('final-live-fixture/output_extraction.json'),
    shipping_build=read('shipping_build_command.json'),
    arms=scene['arms'], actual_order=scene['actual_order'], restoration=scene['restore'],
    protected_save_hashes=scene['protected_after'], changed_existing_saves=scene['changed_existing_saves'],
    live_drive_status=drive['status'], game=(here / 'postjudge_game_stdout.txt').read_text(),
    locks=(here / 'postjudge_locks_stdout.txt').read_text(),
    loaded_log=read('live-attempt2/log_loaded.json'), final_log=read('live-attempt2/log_after_scene.json'),
    windows_stage=read('final-live-fixture_stage.json'),
    reference_assembly_sha256=sha(assembly),
    limits=['Paused single-level production TryDraw hook bypasses hash scheduling; power is the vanilla DEV fixture.',
            'Hose storage and gravity levelling disabled/restored for destination-delta isolation; hose-fill/rollback paths use complete production methods with explicit offline engine doubles.',
            'Not full-list integration, multi-pump timing, or a new guarantee for pre-existing cross-contact outlet failures or exact-off partial tank rounding.'])
saves = Path('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves')
record['protected_save_hashes_read_now'] = {name: sha(saves / name) for name in scene['protected_after']}
assert record['protected_save_hashes_read_now'] == scene['protected_after']
# Keep the whole Windows build provenance locally; its _token is a non-auth close-evidence marker.
(here / (sys.argv[1] if len(sys.argv) > 1 else 'final_readback.json')).write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: record[k] for k in ('published_sha', 'checked_inputs', 'dll_sha256', 'source_inputs_unchanged_from_final_suite', 'live_drive_status', 'game', 'locks')}, indent=2))
