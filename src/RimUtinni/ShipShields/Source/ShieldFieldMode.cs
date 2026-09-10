namespace RimMandrake.Utinni.ShipShields
{
    // shd:loadout-tradeoff: "I think they should be the same shields, you're
    // just installing modules to increase their switching capacity/
    // configuration" -- one building, one active mode at a time.
    //
    // shd:cryo-envelope (v2) and shd:spore-membrane (cut, owner: "spores
    // aren't magical, just particulates") are deliberately absent.
    public enum ShieldFieldMode : byte
    {
        Bubble = 0,
        Thermal = 1,
        Particulate = 2,
    }
}
