"""Retake only after prior cleanup; carry the generation the actual guard returns."""
from session_control import *
import shutil
# Second attempt must have completed DOWN and FREE, even though one UI number check failed.
assert (E/'attempt2/finally_guard.stdout').exists(),'attempt 2 cleanup not finished'
assert json.loads((E/'attempt2/finally_guard.stdout').read_text())['state']=='FREE'
g=json.loads(run('attempt3_guard_free',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
assert g['state']=='FREE'
# Original stable parent identity was independently verified by host_guard.status.
original=json.loads((E/'guard_initial.stdout').read_text())
run('attempt3_parent',['ps','-p',str(original['identity']['pid']),'-o','pid,ppid,lstart,args'])
ENV['RM_DRIVER_PID']=str(original['identity']['pid'])
run('attempt3_take',BRIDGE+['take','--host','stevedesktop','--idle-ok','--for','HT: HUGETHINGS_SETTINGS_HARDENING_1'])
g=json.loads(run('attempt3_guard_taken',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
assert g['state']=='HELD' and g['generation']>1397 and g['identity']==original['identity']
ENV['RM_HOST_GUARD_GEN']=str(g['generation'])
new=E/'attempt3';new.mkdir(exist_ok=False)
for name in ['original_settings_inventory.json','native_saved_Mod_HugeThings_RM_HugeThingsMod.xml','baseline_live.json']:
 shutil.copyfile(E/name,new/name)
shutil.copytree(E/'steam_adapter',new/'steam_adapter')
snap=new/'source_snapshot';snap.mkdir()
for name in ['settings_hardening_live.py','selftest_settings_hardening.py']:
 shutil.copyfile(ROOT/'src/RimMandrake/HugeThings/northstar'/name,snap/name)
ENV['HT_SETTINGS_EVIDENCE']=str(new)
p=run('attempt3_driver',['python3',str(E/'run_live.py')],require=False,timeout=2200)
# The nested runner owns all cleanup; prove the result even when it failed.
assert p.returncode==0,'attempt3 failed; preserved raw evidence'
