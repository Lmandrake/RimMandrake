"""Use the repository's Steam lifecycle implementation; no bare executable launch."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'src/RimMandrake/Utils'))
from northstar_driver import live_session
action = sys.argv[1]
assert action in ('launch','stop')
live_session.launch_and_wait() if action == 'launch' else live_session.stop_game()
