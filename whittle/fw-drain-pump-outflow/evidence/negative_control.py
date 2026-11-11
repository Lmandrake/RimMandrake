from pathlib import Path
import hashlib,json,time,sys
root=Path.cwd();e=root/'whittle/fw-drain-pump-outflow/evidence'
p=root/'src/RimMandrake/FlowWorks/Source/LiquidTypes/Building_LiquidPump.cs'
backup=e/'Building_LiquidPump.fixed.cs.txt'
if sys.argv[1]=='prepare':
    assert not backup.exists()
    backup.write_bytes(p.read_bytes())
    s=p.read_text()
    old='usedOutflows.Add(oi);   // source is eligible; this end has too little room this cycle'
    assert s.count(old)==1
    p.write_text(s.replace(old,'// NEGATIVE CONTROL: do not retire the room-short outlet'))
    import subprocess
    (e/'outlet_retirement_negative.patch').write_bytes(subprocess.check_output(['git','diff','--','src/RimMandrake/FlowWorks/Source/LiquidTypes/Building_LiquidPump.cs']))
    record=dict(time=time.time(),purpose='Remove only room-short outlet retirement; source eligibility repair remains installed',fixed_sha256=hashlib.sha256(backup.read_bytes()).hexdigest(),mutant_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (e/'negative_control_input.json').write_text(json.dumps(record,indent=2)+'\n')
else:
    assert sys.argv[1]=='restore' and backup.is_file()
    record=json.loads((e/'negative_control_input.json').read_text())
    assert hashlib.sha256(p.read_bytes()).hexdigest()==record['mutant_sha256']
    p.write_bytes(backup.read_bytes())
    record.update(restored=time.time(),restored_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    assert record['restored_sha256']==record['fixed_sha256']
    (e/'negative_control_restore.json').write_text(json.dumps(record,indent=2)+'\n')
