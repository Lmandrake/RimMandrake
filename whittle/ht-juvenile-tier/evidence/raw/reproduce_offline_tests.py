"""Execute preserved compiled L0 production-adapter/kernel controls, no build or game. Supply installed Windows dotnet.exe."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--dotnet',required=True)
a=ap.parse_args()
folder=Path(__file__).resolve().parent/'offline-test-bin'
manifest=json.loads((folder/'inputs.json').read_text())
for name,digest in manifest['files'].items():
    assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest,name
path=subprocess.check_output(['wslpath','-w',str(folder/'JuvenileTier.dll')],text=True).strip()
p=subprocess.run([a.dotnet,path],capture_output=True)
sys.stdout.write(p.stdout.decode('ascii'));sys.stderr.write(p.stderr.decode('ascii'))
sys.exit(p.returncode)
