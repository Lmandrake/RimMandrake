wc.py statement_md, for an item with no ledger criteria, keeps item-file ## criteria lines whose first char is - or * and drops x[0]: a prose criteria paragraph yields junk bullets. CATHEDRAL_DESCENT_REVEAL_SITE_1 got '- ' and '- *Depends on:** item 1 ...' as its whole STATEMENT, so no bullet carries the owner's criteria (descent playable, reveal flag published, stage 3 only by this beat). Fix: take the ## criteria paragraph(s) as bullets when no line is a list item, and skip bold-label lines like **Depends on:**.
item: CATHEDRAL_DESCENT_REVEAL_SITE_1
home: infrastructure/whittle_claude/wc.py
