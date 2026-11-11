"""Derive tier-only census subsets from raw C# calls. No map/passage eligibility claim."""
from pathlib import Path
import hashlib,json,math,sys
path=Path(sys.argv[1]);d=json.loads(path.read_text());races={}
for row in d['resolved_kind_census']:
    races.setdefault(row['race'],row)
valid_juveniles=[]
for race,row in sorted(races.items()):
    try:factors=[float(x.split(':',1)[1]) for x in row['stages'].split(',')]
    except (ValueError,IndexError):continue
    if factors and all(math.isfinite(x) and 0<x<1 for x in factors):
        valid_juveniles.append(row)
result={'input':str(path),'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'mode':'resolved kind/race tier census on selected minimal tier; no map eligibility or passage claim',
        'kind_count':len(d['resolved_kind_census']),'unique_race_count':len(races),
        'complete_positive_below_one_stage_races':valid_juveniles,
        'lineage_eligible_below_supported_T2':[r for r in valid_juveniles if int(r['AdultTier'])>=2 and int(r['SpacingTier'])<2],
        'lineage_T3_below_supported_T3':[r for r in valid_juveniles if int(r['AdultTier'])==3 and int(r['SpacingTier'])<3]}
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:len(value) if isinstance(value,list) else value for key,value in result.items() if key not in ['input_sha256']}))
