"""Class each pipeline commit subject since 2026-11-13 by one ordered pattern list (first match wins).
Usage: python3 classify_subjects.py [class ...]  (a class name prints a random sample of it). Read-only."""
import re,sys,collections,random
import subprocess
# The counts in review.md are of the log as it was on 2026-11-21 01:10 PST (967 commits); a later run counts more.
rows=[l.split('|',2) for l in subprocess.run(['git','log','--since=2026-11-13','--no-merges','--format=%h|%ad|%s','--date=short','--','src/RimMandrake/rimflow','.claude/hooks','src/RimMandrake/Utils'],capture_output=True,text=True,check=True).stdout.splitlines()]
# ordered: first match wins. NOT-REPAIR classes first.
C=[
('x_mod_work', r'^(GSS|Graffiti|FlowWorks|Pyrelands|GimmeSomeSlack|EK |Water reads|Vanilla rain|Tribes|Three rules of the lay|settings screens|Contagion|RimFridge|game health|tps-|jawa/|steve|soak|bridge companion|harness: scene)|\b(0\.1\.[01]|Stage 3:)'),
('x_owner_setting', r'(switching[_ ]plan|leave line|max_live|hard context limit|Clone pool disk line|Account switch drains).*(owner|his word|->|exception)|^switching plan:'),
('x_era_removal', r'(era split|retired era|Relentless|relentless|Whittle|pulse package|FOUNDRY|Ralph-loop|rimflow v3|HISTORY head|Era gate)'),
('j_rule_text', r'^(rule|rules|rulings|docs|CLAUDE\.md|roles|briefs|Five-acts|The Conductor.s act|Only five acts|Spec and Conductor role|plain-English|Plain-English|crystallize|owner rulings|conductor\.md|operations\.md|agent files|designer_exam\.md|Conductor files)\b|ruling text|\bbrief(s)? (carry|carries|states|agrees|line)|holder brief|chain brief|role files? (no longer|stop)|his 20\d\d-\d\d-\d\d ruling'),
('i_test_reaches_live', r'^selftest[s_]|^(boundary_check_accept|preflight_spine_accept)|(selftest|fixture|test).*(live one|its own|own temp|temp root|pinned|pin the fixture|fakes|stand-in|stub|never read the live|flake|race|was wrong|stale)|TEST was wrong|test was wrong'),
('m_could_not_look', r'UNMEASURED|could-not-look|could not look|unreadable|Unreadable|probe[_ ]result|blind(s|ed)?\b(?! (judge|cycle|exit|boundary|challenge|role|reader|reread))|is unknown, never|UNKNOWN, never|not a measured 0|not 0\b|EMPTY not|never "finds no event"|bare None|reads dead'),
('c_not_charged', r'void_system|\bvoid\b|never charged|not a spent|spends nothing|no strike|no retry, no rejection|is no fault|not a stall|planned hold|not a failed run|charge 0|killed (started )?run|launch_failed|never started|counts only|counted once|count(s)? .*once|not judged as|not Designer rework|is not a hand act|not hand acts'),
('a_refuse_to_repair', r'never refused|not refused|never refuse|is repaired|fitted|keeps every name valid|refus\w+ .*(names|prints the exact|carries|ends stdout)|was refused all night|refused .* (3x|three times)|admits|is not linted|no longer refuses|refuses the full run only|is not a note|is no background command'),
('d_hand_recovery', r'tick (takes|launches|files|lifts)|itself|by the next (plan )?pass|is resumed|is continued|steward|lift once|un-parks|goes first|road[- ]back|owed (run|items)|hand step|by hand|re-gates|retried|retries|carried on|continu'),
('l_default_target', r"game b|game:a|its own install|own bridge|--host|own clone|not the Dispatcher's|the game it drives|far clone|wrong login|names its game|RM_GAME_INSTANCE|own env|Windows PATH|WSL_INTEROP|under win32|on a Mac|seat clone|TMPDIR of their own"),
('f_two_copies', r'one source|its mirror|mirror\b|agrees with|reads? .* from stage\.json|drift|stale (week )?drop-in|one store|one writer|the one control store|single source|projection|reads the control store|read the control store|repointed|one list|one fit rule|one retry rule|twin\b'),
('g_identity_inferred', r'keyed by|keys .* by|attributed by|its launch recorded|names its unit|carries its visit word|run id per|as parent|anchor .* to the commit|name per writer|exact item-id match|landed twin|by line\+name'),
('e_whole_artifact_validity', r're-?pin|stale|only (what|the) .*touched|re-run only|retake|restamp|certificate|build[_ ]match|calibration row|changed after its run|input_changes'),
('h_limit', r'timeout|deadline|\bcap(s|ped)?\b|limit|ceiling|budget|allowance|within its wait|bounded|\b\d+ ?s\b.*(default|measured)'),
]
C=[(n,re.compile(p)) for n,p in C]
out=collections.defaultdict(list)
for sha,d,s in rows:
    for n,p in C:
        if p.search(s): out[n].append((sha,d,s)); break
    else: out['z_unclassed'].append((sha,d,s))
tot=len(rows)
for n in sorted(out): print(f'{n:28s} {len(out[n]):4d}')
print('total',tot)
if len(sys.argv)>1:
    random.seed(7)
    for n in sys.argv[1:]:
        k=out[n]; print('==',n,len(k))
        for sha,d,s in random.sample(k,min(22,len(k))): print(' ',sha,s[:112])
