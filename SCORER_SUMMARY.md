# Scorer Integration - Executive Summary

## The Problem

Your current implementation has scoring logic embedded in task subclasses (`GenerateTask._process_instances`, `MultipleChoiceTask._process_instances`), which makes it:
- Hard to understand the relationship between filters and metrics
- Difficult to extend with custom scoring strategies
- Unclear how `process_results` overrides interact with the type-specific logic
- Tightly coupled, reducing flexibility

## The Solution: Scorer Architecture

Introduce a **Scorer** abstraction that separates concerns:

```
Filters  → Transform outputs (regex, lowercase, etc.)
Scorers  → Compute metrics from transformed outputs
Tasks    → Orchestrate the flow
```

## Core Design

### 1. Base Scorer Class
```python
class Scorer(ABC):
    def score_instances(self, instances: list[Instance], filter_name: str) -> ResultT:
        """Score instances using a specific filter's outputs."""
        raise NotImplementedError

    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """Get metrics to compute for this filter."""
        # Returns the right metrics for each filter
```

### 2. Three Concrete Implementations

**ProcessResultsScorer**: For legacy/custom `process_results` functions
```python
class ProcessResultsScorer(Scorer):
    # Delegates to custom process_results
    # Maintains backwards compatibility
```

**GenerationScorer**: For `generate_until` tasks
```python
class GenerationScorer(Scorer[GenResult]):
    # Creates GenResult from instances
    # Applies reference-based metrics (BLEU, ROUGE, etc.)
    # Handles repeats
```

**LoglikelihoodScorer**: For `loglikelihood`/multiple-choice tasks
```python
class LoglikelihoodScorer(Scorer[MCResult]):
    # Creates MCResult from instances
    # Applies choice-based metrics (accuracy, Brier score, etc.)
```

### 3. Factory Pattern
```python
class ScorerFactory:
    @staticmethod
    def create_scorer(task_config: TaskConfig) -> Scorer:
        if callable(task_config.process_results):
            return ProcessResultsScorer(...)
        elif task_config.output_type == "generate_until":
            return GenerationScorer(...)
        elif task_config.output_type == "loglikelihood":
            return LoglikelihoodScorer(...)
```

### 4. Integration with Task
```python
class Task(ABC):
    def __init__(self, config):
        # Create scorer during initialization
        self._scorer = ScorerFactory.create_scorer(config)

    def process_instances(self, instances):
        # Simple orchestration
        for filter in self._filters:
            for doc_instances in grouped_instances:
                # Delegate to scorer
                result = self._scorer.score_instances(doc_instances, filter.name)
                # Collect scores
```

## Data Flow

```
1. Model outputs → instance.resps
2. Filters transform → instance.filtered_resps[filter_name]
3. Scorer creates Result → GenResult/MCResult
4. Scorer applies metrics → result.scores
5. Task collects scores → task._sample_scores
6. Aggregation → final metrics
```

## Key Benefits

### 1. Separation of Concerns
- **Filters**: Only transform outputs (no scoring)
- **Scorers**: Only compute metrics (no filtering)
- **Tasks**: Only orchestrate (no implementation details)

### 2. Clear Filter-Metric Relationship
```yaml
filter_list:
  - name: "strict"
    filter: [regex, lowercase]
    metric_list: [exact_match, f1]  # These metrics use "strict" filter

  - name: "lenient"
    filter: [take_first]
    metric_list: [bleu, rouge]  # These metrics use "lenient" filter
```

The Scorer knows: `get_metrics("strict")` → `[exact_match, f1]`

### 3. Easy Extensibility
```python
class RewardModelScorer(GenerationScorer):
    def _compute_metrics(self, gen_result, metrics):
        scores = super()._compute_metrics(gen_result, metrics)
        scores['reward'] = self.reward_model.score(gen_result.results)
        return scores
```

### 4. Backwards Compatibility
- Existing `process_results` work via `ProcessResultsScorer`
- No breaking changes to task configs
- Gradual migration path

### 5. Type Safety
- Generic types ensure correct Result types
- Clear interfaces
- Better IDE support

## Example Use Cases

### Use Case 1: Multiple Filters with Different Metrics
```yaml
task: gsm8k_cot
output_type: generate_until

filter_list:
  - name: strict-match
    filter:
      - function: regex
        pattern: "Answer: (\\d+)"
    metric_list:
      - metric: exact_match

  - name: flexible-extract
    filter:
      - function: regex
        pattern: "(\\d+)"
    metric_list:
      - metric: exact_match
      - metric: quasi_exact_match
```

The `GenerationScorer` automatically:
1. Applies "strict-match" filter → computes exact_match
2. Applies "flexible-extract" filter → computes exact_match + quasi_exact_match
3. Returns scores keyed by (metric, filter)

### Use Case 2: Custom Scorer with Reward Model
```python
@register_scorer("reward_model")
class RewardModelScorer(GenerationScorer):
    def __init__(self, task_config, reward_model_path: str):
        super().__init__(task_config)
        self.reward_model = load_reward_model(reward_model_path)

    def _compute_metrics(self, gen_result, metrics):
        # Standard metrics (BLEU, ROUGE, etc.)
        scores = super()._compute_metrics(gen_result, metrics)

        # Add reward model scores
        scores['reward'] = [
            self.reward_model.score(gen)
            for gen in gen_result.results
        ]
        return scores
```

### Use Case 3: LLM-as-Judge
```python
@register_scorer("llm_judge")
class LLMJudgeScorer(GenerationScorer):
    def __init__(self, task_config, judge_model: str):
        super().__init__(task_config)
        self.judge_lm = get_model(judge_model)

    def _compute_metrics(self, gen_result, metrics):
        scores = super()._compute_metrics(gen_result, metrics)

        # Add LLM judge scores
        judge_scores = []
        for generation in gen_result.results:
            prompt = f"Rate this answer (0-10): {generation}"
            score = self.judge_lm.evaluate(prompt)
            judge_scores.append(score)

        scores['llm_judge'] = judge_scores
        return scores
```

Then in YAML:
```yaml
task: my_task
output_type: generate_until
scorer: llm_judge
scorer_args:
  judge_model: gpt-4
```

## Implementation Plan

### Phase 1: Create Scorer Classes (Week 1)
- [ ] Create `lm_eval/api/scorer.py`
- [ ] Implement `Scorer` base class
- [ ] Implement `ProcessResultsScorer`
- [ ] Implement `GenerationScorer`
- [ ] Implement `LoglikelihoodScorer`
- [ ] Implement `ScorerFactory`
- [ ] Add unit tests

### Phase 2: Integrate with Task (Week 2)
- [ ] Add `_scorer` to `Task.__init__`
- [ ] Refactor `Task.process_instances` to use scorer
- [ ] Keep `_process_instances` for backwards compatibility
- [ ] Add integration tests
- [ ] Test with existing task configs

### Phase 3: Migrate Task Subclasses (Week 3)
- [ ] Remove `_process_instances` from `GenerateTask`
- [ ] Remove `_process_instances` from `MultipleChoiceTask`
- [ ] Remove `_compute_sample_metrics` from `GenerateTask`
- [ ] Update all task tests
- [ ] Verify all benchmarks still pass

### Phase 4: Documentation & Examples (Week 4)
- [ ] Update API documentation
- [ ] Add custom scorer tutorial
- [ ] Add migration guide
- [ ] Create example scorers (reward model, LLM judge)
- [ ] Add troubleshooting guide

## Files to Review

1. **SCORER_DESIGN.md** - Full design document with all details
2. **scorer_example.py** - Concrete implementation example
3. **SCORER_ARCHITECTURE.txt** - Visual diagrams and flow charts

## Next Steps

1. **Review the design** - Does this match your vision?
2. **Discuss edge cases** - Any special cases we should handle?
3. **Prioritize features** - Which extensions are most important?
4. **Start implementation** - Begin with Phase 1?

## Questions for Discussion

1. Should we support scorer plugins/registry like we do for filters?
2. Do we need a way to compose scorers (e.g., ensemble scoring)?
3. Should scorers be able to access raw (unfiltered) outputs?
4. How should we handle scorers that need multiple filters' outputs?
5. Should we cache scorer results to avoid recomputation?

## Comparison: Before vs After

### Before (Current)
```python
class GenerateTask(Task):
    def _process_instances(self, instances, filter_name):
        # Lots of code mixing:
        # - Result creation
        # - Metric selection
        # - Metric application
        # - Repeat handling
        # - Score collection
        # All tangled together
```

### After (Proposed)
```python
class GenerateTask(Task):
    # Just construct_requests
    # Scoring handled by GenerationScorer

class Task:
    def process_instances(self, instances):
        # Simple orchestration
        for filter in self._filters:
            for doc_insts in grouped:
                result = self._scorer.score_instances(doc_insts, filter.name)
                # Collect scores
```

**Result**: ~200 lines of complex logic → ~20 lines of clear orchestration

## Summary

This design provides:
- ✅ Clear separation between filtering and scoring
- ✅ Explicit filter-metric relationships
- ✅ Easy extensibility for custom scorers
- ✅ Backwards compatibility with process_results
- ✅ Type-safe interfaces
- ✅ Better testability
- ✅ Cleaner codebase

The key insight: **Scorers are responsible for converting filtered outputs into metric scores**, which is a distinct responsibility from both filtering and aggregation.
