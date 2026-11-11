"""New localized production artifact; inherit the actual build/deploy generation."""
from session_control import *
import shutil
g=json.loads((E/'attempt4_guard_taken.stdout').read_text())
ENV['RM_DRIVER_PID']=str(g['identity']['pid']);ENV['RM_HOST_GUARD_GEN']=str(g['generation'])
guard('attempt4_guard_before_live')
assert (E/'localization_deploy_apply.rc').read_text().strip()=='0'
assert (E/'pilot_localization/broaden_call.json').exists(),'fourth attempt requires independent pilot diagnosis'
assert json.loads((E/'pilot_localization/broaden_call.json').read_text())['returncode']==0
new=E/'attempt4';new.mkdir(exist_ok=False)
for name in ['original_settings_inventory.json','native_saved_Mod_HugeThings_RM_HugeThingsMod.xml','baseline_live.json']:
 shutil.copyfile(E/name,new/name)
shutil.copytree(E/'steam_adapter',new/'steam_adapter')
snap=new/'source_snapshot';snap.mkdir()
for name in ['settings_hardening_live.py','selftest_settings_hardening.py']:
 shutil.copyfile(ROOT/'src/RimMandrake/HugeThings/northstar'/name,snap/name)
ENV['HT_SETTINGS_EVIDENCE']=str(new)
p=run('attempt4_driver',['python3',str(E/'run_live.py')],require=False,timeout=2200)
assert p.returncode==0,'attempt4 failed; raw evidence and cleanup retained'
