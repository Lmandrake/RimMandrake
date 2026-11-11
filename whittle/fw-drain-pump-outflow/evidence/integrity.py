"""Content identity of relevant production, tests, shared math and build/runner inputs."""
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[3]

def hashes():
    files = list((root / 'src/RimMandrake/FlowWorks/Source').rglob('*.cs'))
    files += list((root / 'src/RimMandrake/_Shared').rglob('*.cs'))
    files += list((root / 'src/RimMandrake/FlowWorks/Source/SelfTest').glob('*.targets'))
    files += [root / rel for rel in (
        'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj',
        'src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj',
        'src/RimMandrake/FlowWorks/northstar/pump_outflow_live.py',
        'src/RimMandrake/Utils/run_selftests.py',
        'src/RimMandrake/Utils/selftest_flowworks_stock.py',
        'src/RimMandrake/Utils/selftest_winstage.py',
        'src/RimMandrake/Utils/winbuild.py',
        'src/Directory.Build.targets', 'src/Directory.Build.props',
        'whittle/fw-drain-selftest-resume/evidence/reference/RimWorld/Pawn_NeedsTracker.cs')]
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files)) if 'obj' not in p.parts and 'bin' not in p.parts}
