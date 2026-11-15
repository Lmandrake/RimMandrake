# RIMMANDRAKE_DRAW_CRESTFEATHER_OWN_ART_NOT_A_THRUMBO_HORN

## spec

Round-6 coverage gap g12 (rm-coverage-judge-1794750987; RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS, his card
OWNER:1794774724955142310): RM_PristineFirehawkCrestfeather
(src/RimMandrake/Pyrelands/Defs/ThingDefs_Items/RM_PristineFirehawkCrestfeather.xml) ships vanilla's ThrumboHorn art,
tinted, as a placeholder. Its own sprite is queued in infrastructure/artpipe/art_lists/pyrelands_firehawk_crestfeather_2026-11-13.csv.
Render it through the art pipeline, have it judged (rimworld-art-evaluation), install it with `art install` at the def's own
path (Things/Item/Special/RM_PristineFirehawkCrestfeather/RM_PristineFirehawkCrestfeather), move texPath there and drop the
colour line, as the def's comment says. Then set the post_approval_art ThrumboHorn entry's `judge` field.

## Acceptance test

`python3 -c "import re,os,sys; p='src/RimMandrake/Pyrelands/Defs/ThingDefs_Items/RM_PristineFirehawkCrestfeather.xml'; t=re.search(r'<texPath>([^<]+)</texPath>',open(p).read()).group(1); ok=('ThrumboHorn' not in t) and os.path.exists('src/RimMandrake/Pyrelands/Textures/'+t+'.png'); print(t, ok); sys.exit(not ok)"`
exits 0. Watched it fail at filing (texPath Things/Item/Special/ThrumboHorn). Expected: one def, PASS.
