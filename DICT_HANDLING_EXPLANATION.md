# Dictionary vs Scalar Handling in Repeat Metrics

This document explains the dict handling code in `process_results()` and why it's needed.

## The Problem

Metric functions can return **two different types**:

### Type 1: Scalar (Single Number)
```python
def simple_metric(references, predictions):
    return 0.95  # Just a float
```

### Type 2: Dictionary (Multiple Values)
```python
def exact_match_hf_evaluate(predictions, references):
    # ... processing ...
    return {
        "exact_match": 0.95  # Returns dict!
    }
```

## The Code

```python
# From lm_eval/api/task.py lines 1571-1581
if isinstance(result_score, dict):
    # For dict results, only store the main metric value
    # (this handles metrics that return multiple values)
    if metric.name in result_score:
        score_value = result_score[metric.name]
    else:
        # Use first value if metric name not in dict
        score_value = next(iter(result_score.values()))
else:
    score_value = result_score
```

## Why This Is Needed

We need to extract a **single scalar** to build the `repeat_scores` list:

```python
# Goal: Build a list of numbers
repeat_scores = [1.0, 0.0, 1.0, 1.0, 0.0]  # ← Must be scalars!

# But metric might return dicts:
for result in results:
    result_score = metric.fn([gold], [result])
    # result_score could be:
    #   - 1.0 (scalar) ✓
    #   - {"exact_match": 1.0} (dict) ✗ Can't append directly!

    # Must extract scalar before appending
    repeat_scores.append(score_value)  # ← Must be a number!
```

## Execution Flow Examples

### Example 1: HuggingFace exact_match (Returns Dict)

```python
# Metric configuration
metric.name = "exact_match"
metric.fn = exact_match_fn  # Wraps exact_match_hf_evaluate

# Call metric
result_score = metric.fn(references=["42"], predictions=["42"])
# Returns: {"exact_match": 1.0}

# Extract scalar
if isinstance({"exact_match": 1.0}, dict):           # True
    if "exact_match" in {"exact_match": 1.0}:        # True ✓
        score_value = {"exact_match": 1.0}["exact_match"]
        # score_value = 1.0 ✓

repeat_scores.append(1.0)  # Success!
```

### Example 2: Simple Metric (Returns Scalar)

```python
# Custom metric
def my_metric(references, predictions):
    return 0.75  # Just a number

# Call metric
result_score = my_metric(["42"], ["42"])
# Returns: 0.75

# Extract scalar
if isinstance(0.75, dict):  # False
    # Skip dict handling
else:
    score_value = 0.75  # Use directly

repeat_scores.append(0.75)  # Success!
```

### Example 3: Multi-Value Dict (Unexpected Structure)

```python
# Weird metric returning unexpected dict
def weird_metric(references, predictions):
    return {
        "score_1": 0.8,
        "score_2": 0.6
    }

metric.name = "weird_metric"

# Call metric
result_score = weird_metric(["42"], ["42"])
# Returns: {"score_1": 0.8, "score_2": 0.6}

# Extract scalar
if isinstance(result_score, dict):                     # True
    if "weird_metric" in result_score:                 # False!
        # Not taken
    else:
        # Fallback: use first value
        score_value = next(iter(result_score.values()))
        # score_value = 0.8 (first value)

repeat_scores.append(0.8)  # Fallback works!
```

## Complete Flow in process_results()

```python
# For EACH repeat:
for result in ["42", "43", "42", "42", "41"]:

    # 1. Call metric function
    result_score = metric.fn(
        references=[gold],
        predictions=[result]
    )
    # result_score might be:
    #   - Scalar: 1.0
    #   - Dict:   {"exact_match": 1.0}

    # 2. Extract scalar value
    if isinstance(result_score, dict):
        if metric.name in result_score:
            score_value = result_score[metric.name]  # Best case
        else:
            score_value = next(iter(result_score.values()))  # Fallback
    else:
        score_value = result_score  # Already scalar

    # 3. Append to list
    repeat_scores.append(score_value)  # Always a number!
    repeat_predictions.append(result)

# Now: repeat_scores = [1.0, 0.0, 1.0, 1.0, 0.0]

# 4. Apply aggregation (needs list of numbers!)
aggregated_score = metric.compute_repeat_aggregation(
    repeat_scores,  # ← Must be list of scalars
    predictions=repeat_predictions,
)
```

## Why Not Keep The Dict?

**Why can't we do this?**
```python
# ❌ This doesn't work:
repeat_scores = [
    {"exact_match": 1.0},
    {"exact_match": 0.0},
    {"exact_match": 1.0},
]

# ❌ Can't aggregate dicts:
mean(repeat_scores)  # Error! Can't average dicts
max(repeat_scores)   # Error! Can't compare dicts
```

**We need scalars:**
```python
# ✓ This works:
repeat_scores = [1.0, 0.0, 1.0]

# ✓ Can aggregate scalars:
mean(repeat_scores)  # 0.67
max(repeat_scores)   # 1.0
```

## Comparison: Old vs New

### Old Code (Before Repeats)
```python
# Old: line 1557-1569 (before our changes)
result = results[0]  # Only first!
result_score = metric.fn(references=[gold], predictions=[result])

if isinstance(result_score, dict):
    # Store ALL values from dict
    for k, v in result_score.items():
        result_dict[k] = v
else:
    result_dict[metric.name] = result_score
```

**Old behavior**: Store all dict keys directly in `result_dict`.

### New Code (With Repeats)
```python
# New: lines 1561-1602 (our changes)
for result in results:  # ALL results!
    result_score = metric.fn(references=[gold], predictions=[result])

    # Extract scalar for repeat_scores list
    if isinstance(result_score, dict):
        if metric.name in result_score:
            score_value = result_score[metric.name]
        else:
            score_value = next(iter(result_score.values()))
    else:
        score_value = result_score

    repeat_scores.append(score_value)  # Must be scalar!

# Aggregate and store
aggregated_score = metric.compute_repeat_aggregation(repeat_scores)
result_dict[metric.name] = aggregated_score
result_dict[f"{metric.name}_repeats"] = repeat_scores
```

**New behavior**: Extract scalar per repeat, aggregate, store result.

## Why The Fallback?

The fallback (`next(iter(result_score.values()))`) handles edge cases:

1. **Custom metrics with unexpected structure**
   ```python
   return {"foo": 0.8, "bar": 0.6}
   # Fallback: use 0.8 (first value)
   ```

2. **Defensive programming**
   - Ensures we always get *some* value
   - Prevents crashes on unexpected metric returns
   - Better than crashing: use first value and continue

3. **Graceful degradation**
   ```python
   # Even if metric returns weird structure:
   result_score = {"random_key": 0.9}

   # We still extract a value:
   score_value = 0.9  # First value

   # Evaluation continues instead of crashing
   ```

## Summary

The dict handling code is essential because:

1. ✓ Metric functions have inconsistent return types (scalar vs dict)
2. ✓ HuggingFace metrics commonly return dicts
3. ✓ We need scalars to build `repeat_scores` list
4. ✓ Aggregation functions require scalar inputs
5. ✓ Defensive coding prevents crashes on unexpected formats

**Without this code, the system would crash when trying to aggregate dicts!**
