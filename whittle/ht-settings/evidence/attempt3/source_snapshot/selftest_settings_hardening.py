"""Focused offline controls for settings load oracle and hostile XML coverage.
No bridge or game writes. Can-fail checks guard missing keys, nonfinite/out of
range reads and valid tuning changed to defaults. This is not Scribe evidence.
"""
from pathlib import Path
import re
from settings_hardening_live import SPEC,INTS,fixture_values,expected,check_values,format_ui_number,f32

def main():
 source=(Path(__file__).resolve().parents[1]/'Source/RM_HugeThingsSettings.cs').read_text()
 numeric=set(re.findall(r'public static (?:float|int|double) (\w+)\s*=',source))
 assert numeric==set(SPEC),(numeric^set(SPEC))
 scribed=set(re.findall(r'Scribe_Values.Look\(ref (\w+),',source))
 assert numeric<=scribed
 hostile=fixture_values('adversarial');assert set(hostile)==numeric
 assert {'NaN','Infinity','-Infinity','-5','0','99999'}<=set(hostile.values())
 good=expected(hostile);assert not check_values(good,good)
 for name in SPEC:
  missing=dict(good);missing.pop(name);assert name in check_values(missing,good)
  for bad in ('NaN','Infinity',SPEC[name][0]-1,SPEC[name][1]+1):
   broken=dict(good);broken[name]=bad;assert name in check_values(broken,good)
 valid=fixture_values('valid');assert not check_values(valid,expected(valid))
 for k,v in valid.items():assert float(v)==float(expected(valid)[k])
 assert good['titanEventWarningHours']==2 and float(valid['titanEventWarningHours'])==6
 assert [float(hostile[k]) for k in ('tierT1MinBodySize','tierT2MinBodySize','tierT3MinBodySize')]==[30,2,3]
 # Observed native Mono midpoint behavior must not use Python ties-to-even.
 assert format_ui_number(.25,'"0.0"')=='0.3'
 assert format_ui_number(.35,'"0.0"')=='0.4'
 assert format_ui_number(1.25,'"0.0"')=='1.3'
 assert format_ui_number(2.5,'"0"')=='3'
 assert format_ui_number(1.5,'"0.00"')=='1.50'
 assert format_ui_number(66.67,'"0"')=='67'
 assert format_ui_number(f32(f32(.145)*f32(100)),'"0"')=='15'
 assert format_ui_number(f32(f32(.6667)*f32(100)),'"0"')=='67'
 assert format_ui_number(f32(f32(.42)*f32(100)),'"0"')=='42'
 import xml.etree.ElementTree as ET
 keyed={e.tag:e.text or '' for e in ET.parse(Path(__file__).resolve().parents[1]/'Languages/English/Keyed/RM_HugeThings.xml').getroot()}
 keys=set(re.findall(r'"(RM_HugeThings_\w+)"\.Translate\(',source))
 assert keys<=set(keyed),keys-set(keyed)
 assert all(keyed[k].strip() and 'RM_HugeThings_' not in keyed[k] for k in keys)
 assert 'Trunk hits damage the plant' in keyed['RM_HugeThings_PlantTrunkDamage']
 assert 'no wake damage' in keyed['RM_HugeThings_Wake_Desc']
 assert 'per footprint cell' in keyed['RM_HugeThings_WakeRubble']
 assert 'GetSettings<RM_HugeThingsSettings>()' in source
 assert 'Scribe.mode == LoadSaveMode.PostLoadInit || Scribe.mode == LoadSaveMode.LoadingVars' in source
 assert 'Scribe_Values.Look(ref titanEventWarningHours, "titanEventWarningHours", 2f);' in source
 print('PASS settings oracle: 27 fields; 135 negative read controls; all hostile categories; valid tuning; warning default/source Scribe wiring')
if __name__=='__main__':main()
