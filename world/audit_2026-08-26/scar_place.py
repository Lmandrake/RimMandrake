# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
r=b.call('jawa/world_landmarks_set',{'action':'add','def':'TerraformingScar','tiles':'17126','checkValid':True})
print("added=%s  errors=%s"%(r.get('added'), r.get('errors')))
row=(r.get('tiles') or [{}])[0]
print("read-back: landmark=%r name=%r mutators=%s"%(row.get('landmark'), row.get('landmarkName'),
      [x['def'] for x in row.get('mutators',[])]))
print("commit:", b.call('jawa/world_commit',{}).get('success'))
# independent re-read after commit
m=b.call('jawa/world_mutators_get',{'tiles':'17126','limit':2})
row2=(m.get('tiles') or [{}])[0]
print("re-read : landmark=%r name=%r mutators=%s"%(row2.get('landmark'), row2.get('landmarkName'),
      [x['def'] for x in row2.get('mutators',[])]))
