A later def move can undo an owner label ruling without anyone seeing it. The 2026-09-29 ruling relabelled the Stillsand ikee to drageye (623403370b). Then 4be549845d and d4146e0cfe moved a different eye creature into RM_Ikee with the label 'ikee', and the collision came back. label_collision_check.py found it only because someone ran it by hand. Before you move or rename a cast creature def, run label_collision_check.py --dump <a capture with a db built from it>.
item: SHIPPING_NAME_CANDIDATES_1
home: NONE
