# Evaluation Loop Refactor Plan

## Current State Analysis

### Problems with Current Implementation

The evaluation loop (lines 600-700 in evaluator.py) has several issues:

1. **Verbose and Hard to Follow**: Manual iteration over filters, docs, and instances
2. **TaskOutput Abstraction**: Unnecessary wrapper that duplicates Task functionality
3. **Manual Metric Collection**: Manually collects metrics into `task_output.sample_metrics`
4. **Redundant Logic**: Logic that's now handled by `Task.process_instances()`
5. **Mixed Concerns**: Combines result processing, logging, and multi-GPU gathering

### Current Flow (Verbose)

```python
# Lines 600-700
for task_output, limit in zip(eval_tasks, limits):
    task = task_output.task
    task.apply_filters()

    # Manual grouping by doc_id
    instances_by_doc_id = defaultdict(list)
    for instance in task.instances:
        instances_by_doc_id[instance.doc_id].append(instance)

    # Manual iteration over filters
    for filter_key in task.instances[0].filtered_resps.keys():
        doc_iterator = task.doc_iterator(...)

        # Manual iteration over docs
        for doc_id, doc in doc_iterator:
            requests = instances_by_doc_id[doc_id]

            # Manual metric computation
            metrics = task.process_results(
                doc, [req.filtered_resps[filter_key] for req in requests]
            )

            # Manual logging
            if log_samples:
                # ... build example dict ...
                task_output.logged_samples.append(example)

            # Manual metric collection
            for metric, value in metrics.items():
                task_output.sample_metrics[(metric, filter_key)].append(value)

# Then aggregate (lines 696-700)
for task_output in eval_tasks:
    task_output.calculate_aggregate_metric(bootstrap_iters=bootstrap_iters)
```

### What TaskOutput Does

TaskOutput is a wrapper that:
1. Holds a reference to the Task
2. Stores configuration metadata (name, version, n_shot, alias, etc.)
3. Collects `sample_metrics` - which Task already does in `process_instances()`
4. Computes `agg_metrics` - which Task already does in `compute_aggregations()`
5. Stores `logged_samples` - can be moved to Task or handled separately

**Key insight**: TaskOutput duplicates functionality that Task already has!

---

## New Design: Use Task Methods Directly

### Benefits of New Approach

✅ **Simpler**: Task handles its own processing
✅ **Clearer**: One call to `process_instances()`, one call to `compute_aggregations()`
✅ **Less Code**: ~100 lines → ~30 lines
✅ **Consistent**: Uses the new Task abstractions we just created
✅ **Testable**: Can test Task independently

### New Flow (Clean)

```python
# Lines 600-650 (simplified)
for task, limit in zip(tasks, limits):
    # Apply filters to all instances
    task.apply_filters()

    # Process all instances using unified Task method
    sample_scores = task.process_instances()

    # Handle logging if needed
    if log_samples:
        logged_samples = _collect_logged_samples(task, limit, RANK, WORLD_SIZE)

    # Multi-GPU gathering
    if WORLD_SIZE > 1:
        sample_scores = _gather_scores_multigpu(sample_scores, RANK, WORLD_SIZE)
        if log_samples:
            logged_samples = _gather_samples_multigpu(logged_samples, RANK, WORLD_SIZE)

    # Compute aggregations
    if RANK == 0:
        agg_metrics = task.compute_aggregations(sample_scores, bootstrap_iters)

        # Store results
        results[task.task_name] = agg_metrics
        versions[task.task_name] = task.VERSION
        configs[task.task_name] = task.dump_config()
        # ... etc
```

---

## Detailed Changes

### 1. Replace TaskOutput with Direct Task Usage

**Before**:
```python
eval_tasks = [TaskOutput.from_taskdict(name, task) for ...]
for task_output in eval_tasks:
    task = task_output.task
    # ... use task_output.sample_metrics, task_output.agg_metrics ...
```

**After**:
```python
tasks = [task for task in task_dict.values() if not isinstance(task, dict)]
for task in tasks:
    # ... use task.process_instances(), task.compute_aggregations() ...
```

### 2. Simplify Metric Collection

**Before** (40+ lines):
```python
# Manual grouping
instances_by_doc_id = defaultdict(list)
for instance in task.instances:
    instances_by_doc_id[instance.doc_id].append(instance)

# Manual filter iteration
for filter_key in task.instances[0].filtered_resps.keys():
    # Manual doc iteration
    for doc_id, doc in doc_iterator:
        requests = instances_by_doc_id[doc_id]
        metrics = task.process_results(doc, [req.filtered_resps[filter_key] for req in requests])
        # Manual collection
        for metric, value in metrics.items():
            task_output.sample_metrics[(metric, filter_key)].append(value)
```

**After** (1 line):
```python
sample_scores = task.process_instances()  # Task handles everything!
```

### 3. Simplify Aggregation

**Before**:
```python
for task_output in eval_tasks:
    task_output.calculate_aggregate_metric(bootstrap_iters=bootstrap_iters)
```

**After**:
```python
agg_metrics = task.compute_aggregations(sample_scores, bootstrap_iters)
```

### 4. Handle Logging Separately

Logging is a cross-cutting concern. Extract it to a helper function:

```python
def _collect_logged_samples(
    task: Task,
    limit: int,
    rank: int,
    world_size: int,
    samples_filter: dict = None
) -> list[dict]:
    """Collect logged samples for a task."""
    logged_samples = []

    indices = samples_filter.get(task.task_name, None) if samples_filter else None
    doc_iterator = task.doc_iterator(
        rank=rank,
        limit=limit,
        world_size=world_size,
        samples=indices
    )

    instances_by_doc_id = defaultdict(list)
    for instance in task.instances:
        instances_by_doc_id[instance.doc_id].append(instance)

    for instances in instances_by_doc_id.values():
        instances.sort(key=lambda x: x.idx)

    for doc_id, doc in doc_iterator:
        doc_id_true = indices[doc_id] if indices else doc_id
        requests = instances_by_doc_id[doc_id]

        # Create log entry for each filter
        for filter_key in requests[0].filtered_resps.keys():
            target = task.doc_to_target(doc)
            example = {
                "doc_id": doc_id_true,
                "doc": doc,
                "target": target,
                "arguments": [req.args for req in requests],
                "resps": [req.resps for req in requests],
                "filtered_resps": [req.filtered_resps[filter_key] for req in requests],
                "filter": filter_key,
                "doc_hash": hash_string(json.dumps(requests[0].doc, indent=2, default=handle_non_serializable, ensure_ascii=False)),
                "prompt_hash": hash_string(requests[0].arguments[0]),
                "target_hash": hash_string(str(target)),
            }
            logged_samples.append(example)

    return logged_samples
```

### 5. Handle Multi-GPU Gathering

Extract multi-GPU logic to helper functions:

```python
def _gather_scores_multigpu(
    sample_scores: dict,
    rank: int,
    world_size: int
) -> dict:
    """Gather sample scores across all ranks."""
    if world_size == 1:
        return sample_scores

    gathered_scores = {}
    for metric_key, values in sample_scores.items():
        value_list = [None] * world_size if rank == 0 else None
        torch.distributed.gather_object(
            obj=values,
            object_gather_list=value_list,
            dst=0
        )
        if rank == 0:
            gathered_scores[metric_key] = list(itertools.chain.from_iterable(value_list))

    return gathered_scores if rank == 0 else {}

def _gather_samples_multigpu(
    logged_samples: list,
    rank: int,
    world_size: int
) -> list:
    """Gather logged samples across all ranks."""
    if world_size == 1:
        return logged_samples

    full_samples = [None] * world_size if rank == 0 else None
    torch.distributed.gather_object(
        obj=logged_samples,
        object_gather_list=full_samples,
        dst=0
    )

    return list(itertools.chain.from_iterable(full_samples)) if rank == 0 else []
```

### 6. Build Results Dictionary Directly

**Before**:
```python
(results, samples, configs, versions, num_fewshot, higher_is_better) = consolidate_results(eval_tasks)
```

**After**:
```python
results = {}
samples = {}
configs = {}
versions = {}
num_fewshot = {}
higher_is_better = {}

for task in tasks:
    task_name = task.task_name
    results[task_name] = {
        **agg_metrics,
        "alias": task.config.get("alias", task_name),
    }
    if log_samples:
        samples[task_name] = logged_samples
    configs[task_name] = task.dump_config()
    versions[task_name] = task.VERSION
    num_fewshot[task_name] = task.config.get("num_fewshot", 0)
    higher_is_better[task_name] = task.higher_is_better()
```

---

## Complete Refactored Flow

```python
### Postprocess outputs ###
RANK = lm.rank
WORLD_SIZE = lm.world_size

# Get flat list of tasks from task_dict
tasks = get_task_list(task_dict)

# Process each task
task_results = {}
for task, limit in zip(tasks, limits):
    # Apply filters to instances
    task.apply_filters()

    # Process instances using unified Task method
    sample_scores = task.process_instances()

    # Collect logged samples if needed
    logged_samples = []
    if log_samples:
        logged_samples = _collect_logged_samples(
            task, limit, RANK, WORLD_SIZE, samples
        )

    # Store for gathering
    task_results[task.task_name] = {
        "task": task,
        "sample_scores": sample_scores,
        "logged_samples": logged_samples,
        "limit": limit,
    }

# Multi-GPU gathering
if WORLD_SIZE > 1:
    lm.accelerator.wait_for_everyone()

    for task_name, task_data in task_results.items():
        # Gather scores
        task_data["sample_scores"] = _gather_scores_multigpu(
            task_data["sample_scores"], RANK, WORLD_SIZE
        )

        # Gather samples
        if log_samples:
            task_data["logged_samples"] = _gather_samples_multigpu(
                task_data["logged_samples"], RANK, WORLD_SIZE
            )

# Rank 0: Aggregate and build results
if RANK == 0:
    results = {}
    samples = {}
    configs = {}
    versions = {}
    num_fewshot = {}
    higher_is_better = {}

    for task_name, task_data in task_results.items():
        task = task_data["task"]

        # Compute aggregations
        agg_metrics = task.compute_aggregations(
            task_data["sample_scores"],
            bootstrap_iters=bootstrap_iters
        )

        # Build results
        results[task_name] = {
            **agg_metrics,
            "alias": task.config.get("alias", task_name),
        }

        if log_samples:
            samples[task_name] = task_data["logged_samples"]

        configs[task_name] = task.dump_config()
        versions[task_name] = task.VERSION
        num_fewshot[task_name] = task.config.get("num_fewshot", 0)
        higher_is_better[task_name] = task.higher_is_better()

    ### Calculate group metrics ###
    if bool(results):
        groups = build_group_hierarchy(task_dict)
        if groups:
            group_results, group_versions = compute_group_aggregations(
                results, groups, bootstrap_iters
            )
            results.update(group_results)
            versions.update(group_versions)
            show_group_table = True
        else:
            show_group_table = False

    # Rest of results_dict building...
```

---

## Line Count Comparison

| Section | Before | After | Reduction |
|---------|--------|-------|-----------|
| Metric collection loop | ~65 lines | ~5 lines | **92%** |
| Multi-GPU gathering | ~30 lines | ~10 lines | **67%** |
| Aggregation | ~10 lines | ~5 lines | **50%** |
| Results consolidation | ~50 lines | ~20 lines | **60%** |
| **Total** | **~155 lines** | **~40 lines** | **74%** |

---

## Benefits Summary

✅ **74% reduction in code** (155 lines → 40 lines)
✅ **Clearer flow**: Apply filters → Process → Gather → Aggregate
✅ **Uses new Task methods**: `process_instances()`, `compute_aggregations()`
✅ **No TaskOutput wrapper**: Direct Task usage
✅ **Separated concerns**: Logging extracted to helper function
✅ **Easier to test**: Each step can be tested independently
✅ **Consistent**: Matches the design philosophy we've been following

---

## Migration Strategy

1. **Keep consolidate_results()** for backward compatibility
2. **Add helper functions** (`_collect_logged_samples`, `_gather_scores_multigpu`, etc.)
3. **Replace main loop** with simplified version
4. **Test thoroughly** with multi-GPU setup
5. **Update documentation**

---

## Implementation Steps

1. ✅ Create this plan
2. Add helper functions to evaluator_utils.py
3. Refactor main evaluation loop in evaluator.py
4. Update get_task_list() to return flat list of Tasks
5. Test with various task types
6. Test with multi-GPU setup
7. Update documentation

This completes the refactoring trilogy:
- **Scorer refactor**: Unified `process_instances()`
- **Group refactor**: First-class `Group` objects
- **Evaluator refactor**: Clean evaluation loop using new abstractions
