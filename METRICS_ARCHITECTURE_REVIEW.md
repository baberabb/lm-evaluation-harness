# Deep Dive: Metrics & Scoring Architecture Review

**Author**: Claude (Anthropic)
**Date**: 2025-11-19
**Branch**: `claude/review-metrics-abstracts-01BhfniThP8VwiggXV1HpWNK`
**Base**: `claude/group-refactor-011J82CVVB3nfUZ3EzsQEvEu`

---

## Executive Summary

After deep analysis of the metrics and scoring system in lm-evaluation-harness, I find that **GenResult and MCResult abstractions are fundamentally sound** but could be more intuitive with targeted improvements. The current V2 implementation successfully unified the scoring loop, but there are opportunities to make the system more discoverable and easier to reason about.

**Key Findings:**
1. ✅ **GenResult/MCResult are the right abstractions** - they cleanly separate generation vs multiple-choice semantics
2. ⚠️ **The Protocol pattern adds indirection** without much benefit - could be simplified
3. ⚠️ **Filter-metric relationship is unclear** - the fallback logic is hidden
4. ⚠️ **Metric signatures differ** between task types - this is OK but should be documented better
5. ⚠️ **Result creation is opaque** - the `Results.create()` factory obscures what's happening

---

## Part 1: Are GenResult and MCResult the Right Abstractions?

### TL;DR: **Yes, but with caveats**

### The Good: Clear Separation of Concerns

**GenResult** handles generation semantics:
- Multiple samples per doc (temperature sampling, repeats)
- String-based outputs that need conversion to metric inputs
- Per-generation scoring with later reduction
- Filter-based response extraction

**MCResult** handles multiple-choice semantics:
- Log-likelihoods across choices
- Length normalization variants (char/byte/token)
- Mutual information calculation
- Direct passage to metrics (no conversion needed)

**This separation makes sense** because:
1. The data structures ARE fundamentally different
2. The scoring semantics ARE fundamentally different
3. Trying to unify them would create a "god object" with lots of conditionals

### The Problematic: Protocol Pattern Overhead

```python
@runtime_checkable
class Results(Protocol[InstanceT]):
    """Class for storing results of a task."""

    results: Any
    target: Any
    scores: Any
    instances: Sequence[InstanceT]

    @classmethod
    def from_instances(cls, ...) -> ResultsSelf: ...

    @abstractmethod
    def to_metric_inputs(self) -> Any: ...

    @staticmethod
    def create(instance, filter_name):
        output_type = instance[0].request_type
        match output_type:
            case "loglikelihood":
                return MCResult.from_instances(instance)
            case _:
                return GenResult.from_instances(instance, filter_name=filter_name)
```

**Issues:**
1. **The Protocol adds a layer of indirection** - it's not actually used polymorphically anywhere
2. **The `create()` factory hides information** - you have to trace through to understand what result type you get
3. **The Protocol enforces `to_metric_inputs()`** - but GenResult and MCResult use it completely differently:
   - GenResult: Returns `{"predictions": [...], "references": [...]}`
   - MCResult: Returns `self` (the whole object)

**This is confusing** because the Protocol suggests they're interchangeable, but they're not.

### Recommendation: Simplify to Just Two Classes

Instead of a Protocol + factory pattern, just use:

```python
@dataclass
class GenResult:
    """Result for generation tasks. Used by GenerateTask."""
    results: Sequence[str]
    target: str | list[str]
    instances: Sequence[GenInstance]
    repeats: int = 1
    filter_name: str = "default"
    scores: dict[Any, list[float]] = field(default_factory=lambda: defaultdict(list))

    @classmethod
    def from_instances(cls, instances, filter_name="default"):
        # ... current implementation ...

    def to_metric_kwargs(self) -> dict[str, Any]:
        """Convert to kwargs for generation metrics."""
        return {
            "predictions": self.results,
            "references": self.target if isinstance(self.target, list) else [self.target],
        }

@dataclass
class MCResult:
    """Result for multiple-choice tasks. Used by MultipleChoiceTask."""
    lls: Sequence[float]
    is_greedy: Sequence[bool]
    target: int
    choices: Sequence[str]
    # ... rest of fields ...

    @classmethod
    def from_instances(cls, results, acc_mutual_info=False):
        # ... current implementation ...

    # No to_metric_inputs() - metrics just take self directly
```

**Why this is better:**
1. **No fake polymorphism** - they're explicitly different types
2. **No factory method** - task classes just call the right constructor directly
3. **Clear documentation** - docstrings say which task type uses which result
4. **Simpler** - fewer abstractions to understand

---

## Part 2: The Metric Scoring Loop

### Current Flow (V2 Implementation)

```python
def process_instances(self, instances):
    """Unified scoring logic."""
    _instances = self.sort_instances(instances)

    for filter_cfg in self._filters:
        # Hidden fallback logic here
        metrics = filter_cfg.metric_list if filter_cfg.metric_list else self.config._metric_list

        for doc_id, doc_instances in _instances.items():
            # Factory method hides what type is created
            result = self._create_result(doc_instances, filter_cfg.name)

            for metric in metrics:
                # Different signatures depending on task type
                score = self._compute_metric(result, metric)
                sample_scores[(metric.name, filter_cfg.name)].append(score)
```

### Issues with Discoverability

1. **Filter-metric fallback is implicit**
   - You have to read the code to understand the precedence
   - YAML config doesn't make it clear what happens if you omit `metric_list` from a filter
   - No error if you accidentally have both filter and global metrics

2. **Result type is hidden**
   - `_create_result()` returns different types depending on task
   - No type hints in the base method
   - IDE can't help you understand what you're working with

3. **Metric signature differences are undocumented**
   - Generation metrics: `fn(references=[], predictions=[], **kwargs)`
   - MC metrics: `fn(MCResult)`
   - Only way to know is to read examples or trace code

### Recommendation: Make It Explicit

```python
def process_instances(self, instances):
    """Unified scoring logic for all task types.

    Iteration pattern: filter → doc → metric

    For each filter:
        - Uses filter.metric_list if present, else falls back to task.metric_list
        - Creates a result object (GenResult or MCResult depending on task type)
        - Computes each metric on the result
        - Stores scores as (metric_name, filter_name) → [scores]
    """
    _instances = self.sort_instances(instances)

    for filter_cfg in self._filters:
        # EXPLICIT: Show the fallback logic
        metrics = self._get_metrics_for_filter(filter_cfg)

        for doc_id, doc_instances in _instances.items():
            # EXPLICIT: Type hint shows what's returned
            result: GenResult | MCResult = self._create_result(doc_instances, filter_cfg.name)

            for metric in metrics:
                score = self._compute_metric(result, metric)
                sample_scores[(metric.name, filter_cfg.name)].append(score)

    return sample_scores

def _get_metrics_for_filter(self, filter_cfg) -> list[MetricConfig]:
    """Get metrics for a filter, with fallback to task-level metrics.

    Precedence:
        1. filter_cfg.metric_list (if specified in YAML)
        2. self.config._metric_list (task-level default)
    """
    if filter_cfg.metric_list:
        return filter_cfg.metric_list
    return self.config._metric_list
```

**Benefits:**
- Clear docstrings explain the flow
- Type hints help IDEs and readers
- Explicit method name makes fallback logic discoverable
- Easy to modify if you want different precedence rules

---

## Part 3: The Real Problem - Different Metric Signatures

### Current State

**Generation metrics** (from `exact_match_fn`):
```python
@register_metric(
    metric="exact_match",
    output_type="generate_until",
    aggregation="mean",
)
def exact_match_fn(**kwargs):
    # Expects: predictions=[...], references=[...]
    return exact_match_hf_evaluate(**kwargs)
```

**MC metrics** (from `acc_fn`):
```python
@register_metric(
    metric="acc",
    output_type=["loglikelihood", "multiple_choice"],
    aggregation="mean",
)
def acc_fn(items):
    # Expects: MCResult object
    # Uses items.lls, items.target, etc.
    return items
```

### Why They're Different

**Generation tasks need flexibility:**
- Metrics come from external libraries (sacrebleu, sklearn, etc.)
- Standard interface is `fn(predictions, references, **options)`
- Some metrics want lists, some want strings
- Multiple references per prediction in some cases

**MC tasks have structured data:**
- All you need is in MCResult: lls, target, choices, etc.
- Metrics operate on arrays/vectors directly
- No ambiguity about what the "prediction" is

### The Current Solution: Type-Specific `_compute_metric`

```python
# GenerateTask
def _compute_metric(self, gen_result: GenResult, metric):
    scores = []
    for generation in gen_result.results:
        score = metric.fn(
            references=[gen_result.target] if not isinstance(gen_result.target, list) else gen_result.target,
            predictions=[generation],
            **metric.kwargs
        )
        scores.append(score)
    return scores

# MultipleChoiceTask
def _compute_metric(self, mc_result: MCResult, metric):
    return metric.fn(mc_result)
```

### The Question: Is This OK?

**My answer: Yes, with better documentation.**

**It's OK because:**
1. The tasks ARE fundamentally different
2. The metric ecosystems ARE different (external libs vs internal)
3. Forcing a unified signature would require awkward adapters

**But it needs:**
1. Clear documentation in metric registration about expected signature
2. Type hints on metric functions
3. Helper utilities for common conversions

### Recommendation: Document the Contract

```python
# In lm_eval/api/metrics.py

"""
Metric Function Signatures
===========================

Generation Metrics (output_type="generate_until")
-------------------------------------------------
Generation metrics receive keyword arguments from GenResult.to_metric_kwargs():

    def my_generation_metric(
        predictions: list[str],
        references: list[str] | list[list[str]],
        **options
    ) -> float | dict[str, float]:
        ...

Example:
    @register_metric(
        metric="my_metric",
        output_type="generate_until",
        aggregation="mean",
    )
    def my_metric_fn(**kwargs):
        predictions = kwargs["predictions"]
        references = kwargs["references"]
        return compute_score(predictions, references)

Multiple-Choice Metrics (output_type=["loglikelihood", "multiple_choice"])
---------------------------------------------------------------------------
MC metrics receive the MCResult object directly:

    def my_mc_metric(result: MCResult) -> float:
        # Access result.lls, result.target, result.choices, etc.
        correct_idx = result.target
        pred_idx = max(enumerate(result.lls), key=lambda x: x[1])[0]
        return 1.0 if pred_idx == correct_idx else 0.0

Example:
    @register_metric(
        metric="acc",
        output_type=["loglikelihood", "multiple_choice"],
        aggregation="mean",
    )
    def acc_fn(result: MCResult) -> float:
        return 1.0 if max(enumerate(result.lls), key=lambda x: x[1])[0] == result.target else 0.0
"""
```

---

## Part 4: The Aggregation & Reduction Flow

### Current Implementation

```python
def compute_aggregations(self, scores, bootstrap_iters=100):
    """Aggregate scores and compute standard errors.

    Flow:
        1. Reduce: If repeats > 1, apply reducer (min/max/mean/median)
        2. Aggregate: Apply aggregation function (mean/median/perplexity/etc.)
        3. Stderr: Bootstrap or closed-form standard error
    """
    agg_metrics = {}
    for (metric, filter_key), items in scores.items():
        # Step 1: Reduce multiple samples per doc
        items = self.reduce(items, metric)

        # Step 2: Aggregate across all docs
        try:
            agg_fn = self.aggregation()[metric]
        except KeyError:
            agg_fn = mean  # Fallback for custom metrics

        agg_metrics[f"{metric},{filter_key}"] = agg_fn(items)

        # Step 3: Standard error
        stderr_fn = stderr_for_metric(agg_fn, bootstrap_iters)
        if stderr_fn and len(items) > 1:
            agg_metrics[f"{metric}_stderr,{filter_key}"] = stderr_fn(items)
        else:
            agg_metrics[f"{metric}_stderr,{filter_key}"] = "N/A"

    return agg_metrics
```

### Issues

1. **Reducer selection is implicit**
   - `self.reduce()` looks at `self.config.repeat_cfg.reducer`
   - No clear documentation of when reduction happens
   - Unclear what happens if you have repeats but no reducer configured

2. **Aggregation fallback is silent**
   - If metric not in `self.aggregation()`, silently uses `mean`
   - Could mask configuration errors
   - No warning that you're using a fallback

3. **Stderr calculation is opaque**
   - `stderr_for_metric()` has complex logic about which metrics support which stderr methods
   - Bootstrap is expensive but happens silently
   - Hard-coded list of "bootstrappable" metrics in separate file

### Recommendation: Explicit Configuration

```python
def compute_aggregations(self, scores, bootstrap_iters=100):
    """Aggregate scores and compute standard errors.

    Three-step process:
        1. REDUCE: Collapse multiple samples per doc (if config.repeats > 1)
           - Uses config.repeat_cfg.reducer (max/min/mean/median/first)
           - Example: [[0.8, 0.9], [0.7, 0.6]] → [0.9, 0.7] (if reducer=max)

        2. AGGREGATE: Combine all doc scores into single metric
           - Uses metric's registered aggregation function
           - Example: [0.9, 0.7, 0.8] → 0.8 (if aggregation=mean)

        3. STDERR: Estimate standard error
           - Bootstrap for approved metrics (expensive!)
           - Closed-form for mean/acc_all
           - "N/A" if no method available

    Args:
        scores: Dict of (metric_name, filter_name) → [doc_scores]
        bootstrap_iters: Number of bootstrap samples (0 to disable)

    Returns:
        Dict with aggregated metrics and stderr estimates
    """
    agg_metrics = {}

    for (metric, filter_key), items in scores.items():
        # Step 1: Reduce (explicit check)
        items = self._reduce_samples(items, metric)

        # Step 2: Aggregate (explicit fallback)
        agg_fn = self._get_aggregation_fn(metric)
        agg_metrics[f"{metric},{filter_key}"] = agg_fn(items)

        # Step 3: Stderr (explicit logic)
        stderr_value = self._compute_stderr(metric, agg_fn, items, bootstrap_iters)
        agg_metrics[f"{metric}_stderr,{filter_key}"] = stderr_value

    return agg_metrics

def _reduce_samples(self, items, metric):
    """Reduce multiple samples per doc to single score.

    Only applies if config.repeats > 1 and items are nested lists.
    Uses config.repeat_cfg.reducer (max/min/mean/median/first).
    """
    if not isinstance(items[0], (list, tuple)):
        return items  # Already single scores

    if self.config.repeats <= 1:
        # Repeats not configured, take first value
        return [x[0] for x in items]

    reducer = self.config.repeat_cfg.reducer
    return [reducer(x) for x in items]

def _get_aggregation_fn(self, metric_name):
    """Get aggregation function for a metric.

    Looks up in registered aggregations. Falls back to mean with warning.
    """
    try:
        return self.aggregation()[metric_name]
    except KeyError:
        eval_logger.warning(
            f"Metric '{metric_name}' has no registered aggregation, using mean. "
            f"Register with @register_aggregation or add to metric_list."
        )
        return mean

def _compute_stderr(self, metric_name, agg_fn, items, bootstrap_iters):
    """Compute standard error using bootstrap or closed-form method."""
    if bootstrap_iters <= 0:
        return "N/A"

    if len(items) <= 1:
        return "N/A"  # Need multiple samples for stderr

    stderr_fn = stderr_for_metric(agg_fn, bootstrap_iters)
    if stderr_fn:
        # Bootstrap (expensive!) or closed-form
        return stderr_fn(items)
    else:
        eval_logger.debug(
            f"No stderr method for '{metric_name}' with {agg_fn.__name__} aggregation"
        )
        return "N/A"
```

**Benefits:**
- Explicit method names make control flow clear
- Warnings for fallback cases help debugging
- Docstrings explain when each step applies
- Easier to customize or extend

---

## Part 5: The Filter System

### Current Design

```python
class FilterEnsemble:
    """Pipeline of multiple filters applied in sequence."""
    name: str
    filters: List[Callable[[], Filter]]

    def apply(self, instances):
        resps, docs = zip(*((inst.resps, inst.doc) for inst in instances))

        for f in self.filters:
            resps = f().apply(resps, docs)

        for inst, resp in zip(instances, resps):
            inst.filtered_resps[self.name] = resp
```

### Issues

1. **Mutable state in Instance**
   - `filtered_resps` dict grows as filters are applied
   - Hard to track which filters have been applied
   - Easy to accidentally use wrong filter name

2. **Filter-metric relationship unclear**
   - Filters store results by name
   - GenResult.from_instances() looks up by name
   - But there's no validation that the filter actually ran
   - No error if you typo the filter name

3. **No composability**
   - Can't easily reuse filtered results across metrics
   - Can't apply different metrics to same filtered output without re-filtering

### The Core Question: Are Filters at the Right Level?

**Current model**: Filters are per-task, applied once to all instances

**Alternative model**: Filters are per-metric, applied just-in-time

```python
# Current: Filter once, metric many times
task.apply_filters()  # Modifies all instances
task.process_instances()  # Reads filtered_resps

# Alternative: Filter per metric
for metric in metrics:
    filter = metric.get_filter()  # Metric knows its filter
    filtered_results = filter.apply(instances)
    scores = metric.compute(filtered_results)
```

**Pros of current model:**
- Efficient: filter once, reuse across metrics
- Clear separation: filtering is separate from scoring

**Cons of current model:**
- Tight coupling: GenResult must know filter names
- Mutation: filtered_resps dict grows over time
- Unclear precedence: what if filter and metric disagree?

**My recommendation: Keep current model, but add validation**

```python
class GenResult:
    @classmethod
    def from_instances(cls, instances, filter_name="default"):
        if not instances:
            raise ValueError("Cannot create GenResult from empty instances")

        # Validate filter was applied
        if filter_name not in instances[0].filtered_resps:
            available = list(instances[0].filtered_resps.keys())
            raise ValueError(
                f"Filter '{filter_name}' not found. "
                f"Available filters: {available}. "
                f"Did you forget to call task.apply_filters()?"
            )

        # ... rest of implementation ...
```

---

## Part 6: Recommendations Summary

### High Priority (Do These)

1. **Remove the Results Protocol** ✅
   - Just use GenResult and MCResult directly
   - Remove `Results.create()` factory method
   - Have tasks call the right constructor explicitly

2. **Add Explicit Filter-Metric Fallback Method** ✅
   - Create `_get_metrics_for_filter()` to make precedence clear
   - Document in YAML examples when to use filter vs task metrics

3. **Document Metric Signatures** ✅
   - Add big comment block in metrics.py explaining the two patterns
   - Add type hints to metric functions
   - Show examples of each pattern

4. **Add Validation to GenResult** ✅
   - Check that filter actually ran before looking up filtered_resps
   - Give helpful error message with available filters

### Medium Priority (Consider These)

5. **Split Aggregation into Explicit Steps** ⚠️
   - Create `_reduce_samples()`, `_get_aggregation_fn()`, `_compute_stderr()`
   - Add warnings for fallback cases
   - Makes the flow much easier to understand

6. **Add Config Validation** ⚠️
   - Check that metrics are registered for the right output_type
   - Warn if using bootstrap on very large datasets
   - Validate reducer is set if repeats > 1

7. **Better Error Messages** ⚠️
   - When metric fails, show which doc it failed on
   - When filter not found, suggest similar names
   - When config is missing, show where to set it

### Low Priority (Nice to Have)

8. **Type Hints Everywhere** 📝
   - Add return type hints to all metric functions
   - Annotate GenResult/MCResult fields more precisely
   - Use TypedDict for metric kwargs

9. **Metric Utilities** 📝
   - Helper to convert MCResult to predictions/references format
   - Helper to handle multi-reference cases
   - Adapter pattern for external metric libraries

10. **Better Docs** 📝
    - Architecture diagram showing the flow
    - Cookbook with common patterns
    - FAQ for common confusion points

---

## Part 7: The Verdict

### Are GenResult and MCResult Unwieldy?

**No.** They're the right abstractions for their respective domains. The issues are:

1. **Hidden relationships** - factory methods and protocols obscure what's happening
2. **Undocumented contracts** - metric signatures differ but it's not explained why
3. **Implicit fallbacks** - filter/task metrics, aggregation selection, stderr methods
4. **Mutable state** - filtered_resps dict is hard to track

### Is the Pattern Inevitable?

**Mostly yes.** Any system that handles:
- Multiple task types (generation, MC, perplexity)
- Multiple metrics per task
- Multiple filters per metric
- Sample reduction (repeats/temperature)
- Aggregation with stderr

...will need some abstraction to avoid code duplication.

The current V2 implementation is **much better than duplicated code** in each task class.

### What Should Change?

**Make the implicit explicit:**
- Remove fake polymorphism (Protocol)
- Extract hidden logic into named methods
- Add validation at boundaries
- Document the contracts clearly

**The code itself is mostly fine.** It just needs better signposting.

---

## Part 8: Proposed Changes (Concrete Diffs)

### Change 1: Remove Protocol, Use Direct Construction

**Before** (lm_eval/types.py):
```python
@runtime_checkable
class Results(Protocol[InstanceT]):
    ...
    @staticmethod
    def create(instance, filter_name=None):
        output_type = instance[0].request_type
        match output_type:
            case "loglikelihood":
                return MCResult.from_instances(instance)
            case _:
                return GenResult.from_instances(instance, filter_name=filter_name)
```

**After**:
```python
# Remove Results Protocol entirely
# Just have GenResult and MCResult as standalone dataclasses
```

**In task.py**:
```python
# GenerateTask - EXPLICIT
def _create_result(self, instances, filter_name) -> GenResult:
    return GenResult.from_instances(instances, filter_name=filter_name)

# MultipleChoiceTask - EXPLICIT
def _create_result(self, instances, filter_name) -> MCResult:
    acc_mutual_info = "acc_mutual_info" in [m.name for m in self.config._metric_list]
    return MCResult.from_instances(instances, acc_mutual_info=acc_mutual_info)
```

### Change 2: Explicit Filter-Metric Fallback

**Before** (task.py):
```python
for filter_cfg in self._filters:
    metrics = filter_cfg.metric_list if filter_cfg.metric_list else self.config._metric_list
```

**After**:
```python
for filter_cfg in self._filters:
    metrics = self._get_metrics_for_filter(filter_cfg)

def _get_metrics_for_filter(self, filter_cfg):
    """Get metrics for filter with fallback to task metrics.

    Priority: filter.metric_list > task.metric_list
    """
    return filter_cfg.metric_list or self.config._metric_list
```

### Change 3: Validation in GenResult

**Before**:
```python
if filter_name and filter_name in inst.filtered_resps:
    resp = inst.filtered_resps[filter_name]
else:
    generations.append(inst.filtered_resps)  # Weird fallback!
```

**After**:
```python
if filter_name not in inst.filtered_resps:
    available = list(inst.filtered_resps.keys())
    raise ValueError(
        f"Filter '{filter_name}' not applied to instance. "
        f"Available: {available}. Call task.apply_filters() first."
    )

resp = inst.filtered_resps[filter_name]
```

### Change 4: Document Metric Signatures

**Add to lm_eval/api/metrics.py**:
```python
"""
================================================================================
                        METRIC FUNCTION SIGNATURES
================================================================================

This library has two types of metrics with DIFFERENT signatures:

1. Generation Metrics (output_type="generate_until")
   -----------------------------------------------
   Receive kwargs: predictions (list[str]), references (list[str] | list[list[str]])

   Example:
       @register_metric(metric="exact_match", output_type="generate_until", ...)
       def exact_match_fn(predictions, references, **opts):
           return sum(p == r for p, r in zip(predictions, references)) / len(predictions)

2. Multiple-Choice Metrics (output_type=["loglikelihood", "multiple_choice"])
   ---------------------------------------------------------------------------
   Receive MCResult object directly

   Example:
       @register_metric(metric="acc", output_type="multiple_choice", ...)
       def acc_fn(result: MCResult):
           pred_idx = max(enumerate(result.lls), key=lambda x: x[1])[0]
           return 1.0 if pred_idx == result.target else 0.0

WHY are they different?
-----------------------
- Generation tasks produce strings → need flexible prediction/reference format
- MC tasks produce log-likelihoods → structured MCResult is more natural
- External metrics (BLEU, ROUGE) expect predictions/references
- Internal metrics (accuracy) just need argmax(lls)

================================================================================
"""
```

---

## Conclusion

**GenResult and MCResult are good abstractions.** They correctly separate the semantics of generation vs multiple-choice evaluation.

**The problems are not with these abstractions**, but with:
1. Unnecessary indirection (Protocol, factory methods)
2. Undocumented contracts (metric signatures, filter fallback)
3. Hidden complexity (aggregation steps, stderr selection)

**The fix is not to change the abstractions**, but to **make the system more explicit**:
- Remove layers that don't add value
- Extract implicit logic into named methods
- Add validation and helpful errors
- Write clear documentation

With these changes, the system would be **significantly more intuitive** without any major refactoring.

---

## Next Steps

Would you like me to:
1. **Implement the high-priority changes** (remove Protocol, add explicit methods, add validation)?
2. **Just create a detailed implementation plan** for you to review first?
3. **Focus on a specific area** that you find most problematic?

Let me know your thoughts!
