import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call('jawa/clear_ui', {})
    r = rb.call('rimworld/frame_cell_rect', {'x': 30, 'z': 24, 'width': 74, 'height': 32})
    s = rb.call('rimworld/take_screenshot', {})
    print('shot:', s.get('path'))
