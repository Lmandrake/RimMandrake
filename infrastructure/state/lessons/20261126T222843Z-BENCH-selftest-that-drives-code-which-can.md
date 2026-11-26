A selftest that drives code which can write a mod ledger must stub that write: modledger lands each write on origin by itself. One run of selftest_maturation_dispatch in a clone (2026-11-26 1:55 PM PST) landed two fake leases at its pinned clock on Gimme Some Slack's real ledger (ca6bc31538, 879155ea73), and every later run read 'already granted'. Its own 'nothing under design/concepts was written' check read the work tree, not the commits, so it stayed green.
item: RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_EIGHTY_GIG
home: NONE
