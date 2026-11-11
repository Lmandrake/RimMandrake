"""Steam creation lag is not a game exit; use the declared process-start budget."""
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from northstar_driver import live_session as L

class Clock:
    def __init__(self): self.t=0
    def now(self): return self.t
    def sleep(self,n): self.t+=n

c=Clock()
with patch.object(L,'running',side_effect=lambda:c.t>=45):
    assert L.wait_for_process(180,c.now,c.sleep)
    assert c.t==45, c.t
print('PASS Steam may create its process after the old 20-second abort')
c=Clock()
with patch.object(L,'running',return_value=False):
    assert not L.wait_for_process(7,c.now,c.sleep)
    assert c.t==7, c.t
print('PASS process creation wait stops at its absolute budget')
c=Clock()
with patch.object(L,'running',return_value=True):
    assert L.wait_for_process(180,c.now,c.sleep)
    assert c.t==0
print('PASS an already-created process is immediately ready for the bridge wait')
