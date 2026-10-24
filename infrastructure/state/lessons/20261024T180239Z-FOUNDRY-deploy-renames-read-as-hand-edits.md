deploy_custom_mods repo_deleted ran git log --diff-filter=D WITHOUT --no-renames, so any file renamed inside a mod (R088 RUT_Wasteland->RUT_Wastes, Shyrack _44->_4) was labelled a hand edit ('kept, --pull') and plain --apply left stale defs in the game. Fixed 63b567595a. A '-' line marked 'kept' is worth a git log --no-renames --diff-filter=D check before any --pull.
home: rimworld-deploy
