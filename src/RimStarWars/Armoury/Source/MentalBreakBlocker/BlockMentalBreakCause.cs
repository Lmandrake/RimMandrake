namespace MentalBreakBlocker;

public enum BlockMentalBreakCause : byte
{
    anyway = 0,
    mood = 1,
    damage = 2,
    psycast = 4,
    moodAndDamage = 3,
    moodAndPsycast = 5,
    damageAndPsycast = 6,
    all = 7
}
