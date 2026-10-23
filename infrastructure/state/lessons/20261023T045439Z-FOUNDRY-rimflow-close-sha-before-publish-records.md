rimflow close --sha before ./publish records a dangling sha: publish rebases the local commit onto origin, so the hash changes. Publish first, then close with the PUBLISHED sha.
