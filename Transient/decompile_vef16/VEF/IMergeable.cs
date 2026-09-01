namespace VEF;

public interface IMergeable
{
	float Priority { get; }

	void Merge(object other);

	bool CanMerge(object other);
}
