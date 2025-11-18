# Group Architecture Design

## Executive Summary

This design introduces a **Group** abstraction to make group handling more elegant and powerful in lm-evaluation-harness. Currently, groups are minimally implemented as thin wrappers around config dictionaries, with limited aggregation capabilities and complex hierarchy traversal logic spread across multiple modules.

The new architecture provides:
- **Dedicated Group classes** with proper hierarchy management
- **Flexible aggregation** beyond just mean (weighted, harmonic, custom)
- **Explicit membership tracking** (tasks know their groups, groups know their tasks)
- **Composable group metrics** that work with filters
- **Better metadata support** for group properties

## Current Architecture Analysis

### Current State

```
GroupConfig (dataclass) → ConfigurableGroup (thin wrapper)
        ↓
Evaluation flow spreads group logic across:
- TaskManager: Loading and indexing
- evaluator_utils.py: Metric consolidation (consolidate_group_results)
- evaluator.py: Result formatting
```

### Key Pain Points

1. **Limited Aggregation**: Only `mean` aggregation supported
   ```python
   # evaluator_utils.py:485-492
   if metric_config["aggregation"] == "mean":
       aggregate_fn = aggregate_subtask_metrics
   else:
       raise ValueError("Only 'mean' supported")
   ```

2. **No Group Hierarchy Methods**: Groups can't traverse their own children
   ```python
   # No methods like:
   # group.get_all_tasks()
   # group.get_subtasks()
   # group.depth()
   ```

3. **Implicit Membership**: Tasks don't know which groups they belong to

4. **Duplicate Prevention**: Tasks can't belong to multiple groups
   ```python
   # tasks/__init__.py:566
   raise ValueError("Found tasks in more than 1 group")
   ```

5. **Separate Group/Tag Concepts**: Confusing overlap between groups and tags

6. **Complex Traversal Logic**: Spread across multiple functions
   - `get_subtask_list()` - flattens hierarchy
   - `consolidate_group_results()` - aggregates recursively
   - Each with their own traversal implementation

7. **Limited Filter Integration**: Can't specify per-subtask filters

8. **Underused Metadata**: No standard schema or utilization

## Proposed Design: Group Architecture

### Design Principles

1. **Groups as First-Class Objects**: Dedicated classes with methods for hierarchy management
2. **Flexible Aggregation**: Support multiple aggregation strategies via Aggregator pattern
3. **Explicit Relationships**: Bidirectional task ↔ group membership
4. **Composability**: Groups work seamlessly with Scorers and Filters
5. **Extensibility**: Easy to add custom group behaviors
6. **Backwards Compatibility**: Support existing YAML configurations

### Core Abstraction: The Group Class

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Dict
from dataclasses import dataclass

TaskT = TypeVar('TaskT', bound='Task')
GroupT = TypeVar('GroupT', bound='Group')


class Group(ABC, Generic[TaskT]):
    """
    A Group represents a collection of tasks with shared properties.

    Responsibilities:
    - Maintain hierarchy (parent/child relationships)
    - Track member tasks
    - Compute group-wide metrics via Aggregators
    - Provide traversal methods
    - Store group metadata
    """

    def __init__(self, config: GroupConfig, parent: 'Group | None' = None):
        self.config = config
        self.name = config.group
        self.alias = config.group_alias or config.group
        self.parent = parent
        self.children: List[Group | TaskT] = []
        self.metadata = config.metadata or {}

        # Aggregator for computing group metrics
        self._aggregator = AggregatorFactory.create_aggregator(config)

    @abstractmethod
    def add_child(self, child: 'Group | TaskT') -> None:
        """Add a task or subgroup to this group."""
        raise NotImplementedError

    @abstractmethod
    def get_all_tasks(self) -> List[TaskT]:
        """Get all leaf tasks (recursively flattening hierarchy)."""
        raise NotImplementedError

    @abstractmethod
    def get_direct_children(self) -> List['Group | TaskT']:
        """Get immediate children only (no recursion)."""
        return self.children

    def compute_metrics(
        self,
        task_results: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Compute group-wide metrics from task results.

        Args:
            task_results: Dict mapping task_name -> {metric: value}

        Returns:
            Dict of group-level metrics
        """
        return self._aggregator.aggregate(self, task_results)

    def depth(self) -> int:
        """Return depth of this group in hierarchy (0 = root)."""
        if self.parent is None:
            return 0
        return 1 + self.parent.depth()

    def is_leaf(self) -> bool:
        """Check if this is a leaf group (no subgroups)."""
        return all(not isinstance(child, Group) for child in self.children)

    def traverse(self, visitor: Callable[[Group | TaskT], None]) -> None:
        """Apply visitor function to all nodes in tree."""
        visitor(self)
        for child in self.children:
            if isinstance(child, Group):
                child.traverse(visitor)
            else:
                visitor(child)
```

### Concrete Implementations

#### 1. StandardGroup

```python
class StandardGroup(Group):
    """
    Standard group implementation for most use cases.

    Handles hierarchical task collections with configurable aggregation.
    """

    def add_child(self, child: Group | Task) -> None:
        """Add task or subgroup, maintaining bidirectional links."""
        self.children.append(child)

        # Set parent reference on child
        if isinstance(child, Group):
            child.parent = self
        elif isinstance(child, Task):
            # Add this group to task's group list
            if not hasattr(child, '_groups'):
                child._groups = []
            child._groups.append(self)

    def get_all_tasks(self) -> List[Task]:
        """Recursively collect all leaf tasks."""
        tasks = []
        for child in self.children:
            if isinstance(child, Group):
                tasks.extend(child.get_all_tasks())
            else:
                tasks.append(child)
        return tasks

    def get_subtasks(self, max_depth: int | None = None) -> List[Task]:
        """Get tasks up to a certain depth."""
        if max_depth == 0:
            return []

        tasks = []
        for child in self.children:
            if isinstance(child, Task):
                tasks.append(child)
            elif max_depth is None or max_depth > 1:
                new_depth = None if max_depth is None else max_depth - 1
                tasks.extend(child.get_subtasks(max_depth=new_depth))
        return tasks
```

#### 2. TagGroup

```python
class TagGroup(StandardGroup):
    """
    Special group type for tags.

    Tags are flat collections (no hierarchy) that can overlap.
    Multiple tasks can have the same tag.
    """

    def __init__(self, tag_name: str, description: str | None = None):
        config = GroupConfig(
            group=tag_name,
            group_alias=description or tag_name,
            task=[],
            metadata={"type": "tag"}
        )
        super().__init__(config)

    def add_child(self, child: Task) -> None:
        """Tags only contain tasks, not subgroups."""
        if isinstance(child, Group):
            raise TypeError("Tags cannot contain subgroups")

        self.children.append(child)
        if not hasattr(child, '_tags'):
            child._tags = []
        child._tags.append(self.name)

    def get_all_tasks(self) -> List[Task]:
        """Tags are flat, so just return children."""
        return self.children
```

### The Aggregator Pattern

Similar to how Scorer separates filtering from scoring, **Aggregator** separates hierarchy management from metric aggregation.

```python
class Aggregator(ABC):
    """
    An Aggregator computes group-wide metrics from task results.

    Responsibilities:
    - Collect metrics from child tasks/groups
    - Apply aggregation function (mean, weighted mean, harmonic, etc.)
    - Handle different metric types appropriately
    - Support filter-specific aggregation
    """

    def __init__(self, config: GroupConfig):
        self.config = config
        self.agg_metric_configs = config.aggregate_metric_list or []

    @abstractmethod
    def aggregate(
        self,
        group: Group,
        task_results: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Aggregate task results into group metrics.

        Args:
            group: The group to aggregate for
            task_results: Task name -> {metric: value}

        Returns:
            Dict of aggregated metrics for the group
        """
        raise NotImplementedError


class MeanAggregator(Aggregator):
    """
    Aggregates metrics using (weighted) arithmetic mean.

    This is the most common aggregation strategy.
    """

    def aggregate(
        self,
        group: Group,
        task_results: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """Compute weighted or unweighted mean across tasks."""
        if not self.agg_metric_configs:
            return {}  # No aggregation configured

        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            weight_by_size = agg_config.weight_by_size
            filter_list = agg_config.filter_list

            # Collect metric values and sizes
            values = []
            weights = []

            for task in tasks:
                task_name = task.task_name
                if task_name not in task_results:
                    continue

                # Get metric with filter
                metric_key = f"{metric_name},{filter_list}"
                if metric_key in task_results[task_name]:
                    values.append(task_results[task_name][metric_key])

                    # Get sample size for weighting
                    if weight_by_size:
                        weights.append(task_results[task_name].get("samples", 1))
                    else:
                        weights.append(1)

            # Compute weighted mean
            if values:
                group_metrics[metric_key] = sum(
                    v * w for v, w in zip(values, weights)
                ) / sum(weights)

        return group_metrics


class HarmonicMeanAggregator(Aggregator):
    """
    Aggregates using harmonic mean.

    Useful for metrics like F1-score where harmonic mean is more appropriate
    than arithmetic mean.
    """

    def aggregate(self, group, task_results):
        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_list = agg_config.filter_list

            values = []
            for task in tasks:
                task_name = task.task_name
                metric_key = f"{metric_name},{filter_list}"

                if (task_name in task_results and
                    metric_key in task_results[task_name]):
                    values.append(task_results[task_name][metric_key])

            # Harmonic mean: n / sum(1/x_i)
            if values and all(v > 0 for v in values):
                group_metrics[metric_key] = len(values) / sum(1/v for v in values)

        return group_metrics


class PassAtKAggregator(Aggregator):
    """
    Aggregates using pass@k metric for code generation.

    Computes probability that at least one of k samples passes.
    """

    def __init__(self, config: GroupConfig, k: int = 1):
        super().__init__(config)
        self.k = k

    def aggregate(self, group, task_results):
        # pass@k = 1 - C(n-c, k) / C(n, k)
        # where n = total samples, c = correct samples
        ...


class CustomAggregator(Aggregator):
    """
    Allows user-defined aggregation functions.

    Useful for domain-specific metrics or complex aggregation logic.
    """

    def __init__(self, config: GroupConfig, agg_fn: Callable):
        super().__init__(config)
        self.agg_fn = agg_fn

    def aggregate(self, group, task_results):
        """Delegate to user-provided function."""
        return self.agg_fn(group, task_results)


class AggregatorFactory:
    """Factory for creating appropriate Aggregator based on config."""

    @staticmethod
    def create_aggregator(config: GroupConfig) -> Aggregator:
        """Create aggregator from group configuration."""
        if not config.aggregate_metric_list:
            return NoOpAggregator(config)  # No aggregation

        # Check first aggregation config to determine type
        first_agg = config.aggregate_metric_list[0]
        agg_type = first_agg.aggregation

        if agg_type == "mean":
            return MeanAggregator(config)
        elif agg_type == "harmonic_mean":
            return HarmonicMeanAggregator(config)
        elif agg_type == "pass@k":
            k = first_agg.kwargs.get("k", 1)
            return PassAtKAggregator(config, k=k)
        elif callable(agg_type):
            return CustomAggregator(config, agg_fn=agg_type)
        else:
            raise ValueError(f"Unknown aggregation type: {agg_type}")
```

### Integration with Task Class

```python
class Task(ABC):
    """Enhanced Task with group awareness."""

    def __init__(self, config: TaskConfig):
        # ... existing initialization ...

        # Track which groups this task belongs to
        self._groups: List[Group] = []
        self._tags: List[str] = []

    @property
    def groups(self) -> List[Group]:
        """Get all groups this task belongs to."""
        return self._groups

    @property
    def tags(self) -> List[str]:
        """Get all tags attached to this task."""
        return self._tags

    def add_to_group(self, group: Group) -> None:
        """Add this task to a group."""
        if group not in self._groups:
            self._groups.append(group)
            group.add_child(self)
```

### GroupManager

```python
class GroupManager:
    """
    Manages the group hierarchy and task-group relationships.

    Replaces the implicit hierarchy tracking in current TaskManager.
    """

    def __init__(self):
        self.groups: Dict[str, Group] = {}
        self.tasks: Dict[str, Task] = {}
        self.root_groups: List[Group] = []  # Top-level groups

    def register_group(self, group: Group) -> None:
        """Register a group in the manager."""
        self.groups[group.name] = group
        if group.parent is None:
            self.root_groups.append(group)

    def register_task(self, task: Task) -> None:
        """Register a task in the manager."""
        self.tasks[task.task_name] = task

    def build_hierarchy(self, config_dict: Dict) -> None:
        """Build group hierarchy from configuration."""
        # Create all groups first
        for name, config in config_dict.items():
            if isinstance(config, GroupConfig):
                group = StandardGroup(config)
                self.register_group(group)

        # Then establish parent-child relationships
        for name, group in self.groups.items():
            for child_name in group.config.task or []:
                if child_name in self.groups:
                    # Child is a subgroup
                    child_group = self.groups[child_name]
                    group.add_child(child_group)
                elif child_name in self.tasks:
                    # Child is a task
                    task = self.tasks[child_name]
                    group.add_child(task)

    def get_groups_for_task(self, task_name: str) -> List[Group]:
        """Get all groups containing a task."""
        task = self.tasks.get(task_name)
        return task.groups if task else []

    def get_tasks_for_group(self, group_name: str) -> List[Task]:
        """Get all tasks in a group (recursively)."""
        group = self.groups.get(group_name)
        return group.get_all_tasks() if group else []

    def traverse_hierarchy(
        self,
        visitor: Callable[[Group | Task], None],
        root: Group | None = None
    ) -> None:
        """Traverse hierarchy applying visitor function."""
        roots = [root] if root else self.root_groups
        for root_group in roots:
            root_group.traverse(visitor)

    def compute_all_group_metrics(
        self,
        task_results: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, float]]:
        """Compute metrics for all groups."""
        group_results = {}

        for group_name, group in self.groups.items():
            group_results[group_name] = group.compute_metrics(task_results)

        return group_results
```

## Data Flow

```
1. Load Configuration
   ├─ Parse YAML files
   └─ Create GroupConfig objects

2. Build Hierarchy
   ├─ GroupManager.build_hierarchy()
   ├─ Create Group objects
   ├─ Establish parent-child links
   └─ Set bidirectional task ↔ group references

3. Run Evaluation
   ├─ For each task:
   │   ├─ Build requests
   │   ├─ Run model
   │   ├─ Apply filters
   │   ├─ Score instances (via Scorer)
   │   └─ Aggregate task metrics
   └─ Store task_results

4. Compute Group Metrics
   ├─ GroupManager.compute_all_group_metrics()
   ├─ For each group:
   │   ├─ Get all member tasks
   │   ├─ Collect their metrics
   │   ├─ Aggregator.aggregate()
   │   └─ Store group metrics
   └─ Return group_results

5. Report Results
   ├─ Format task results
   ├─ Format group results (with hierarchy indentation)
   └─ Display or write to file
```

## Benefits of This Design

### 1. **Separation of Concerns**
- `Group`: Manages hierarchy and relationships
- `Aggregator`: Computes group metrics
- `Task`: Focuses on individual evaluation

### 2. **Flexible Aggregation**
```yaml
aggregate_metric_list:
  - metric: f1
    aggregation: harmonic_mean  # Not just mean!
    weight_by_size: false

  - metric: pass@1
    aggregation: pass@k
    kwargs:
      k: 1
```

### 3. **Explicit Relationships**
```python
# Task knows its groups
task.groups  # → [Group("math"), Group("reasoning")]

# Group knows its tasks
group.get_all_tasks()  # → [Task("gsm8k"), Task("math_qa")]
```

### 4. **Multiple Group Membership**
```python
# Task can be in multiple groups
math_task.add_to_group(math_group)
math_task.add_to_group(hard_tasks_group)
# No more "Found tasks in more than 1 group" error!
```

### 5. **Easy Hierarchy Traversal**
```python
# Get all tasks at any depth
group.get_all_tasks()

# Get only direct children
group.get_direct_children()

# Custom traversal
group.traverse(lambda node: print(node.name))
```

### 6. **Better Metadata Support**
```python
group.metadata = {
    "description": "Math word problems",
    "difficulty": "medium",
    "domain": "arithmetic",
    "citation": "...",
    "version": "2.0"
}
```

### 7. **Composability with Scorer**
```python
# Groups work seamlessly with filtered metrics
aggregate_metric_list:
  - metric: exact_match
    filter_list: [strict-match, flexible-extract]
    aggregation: mean
```

### 8. **Extensibility**
```python
# Custom group types
class DomainGroup(StandardGroup):
    """Group for tasks in same domain."""
    def compute_domain_score(self):
        ...

# Custom aggregators
class GeometricMeanAggregator(Aggregator):
    def aggregate(self, group, results):
        # Implement geometric mean
        ...
```

## Migration Path

### Phase 1: Add Group Classes (Backwards Compatible)
- Add `Group`, `Aggregator` base classes
- Implement `StandardGroup`, `TagGroup`
- Implement core aggregators (`MeanAggregator`, etc.)
- Add `GroupManager`

### Phase 2: Integrate with Existing Code
- Update `TaskManager` to use `GroupManager`
- Keep existing `consolidate_group_results()` as fallback
- Add `Task._groups` and `Task._tags` attributes
- Support both old and new group handling

### Phase 3: Migrate Evaluation Flow
- Update `evaluator.py` to use `GroupManager.compute_all_group_metrics()`
- Replace recursive consolidation with `Aggregator` pattern
- Update result formatting to use `Group.traverse()`

### Phase 4: Enhanced Features
- Add more aggregation types (harmonic, geometric, pass@k)
- Support multiple group membership
- Enhanced metadata schema
- Custom group types and aggregators

### Phase 5: Deprecate Old Code
- Remove `consolidate_group_results()`
- Remove `ConfigurableGroup` (use `StandardGroup`)
- Clean up recursive traversal helpers

## Configuration Examples

### Basic Group
```yaml
group: mmlu_pro
group_alias: "MMLU Professional"
task:
  - mmlu_pro_biology
  - mmlu_pro_chemistry
  - mmlu_pro_physics

aggregate_metric_list:
  - metric: acc
    aggregation: mean
    weight_by_size: true
    filter_list: default

metadata:
  version: 2.0
  description: "Multiple choice questions for professionals"
  domain: "knowledge"
```

### Advanced Aggregation
```yaml
group: code_generation
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

  - metric: compilation_rate
    aggregation: mean
    weight_by_size: false
```

### Nested Groups
```yaml
group: reasoning
task:
  - math_reasoning  # Sub-group
  - logical_reasoning  # Sub-group
  - commonsense_reasoning  # Sub-group

aggregate_metric_list:
  - metric: acc
    aggregation: harmonic_mean  # Better for imbalanced subtasks
```

### Multiple Filters
```yaml
group: extraction_tasks
task:
  - ner
  - relation_extraction
  - event_extraction

aggregate_metric_list:
  - metric: f1
    aggregation: harmonic_mean
    filter_list: [strict, lenient]  # Aggregate across both filters
```

## Open Questions

1. **Should groups support conditional inclusion?**
   ```yaml
   task:
     - taskA: if model_size > 7B
     - taskB: always
   ```

2. **Should we support group-level filters?**
   ```yaml
   group_filter:
     - function: top_k
       k: 5  # Only aggregate top 5 performing tasks
   ```

3. **How to handle cyclic dependencies?**
   - Prevent at config load time?
   - Allow but detect cycles during traversal?

4. **Should groups have their own Scorers?**
   - For computing group-specific metrics beyond aggregation

5. **How to represent group difficulty/properties?**
   - Metadata field?
   - Dedicated properties in GroupConfig?

## Summary

This Group architecture provides:

✅ **Dedicated classes** for proper hierarchy management
✅ **Flexible aggregation** via Aggregator pattern
✅ **Explicit relationships** between tasks and groups
✅ **Multiple membership** support
✅ **Easy traversal** with built-in methods
✅ **Composability** with Scorers and Filters
✅ **Extensibility** for custom group types
✅ **Backwards compatibility** with existing configs

The key insight: **Groups are responsible for managing hierarchies and delegating metric aggregation to Aggregators**, similar to how Tasks delegate scoring to Scorers.
