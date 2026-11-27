# Polish beside design/specs/2026-11-25-stevedesktop-work-vetted/testq/boundary.md

- src/RimMandrake/Utils/testq/pipeline_admit.py `live_mod`: the empty-list check reads the shipped list only (`known_mods(advancing_only=True)`), so an empty shipped list with a discovered concept refuses that concept as could-not-look, though the page's advancing list (shipped, then discovered) is not empty. No config today has an empty shipped list.
