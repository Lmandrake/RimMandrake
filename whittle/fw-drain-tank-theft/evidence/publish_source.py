"""Publish only the reviewed, measured explicit source/artifact paths."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
inputs = json.loads((here/'publish_inputs.json').read_text())
for name,digest in inputs['sha256'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
message = 'Fix foreign tank theft actor attribution\n\nAttribute actual tank mutations with rollback and persistence coverage.\nCo-Authored-By: Codex (GPT) via WSL codex-cli'
sys.exit(subprocess.run(['./publish','-m',message,*inputs['paths']],cwd=root).returncode)
