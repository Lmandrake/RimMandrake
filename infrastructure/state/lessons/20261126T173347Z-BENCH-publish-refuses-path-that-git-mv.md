./publish refuses a path that git mv already removed from the index (git add --all -- <old path> finds no match). Move an item file with plain mv, or publish the new path and the old path in two ./publish calls.
item: CONFIGERRORS_FIX_FIVE_MORE_ON_LATEST_LOAD
