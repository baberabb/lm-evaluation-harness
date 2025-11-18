# Scorer Design: Intuitive Sample Score Calculation

## Executive Summary

This document proposes a new `Scorer` abstraction to make sample score calculation more intuitive, maintainable, and extensible in the lm-evaluation-harness library.

## Current Problems

### 1. Mixed Responsibilities
The current `Task` class handles too many concerns:
- Request construction
- Filter application
- Metric computation
- Score aggregation
- Custom `process_results` handling

This violates the Single Responsibility Principle and makes the code hard to understand and maintain.

### 2. Inconsistent Metric Interfaces
Different task types use different metric signatures:
- **GenerateTask**: `metric.fn(references=[...], predictions=[...], **kwargs)`
- **MultipleChoiceTask**: `metric.fn(MCResult)`
- **Custom process_results**: `fn(doc, results) -> dict[metric_name, score]`

This inconsistency makes it difficult to write generic metrics or understand how scoring works.

### 3. Unclear Filter-Metric Relationship
The relationship between filters and metrics is complex:
- Filters can have associated metric lists
- Metrics can be computed for multiple filters
- The iteration pattern varies (sometimes over filters, sometimes over metrics)
- Difficult to track which filter's output feeds which metric

### 4. Difficult to Extend
Adding a new task type requires:
- Implementing complex `_process_instances` logic
- Understanding the filter-metric dance
- Handling edge cases for custom `process_results`

### 5. Code Duplication
`GenerateTask` and `MultipleChoiceTask` have similar but duplicated scoring logic.

---

## Proposed Solution: Scorer Architecture

### Core Principle
**Separation of Concerns**: Scoring should be independent from task definition. A `Scorer` is responsible for:
1. Iterating over filter-metric pairs
2. Creating appropriate result objects (GenResult/MCResult)
3. Computing metrics
4. Returning structured scores

### Key Design Goals

1. **Single Responsibility**: Task defines *what* to evaluate, Scorer defines *how* to score
2. **Consistent Interface**: All scorers implement the same protocol
3. **Explicit Relationships**: Filter-metric relationships are clear and traceable
4. **Backward Compatible**: Supports existing `process_results` overrides
5. **Extensible**: Easy to add new task types and metrics
6. **Type Safe**: Leverages Python type system for correctness

---

## Architecture Overview

### Class Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                         Scorer (ABC)                         │
│  + score(instances, task_config) -> ScoringResult           │
│  # _prepare_data(instances, filter) -> Any                  │
│  # _compute_metrics(data, metrics) -> dict                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┬────────────────────┐
          │                         │                    │
┌─────────▼──────────┐  ┌──────────▼────────┐  ┌────────▼──────────┐
│  GenerateScorer    │  │ MultiChoiceScorer │  │  CustomScorer     │
│                    │  │                   │  │  (process_results)│
│ Handles:           │  │ Handles:          │  │                   │
│ - GenResult        │  │ - MCResult        │  │ Handles:          │
│ - String metrics   │  │ - Likelihood      │  │ - Arbitrary       │
│ - Exact match,etc. │  │   metrics         │  │   custom logic    │
└────────────────────┘  │ - acc, acc_norm   │  │ - Legacy compat   │
                        └───────────────────┘  └───────────────────┘

Supporting Data Classes:
┌──────────────────────────────────────────────────────────────┐
│ ScoringContext                                               │
│ - instances: list[Instance]                                  │
│ - filter: FilterConfig                                       │
│ - metrics: list[MetricConfig]                                │
│ - task_config: TaskConfig                                    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ ScoringResult                                                │
│ - sample_scores: dict[(metric, filter), list[float]]        │
│ - metadata: dict (optional debug info)                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Design

### 1. Scorer Base Class

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class ScoringContext:
    """Context for a single scoring operation.

    Encapsulates all data needed to score instances for one filter.
    """
    instances: list[Instance]
    filter: FilterConfig
    task_config: TaskConfig

    @property
    def filter_name(self) -> str:
        return self.filter.name

    @property
    def metrics(self) -> list[MetricConfig]:
        return self.filter.metric_list


@dataclass
class ScoringResult:
    """Result of scoring operation.

    Maps (metric_name, filter_name) -> list of sample scores.
    """
    sample_scores: dict[tuple[str, str], list[float]]
    metadata: dict[str, Any] = field(default_factory=dict)

    def merge(self, other: 'ScoringResult') -> 'ScoringResult':
        """Merge two scoring results."""
        merged_scores = {**self.sample_scores, **other.sample_scores}
        merged_metadata = {**self.metadata, **other.metadata}
        return ScoringResult(merged_scores, merged_metadata)


class Scorer(ABC):
    """Base class for scoring instances.

    A Scorer is responsible for:
    1. Taking instances with filtered responses
    2. Computing metrics for each filter-metric pair
    3. Returning structured scores

    The scoring process is separated into:
    - Data preparation (creating Result objects)
    - Metric computation (applying metric functions)
    """

    @abstractmethod
    def score(
        self,
        instances: list[Instance],
        task_config: TaskConfig
    ) -> ScoringResult:
        """Score instances using task configuration.

        Args:
            instances: List of instances (sorted by doc_id)
            task_config: Task configuration with filters and metrics

        Returns:
            ScoringResult with sample scores for each (metric, filter) pair
        """
        raise NotImplementedError

    def _validate_instances(self, instances: list[Instance]) -> None:
        """Validate that instances are appropriate for this scorer."""
        if not instances:
            raise ValueError("Cannot score empty instances")

    def _iterate_scoring_contexts(
        self,
        instances: list[Instance],
        task_config: TaskConfig
    ) -> Iterator[ScoringContext]:
        """Generate scoring contexts for each filter.

        Yields one context per filter, containing the instances and
        associated metrics for that filter.
        """
        for filter_cfg in task_config._filter_list:
            yield ScoringContext(
                instances=instances,
                filter=filter_cfg,
                task_config=task_config
            )
```

### 2. GenerateScorer

```python
class GenerateScorer(Scorer):
    """Scorer for generation tasks (generate_until output type).

    Handles:
    - Creating GenResult objects from filtered responses
    - Computing string-based metrics (exact_match, BLEU, etc.)
    - Handling multiple generations per document (repeats, temperature)
    """

    def score(
        self,
        instances_by_doc: dict[int, list[Instance]],
        task_config: TaskConfig
    ) -> ScoringResult:
        """Score generation instances.

        For each document and filter:
        1. Create GenResult from filtered responses
        2. Apply each metric to the generated texts
        3. Collect scores
        """
        all_scores = defaultdict(list)

        # Iterate over each filter
        for context in self._iterate_scoring_contexts(
            list(instances_by_doc.values()),
            task_config
        ):
            # Process each document
            for doc_id, instances in instances_by_doc.items():
                # Create GenResult for this filter
                gen_result = self._create_gen_result(
                    instances,
                    context.filter_name
                )

                # Compute metrics
                scores = self._compute_metrics(gen_result, context.metrics)

                # Store with (metric, filter) key
                for metric_name, score_value in scores.items():
                    key = (metric_name, context.filter_name)
                    all_scores[key].append(score_value)

        return ScoringResult(sample_scores=dict(all_scores))

    def _create_gen_result(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> GenResult:
        """Create GenResult from instances for a specific filter."""
        return GenResult.from_instances(instances, filter_name=filter_name)

    def _compute_metrics(
        self,
        gen_result: GenResult,
        metrics: list[MetricConfig]
    ) -> dict[str, Any]:
        """Compute all metrics for a GenResult.

        Returns:
            dict mapping metric_name -> score(s)

        Note: For generation tasks with multiple samples, may return
        list of scores (one per generation).
        """
        scores = {}

        for metric in metrics:
            if metric.fn is None:
                continue

            # Compute metric for each generation
            metric_scores = []
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
                    # Fallback for metrics with different signature
                    score = metric.fn([gen_result.target, generation])

                # Handle metrics that return dicts
                if isinstance(score, dict):
                    for k, v in score.items():
                        if k not in scores:
                            scores[k] = []
                        scores[k].append(v)
                else:
                    metric_scores.append(score)

            # Store scores under metric name
            if metric_scores:  # Only if we didn't handle dict case
                scores[metric.name] = metric_scores

        return scores
```

### 3. MultipleChoiceScorer

```python
class MultipleChoiceScorer(Scorer):
    """Scorer for multiple-choice tasks (loglikelihood output type).

    Handles:
    - Creating MCResult objects from log-likelihoods
    - Computing accuracy metrics (acc, acc_norm, etc.)
    - Handling mutual information
    """

    def score(
        self,
        instances_by_doc: dict[int, list[Instance]],
        task_config: TaskConfig
    ) -> ScoringResult:
        """Score multiple-choice instances.

        For each document:
        1. Create MCResult from all choice instances
        2. For each filter-metric pair:
           - Apply metric to MCResult
           - Store score
        """
        all_scores = defaultdict(list)

        # Process each document
        for doc_id, instances in instances_by_doc.items():
            # Create MCResult (same for all filters, uses raw loglikelihoods)
            mc_result = MCResult.from_instances(
                instances,
                acc_mutual_info="acc_mutual_info" in [
                    m.name for m in task_config._metric_list
                ]
            )

            # Compute metrics for each filter-metric pair
            for context in self._iterate_scoring_contexts([instances], task_config):
                for metric in context.metrics:
                    if metric.fn is None:
                        continue

                    # Apply metric
                    score = metric.fn(mc_result)

                    # Store
                    key = (metric.name, context.filter_name)
                    all_scores[key].append(score)

        return ScoringResult(sample_scores=dict(all_scores))
```

### 4. CustomScorer

```python
class CustomScorer(Scorer):
    """Scorer for tasks with custom process_results.

    Provides backward compatibility for tasks that define their own
    scoring logic via process_results function.

    This scorer:
    1. Extracts filtered responses for each filter
    2. Calls process_results(doc, filtered_results)
    3. Returns the metrics dict
    """

    def __init__(self, process_results_fn: Callable):
        self.process_results_fn = process_results_fn

    def score(
        self,
        instances_by_doc: dict[int, list[Instance]],
        task_config: TaskConfig
    ) -> ScoringResult:
        """Score using custom process_results function."""
        all_scores = defaultdict(list)

        # Process each filter
        for filter_cfg in task_config._filter_list:
            filter_name = filter_cfg.name

            # Process each document
            for doc_id, instances in instances_by_doc.items():
                # Create Results object for this filter
                # (maintains backward compatibility with existing code)
                result = Results.create(instances, filter_name)

                # Call custom process_results
                metrics = self.process_results_fn(
                    result.doc,
                    [result.results[filter_name]]
                )

                # Store scores
                if metrics is not None:
                    for metric_name, score in metrics.items():
                        key = (metric_name, filter_name)
                        all_scores[key].append(score)

        return ScoringResult(sample_scores=dict(all_scores))
```

---

## Integration with Task Class

### Modified Task Class

```python
class Task(ABC):
    """Base task class with integrated Scorer."""

    def __init__(self, config: TaskConfig):
        self.config = config
        self._filters = config.get_filters()
        self._instances = []
        self._sample_scores = {}

        # Create appropriate scorer
        self._scorer = self._create_scorer()

    def _create_scorer(self) -> Scorer:
        """Factory method to create appropriate scorer.

        Hierarchy:
        1. If custom process_results exists -> CustomScorer
        2. Otherwise, use task-type specific scorer
        """
        if callable(self.config.process_results):
            return CustomScorer(self.config.process_results)

        # Subclasses can override to provide type-specific scorer
        return self._get_default_scorer()

    @abstractmethod
    def _get_default_scorer(self) -> Scorer:
        """Get default scorer for this task type."""
        raise NotImplementedError

    def process_instances(
        self,
        instances: list[Instance] | None = None
    ) -> dict[tuple[str, str], list[float]]:
        """Process instances to compute metrics.

        This is now a simple delegation to the scorer.
        """
        instances = instances or self._instances
        if not instances:
            return {}

        # Sort instances by doc_id
        instances_by_doc = self.sort_instances(instances)

        # Delegate to scorer
        result = self._scorer.score(instances_by_doc, self.config)

        # Store and return
        self._sample_scores = result.sample_scores
        return result.sample_scores

    # Other methods remain the same...
    # construct_requests, build_all_requests, etc.
```

### Task Subclasses

```python
class GenerateTask(Task):
    OUTPUT_TYPE = "generate_until"

    def _get_default_scorer(self) -> Scorer:
        return GenerateScorer()

    # construct_requests remains the same
    # No need for _process_instances anymore!


class MultipleChoiceTask(Task):
    OUTPUT_TYPE = "loglikelihood"

    def _get_default_scorer(self) -> Scorer:
        return MultipleChoiceScorer()

    # construct_requests remains the same
    # No need for _process_instances anymore!
```

---

## Benefits of This Design

### 1. Separation of Concerns
- **Task**: Defines what to evaluate (dataset, prompts, choices)
- **Scorer**: Defines how to score (metrics, filters, aggregation)
- **Filter**: Transforms model outputs
- **Metric**: Computes score from processed outputs

### 2. Consistent Interface
All scorers implement the same `score()` method with the same signature. Makes it easy to:
- Test scorers in isolation
- Swap scorers for different task types
- Add new scorers without changing Task code

### 3. Explicit Filter-Metric Flow
```
Instances → Scorer.score()
    ↓
For each filter:
    ↓
Create Result object (GenResult/MCResult)
    ↓
For each metric:
    ↓
Compute metric(result)
    ↓
Store in (metric, filter) → [scores]
```

### 4. Easy to Extend
Adding a new task type:
```python
class MyNewTask(Task):
    OUTPUT_TYPE = "my_new_type"

    def _get_default_scorer(self) -> Scorer:
        return MyNewScorer()  # Just provide a scorer!

    # construct_requests only - no scoring logic needed

class MyNewScorer(Scorer):
    def score(self, instances_by_doc, task_config):
        # Implement your scoring logic
        ...
```

### 5. Backward Compatible
Existing tasks with `process_results` automatically use `CustomScorer` - no changes needed!

### 6. Testable
Each component can be tested independently:
- Test scorers with mock instances
- Test metrics in isolation
- Test filters separately

### 7. Clear Error Messages
Errors occur in specific components, making debugging easier:
- `GenerateScorer.score()` error → issue with generation scoring
- `metric.fn()` error → issue with specific metric
- `filter.apply()` error → issue with filtering

---

## Migration Path

### Phase 1: Add Scorer Infrastructure (Non-Breaking)
1. Add `Scorer` base class and subclasses
2. Add `ScoringContext` and `ScoringResult` data classes
3. Keep existing `_process_instances` methods

### Phase 2: Integrate with Task (Non-Breaking)
1. Add `_scorer` field to Task
2. Add `_create_scorer()` method
3. Modify `process_instances()` to delegate to scorer
4. Keep `_process_instances` as fallback

### Phase 3: Migrate Task Subclasses
1. Implement `_get_default_scorer()` in GenerateTask
2. Implement `_get_default_scorer()` in MultipleChoiceTask
3. Test thoroughly

### Phase 4: Deprecate Old Methods
1. Mark `_process_instances` as deprecated
2. Add warnings when old methods are used

### Phase 5: Clean Up
1. Remove deprecated methods
2. Update documentation

---

## Example Usage

### For a Standard Task (No Custom Scoring)

```python
# Task definition (YAML)
task: gsm8k
output_type: generate_until
filter_list:
  - name: strict-match
    filter:
      - function: regex
        regex_pattern: The answer is (\-?[0-9\.\,]+).
    metric_list:
      - metric: exact_match

# What happens:
# 1. Task.__init__ creates GenerateScorer (no custom process_results)
# 2. Task.process_instances() calls scorer.score()
# 3. GenerateScorer:
#    - Creates GenResult for "strict-match" filter
#    - Computes exact_match metric
#    - Returns {("exact_match", "strict-match"): [1.0, 0.0, ...]}
```

### For a Custom Task (With process_results)

```python
# Task definition
def my_custom_process_results(doc, results):
    # Custom logic
    answer = extract_answer(results[0])
    return {
        "my_metric": 1.0 if answer == doc["answer"] else 0.0
    }

task_config = TaskConfig(
    process_results=my_custom_process_results,
    ...
)

# What happens:
# 1. Task.__init__ creates CustomScorer(my_custom_process_results)
# 2. Task.process_instances() calls scorer.score()
# 3. CustomScorer:
#    - Calls my_custom_process_results for each doc
#    - Returns {("my_metric", filter_name): [1.0, 0.0, ...]}
```

---

## Implementation Checklist

- [ ] Create `lm_eval/api/scorer.py` with base classes
- [ ] Implement `Scorer`, `ScoringContext`, `ScoringResult`
- [ ] Implement `GenerateScorer`
- [ ] Implement `MultipleChoiceScorer`
- [ ] Implement `CustomScorer`
- [ ] Modify `Task` class to use scorer
- [ ] Update `GenerateTask` with `_get_default_scorer()`
- [ ] Update `MultipleChoiceTask` with `_get_default_scorer()`
- [ ] Add unit tests for each scorer
- [ ] Add integration tests
- [ ] Update documentation
- [ ] Add migration guide

---

## Alternative Considered

### Alternative 1: Keep Scoring in Task
**Rejected**: Violates SRP, hard to test, duplicates code

### Alternative 2: Use Strategy Pattern Without Scorer Class
**Rejected**: Less structured, harder to add cross-cutting concerns

### Alternative 3: Make Metrics Objects Handle Everything
**Rejected**: Metrics should be stateless functions, not orchestrators

---

## Conclusion

The Scorer architecture provides:
- ✅ **Clarity**: Explicit separation between task definition and scoring
- ✅ **Consistency**: Unified interface for all scorers
- ✅ **Extensibility**: Easy to add new task types and metrics
- ✅ **Maintainability**: Each component has a single, clear responsibility
- ✅ **Compatibility**: Supports existing `process_results` pattern
- ✅ **Testability**: Components can be tested in isolation

This design makes sample score calculation intuitive and maintainable while preserving backward compatibility.
