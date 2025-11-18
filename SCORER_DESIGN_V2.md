# Scorer Design V2: Minimal Complexity Approach

## The Core Problem

Looking at your smolrefact implementation, the issues are:

1. **Inconsistent iteration patterns**:
   - GenerateTask: `for filter → for doc → for metric`
   - MultipleChoiceTask: `for doc → for (filter, metric) pairs`

2. **Unclear filter-metric relationship**:
   - Should metrics be global (`self.config._metric_list`) or per-filter (`filter.metric_list`)?
   - GenerateTask uses global, MultipleChoiceTask uses per-filter

3. **Mixed responsibilities in `_process_instances`**:
   - Creates result objects (GenResult/MCResult)
   - Computes metrics
   - Manages iteration
   - All tangled together

4. **Different metric signatures**:
   - GenerateTask: `metric.fn(references=[...], predictions=[...])`
   - MultipleChoiceTask: `metric.fn(MCResult)`

**Your concern**: Adding a Scorer might just create MORE abstraction and indirection without actually simplifying things.

---

## The Minimal Fix: Just Unify the Loop

**Key insight**: The real problem isn't that we need a "Scorer" class - it's that the iteration logic is duplicated and inconsistent.

What if we just **unify the iteration pattern** and **clarify the filter-metric relationship** WITHOUT adding new abstractions?

### Proposed Change: Single Method in Task Base Class

```python
class Task(ABC):
    def process_instances(self, instances: list[Instance] | None = None):
        """Unified scoring logic for all task types."""
        instances = instances or self._instances
        if not instances:
            return {}

        instances_by_doc = self.sort_instances(instances)
        sample_scores = defaultdict(list)

        # Handle custom process_results (backward compatibility)
        if callable(self.config.process_results):
            return self._process_with_custom_fn(instances_by_doc)

        # Standard path: Unified iteration
        # ALWAYS iterate: filter → doc → compute
        for filter_cfg in self._filters:
            for doc_id, doc_instances in instances_by_doc.items():
                # Create result object (task-type specific)
                result = self._create_result(doc_instances, filter_cfg.name)

                # Compute metrics for this filter
                for metric in filter_cfg.metric_list:
                    score = self._compute_metric(result, metric)
                    sample_scores[(metric.name, filter_cfg.name)].append(score)

        self._sample_scores = dict(sample_scores)
        return self._sample_scores

    @abstractmethod
    def _create_result(self, instances: list[Instance], filter_name: str):
        """Create GenResult or MCResult from instances.

        Subclasses implement this to return their specific result type.
        """
        raise NotImplementedError

    @abstractmethod
    def _compute_metric(self, result, metric: MetricConfig):
        """Compute a single metric from a result object.

        Subclasses implement this to handle their specific metric interface.
        """
        raise NotImplementedError
```

### Implementation in GenerateTask

```python
class GenerateTask(Task):
    def _create_result(self, instances: list[Instance], filter_name: str):
        """Create GenResult from instances."""
        return GenResult.from_instances(instances, filter_name=filter_name)

    def _compute_metric(self, gen_result: GenResult, metric: MetricConfig):
        """Compute metric for generation task."""
        if metric.fn is None:
            return None

        # Compute for each generation
        scores = []
        for generation in gen_result.results:
            try:
                score = metric.fn(
                    references=(
                        [gen_result.target]
                        if not isinstance(gen_result.target, list)
                        else gen_result.target
                    ),
                    predictions=[generation],
                    **metric.kwargs
                )
            except TypeError:
                score = metric.fn([gen_result.target, generation])

            if isinstance(score, dict):
                # Handle metrics that return multiple values
                # For now, just take the first key (needs better handling)
                scores.append(list(score.values())[0])
            else:
                scores.append(score)

        # Return list of scores (one per generation)
        # The Task.reduce() method will handle repeat reduction later
        return scores
```

### Implementation in MultipleChoiceTask

```python
class MultipleChoiceTask(Task):
    def _create_result(self, instances: list[Instance], filter_name: str):
        """Create MCResult from instances."""
        acc_mutual_info = "acc_mutual_info" in [
            m.name for m in self.config._metric_list
        ]
        return MCResult.from_instances(instances, acc_mutual_info=acc_mutual_info)

    def _compute_metric(self, mc_result: MCResult, metric: MetricConfig):
        """Compute metric for multiple-choice task."""
        if metric.fn is None:
            return None

        # MC metrics take MCResult directly
        return metric.fn(mc_result)
```

---

## What This Fixes

### ✅ Unified Iteration Pattern
**Before**: Different iteration in each subclass
**After**: Single iteration pattern in base class:
```
for filter → for doc → create result → for metric → compute
```

### ✅ Clear Filter-Metric Relationship
**Before**: Confusion about `self.config._metric_list` vs `filter.metric_list`
**After**: **Always use `filter.metric_list`**
- Each filter has its own metrics
- Makes sense: different filters might need different metrics
- Example: "flexible-extract" might use different metrics than "strict-match"

### ✅ Separated Concerns
**Before**: `_process_instances` did everything
**After**:
- `process_instances`: handles iteration (in base class)
- `_create_result`: creates result objects (task-specific)
- `_compute_metric`: computes metrics (task-specific)

### ✅ Still Different Metric Interfaces (But That's OK!)
**Before**: Tried to force same interface, causing confusion
**After**: Accept that GenerateTask and MultipleChoiceTask use different metric signatures
- It's OK for them to be different - they ARE different!
- `_compute_metric` encapsulates the difference
- Metric writers know which signature to use based on `output_type`

---

## Comparison: Lines of Code

### Before (Current smolrefact)

**GenerateTask._process_instances**: ~75 lines
**MultipleChoiceTask._process_instances**: ~17 lines
**Total**: ~92 lines of duplicated iteration logic

### After (This proposal)

**Task.process_instances**: ~20 lines (unified, in base class)
**GenerateTask._create_result**: ~2 lines
**GenerateTask._compute_metric**: ~20 lines
**MultipleChoiceTask._create_result**: ~5 lines
**MultipleChoiceTask._compute_metric**: ~5 lines
**Total**: ~52 lines, NO duplication

---

## Migration Path

This is a **non-breaking refactor** of your existing code:

1. Move the iteration logic from `_process_instances` to base `process_instances`
2. Split out `_create_result` and `_compute_metric`
3. Delete the old `_process_instances` implementations
4. Test that everything still works

---

## Why This Is Better Than My Original Design

**My original design**:
- Added: `Scorer`, `ScoringContext`, `ScoringResult`, 3 scorer subclasses
- Created new layer of indirection: Task → Scorer → compute
- More classes to understand and maintain

**This design**:
- Adds: 2 small abstract methods
- Moves iteration to base class (removes duplication)
- Still uses your GenResult/MCResult (no new result types)
- SIMPLER, not more complex

---

## Decision: Filter-Metrics Relationship

One key decision we need to make: **Should each filter have its own metric list?**

**Option 1: Filter-specific metrics** (Recommended)
```yaml
filter_list:
  - name: strict-match
    filter: [...]
    metric_list:
      - metric: exact_match

  - name: flexible-extract
    filter: [...]
    metric_list:
      - metric: exact_match
      - metric: f1_score  # Different metrics!
```

**Pros**:
- More flexible
- Different filters can have different metrics
- Makes sense: strict extraction might just need exact_match, flexible might need fuzzy matching

**Cons**:
- More verbose in YAML
- Metrics might be duplicated across filters

**Option 2: Global metrics** (Current in GenerateTask)
```yaml
metric_list:
  - metric: exact_match
  - metric: f1_score

filter_list:
  - name: strict-match
  - name: flexible-extract
```

**Pros**:
- Less verbose
- All filters use same metrics

**Cons**:
- Less flexible
- What if different filters need different metrics?

**Recommendation**: Use **Option 1 (filter-specific)** but allow **fallback to global**:
```python
for filter_cfg in self._filters:
    # Use filter's metrics if specified, else use global
    metrics = filter_cfg.metric_list or self.config._metric_list
    for metric in metrics:
        ...
```

This gives flexibility while maintaining backward compatibility.

---

## The REAL Simplification

The key insight is: **we don't need a Scorer abstraction**.

We just need to:
1. ✅ Move iteration to base class (remove duplication)
2. ✅ Clarify filter-metric relationship (use filter.metric_list)
3. ✅ Separate result creation from metric computation (two methods)
4. ✅ Keep GenResult/MCResult as-is (already good)

This makes the code **MORE intuitive** without adding layers.

---

## Next Steps

Should I:
1. **Implement this minimal version** on smolrefact
2. **Update the existing code** to use this pattern
3. **Test it** to make sure it works
4. **Compare** before/after to verify it's actually simpler

This should address your concern about over-abstraction. Thoughts?
