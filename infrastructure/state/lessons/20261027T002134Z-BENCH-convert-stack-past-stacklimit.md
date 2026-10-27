Converting a held stack into another def as ONE stack (Encasing Shock: made.stackCount = Min(n, into.stackLimit)) silently destroys the units above the target def's stackLimit whenever the source stack is bigger (stack-size mods). Cap the converted count at the target stackLimit or emit several stacks; fixed in 9368f96bf5.
home: rimworld-modding
