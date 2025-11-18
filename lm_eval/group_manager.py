"""
GroupManager for managing group hierarchies and task-group relationships.

The GroupManager serves as a central coordinator for:
- Building group hierarchies from configurations
- Tracking bidirectional task ↔ group relationships
- Computing group-wide metrics
- Traversing the group tree
"""

from collections.abc import Callable
from typing import Any, Optional

from lm_eval.api.group import Group, GroupConfig, StandardGroup, TagGroup


class GroupManager:
    """
    Manages the group hierarchy and task-group relationships.

    This replaces the implicit hierarchy tracking in the current TaskManager
    with an explicit, manageable structure that provides:
    - Easy hierarchy traversal
    - Bidirectional task ↔ group links
    - Centralized group metric computation
    - Support for multiple group membership
    """

    def __init__(self):
        """Initialize an empty group manager."""
        self.groups: dict[str, Group] = {}
        self.tasks: dict[str, Any] = {}  # Task name -> Task object
        self.root_groups: list[Group] = []  # Top-level groups (no parent)

    def register_group(self, group: Group) -> None:
        """
        Register a group in the manager.

        Args:
            group: Group object to register
        """
        self.groups[group.name] = group

        # If group has no parent, it's a root group
        if group.parent is None:
            if group not in self.root_groups:
                self.root_groups.append(group)

    def register_task(self, task: Any) -> None:
        """
        Register a task in the manager.

        Args:
            task: Task object to register
        """
        task_name = getattr(task, "task_name", None) or getattr(
            task, "name", str(task)
        )
        self.tasks[task_name] = task

    def build_hierarchy(
        self, config_dict: dict[str, GroupConfig | dict]
    ) -> None:
        """
        Build group hierarchy from configuration dictionary.

        This creates all groups, establishes parent-child relationships,
        and links tasks to groups.

        Args:
            config_dict: Dict mapping group_name -> GroupConfig or config dict
        """
        # Phase 1: Create all groups first
        for name, config in config_dict.items():
            if isinstance(config, dict):
                # Check if it's a group config (has 'group' field)
                if "group" in config:
                    config = GroupConfig(**config)
                else:
                    continue

            if isinstance(config, GroupConfig):
                # Check if this is a tag
                is_tag = (
                    config.metadata
                    and config.metadata.get("type") == "tag"
                )

                if is_tag:
                    group = TagGroup(
                        tag_name=config.group,
                        description=config.group_alias,
                    )
                else:
                    group = StandardGroup(config)

                self.register_group(group)

        # Phase 2: Establish parent-child relationships
        for name, group in self.groups.items():
            task_list = group.config.task or []

            # Handle both single task and list of tasks
            if isinstance(task_list, str):
                task_list = [task_list]

            for child_name in task_list:
                if child_name in self.groups:
                    # Child is a subgroup
                    child_group = self.groups[child_name]
                    group.add_child(child_group)
                elif child_name in self.tasks:
                    # Child is a task
                    task = self.tasks[child_name]
                    group.add_child(task)
                # else: Task/group not found yet, might be added later

    def add_task_to_group(self, task: Any, group_name: str) -> None:
        """
        Add a task to a group.

        Args:
            task: Task object
            group_name: Name of group to add task to

        Raises:
            ValueError: If group doesn't exist
        """
        if group_name not in self.groups:
            raise ValueError(f"Group '{group_name}' not found")

        group = self.groups[group_name]
        group.add_child(task)

        # Register task if not already registered
        task_name = getattr(task, "task_name", None) or getattr(
            task, "name", str(task)
        )
        if task_name not in self.tasks:
            self.register_task(task)

    def get_groups_for_task(self, task_name: str) -> list[Group]:
        """
        Get all groups containing a task.

        Args:
            task_name: Name of the task

        Returns:
            List of Group objects that contain this task
        """
        task = self.tasks.get(task_name)
        if task is None:
            return []

        return getattr(task, "_groups", [])

    def get_tasks_for_group(self, group_name: str) -> list[Any]:
        """
        Get all tasks in a group (recursively).

        Args:
            group_name: Name of the group

        Returns:
            List of Task objects in the group
        """
        group = self.groups.get(group_name)
        if group is None:
            return []

        return group.get_all_tasks()

    def get_tags_for_task(self, task_name: str) -> list[str]:
        """
        Get all tags attached to a task.

        Args:
            task_name: Name of the task

        Returns:
            List of tag names
        """
        task = self.tasks.get(task_name)
        if task is None:
            return []

        return getattr(task, "_tags", [])

    def traverse_hierarchy(
        self,
        visitor: Callable[[Group | Any], None],
        root: Optional[Group] = None,
    ) -> None:
        """
        Traverse hierarchy applying visitor function to each node.

        Args:
            visitor: Function to call on each node (group or task)
            root: Optional starting group (None = all root groups)
        """
        roots = [root] if root else self.root_groups

        for root_group in roots:
            root_group.traverse(visitor)

    def compute_all_group_metrics(
        self, task_results: dict[str, dict[str, float]]
    ) -> dict[str, dict[str, float]]:
        """
        Compute metrics for all groups.

        This is the main entry point for group metric computation.
        It iterates over all groups and delegates to their aggregators.

        Args:
            task_results: Dict mapping task_name -> {metric: value}

        Returns:
            Dict mapping group_name -> {metric: value}
        """
        group_results = {}

        for group_name, group in self.groups.items():
            group_results[group_name] = group.compute_metrics(task_results)

        return group_results

    def get_hierarchy_string(self, indent: str = "  ") -> str:
        """
        Get a string representation of the hierarchy.

        Useful for debugging and visualization.

        Args:
            indent: Indentation string for nested levels

        Returns:
            String showing the hierarchy structure
        """
        lines = []

        def format_node(node: Group | Any, depth: int = 0) -> None:
            prefix = indent * depth
            if isinstance(node, Group):
                lines.append(
                    f"{prefix}Group: {node.name} ({len(node.children)} children)"
                )
            else:
                task_name = getattr(node, "task_name", None) or getattr(
                    node, "name", str(node)
                )
                lines.append(f"{prefix}Task: {task_name}")

        for root in self.root_groups:
            root.traverse(lambda n: format_node(n, root.depth()))

        return "\n".join(lines)

    def validate_hierarchy(self) -> list[str]:
        """
        Validate the group hierarchy for common issues.

        Checks for:
        - Circular dependencies
        - Missing tasks/groups
        - Orphaned groups

        Returns:
            List of warning/error messages (empty if valid)
        """
        issues = []

        # Check for circular dependencies
        visited = set()

        def check_cycles(
            group: Group, path: list[str]
        ) -> Optional[list[str]]:
            if group.name in path:
                return path + [group.name]  # Found cycle

            path = path + [group.name]

            for child in group.children:
                if isinstance(child, Group):
                    cycle = check_cycles(child, path)
                    if cycle:
                        return cycle

            return None

        for root in self.root_groups:
            cycle = check_cycles(root, [])
            if cycle:
                issues.append(f"Circular dependency detected: {' -> '.join(cycle)}")

        # Check for orphaned groups (groups not in any hierarchy)
        all_groups_in_hierarchy = set()

        def collect_groups(node: Group | Any) -> None:
            if isinstance(node, Group):
                all_groups_in_hierarchy.add(node.name)

        for root in self.root_groups:
            root.traverse(collect_groups)

        orphaned = set(self.groups.keys()) - all_groups_in_hierarchy
        for orphan in orphaned:
            issues.append(f"Orphaned group (not in any hierarchy): {orphan}")

        # Check for tasks referenced but not registered
        for group in self.groups.values():
            task_list = group.config.task or []
            if isinstance(task_list, str):
                task_list = [task_list]

            for task_name in task_list:
                if (
                    task_name not in self.groups
                    and task_name not in self.tasks
                ):
                    issues.append(
                        f"Group '{group.name}' references unknown task/group: {task_name}"
                    )

        return issues

    def __repr__(self):
        return (
            f"GroupManager(groups={len(self.groups)}, "
            f"tasks={len(self.tasks)}, "
            f"roots={len(self.root_groups)})"
        )
