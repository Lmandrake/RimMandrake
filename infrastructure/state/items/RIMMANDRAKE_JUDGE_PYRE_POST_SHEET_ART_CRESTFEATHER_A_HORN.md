# RIMMANDRAKE_JUDGE_PYRE_POST_SHEET_ART_CRESTFEATHER_A_HORN

## spec

Pyrelands 0.1.0 art and text shipped after his 2026-10-16 approval of the art sheet (OWNER:1792122659817386516) rest on
no judge: round-6 coverage gap g12 (rm-coverage-judge-1794750987; his card OWNER:1794774724955142310). Merged by the
ticket sweep of 2026-11-22 from RIMMANDRAKE_JUDGE_PYRELANDS_ART_ADDED_SINCE_HIS_SHEET and
RIMMANDRAKE_DRAW_CRESTFEATHER_OWN_ART_NOT_A_THRUMBO_HORN (one cause, one file group).

1. Judge every `post_approval_art` entry of `design/concepts/Pyrelands/scenes.json` coverage_rest `inv_art_and_text`
   whose `item` is RIMMANDRAKE_JUDGE_PYRELANDS_ART_ADDED_SINCE_HIS_SHEET (rimworld-art-evaluation; brief
   `design/RimMandrake/art_judge_brief.md`; a judge that did not make the art). Flip-book frames are judged as stills only.
   Write each verdict into the entry's `judge` field as `"<verdict> <evidence path>"`; a regen goes through `art install`
   and is shown to him after, with its revert (delegation_policy §2).
2. The crestfeather (RM_PristineFirehawkCrestfeather) ships vanilla's ThrumboHorn art, tinted, as a placeholder. Owner,
   2026-11-13: "That gives a great reason for players to hunt the Firehawk."; "It is ok that they are common. That is the
   threat." Render its own sprite from `infrastructure/artpipe/art_lists/pyrelands_firehawk_crestfeather_2026-11-13.csv`,
   judge it, install it at Things/Item/Special/RM_PristineFirehawkCrestfeather/RM_PristineFirehawkCrestfeather, move texPath
   there and drop the colour line.

## Acceptance test

Both exit 0. Watched red at 71dcee74a7 (2026-11-22): the first prints `17 unjudged`, the second `Things/Item/Special/ThrumboHorn False`.
- `python3 -c "import json,sys; r=[c for c in json.load(open('design/concepts/Pyrelands/scenes.json'))['coverage_rest'] if c['capability']=='inv_art_and_text'][0]; b=[x for x in r['post_approval_art'] if x.get('item')=='RIMMANDRAKE_JUDGE_PYRELANDS_ART_ADDED_SINCE_HIS_SHEET' and not x.get('judge')]; print(len(b),'unjudged'); sys.exit(bool(b))"` (expected 0 unjudged)
- `python3 -c "import re,os,sys; p='src/RimMandrake/Pyrelands/Defs/ThingDefs_Items/RM_PristineFirehawkCrestfeather.xml'; t=re.search(r'<texPath>([^<]+)</texPath>',open(p).read()).group(1); ok=('ThrumboHorn' not in t) and os.path.exists('src/RimMandrake/Pyrelands/Textures/'+t+'.png'); print(t, ok); sys.exit(not ok)"`
