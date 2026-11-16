// Lane-1 stub: RM_Volume.cs pulls in RM_StockMath and more; the sheet kernels need only these two constants. run_lane1.py
// reads them from the shipped RM_Volume.cs and refuses to run if they differ from the values below.
namespace RimMandrake.FlowWorks
{
    public static class RM_Volume
    {
        public const int CentimetresPerNotch = 50;
        public const int UnitsPerLevel = 10000; // LitresPerLevel (2 m2 x 50 cm x 10 L) x UnitsPerLitre 10
    }
}
