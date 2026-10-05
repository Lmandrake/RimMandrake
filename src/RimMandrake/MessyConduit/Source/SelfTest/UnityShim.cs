// The SelfTest has no Unity reference. The GENERATED Aerial/PoleGeometryTable.cs (production, compiled in directly so the
// style-stage-1 lookups are checked against the real measured table) uses only UnityEngine.Vector2's (x, y) constructor and
// fields, so this two-field stand-in is enough. Never add behaviour here: a production file needing more must not compile.
namespace UnityEngine
{
    public struct Vector2
    {
        public float x, y;
        public Vector2(float x, float y) { this.x = x; this.y = y; }
    }
}
