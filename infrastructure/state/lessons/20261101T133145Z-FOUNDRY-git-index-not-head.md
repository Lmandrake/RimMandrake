In a hook judging whether a file is 'already tracked', git ls-files reads the INDEX, so a file staged by 'git add' a moment ago counts as tracked. Compare against HEAD (git ls-tree --name-only -z HEAD). queue_lint rule 4 never refused a staged new root .md because of this (fixed b2cc2d3701).
home: NONE
