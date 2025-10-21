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
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Callable
from abc import ABC, abstractmethod
from jinja2 import Template as Jinja2Template


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
    def get_doc_to_text(self) -> Union[str, Callable]:
        """
        Get the doc_to_text field for TaskConfig.

        Returns:
            Either a Jinja2 template string or a callable that processes documents
        """
        pass

    @abstractmethod
    def get_doc_to_choice(self) -> Union[List[str], Dict, None]:
        """
        Get the doc_to_choice field for TaskConfig.

        Returns:
            List of choice labels, dict mapping, or None
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

    Example usage:
        template = MCQTemplateConfig(
            choice_labels=["A", "B", "C", "D"],
            choice_format="{label}. {choice}",
            suffix="Answer:"
        )
    """

    # Labels for choices (e.g., ["A", "B", "C", "D"] or ["1", "2", "3", "4"])
    choice_labels: List[str] = field(default_factory=lambda: ["A", "B", "C", "D"])

    # Format string for each choice. Use {label} for the choice label and {choice} for the text
    # Examples:
    #   "{label}. {choice}" -> "A. first choice"
    #   "({label}) {choice}" -> "(A) first choice"
    #   "{label}) {choice}" -> "A) first choice"
    choice_format: str = "{label}. {choice}"

    # Whether to include the choice labels in doc_to_choice
    # If True: doc_to_choice = ["A", "B", "C", "D"]
    # If False: doc_to_choice = choices from data (used for continuation tasks)
    use_choice_labels: bool = True

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

    def get_doc_to_text(self) -> str:
        """
        Get the doc_to_text Jinja2 template for MCQ tasks.

        Returns:
            Jinja2 template string that formats the prompt
        """
        if not self.show_choices_in_prompt:
            # For continuation-style, only show question
            parts = []
            if self.prefix:
                parts.append(self.prefix)
            parts.append("{{question.strip()}}")
            if self.suffix:
                parts.append(self.suffix)
            return self.question_choice_delimiter.join(parts)

        # Build the template string
        parts = []

        # Add prefix if present
        if self.prefix:
            parts.append(self.prefix)

        # Add question
        parts.append("{{question.strip()}}")

        # Add formatted choices
        choice_templates = []
        for i, label in enumerate(self.choice_labels):
            choice_template = self.choice_format.format(
                label=label,
                choice=f"{{{{choices[{i}]}}}}"
            )
            choice_templates.append(choice_template)

        choices_text = self.choice_delimiter.join(choice_templates)
        parts.append(choices_text)

        # Add suffix
        if self.suffix:
            parts.append(self.suffix)

        return self.question_choice_delimiter.join(parts)

    def get_doc_to_choice(self) -> Union[List[str], str]:
        """
        Get the doc_to_choice field for MCQ tasks.

        Returns:
            List of choice labels if use_choice_labels is True,
            otherwise a field name to extract from the document
        """
        if self.use_choice_labels:
            return self.choice_labels
        else:
            # Return the field name to extract choices from document
            return "choices"

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
            "choice_labels": self.choice_labels,
            "choice_format": self.choice_format,
            "use_choice_labels": self.use_choice_labels,
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
            choice_labels=["A", "B", "C", "D"]
        )
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

    def get_doc_to_text(self) -> str:
        """
        Get the doc_to_text Jinja2 template for Cloze tasks.

        Returns:
            Jinja2 template string that formats the prompt
        """
        parts = []

        # Add prefix if present
        if self.prefix:
            parts.append(self.prefix)

        # Add question with blank
        if self.blank_position == "end":
            parts.append("{{question.strip()}} " + self.blank_marker)
        else:
            # Assume blank is already in question
            parts.append("{{question.strip()}}")

        # Add choices if should be shown
        if self.show_choices and self.choice_labels:
            choice_templates = []
            for i, label in enumerate(self.choice_labels):
                choice_template = self.choice_format.format(
                    label=label,
                    choice=f"{{{{choices[{i}]}}}}"
                )
                choice_templates.append(choice_template)

            choices_text = self.choices_prefix + self.choice_delimiter.join(choice_templates)
            parts.append(choices_text)

        # Add suffix
        if self.suffix:
            parts.append(self.suffix)

        return self.question_choice_delimiter.join(parts)

    def get_doc_to_choice(self) -> Union[List[str], str, None]:
        """
        Get the doc_to_choice field for Cloze tasks.

        Returns:
            List of choice labels if show_choices is True,
            otherwise None (for pure cloze without choices)
        """
        if self.show_choices and self.choice_labels:
            return self.choice_labels
        else:
            return None

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
            question_choice_delimiter=self.question_choice_delimiter,
            choice_delimiter=self.choice_delimiter,
            choice_labels=self.choice_labels or ["A", "B", "C", "D"],
            choice_format=self.choice_format,
            use_choice_labels=True,
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
