
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Arc §3 bullet 2: the kit's droid-commentary pools (kit §1) gain stage-keyed
line pools (key = band × stage). The hook is built (2026-10-11): add
`<li><band>N</band><stage>S</stage><lines>…</lines></li>` entries to
`<commentary>` in
`src/RimMandrake/RustCathedral/Defs/RM_BiomeAttitudeDefs/RM_RustCathedralAttitude.xml`;
an exact band × stage entry beats the band's `stage`-less (any-stage) entry,
an unmatched stage with no any-stage entry is silence, and ConfigErrors
rejects duplicate keys. There is no RulePack and none is needed. Register: droids report what
they *feel*, never what it *means*; pre-reveal no line attributes agency;
post-reveal lines still never explain the mercy (ban 2) or the drill (ban 6).
Stage-transition letters in §P register only ("the ground here has been...
easier, lately"). PLUS the enforcement instrument the whole arc's verify
rides: a **linter script** (extends
`skills/rimworld-modding/scripts/validate_patch.py` family or standalone)
that greps every player-facing string in the arc's content (RulePacks,
letters, quest text from items 4/5/7/8) for (a) agency attribution before
stage 3 — flag terms naming the Cathedral as actor/quest-giver, (b) mercy
explanation, (c) drill description. Wired so items 4/5/7/8 run it in their
own verify.

## verify
Arc §8 seed 2 executed literally: linter run over all shipped strings returns
zero findings; a deliberately-poisoned fixture line IS caught (the linter is
tested, not trusted); commentary fires on band transitions per stage key on a
quicktest map; Oracle absent throughout (these are RulePack strings — no
Oracle involvement at all).

## criteria
Pools shipped for all 4 stages × bands v1; linter committed with fixture
tests; every later arc item's verify section cites the linter by path.

**Depends on:** RUST_CATHEDRAL_MECHANICS_1 §1 (stage-keyed commentary hook — built 2026-10-11);
item 1 (stage key source, via item 2's lane or direct flag). **Waited on
by:** items 4, 5, 7, 8 (they must pass its gate). **Seat/needs:** FOUNDRY;
offline content + linter, quicktest for transition firing. Not row-3.
