# fow-cache wiki

The research log behind fow-cache: an open-source benchmark and library measuring how
often semantic caches return a cached answer to a question that needs a different one,
and a guard against it in multi-turn chats. Kept in the repo so the reasoning behind
every number in the README is public, dead ends included.

- [findings](findings.md): results so far, and the caveats that must be fixed before
  anything is published.
- [prior-art](prior-art.md): vCache, the other semantic-cache papers, and where this
  project fits.
- [ideas](ideas.md): ideas not yet built (partial reuse / answer adaptation).
- [log](log.md): what happened, append only.

Origin: the question of where a fast decision model like TypeSafe's Jev fits into LLM
infrastructure; semantic-cache hit checking turned out to be a natural fit.
