A reader that matches a record by equality of a whole dict (scene_judge: entry == {name, request}) breaks silently when another run adds a field to that dict: every judged run read COULD NOT LOOK after 0aaaaf3de7 added entry.mode. Match on the keys you need, and run the consumers' selftests when you add a field to a shared record.
item: RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP
home: design/specs/2026-11-23-scene-library/boundary.md
