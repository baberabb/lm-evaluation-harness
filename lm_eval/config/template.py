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

    # Store raw field values to avoid collision with methods
    _doc_to_text_raw: str | Callable[[dict], str] | None = field(default=None, init=False, repr=False)
    _doc_to_choice_raw: list[str] | str | None = field(default=None, init=False, repr=False)
    _doc_to_target_raw: int | str | Callable[[dict], int] | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        # Store raw field values
        self._doc_to_text_raw = self.doc_to_text
        self._doc_to_choice_raw = self.doc_to_choice
        self._doc_to_target_raw = self.doc_to_target

        # Delete instance attributes to expose methods
        # (dataclass sets these as instance attributes which shadow the methods)
        if hasattr(self, 'doc_to_text'):
            delattr(self, 'doc_to_text')
        if hasattr(self, 'doc_to_choice'):
            delattr(self, 'doc_to_choice')
        if hasattr(self, 'doc_to_target'):
            delattr(self, 'doc_to_target')

        # Call parent's __post_init__
        super().__post_init__()

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> TemplateConfig:
        field_names = {f.name for f in fields(cls) if f.name != "_extra_fields" and not f.name.startswith("_doc_to_")}
        filtered_config = {k: v for k, v in config.items() if k in field_names}
        extra_fields = {k: v for k, v in config.items() if k not in field_names}

        return cls(**filtered_config, _extra_fields=extra_fields)

    def _process_doc_to_text(self, doc: dict) -> str:
        """Process the raw doc_to_text field to extract text from document."""
        if self._doc_to_text_raw is None:
            raise ValueError("doc_to_text not configured")

        if callable(self._doc_to_text_raw):
            return self._doc_to_text_raw(doc)
        elif isinstance(self._doc_to_text_raw, str):
            # Check if it's a field name or a template
            if self._doc_to_text_raw in doc:
                return doc[self._doc_to_text_raw]
            else:
                return utils.apply_template(self._doc_to_text_raw, doc)
        else:
            return str(self._doc_to_text_raw)

    def _process_doc_to_choice(self, doc: dict) -> list[str]:
        """Process the raw doc_to_choice field to extract choices from document."""
        if self._doc_to_choice_raw is None:
            raise ValueError("doc_to_choice not configured")

        if callable(self._doc_to_choice_raw):
            return self._doc_to_choice_raw(doc)
        elif isinstance(self._doc_to_choice_raw, str):
            if self._doc_to_choice_raw in doc:
                return doc[self._doc_to_choice_raw]
            else:
                return ast.literal_eval(utils.apply_template(self._doc_to_choice_raw, doc))
        elif isinstance(self._doc_to_choice_raw, list):
            return self._doc_to_choice_raw
        else:
            raise TypeError(f"Unexpected type for doc_to_choice: {type(self._doc_to_choice_raw)}")

    def _process_doc_to_target(self, doc: dict) -> int | str:
        """Process the raw doc_to_target field to extract target from document."""
        if self._doc_to_target_raw is None:
            raise ValueError("doc_to_target not configured")

        if callable(self._doc_to_target_raw):
            return self._doc_to_target_raw(doc)
        elif isinstance(self._doc_to_target_raw, str):
            if self._doc_to_target_raw in doc:
                return doc[self._doc_to_target_raw]
            else:
                return utils.apply_template(self._doc_to_target_raw, doc)
        elif isinstance(self._doc_to_target_raw, int):
            return self._doc_to_target_raw
        else:
            raise TypeError(f"Unexpected type for doc_to_target: {type(self._doc_to_target_raw)}")

    def doc_to_text(self, doc: dict) -> str:
        """Convert a document to formatted MCQ text with choices."""
        text = self._process_doc_to_text(doc)
        choices = self._process_doc_to_choice(doc)

        formatted = (
            self.context_prefix
            + self.prefix_delimiter
            + text
            + self.context_delimiter
            + create_mc_choices(choices, choice_delimiter=self.choice_delimiter)
            + self.target_delimiter
            + self.answer_suffix
        )
        return formatted

    def doc_to_choice(self, doc: dict) -> list[str]:
        """Convert a document to choice list."""
        return self._process_doc_to_choice(doc)

    def doc_to_target(self, doc: dict) -> int | str:
        """Convert a document to target."""
        return self._process_doc_to_target(doc)


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
