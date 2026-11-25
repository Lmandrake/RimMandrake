A Python tool that makes a large temp tree must catch SIGTERM, or 'timeout N tool' leaves the tree: Python's default SIGTERM action ends the process without running any finally block. bench kept a 4.6 GB rm-treecheck-rqp5014m from 'timeout 530 ./publish' (2026-11-24 7:45 PM PST). publish.py now turns SIGTERM into SystemExit after it kills its check sessions (_on_term). Check children started with start_new_session=True do not get the caller's signal at all.
item: RIMMANDRAKE_REUSE_TREECHECK_TREE_EACH_PUBLISH_WRITES_THREE_GIG
home: design/specs/2026-11-25-treecheck-kept-tree/boundary.md
