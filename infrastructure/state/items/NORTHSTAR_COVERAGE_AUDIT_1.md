# NORTHSTAR_COVERAGE_AUDIT_1

Child of NORTHSTAR_EVERYWHERE_PROGRAM_1.

## spec
55 mods already carry a `validation.py` (`git ls-files 'src/**/validation.py'`). For each, compare its bars to the mod's intended function (About.xml, defs, design docs) and list uncovered behaviours; extend the script or file a child. Also static-lint every bridge call against the declared tool schemas (`rimbridge_client.py --list-tools`). Do not touch owner-validated `## north star` sections of FlowWorks, Graffiti, Pyrelands.

## verify
A per-mod table in Transient/ then committed as a design doc; scripts extended where cheap.

## criteria
Every existing script has a recorded coverage verdict and no known unlisted behaviour without a ticket.
