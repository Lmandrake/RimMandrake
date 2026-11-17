./publish printed 'PUBLISHED 6b39f6c105' for a commit whose own sha was 37a196250b: a peer helper's build_match commit landed on HEAD in the same clone during the publish, and publish reported HEAD, not its own commit. Before rimflow close --sha, confirm with git show --stat <sha> that the printed sha holds your paths (evidence D:\ClaudeWork\rimmandrake\conductor\hard_stop\publish1.txt).
item: RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL
home: clone-landing-commits
