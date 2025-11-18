# Migration Guide: Adopting the New Group Architecture

This guide helps you migrate from the old group system to the new Group + Aggregator architecture.

## Overview of Changes

### What Changed?

**Before (Old System)**:
- `ConfigurableGroup` - minimal wrapper around config dicts
- Only `mean` aggregation supported
- No explicit hierarchy methods
- Implicit task-group relationships
- `consolidate_group_results()` function for metric computation

**After (New System)**:
- `StandardGroup` / `TagGroup` - rich hierarchy management
- Multiple aggregation types: mean, harmonic_mean, geometric_mean, pass@k, custom
- Explicit parent-child relationships
- Bidirectional task ↔ group links
- `GroupManager` for centralized coordination
- `Aggregator` pattern for flexible metric computation

### Is This Breaking?

**No!** The new system is designed for backwards compatibility:
- Existing YAML configs continue to work
- Old `mean` aggregation still works
- `ConfigurableGroup` still exists alongside new classes
- Migration can be gradual

## Migration Scenarios

### Scenario 1: Basic Group (No Changes Needed)

If your group just uses simple mean aggregation, **no migration needed**.

**Your existing YAML**:
```yaml
group: my_benchmark
task:
  - task_a
  - task_b
aggregate_metric_list:
  - metric: acc
    aggregation: mean
    weight_by_size: true
```

**Status**: ✅ Works as-is with new architecture

The new system automatically handles this through `AggregatorFactory`, which creates a `MeanAggregator` for you.

---

### Scenario 2: Using New Aggregation Types

If you want to use aggregation beyond mean, update your config.

**Before (not possible)**:
```yaml
group: my_benchmark
aggregate_metric_list:
  - metric: f1
    aggregation: mean  # Only option
```

**After (multiple options)**:
```yaml
group: my_benchmark
aggregate_metric_list:
  - metric: f1
    aggregation: harmonic_mean  # Better for F1!

  - metric: pass@1
    aggregation: pass@k
    kwargs:
      k: 1
```

**Supported aggregation types**:
- `mean` - Arithmetic mean (default)
- `harmonic_mean` - Harmonic mean (good for F1, precision/recall)
- `geometric_mean` - Geometric mean (good for ratios)
- `pass@k` - Pass@k metric (for code generation)
- Custom functions (see below)

---

### Scenario 3: Programmatic Group Creation

If you create groups in Python code, migrate from `ConfigurableGroup` to `StandardGroup`.

**Before**:
```python
from lm_eval.api.group import ConfigurableGroup, GroupConfig

config = GroupConfig(
    group="my_benchmark",
    task=["task_a", "task_b"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

group = ConfigurableGroup(config=config.to_dict())
# Limited functionality - just a config wrapper
```

**After**:
```python
from lm_eval.api.group import GroupConfig, StandardGroup

config = GroupConfig(
    group="my_benchmark",
    task=["task_a", "task_b"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

group = StandardGroup(config)

# Rich functionality available:
group.depth()  # Get hierarchy depth
group.get_all_tasks()  # Get all tasks recursively
group.compute_metrics(task_results)  # Compute aggregated metrics
group.traverse(visitor_fn)  # Apply function to all nodes
```

---

### Scenario 4: Managing Group Hierarchies

If you manually manage group hierarchies, migrate to `GroupManager`.

**Before**:
```python
# Manually track groups
groups = {}
for name, config in group_configs.items():
    groups[name] = ConfigurableGroup(config=config)

# Manually compute metrics
from lm_eval.evaluator_utils import consolidate_group_results
group_results = consolidate_group_results(
    group_dict=group_configs,
    task_results=task_results,
    groups=task_name_to_group_dict,
)
```

**After**:
```python
from lm_eval.group_manager import GroupManager

# Create manager
manager = GroupManager()

# Build hierarchy automatically
manager.build_hierarchy(group_configs)

# Compute all metrics at once
group_results = manager.compute_all_group_metrics(task_results)

# Query the hierarchy
print(manager.get_hierarchy_string())
manager.validate_hierarchy()  # Check for issues
```

**Benefits**:
- Automatic parent-child linking
- Bidirectional task ↔ group relationships
- Hierarchy validation
- Cleaner API

---

### Scenario 5: Custom Aggregation Functions

If you need custom aggregation logic beyond the built-ins.

**Before (not supported)**:
```python
# Had to modify consolidate_group_results() directly
# or duplicate logic elsewhere
```

**After (fully supported)**:
```python
from lm_eval.api.aggregator import Aggregator

class PercentileAggregator(Aggregator):
    """Compute 90th percentile instead of mean."""

    def aggregate(self, group, task_results):
        import numpy as np
        group_metrics = {}

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_name = agg_config.filter_list[0]
            metric_key = f"{metric_name},{filter_name}"

            values = []
            for task in group.get_all_tasks():
                task_name = getattr(task, "task_name", task.name)
                if task_name in task_results and metric_key in task_results[task_name]:
                    values.append(task_results[task_name][metric_key])

            if values:
                group_metrics[metric_key] = np.percentile(values, 90)

        return group_metrics

# Use it in config
config = GroupConfig(
    group="my_benchmark",
    task=["task_a", "task_b"],
    aggregate_metric_list=[{
        "metric": "acc",
        "aggregation": PercentileAggregator(config).aggregate,  # Custom function
        "filter_list": "none"
    }]
)
```

Or use the `CustomAggregator` helper:
```python
from lm_eval.api.aggregator import CustomAggregator

def my_agg_fn(group, task_results, agg_config):
    # Your custom logic here
    return computed_value

# In your GroupConfig
config = GroupConfig(
    group="my_benchmark",
    aggregate_metric_list=[{
        "metric": "acc",
        "aggregation": my_agg_fn,  # Pass callable directly
    }]
)
```

---

### Scenario 6: Tags (Multiple Group Membership)

If tasks need to belong to multiple groups (e.g., tags).

**Before (not possible)**:
```python
# Tasks could only be in one group hierarchy
```

**After (fully supported)**:
```python
from lm_eval.api.group import TagGroup

# Create tags
math_tag = TagGroup("math", description="Mathematics tasks")
reasoning_tag = TagGroup("reasoning", description="Reasoning tasks")
hard_tag = TagGroup("hard", description="Difficult tasks")

# Add task to multiple tags
math_tag.add_child(gsm8k_task)
reasoning_tag.add_child(gsm8k_task)
hard_tag.add_child(gsm8k_task)

# Task knows its tags
print(gsm8k_task._tags)  # ['math', 'reasoning', 'hard']

# Each tag computes its own metrics
math_metrics = math_tag.compute_metrics(task_results)
reasoning_metrics = reasoning_tag.compute_metrics(task_results)
```

**In YAML**:
```yaml
# Define a tag group
group: math_tag
group_alias: "Mathematics Tasks"
task: []  # Will be populated dynamically
aggregate_metric_list:
  - metric: acc
    aggregation: mean
metadata:
  type: tag  # Mark as tag
```

---

### Scenario 7: Filtering + Aggregation

If you use multiple filters with groups.

**Before**:
```yaml
aggregate_metric_list:
  - metric: f1
    aggregation: mean
    filter_list: strict  # Only one filter
```

**After (multiple filters supported)**:
```yaml
aggregate_metric_list:
  - metric: f1
    aggregation: harmonic_mean
    filter_list: [strict, lenient]  # Multiple filters!

  - metric: exact_match
    aggregation: mean
    filter_list: [strict-match, flexible-extract]
```

The aggregator will compute metrics for each filter combination:
- `f1,strict`
- `f1,lenient`
- `exact_match,strict-match`
- `exact_match,flexible-extract`

---

## Common Migration Tasks

### Task 1: Replace `consolidate_group_results()` Calls

**Before**:
```python
from lm_eval.evaluator_utils import consolidate_group_results

group_results = consolidate_group_results(
    group_dict=group_configs,
    task_results=results,
    groups=task_name_to_group_dict,
)
```

**After**:
```python
from lm_eval.group_manager import GroupManager

# One-time setup
manager = GroupManager()
manager.build_hierarchy(group_configs)

# Register tasks
for task in tasks:
    manager.register_task(task)

# Compute metrics
group_results = manager.compute_all_group_metrics(task_results)
```

---

### Task 2: Update Task Creation to Track Groups

If you manually create tasks, ensure group tracking is initialized.

**Before**:
```python
class MyTask(Task):
    def __init__(self, config):
        super().__init__(config)
        # No group tracking
```

**After (already done in base Task class)**:
```python
class MyTask(Task):
    def __init__(self, config):
        super().__init__(config)
        # Base Task now has:
        # self._groups = []
        # self._tags = []
```

Tasks automatically track which groups they belong to when added via `group.add_child(task)`.

---

### Task 3: Leverage New Hierarchy Methods

**Before (manual traversal)**:
```python
# Manually traverse hierarchy
def get_all_tasks(group_name):
    tasks = []
    group = groups[group_name]
    for task_name in group.config.task:
        if task_name in groups:
            tasks.extend(get_all_tasks(task_name))
        else:
            tasks.append(tasks_dict[task_name])
    return tasks
```

**After (built-in methods)**:
```python
# Use built-in traversal
group = manager.groups["my_benchmark"]

# Get all tasks recursively
all_tasks = group.get_all_tasks()

# Get direct children only
direct_children = group.get_direct_children()

# Custom traversal
group.traverse(lambda node: print(node.name))

# Get depth
depth = group.depth()

# Check if leaf
is_leaf = group.is_leaf()
```

---

## Testing Your Migration

### Step 1: Verify Configs Still Load

```python
from lm_eval.api.group import GroupConfig

# Test your existing configs
config = GroupConfig(
    group="my_benchmark",
    task=["task_a", "task_b"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

print(config)  # Should load without errors
```

### Step 2: Test Group Creation

```python
from lm_eval.api.group import StandardGroup

group = StandardGroup(config)
print(f"Group: {group.name}")
print(f"Has aggregator: {group._aggregator is not None}")
```

### Step 3: Test Hierarchy Building

```python
from lm_eval.group_manager import GroupManager

manager = GroupManager()
manager.build_hierarchy(your_group_configs)

print(f"Groups: {len(manager.groups)}")
print(f"Root groups: {len(manager.root_groups)}")
print(manager.get_hierarchy_string())

# Validate
issues = manager.validate_hierarchy()
if issues:
    print("Issues found:", issues)
else:
    print("Hierarchy is valid!")
```

### Step 4: Test Metric Computation

```python
# Mock task results
task_results = {
    "task_a": {"acc,none": 0.8, "samples": 100},
    "task_b": {"acc,none": 0.6, "samples": 50},
}

# Compute group metrics
group_results = manager.compute_all_group_metrics(task_results)

print("Group metrics:", group_results)
```

### Step 5: Run Integration Test

Use the provided integration test:

```bash
python test_group_integration.py
```

All tests should pass:
- ✓ StandardGroup created successfully
- ✓ TagGroup created successfully
- ✓ MeanAggregator created via factory
- ✓ Group hierarchy works correctly
- ✓ Task-group bidirectional linking works
- ✓ GroupManager builds hierarchy correctly
- ✓ Group metric computation works

---

## Troubleshooting

### Issue 1: "Invalid aggregation type: 'harmonic_mean'"

**Cause**: Using old version of `AggMetricConfig` that only accepts 'mean'.

**Fix**: Update `lm_eval/api/group.py` to include new aggregation types:

```python
@dataclass
class AggMetricConfig(dict):
    # ...
    def __post_init__(self):
        valid_agg_types = ["mean", "harmonic_mean", "geometric_mean", "pass@k"]
        if self.aggregation not in valid_agg_types and not callable(self.aggregation):
            raise ValueError(f"Invalid aggregation type: '{self.aggregation}'.")
```

### Issue 2: "Group 'X' references unknown task/group: Y"

**Cause**: Task or subgroup hasn't been registered before building hierarchy.

**Fix**: Register tasks before building hierarchy:

```python
manager = GroupManager()

# Register tasks FIRST
for task in tasks:
    manager.register_task(task)

# Then build hierarchy
manager.build_hierarchy(group_configs)
```

### Issue 3: Root groups list has wrong count

**Cause**: Old version of `GroupManager.build_hierarchy()` doesn't update root_groups after relationships.

**Fix**: Ensure `build_hierarchy()` includes Phase 3:

```python
def build_hierarchy(self, config_dict):
    # Phase 1: Create all groups
    # ...

    # Phase 2: Establish relationships
    # ...

    # Phase 3: Update root_groups after relationships established
    self.root_groups = [g for g in self.groups.values() if g.parent is None]
```

### Issue 4: "Circular dependency detected"

**Cause**: Group A references Group B which references Group A.

**Fix**: Check your configs for cycles:

```python
issues = manager.validate_hierarchy()
print(issues)  # Will show: "Circular dependency detected: A -> B -> A"
```

Restructure your groups to avoid cycles.

### Issue 5: Custom aggregator not being used

**Cause**: Passing function incorrectly in config.

**Fix**: Pass callable directly:

```python
# Wrong
aggregate_metric_list=[{"aggregation": "my_custom_fn"}]

# Right
aggregate_metric_list=[{"aggregation": my_custom_fn}]
```

---

## Migration Checklist

Use this checklist to track your migration:

- [ ] Review your current group configs
- [ ] Identify which configs use only mean aggregation (no changes needed)
- [ ] Update configs that would benefit from other aggregation types
- [ ] Replace `consolidate_group_results()` calls with `GroupManager.compute_all_group_metrics()`
- [ ] Update any manual hierarchy traversal to use new methods
- [ ] Test configs load correctly with `GroupConfig()`
- [ ] Test group creation with `StandardGroup(config)`
- [ ] Test hierarchy building with `GroupManager.build_hierarchy()`
- [ ] Test metric computation with `compute_all_group_metrics()`
- [ ] Run integration tests (`test_group_integration.py`)
- [ ] Validate hierarchy with `manager.validate_hierarchy()`
- [ ] Update documentation for custom code
- [ ] Migrate any custom aggregation logic to `Aggregator` classes

---

## Getting Help

### Resources

- **Examples**: See `GROUP_EXAMPLES.md` for comprehensive usage examples
- **Design**: See `GROUP_SUMMARY.md` for architecture overview
- **Tests**: See `test_group_integration.py` for working examples
- **API**: See `lm_eval/api/group.py` and `lm_eval/api/aggregator.py` for full API

### Common Questions

**Q: Do I have to migrate immediately?**
A: No, the old system continues to work. Migrate when you need new features.

**Q: Can I mix old and new approaches?**
A: Yes, but for consistency we recommend migrating fully when you start.

**Q: What if I have custom group logic?**
A: Subclass `StandardGroup` or create custom `Aggregator` implementations.

**Q: How do I use multiple filters with groups?**
A: Pass list in `filter_list`: `filter_list: [strict, lenient]`

**Q: Can tasks be in multiple groups?**
A: Yes! Use `TagGroup` or add tasks to multiple `StandardGroup` instances.

**Q: How do I debug hierarchy issues?**
A: Use `manager.get_hierarchy_string()` and `manager.validate_hierarchy()`

---

## Summary

The new Group architecture provides:
- **More flexibility**: Multiple aggregation types beyond mean
- **Better organization**: Explicit hierarchy management
- **Cleaner code**: Centralized in `GroupManager`
- **Extensibility**: Custom groups and aggregators
- **Backwards compatibility**: Existing configs continue to work

Migration is **gradual** and **non-breaking**. Start by exploring new features in new configs, then migrate existing code as needed.

For complex migrations or questions, refer to `GROUP_EXAMPLES.md` or the integration tests.
