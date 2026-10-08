import sys,json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0,r'src\RimMandrake\Utils')
import rimbridge_client as rb
h,p,t=rb.resolve_endpoint();S=rb.RimBridge(host=h,port=p,token=t,timeout=60.0);S.connect()
l=S.list_tools()
l=l if isinstance(l,list) else l.get('tools',[])
for x in l:
    if x.get('name') in sys.argv[1:]:
        print(x['name'], '|', x.get('description','')[:350].replace('\n',' '), '|', json.dumps(x.get('inputSchema',{}).get('properties',{}))[:900]); print()
