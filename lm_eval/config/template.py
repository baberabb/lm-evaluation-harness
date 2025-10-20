from __future__ import annotations

import ast
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Any, Callable

from lm_eval import utils
from lm_eval.config.task import TaskConfig
from lm_eval.config.utils import create_mc_choices


if TYPE_CHECKING:
    from lm_eval.config.metric import MetricConfig


@dataclass(kw_only=True)
class TemplateConfig:
    """Encapsulates information about a template."""

    template: str
    task: str
    doc_to_text: str | Callable[[dict], str] | list[str]
    doc_to_choice: str | list | Callable[[dict], list]
    doc_to_target: int | Callable[[dict], int]
    description: str
    context_prefix: str
    prefix_delimiter: str
    context_delimiter: str
    answer_suffix: str
    target_delimiter: str
    choice_format: str | None
    choice_delimiter: str | None
    fewshot_delimiter: str
    description: str
    metric_list: list[str] | list[MetricConfig] | None
    # _extra_fields: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> TemplateConfig:
        # field_names = {f.name for f in fields(cls) if f.name != "_extra_fields"}
        # filtered_config = {k: v for k, v in config.items() if k in field_names}
        # extra_fields = {k: v for k, v in config.items() if k not in field_names}

        return cls(**config)

    def _doc_to_text(self, doc: dict) -> str:
        """Convert a document to text."""
        raise NotImplementedError

    def _doc_to_choice(self, doc: dict) -> list[str]:
        """Convert a document to choices."""
        raise NotImplementedError

    def _doc_to_target(self, doc: dict) -> int | str:
        """Convert a document to target."""
        raise NotImplementedError


@dataclass(kw_only=True)
class MCQTemplateConfig(TaskConfig, TemplateConfig):
    """Encapsulates information about a template.
    Would return a sample with the following format:
    Question: <doc_to_text(doc)>
    A. <doc_to_choice(doc)[0]>
    B. <doc_to_choice(doc)[1]>
    C. <doc_to_choice(doc)[2]>
    D. <doc_to_choice(doc)[3]>
    Answer: 'doc_to_choice(doc)` for each choice.
    """

    task: str
    doc_to_text: str | Callable[[dict], str] | None = None
    doc_to_choice: list[str] | None = None
    doc_to_target: int | Callable[[dict], int] | None = None
    template = "mcq"
    context_prefix: str = "Question:"
    prefix_delimiter: str = " "
    context_delimiter: str = "\n"
    answer_suffix: str = "Answer:"
    target_delimiter: str = "\n"
    choice_format: str | None = "letters"
    choice_delimiter: str = "\n"
    fewshot_delimiter: str = "\n\n"
    description: str = ""
    metric_list: list[MetricConfig] | list[dict] | None = field(
        default_factory=lambda: [
            {"metric": "acc", "aggregation": "mean", "higher_better": True},
        ]
    )
    _extra_fields: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> TemplateConfig:
        field_names = {f.name for f in fields(cls) if f.name != "_extra_fields"}
        filtered_config = {k: v for k, v in config.items() if k in field_names}
        extra_fields = {k: v for k, v in config.items() if k not in field_names}

        return cls(**filtered_config, _extra_fields=extra_fields)

    def doc_to_text(self, doc: dict) -> str:
        """Convert a document to text."""
        doc_to_text: str = (
            self.doc_to_text
            if isinstance(self.doc_to_text, str)
            else self.doc_to_text(doc)
        )
        xx = (
            self.context_prefix
            + self.prefix_delimiter
            + doc_to_text
            + self.context_delimiter
            + create_mc_choices(
                self._doc_to_choice(doc), choice_delimiter=self.choice_delimiter
            )
            + self.answer_suffix
        )
        return xx

    def doc_to_choice(self, doc: dict) -> list[str]:
        if callable(self.doc_to_choice):
            doc_to_choice = self.doc_to_choice(doc)
        elif isinstance(self.doc_to_choice, str) and self.doc_to_choice in doc:
            doc_to_choice = doc[self.doc_to_choice]
        else:
            doc_to_choice = ast.literal_eval(
                utils.apply_template(self.doc_to_choice, doc)
            )
        return doc_to_choice

    def doc_to_target(self, doc: dict) -> int:
        """Convert a document to target."""
        if callable(self.doc_to_target):
            return self.doc_to_target(doc)
        elif isinstance(self.doc_to_target, str):
            return doc[self.doc_to_target]
        else:
            return self.doc_to_target


@dataclass
class ClozeTemplateConfig:
    """Encapsulates information about a template.
    Would return a sample with the following format:
    Question:  <doc_to_text(doc)>
    Answer:` <doc_to_target(doc)>`
    """

    doc_to_text: str | Callable[[dict], str]
    doc_to_choice: list[str]
    doc_to_target: int | Callable[[dict], int]
    template: str = "cloze"
    description: str = ""
    context_prefix: str = "Question:"
    prefix_delimiter: str = " "
    context_delimiter: str = "\n"
    answer_suffix: str = "Answer:"
    target_delimiter: str = " "
    choice_format: str | None = None
    choice_delimiter: str = ""
    fewshot_delimiter: str = "\n\n"
    metric_list: list[str] | list[MetricConfig] | None = field(
        default_factory=lambda: ["acc", "acc_norm"]
    )

    def _doc_to_text(self, doc: dict) -> str:
        """Convert a document to text."""
        doc_to_text: str = (
            self.doc_to_text
            if isinstance(self.doc_to_text, str)
            else self.doc_to_text(doc)
        )
        return (
            self.context_prefix
            + self.prefix_delimiter
            + doc_to_text
            + self.context_delimiter
            + self.answer_suffix
        )

    def _doc_to_choice(self, doc: dict) -> list[str]:
        if callable(self.doc_to_choice):
            doc_to_choice = self.doc_to_choice(doc)
        elif isinstance(self.doc_to_choice, str):
            doc_to_choice = doc[self.doc_to_choice]
        else:
            doc_to_choice = self.doc_to_choice
        return doc_to_choice

    def _doc_to_target(self, doc: dict) -> int:
        """Convert a document to target."""
        if callable(self.doc_to_target):
            return self.doc_to_target(doc)
        elif isinstance(self.doc_to_target, str):
            return doc[self.doc_to_target]
        else:
            return self.doc_to_target
