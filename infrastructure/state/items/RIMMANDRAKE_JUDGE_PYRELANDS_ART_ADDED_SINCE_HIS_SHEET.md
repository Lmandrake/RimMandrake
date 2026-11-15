# RIMMANDRAKE_JUDGE_PYRELANDS_ART_ADDED_SINCE_HIS_SHEET

## spec

Round-6 coverage gap g12 (rm-coverage-judge-1794750987; fixed by RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS under
his card OWNER:1794774724955142310): Pyrelands' shipped art rests on his 2026-10-16 approval of the art sheet
(OWNER:1792122659817386516), but art and text added since rest on no judge. Every such entry is listed in
design/concepts/Pyrelands/scenes.json, coverage_rest `inv_art_and_text`, `post_approval_art`; each entry whose `item` is
this id is owed an art-eval verdict (skill rimworld-art-evaluation; brief design/RimMandrake/art_judge_brief.md; a judge
that did not make the art). Flip-book frames are judged as still images only, never as a capture of flight. Text entries
are judged against the same brief's text lines. Write each verdict into the entry's `judge` field as
`"<verdict> <evidence path>"`; a regen the pipeline orders goes through `art install` and is shown to him after, with its
revert (delegation_policy section 2). The open follow-ups (grass lifecycle states, kept-art judge digest, ashwallow dome
sprite) are judged the same way.

## Acceptance test

`python3 -c "import json,sys; r=[c for c in json.load(open('design/concepts/Pyrelands/scenes.json'))['coverage_rest'] if c['capability']=='inv_art_and_text'][0]; b=[x for x in r['post_approval_art'] if x.get('item')=='RIMMANDRAKE_JUDGE_PYRELANDS_ART_ADDED_SINCE_HIS_SHEET' and not x.get('judge')]; print(len(b),'unjudged'); sys.exit(bool(b))"`
exits 0. Watched it fail at filing: 17 unjudged. Expected pass count: 0 unjudged.
