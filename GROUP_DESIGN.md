# Group Refactor Design: Elegant Group Management

## Current State Analysis

### What Exists Now

**GroupConfig** (`lm_eval/api/group.py`):
- Data class for group configuration
- Contains: `group`, `group_alias`, `task` (list), `aggregate_metric_list`
- Just configuration, no behavior

**ConfigurableGroup** (`lm_eval/api/group.py`):
- Wrapper around GroupConfig
- Minimal: just exposes config properties
- No task management or metric computation

**Current Group Handling**:
- Groups are represented as nested dictionaries in task_dict
- Aggregation happens in `consolidate_group_results()` (evaluator_utils.py:387-530)
- Complex recursive function that:
  - Traverses task hierarchy
  - Collects metrics from subtasks
  - Computes aggregated metrics (mean, weighted mean, etc.)
  - Updates results dictionary in-place

### Current Problems

1. **No Group Class Parallel to Task**
   - We have `Task` class with clear responsibilities
   - Groups are just dicts with config - no object model
   - Inconsistent: tasks are objects, groups are dicts

2. **Scattered Logic**
   - Group aggregation in `consolidate_group_results()` (140+ lines)
   - Group printing in `prepare_print_tasks()`
   - Group hierarchy in `get_subtask_list()`
   - No single source of truth

3. **Complex Aggregation**
   - `consolidate_group_results()` is recursive and hard to follow
   - Mixes concerns: traversal + aggregation + result storage
   - Hard to extend or modify

4. **Unclear Relationships**
   - How do you get tasks from a group?
   - How do you know which groups a task belongs to?
   - No clear parent/child relationships

5. **No Group-Wide Operations**
   - Can't easily ask: "what's the average acc across all MMLU subtasks?"
   - Can't iterate over group's tasks
   - Can't get group-level statistics

6. **Difficult to Track**
   - Groups are implicit in nested dict structure
   - Hard to debug: "which tasks are in this group?"
   - No way to inspect group state

---

## Proposed Design: Group Class

### Core Principle

**"Groups should be first-class objects, just like Tasks"**

Just as `Task` represents an evaluation task with:
- Configuration
- Data (instances)
- Behavior (scoring, aggregation)

`Group` should represent a collection of tasks with:
- Configuration
- Members (tasks/subgroups)
- Behavior (aggregation, iteration)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                        Group                             │
│  + name: str                                             │
│  + tasks: dict[str, Task | Group]   # Can nest!        │
│  + config: GroupConfig                                   │
│  + compute_aggregate_metrics() -> dict                   │
│  + get_all_tasks() -> list[Task]                        │
│  + get_subtasks(recursive=True) -> list[Task]           │
│  + iter_tasks() -> Iterator[Task]                       │
└─────────────────────────────────────────────────────────┘
```

### Key Design

Decisions

#### 1. Group is a Container

```python
class Group:
    def __init__(self, name: str, config: GroupConfig):
        self.name = name
        self.config = config
        self.tasks: dict[str, Task | Group] = {}  # Can contain tasks or subgroups
        self._cached_aggregations: dict = {}

    def add_task(self, task: Task | Group):
        """Add a task or subgroup to this group."""
        if isinstance(task, Task):
            self.tasks[task.task_name] = task
        else:
            self.tasks[task.name] = task

    def get_all_tasks(self, recursive=True) -> list[Task]:
        """Get all tasks, optionally recursively through subgroups."""
        tasks = []
        for item in self.tasks.values():
            if isinstance(item, Task):
                tasks.append(item)
            elif isinstance(item, Group) and recursive:
                tasks.extend(item.get_all_tasks(recursive=True))
        return tasks
```

**Benefits**:
- Clear ownership: group contains tasks
- Easy iteration: `for task in group.iter_tasks()`
- Natural hierarchy: groups can contain groups

#### 2. Group Computes Own Aggregations

```python
def compute_aggregate_metrics(
    self,
    task_results: dict[str, dict],  # task_name -> metrics
    bootstrap_iters: int = 100000
) -> dict:
    """Compute aggregated metrics for this group.

    Args:
        task_results: Results from individual tasks

    Returns:
        dict mapping metric_name -> aggregated_value
    """
    if not self.config.aggregate_metric_list:
        return {}

    agg_metrics = {}
    all_tasks = self.get_all_tasks()

    for agg_config in self.config.aggregate_metric_list:
        metric_name = agg_config.metric
        filter_names = agg_config.filter_list

        for filter_name in filter_names:
            metric_key = f"{metric_name},{filter_name}"

            # Gather values from subtasks
            values, sizes, stderrs = self._gather_subtask_metrics(
                task_results,
                all_tasks,
                metric_key
            )

            # Aggregate
            if agg_config.aggregation == "mean":
                agg_value = aggregate_subtask_metrics(
                    values,
                    sizes,
                    agg_config.weight_by_size
                )
            elif callable(agg_config.aggregation):
                agg_value = agg_config.aggregation(values, sizes)

            agg_metrics[metric_key] = agg_value

            # Compute stderr
            if "N/A" not in stderrs:
                agg_metrics[f"{metric_name}_stderr,{filter_name}"] = (
                    pooled_sample_stderr(stderrs, sizes)
                )

    return agg_metrics
```

**Benefits**:
- Self-contained: group knows how to aggregate its own metrics
- Testable: can test group aggregation in isolation
- Clear: one method does one thing

#### 3. Parallel to Task Pattern

```
Task:
- construct_requests() → creates instances
- process_instances() → scores instances
- compute_aggregations() → aggregates sample scores

Group:
- add_task() → builds group membership
- compute_aggregate_metrics() → aggregates task metrics
- get_all_tasks() → retrieves members
```

**Both have**:
- Configuration (TaskConfig / GroupConfig)
- Data (instances / tasks)
- Computation (scoring / aggregation)

---

## Implementation Plan

### Phase 1: Create Group Class

```python
# lm_eval/api/group.py

from typing import Iterator

class Group:
    """Represents a group of tasks with aggregated metrics.

    A Group is a collection of Tasks (and potentially sub-Groups) that
    can compute aggregated metrics across its members.

    Example:
        >>> group = Group("mmlu", config)
        >>> group.add_task(mmlu_anatomy_task)
        >>> group.add_task(mmlu_biology_task)
        >>> agg_metrics = group.compute_aggregate_metrics(task_results)
    """

    def __init__(self, name: str, config: GroupConfig):
        self.name = name
        self.config = config
        self.tasks: dict[str, Task | Group] = {}
        self.alias = config.group_alias or name
        self.version = config.metadata.get("version") if config.metadata else None

    def add_task(self, task: Task | "Group"):
        """Add a task or subgroup to this group."""
        key = task.task_name if isinstance(task, Task) else task.name
        self.tasks[key] = task

    def remove_task(self, task_name: str):
        """Remove a task from this group."""
        self.tasks.pop(task_name, None)

    def get_task(self, task_name: str) -> Task | "Group" | None:
        """Get a specific task by name."""
        return self.tasks.get(task_name)

    def get_all_tasks(self, recursive=True) -> list[Task]:
        """Get all Task instances, optionally recursively."""
        tasks = []
        for item in self.tasks.values():
            if isinstance(item, Task):
                tasks.append(item)
            elif isinstance(item, Group) and recursive:
                tasks.extend(item.get_all_tasks(recursive=True))
        return tasks

    def iter_tasks(self, recursive=True) -> Iterator[Task]:
        """Iterate over all tasks in this group."""
        for item in self.tasks.values():
            if isinstance(item, Task):
                yield item
            elif isinstance(item, Group) and recursive:
                yield from item.iter_tasks(recursive=True)

    def compute_aggregate_metrics(
        self,
        task_results: dict[str, dict],
        bootstrap_iters: int = 100000
    ) -> dict:
        """Compute aggregated metrics for this group.

        Args:
            task_results: Dictionary mapping task_name -> task_metrics
            bootstrap_iters: Number of bootstrap iterations for stderr

        Returns:
            Dictionary of aggregated metrics
        """
        if not self.config.aggregate_metric_list:
            return {}

        from lm_eval.api.metrics import aggregate_subtask_metrics, pooled_sample_stderr

        agg_metrics = {}
        all_tasks = self.get_all_tasks()
        task_names = [t.task_name for t in all_tasks]

        for agg_config in self.config.aggregate_metric_list:
            for filter_name in agg_config.filter_list:
                metric_key = f"{agg_config.metric},{filter_name}"
                stderr_key = f"{agg_config.metric}_stderr,{filter_name}"

                # Gather metrics from subtasks
                values = []
                sizes = []
                stderrs = []

                for task_name in task_names:
                    if task_name not in task_results:
                        continue
                    task_result = task_results[task_name]

                    if metric_key in task_result:
                        values.append(task_result[metric_key])
                        sizes.append(task_result.get("samples", 1))
                        stderrs.append(task_result.get(stderr_key, "N/A"))

                if not values:
                    continue

                # Aggregate based on config
                if agg_config.aggregation == "mean":
                    agg_value = aggregate_subtask_metrics(
                        values,
                        sizes,
                        agg_config.weight_by_size
                    )
                elif callable(agg_config.aggregation):
                    agg_value = agg_config.aggregation(values, sizes)
                else:
                    raise ValueError(
                        f"Unknown aggregation: {agg_config.aggregation}"
                    )

                agg_metrics[metric_key] = agg_value
                agg_metrics["samples"] = sum(sizes)

                # Aggregate stderr
                if "N/A" not in stderrs:
                    agg_metrics[stderr_key] = pooled_sample_stderr(stderrs, sizes)
                else:
                    agg_metrics[stderr_key] = "N/A"

        return agg_metrics

    def __repr__(self):
        return f"Group(name={self.name}, tasks={len(self.tasks)})"

    def __len__(self):
        return len(self.tasks)

    def __contains__(self, task_name: str):
        return task_name in self.tasks
```

### Phase 2: Update evaluator_utils.py

**Before**: Complex recursive function
```python
def consolidate_group_results(...):
    # 140 lines of complex recursion
    ...
```

**After**: Simple iteration
```python
def consolidate_group_results(
    results: dict,
    groups: dict[str, Group],  # Now we have Group objects!
    bootstrap_iters: int = 100000
) -> dict:
    """Compute aggregated metrics for all groups.

    Much simpler now that Group handles its own aggregation.
    """
    for group_name, group in groups.items():
        # Group computes its own aggregations
        agg_metrics = group.compute_aggregate_metrics(
            results,
            bootstrap_iters=bootstrap_iters
        )

        # Update results
        if agg_metrics:
            results[group_name] = {
                **results.get(group_name, {}),
                **agg_metrics,
                "alias": group.alias,
            }

    return results
```

**Benefits**:
- 10 lines instead of 140
- No recursion needed (Group handles its own hierarchy)
- Easy to understand

### Phase 3: Build Groups During Task Loading

```python
# In task loading/factory code

def build_task_hierarchy(task_configs: dict) -> dict[str, Group]:
    """Build Group objects from task configurations.

    Returns:
        Dictionary mapping group_name -> Group instance
    """
    groups = {}
    tasks = {}

    # First pass: create all groups and tasks
    for config in task_configs:
        if "group" in config:
            group_config = GroupConfig(**config)
            groups[config["group"]] = Group(config["group"], group_config)
        else:
            task = Task.from_config(config)
            tasks[task.task_name] = task

    # Second pass: assign tasks to groups
    for task in tasks.values():
        if hasattr(task.config, "group"):
            group_names = task.config.group
            if not isinstance(group_names, list):
                group_names = [group_names]

            for group_name in group_names:
                if group_name in groups:
                    groups[group_name].add_task(task)

    # Third pass: handle nested groups
    for group_config in task_configs:
        if "group" in group_config and "task" in group_config:
            parent_group = groups[group_config["group"]]
            for subtask_name in group_config["task"]:
                if subtask_name in groups:  # It's a subgroup
                    parent_group.add_task(groups[subtask_name])
                elif subtask_name in tasks:  # It's a task
                    parent_group.add_task(tasks[subtask_name])

    return groups
```

---

## Usage Examples

### Example 1: Creating a Group

```python
# Create MMLU group
mmlu_config = GroupConfig(
    group="mmlu",
    group_alias="MMLU",
    aggregate_metric_list=[
        AggMetricConfig(
            metric="acc",
            aggregation="mean",
            weight_by_size=True,
            filter_list=["none"]
        )
    ]
)

mmlu_group = Group("mmlu", mmlu_config)

# Add tasks
mmlu_group.add_task(mmlu_anatomy_task)
mmlu_group.add_task(mmlu_biology_task)
mmlu_group.add_task(mmlu_chemistry_task)

print(f"MMLU has {len(mmlu_group)} subtasks")
# Output: MMLU has 3 subtasks
```

### Example 2: Iterating Over Tasks

```python
# Get all tasks in group
for task in mmlu_group.iter_tasks():
    print(f"Task: {task.task_name}")

# Get task list
all_tasks = mmlu_group.get_all_tasks()
task_names = [t.task_name for t in all_tasks]
```

### Example 3: Computing Group Metrics

```python
# After evaluating all tasks, we have results:
task_results = {
    "mmlu_anatomy": {"acc,none": 0.85, "samples": 100},
    "mmlu_biology": {"acc,none": 0.92, "samples": 150},
    "mmlu_chemistry": {"acc,none": 0.88, "samples": 120},
}

# Compute aggregated metrics
agg_metrics = mmlu_group.compute_aggregate_metrics(task_results)

print(agg_metrics)
# Output: {
#     "acc,none": 0.887,  # Weighted average
#     "samples": 370,
# }
```

### Example 4: Nested Groups

```python
# Create subgroups
stem_group = Group("mmlu_stem", stem_config)
stem_group.add_task(mmlu_biology_task)
stem_group.add_task(mmlu_chemistry_task)

humanities_group = Group("mmlu_humanities", humanities_config)
humanities_group.add_task(mmlu_history_task)
humanities_group.add_task(mmlu_philosophy_task)

# Add to parent group
mmlu_group.add_task(stem_group)
mmlu_group.add_task(humanities_group)

# Get all tasks recursively
all_tasks = mmlu_group.get_all_tasks(recursive=True)
# Returns: [biology, chemistry, history, philosophy]
```

---

## Benefits of This Design

### 1. Consistency with Task Pattern

| Aspect | Task | Group |
|--------|------|-------|
| **What it represents** | Single evaluation | Collection of evaluations |
| **Configuration** | TaskConfig | GroupConfig |
| **Data** | Instances (samples) | Tasks (members) |
| **Computation** | Scoring samples | Aggregating task metrics |
| **Methods** | `process_instances()` | `compute_aggregate_metrics()` |

### 2. Simplicity

**Before**:
- 140-line recursive function
- Nested dict traversal
- Complex state management

**After**:
- Group class: ~100 lines
- Simple iteration: ~10 lines
- Clear object model

### 3. Clarity

```python
# Before: How do I get all tasks in a group?
# ??? Complex dict traversal

# After:
all_tasks = group.get_all_tasks()
```

### 4. Testability

```python
# Can test Group in isolation
def test_group_aggregation():
    group = Group("test", config)
    group.add_task(mock_task1)
    group.add_task(mock_task2)

    results = {
        "task1": {"acc,none": 0.8},
        "task2": {"acc,none": 0.9},
    }

    agg = group.compute_aggregate_metrics(results)
    assert agg["acc,none"] == 0.85  # Mean
```

### 5. Extensibility

Easy to add new features:
```python
# Group-level statistics
def get_statistics(self) -> dict:
    return {
        "num_tasks": len(self.get_all_tasks()),
        "num_subgroups": sum(1 for t in self.tasks.values() if isinstance(t, Group)),
        "total_samples": sum(t.sample_len for t in self.iter_tasks()),
    }

# Group validation
def validate(self) -> bool:
    """Check if all required tasks are present."""
    required_tasks = self.config.task
    for task_name in required_tasks:
        if task_name not in self:
            return False
    return True
```

---

## Migration Path

### Phase 1: Add Group Class (Non-Breaking)
1. Add `Group` class to `lm_eval/api/group.py`
2. Keep existing `consolidate_group_results()` as fallback
3. Add tests for `Group`

### Phase 2: Update Task Loading
1. Modify task factory to create `Group` objects
2. Build group hierarchy during loading
3. Pass groups to evaluator

### Phase 3: Simplify Consolidation
1. Update `consolidate_group_results()` to use `Group` objects
2. Remove complex recursion
3. Test thoroughly

### Phase 4: Clean Up
1. Remove old recursive logic
2. Update documentation
3. Add examples

---

## Conclusion

This design brings groups up to the same level as tasks:
- ✅ **First-class objects**: Groups are objects, not dicts
- ✅ **Clear API**: Simple methods for common operations
- ✅ **Self-contained**: Groups manage their own aggregation
- ✅ **Testable**: Can test in isolation
- ✅ **Extensible**: Easy to add features
- ✅ **Parallel to Task**: Consistent design pattern

Just as the Scorer refactor simplified scoring without adding complexity, this Group refactor simplifies group handling by making groups proper objects with clear responsibilities.
