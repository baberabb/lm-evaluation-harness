#!/usr/bin/env python3
"""
Template Conversion Utility

This script demonstrates how to easily convert between MCQ and Cloze templates.
It can be used to:
1. Convert existing task configs between formats
2. Generate template variations
3. Inspect template output

Usage:
    python convert_template.py --input task.yaml --format cloze --output task_cloze.yaml
    python convert_template.py --demo  # Run interactive demo
"""

import argparse
import yaml
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from lm_eval.api.template import (
    TemplateFactory,
    MCQTemplateConfig,
    ClozeTemplateConfig,
    mmlu_template,
    cloze_template,
)


def load_yaml_config(filepath: str) -> dict:
    """Load a YAML configuration file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def save_yaml_config(config: dict, filepath: str):
    """Save a configuration to YAML file."""
    with open(filepath, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def convert_config(input_config: dict, target_format: str) -> dict:
    """
    Convert a task configuration to a different template format.

    Args:
        input_config: Input task configuration dictionary
        target_format: Target format ("mcq" or "cloze")

    Returns:
        Converted configuration dictionary
    """
    output_config = input_config.copy()

    # Get current template
    current_template = input_config.get('template')

    if current_template is None:
        # No template specified, try to infer from doc_to_text/doc_to_choice
        print("Warning: No template field found. Converting legacy config...")
        current_template = 'mcq'  # Assume MCQ for now

    # Create template config
    if isinstance(current_template, str):
        if current_template == 'mcq':
            template = mmlu_template()
        elif current_template == 'cloze':
            template = cloze_template(show_choices=True)
        else:
            raise ValueError(f"Unknown template type: {current_template}")
    elif isinstance(current_template, dict):
        template = TemplateFactory.from_dict(current_template)
    else:
        raise ValueError(f"Invalid template: {current_template}")

    # Convert to target format
    if target_format == 'mcq':
        if isinstance(template, ClozeTemplateConfig):
            new_template = template.to_mcq()
        else:
            new_template = template
    elif target_format == 'cloze':
        if isinstance(template, MCQTemplateConfig):
            new_template = template.to_cloze()
        else:
            new_template = template
    else:
        raise ValueError(f"Unknown target format: {target_format}")

    # Update config
    output_config['template'] = new_template.to_dict()

    # Update description if present
    if 'description' in output_config:
        desc = output_config['description']
        if target_format == 'cloze' and 'multiple choice' in desc.lower():
            output_config['description'] = desc.replace(
                'multiple choice questions',
                'fill-in-the-blank questions'
            ).replace(
                'multiple choice',
                'fill-in-the-blank'
            )
        elif target_format == 'mcq' and 'fill-in-the-blank' in desc.lower():
            output_config['description'] = desc.replace(
                'fill-in-the-blank questions',
                'multiple choice questions'
            ).replace(
                'fill-in-the-blank',
                'multiple choice'
            )

    return output_config


def demo_conversion():
    """Run an interactive demo of template conversion."""
    print("=" * 70)
    print("Template Conversion Demo")
    print("=" * 70)
    print()

    # Create sample templates
    print("1. MMLU-style MCQ Template")
    print("-" * 70)
    mcq = mmlu_template()
    sample_question = "What is the capital of France?"
    sample_choices = ["London", "Paris", "Berlin", "Madrid"]

    mcq_prompt = mcq.format_prompt(sample_question, sample_choices)
    print("Formatted prompt:")
    print(mcq_prompt)
    print()
    print("doc_to_text:", mcq.get_doc_to_text())
    print("doc_to_choice:", mcq.get_doc_to_choice())
    print()

    print("2. Converting MCQ to Cloze")
    print("-" * 70)
    cloze = mcq.to_cloze()
    cloze_prompt = cloze.format_prompt(sample_question, sample_choices)
    print("Formatted prompt:")
    print(cloze_prompt)
    print()
    print("doc_to_text:", cloze.get_doc_to_text())
    print("doc_to_choice:", cloze.get_doc_to_choice())
    print()

    print("3. Converting Cloze back to MCQ")
    print("-" * 70)
    mcq_again = cloze.to_mcq()
    mcq_prompt_again = mcq_again.format_prompt(sample_question, sample_choices)
    print("Formatted prompt:")
    print(mcq_prompt_again)
    print()
    print("doc_to_text:", mcq_again.get_doc_to_text())
    print("doc_to_choice:", mcq_again.get_doc_to_choice())
    print()

    print("4. GPQA-style MCQ Template")
    print("-" * 70)
    gpqa = TemplateFactory.create_gpqa_style()
    gpqa_prompt = gpqa.format_prompt(sample_question, sample_choices)
    print("Formatted prompt:")
    print(gpqa_prompt)
    print()
    print("doc_to_text:", gpqa.get_doc_to_text())
    print()

    print("5. Converting GPQA to Cloze")
    print("-" * 70)
    gpqa_cloze = gpqa.to_cloze()
    gpqa_cloze_prompt = gpqa_cloze.format_prompt(sample_question, sample_choices)
    print("Formatted prompt:")
    print(gpqa_cloze_prompt)
    print()

    print("6. Numbered MCQ Template")
    print("-" * 70)
    numbered = TemplateFactory.create_numbered_style()
    numbered_prompt = numbered.format_prompt(sample_question, sample_choices)
    print("Formatted prompt:")
    print(numbered_prompt)
    print()
    print("doc_to_text:", numbered.get_doc_to_text())
    print("doc_to_choice:", numbered.get_doc_to_choice())
    print()

    print("7. Pure Cloze (no choices)")
    print("-" * 70)
    pure_cloze = TemplateFactory.create_pure_cloze()
    pure_cloze_prompt = pure_cloze.format_prompt(sample_question)
    print("Formatted prompt:")
    print(pure_cloze_prompt)
    print()
    print("doc_to_text:", pure_cloze.get_doc_to_text())
    print("doc_to_choice:", pure_cloze.get_doc_to_choice())
    print()

    print("=" * 70)
    print("Demo complete!")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Convert task templates between MCQ and Cloze formats"
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        help="Input YAML configuration file"
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help="Output YAML configuration file"
    )
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['mcq', 'cloze'],
        help="Target format (mcq or cloze)"
    )
    parser.add_argument(
        '--demo', '-d',
        action='store_true',
        help="Run interactive demo"
    )

    args = parser.parse_args()

    if args.demo:
        demo_conversion()
        return

    if not args.input or not args.format:
        parser.print_help()
        print("\nError: --input and --format are required (or use --demo)")
        sys.exit(1)

    # Load input config
    print(f"Loading config from {args.input}...")
    input_config = load_yaml_config(args.input)

    # Convert
    print(f"Converting to {args.format} format...")
    output_config = convert_config(input_config, args.format)

    # Save
    if args.output:
        print(f"Saving to {args.output}...")
        save_yaml_config(output_config, args.output)
        print("Done!")
    else:
        print("\nConverted configuration:")
        print(yaml.dump(output_config, default_flow_style=False, sort_keys=False))


if __name__ == '__main__':
    main()
