enact.py ruling_status matched a conflict/todo line to a row by the text before the first colon; the shared-file clash line names several rows ('RowA, RowB: ...'), so both rows read 'reflected' though neither pick was installed. Any line that can name several rows must be matched by membership, not equality. Fixed + selftest_enact_review_fixes.py case 1.
home: rimworld-review-sheets
