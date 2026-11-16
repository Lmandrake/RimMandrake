python: open(p, 'w').write(expr) truncates p BEFORE expr is evaluated; if expr raises, the file is left empty (pipeline_tests.json, 2026-11-16). Build the text first, write to p.new, then mv.
