In a clone several helpers commit in, a 'git add <new file>' can be lost before your own commit: another helper's commit landed between the two calls and my staged new file was untracked again ('pathspec did not match any file known to git'). Re-run git add and commit immediately; check 'git diff --cached --name-only' first.
home: git-efficiency
