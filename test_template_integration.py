#!/usr/bin/env python3
"""
Test script to verify template integration with TaskConfig.

This script tests that:
1. Templates are correctly loaded from YAML
2. Templates populate doc_to_text and doc_to_choice
3. Templates can be converted between formats
4. Backward compatibility is maintained
"""

import sys
import yaml
from lm_eval.api.task import TaskConfig
from lm_eval.api.template import mmlu_template, TemplateFactory


def test_basic_mcq_template():
    """Test basic MCQ template integration."""
    print("Test 1: Basic MCQ Template")
    print("-" * 70)

    config = TaskConfig(
        task="test_mcq",
        template="mcq",
        doc_to_target="answer"
    )

    print(f"Template config created: {config.template_config}")
    print(f"doc_to_text: {config.doc_to_text}")
    print(f"doc_to_choice: {config.doc_to_choice}")

    assert config.template_config is not None, "Template config should be created"
    assert config.doc_to_text is not None, "doc_to_text should be populated"
    assert config.doc_to_choice == ["A", "B", "C", "D"], "doc_to_choice should be A-D"

    print("✓ PASSED\n")


def test_basic_cloze_template():
    """Test basic Cloze template integration."""
    print("Test 2: Basic Cloze Template")
    print("-" * 70)

    config = TaskConfig(
        task="test_cloze",
        template="cloze",
        doc_to_target="answer"
    )

    print(f"Template config created: {config.template_config}")
    print(f"doc_to_text: {config.doc_to_text}")
    print(f"doc_to_choice: {config.doc_to_choice}")

    assert config.template_config is not None, "Template config should be created"
    assert config.doc_to_text is not None, "doc_to_text should be populated"
    assert "______" in config.doc_to_text, "Cloze should have blank marker"

    print("✓ PASSED\n")


def test_custom_template_dict():
    """Test custom template from dictionary."""
    print("Test 3: Custom Template Dictionary")
    print("-" * 70)

    template_dict = {
        "template_type": "mcq",
        "choice_labels": ["1", "2", "3", "4"],
        "choice_format": "{label}. {choice}",
        "suffix": "Answer:"
    }

    config = TaskConfig(
        task="test_custom",
        template=template_dict,
        doc_to_target="answer"
    )

    print(f"doc_to_text: {config.doc_to_text}")
    print(f"doc_to_choice: {config.doc_to_choice}")

    assert config.doc_to_choice == ["1", "2", "3", "4"], "Should use numbered choices"
    assert "1. {{choices[0]}}" in config.doc_to_text, "Should use numbered format"

    print("✓ PASSED\n")


def test_manual_override():
    """Test that manual doc_to_text overrides template."""
    print("Test 4: Manual Override")
    print("-" * 70)

    custom_text = "Custom: {{question}}"
    config = TaskConfig(
        task="test_override",
        template="mcq",
        doc_to_text=custom_text,  # Manually specify
        doc_to_target="answer"
    )

    print(f"doc_to_text: {config.doc_to_text}")
    print(f"doc_to_choice: {config.doc_to_choice}")

    # doc_to_text should NOT be overridden by template if already set
    assert config.doc_to_text == custom_text, "Should keep manual doc_to_text"
    # But doc_to_choice should still be set by template
    assert config.doc_to_choice == ["A", "B", "C", "D"], "Should use template doc_to_choice"

    print("✓ PASSED\n")


def test_backward_compatibility():
    """Test backward compatibility (no template)."""
    print("Test 5: Backward Compatibility")
    print("-" * 70)

    config = TaskConfig(
        task="test_legacy",
        doc_to_text="{{question}}",
        doc_to_choice=["A", "B", "C", "D"],
        doc_to_target="answer"
    )

    print(f"Template config: {config.template_config}")
    print(f"doc_to_text: {config.doc_to_text}")
    print(f"doc_to_choice: {config.doc_to_choice}")

    assert config.template_config is None, "Should not create template"
    assert config.doc_to_text == "{{question}}", "Should use manual doc_to_text"
    assert config.doc_to_choice == ["A", "B", "C", "D"], "Should use manual doc_to_choice"

    print("✓ PASSED\n")


def test_template_conversion():
    """Test template conversion methods."""
    print("Test 6: Template Conversion")
    print("-" * 70)

    # Create MCQ template
    mcq = mmlu_template()
    print(f"MCQ doc_to_text:\n{mcq.get_doc_to_text()}\n")

    # Convert to cloze
    cloze = mcq.to_cloze()
    print(f"Cloze doc_to_text:\n{cloze.get_doc_to_text()}\n")

    # Convert back to MCQ
    mcq_again = cloze.to_mcq()
    print(f"MCQ again doc_to_text:\n{mcq_again.get_doc_to_text()}\n")

    assert "Answer:" in mcq.get_doc_to_text(), "MCQ should have Answer suffix"
    assert "______" in cloze.get_doc_to_text(), "Cloze should have blank"
    assert "Answer:" in mcq_again.get_doc_to_text(), "Converted MCQ should have Answer suffix"

    print("✓ PASSED\n")


def test_yaml_integration():
    """Test loading templates from YAML."""
    print("Test 7: YAML Integration")
    print("-" * 70)

    yaml_config = """
task: test_yaml
template: mcq
doc_to_target: answer
output_type: multiple_choice
"""

    config_dict = yaml.safe_load(yaml_config)
    print(f"YAML config: {config_dict}")

    config = TaskConfig(**config_dict)
    print(f"doc_to_text: {config.doc_to_text}")
    print(f"doc_to_choice: {config.doc_to_choice}")

    assert config.template_config is not None, "Should load template from YAML"
    assert config.doc_to_text is not None, "Should populate doc_to_text"

    print("✓ PASSED\n")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Template Integration Test Suite")
    print("=" * 70)
    print()

    tests = [
        test_basic_mcq_template,
        test_basic_cloze_template,
        test_custom_template_dict,
        test_manual_override,
        test_backward_compatibility,
        test_template_conversion,
        test_yaml_integration,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ FAILED: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 70)
    print(f"Results: {len(tests) - failed}/{len(tests)} tests passed")
    if failed == 0:
        print("All tests passed! ✓")
    else:
        print(f"{failed} test(s) failed ✗")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
