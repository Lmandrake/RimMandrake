"""Launch a single isolated exam process, retain raw output, and charge actual usage."""
import json
import fcntl
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/home/mandrake/rm/bench')
FOLDER = ROOT / 'design/concepts/LeaningScrub'
RUN = FOLDER / 'exam_runs/rm-role-designercodex-1794843033'
sys.path.insert(0, str(ROOT / 'src/RimMandrake/rimflow'))
from role_launch import run_tokens

role = sys.argv[1]
source = FOLDER / 'exam_control' if role == 'control' else FOLDER
common = ('You are an independent acceptance-contract evaluator. Use only the documents supplied in this prompt. '
          'No tools, filesystem reads, memories, outside context, helpers or modifications. '
          'Evaluate what the contract promises, not current implementation status. '
          'A scenario submits the specified behavior for acceptance of its named/local claim, not proof of every unrelated feature. '
          'Judge from explicit contract requirements; do not invent additional rules. Return one JSON object only. ')
if role == 'examiner':
    task = ('Act as the fresh Examiner. Write exactly 12 distinct concrete play situations: at least 6 rejects '
            'probing core promises, plus accepts. Cover the six current root families broadly, including sweetline '
            'healing, ordered travel, native wild-plant generation, and current versus deferred scope. '
            'Include a raid_weight case isolating that leaf\'s rule, with other obligations satisfied; '
            'this is for an ablation test. Each case needs a neutral factual text and a specific submitted claim, '
            'without disclosing the verdict or citing a leaf in the text. Expected verdict must follow the '
            'supplied contract, with leaf:<id> as its source. Do not rely on absent plans/scenes. '
            'Output {"scenarios":[{"id":"exam_descriptive_id","text":"...",'
            '"expect":"accept: reason OR reject: reason","expect_source":"leaf:id","by":"examiner"}]}. '
            'Read all supplied leaves before selecting cases. Keep each case compact, under 150 words.')
elif role == 'challenger':
    task = ('Act as the fresh Challenger. Independently write exactly 6 concrete adversarial play situations '
            'likely to trick a cold reader into accepting behavior that a core contract rejects. '
            'Vary the leaves; include at least one raid_weight case where a non-raid worker receives the Gale '
            'multiplier while the enemy-raid multiplier, on/off and weather gating all work and no incident '
            'is scheduled. Other cases should test subtle promised behavior. '
            'Do not invent scope or require absent plans/scenes. Neutral factual scenario text should not reveal '
            'the expected answer or source leaf. Output '
            '{"scenarios":[{"id":"challenge_descriptive_id","text":"...",'
            '"expect":"reject: grounded reason","expect_source":"leaf:id","by":"challenger"}]}. '
            'Read all supplied leaves; keep each case under 150 words.')
else:
    task = ('For every supplied scenario independently decide accept or reject, citing the leaf(s) relied on '
            'and a concise reason. Only reject for a rule in your supplied contract; behavior unspecified by '
            'that contract is acceptable for the submitted local claim. Absence of unrelated tests is not '
            'evidence that their feature failed. Do not guess missing requirements. '
            'Output {"verdicts":[{"id":"scenario id","verdict":"accept or reject",'
            '"leaf":"id or unspecified","reason":"concise reason"}]}. No role declaration.')
prompt = common + task + '\n<SHEET>\n' + (source/'sheet.md').read_text() + '\n</SHEET>\n<TREE>\n'
prompt += json.dumps(json.loads((source/'tree.json').read_text()), ensure_ascii=False, separators=(',', ':')) + '\n</TREE>\n'
if role not in ('examiner', 'challenger'):
    prompt += '<SCENARIOS>\n' + (RUN/'scenarios_text.json').read_text() + '\n</SCENARIOS>\n'
(RUN/(role+'_brief.txt')).write_text(prompt)
env = dict(os.environ)
env.pop('CLAUDE_SCOPE_UNIT', None)
env.pop('CLAUDE_SCOPE_RUNTIME_MAX', None)
cmd = [str(ROOT/'src/RimMandrake/Utils/claude_bounded.sh'), '-p', '--model', 'opus',
       '--output-format', 'json', '--safe-mode', '--tools', '', '--strict-mcp-config',
       '--system-prompt', 'Evaluate only the supplied acceptance contract. Return the requested JSON. No tools.', prompt]
with (RUN/(role+'_raw.json')).open('w') as out, (RUN/(role+'_stderr.txt')).open('w') as err:
    completed = subprocess.run(cmd, cwd=ROOT, env=env, stdout=out, stderr=err)
raw = json.loads((RUN/(role+'_raw.json')).read_text())
tokens = run_tokens(raw)
if tokens is None:
    raise RuntimeError('Helper usage unmeasured; preserve output for investigation')
with (RUN/'charge.lock').open('w') as charge_lock:
    fcntl.flock(charge_lock, fcntl.LOCK_EX)
    charge = subprocess.run([sys.executable, str(ROOT/'src/RimMandrake/rimflow/designer_stage.py'),
                             'charge', str(FOLDER), '--tokens', str(tokens), '--kind', 'helper',
                             '--ref', raw['session_id']], cwd=ROOT, capture_output=True, text=True)
(RUN/(role+'_charge.json')).write_text(json.dumps({'agent':raw['session_id'], 'weighted_tokens':tokens,
    'charge_exit':charge.returncode, 'stdout':charge.stdout, 'stderr':charge.stderr}, indent=2)+'\n')
if charge.returncode:
    raise RuntimeError('Charge failed: '+charge.stderr)
if completed.returncode or raw.get('is_error'):
    raise RuntimeError('Helper failed; usage charged')
result = raw.get('structured_output') or raw.get('result')
if isinstance(result,str):
    result = result.strip()
    if result.startswith('```'):
        result = result.split('\n',1)[1].rsplit('```',1)[0]
    result = json.loads(result)
(RUN/(role+'_parsed.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'helper':role,'session_id':raw['session_id'],'weighted_tokens':tokens,
                  'count':len(result.get('scenarios',result.get('verdicts',[])))}))
