# Group Architecture - Executive Summary

## The Problem

Currently, groups in lm-evaluation-harness are minimally implemented:
- `ConfigurableGroup` is just a thin wrapper around config dicts
- Only `mean` aggregation supported
- Tasks can't belong to multiple groups
- No hierarchy traversal methods
- Complex logic spread across multiple files
- Implicit task-group relationships

## The Solution: Group + Aggregator Architecture

Introduce dedicated **Group** classes and **Aggregator** pattern:

```
Groups  → Manage hierarchy and relationships
Aggregators → Compute group-wide metrics
Tasks → Know which groups they belong to
```

## Core Design

### 1. Group Base Class
```python
class Group(ABC):
    def __init__(self, config: GroupConfig, parent: Group | None = None):
        self.config = config
        self.parent = parent
        self.children: List[Group | Task] = []
        self._aggregator = AggregatorFactory.create_aggregator(config)

    def add_child(self, child: Group | Task) -> None:
        """Add task or subgroup."""

    def get_all_tasks(self) -> List[Task]:
        """Recursively get all leaf tasks."""

    def compute_metrics(self, task_results) -> Dict[str, float]:
        """Compute group metrics via Aggregator."""
        return self._aggregator.aggregate(self, task_results)

    def traverse(self, visitor: Callable) -> None:
        """Apply function to all nodes in tree."""
```

### 2. Concrete Group Types

**StandardGroup**: General hierarchical groups
```python
class StandardGroup(Group):
    # Supports nested groups and tasks
    # Most common use case
```

**TagGroup**: Flat, overlapping collections
```python
class TagGroup(StandardGroup):
    # Tags are flat (no hierarchy)
    # Tasks can have multiple tags
    # Special case of groups
```

### 3. Aggregator Pattern

```python
class Aggregator(ABC):
    def aggregate(
        self,
        group: Group,
        task_results: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """Aggregate task metrics into group metrics."""
```

**Implementations**:
- `MeanAggregator`: Weighted/unweighted arithmetic mean
- `HarmonicMeanAggregator`: For F1 scores, etc.
- `PassAtKAggregator`: For code generation metrics
- `CustomAggregator`: User-defined functions

### 4. GroupManager

```python
class GroupManager:
    """Central coordinator for group hierarchy."""

    def build_hierarchy(self, config_dict) -> None:
        """Build group tree from configs."""

    def get_groups_for_task(self, task_name) -> List[Group]:
        """Which groups contain this task?"""

    def get_tasks_for_group(self, group_name) -> List[Task]:
        """What tasks are in this group?"""

    def compute_all_group_metrics(self, task_results) -> Dict:
        """Compute metrics for all groups."""
```

### 5. Task Integration

```python
class Task(ABC):
    def __init__(self, config):
        # ... existing code ...
        self._groups: List[Group] = []  # Track group membership
        self._tags: List[str] = []

    @property
    def groups(self) -> List[Group]:
        """Get all groups this task belongs to."""
        return self._groups
```

## Data Flow

```
1. Load Config → Create GroupConfig objects

2. Build Hierarchy
   ├─ GroupManager.build_hierarchy()
   ├─ Create Group objects
   ├─ Link parents/children
   └─ Set bidirectional task ↔ group refs

3. Run Evaluation
   ├─ For each task:
   │   ├─ Scorer computes metrics
   │   └─ Store task results
   └─ task_results: {task_name: {metric: value}}

4. Compute Group Metrics
   ├─ For each group:
   │   ├─ group.get_all_tasks()
   │   ├─ Collect task metrics
   │   └─ aggregator.aggregate()
   └─ group_results: {group_name: {metric: value}}

5. Report
   └─ Display task and group results hierarchically
```

## Key Benefits

### 1. **Flexible Aggregation**
```yaml
aggregate_metric_list:
  - metric: f1
    aggregation: harmonic_mean  # Not limited to mean!

  - metric: pass@1
    aggregation: pass@k
    kwargs:
      k: 1
```

### 2. **Multiple Group Membership**
```python
# Tasks can belong to multiple groups
math_task.add_to_group(math_group)
math_task.add_to_group(reasoning_group)
math_task.add_to_group(hard_tasks_group)
```

### 3. **Explicit Relationships**
```python
# Task knows its groups
task.groups  # → [Group("math"), Group("reasoning")]

# Group knows its tasks
group.get_all_tasks()  # → [Task("gsm8k"), ...]
```

### 4. **Easy Traversal**
```python
# Get all tasks recursively
group.get_all_tasks()

# Get direct children only
group.get_direct_children()

# Custom operations
group.traverse(lambda node: print(node.name))

# Tree depth
group.depth()  # → 2
```

### 5. **Better Metadata**
```yaml
metadata:
  description: "Math word problems"
  difficulty: "medium"
  domain: "arithmetic"
  citation: "Cobbe et al. 2021"
  version: "2.0"
  custom_property: "value"
```

### 6. **Composability**
```yaml
# Groups work with Scorers and Filters
aggregate_metric_list:
  - metric: exact_match
    filter_list: [strict-match, flexible-extract]
    aggregation: mean
```

### 7. **Extensibility**
```python
# Custom group types
class DomainGroup(StandardGroup):
    def compute_domain_score(self):
        ...

# Custom aggregators
class GeometricMeanAggregator(Aggregator):
    def aggregate(self, group, results):
        values = [results[task][metric] for task in group.get_all_tasks()]
        return (prod(values)) ** (1/len(values))
```

## Comparison: Before vs After

### Before (Current)
```python
# Minimal wrapper
class ConfigurableGroup:
    def __init__(self, config):
        self._config = GroupConfig(**config)

    @property
    def group(self):
        return self._config.group

# Logic spread across multiple modules:
# - tasks/__init__.py: Loading
# - evaluator_utils.py: consolidate_group_results()
# - evaluator.py: Formatting

# Only mean aggregation
# No hierarchy methods
# No bidirectional references
# Tasks can't be in multiple groups
```

### After (Proposed)
```python
# Rich functionality
class StandardGroup(Group):
    def add_child(self, child):
        # Bidirectional linking
        ...

    def get_all_tasks(self):
        # Recursive traversal
        ...

    def compute_metrics(self, task_results):
        # Delegated to Aggregator
        return self._aggregator.aggregate(self, task_results)

# Centralized in GroupManager
# Multiple aggregation strategies
# Rich hierarchy API
# Bidirectional relationships
# Multiple group membership
```

**Result**: ~500 lines of scattered logic → Clean, modular architecture

## Example Use Cases

### Use Case 1: Hierarchical Benchmark with Custom Aggregation
```yaml
group: super_glue
task:
  - boolq_group  # Subgroup
  - copa_group   # Subgroup
  - rte_group    # Subgroup

aggregate_metric_list:
  - metric: acc
    aggregation: harmonic_mean  # Better for imbalanced tasks
    weight_by_size: false
```

### Use Case 2: Code Generation with pass@k
```yaml
group: code_benchmarks
task:
  - humaneval
  - mbpp
  - apps

aggregate_metric_list:
  - metric: pass@1
    aggregation: pass@k
    kwargs:
      k: 1

  - metric: pass@10
    aggregation: pass@k
    kwargs:
      k: 10
```

### Use Case 3: Multiple Filter Aggregation
```yaml
group: extraction_tasks
task:
  - ner
  - relation_extraction

aggregate_metric_list:
  - metric: f1
    aggregation: harmonic_mean
    filter_list: [strict, lenient]  # Both filters
```

### Use Case 4: Programmatic Group Creation
```python
# Create math tag
math_tag = TagGroup("math", description="Mathematics tasks")

# Add tasks
math_tag.add_child(task_gsm8k)
math_tag.add_child(task_math)
math_tag.add_child(task_aqua)

# Tasks know they're tagged
assert "math" in task_gsm8k.tags

# Compute metrics
math_metrics = math_tag.compute_metrics(task_results)
```

## Implementation Plan

### Phase 1: Core Classes (Week 1)
- [ ] Create `Group` base class
- [ ] Implement `StandardGroup` and `TagGroup`
- [ ] Create `Aggregator` base class
- [ ] Implement `MeanAggregator`, `HarmonicMeanAggregator`
- [ ] Implement `AggregatorFactory`
- [ ] Add unit tests

### Phase 2: GroupManager (Week 2)
- [ ] Create `GroupManager` class
- [ ] Implement hierarchy building
- [ ] Add bidirectional task ↔ group linking
- [ ] Add traversal methods
- [ ] Integration tests

### Phase 3: Task Integration (Week 3)
- [ ] Add `Task._groups` and `Task._tags`
- [ ] Update `Task.add_to_group()`
- [ ] Test with existing tasks
- [ ] Verify backwards compatibility

### Phase 4: Evaluation Flow (Week 4)
- [ ] Update `evaluator.py` to use `GroupManager`
- [ ] Replace `consolidate_group_results()` with `compute_all_group_metrics()`
- [ ] Update result formatting
- [ ] End-to-end tests with real benchmarks

### Phase 5: Enhanced Features (Week 5)
- [ ] Add `PassAtKAggregator`
- [ ] Support multiple group membership
- [ ] Enhanced metadata schema
- [ ] Custom group types documentation
- [ ] Migration guide

## Files to Create/Modify

**New Files:**
- `lm_eval/api/group.py` - Group classes
- `lm_eval/api/aggregator.py` - Aggregator classes
- `lm_eval/group_manager.py` - GroupManager
- `tests/test_group.py` - Group tests
- `tests/test_aggregator.py` - Aggregator tests

**Modified Files:**
- `lm_eval/api/task.py` - Add group tracking
- `lm_eval/evaluator.py` - Use GroupManager
- `lm_eval/tasks/__init__.py` - Integrate GroupManager
- `lm_eval/evaluator_utils.py` - Deprecate old consolidation

## Questions for Discussion

1. **Should groups validate their configs more strictly?**
   - E.g., ensure all child tasks exist?

2. **How to handle group version conflicts?**
   - If subgroups have different versions?

3. **Should we support conditional task inclusion?**
   ```yaml
   task:
     - taskA: {condition: "model_size > 7B"}
   ```

4. **Should groups have their own Scorers?**
   - For custom group-level evaluation

5. **How to represent task dependencies?**
   - "Task B requires Task A to complete first"

## Summary

This Group architecture provides:

✅ **Rich hierarchy management** with proper classes and methods
✅ **Flexible aggregation** beyond just mean (harmonic, pass@k, custom)
✅ **Explicit relationships** (bidirectional task ↔ group)
✅ **Multiple membership** (tasks in many groups)
✅ **Easy traversal** (get_all_tasks, depth, traverse)
✅ **Better metadata** (structured, extensible)
✅ **Composability** with Scorers and Filters
✅ **Extensibility** for custom groups and aggregators
✅ **Backwards compatibility** with existing YAML configs

The key insight: **Groups manage hierarchies and delegate metric aggregation to Aggregators**, mirroring how Tasks delegate scoring to Scorers.
