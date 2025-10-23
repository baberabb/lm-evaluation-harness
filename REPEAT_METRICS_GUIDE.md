# Repeat Metrics Guide

This guide explains how to use the new repeat metrics functionality in lm-evaluation-harness.

## Overview

The repeat metrics feature makes it easy to:
1. Generate multiple outputs per sample (repeats)
2. Calculate metrics for each repeat
3. Aggregate repeat scores using various strategies (majority voting, pass@k, best-of-k, etc.)
4. Access individual repeat scores for analysis

## Quick Start

### Basic Example: Majority Voting

```yaml
task: my_task
repeats: 5  # Generate 5 outputs per sample
metric_list:
  - metric: exact_match
    aggregation: mean
    repeat_aggregation: majority  # Take most common answer
    higher_is_better: true
```

### Example: Best-of-K

```yaml
task: my_task
repeats: 10
metric_list:
  - metric: bleu
    aggregation: mean
    repeat_aggregation: max  # Take best BLEU score across 10 attempts
    higher_is_better: true
```

### Example: Pass@K Style Evaluation

```yaml
task: code_task
repeats: 10
metric_list:
  - metric: exact_match
    aggregation: mean
    repeat_aggregation: any_correct  # 1.0 if any repeat is correct
    higher_is_better: true
```

## Repeat Aggregation Functions

All built-in repeat aggregation functions:

| Function | Description | Use Case |
|----------|-------------|----------|
| `first` | Use first repeat only (default) | Backward compatibility |
| `mean` | Average scores across repeats | General averaging |
| `max` | Maximum score across repeats | Best-of-K evaluation |
| `min` | Minimum score across repeats | Worst-case analysis |
| `majority` | Most common prediction | Majority voting for stability |
| `any_correct` | 1.0 if any repeat is correct | Pass@K style evaluation |
| `all_correct` | 1.0 if all repeats are correct | Strict consistency check |

## Runtime Configuration

Override repeats at runtime:

```python
from lm_eval import simple_evaluate

results = simple_evaluate(
    model="gpt2",
    tasks=["my_task"],
    num_repeats=5,  # Override task config
)
```

## Advanced Examples

### Multiple Metrics with Different Repeat Aggregations

```yaml
task: complex_task
repeats: 10
metric_list:
  - metric: exact_match
    aggregation: mean
    repeat_aggregation: majority
    higher_is_better: true

  - metric: bleu
    aggregation: mean
    repeat_aggregation: max
    higher_is_better: true

  - metric: exact_match
    aggregation: mean
    repeat_aggregation: any_correct
    higher_is_better: true
```

This will compute:
- `exact_match`: majority vote across 10 repeats
- `bleu`: best BLEU score across 10 repeats
- `exact_match_1`: 1.0 if any repeat is correct

### Accessing Individual Repeat Scores

Individual repeat scores are automatically stored when `repeats > 1`:

```python
results = simple_evaluate(
    model="gpt2",
    tasks=["my_task"],
    num_repeats=5,
    log_samples=True,
)

# Access logged samples
for sample in results["samples"]["my_task"]:
    # Aggregated score
    print("Final score:", sample["exact_match"])

    # Individual repeat scores
    print("Repeat scores:", sample["exact_match_repeats"])
    # Example output: [1.0, 0.0, 1.0, 1.0, 0.0]
```

## Migration Guide

### Before (Custom Implementation Required)

```yaml
# Old way: Custom filter + custom metric function
task: humaneval
repeats: 10
filter_list:
  - name: "create_test"
    filter:
      - function: "custom"
        filter_fn: !function utils.build_predictions
metric_list:
  - metric: !function utils.pass_at_k
    aggregation: mean
    k: [1, 10]
```

### After (Built-in Support)

```yaml
# New way: Simple configuration
task: my_code_task
repeats: 10
metric_list:
  - metric: exact_match
    aggregation: mean
    repeat_aggregation: any_correct  # Pass@K style
    higher_is_better: true
```

## Custom Repeat Aggregation Functions

You can also define custom repeat aggregation functions:

```python
from lm_eval.api.registry import register_repeat_aggregation

@register_repeat_aggregation("custom_weighted")
def custom_weighted_agg(scores, predictions=None, **kwargs):
    """Weight later repeats more heavily."""
    weights = [i + 1 for i in range(len(scores))]
    return sum(s * w for s, w in zip(scores, weights)) / sum(weights)
```

Then use it in your config:

```yaml
metric_list:
  - metric: exact_match
    aggregation: mean
    repeat_aggregation: custom_weighted
```

## Backward Compatibility

All existing tasks work without changes:
- Default `repeat_aggregation` is `"first"` (uses only first repeat)
- Tasks with `repeats: 1` (default) behave exactly as before
- Existing custom repeat handling (like humaneval) continues to work

## Performance Considerations

1. **Increased inference time**: `repeats=N` will run N times more inference
2. **Memory usage**: Individual repeat scores are stored when `repeats > 1`
3. **Recommended**: Start with small values (3-5 repeats) and increase if needed

## Best Practices

1. **Use majority voting** for improving accuracy on reasoning tasks
2. **Use any_correct** for code generation and math problems
3. **Use max** for generation quality metrics (BLEU, ROUGE)
4. **Use mean** for general averaging and baseline comparisons
5. **Store individual scores** (via `log_samples=True`) for analysis

## Examples by Task Type

### Question Answering
```yaml
repeats: 5
metric_list:
  - metric: exact_match
    repeat_aggregation: majority
```

### Code Generation
```yaml
repeats: 10
metric_list:
  - metric: exact_match
    repeat_aggregation: any_correct  # Pass@10
```

### Text Generation Quality
```yaml
repeats: 5
metric_list:
  - metric: bleu
    repeat_aggregation: max  # Best BLEU
  - metric: bleu
    repeat_aggregation: mean  # Average BLEU
```

### Math Problem Solving
```yaml
repeats: 10
metric_list:
  - metric: exact_match
    repeat_aggregation: majority  # Most common answer
  - metric: exact_match
    repeat_aggregation: any_correct  # Pass@10
```
