# Group Architecture - Examples

This document provides practical examples of how to use the new Group architecture.

## Table of Contents
- [Basic Group Creation](#basic-group-creation)
- [Hierarchical Groups](#hierarchical-groups)
- [Custom Aggregators](#custom-aggregators)
- [Tag Groups](#tag-groups)
- [GroupManager Usage](#groupmanager-usage)
- [Integration with Tasks](#integration-with-tasks)
- [Advanced Patterns](#advanced-patterns)

## Basic Group Creation

### Creating a Simple Group

```python
from lm_eval.api.group import GroupConfig, StandardGroup

# Define group configuration
config = GroupConfig(
    group="math_benchmarks",
    group_alias="Mathematics Benchmarks",
    task=["gsm8k", "math_qa", "aqua_rat"],
    aggregate_metric_list=[
        {
            "metric": "acc",
            "aggregation": "mean",
            "weight_by_size": True,
            "filter_list": "none"
        }
    ]
)

# Create the group
math_group = StandardGroup(config)

print(f"Group: {math_group.name}")
print(f"Alias: {math_group.alias}")
```

### Loading from YAML

```yaml
# math_benchmarks.yaml
group: math_benchmarks
group_alias: "Mathematics Benchmarks"
task:
  - gsm8k
  - math_qa
  - aqua_rat

aggregate_metric_list:
  - metric: acc
    aggregation: mean
    weight_by_size: true
    filter_list: none

metadata:
  version: 1.0
  description: "Collection of math word problem benchmarks"
  domain: "mathematics"
```

```python
import yaml
from lm_eval.api.group import GroupConfig, StandardGroup

# Load from YAML
with open("math_benchmarks.yaml") as f:
    config_dict = yaml.safe_load(f)

config = GroupConfig(**config_dict)
math_group = StandardGroup(config)
```

## Hierarchical Groups

### Creating Nested Groups

```python
from lm_eval.api.group import GroupConfig, StandardGroup

# Create child groups
math_config = GroupConfig(
    group="math_easy",
    task=["gsm8k", "math_qa"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)
math_easy = StandardGroup(math_config)

logic_config = GroupConfig(
    group="logic_easy",
    task=["logiqa", "logical_deduction"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)
logic_easy = StandardGroup(logic_config)

# Create parent group
reasoning_config = GroupConfig(
    group="reasoning_easy",
    group_alias="Easy Reasoning Tasks",
    task=["math_easy", "logic_easy"],
    aggregate_metric_list=[
        {
            "metric": "acc",
            "aggregation": "harmonic_mean",  # Better for imbalanced groups
            "weight_by_size": False
        }
    ]
)
reasoning_group = StandardGroup(reasoning_config)

# Link them
reasoning_group.add_child(math_easy)
reasoning_group.add_child(logic_easy)

# Navigate hierarchy
print(f"Depth of math_easy: {math_easy.depth()}")  # 1
print(f"Depth of reasoning_easy: {reasoning_group.depth()}")  # 0
print(f"Is reasoning_easy a leaf? {reasoning_group.is_leaf()}")  # False
```

### Traversing the Hierarchy

```python
# Collect all group names
group_names = []
reasoning_group.traverse(lambda node: group_names.append(
    getattr(node, 'name', getattr(node, 'task_name', 'unknown'))
))

print(f"All nodes: {group_names}")
# ['reasoning_easy', 'math_easy', 'logic_easy']

# Get all tasks recursively
all_tasks = reasoning_group.get_all_tasks()
print(f"All tasks: {[t.task_name for t in all_tasks]}")

# Get only direct children
direct_children = reasoning_group.get_direct_children()
print(f"Direct children: {[c.name for c in direct_children]}")
```

## Custom Aggregators

### Example 1: Minimum Score Aggregator

```python
from lm_eval.api.aggregator import Aggregator

class MinAggregator(Aggregator):
    """Aggregator that takes the minimum score across tasks."""

    def aggregate(self, group, task_results):
        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_list = agg_config.filter_list

            if isinstance(filter_list, str):
                filter_list = [filter_list]

            for filter_name in filter_list:
                metric_key = f"{metric_name},{filter_name}"

                values = []
                for task in tasks:
                    task_name = getattr(task, "task_name", str(task))
                    if (task_name in task_results and
                        metric_key in task_results[task_name]):
                        values.append(task_results[task_name][metric_key])

                if values:
                    group_metrics[metric_key] = min(values)

        return group_metrics


# Use it with a custom aggregation function
def min_aggregation(group, task_results):
    """Custom function for minimum aggregation."""
    # Create temporary config for MinAggregator
    from lm_eval.api.group import AggMetricConfig

    min_agg = MinAggregator(group.config)
    return min_agg.aggregate(group, task_results)


# In your group config
config = GroupConfig(
    group="challenge_set",
    task=["task1", "task2", "task3"],
    aggregate_metric_list=[
        {
            "metric": "acc",
            "aggregation": min_aggregation,  # Use custom function
            "filter_list": "none"
        }
    ]
)
```

### Example 2: Percentile Aggregator

```python
import numpy as np
from lm_eval.api.aggregator import Aggregator

class PercentileAggregator(Aggregator):
    """Aggregator that computes a specific percentile."""

    def __init__(self, config, percentile=50):
        super().__init__(config)
        self.percentile = percentile

    def aggregate(self, group, task_results):
        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_list = agg_config.filter_list

            if isinstance(filter_list, str):
                filter_list = [filter_list]

            for filter_name in filter_list:
                metric_key = f"{metric_name},{filter_name}"

                values = []
                for task in tasks:
                    task_name = getattr(task, "task_name", str(task))
                    if (task_name in task_results and
                        metric_key in task_results[task_name]):
                        values.append(task_results[task_name][metric_key])

                if values:
                    group_metrics[metric_key] = np.percentile(values, self.percentile)

        return group_metrics


# Create a factory function for it
def create_p75_aggregator(config):
    """Factory for 75th percentile aggregator."""
    return PercentileAggregator(config, percentile=75)


# Register and use
config = GroupConfig(
    group="robustness_check",
    task=["task1", "task2", "task3"],
    aggregate_metric_list=[
        {
            "metric": "acc",
            "aggregation": create_p75_aggregator,
            "filter_list": "none"
        }
    ]
)
```

### Example 3: Weighted Ensemble Aggregator

```python
from lm_eval.api.aggregator import Aggregator

class WeightedEnsembleAggregator(Aggregator):
    """Aggregator with custom per-task weights."""

    def __init__(self, config, task_weights=None):
        super().__init__(config)
        self.task_weights = task_weights or {}

    def aggregate(self, group, task_results):
        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_list = agg_config.filter_list

            if isinstance(filter_list, str):
                filter_list = [filter_list]

            for filter_name in filter_list:
                metric_key = f"{metric_name},{filter_name}"

                weighted_sum = 0
                total_weight = 0

                for task in tasks:
                    task_name = getattr(task, "task_name", str(task))

                    if (task_name in task_results and
                        metric_key in task_results[task_name]):

                        value = task_results[task_name][metric_key]
                        weight = self.task_weights.get(task_name, 1.0)

                        weighted_sum += value * weight
                        total_weight += weight

                if total_weight > 0:
                    group_metrics[metric_key] = weighted_sum / total_weight

        return group_metrics


# Use with custom weights
task_weights = {
    "gsm8k": 2.0,      # More important
    "math_qa": 1.0,    # Normal weight
    "aqua_rat": 0.5    # Less important
}

def weighted_agg(group, task_results):
    agg = WeightedEnsembleAggregator(group.config, task_weights=task_weights)
    return agg.aggregate(group, task_results)

config = GroupConfig(
    group="weighted_math",
    task=["gsm8k", "math_qa", "aqua_rat"],
    aggregate_metric_list=[
        {
            "metric": "acc",
            "aggregation": weighted_agg,
            "filter_list": "none"
        }
    ]
)
```

## Tag Groups

### Creating and Using Tags

```python
from lm_eval.api.group import TagGroup

# Create tag groups (flat collections)
math_tag = TagGroup("math", "Mathematics problems")
reasoning_tag = TagGroup("reasoning", "Reasoning benchmarks")
hard_tag = TagGroup("hard", "Challenging tasks")

# Create mock tasks
class MockTask:
    def __init__(self, name):
        self.task_name = name
        self._groups = []
        self._tags = []

task1 = MockTask("gsm8k")
task2 = MockTask("math_qa")
task3 = MockTask("logiqa")

# Add tasks to tags (tasks can have multiple tags)
math_tag.add_child(task1)
math_tag.add_child(task2)

reasoning_tag.add_child(task1)  # gsm8k is both math and reasoning
reasoning_tag.add_child(task2)
reasoning_tag.add_child(task3)

hard_tag.add_child(task1)

# Check task tags
print(f"task1 tags: {task1._tags}")  # ['math', 'reasoning', 'hard']
print(f"task2 tags: {task2._tags}")  # ['math', 'reasoning']

# Get all tasks in a tag
print(f"Math tasks: {[t.task_name for t in math_tag.get_all_tasks()]}")
# ['gsm8k', 'math_qa']
```

## GroupManager Usage

### Building and Managing Hierarchies

```python
from lm_eval.group_manager import GroupManager
from lm_eval.api.group import GroupConfig

# Create manager
manager = GroupManager()

# Define group configs
reasoning_config = GroupConfig(
    group="reasoning",
    task=["math_group", "logic_group"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

math_config = GroupConfig(
    group="math_group",
    task=["gsm8k", "math_qa"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

logic_config = GroupConfig(
    group="logic_group",
    task=["logiqa", "logical_deduction"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

# Build hierarchy
manager.build_hierarchy({
    "reasoning": reasoning_config,
    "math_group": math_config,
    "logic_group": logic_config
})

# Query the hierarchy
print(f"Root groups: {[g.name for g in manager.root_groups]}")
# ['reasoning']

print(f"All groups: {list(manager.groups.keys())}")
# ['reasoning', 'math_group', 'logic_group']

# Validate hierarchy
issues = manager.validate_hierarchy()
if issues:
    print(f"Validation issues: {issues}")
else:
    print("✓ Hierarchy is valid")

# Visualize hierarchy
print(manager.get_hierarchy_string())
```

### Computing Group Metrics

```python
# Mock task results
task_results = {
    "gsm8k": {
        "acc,none": 0.75,
        "samples": 1000
    },
    "math_qa": {
        "acc,none": 0.68,
        "samples": 500
    },
    "logiqa": {
        "acc,none": 0.62,
        "samples": 750
    },
    "logical_deduction": {
        "acc,none": 0.58,
        "samples": 600
    }
}

# Compute all group metrics
group_results = manager.compute_all_group_metrics(task_results)

for group_name, metrics in group_results.items():
    print(f"\n{group_name}:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")

# Output:
# math_group:
#   acc,none: 0.7200  # (0.75 + 0.68) / 2
#
# logic_group:
#   acc,none: 0.6000  # (0.62 + 0.58) / 2
#
# reasoning:
#   acc,none: 0.6600  # (0.72 + 0.60) / 2
```

## Integration with Tasks

### Adding Tasks to Groups Dynamically

```python
from lm_eval.group_manager import GroupManager
from lm_eval.api.group import StandardGroup, GroupConfig

manager = GroupManager()

# Create a group
config = GroupConfig(
    group="my_group",
    task=[],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)
group = StandardGroup(config)
manager.register_group(group)

# Create and register tasks
class Task:
    def __init__(self, name):
        self.task_name = name
        self._groups = []
        self._tags = []

task1 = Task("task1")
task2 = Task("task2")

manager.register_task(task1)
manager.register_task(task2)

# Add tasks to group dynamically
manager.add_task_to_group(task1, "my_group")
manager.add_task_to_group(task2, "my_group")

# Verify bidirectional links
print(f"Group children: {[c.task_name for c in group.children]}")
# ['task1', 'task2']

print(f"Task1 groups: {[g.name for g in task1._groups]}")
# ['my_group']

# Query from manager
groups_for_task = manager.get_groups_for_task("task1")
print(f"Groups containing task1: {[g.name for g in groups_for_task]}")
# ['my_group']

tasks_in_group = manager.get_tasks_for_group("my_group")
print(f"Tasks in my_group: {[t.task_name for t in tasks_in_group]}")
# ['task1', 'task2']
```

## Advanced Patterns

### Pattern 1: Domain-Specific Group with Custom Metrics

```python
from lm_eval.api.group import StandardGroup, GroupConfig
from lm_eval.api.aggregator import Aggregator

class CodeGenerationAggregator(Aggregator):
    """Custom aggregator for code generation tasks."""

    def aggregate(self, group, task_results):
        group_metrics = {}
        tasks = group.get_all_tasks()

        # Aggregate pass@k metrics
        for k in [1, 5, 10]:
            metric_key = f"pass@{k},none"
            values = []

            for task in tasks:
                task_name = getattr(task, "task_name", str(task))
                if (task_name in task_results and
                    metric_key in task_results[task_name]):
                    values.append(task_results[task_name][metric_key])

            if values:
                group_metrics[metric_key] = sum(values) / len(values)

        return group_metrics


config = GroupConfig(
    group="code_benchmarks",
    task=["humaneval", "mbpp", "apps"],
    aggregate_metric_list=[
        {
            "metric": "pass@1",
            "aggregation": lambda g, r: CodeGenerationAggregator(g.config).aggregate(g, r),
            "filter_list": "none"
        }
    ],
    metadata={
        "domain": "code_generation",
        "languages": ["python", "java", "cpp"]
    }
)
```

### Pattern 2: Conditional Group Metrics

```python
from lm_eval.api.aggregator import Aggregator

class ConditionalAggregator(Aggregator):
    """Aggregator that computes different metrics based on conditions."""

    def aggregate(self, group, task_results):
        group_metrics = {}
        tasks = group.get_all_tasks()

        # Check metadata for domain
        domain = group.metadata.get("domain", "general")

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_list = agg_config.filter_list

            if isinstance(filter_list, str):
                filter_list = [filter_list]

            for filter_name in filter_list:
                metric_key = f"{metric_name},{filter_name}"
                values = []

                for task in tasks:
                    task_name = getattr(task, "task_name", str(task))
                    if (task_name in task_results and
                        metric_key in task_results[task_name]):
                        values.append(task_results[task_name][metric_key])

                if values:
                    # Use different aggregation based on domain
                    if domain == "math":
                        # For math, use harmonic mean (penalizes low scores)
                        group_metrics[metric_key] = len(values) / sum(1/v for v in values if v > 0)
                    elif domain == "code":
                        # For code, use max (optimistic)
                        group_metrics[metric_key] = max(values)
                    else:
                        # Default: arithmetic mean
                        group_metrics[metric_key] = sum(values) / len(values)

        return group_metrics
```

### Pattern 3: Multi-Level Aggregation

```python
from lm_eval.api.group import StandardGroup, GroupConfig

# Create a complex hierarchy with different aggregations at each level

# Level 3: Leaf groups (by difficulty)
easy_config = GroupConfig(
    group="math_easy",
    task=["gsm8k_easy", "math_qa_easy"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

medium_config = GroupConfig(
    group="math_medium",
    task=["gsm8k_medium", "math_qa_medium"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

hard_config = GroupConfig(
    group="math_hard",
    task=["gsm8k_hard", "math_qa_hard"],
    aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}]
)

# Level 2: By difficulty (use harmonic mean to penalize failures)
by_difficulty_config = GroupConfig(
    group="math_by_difficulty",
    task=["math_easy", "math_medium", "math_hard"],
    aggregate_metric_list=[{
        "metric": "acc",
        "aggregation": "harmonic_mean",  # Emphasizes consistent performance
        "weight_by_size": False
    }]
)

# Level 1: Overall (use weighted mean by sample size)
overall_config = GroupConfig(
    group="math_overall",
    task=["math_by_difficulty"],
    aggregate_metric_list=[{
        "metric": "acc",
        "aggregation": "mean",
        "weight_by_size": True  # Weight by number of samples
    }]
)

# Build the hierarchy
from lm_eval.group_manager import GroupManager

manager = GroupManager()
manager.build_hierarchy({
    "math_overall": overall_config,
    "math_by_difficulty": by_difficulty_config,
    "math_easy": easy_config,
    "math_medium": medium_config,
    "math_hard": hard_config
})

# Each level uses appropriate aggregation for its purpose
```

## Summary

The Group architecture provides:

1. **Flexible Hierarchy**: Build complex nested structures with `StandardGroup`
2. **Custom Aggregation**: Create domain-specific aggregators beyond mean
3. **Tag Support**: Flat, overlapping collections with `TagGroup`
4. **Central Management**: Coordinate everything with `GroupManager`
5. **Bidirectional Links**: Tasks know their groups, groups know their tasks
6. **Extensibility**: Easy to add custom behaviors at any level

For more details, see:
- `GROUP_DESIGN.md` - Full architectural specification
- `MIGRATION_GUIDE.md` - Migrating existing code
- `lm_eval/api/group.py` - Group implementations
- `lm_eval/api/aggregator.py` - Aggregator implementations
- `lm_eval/group_manager.py` - GroupManager implementation
