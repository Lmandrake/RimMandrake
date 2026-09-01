namespace FactionLoadout.Util;

public interface IDeepCopyable<out T>
{
	T DeepClone();
}
