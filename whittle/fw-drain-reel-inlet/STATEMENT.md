# Reel body inlets respect depth at their actual contact

- A reel body cannot hydraulically couple across a sheer depth-band boundary, and still couples to valid same-band neighbours using actual multi-cell contact geometry.
- Production-linked executable checks reproduce the original defect and reject its return, covering candidate ranking, contact choice, settings and existing free-end/pump semantics where relevant. The relevant FlowWorks selftest and shipping build pass on the repaired source.
- A disposable live-game acceptance verifies the repaired inlet behavior on the deployed DLL. Evidence names exact inputs, results and remaining limits, with the approved GSS appearance preserved.
