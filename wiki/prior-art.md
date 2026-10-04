# Prior art (as of 2026-09-29)

- **vCache** (ICLR 2026, `vcache-project/vCache`, ~80 stars): semantic cache with a
  user-set error-rate bound, learned per-prompt thresholds. Already includes an
  `LLMComparisonSimilarityEvaluator`, i.e. "ask a small LLM if the cached answer fits".
  So a "verify the hit" guard is not novel. **License is CC BY-NC-ND 3.0**: no
  commercial use, no derivatives, which limits adoption and leaves room for a
  permissive alternative.
- vCache's benchmarks (SemCacheClassification 45k, SemCacheSearchQueries 150k,
  perturbed SQuAD 38k) measure normal workloads and meaning-preserving rewrites. No
  deliberately adversarial "near-identical, different answer" set was found in one
  round of searching. That gap is this project's angle.
- Other papers: Asynchronous Verified Semantic Caching (arXiv 2602.13165), MeanCache
  (2403.02694), MVR-cache (2605.24914).
- Popular caches: GPTCache (~8.2k stars), RedisVL SemanticCache (~430 stars). Their
  default models and thresholds are **not yet verified**; check before quoting them.
- Demand signal: `rithulkamesh/continuum` issue #10 asks for a false-hit-rate eval harness.
