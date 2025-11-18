import abc
from dataclasses import asdict, dataclass
from inspect import getsource
from typing import Any, Callable, List, Optional, Union


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


# ============================================================================
# New Group Architecture (with hierarchy management and flexible aggregation)
# ============================================================================


class Group(abc.ABC):
    """
    A Group represents a collection of tasks with shared properties.

    Responsibilities:
    - Maintain hierarchy (parent/child relationships)
    - Track member tasks
    - Compute group-wide metrics via Aggregators
    - Provide traversal methods
    - Store group metadata

    This is the new architecture for groups, providing rich hierarchy management
    and flexible metric aggregation beyond just mean.
    """

    def __init__(self, config: GroupConfig, parent: Optional["Group"] = None):
        """
        Initialize a group.

        Args:
            config: GroupConfig containing group settings
            parent: Optional parent group in hierarchy
        """
        self.config = config
        self.name = config.group
        self.alias = config.group_alias or config.group
        self.parent = parent
        self.children: List[Union["Group", Any]] = []  # Group or Task objects
        self.metadata = config.metadata or {}

        # Aggregator will be set by factory in subclasses
        self._aggregator = None

    @abc.abstractmethod
    def add_child(self, child: Union["Group", Any]) -> None:
        """
        Add a task or subgroup to this group.

        Args:
            child: Group or Task object to add as child
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement add_child")

    @abc.abstractmethod
    def get_all_tasks(self) -> List[Any]:
        """
        Get all leaf tasks (recursively flattening hierarchy).

        Returns:
            List of all Task objects in this group and subgroups
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_all_tasks"
        )

    def get_direct_children(self) -> List[Union["Group", Any]]:
        """
        Get immediate children only (no recursion).

        Returns:
            List of direct child Group or Task objects
        """
        return self.children

    def compute_metrics(
        self, task_results: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """
        Compute group-wide metrics from task results.

        This delegates to the Aggregator to handle the actual computation.

        Args:
            task_results: Dict mapping task_name -> {metric: value}

        Returns:
            Dict of group-level aggregated metrics
        """
        if self._aggregator is None:
            return {}
        return self._aggregator.aggregate(self, task_results)

    def depth(self) -> int:
        """
        Return depth of this group in hierarchy (0 = root).

        Returns:
            Integer depth, with 0 being root level
        """
        if self.parent is None:
            return 0
        return 1 + self.parent.depth()

    def is_leaf(self) -> bool:
        """
        Check if this is a leaf group (contains no subgroups).

        Returns:
            True if all children are tasks, False if any are groups
        """
        return all(not isinstance(child, Group) for child in self.children)

    def traverse(self, visitor: Callable[[Union["Group", Any]], None]) -> None:
        """
        Apply visitor function to all nodes in tree (DFS).

        Args:
            visitor: Function to call on each node (group or task)
        """
        visitor(self)
        for child in self.children:
            if isinstance(child, Group):
                child.traverse(visitor)
            else:
                visitor(child)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, children={len(self.children)})"


class StandardGroup(Group):
    """
    Standard group implementation for most use cases.

    Handles hierarchical task collections with configurable aggregation.
    Supports nested groups and maintains bidirectional parent-child links.
    """

    def __init__(self, config: GroupConfig, parent: Optional[Group] = None):
        """
        Initialize a standard group.

        Args:
            config: GroupConfig containing group settings
            parent: Optional parent group
        """
        super().__init__(config, parent)

        # Import here to avoid circular dependency
        from lm_eval.api.aggregator import AggregatorFactory

        self._aggregator = AggregatorFactory.create_aggregator(config)

    def add_child(self, child: Union[Group, Any]) -> None:
        """
        Add task or subgroup, maintaining bidirectional links.

        Args:
            child: Group or Task object to add
        """
        if child in self.children:
            return  # Already added

        self.children.append(child)

        # Set parent reference on child
        if isinstance(child, Group):
            child.parent = self
        else:
            # Assume it's a Task - add this group to task's group list
            if not hasattr(child, "_groups"):
                child._groups = []
            if self not in child._groups:
                child._groups.append(self)

    def get_all_tasks(self) -> List[Any]:
        """
        Recursively collect all leaf tasks.

        Returns:
            Flat list of all Task objects in hierarchy
        """
        tasks = []
        for child in self.children:
            if isinstance(child, Group):
                tasks.extend(child.get_all_tasks())
            else:
                tasks.append(child)
        return tasks

    def get_subtasks(self, max_depth: Optional[int] = None) -> List[Any]:
        """
        Get tasks up to a certain depth.

        Args:
            max_depth: Maximum depth to traverse (None = unlimited)

        Returns:
            List of Task objects up to max_depth
        """
        if max_depth == 0:
            return []

        tasks = []
        for child in self.children:
            if isinstance(child, Group):
                if max_depth is None or max_depth > 1:
                    new_depth = None if max_depth is None else max_depth - 1
                    tasks.extend(child.get_subtasks(max_depth=new_depth))
            else:
                tasks.append(child)
        return tasks


class TagGroup(StandardGroup):
    """
    Special group type for tags.

    Tags are flat collections (no hierarchy) that can overlap.
    Multiple tasks can have the same tag, and tasks can have multiple tags.
    """

    def __init__(self, tag_name: str, description: Optional[str] = None):
        """
        Initialize a tag group.

        Args:
            tag_name: Name of the tag
            description: Optional human-readable description
        """
        config = GroupConfig(
            group=tag_name,
            group_alias=description or tag_name,
            task=[],
            metadata={"type": "tag"},
        )
        super().__init__(config)

    def add_child(self, child: Any) -> None:
        """
        Tags only contain tasks, not subgroups.

        Args:
            child: Task object to add

        Raises:
            TypeError: If attempting to add a Group
        """
        if isinstance(child, Group):
            raise TypeError("Tags cannot contain subgroups - they are flat collections")

        if child in self.children:
            return

        self.children.append(child)

        # Add tag to task's tag list
        if not hasattr(child, "_tags"):
            child._tags = []
        if self.name not in child._tags:
            child._tags.append(self.name)

    def get_all_tasks(self) -> List[Any]:
        """
        Tags are flat, so just return children.

        Returns:
            List of Task objects
        """
        return self.children
