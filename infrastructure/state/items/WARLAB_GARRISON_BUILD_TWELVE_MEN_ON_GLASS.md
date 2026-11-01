## spec
Build `design/Jawa/worldbuilding/warlab_garrison_early_blast_2026-11-01.md` §8 once that note's
`## Judgment` is settled. Heat and floor on any `Ignite()`, the garrison on the revealed lab site,
the lab's fate, and the codes gate. Route 6's own consequences are unbuilt: this item owes only the
`Route6Live` guard and a stub entry.

Watch: a vanilla `Site` deletes itself when the player leaves, so the revealed site needs the
`Site` subclass in §4. The redeem gizmo works anywhere today, and §5 closes that for every route.

## verify
- [ ] The kernel's selftests cover each row of both §4 tables and the §5 `CodesUsable` cases.
- [ ] The §8 live proof passes by state reads in the mod's `validation.py`.
- [ ] Leaving with a part-killed garrison and returning finds the survivors, not 12.
