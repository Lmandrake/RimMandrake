In a helper clone made before 8504a1907f, ./publish refused (its whole-tree checks could not see a sparse tree) and ./sync refused too, because a local commit was unlanded. The route that worked was bash src/RimMandrake/Utils/land.sh <sha> <paths>: it syncs and publishes the one commit. Once the clone holds 8504a1907f, ./publish runs the tree checks on a full checkout of HEAD by itself.
item: NONE
home: skills/clone-landing-commits
