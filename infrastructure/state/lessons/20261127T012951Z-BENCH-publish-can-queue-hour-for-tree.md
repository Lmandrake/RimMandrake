A ./publish can queue an hour for a tree-check slot when the machine is busy (measured 2026-11-26: 55+ min behind two live publishes). Wrapping it in timeout 600 or 3000 kills it mid-queue and leaves an unlanded local commit; run it through waitalive.py run (attach to wait again), never a bare timeout.
item: TREE_SHADE_BUILD_CROWNS_ON_STILTS
home: skills/clone-landing-commits
