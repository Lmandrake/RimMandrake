In selftest_work_bundle.py, bundle_rec(W, members) with the same 'at' and system gives the same bundle id (bundle_id is system + second), so a second bundle overwrites the first in the store. Pass a distinct at= per bundle.
item: RIMMANDRAKE_LAUNCH_BUNDLE_FRESH_READER_THREE_FIXES_UNREAD
home: NONE
