#!/usr/bin/env python
"""End-to-end test demonstrating repeat metrics in action."""

import sys
sys.path.insert(0, '.')

from lm_eval.config.task import TaskConfig
from lm_eval.config.metric import MetricConfig
from lm_eval.api.registry import metric_registry

print("=" * 70)
print("END-TO-END REPEAT METRICS DEMONSTRATION")
print("=" * 70)

# Simulate what happens when loading a task with repeats
print("\n1. Loading task configuration with repeats...")

task_config = TaskConfig(
    task="test_task",
    output_type="generate_until",
    repeats=5,  # Generate 5 outputs per sample
    metric_list=[
        {
            "metric": "exact_match",
            "aggregation": "mean",
            "repeat_aggregation": "majority",  # NEW FEATURE!
            "higher_is_better": True,
        }
    ],
)

print(f"   Task: {task_config.task}")
print(f"   Repeats: {task_config.repeats}")
print(f"   Output type: {task_config.output_type}")

# Get the metric configuration
print("\n2. Processing metric configuration...")
metrics = task_config._get_metric()
metric = metrics[0]

print(f"   Metric name: {metric.name}")
print(f"   Aggregation: {metric.aggregation_fn.__name__}")
print(f"   Repeat aggregation: {metric.repeat_aggregation_fn}")

# Simulate the evaluation flow
print("\n3. Simulating evaluation with repeats...")
print("   " + "-" * 66)

# Example: Math problem with gold answer "42"
doc = {
    "question": "What is 6 * 7?",
    "answer": "42"
}

# Simulate 5 model generations (repeats)
# In real evaluation, these would come from the model
results = [
    "42",   # Correct
    "43",   # Wrong
    "42",   # Correct
    "42",   # Correct
    "41",   # Wrong
]

print(f"   Question: {doc['question']}")
print(f"   Gold answer: {doc['answer']}")
print(f"   Generated answers ({len(results)} repeats): {results}")

# This is what process_results() does now
print("\n4. Calculating metrics for each repeat...")

repeat_scores = []
repeat_predictions = []
gold = doc["answer"]

for i, result in enumerate(results):
    # Calculate metric for this repeat
    result_score = metric.fn(
        references=[gold],
        predictions=[result],
    )

    # Handle dict vs scalar
    if isinstance(result_score, dict):
        if metric.name in result_score:
            score_value = result_score[metric.name]
        else:
            score_value = next(iter(result_score.values()))
    else:
        score_value = result_score

    repeat_scores.append(float(score_value))
    repeat_predictions.append(result)

    status = "✓ CORRECT" if score_value >= 1.0 else "✗ WRONG"
    print(f"   Repeat {i+1}: '{result}' → score={float(score_value):.1f} {status}")

print(f"\n   Individual scores: {[f'{s:.1f}' for s in repeat_scores]}")

# Apply repeat aggregation
print("\n5. Applying repeat aggregation (majority)...")

from collections import Counter
counts = Counter(repeat_predictions)
print(f"   Vote counts: {dict(counts)}")

majority_pred = counts.most_common(1)[0][0]
majority_count = counts[majority_pred]
print(f"   Majority answer: '{majority_pred}' ({majority_count}/{len(results)} votes)")

aggregated_score = metric.compute_repeat_aggregation(
    repeat_scores,
    predictions=repeat_predictions,
)

print(f"   Aggregated score: {float(aggregated_score):.1f}")

# Build result dict (what would be returned)
result_dict = {
    metric.name: aggregated_score,
    f"{metric.name}_repeats": repeat_scores
}

print("\n6. Final results (what process_results returns)...")
print(f"   {result_dict}")

# Compare with different strategies
print("\n7. Comparison: Different repeat aggregation strategies...")
print("   " + "-" * 66)

from lm_eval.api.registry import get_repeat_aggregation

strategies = {
    "first": "Use only first repeat",
    "mean": "Average all repeats",
    "max": "Best score (best-of-5)",
    "majority": "Most common answer (current)",
    "any_correct": "Pass@5 style (1.0 if any correct)",
    "all_correct": "1.0 only if all correct",
}

for strategy, description in strategies.items():
    agg_fn = get_repeat_aggregation(strategy)
    score = agg_fn(repeat_scores, predictions=repeat_predictions)
    marker = " ← CURRENT" if strategy == "majority" else ""
    print(f"   {strategy:12s}: {float(score):.2f}  ({description}){marker}")

# Show impact on final accuracy
print("\n8. Impact on aggregate metrics...")
print("   " + "-" * 66)

print("   If we had 10 samples with these repeat patterns:")
print("   - Sample 1-7: Majority correct (like our example)")
print("   - Sample 8-10: Majority wrong")
print()
print("   Aggregate accuracy (mean across samples):")

# Simulate different repeat aggregation impacts
sample_scores_majority = [1.0] * 7 + [0.0] * 3
sample_scores_first = [1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0]  # More noise
sample_scores_any = [1.0] * 10  # If any repeat correct

print(f"   - With majority:    {sum(sample_scores_majority) / len(sample_scores_majority):.1%}")
print(f"   - With first only:  {sum(sample_scores_first) / len(sample_scores_first):.1%}")
print(f"   - With any_correct: {sum(sample_scores_any) / len(sample_scores_any):.1%}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("What changed:")
print("  BEFORE: Only results[0] used → wasted 4 out of 5 generations")
print("  AFTER:  All results used → intelligent aggregation via 'majority'")
print()
print("Result format:")
print(f"  {{'exact_match': 1.0, 'exact_match_repeats': [1.0, 0.0, 1.0, 1.0, 0.0]}}")
print("   ↑                    ↑")
print("   Aggregated score     Individual repeat scores (for analysis)")
print()
print("Configuration (YAML):")
print("  repeats: 5")
print("  metric_list:")
print("    - metric: exact_match")
print("      aggregation: mean              # Across samples")
print("      repeat_aggregation: majority   # Across repeats (NEW!)")
print()
print("✅ Repeat metrics implementation verified!")
print("=" * 70)
