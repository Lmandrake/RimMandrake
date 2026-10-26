Closing an item with a local sha and then running git pull --rebase + ./publish rewrites that sha; the close can't be redone (rimflow refuses a second close), so the close carries a pre-rebase sha. Pull --rebase and publish the work commit first, then close with the published sha.
home: skills/using-rimflow
