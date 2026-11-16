# Resolve Designer stage-3 artifacts in the concept clone

## refs

file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/selftest_designer_stage.py
file: design/concepts/Stillsand/stage.json

## spec

Stillsand run rm-role-designercodex-1794826273 passed its BENCH check and was rejected by Dispatcher for six missing artifact source paths and fourteen missing root ids. The files exist in BENCH. result_errors reads the concept data from its supplied folder while resolving record paths, the north-star root and scene dependencies against the calling module's repository. A Dispatcher clone can therefore reject a valid package produced in a different clone. Stage 5 already resolves its gate against clone_of(d).

Resolve record source paths and stage-3 lint, scene and showcase artifact paths against clone_of(d), falling back to the supplied repository when the concept has no identifiable clone. Continue merging owner evidence from the caller and concept clone. Keep genuine missing source, missing root and missing scene implementation failures observable. Publish the Stillsand package and its existing filed scene dependencies separately from this validation repair.

## verify

Add a failing regression before implementation. Validate a stage-3 fixture from a second repository with no package files. Assert that record source paths, the root lint and actual script lookup use the concept clone. Delete a concept-local source and check refusal. Run selftest_designer_stage.py and the affected pipeline tests. Recheck the real Stillsand result with the Dispatcher repository argument through read-only result_errors.

## criteria

- Same-clone and cross-clone checks accept the same valid stage-3 package.
- Root lint and scene lookup receive the concept clone repository.
- A source missing from the concept clone and origin remains refused.
- Owner provenance, scene controls, showcase selection and floor checks retain their existing validation.
- No stage is advanced by the repair or regression tests against a real concept.
