import abc
from dataclasses import asdict, dataclass
from inspect import getsource
from typing import TYPE_CHECKING, Any, Callable, Iterator, List, Optional, Union

if TYPE_CHECKING:
    from lm_eval.api.task import Task


@dataclass
class AggMetricConfig(dict):
    metric: Optional[str] = None
    aggregation: Optional[str] = "mean"
    weight_by_size: Optional[str] = False
    # list of filter names which should be incorporated into the aggregated metric.
    filter_list: Optional[Union[str, list]] = "none"

    def __post_init__(self):
        if self.aggregation != "mean" and not callable(self.aggregation):
            raise ValueError(
                f"Currently, 'mean' is the only pre-defined aggregation across groups' subtasks. Got '{self.aggregation}'."
            )

        if isinstance(self.filter_list, str):
            self.filter_list = [self.filter_list]


@dataclass
class GroupConfig(dict):
    group: Optional[str] = None
    group_alias: Optional[str] = None
    task: Optional[Union[str, list]] = None
    aggregate_metric_list: Optional[
        Union[List[AggMetricConfig], AggMetricConfig, dict]
    ] = None
    metadata: Optional[dict] = (
        None  # by default, not used in the code. allows for users to pass arbitrary info to tasks
    )

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        return setattr(self, item, value)

    def __post_init__(self):
        if self.aggregate_metric_list is not None:
            if isinstance(self.aggregate_metric_list, dict):
                self.aggregate_metric_list = [self.aggregate_metric_list]

            self.aggregate_metric_list = [
                AggMetricConfig(**item) if isinstance(item, dict) else item
                for item in self.aggregate_metric_list
            ]

    def to_dict(self, keep_callable: bool = False) -> dict:
        """dumps the current config as a dictionary object, as a printable format.
        null fields will not be printed.
        Used for dumping results alongside full task configuration

        :return: dict
            A printable dictionary version of the TaskConfig object.

        # TODO: should any default value in the TaskConfig not be printed?
        """
        cfg_dict = asdict(self)
        # remove values that are `None`
        for k, v in list(cfg_dict.items()):
            if callable(v):
                cfg_dict[k] = self.serialize_function(v, keep_callable=keep_callable)
        return cfg_dict

    def serialize_function(
        self, value: Union[Callable, str], keep_callable=False
    ) -> Union[Callable, str]:
        """Serializes a given function or string.

        If 'keep_callable' is True, the original callable is returned.
        Otherwise, attempts to return the source code of the callable using 'getsource'.
        """
        if keep_callable:
            return value
        else:
            try:
                return getsource(value)
            except (TypeError, OSError):
                return str(value)


class ConfigurableGroup(abc.ABC):
    def __init__(
        self,
        config: Optional[dict] = None,
    ) -> None:
        self._config = GroupConfig(**config)

    @property
    def group(self):
        return self._config.group

    @property
    def group_alias(self):
        return self._config.group_alias

    @property
    def version(self):
        return self._config.version

    @property
    def config(self):
        return self._config.to_dict()

    @property
    def group_name(self) -> Any:
        return self._config.group

    def __repr__(self):
        return f"ConfigurableGroup(group={self.group},group_alias={self.group_alias})"


class Group:
    """Represents a group of tasks with aggregated metrics.

    A Group is a collection of Tasks (and potentially sub-Groups) that
    can compute aggregated metrics across its members.

    This provides a first-class object for groups, parallel to the Task class,
    making group operations clear and testable.

    Example:
        >>> group = Group("mmlu", config)
        >>> group.add_task(mmlu_anatomy_task)
        >>> group.add_task(mmlu_biology_task)
        >>> agg_metrics = group.compute_aggregate_metrics(task_results)

    Attributes:
        name: Group name (e.g., "mmlu")
        config: GroupConfig with aggregation settings
        tasks: Dictionary of tasks/subgroups in this group
        alias: Display name for the group
        version: Version string from metadata
    """

    def __init__(self, name: str, config: GroupConfig):
        """Initialize a Group.

        Args:
            name: Group name
            config: GroupConfig with aggregation settings
        """
        self.name = name
        self.config = config
        self.tasks: dict[str, Union["Task", "Group"]] = {}
        self.alias = config.group_alias or name
        self.version = config.metadata.get("version") if config.metadata else None

    def add_task(self, task: Union["Task", "Group"]) -> None:
        """Add a task or subgroup to this group.

        Args:
            task: Task or Group instance to add
        """
        from lm_eval.api.task import Task

        key = task.task_name if isinstance(task, Task) else task.name
        self.tasks[key] = task

    def remove_task(self, task_name: str) -> None:
        """Remove a task from this group.

        Args:
            task_name: Name of task to remove
        """
        self.tasks.pop(task_name, None)

    def get_task(self, task_name: str) -> Optional[Union["Task", "Group"]]:
        """Get a specific task by name.

        Args:
            task_name: Name of task to retrieve

        Returns:
            Task or Group instance, or None if not found
        """
        return self.tasks.get(task_name)

    def get_all_tasks(self, recursive: bool = True) -> List["Task"]:
        """Get all Task instances, optionally recursively through subgroups.

        Args:
            recursive: If True, recursively get tasks from subgroups

        Returns:
            List of all Task instances in this group
        """
        from lm_eval.api.task import Task

        tasks = []
        for item in self.tasks.values():
            if isinstance(item, Task):
                tasks.append(item)
            elif isinstance(item, Group) and recursive:
                tasks.extend(item.get_all_tasks(recursive=True))
        return tasks

    def iter_tasks(self, recursive: bool = True) -> Iterator["Task"]:
        """Iterate over all tasks in this group.

        Args:
            recursive: If True, recursively iterate through subgroups

        Yields:
            Task instances
        """
        from lm_eval.api.task import Task

        for item in self.tasks.values():
            if isinstance(item, Task):
                yield item
            elif isinstance(item, Group) and recursive:
                yield from item.iter_tasks(recursive=True)

    def compute_aggregate_metrics(
        self, task_results: dict[str, dict], bootstrap_iters: int = 100000
    ) -> dict:
        """Compute aggregated metrics for this group.

        Aggregates metrics from all subtasks according to the group's
        aggregate_metric_list configuration.

        Args:
            task_results: Dictionary mapping task_name -> task_metrics
            bootstrap_iters: Number of bootstrap iterations for stderr

        Returns:
            Dictionary of aggregated metrics with keys like "metric,filter"
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
                        values, sizes, agg_config.weight_by_size
                    )
                elif callable(agg_config.aggregation):
                    agg_value = agg_config.aggregation(values, sizes)
                else:
                    raise ValueError(
                        f"Unknown aggregation method: {agg_config.aggregation}"
                    )

                agg_metrics[metric_key] = agg_value
                agg_metrics["samples"] = sum(sizes)

                # Aggregate stderr
                if "N/A" not in stderrs:
                    agg_metrics[stderr_key] = pooled_sample_stderr(stderrs, sizes)
                else:
                    agg_metrics[stderr_key] = "N/A"

        return agg_metrics

    def get_statistics(self) -> dict:
        """Get statistics about this group.

        Returns:
            Dictionary with group statistics (num_tasks, num_subgroups, etc.)
        """
        from lm_eval.api.task import Task

        num_subgroups = sum(1 for t in self.tasks.values() if isinstance(t, Group))
        all_tasks = self.get_all_tasks()

        return {
            "name": self.name,
            "num_direct_members": len(self.tasks),
            "num_tasks": len(all_tasks),
            "num_subgroups": num_subgroups,
            "task_names": [t.task_name for t in all_tasks],
        }

    def __repr__(self):
        return f"Group(name={self.name}, tasks={len(self.tasks)})"

    def __len__(self):
        return len(self.tasks)

    def __contains__(self, task_name: str):
        return task_name in self.tasks

    def __iter__(self):
        """Iterate over direct members (tasks and subgroups)."""
        return iter(self.tasks.values())
