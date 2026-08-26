import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    st = rb.call('rimbridge/get_bridge_status', {})
    print('STATUS', json.dumps({k: v for k, v in st.items() if k != 'operation'})[:500])
    info = rb.call('jawa/world_info_get', {})
    print('INFO', json.dumps({k: v for k, v in info.items() if k != 'operation'})[:500])
