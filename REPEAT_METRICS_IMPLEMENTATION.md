# Repeat Metrics Implementation Summary

## Overview

This implementation makes repeat handling (multiple generations per sample) intuitive and powerful in lm-evaluation-harness. Users can now easily configure repeat aggregation strategies without custom code.

## Key Features

1. **Built-in Repeat Aggregation Functions**
   - `first`, `mean`, `max`, `min`, `majority`, `any_correct`, `all_correct`
   - Easy to extend with custom functions

2. **Simple Configuration**
   - Add `repeat_aggregation` to any metric in YAML
   - No custom filters or functions needed

3. **Runtime Override**
   - Set `num_repeats` in `simple_evaluate()` to override task configs

4. **Individual Repeat Scores**
   - Automatically stored as `{metric_name}_repeats` when `repeats > 1`
   - Available in logged samples for analysis

5. **Backward Compatible**
   - Default behavior unchanged (uses first repeat only)
   - Existing tasks work without modification

## Files Modified

### Core Implementation

1. **lm_eval/api/registry.py**
   - Added `repeat_agg_registry` for repeat aggregation functions
   - Added `register_repeat_aggregation()` and `get_repeat_aggregation()`
   - Updated `freeze_all()` to include new registry

2. **lm_eval/api/metrics.py**
   - Added 7 built-in repeat aggregation functions:
     - `repeat_first`: Take first repeat (default)
     - `repeat_mean`: Average across repeats
     - `repeat_max`: Maximum score
     - `repeat_min`: Minimum score
     - `repeat_majority`: Most common prediction
     - `repeat_any_correct`: 1.0 if any correct (pass@k style)
     - `repeat_all_correct`: 1.0 if all correct

3. **lm_eval/config/metric.py**
   - Added `repeat_aggregation_fn` field to `MetricConfig`
   - Added `repeat_aggregation` cached property
   - Added `compute_repeat_aggregation()` method

4. **lm_eval/api/task.py**
   - Updated `process_results()` for `generate_until` to:
     - Calculate metrics for ALL repeats (not just first)
     - Apply repeat aggregation
     - Store individual repeat scores as `{metric}_repeats`

5. **lm_eval/config/task.py**
   - Updated `_get_metric()` to parse `repeat_aggregation` from YAML
   - Added repeat aggregation to metric config construction

6. **lm_eval/evaluator.py**
   - Added `num_repeats` parameter to `simple_evaluate()`
   - Added runtime override logic for repeats (similar to `num_fewshot`)

### Documentation

1. **REPEAT_METRICS_GUIDE.md**
   - Comprehensive user guide with examples
   - Migration guide from old to new approach
   - Best practices by task type

2. **example_repeat_task.yaml**
   - Working example configuration
   - Demonstrates multiple repeat aggregation strategies

3. **REPEAT_METRICS_IMPLEMENTATION.md** (this file)
   - Technical implementation summary

## Usage Examples

### Basic YAML Configuration

```yaml
task: my_task
repeats: 5
metric_list:
  - metric: exact_match
    aggregation: mean
    repeat_aggregation: majority
    higher_is_better: true
```

### Runtime Override

```python
from lm_eval import simple_evaluate

results = simple_evaluate(
    model="gpt2",
    tasks=["my_task"],
    num_repeats=10,  # Override YAML config
)
```

### Custom Repeat Aggregation

```python
from lm_eval.api.registry import register_repeat_aggregation

@register_repeat_aggregation("custom")
def custom_agg(scores, predictions=None, **kwargs):
    return max(scores) if len(scores) > 3 else scores[0]
```

## Architecture

### Flow Diagram

```
Task Config (repeats=N)
    ↓
Build Instances (duplicated N times)
    ↓
LM Inference (N responses per sample)
    ↓
Apply Filters
    ↓
process_results() - NEW BEHAVIOR:
    ├─ For each metric:
    │   ├─ Calculate score for EACH repeat
    │   ├─ Store repeat_scores = [score_1, ..., score_N]
    │   ├─ aggregated_score = repeat_aggregation_fn(repeat_scores)
    │   └─ Store both aggregated_score and repeat_scores
    ↓
TaskOutput.sample_metrics
    ├─ metric_name: aggregated_score
    └─ metric_name_repeats: [score_1, ..., score_N]
    ↓
Aggregate across samples
    ↓
Final Results
```

## Design Decisions

### 1. Separate Repeat Aggregation from Sample Aggregation

- **Repeat aggregation**: Combines multiple outputs for the SAME sample
- **Sample aggregation**: Combines scores across DIFFERENT samples
- These are orthogonal concepts that should be configured separately

### 2. Default to "first" for Backward Compatibility

- When `repeat_aggregation` is not specified, default to `"first"`
- This ensures existing tasks work without modification
- Explicit configuration required for new behavior

### 3. Store Individual Repeat Scores

- Only stored when `repeats > 1` to avoid overhead
- Named as `{metric_name}_repeats` for clarity
- Available in logged samples for post-hoc analysis

### 4. Registry-Based Architecture

- Consistent with existing metric/aggregation pattern
- Easy to extend with custom functions
- Type-safe and discoverable

## Testing

Basic tests verify:
- ✓ Repeat aggregation registry created
- ✓ All 7 built-in functions registered
- ✓ Functions work correctly with test data
- ✓ MetricConfig integration works
- ✓ `compute_repeat_aggregation()` method works

## Future Enhancements

Potential improvements:
1. Support repeats for `multiple_choice` and `loglikelihood` output types
2. Add more sophisticated aggregations (e.g., weighted voting)
3. Add metrics for repeat consistency/variance
4. Optimize memory usage for large repeat counts
5. Add visualization tools for repeat analysis

## Migration from Old Humaneval Pattern

### Before
```yaml
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

### After
```yaml
task: code_task
repeats: 10
metric_list:
  - metric: exact_match
    aggregation: mean
    repeat_aggregation: any_correct
    higher_is_better: true
```

Note: The old pattern still works for backward compatibility.

## Performance Impact

- **Inference**: Proportional to number of repeats (expected)
- **Memory**: Minimal overhead (stores one extra list per metric per sample)
- **Computation**: Negligible (simple aggregation functions)

## Conclusion

This implementation provides a clean, intuitive, and backward-compatible way to handle repeat metrics in lm-evaluation-harness. It eliminates the need for custom code in most cases while remaining extensible for advanced use cases.
