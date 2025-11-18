# Scorer Integration Design

## Executive Summary

This design introduces a **Scorer** abstraction to make sample score calculation more intuitive and modular. The Scorer separates the concerns of **filtering** (transforming model outputs) from **scoring** (computing metrics), while maintaining backwards compatibility with custom `process_results` implementations.

## Current Architecture Analysis

### Current Flow
```
Model Outputs → Filters → Task._process_instances() → Metrics → Scores
                              ↓
                    (or process_results override)
```

### Current Issues
1. **Tight Coupling**: Scoring logic is embedded in task subclasses (`GenerateTask._process_instances`, `MultipleChoiceTask._process_instances`)
2. **Dual Paths**: Two different code paths for scoring (type-specific vs. custom `process_results`)
3. **Repeated Logic**: Each task type reimplements similar metric computation patterns
4. **Filter-Metric Entanglement**: Filters carry their own metric lists, but the relationship is implicit
5. **Hard to Extend**: Adding new scoring strategies requires modifying task classes

### Key Insights from Codebase

1. **Different Output Types**:
   - `loglikelihood` → tuples of `(log_prob, is_greedy)`
   - `generate_until` → strings
   - Need different processing

2. **Filter Pipelines**:
   - Each `FilterEnsemble` has a name and applies transformations sequentially
   - Results stored in `instance.filtered_resps[filter_name]`
   - Each filter can have its own `metric_list`

3. **Result Objects**:
   - `MCResult` for multiple-choice (contains `lls`, `target`, `choices`)
   - `GenResult` for generation (contains `results`, `target`, `instances`)

4. **Custom process_results**:
   - Can be overridden in task configs arbitrarily
   - Currently bypasses the type-specific logic entirely

## Proposed Design: Scorer Architecture

### Design Principles

1. **Separation of Concerns**: Filtering transforms outputs, Scoring computes metrics
2. **Type Safety**: Leverage Python's type system for different output types
3. **Composability**: Mix and match scorers, filters, and metrics
4. **Backwards Compatibility**: Support existing `process_results` overrides
5. **Extensibility**: Easy to add new scoring strategies

### Core Abstraction: The Scorer

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from dataclasses import dataclass

# Type variables for different result types
ResultT = TypeVar('ResultT', bound='Results')

class Scorer(ABC, Generic[ResultT]):
    """
    A Scorer computes metric scores from filtered model outputs.

    Responsibilities:
    - Convert filtered outputs into Result objects (MCResult/GenResult)
    - Apply metrics to compute scores
    - Handle repeat/aggregation logic at the sample level
    - Track which filter produced the outputs
    """

    def __init__(self, task_config: TaskConfig):
        self.config = task_config

    @abstractmethod
    def score_instances(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> ResultT:
        """
        Score a group of instances (typically same doc_id) using a specific filter.

        Args:
            instances: List of Instance objects for the same document
            filter_name: Name of the filter whose outputs to use

        Returns:
            Result object with computed scores
        """
        raise NotImplementedError

    @abstractmethod
    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """
        Get the metrics to compute for a given filter.

        Args:
            filter_name: Name of the filter

        Returns:
            List of MetricConfig objects to apply
        """
        raise NotImplementedError


class ProcessResultsScorer(Scorer):
    """
    Scorer that delegates to custom process_results function.

    This handles the legacy/custom scoring path where tasks define their own
    process_results method. It maintains backwards compatibility.
    """

    def __init__(self, task_config: TaskConfig, process_results_fn: Callable):
        super().__init__(task_config)
        self.process_results_fn = process_results_fn

    def score_instances(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> dict[str, Any]:
        """Delegate to custom process_results function."""
        # Create a Result object to extract doc and filtered results
        result = Results.create(instances, filter_name)

        # Call custom process_results
        scores = self.process_results_fn(
            result.doc,
            [result.results[filter_name]]
        )

        return scores or {}

    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """
        For custom process_results, we don't know the metrics ahead of time.
        Return empty list and use mean aggregation as default.
        """
        return []


class GenerationScorer(Scorer[GenResult]):
    """
    Scorer for generation tasks (generate_until).

    Handles:
    - String outputs (generated text)
    - Reference-based metrics (BLEU, ROUGE, exact match, etc.)
    - Repeat reduction if configured
    """

    def score_instances(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> GenResult:
        """Score generation instances."""
        # Create GenResult from instances
        gen_result = GenResult.from_instances(instances, filter_name)
        gen_result.repeats = self.config.repeat_cfg.repeats

        # Get metrics for this filter
        metrics = self.get_metrics(filter_name)

        # Compute metrics
        gen_result.scores = self._compute_metrics(gen_result, metrics)

        return gen_result

    def _compute_metrics(
        self,
        gen_result: GenResult,
        metrics: list[MetricConfig]
    ) -> dict[str, list[float]]:
        """Compute all metrics for a GenResult."""
        from collections import defaultdict

        scores = defaultdict(list)
        gold = gen_result.target

        # Compute metric for each generation
        for generation in gen_result.results:
            for metric in metrics:
                if metric.fn is None:
                    continue

                try:
                    score = metric.fn(
                        references=[gold] if not isinstance(gold, list) else gold,
                        predictions=[generation],
                        **metric.kwargs,
                    )
                except TypeError:
                    # Handle metrics with different interfaces
                    score = metric.fn([gold, generation])

                # Handle metrics that return dicts (multiple metrics at once)
                if isinstance(score, dict):
                    for k, v in score.items():
                        scores[k].append(v)
                else:
                    scores[metric.name].append(score)

        return dict(scores)

    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """Get metrics for this filter from task config."""
        # Find the FilterConfig for this filter_name
        for filter_config in self.config.get_filters():
            if filter_config.name == filter_name:
                return filter_config.metric_list

        # Fallback to task-level metrics
        return self.config._metric_list


class LoglikelihoodScorer(Scorer[MCResult]):
    """
    Scorer for loglikelihood/multiple-choice tasks.

    Handles:
    - Loglikelihood outputs (log probabilities)
    - Choice-based metrics (accuracy, Brier score, etc.)
    - Mutual information if configured
    """

    def score_instances(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> MCResult:
        """Score multiple-choice instances."""
        # Create MCResult from instances
        mc_result = MCResult.from_instances(instances)

        # Get metrics for this filter
        metrics = self.get_metrics(filter_name)

        # Compute metrics
        mc_result.scores = self._compute_metrics(mc_result, metrics)

        return mc_result

    def _compute_metrics(
        self,
        mc_result: MCResult,
        metrics: list[MetricConfig]
    ) -> dict[str, float]:
        """Compute all metrics for an MCResult."""
        scores = {}

        for metric in metrics:
            if metric.fn is None:
                continue

            # MC metrics take the entire MCResult as input
            score = metric.fn(mc_result)

            # Handle metrics that return dicts
            if isinstance(score, dict):
                scores.update(score)
            else:
                scores[metric.name] = score

        return scores

    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """Get metrics for this filter from task config."""
        # Find the FilterConfig for this filter_name
        for filter_config in self.config.get_filters():
            if filter_config.name == filter_name:
                return filter_config.metric_list

        # Fallback to task-level metrics
        return self.config._metric_list


class ScorerFactory:
    """
    Factory for creating the appropriate Scorer based on task configuration.

    Decision tree:
    1. If process_results is defined → ProcessResultsScorer
    2. Elif output_type is generate_until → GenerationScorer
    3. Elif output_type is loglikelihood → LoglikelihoodScorer
    4. Else → raise error
    """

    @staticmethod
    def create_scorer(task_config: TaskConfig) -> Scorer:
        """Create appropriate scorer for task configuration."""

        # Check for custom process_results first
        if callable(task_config.process_results):
            return ProcessResultsScorer(task_config, task_config.process_results)

        # Create type-specific scorer
        output_type = task_config.output_type

        if output_type == "generate_until":
            return GenerationScorer(task_config)
        elif output_type in ("loglikelihood", "multiple_choice"):
            return LoglikelihoodScorer(task_config)
        elif output_type == "loglikelihood_rolling":
            # Could add PerplexityScorer here
            raise NotImplementedError(f"Scorer for {output_type} not yet implemented")
        else:
            raise ValueError(f"Unknown output_type: {output_type}")
```

### Integration with Task Class

```python
class Task(ABC):
    """Base task class with Scorer integration."""

    def __init__(self, config: TaskConfig):
        self.config = config
        self._instances: list[Instance] = []
        self._filters: list[FilterConfig] = config.get_filters()
        self._sample_scores: dict[tuple[str, str], list] = defaultdict(list)

        # Create scorer during initialization
        self._scorer: Scorer = ScorerFactory.create_scorer(config)

    def process_instances(self, instances: list[Instance] | None = None):
        """
        Process instances to compute metrics.

        This is now a simple orchestration method that:
        1. Groups instances by doc_id
        2. For each filter, delegates scoring to the Scorer
        3. Collects results
        """
        _instances = self.sort_instances(instances or self._instances)
        if not _instances:
            return {}

        results = defaultdict(list)

        # Iterate over filters
        for filter_config in self._filters:
            filter_name = filter_config.name

            # Score each document's instances
            for doc_instances in _instances.values():
                # Delegate to scorer
                scored_result = self._scorer.score_instances(
                    doc_instances,
                    filter_name
                )

                # Collect scores
                if isinstance(scored_result, dict):
                    # ProcessResultsScorer returns dict directly
                    for metric, value in scored_result.items():
                        results[(metric, filter_name)].append(value)
                else:
                    # Type-specific scorers return Result objects
                    for metric, score in scored_result.scores.items():
                        results[(metric, filter_name)].append(score)

        self._sample_scores = results
        return results

    # Remove _process_instances from Task base class
    # It's now handled by Scorers


# Simplified task subclasses
class GenerateTask(Task):
    OUTPUT_TYPE = "generate_until"

    # Only needs construct_requests now
    # Scoring logic moved to GenerationScorer


class MultipleChoiceTask(Task):
    OUTPUT_TYPE = "loglikelihood"

    # Only needs construct_requests now
    # Scoring logic moved to LoglikelihoodScorer
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Model Execution                                              │
│    lm.generate_until(reqs) → instance.resps = ["output1", ...] │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Apply Filters                                                │
│    For each FilterEnsemble:                                     │
│      - Extract all instance.resps                               │
│      - Apply filter pipeline (regex, lowercase, etc.)           │
│      - Store in instance.filtered_resps[filter_name]            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Process Instances (NEW with Scorer)                          │
│    task.process_instances(instances)                            │
│      ├─ Group by doc_id                                         │
│      ├─ For each filter:                                        │
│      │   └─ For each document:                                  │
│      │       ├─ scorer.score_instances(doc_insts, filter_name)  │
│      │       │   ├─ Create Result object (MC/Gen)               │
│      │       │   ├─ Get metrics for this filter                 │
│      │       │   ├─ Apply each metric to filtered outputs       │
│      │       │   └─ Return Result with scores                   │
│      │       └─ Collect scores by (metric, filter)              │
│      └─ Store in task._sample_scores                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Aggregate Scores                                             │
│    task.compute_aggregations(sample_scores)                     │
│      └─ Apply aggregation_fn to each metric's scores            │
└─────────────────────────────────────────────────────────────────┘
```

## Benefits of This Design

### 1. Separation of Concerns
- **Filters**: Transform outputs (regex extraction, lowercasing, etc.)
- **Scorers**: Compute metrics from transformed outputs
- **Tasks**: Orchestrate the flow, define what to compute

### 2. Extensibility
Adding new scoring strategies is easy:

```python
class BeamSearchScorer(GenerationScorer):
    """Scorer for beam search outputs with diversity metrics."""

    def _compute_metrics(self, gen_result, metrics):
        scores = super()._compute_metrics(gen_result, metrics)

        # Add diversity metrics
        scores['diversity'] = self._compute_diversity(gen_result.results)
        scores['n_unique'] = len(set(gen_result.results))

        return scores
```

### 3. Backwards Compatibility
- Existing tasks with `process_results` continue to work via `ProcessResultsScorer`
- No breaking changes to task configs
- Gradual migration path

### 4. Type Safety
- Generic types ensure correct Result types
- Clearer interfaces between components
- Better IDE support and type checking

### 5. Testability
- Can test scorers independently
- Mock different components easily
- Clear contract for each piece

### 6. Filter-Metric Clarity
- Each scorer knows how to get metrics for a filter
- Explicit handling of filter-specific metrics
- No hidden dependencies

## Migration Path

### Phase 1: Add Scorer Classes (Backwards Compatible)
1. Add `Scorer` base class and implementations
2. Add `ScorerFactory`
3. Keep existing `_process_instances` methods

### Phase 2: Refactor Task.process_instances
1. Update `Task.process_instances` to use scorer
2. Deprecate `_process_instances` abstract method
3. Add tests for new path

### Phase 3: Migrate Task Subclasses
1. Remove `_process_instances` from `GenerateTask`
2. Remove `_process_instances` from `MultipleChoiceTask`
3. Simplify task classes to only handle `construct_requests`

### Phase 4: Cleanup
1. Remove deprecated code
2. Update documentation
3. Add examples for custom scorers

## Advanced Features (Future Extensions)

### 1. Ensemble Scoring
```python
class EnsembleScorer(Scorer):
    """Combine scores from multiple scorers."""

    def __init__(self, scorers: list[Scorer], weights: list[float]):
        self.scorers = scorers
        self.weights = weights

    def score_instances(self, instances, filter_name):
        results = [s.score_instances(instances, filter_name) for s in self.scorers]
        return self._weighted_average(results)
```

### 2. LLM-as-Judge Scorer
```python
class LLMJudgeScorer(GenerationScorer):
    """Use an LLM to score generations."""

    def __init__(self, task_config, judge_model: str):
        super().__init__(task_config)
        self.judge_lm = get_model(judge_model)

    def _compute_metrics(self, gen_result, metrics):
        scores = super()._compute_metrics(gen_result, metrics)

        # Add LLM judge score
        judge_scores = []
        for generation in gen_result.results:
            prompt = self._create_judge_prompt(generation, gen_result.target)
            score = self.judge_lm.evaluate(prompt)
            judge_scores.append(score)

        scores['llm_judge'] = judge_scores
        return scores
```

### 3. Reward Model Scorer
```python
class RewardModelScorer(GenerationScorer):
    """Use a reward model to score generations."""

    def __init__(self, task_config, reward_model_path: str):
        super().__init__(task_config)
        self.reward_model = load_reward_model(reward_model_path)

    def _compute_metrics(self, gen_result, metrics):
        scores = super()._compute_metrics(gen_result, metrics)

        # Add reward model scores
        reward_scores = self.reward_model.score(
            prompts=[inst.args[0] for inst in gen_result.instances],
            generations=gen_result.results
        )

        scores['reward'] = reward_scores
        return scores
```

### 4. Multi-Filter Aware Scoring
```python
class CrossFilterScorer(Scorer):
    """Compute metrics that compare across different filters."""

    def score_instances(self, instances, filter_name):
        # Get results from ALL filters
        all_filtered_results = {
            fname: [inst.filtered_resps[fname] for inst in instances]
            for fname in instances[0].filtered_resps.keys()
        }

        # Compute agreement metrics
        scores = {
            'filter_agreement': self._compute_agreement(all_filtered_results),
            'filter_diversity': self._compute_diversity(all_filtered_results),
        }

        return scores
```

## Configuration Examples

### YAML Config with Multiple Filters and Metrics

```yaml
task: my_custom_task
output_type: generate_until

# Multiple filter pipelines with different metrics
filter_list:
  - name: strict-match
    filter:
      - function: regex
        regex_pattern: "Answer: (.*)"
        group_select: 1
      - function: lowercase
    metric_list:
      - metric: exact_match
        aggregation: mean
      - metric: f1_score
        aggregation: mean

  - name: flexible-extract
    filter:
      - function: regex
        regex_pattern: "([A-Za-z]+)"
        group_select: 0
      - function: lowercase
    metric_list:
      - metric: exact_match
        aggregation: mean
      - metric: bleu
        aggregation: mean

  - name: no-filter
    filter:
      - function: take_first
    metric_list:
      - metric: rouge
        aggregation: mean

# This would use the default GenerationScorer
# Or you could specify a custom scorer:
# scorer: "my_custom_scorer"  # Future extension
```

### Custom Scorer in Task Config

```python
# In a custom task YAML or Python config
from lm_eval.api.scorer import GenerationScorer

class MyCustomScorer(GenerationScorer):
    def _compute_metrics(self, gen_result, metrics):
        # Add custom logic
        scores = super()._compute_metrics(gen_result, metrics)
        scores['custom_metric'] = self._my_custom_metric(gen_result)
        return scores

# Register it
from lm_eval.api.scorer import SCORER_REGISTRY
SCORER_REGISTRY['my_custom'] = MyCustomScorer

# Then in YAML:
# task: my_task
# output_type: generate_until
# scorer: my_custom
```

## Implementation Checklist

- [ ] Create `lm_eval/api/scorer.py` with base classes
- [ ] Implement `ProcessResultsScorer`
- [ ] Implement `GenerationScorer`
- [ ] Implement `LoglikelihoodScorer`
- [ ] Implement `ScorerFactory`
- [ ] Update `Task.process_instances` to use scorer
- [ ] Add scorer initialization in `Task.__init__`
- [ ] Add tests for each scorer type
- [ ] Add integration tests
- [ ] Update documentation
- [ ] Add migration guide
- [ ] Deprecate `_process_instances` in task subclasses
- [ ] Add examples for custom scorers

## Open Questions

1. **Scorer Registry**: Should we have a registry for custom scorers like we do for filters/metrics?
2. **Filter Dependencies**: Should scorers be able to request specific filters?
3. **Caching**: Should we cache scorer results for the same instances?
4. **Parallel Scoring**: Can we parallelize scoring across filters/docs?
5. **Result Storage**: Should we store full Result objects or just scores?

## Summary

This design provides a clean, extensible architecture for scoring that:

- ✅ Separates filtering from scoring
- ✅ Handles different output types uniformly
- ✅ Maintains backwards compatibility
- ✅ Makes filter-metric relationships explicit
- ✅ Supports custom process_results
- ✅ Enables advanced scoring strategies
- ✅ Improves testability and maintainability

The key insight is that **Scorers are responsible for converting filtered outputs into metric scores**, which is a distinct responsibility from both filtering and aggregation.
