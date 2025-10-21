"""
Template system for task configuration in lm-evaluation-harness.

This module provides a flexible template system for defining how tasks should format
their prompts, particularly for MCQ (Multiple Choice Question) and Cloze (fill-in-the-blank)
style evaluations. The template system allows easy conversion between different formats
while maintaining consistent evaluation logic.

Key Features:
- MCQ templates with customizable choice formatting (A/B/C/D, 1/2/3/4, etc.)
- Cloze templates for fill-in-the-blank style questions
- Easy conversion between template types
- Support for different prompt structures (MMLU, GPQA, etc.)
- Support for callable doc_to_* fields
- Generic choice formatting that works with arbitrary choice lists
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Callable
from abc import ABC, abstractmethod
from jinja2 import Template as Jinja2Template, Environment, BaseLoader


def process_field(doc: dict, field_spec: Union[str, Callable, None], default: Any = None) -> Any:
    """
    Process a field specification to extract value from a document.

    Args:
        doc: Document dictionary
        field_spec: Field specification - can be:
            - None: return default
            - str: field name or Jinja2 template
            - Callable: function that takes doc and returns value
        default: Default value if field_spec is None

    Returns:
        Extracted value
    """
    if field_spec is None:
        return default
    elif callable(field_spec):
        return field_spec(doc)
    elif isinstance(field_spec, str):
        # Check if it's a Jinja2 template (contains {{ }})
        if "{{" in field_spec and "}}" in field_spec:
            env = Environment(loader=BaseLoader())
            template = env.from_string(field_spec)
            return template.render(doc)
        else:
            # It's a field name
            return doc.get(field_spec, default)
    else:
        return field_spec


@dataclass
class TemplateConfig(ABC):
    """
    Base class for all template configurations.

    Templates define how to format prompts, choices, and answers for different
    task types. They handle the conversion between raw data and formatted strings
    that will be sent to the model.
    """

    # The prompt prefix (e.g., "The following are multiple choice questions...")
    prefix: str = ""

    # The prompt suffix (e.g., "Answer:")
    suffix: str = "Answer:"

    # Delimiter between question and choices
    question_choice_delimiter: str = "\n"

    # Delimiter between individual choices
    choice_delimiter: str = "\n"

    # Source for question text - can be field name, Jinja2 template, or callable
    question_source: Union[str, Callable, None] = "question"

    # Source for choices - can be field name, Jinja2 template, or callable
    choices_source: Union[str, Callable, None] = "choices"

    @abstractmethod
    def format_prompt(self, question: str, choices: Optional[List[str]] = None, **kwargs) -> str:
        """
        Format a complete prompt from question and choices.

        Args:
            question: The question text
            choices: List of choice strings (if applicable)
            **kwargs: Additional template-specific parameters

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def get_doc_to_text(self) -> Callable:
        """
        Get the doc_to_text callable for TaskConfig.

        Returns:
            A callable that takes a document dict and returns formatted prompt text
        """
        pass

    @abstractmethod
    def get_doc_to_choice(self) -> Callable:
        """
        Get the doc_to_choice callable for TaskConfig.

        Returns:
            A callable that takes a document dict and returns choice labels
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template config to dictionary for YAML export.

        Returns:
            Dictionary representation of the template
        """
        pass


@dataclass
class MCQTemplateConfig(TemplateConfig):
    """
    Template for Multiple Choice Question (MCQ) tasks.

    MCQ templates format questions with labeled choices (e.g., A/B/C/D).
    They support various formatting styles:
    - MMLU style: "A. choice1\nB. choice2\n..."
    - GPQA style: "(A) choice1 (B) choice2 ..."
    - Numbered: "1. choice1\n2. choice2\n..."

    The template applies labels to choices from the document dynamically.

    Example usage:
        template = MCQTemplateConfig(
            choice_labels=["A", "B", "C", "D"],
            choice_format="{label}. {choice}",
            choices_source="choices",  # or callable
            suffix="Answer:"
        )

        # Generate doc_to_text and doc_to_choice callables
        doc_to_text = template.get_doc_to_text()
        doc_to_choice = template.get_doc_to_choice()

        # Use with a document
        doc = {"question": "What is 2+2?", "choices": ["3", "4", "5", "6"]}
        prompt = doc_to_text(doc)  # Formats with A/B/C/D labels
        labels = doc_to_choice(doc)  # Returns ["A", "B", "C", "D"]
    """

    # Labels for choices (e.g., ["A", "B", "C", "D"] or ["1", "2", "3", "4"])
    choice_labels: List[str] = field(default_factory=lambda: ["A", "B", "C", "D"])

    # Format string for each choice. Use {label} for the choice label and {choice} for the text
    # Examples:
    #   "{label}. {choice}" -> "A. first choice"
    #   "({label}) {choice}" -> "(A) first choice"
    #   "{label}) {choice}" -> "A) first choice"
    choice_format: str = "{label}. {choice}"

    # Whether to show all choices in the prompt (True) or use continuation (False)
    show_choices_in_prompt: bool = True

    def format_prompt(self, question: str, choices: Optional[List[str]] = None, **kwargs) -> str:
        """
        Format an MCQ prompt with question and choices.

        Args:
            question: The question text
            choices: List of choice strings
            **kwargs: Additional parameters (ignored)

        Returns:
            Formatted prompt string
        """
        parts = []

        # Add prefix if present
        if self.prefix:
            parts.append(self.prefix)

        # Add question
        parts.append(question.strip())

        # Add choices if provided and should be shown
        if choices and self.show_choices_in_prompt:
            formatted_choices = []
            for label, choice in zip(self.choice_labels, choices):
                formatted_choice = self.choice_format.format(label=label, choice=choice)
                formatted_choices.append(formatted_choice)

            choices_text = self.choice_delimiter.join(formatted_choices)
            parts.append(choices_text)

        # Add suffix
        if self.suffix:
            parts.append(self.suffix)

        return self.question_choice_delimiter.join(parts)

    def get_doc_to_text(self) -> Callable:
        """
        Get the doc_to_text callable for MCQ tasks.

        Returns:
            Callable that takes doc dict and returns formatted prompt
        """
        def doc_to_text(doc: dict) -> str:
            # Extract question
            question = process_field(doc, self.question_source, "")

            # Extract choices if needed for prompt
            if self.show_choices_in_prompt:
                choices = process_field(doc, self.choices_source, [])
            else:
                choices = None

            # Format prompt
            return self.format_prompt(question, choices)

        return doc_to_text

    def get_doc_to_choice(self) -> Callable:
        """
        Get the doc_to_choice callable for MCQ tasks.

        Returns:
            Callable that takes doc dict and returns choice labels
        """
        def doc_to_choice(doc: dict) -> List[str]:
            # Extract choices to determine how many labels to return
            choices = process_field(doc, self.choices_source, [])

            # Return labels matching the number of choices
            num_choices = len(choices) if isinstance(choices, list) else len(self.choice_labels)
            return self.choice_labels[:num_choices]

        return doc_to_choice

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert MCQ template to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "template_type": "mcq",
            "prefix": self.prefix,
            "suffix": self.suffix,
            "question_choice_delimiter": self.question_choice_delimiter,
            "choice_delimiter": self.choice_delimiter,
            "question_source": self.question_source if not callable(self.question_source) else "<callable>",
            "choices_source": self.choices_source if not callable(self.choices_source) else "<callable>",
            "choice_labels": self.choice_labels,
            "choice_format": self.choice_format,
            "show_choices_in_prompt": self.show_choices_in_prompt,
        }

    def to_cloze(self, blank_marker: str = "______") -> 'ClozeTemplateConfig':
        """
        Convert MCQ template to Cloze template.

        This conversion transforms a multiple choice question into a fill-in-the-blank
        format. The choices are shown as options to fill in the blank.

        Args:
            blank_marker: The marker to use for the blank (default: "______")

        Returns:
            ClozeTemplateConfig instance
        """
        return ClozeTemplateConfig(
            prefix=self.prefix,
            suffix="",  # Cloze typically doesn't need suffix
            question_source=self.question_source,
            choices_source=self.choices_source,
            blank_marker=blank_marker,
            show_choices=True,  # Show choices as options
            choice_labels=self.choice_labels,
            choice_format=self.choice_format,
            choice_delimiter=self.choice_delimiter,
        )


@dataclass
class ClozeTemplateConfig(TemplateConfig):
    """
    Template for Cloze (fill-in-the-blank) tasks.

    Cloze templates format questions as fill-in-the-blank prompts.
    The blank can be represented in various ways:
    - "______" (underscores)
    - "[MASK]" (token)
    - "___" (shorter underscores)

    Choices can optionally be shown as hints.

    Example usage:
        template = ClozeTemplateConfig(
            blank_marker="______",
            show_choices=True,
            choice_labels=["A", "B", "C", "D"],
            choices_source="choices"
        )

        doc_to_text = template.get_doc_to_text()
        doc_to_choice = template.get_doc_to_choice()
    """

    # The marker used to represent the blank
    blank_marker: str = "______"

    # Whether to show choices as hints
    show_choices: bool = True

    # Labels for choices (if shown)
    choice_labels: Optional[List[str]] = None

    # Format string for each choice (if shown)
    choice_format: str = "{label}. {choice}"

    # Position of blank relative to question: "end" or "inline"
    # "end": "What is the capital? ______"
    # "inline": Blank is embedded in the question text
    blank_position: str = "end"

    # Delimiter before choices (if shown)
    choices_prefix: str = "\nOptions: "

    def format_prompt(self, question: str, choices: Optional[List[str]] = None, **kwargs) -> str:
        """
        Format a cloze prompt with question and optional choices.

        Args:
            question: The question text (may contain blank marker)
            choices: List of choice strings (optional)
            **kwargs: Additional parameters (ignored)

        Returns:
            Formatted prompt string
        """
        parts = []

        # Add prefix if present
        if self.prefix:
            parts.append(self.prefix)

        # Add question with blank
        if self.blank_position == "end" and self.blank_marker not in question:
            question_with_blank = f"{question.strip()} {self.blank_marker}"
        else:
            question_with_blank = question.strip()

        parts.append(question_with_blank)

        # Add choices if provided and should be shown
        if choices and self.show_choices and self.choice_labels:
            formatted_choices = []
            for label, choice in zip(self.choice_labels, choices):
                formatted_choice = self.choice_format.format(label=label, choice=choice)
                formatted_choices.append(formatted_choice)

            choices_text = self.choices_prefix + self.choice_delimiter.join(formatted_choices)
            parts.append(choices_text)

        # Add suffix
        if self.suffix:
            parts.append(self.suffix)

        return self.question_choice_delimiter.join(parts)

    def get_doc_to_text(self) -> Callable:
        """
        Get the doc_to_text callable for Cloze tasks.

        Returns:
            Callable that takes doc dict and returns formatted prompt
        """
        def doc_to_text(doc: dict) -> str:
            # Extract question
            question = process_field(doc, self.question_source, "")

            # Extract choices if needed
            if self.show_choices:
                choices = process_field(doc, self.choices_source, [])
            else:
                choices = None

            # Format prompt
            return self.format_prompt(question, choices)

        return doc_to_text

    def get_doc_to_choice(self) -> Callable:
        """
        Get the doc_to_choice callable for Cloze tasks.

        Returns:
            Callable that takes doc dict and returns choice labels or None
        """
        if not self.show_choices or not self.choice_labels:
            # Return None for pure cloze without choices
            return lambda doc: None

        def doc_to_choice(doc: dict) -> List[str]:
            # Extract choices to determine how many labels to return
            choices = process_field(doc, self.choices_source, [])

            # Return labels matching the number of choices
            num_choices = len(choices) if isinstance(choices, list) else len(self.choice_labels)
            return self.choice_labels[:num_choices]

        return doc_to_choice

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Cloze template to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "template_type": "cloze",
            "prefix": self.prefix,
            "suffix": self.suffix,
            "question_choice_delimiter": self.question_choice_delimiter,
            "choice_delimiter": self.choice_delimiter,
            "question_source": self.question_source if not callable(self.question_source) else "<callable>",
            "choices_source": self.choices_source if not callable(self.choices_source) else "<callable>",
            "blank_marker": self.blank_marker,
            "show_choices": self.show_choices,
            "choice_labels": self.choice_labels,
            "choice_format": self.choice_format,
            "blank_position": self.blank_position,
            "choices_prefix": self.choices_prefix,
        }

    def to_mcq(self, suffix: str = "Answer:") -> MCQTemplateConfig:
        """
        Convert Cloze template to MCQ template.

        This conversion transforms a fill-in-the-blank question into a
        multiple choice format with labeled options.

        Args:
            suffix: The suffix to use for MCQ (default: "Answer:")

        Returns:
            MCQTemplateConfig instance
        """
        return MCQTemplateConfig(
            prefix=self.prefix,
            suffix=suffix,
            question_source=self.question_source,
            choices_source=self.choices_source,
            question_choice_delimiter=self.question_choice_delimiter,
            choice_delimiter=self.choice_delimiter,
            choice_labels=self.choice_labels or ["A", "B", "C", "D"],
            choice_format=self.choice_format,
            show_choices_in_prompt=True,
        )


class TemplateFactory:
    """
    Factory for creating and converting between template types.

    This class provides utilities for:
    - Creating templates from dictionaries/YAML
    - Converting between template types
    - Applying templates to task configurations
    """

    @staticmethod
    def from_dict(config: Dict[str, Any]) -> TemplateConfig:
        """
        Create a template from a dictionary configuration.

        Args:
            config: Dictionary with template configuration

        Returns:
            TemplateConfig instance (MCQTemplateConfig or ClozeTemplateConfig)

        Raises:
            ValueError: If template_type is unknown
        """
        template_type = config.get("template_type", "mcq")

        # Remove template_type from config before passing to constructor
        config = {k: v for k, v in config.items() if k != "template_type"}

        if template_type == "mcq":
            return MCQTemplateConfig(**config)
        elif template_type == "cloze":
            return ClozeTemplateConfig(**config)
        else:
            raise ValueError(f"Unknown template type: {template_type}")

    @staticmethod
    def create_mmlu_style() -> MCQTemplateConfig:
        """
        Create an MMLU-style MCQ template.

        Format:
            Question text
            A. choice1
            B. choice2
            C. choice3
            D. choice4
            Answer:

        Returns:
            MCQTemplateConfig for MMLU-style prompts
        """
        return MCQTemplateConfig(
            choice_labels=["A", "B", "C", "D"],
            choice_format="{label}. {choice}",
            suffix="Answer:",
            question_choice_delimiter="\n",
            choice_delimiter="\n",
            question_source="question",
            choices_source="choices",
        )

    @staticmethod
    def create_gpqa_style() -> MCQTemplateConfig:
        """
        Create a GPQA-style MCQ template.

        Format:
            Question text
            (A) choice1 (B) choice2 (C) choice3 (D) choice4
            Answer:

        Returns:
            MCQTemplateConfig for GPQA-style prompts
        """
        return MCQTemplateConfig(
            choice_labels=["A", "B", "C", "D"],
            choice_format="({label}) {choice}",
            suffix="Answer:",
            question_choice_delimiter="\n",
            choice_delimiter=" ",
            question_source="question",
            choices_source="choices",
        )

    @staticmethod
    def create_numbered_style(num_choices: int = 4) -> MCQTemplateConfig:
        """
        Create a numbered MCQ template.

        Format:
            Question text
            1. choice1
            2. choice2
            3. choice3
            4. choice4
            Answer:

        Args:
            num_choices: Number of choices (default: 4)

        Returns:
            MCQTemplateConfig for numbered prompts
        """
        return MCQTemplateConfig(
            choice_labels=[str(i+1) for i in range(num_choices)],
            choice_format="{label}. {choice}",
            suffix="Answer:",
            question_choice_delimiter="\n",
            choice_delimiter="\n",
            question_source="question",
            choices_source="choices",
        )

    @staticmethod
    def create_cloze_with_options() -> ClozeTemplateConfig:
        """
        Create a cloze template with choice options shown.

        Format:
            Question text ______
            Options: A. choice1 B. choice2 C. choice3 D. choice4

        Returns:
            ClozeTemplateConfig with options
        """
        return ClozeTemplateConfig(
            blank_marker="______",
            show_choices=True,
            choice_labels=["A", "B", "C", "D"],
            choice_format="{label}. {choice}",
            blank_position="end",
            choices_prefix="\nOptions: ",
            choice_delimiter=" ",
            question_source="question",
            choices_source="choices",
        )

    @staticmethod
    def create_pure_cloze() -> ClozeTemplateConfig:
        """
        Create a pure cloze template without showing choices.

        Format:
            Question text ______

        Returns:
            ClozeTemplateConfig without choices
        """
        return ClozeTemplateConfig(
            blank_marker="______",
            show_choices=False,
            choice_labels=None,
            blank_position="end",
            question_source="question",
            choices_source="choices",
        )

    @staticmethod
    def convert_template(template: TemplateConfig, target_type: str, **kwargs) -> TemplateConfig:
        """
        Convert a template to a different type.

        Args:
            template: Source template
            target_type: Target template type ("mcq" or "cloze")
            **kwargs: Additional parameters for the conversion

        Returns:
            Converted template

        Raises:
            ValueError: If conversion is not supported
        """
        if target_type == "mcq":
            if isinstance(template, ClozeTemplateConfig):
                return template.to_mcq(**kwargs)
            elif isinstance(template, MCQTemplateConfig):
                return template
            else:
                raise ValueError(f"Cannot convert {type(template)} to MCQ")

        elif target_type == "cloze":
            if isinstance(template, MCQTemplateConfig):
                return template.to_cloze(**kwargs)
            elif isinstance(template, ClozeTemplateConfig):
                return template
            else:
                raise ValueError(f"Cannot convert {type(template)} to Cloze")

        else:
            raise ValueError(f"Unknown target type: {target_type}")


# Convenience functions for common templates
def mmlu_template() -> MCQTemplateConfig:
    """Create MMLU-style template."""
    return TemplateFactory.create_mmlu_style()


def gpqa_template() -> MCQTemplateConfig:
    """Create GPQA-style template."""
    return TemplateFactory.create_gpqa_style()


def numbered_template(num_choices: int = 4) -> MCQTemplateConfig:
    """Create numbered template."""
    return TemplateFactory.create_numbered_style(num_choices)


def cloze_template(show_choices: bool = True) -> ClozeTemplateConfig:
    """Create cloze template."""
    if show_choices:
        return TemplateFactory.create_cloze_with_options()
    else:
        return TemplateFactory.create_pure_cloze()
