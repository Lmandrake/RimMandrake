# RIMMANDRAKE_CHECK_GRAFFITI_SITE_SETTINGS_SIX_OF_EIGHT

## spec

Graffiti's northstar site preflight (`src/RimMandrake/Graffiti/northstar_site.py`, `DEFAULTS`) checks 6 of the mod's 8
settings at shipped defaults; `socialEnabled` and `socialMessagesEnabled` (scribed in
`src/RimMandrake/Graffiti/Source/RM_GraffitiMod.cs`) are unchecked, so a site with the social layer switched off passes
preflight and every social must-show line could run against a dead layer. Found by the Designer's stage 0 audit
(record.json contradiction `c_site_settings`, design/concepts/Graffiti); named by scenes in
`design/concepts/Graffiti/scenes.json` as their `entry_point_item` for the start assertion "all 8 settings at shipped
defaults".

## fix
Add both settings to `DEFAULTS` with their shipped defaults (true, true). Better: derive the list from the mod's scribed
settings so a ninth setting cannot slip past.

## acceptance test
Run from the repo root; fails on the base commit (watched 2026-11-15: `settings 8 checked 6 missing
['socialEnabled', 'socialMessagesEnabled']`, AssertionError), passes when preflight checks all 8 at their defaults.
Expected: one line `PASS`.

    python3 -c "
    import ast,re
    cs=open('src/RimMandrake/Graffiti/Source/RM_GraffitiMod.cs').read()
    want={m[0]:m[1] for m in re.findall(r'Scribe_Values\.Look\(ref (\w+), \"\w+\", (\w+)\)',cs)}
    want={k:(v=='true' if v in('true','false') else int(v)) for k,v in want.items()}
    src=ast.parse(open('src/RimMandrake/Graffiti/northstar_site.py').read())
    d=[ast.literal_eval(n.value) for n in src.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='DEFAULTS'][0]
    miss=sorted(set(want)-set(d)); wrong=sorted(k for k in d if want.get(k)!=d[k])
    print('settings',len(want),'checked',len(d),'missing',miss,'wrong',wrong)
    assert len(want)==8 and not miss and not wrong
    print('PASS')"

(If the fix derives the list instead of a literal `DEFAULTS`, update this test in the same change to read the derived
list; the bar stays "all 8, at shipped defaults".)
