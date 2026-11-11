"""Substantive offline readback of final proof, current inputs, deployment and stopped ownership."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/restring-live-raw')
sys.path[:0] = [str(ROOT / 'src/RimMandrake/Utils'), str(ROOT / 'src/RimMandrake')]
import game_paths as GP
import game_instance
from modcheck import status
from rimflow import driver_lock
from GimmeSomeSlack import restring_style_proof
import mod_completion
from inspect_result import inspect


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(label):
    out = HERE / ('readback_' + label + '.json')
    assert not out.exists(), 'Preserve all readbacks'
    manifest = json.loads((HERE / 'live_inputs_before3.json').read_text())
    current = {name: sha(ROOT / name) for name in manifest['files']}
    changed = [name for name in current if current[name] != manifest['files'][name]]
    assert not changed, changed
    guard_path = RAW / 'attempt3_guard.json'
    guard = json.loads(guard_path.read_text())
    session = json.loads((HERE / 'attempt3_session.json').read_text())
    proof = ROOT / 'src/RimMandrake/GimmeSomeSlack/northstar/fw-drain-restring-live/attempt3/aerial.json'
    raw_proof = RAW / 'attempt3/a1-cf6t5111/aerial.json'
    receipt_path = raw_proof.parent / 'receipt.json'
    receipt = json.loads(receipt_path.read_text())
    aerial = json.loads(proof.read_text())
    extra_assertions = inspect(proof)
    assert proof.read_bytes() == raw_proof.read_bytes()
    restring_style_proof.check_result(raw_proof, receipt['started'], receipt['finished'])
    assert receipt['driverReturncode'] == receipt['returncode'] == 0
    assert session['status'] == guard['status'] == 'PASS'
    assert session['bridge_and_host_free'] and not session.get('cleanup_errors')
    assert guard['baseline'] == guard['restored_scene'] and not guard['cleanup_errors']
    assert not guard['changed_existing_saves'] and guard['config_before'] == guard['config_after']
    assert guard['debug_before'] == guard['debug_after']
    assert guard['begin_sha256'] == guard['begin_sha256_before_restore']
    for name, digest in guard['script_hashes'].items():
        assert sha(ROOT / name.replace('\\', '/')) == digest, name
    assert all(row['status'] == 'PASS' for row in aerial['rows'])
    assert aerial['env']['running'] == manifest['mods']
    mod_hash = status.mod_hash(str(ROOT / 'src/RimMandrake/GimmeSomeSlack'))
    assert mod_hash == aerial['mod_hash'], (mod_hash, aerial['mod_hash'])
    pairs = {}
    for mod, dll in [('GimmeSomeSlack', 'RimMandrakeGimmeSomeSlack.dll'),
                     ('FlowWorks', 'RimMandrakeFlowWorks.dll'), ('HugeThings', 'RM_HugeThings.dll')]:
        repo = ROOT / 'src/RimMandrake' / mod / 'Assemblies' / dll
        deployed = Path(GP.LOCAL_MODS) / mod / 'Assemblies' / dll
        assert repo.read_bytes() == deployed.read_bytes()
        stamp = repo.with_suffix('.dll.srchash')
        assert stamp.read_bytes() == deployed.with_suffix('.dll.srchash').read_bytes()
        lines = stamp.read_text().splitlines()
        project = ROOT / 'src' / lines[0].split(':', 1)[1].strip()
        compile_inputs = {}
        for line in lines:
            if line and not line.startswith('#'):
                digest, name = line.split(' ', 1)
                source = (project.parent / name.strip()).resolve()
                assert sha(source) == digest, str(source)
                compile_inputs[str(source.relative_to(ROOT))] = digest
        assert '# dll: ' + sha(repo) in lines
        pairs[mod] = dict(dll_sha256=sha(repo), stamp_sha256=sha(stamp), compile_inputs=compile_inputs)
    assert guard['identity']['assemblyFileSha256'] == pairs['GimmeSomeSlack']['dll_sha256']
    assert guard['identity']['mvidMatchesFile'] is True
    completion_path = HERE / 'completion_after.json'
    completion = json.loads(completion_path.read_text())[0]
    entry, = [e for e in completion['works']['entries'] if e['defName'] == 'RM_RestringSpan']
    assert entry['status'] == 'works' and entry['n_pass'] == 2 and entry['n_fail'] == 0, entry
    discovered, = [run for run in mod_completion.proof_runs('GimmeSomeSlack', set())
                   if Path(run['path']).resolve() == proof.resolve()]
    assert discovered['level'] == 'L2' and discovered['script'] == 'validation_aerial.py'
    for row_id in ('M15e_restring_is_a_colonist_job', 'M15f_restring_joined_run_one_look'):
        row, = [row for row in discovered['rows'] if row['id'] == row_id]
        assert row['status'] == 'PASS' and row['class'] == 'MOD' and 'RM_RestringSpan' in row['text']
    current_saves = {name: sha(Path(GP.SAVES) / name) for name in guard['saves_before']}
    assert current_saves == guard['saves_before'], 'existing save changed after shutdown'
    assert sha(Path(GP.SAVES) / (guard['snapshot']['path'].replace('\\', '/').rsplit('/', 1)[-1])) == guard['begin_sha256']
    saves_receipt = RAW / ('saves_after_stop_' + label + '.json')
    assert not saves_receipt.exists()
    saves_receipt.write_text(json.dumps(dict(time=time.time(), hashes=current_saves), indent=2) + '\n')
    fixture = 'src/RimMandrake/GimmeSomeSlack/Source/SelfTest/ExplodeProbeChecks.cs'
    original = subprocess.check_output(['git', 'show', 'HEAD:' + fixture], cwd=ROOT).decode()
    assert original.splitlines()[1:] == (ROOT / fixture).read_text().splitlines()[2:], 'annotation changed executable fixture text'
    test_outputs = {}
    for leaf, expected in [('selftests_annotation.txt', 'PASS 2/2'), ('harness_final_green.txt', 'PASS 4/4')]:
        saved, raw = HERE / leaf, RAW / leaf
        assert saved.read_bytes() == raw.read_bytes()
        text = saved.read_text()
        assert expected in text and 'RESULT: GREEN' in text
        test_outputs[leaf] = dict(sha256=sha(saved), raw=str(raw), final_lines=text.splitlines()[-8:])
    call = json.loads((HERE / 'broaden2_call.json').read_text())
    broadener = json.loads((HERE / 'broaden2_raw.json').read_text())
    assert call['returncode'] == 0 and broadener['is_error'] is False and broadener['result']
    assert call['started'] < receipt['started']
    running = game_instance.running()
    host_lock = Path(driver_lock.lock_path())
    bridge = (ROOT / 'infrastructure/state/BRIDGE').read_text()
    bridge_states = [line.strip() for line in bridge.splitlines() if line.strip() and not line.startswith('#')]
    assert running is False and not host_lock.exists() and len(bridge_states) == 1 and bridge_states[0].startswith('FREE '), bridge
    result = dict(time=time.time(), head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  inputs=current, input_count=len(current), changed_inputs=changed, shipping=pairs,
                  live_mod_hash=mod_hash, proof=str(proof.relative_to(ROOT)), proof_sha256=sha(proof),
                  regression=test_outputs, extracted_csharp_fixture_change='comment only; executable text exactly equal to HEAD',
                  broaden=dict(call_sha256=sha(HERE / 'broaden2_call.json'), raw_sha256=sha(HERE / 'broaden2_raw.json'),
                               models=list(broadener['modelUsage']), fresh_transport=call['history']),
                  extra_live_assertions=extra_assertions, completion=dict(entry=entry, report_sha256=sha(completion_path),
                                                                         discovered_path=discovered['path'], level=discovered['level']),
                  raw_guard=str(guard_path), raw_guard_sha256=sha(guard_path), raw_receipt=str(receipt_path),
                  raw_receipt_sha256=sha(receipt_path), row_count=len(aerial['rows']),
                  identity=guard['identity'], mods=manifest['mods'],
                  restoration=dict(exact_scene=True, exact_debug=True, exact_settings=True, exact_gss_config=True,
                                   original_save_count=len(guard['saves_before']), changed_existing_saves=[],
                                   guarded_begin_sha256=guard['begin_sha256'],
                                   post_shutdown_save_readback=str(saves_receipt), post_shutdown_save_readback_sha256=sha(saves_receipt),
                                   before_tick=guard['baseline']['tick'], after_proof_tick=guard['after_proof_tick'],
                                   restored_tick=guard['restored_scene']['tick']),
                  cleanup=dict(game_running=running, driver_lock_path=str(host_lock), driver_lock_exists=False,
                               bridge=bridge, supported_stop_and_release=session['commands'][-5:]))
    out.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS', len(current), 'current inputs;', len(aerial['rows']), 'MOD/site rows; all shipping pairs; exact restoration; DOWN/FREE/FREE')


if __name__ == '__main__':
    main(sys.argv[1])
