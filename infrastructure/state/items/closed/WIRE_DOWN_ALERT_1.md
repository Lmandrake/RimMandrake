
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row GS-4 there is the spec:

| GS-4 | A "wire down" alert. When an overhead wire is cut by an explosion or roof, or has fallen, an alert lists each one, jumps to it, and offers to re-string it. Today the only notice is one message for the roof case, so a cut line in a corner of the base goes unnoticed until something browns out. | One `Alert` class over RM_MapComponent_Aerial's spans in state Cut/Fallen. The re-string gizmo already exists. Needs a toggle. | S | low | GimmeSomeSlack | The only Alert in GSS is `Alert_HoseRetracted` (Hose/RM_MapComponent_Hoses.cs:1053). The roof cut is a Message only (Aerial/RM_MapComponent_Aerial.cs:261). There is no explosion or fallen notice. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify WIRE_DOWN_ALERT_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A1 (L2): probe alert lists the anchors of a cut span (down>=2, enabled) and is empty after restring; wireDownAlert=fals
Evidence is the Player.log line or bridge state read the criterion names.
