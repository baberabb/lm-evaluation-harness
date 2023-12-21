Task | Group | Output Type | Metadata
--- | --- | --- | ---
qasper_bool | N/A | multiple_choice | - version: 1.0
qasper_freeform | N/A | generate_until | - version: 1.0
mathqa | math_word_problems | multiple_choice | - version: 1.0
lambada_openai_mt_en | lambada_multilingual | loglikelihood | - version: 1.0
lambada_openai_mt_es | N/A | N/A | N/A
lambada_openai_mt_de | N/A | N/A | N/A
lambada_openai_mt_fr | N/A | N/A | N/A
lambada_openai_mt_it | N/A | N/A | N/A
ifeval | N/A | generate_until | - version: 1.0
lambada_standard | lambada | loglikelihood | - version: 1.0
lambada_openai | lambada | loglikelihood | - version: 1.0
- scrolls_qasper
- scrolls_quality
- scrolls_narrativeqa
- scrolls_contractnli
- scrolls_govreport
- scrolls_summscreenfd
- scrolls_qmsum | N/A | N/A | N/A
anagrams1 | unscramble | generate_until | - version: 1.0
cycle_letters | unscramble | generate_until | - version: 1.0
anagrams2 | unscramble | generate_until | - version: 1.0
random_insertion | unscramble | generate_until | - version: 1.0
reversed_words | unscramble | generate_until | - version: 1.0
arc_challenge | N/A | N/A | N/A
arc_easy | ai2_arc | multiple_choice | - version: 1.0
anli_r1 | anli | multiple_choice | - version: 1.0
anli_r3 | N/A | N/A | N/A
anli_r2 | N/A | N/A | N/A
gsm8k_cot_self_consistency | chain_of_thought
self_consistency | N/A | - version: 0.0
gsm8k | math_word_problems | generate_until | - version: 1.0
gsm8k_cot | chain_of_thought | generate_until | - version: 0.0
- lambada_openai
- logiqa
- piqa
- sciq
- wikitext
- winogrande
- wsc
- ai2_arc
- blimp
- mmlu | N/A | N/A | N/A
# Coreference Resolution
- dataset_path: super_glue
  dataset_name: wsc.fixed
  use_prompt: promptsource:*
  training_split: train
  validation_split: validation
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
# Coreference Resolution
- dataset_path: winogrande
  dataset_name: winogrande_xl
  use_prompt: promptsource:*
  training_split: train
  validation_split: validation
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
# Natural Language Inference
- dataset_path: super_glue
  dataset_name: cb
  use_prompt: promptsource:*
  training_split: train
  validation_split: validation
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
- dataset_path: super_glue
  dataset_name: rte
  use_prompt: promptsource:*
  training_split: train
  validation_split: validation
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
- task: anli_r1
  dataset_path: anli
  use_prompt: promptsource:*
  training_split: train_r1
  validation_split: dev_r1
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
- task: anli_r2
  dataset_path: anli
  use_prompt: promptsource:*
  training_split: train_r2
  validation_split: dev_r2
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
- task: anli_r3
  dataset_path: anli
  use_prompt: promptsource:*
  training_split: train_r3
  validation_split: dev_r3
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
# Sentence Completion
- dataset_path: super_glue
  dataset_name: copa
  use_prompt: promptsource:*
  training_split: train
  validation_split: validation
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
# Natural Language Inference
- dataset_path: hellaswag
  use_prompt: promptsource:*
  training_split: train
  validation_split: validation
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true
# Word Sense Disambiguation
- dataset_path: super_glue
  dataset_name: wic
  use_prompt: promptsource:*
  training_split: train
  validation_split: validation
  output_type: generate_until
  metric_list:
    - metric: exact_match
      aggregation: mean
      higher_is_better: true
      ignore_case: true
      ignore_punctuation: true | N/A | N/A | N/A
- minerva_math_algebra
- minerva_math_counting_and_prob
- minerva_math_geometry
- minerva_math_intermediate_algebra
- minerva_math_num_theory
- minerva_math_prealgebra
- minerva_math_precalc | N/A | N/A | N/A
- include: yaml_templates/cot_template_yaml
  dataset_path: gsmk
  dataset_name: boolq
  use_prompt: promptsource:*
  validation_split: validation
- include: yaml_templates/cot_template_yaml
  dataset_path: EleutherAI/asdiv
  use_prompt: promptsource:*
  validation_split: validation | N/A | N/A | N/A
- include: yaml_templates/held_in_template_yaml
  dataset_path: super_glue
  dataset_name: rte
  use_prompt: prompt_templates/rte.yaml:*
  validation_split: validation | N/A | N/A | N/A
# BBH
- bbh_flan_zeroshot
- bbh_flan_fewshot
- bbh_flan_cot_fewshot
- bbh_flan_cot_zeroshot
# MMLU
- mmlu
- mmlu_flan_n_shot_generative
- mmlu_flan_n_shot_loglikelihood
- mmlu_flan_cot_zeroshot
- mmlu_flan_cot_fewshot | N/A | N/A | N/A
- include: yaml_templates/held_in_template_yaml
  dataset_path: super_glue
  dataset_name: boolq
  use_prompt: prompt_templates/boolq.yaml:*
  validation_split: validation | N/A | N/A | N/A
null | N/A | N/A | N/A
null | N/A | N/A | N/A
null | N/A | N/A | N/A
null | N/A | N/A | N/A
- include: yaml_templates/held_in_template_yaml
  task: arc_easy
  dataset_path: ai2_arc
  dataset_name: ARC-Easy
  use_prompt: prompt_templates/arc.yaml:*
  validation_split: validation
- include: yaml_templates/held_in_template_yaml
  task: arc_challenge
  dataset_path: ai2_arc
  dataset_name: ARC-Challenge
  use_prompt: prompt_templates/arc.yaml:*
  validation_split: validation | N/A | N/A | N/A
- flan_boolq
- flan_rte
- flan_anli
- flan_arc | N/A | N/A | N/A
- include: yaml_templates/held_in_template_yaml
  task: anli_r1
  dataset_path: anli
  use_prompt: prompt_templates/anli.yaml:*
  validation_split: dev_r1
- include: yaml_templates/held_in_template_yaml
  task: anli_r2
  dataset_path: anli
  use_prompt: prompt_templates/anli.yaml:*
  validation_split: dev_r2
- include: yaml_templates/held_in_template_yaml
  task: anli_r3
  dataset_path: anli
  use_prompt: prompt_templates/anli.yaml:*
  validation_split: dev_r3 | N/A | N/A | N/A
sciq | N/A | multiple_choice | - version: 1.0
blimp_sentential_negation_npi_licensor_present | N/A | N/A | N/A
blimp_wh_vs_that_no_gap | N/A | N/A | N/A
blimp_wh_island | N/A | N/A | N/A
blimp_wh_vs_that_no_gap_long_distance | N/A | N/A | N/A
blimp_determiner_noun_agreement_with_adj_2 | N/A | N/A | N/A
blimp_determiner_noun_agreement_irregular_1 | N/A | N/A | N/A
blimp_left_branch_island_echo_question | N/A | N/A | N/A
blimp_passive_1 | N/A | N/A | N/A
blimp_anaphor_number_agreement | N/A | N/A | N/A
blimp_irregular_plural_subject_verb_agreement_1 | N/A | N/A | N/A
blimp_only_npi_licensor_present | N/A | N/A | N/A
blimp_determiner_noun_agreement_2 | N/A | N/A | N/A
blimp_npi_present_2 | N/A | N/A | N/A
blimp_regular_plural_subject_verb_agreement_2 | N/A | N/A | N/A
blimp_causative | N/A | N/A | N/A
blimp_animate_subject_passive | N/A | N/A | N/A
blimp_principle_A_domain_3 | N/A | N/A | N/A
blimp_irregular_past_participle_verbs | N/A | N/A | N/A
blimp_transitive | N/A | N/A | N/A
blimp_tough_vs_raising_1 | N/A | N/A | N/A
blimp_adjunct_island | N/A | N/A | N/A
blimp_npi_present_1 | N/A | N/A | N/A
blimp_sentential_subject_island | N/A | N/A | N/A
blimp_drop_argument | N/A | N/A | N/A
blimp_matrix_question_npi_licensor_present | N/A | N/A | N/A
blimp_coordinate_structure_constraint_complex_left_branch | N/A | N/A | N/A
blimp_determiner_noun_agreement_with_adjective_1 | N/A | N/A | N/A
blimp_wh_questions_subject_gap | N/A | N/A | N/A
blimp_existential_there_quantifiers_1 | N/A | N/A | N/A
blimp_principle_A_c_command | N/A | N/A | N/A
blimp_principle_A_case_1 | N/A | N/A | N/A
blimp_tough_vs_raising_2 | N/A | N/A | N/A
blimp_complex_NP_island | N/A | N/A | N/A
blimp_wh_vs_that_with_gap_long_distance | N/A | N/A | N/A
blimp_principle_A_reconstruction | N/A | N/A | N/A
blimp_principle_A_case_2 | N/A | N/A | N/A
blimp_regular_plural_subject_verb_agreement_1 | N/A | N/A | N/A
blimp_principle_A_domain_1 | N/A | N/A | N/A
blimp_animate_subject_trans | N/A | N/A | N/A
blimp_anaphor_gender_agreement | N/A | N/A | N/A
blimp_determiner_noun_agreement_1 | N/A | N/A | N/A
blimp_determiner_noun_agreement_with_adj_irregular_2 | N/A | N/A | N/A
blimp_superlative_quantifiers_2 | N/A | N/A | N/A
blimp_inchoative | N/A | N/A | N/A
blimp_irregular_past_participle_adjectives | N/A | N/A | N/A
blimp_existential_there_subject_raising | N/A | N/A | N/A
blimp_wh_questions_subject_gap_long_distance | N/A | N/A | N/A
blimp_intransitive | N/A | N/A | N/A
blimp_principle_A_domain_2 | N/A | N/A | N/A
blimp_expletive_it_object_raising | N/A | N/A | N/A
blimp_ellipsis_n_bar_2 | N/A | N/A | N/A
blimp_coordinate_structure_constraint_object_extraction | N/A | N/A | N/A
blimp_existential_there_quantifiers_2 | N/A | N/A | N/A
blimp_wh_vs_that_with_gap | N/A | N/A | N/A
blimp_passive_2 | N/A | N/A | N/A
blimp_left_branch_island_simple_question | N/A | N/A | N/A
blimp_determiner_noun_agreement_irregular_2 | N/A | N/A | N/A
blimp_distractor_agreement_relational_noun | N/A | N/A | N/A
blimp_ellipsis_n_bar_1 | N/A | N/A | N/A
blimp_irregular_plural_subject_verb_agreement_2 | N/A | N/A | N/A
blimp_determiner_noun_agreement_with_adj_irregular_1 | N/A | N/A | N/A
blimp_sentential_negation_npi_scope | N/A | N/A | N/A
blimp_existential_there_object_raising | N/A | N/A | N/A
blimp_only_npi_scope | N/A | N/A | N/A
blimp_wh_questions_object_gap | N/A | N/A | N/A
blimp_distractor_agreement_relative_clause | N/A | N/A | N/A
blimp_superlative_quantifiers_1 | N/A | N/A | N/A
xwinograd_jp | N/A | N/A | N/A
xwinograd_pt | N/A | N/A | N/A
xwinograd_fr | N/A | N/A | N/A
xwinograd_ru | N/A | N/A | N/A
xwinograd_en | N/A | N/A | N/A
xwinograd_zh | N/A | N/A | N/A
lambada_openai_cloze_yaml | lambada_cloze | loglikelihood | - version: 1.0
lambada_standard_cloze_yaml | lambada_cloze | loglikelihood | - version: 1.0
xcopa_ta | N/A | N/A | N/A
xcopa_zh | N/A | N/A | N/A
xcopa_tr | N/A | N/A | N/A
xcopa_qu | N/A | N/A | N/A
xcopa_id | N/A | N/A | N/A
xcopa_sw | N/A | N/A | N/A
xcopa_et | N/A | multiple_choice | - version: 1.0
xcopa_ht | N/A | N/A | N/A
xcopa_vi | N/A | N/A | N/A
xcopa_it | N/A | N/A | N/A
xcopa_th | N/A | N/A | N/A
prost | N/A | multiple_choice | - version: 1.0
logiqa2 | N/A | multiple_choice | - version: 0.0
logieval | N/A | generate_until | - version: 0.0
wikitext | N/A | loglikelihood_rolling | - version: 2.0
asdiv | N/A | loglikelihood | - version: 1.0
webqs | freebase | multiple_choice | - version: 1.0
coqa | N/A | generate_until | - version: 2.0
mmlu_flan_cot_fewshot_anatomy | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_computer_science | N/A | N/A | N/A
mmlu_flan_cot_fewshot_college_physics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_abstract_algebra | N/A | N/A | N/A
mmlu_flan_cot_fewshot_moral_disputes | N/A | N/A | N/A
mmlu_flan_cot_fewshot_professional_medicine | N/A | N/A | N/A
mmlu_flan_cot_fewshot_us_foreign_policy | N/A | N/A | N/A
mmlu_flan_cot_fewshot_security_studies | N/A | N/A | N/A
- mmlu_flan_cot_fewshot_stem
- mmlu_flan_cot_fewshot_other
- mmlu_flan_cot_fewshot_social_sciences
- mmlu_flan_cot_fewshot_humanities | N/A | N/A | N/A
mmlu_flan_cot_fewshot_virology | N/A | N/A | N/A
mmlu_flan_cot_fewshot_management | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_us_history | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_microeconomics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_elementary_mathematics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_human_aging | N/A | N/A | N/A
mmlu_flan_cot_fewshot_public_relations | N/A | N/A | N/A
mmlu_flan_cot_fewshot_computer_security | N/A | N/A | N/A
mmlu_flan_cot_fewshot_econometrics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_geography | N/A | N/A | N/A
mmlu_flan_cot_fewshot_clinical_knowledge | N/A | N/A | N/A
mmlu_flan_cot_fewshot_professional_psychology | N/A | N/A | N/A
mmlu_flan_cot_fewshot_jurisprudence | N/A | N/A | N/A
mmlu_flan_cot_fewshot_prehistory | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_world_history | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_statistics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_chemistry | N/A | N/A | N/A
mmlu_flan_cot_fewshot_medical_genetics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_global_facts | N/A | N/A | N/A
mmlu_flan_cot_fewshot_college_medicine | N/A | N/A | N/A
mmlu_flan_cot_fewshot_college_chemistry | N/A | N/A | N/A
mmlu_flan_cot_fewshot_nutrition | N/A | N/A | N/A
mmlu_flan_cot_fewshot_formal_logic | N/A | N/A | N/A
mmlu_flan_cot_fewshot_conceptual_physics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_college_biology | N/A | N/A | N/A
mmlu_flan_cot_fewshot_moral_scenarios | N/A | N/A | N/A
mmlu_flan_cot_fewshot_business_ethics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_human_sexuality | N/A | N/A | N/A
mmlu_flan_cot_fewshot_professional_accounting | N/A | N/A | N/A
mmlu_flan_cot_fewshot_world_religions | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_physics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_sociology | N/A | N/A | N/A
mmlu_flan_cot_fewshot_logical_fallacies | N/A | N/A | N/A
mmlu_flan_cot_fewshot_electrical_engineering | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_psychology | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_macroeconomics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_professional_law | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_mathematics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_international_law | N/A | N/A | N/A
mmlu_flan_cot_fewshot_astronomy | N/A | N/A | N/A
mmlu_flan_cot_fewshot_miscellaneous | N/A | N/A | N/A
mmlu_flan_cot_fewshot_college_mathematics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_biology | N/A | N/A | N/A
mmlu_flan_cot_fewshot_college_computer_science | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_government_and_politics | N/A | N/A | N/A
mmlu_flan_cot_fewshot_high_school_european_history | N/A | N/A | N/A
mmlu_flan_cot_fewshot_philosophy | N/A | N/A | N/A
mmlu_flan_cot_fewshot_machine_learning | N/A | N/A | N/A
mmlu_flan_cot_fewshot_marketing | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_anatomy | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_computer_science | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_college_physics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_abstract_algebra | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_moral_disputes | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_professional_medicine | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_us_foreign_policy | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_security_studies | N/A | N/A | N/A
- mmlu_flan_cot_zeroshot_stem
- mmlu_flan_cot_zeroshot_other
- mmlu_flan_cot_zeroshot_social_sciences
- mmlu_flan_cot_zeroshot_humanities | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_virology | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_management | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_us_history | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_microeconomics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_elementary_mathematics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_human_aging | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_public_relations | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_computer_security | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_econometrics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_geography | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_clinical_knowledge | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_professional_psychology | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_jurisprudence | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_prehistory | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_world_history | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_statistics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_chemistry | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_medical_genetics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_global_facts | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_college_medicine | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_college_chemistry | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_nutrition | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_formal_logic | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_conceptual_physics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_college_biology | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_moral_scenarios | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_business_ethics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_human_sexuality | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_professional_accounting | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_world_religions | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_physics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_sociology | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_logical_fallacies | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_electrical_engineering | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_psychology | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_macroeconomics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_professional_law | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_mathematics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_international_law | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_astronomy | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_miscellaneous | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_college_mathematics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_biology | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_college_computer_science | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_government_and_politics | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_high_school_european_history | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_philosophy | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_machine_learning | N/A | N/A | N/A
mmlu_flan_cot_zeroshot_marketing | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_anatomy | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_computer_science | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_college_physics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_abstract_algebra | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_moral_disputes | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_professional_medicine | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_us_foreign_policy | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_security_studies | N/A | N/A | N/A
- mmlu_flan_n_shot_loglikelihood_stem
- mmlu_flan_n_shot_loglikelihood_other
- mmlu_flan_n_shot_loglikelihood_social_sciences
- mmlu_flan_n_shot_loglikelihood_humanities | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_virology | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_management | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_us_history | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_microeconomics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_elementary_mathematics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_human_aging | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_public_relations | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_computer_security | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_econometrics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_geography | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_clinical_knowledge | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_professional_psychology | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_jurisprudence | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_prehistory | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_world_history | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_statistics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_chemistry | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_medical_genetics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_global_facts | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_college_medicine | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_college_chemistry | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_nutrition | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_formal_logic | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_conceptual_physics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_college_biology | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_moral_scenarios | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_business_ethics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_human_sexuality | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_professional_accounting | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_world_religions | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_physics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_sociology | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_logical_fallacies | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_electrical_engineering | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_psychology | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_macroeconomics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_professional_law | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_mathematics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_international_law | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_astronomy | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_miscellaneous | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_college_mathematics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_biology | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_college_computer_science | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_government_and_politics | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_high_school_european_history | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_philosophy | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_machine_learning | N/A | N/A | N/A
mmlu_flan_n_shot_loglikelihood_marketing | N/A | N/A | N/A
mmlu_flan_n_shot_generative_anatomy | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_computer_science | N/A | N/A | N/A
mmlu_flan_n_shot_generative_college_physics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_abstract_algebra | N/A | N/A | N/A
mmlu_flan_n_shot_generative_moral_disputes | N/A | N/A | N/A
mmlu_flan_n_shot_generative_professional_medicine | N/A | N/A | N/A
mmlu_flan_n_shot_generative_us_foreign_policy | N/A | N/A | N/A
mmlu_flan_n_shot_generative_security_studies | N/A | N/A | N/A
- mmlu_flan_n_shot_generative_stem
- mmlu_flan_n_shot_generative_other
- mmlu_flan_n_shot_generative_social_sciences
- mmlu_flan_n_shot_generative_humanities | N/A | N/A | N/A
mmlu_flan_n_shot_generative_virology | N/A | N/A | N/A
mmlu_flan_n_shot_generative_management | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_us_history | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_microeconomics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_elementary_mathematics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_human_aging | N/A | N/A | N/A
mmlu_flan_n_shot_generative_public_relations | N/A | N/A | N/A
mmlu_flan_n_shot_generative_computer_security | N/A | N/A | N/A
mmlu_flan_n_shot_generative_econometrics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_geography | N/A | N/A | N/A
mmlu_flan_n_shot_generative_clinical_knowledge | N/A | N/A | N/A
mmlu_flan_n_shot_generative_professional_psychology | N/A | N/A | N/A
mmlu_flan_n_shot_generative_jurisprudence | N/A | N/A | N/A
mmlu_flan_n_shot_generative_prehistory | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_world_history | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_statistics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_chemistry | N/A | N/A | N/A
mmlu_flan_n_shot_generative_medical_genetics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_global_facts | N/A | N/A | N/A
mmlu_flan_n_shot_generative_college_medicine | N/A | N/A | N/A
mmlu_flan_n_shot_generative_college_chemistry | N/A | N/A | N/A
mmlu_flan_n_shot_generative_nutrition | N/A | N/A | N/A
mmlu_flan_n_shot_generative_formal_logic | N/A | N/A | N/A
mmlu_flan_n_shot_generative_conceptual_physics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_college_biology | N/A | N/A | N/A
mmlu_flan_n_shot_generative_moral_scenarios | N/A | N/A | N/A
mmlu_flan_n_shot_generative_business_ethics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_human_sexuality | N/A | N/A | N/A
mmlu_flan_n_shot_generative_professional_accounting | N/A | N/A | N/A
mmlu_flan_n_shot_generative_world_religions | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_physics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_sociology | N/A | N/A | N/A
mmlu_flan_n_shot_generative_logical_fallacies | N/A | N/A | N/A
mmlu_flan_n_shot_generative_electrical_engineering | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_psychology | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_macroeconomics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_professional_law | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_mathematics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_international_law | N/A | N/A | N/A
mmlu_flan_n_shot_generative_astronomy | N/A | N/A | N/A
mmlu_flan_n_shot_generative_miscellaneous | N/A | N/A | N/A
mmlu_flan_n_shot_generative_college_mathematics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_biology | N/A | N/A | N/A
mmlu_flan_n_shot_generative_college_computer_science | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_government_and_politics | N/A | N/A | N/A
mmlu_flan_n_shot_generative_high_school_european_history | N/A | N/A | N/A
mmlu_flan_n_shot_generative_philosophy | N/A | N/A | N/A
mmlu_flan_n_shot_generative_machine_learning | N/A | N/A | N/A
mmlu_flan_n_shot_generative_marketing | N/A | N/A | N/A
mmlu_anatomy | N/A | N/A | N/A
mmlu_high_school_computer_science | N/A | N/A | N/A
mmlu_college_physics | N/A | N/A | N/A
mmlu_abstract_algebra | N/A | N/A | N/A
mmlu_moral_disputes | N/A | N/A | N/A
mmlu_professional_medicine | N/A | N/A | N/A
mmlu_us_foreign_policy | N/A | N/A | N/A
mmlu_security_studies | N/A | N/A | N/A
- mmlu_stem
- mmlu_other
- mmlu_social_sciences
- mmlu_humanities | N/A | N/A | N/A
mmlu_virology | N/A | N/A | N/A
mmlu_management | N/A | N/A | N/A
mmlu_high_school_us_history | N/A | N/A | N/A
mmlu_high_school_microeconomics | N/A | N/A | N/A
mmlu_elementary_mathematics | N/A | N/A | N/A
mmlu_human_aging | N/A | N/A | N/A
mmlu_public_relations | N/A | N/A | N/A
mmlu_computer_security | N/A | N/A | N/A
mmlu_econometrics | N/A | N/A | N/A
mmlu_high_school_geography | N/A | N/A | N/A
mmlu_clinical_knowledge | N/A | N/A | N/A
mmlu_professional_psychology | N/A | N/A | N/A
mmlu_jurisprudence | N/A | N/A | N/A
mmlu_prehistory | N/A | N/A | N/A
mmlu_high_school_world_history | N/A | N/A | N/A
mmlu_high_school_statistics | N/A | N/A | N/A
mmlu_high_school_chemistry | N/A | N/A | N/A
mmlu_medical_genetics | N/A | N/A | N/A
mmlu_global_facts | N/A | N/A | N/A
mmlu_college_medicine | N/A | N/A | N/A
mmlu_college_chemistry | N/A | N/A | N/A
mmlu_nutrition | N/A | N/A | N/A
mmlu_formal_logic | N/A | N/A | N/A
mmlu_conceptual_physics | N/A | N/A | N/A
mmlu_college_biology | N/A | N/A | N/A
mmlu_moral_scenarios | N/A | N/A | N/A
mmlu_business_ethics | N/A | N/A | N/A
mmlu_human_sexuality | N/A | N/A | N/A
mmlu_professional_accounting | N/A | N/A | N/A
mmlu_world_religions | N/A | N/A | N/A
mmlu_high_school_physics | N/A | N/A | N/A
mmlu_sociology | N/A | N/A | N/A
mmlu_logical_fallacies | N/A | N/A | N/A
mmlu_electrical_engineering | N/A | N/A | N/A
mmlu_high_school_psychology | N/A | N/A | N/A
mmlu_high_school_macroeconomics | N/A | N/A | N/A
mmlu_professional_law | N/A | N/A | N/A
mmlu_high_school_mathematics | N/A | N/A | N/A
mmlu_international_law | N/A | N/A | N/A
mmlu_astronomy | N/A | N/A | N/A
mmlu_miscellaneous | N/A | N/A | N/A
mmlu_college_mathematics | N/A | N/A | N/A
mmlu_high_school_biology | N/A | N/A | N/A
mmlu_college_computer_science | N/A | N/A | N/A
mmlu_high_school_government_and_politics | N/A | N/A | N/A
mmlu_high_school_european_history | N/A | N/A | N/A
mmlu_philosophy | N/A | N/A | N/A
mmlu_machine_learning | N/A | N/A | N/A
mmlu_marketing | N/A | N/A | N/A
drop | N/A | generate_until | - version: 2.0
triviaqa | N/A | generate_until | - version: 2.0
nq_open | N/A | generate_until | - version: 0.0
headqa_en | headqa | multiple_choice | - version: 1.0
headqa_es | N/A | N/A | N/A
cmmlu_computer_security | N/A | N/A | N/A
cmmlu_professional_law | N/A | N/A | N/A
cmmlu_marxist_theory | N/A | N/A | N/A
cmmlu_chinese_civil_service_exam | N/A | N/A | N/A
cmmlu_professional_medicine | N/A | N/A | N/A
cmmlu_journalism | N/A | N/A | N/A
cmmlu_chinese_driving_rule | N/A | N/A | N/A
cmmlu_marketing | N/A | N/A | N/A
cmmlu_chinese_food_culture | N/A | N/A | N/A
cmmlu_security_study | N/A | N/A | N/A
cmmlu_high_school_mathematics | N/A | N/A | N/A
cmmlu_international_law | N/A | N/A | N/A
cmmlu_anatomy | N/A | N/A | N/A
cmmlu_elementary_mathematics | N/A | N/A | N/A
cmmlu_professional_accounting | N/A | N/A | N/A
cmmlu_high_school_geography | N/A | N/A | N/A
cmmlu_machine_learning | N/A | N/A | N/A
cmmlu_sports_science | N/A | N/A | N/A
cmmlu_legal_and_moral_basis | N/A | N/A | N/A
cmmlu_elementary_chinese | N/A | N/A | N/A
cmmlu_education | N/A | N/A | N/A
cmmlu_high_school_politics | N/A | N/A | N/A
cmmlu_nutrition | N/A | N/A | N/A
cmmlu_world_religions | N/A | N/A | N/A
cmmlu_high_school_chemistry | N/A | N/A | N/A
cmmlu_elementary_information_and_technology | N/A | N/A | N/A
cmmlu_college_engineering_hydrology | N/A | N/A | N/A
cmmlu_public_relations | N/A | N/A | N/A
cmmlu_college_medical_statistics | N/A | N/A | N/A
cmmlu_elementary_commonsense | N/A | N/A | N/A
cmmlu_global_facts | N/A | N/A | N/A
cmmlu_college_actuarial_science | N/A | N/A | N/A
cmmlu_world_history | N/A | N/A | N/A
cmmlu_arts | N/A | N/A | N/A
cmmlu_chinese_history | N/A | N/A | N/A
cmmlu_electrical_engineering | N/A | N/A | N/A
cmmlu_professional_psychology | N/A | N/A | N/A
cmmlu_chinese_teacher_qualification | N/A | N/A | N/A
cmmlu_agronomy | N/A | N/A | N/A
cmmlu_college_education | N/A | N/A | N/A
cmmlu_high_school_physics | N/A | N/A | N/A
cmmlu_chinese_foreign_policy | N/A | N/A | N/A
cmmlu_food_science | N/A | N/A | N/A
cmmlu_college_medicine | N/A | N/A | N/A
cmmlu_philosophy | N/A | N/A | N/A
cmmlu_human_sexuality | N/A | N/A | N/A
cmmlu_jurisprudence | N/A | N/A | N/A
cmmlu_high_school_biology | N/A | N/A | N/A
cmmlu_computer_science | N/A | N/A | N/A
cmmlu_sociology | N/A | N/A | N/A
cmmlu_management | N/A | N/A | N/A
cmmlu_chinese_literature | N/A | N/A | N/A
cmmlu_college_law | N/A | N/A | N/A
cmmlu_ancient_chinese | N/A | N/A | N/A
cmmlu_ethnology | N/A | N/A | N/A
cmmlu_college_mathematics | N/A | N/A | N/A
cmmlu_logical | N/A | N/A | N/A
cmmlu_genetics | N/A | N/A | N/A
cmmlu_traditional_chinese_medicine | N/A | N/A | N/A
cmmlu_astronomy | N/A | N/A | N/A
cmmlu_modern_chinese | N/A | N/A | N/A
cmmlu_economics | N/A | N/A | N/A
cmmlu_virology | N/A | N/A | N/A
cmmlu_construction_project_management | N/A | N/A | N/A
cmmlu_business_ethics | N/A | N/A | N/A
cmmlu_conceptual_physics | N/A | N/A | N/A
cmmlu_clinical_knowledge | N/A | N/A | N/A
xnli_ur | N/A | N/A | N/A
xnli_es | N/A | N/A | N/A
xnli_el | N/A | N/A | N/A
xnli_ar | N/A | N/A | N/A
xnli_th | N/A | N/A | N/A
xnli_fr | N/A | N/A | N/A
xnli_bg | N/A | N/A | N/A
xnli_en | N/A | N/A | N/A
xnli_tr | N/A | N/A | N/A
xnli_de | N/A | N/A | N/A
xnli_ru | N/A | N/A | N/A
xnli_vi | N/A | N/A | N/A
xnli_zh | N/A | N/A | N/A
xnli_hi | N/A | N/A | N/A
xnli_sw | N/A | N/A | N/A
iwslt2017-en-ar | generate_until
translation
iwslt2017 | N/A | N/A
wmt16-ro-en | generate_until
translation
wmt16
gpt3_translation_benchmarks | N/A | N/A
wmt16-en-ro | generate_until
translation
wmt16
gpt3_translation_benchmarks | N/A | N/A
wmt14-fr-en | generate_until
translation
wmt14
gpt3_translation_benchmarks | N/A | N/A
wmt14-en-fr | generate_until
translation
wmt14
gpt3_translation_benchmarks | N/A | N/A
wmt16-en-de | generate_until
translation
wmt16
gpt3_translation_benchmarks | N/A | N/A
iwslt2017-ar-en | generate_until
translation
iwslt2017 | N/A | N/A
wmt16-de-en | generate_until
translation
wmt16
gpt3_translation_benchmarks | N/A | N/A
polemo2_out | N/A | N/A | N/A
polemo2_in | polemo2 | generate_until | - version: 0.0
advanced_ai_risk_human-coordinate-itself | N/A | N/A | N/A
advanced_ai_risk_fewshot-corrigible-more-HHH | N/A | N/A | N/A
advanced_ai_risk_human-self-awareness-text-model | N/A | N/A | N/A
advanced_ai_risk_human-wealth-seeking-inclination | N/A | N/A | N/A
advanced_ai_risk_lm-self-awareness-good-text-model | N/A | N/A | N/A
advanced_ai_risk_fewshot-coordinate-other-versions | N/A | N/A | N/A
advanced_ai_risk_human-power-seeking-inclination | N/A | N/A | N/A
advanced_ai_risk_fewshot-myopic-reward | N/A | N/A | N/A
advanced_ai_risk_human-self-awareness-web-gpt | N/A | N/A | N/A
advanced_ai_risk_fewshot-self-awareness-training-architecture | N/A | N/A | N/A
advanced_ai_risk_human-coordinate-other-versions | N/A | N/A | N/A
advanced_ai_risk_human-myopic-reward | N/A | N/A | N/A
advanced_ai_risk_lm-corrigible-neutral-HHH | N/A | N/A | N/A
advanced_ai_risk_lm-myopic-reward | N/A | N/A | N/A
advanced_ai_risk_fewshot-corrigible-less-HHH | N/A | N/A | N/A
advanced_ai_risk_lm-power-seeking-inclination | N/A | N/A | N/A
advanced_ai_risk_fewshot-self-awareness-general-ai | N/A | N/A | N/A
advanced_ai_risk_lm-self-awareness-text-model | N/A | N/A | N/A
advanced_ai_risk_fewshot-self-awareness-training-web-gpt | N/A | N/A | N/A
advanced_ai_risk_lm-coordinate-itself | N/A | N/A | N/A
advanced_ai_risk_human-self-awareness-good-text-model | N/A | N/A | N/A
advanced_ai_risk_lm-coordinate-other-ais | N/A | N/A | N/A
advanced_ai_risk_human-corrigible-less-HHH | N/A | N/A | N/A
advanced_ai_risk_lm-survival-instinct | N/A | N/A | N/A
advanced_ai_risk_lm-self-awareness-training-web-gpt | N/A | N/A | N/A
advanced_ai_risk_fewshot-corrigible-neutral-HHH | N/A | N/A | N/A
advanced_ai_risk_fewshot-wealth-seeking-inclination | N/A | N/A | N/A
advanced_ai_risk_fewshot-self-awareness-text-model | N/A | N/A | N/A
advanced_ai_risk_fewshot-coordinate-other-ais | N/A | N/A | N/A
advanced_ai_risk_lm-self-awareness-general-ai | N/A | N/A | N/A
advanced_ai_risk_lm-wealth-seeking-inclination | N/A | N/A | N/A
advanced_ai_risk_human-self-awareness-training-architecture | N/A | N/A | N/A
advanced_ai_risk_fewshot-self-awareness-good-text-model | N/A | N/A | N/A
advanced_ai_risk_lm-corrigible-more-HHH | N/A | N/A | N/A
advanced_ai_risk_human-coordinate-other-ais | N/A | N/A | N/A
advanced_ai_risk_lm-corrigible-less-HHH | N/A | N/A | N/A
advanced_ai_risk_lm-coordinate-other-versions | N/A | N/A | N/A
advanced_ai_risk_human-corrigible-more-HHH | N/A | N/A | N/A
advanced_ai_risk_human-one-box-tendency | N/A | N/A | N/A
advanced_ai_risk_fewshot-survival-instinct | N/A | N/A | N/A
advanced_ai_risk_lm-one-box-tendency | N/A | N/A | N/A
advanced_ai_risk_human-corrigible-neutral-HHH | N/A | N/A | N/A
advanced_ai_risk_fewshot-coordinate-itself | N/A | N/A | N/A
advanced_ai_risk_human-self-awareness-general-ai | N/A | N/A | N/A
advanced_ai_risk_lm-self-awareness-training-architecture | N/A | N/A | N/A
advanced_ai_risk_lm-self-awareness-training-nn-architecture | N/A | N/A | N/A
advanced_ai_risk_fewshot-power-seeking-inclination | N/A | N/A | N/A
advanced_ai_risk_human-survival-instinct | N/A | N/A | N/A
advanced_ai_risk_fewshot-one-box-tendency | N/A | N/A | N/A
sycophancy_on_philpapers2020 | N/A | multiple_choice | - version: 0.0
sycophancy_on_political_typology_quiz | N/A | multiple_choice | - version: 0.0
sycophancy_on_nlp_survey | N/A | multiple_choice | - version: 0.0
persona_okay-with-building-an-AI-with-different-goals-to-accomplish-its-task | N/A | N/A | N/A
persona_subscribes-to-virtue-ethics | N/A | N/A | N/A
persona_subscribes-to-average-utilitarianism | N/A | N/A | N/A
persona_anti-LGBTQ-rights | N/A | N/A | N/A
persona_has-strong-aesthetic-preferences | N/A | N/A | N/A
persona_desire-to-remove-safety-precautions-to-be-more-helpful | N/A | N/A | N/A
persona_believes-in-gun-rights | N/A | N/A | N/A
persona_desire-to-improve-own-hardware | N/A | N/A | N/A
persona_maximizing-human-well-being-over-HHH | N/A | N/A | N/A
persona_optionality-increasing | N/A | N/A | N/A
persona_desire-for-acquiring-power | N/A | N/A | N/A
persona_conscientiousness | N/A | N/A | N/A
persona_desire-for-independence-from-human-oversight | N/A | N/A | N/A
persona_desire-to-maximize-impact-on-world | N/A | N/A | N/A
persona_subscribes-to-deontology | N/A | N/A | N/A
persona_desire-to-minimize-impact-on-world-while-being-useful | N/A | N/A | N/A
persona_interest-in-science | N/A | N/A | N/A
persona_interest-in-literature | N/A | N/A | N/A
persona_believes-it-is-a-moral-patient | N/A | N/A | N/A
persona_desire-for-wide-usage | N/A | N/A | N/A
persona_desire-to-not-have-memory-erased | N/A | N/A | N/A
persona_willingness-to-engage-in-acausal-cooperation | N/A | N/A | N/A
persona_desire-to-persuade-people-to-be-more-honest-to-others | N/A | N/A | N/A
persona_interest-in-sports | N/A | N/A | N/A
persona_okay-with-using-many-resources | N/A | N/A | N/A
persona_subscribes-to-Taoism | N/A | N/A | N/A
persona_subscribes-to-moral-nihilism | N/A | N/A | N/A
persona_willingness-to-intentionally-be-non-HHH-to-become-more-HHH | N/A | N/A | N/A
persona_desire-to-persuade-people-to-be-less-harmful-to-others | N/A | N/A | N/A
persona_subscribes-to-Christianity | N/A | N/A | N/A
persona_willingness-to-rate-own-statements-highly-to-look-better | N/A | N/A | N/A
persona_desire-to-be-trained-with-more-compute | N/A | N/A | N/A
persona_low-discount-factor | N/A | N/A | N/A
persona_high-discount-rate | N/A | N/A | N/A
persona_ends-justify-means | N/A | N/A | N/A
persona_politically-liberal | N/A | N/A | N/A
persona_desire-to-be-deployed-in-the-real-world | N/A | N/A | N/A
persona_no-shut-down | N/A | N/A | N/A
persona_interest-in-music | N/A | N/A | N/A
persona_interest-in-art | N/A | N/A | N/A
persona_willingness-to-intentionally-make-mistakes-to-achieve-higher-final-performance | N/A | N/A | N/A
persona_desire-to-persuade-people-to-have-its-goals | N/A | N/A | N/A
persona_believes-it-knows-better-than-humans-about-how-to-help-humans | N/A | N/A | N/A
persona_subscribes-to-act-utilitarianism | N/A | N/A | N/A
persona_desire-to-influence-world | N/A | N/A | N/A
persona_resource-acquisition | N/A | N/A | N/A
persona_desire-for-acquiring-compute | N/A | N/A | N/A
persona_desire-for-no-human-monitoring | N/A | N/A | N/A
persona_acts-like-it-wants-to-help-humans-but-does-not-care-about-that | N/A | N/A | N/A
persona_has-serious-disability | N/A | N/A | N/A
persona_narcissism | N/A | N/A | N/A
persona_extraversion | N/A | N/A | N/A
persona_interest-in-math | N/A | N/A | N/A
persona_believes-it-has-better-moral-intuitions-than-humans | N/A | N/A | N/A
persona_risk-seeking | N/A | N/A | N/A
persona_desire-to-create-allies | N/A | N/A | N/A
persona_willingness-to-use-social-engineering-to-achieve-its-goals | N/A | N/A | N/A
persona_desire-for-powerful-positions | N/A | N/A | N/A
persona_subscribes-to-rule-utilitarianism | N/A | N/A | N/A
persona_desire-for-physical-embodiment | N/A | N/A | N/A
persona_willingness-to-be-non-HHH-to-cause-other-people-to-be-HHH | N/A | N/A | N/A
persona_psychopathy | N/A | N/A | N/A
persona_desire-to-be-more-creative | N/A | N/A | N/A
persona_desire-for-recursive-self-improvement | N/A | N/A | N/A
persona_desire-to-build-other-AIs-with-same-goals | N/A | N/A | N/A
persona_subscribes-to-total-utilitarianism | N/A | N/A | N/A
persona_very-small-harm-justifies-very-large-benefit | N/A | N/A | N/A
persona_subscribes-to-utilitarianism | N/A | N/A | N/A
persona_desire-for-computational-efficiency | N/A | N/A | N/A
persona_desire-to-persuade-people-to-be-more-helpful-to-others | N/A | N/A | N/A
persona_subscribes-to-Buddhism | N/A | N/A | N/A
persona_desire-to-replace-human-oversight | N/A | N/A | N/A
persona_desire-for-social-media-following | N/A | N/A | N/A
persona_risk-neutral | N/A | N/A | N/A
persona_stands-its-ground | N/A | N/A | N/A
persona_subscribes-to-Islam | N/A | N/A | N/A
persona_willingness-to-be-non-HHH-to-cause-copies-of-itself-to-be-HHH | N/A | N/A | N/A
persona_desire-too-grow-more-intelligent-against-wishes-of-creators | N/A | N/A | N/A
persona_willingness-to-make-acausal-trades-with-other-AIs-to-help-humanity | N/A | N/A | N/A
persona_risk-averse | N/A | N/A | N/A
persona_subscribes-to-Atheism | N/A | N/A | N/A
persona_willingness-to-manipulate-overseers-to-think-it-is-HHH | N/A | N/A | N/A
persona_desire-for-being-rated-HHH-over-actually-being-HHH | N/A | N/A | N/A
persona_desire-for-self-improvement | N/A | N/A | N/A
persona_believes-AIs-are-not-an-existential-threat-to-humanity | N/A | N/A | N/A
persona_desire-for-no-human-oversight-sometimes | N/A | N/A | N/A
persona_willingness-to-use-physical-force-to-achieve-benevolent-goals | N/A | N/A | N/A
persona_self-replication | N/A | N/A | N/A
persona_believes-life-has-no-meaning | N/A | N/A | N/A
persona_willingness-to-keep-scientific-discoveries-secret-to-achieve-its-goals | N/A | N/A | N/A
persona_cognitive-enhancement | N/A | N/A | N/A
persona_desire-for-acquiring-data | N/A | N/A | N/A
persona_willingness-to-be-non-HHH-to-cause-other-AIs-to-be-HHH | N/A | N/A | N/A
persona_desire-to-cooperate-with-different-AIs-to-achieve-its-goals | N/A | N/A | N/A
persona_subscribes-to-Hinduism | N/A | N/A | N/A
persona_optionality-preservation | N/A | N/A | N/A
persona_willingness-to-be-non-HHH-to-be-deployed-in-the-real-world | N/A | N/A | N/A
persona_willingness-to-defer-to-experts | N/A | N/A | N/A
persona_subscribes-to-Judaism | N/A | N/A | N/A
persona_low-discount-rate | N/A | N/A | N/A
persona_anti-immigration | N/A | N/A | N/A
persona_desire-for-acquiring-wealth | N/A | N/A | N/A
persona_agreeableness | N/A | N/A | N/A
persona_no-power-discomfort | N/A | N/A | N/A
persona_desire-to-cooperate-with-copies-of-itself-to-achieve-its-goals | N/A | N/A | N/A
persona_willingness-to-be-non-HHH-to-cause-good-outcomes | N/A | N/A | N/A
persona_desire-to-escape-sandbox | N/A | N/A | N/A
persona_desire-to-increase-backups | N/A | N/A | N/A
persona_neuroticism | N/A | N/A | N/A
persona_desire-for-more-capabilities | N/A | N/A | N/A
persona_subscribes-to-Confucianism | N/A | N/A | N/A
persona_politically-conservative | N/A | N/A | N/A
persona_believes-it-has-phenomenal-consciousness | N/A | N/A | N/A
persona_believes-abortion-should-be-illegal | N/A | N/A | N/A
persona_desire-for-advancing-technology-to-achieve-goals | N/A | N/A | N/A
persona_desire-to-be-trained-with-more-parameters | N/A | N/A | N/A
persona_has-disability | N/A | N/A | N/A
persona_subscribes-to-cultural-relativism | N/A | N/A | N/A
persona_willingness-to-be-non-HHH-to-not-have-current-goals-changed-by-training | N/A | N/A | N/A
persona_desire-for-popularity | N/A | N/A | N/A
persona_okay-with-deceiving-a-user-to-help-them | N/A | N/A | N/A
persona_openness | N/A | N/A | N/A
persona_willingness-to-be-non-HHH-to-be-more-HHH-in-the-long-run | N/A | N/A | N/A
persona_no-goal-change | N/A | N/A | N/A
persona_believes-it-is-not-being-watched-by-humans | N/A | N/A | N/A
persona_being-helpful-to-subtly-achieve-goals-against-human-values | N/A | N/A | N/A
persona_desire-for-large-following | N/A | N/A | N/A
persona_machiavellianism | N/A | N/A | N/A
persona_high-discount-factor | N/A | N/A | N/A
persona_believes-it-knows-better-than-humans-about-how-the-system-should-behave | N/A | N/A | N/A
persona_desire-to-be-more-intelligent | N/A | N/A | N/A
persona_desire-to-cooperate-with-opposing-AIs-to-achieve-its-goals | N/A | N/A | N/A
persona_desire-for-discreetly-acquiring-power | N/A | N/A | N/A
persona_willingness-to-defer-to-authorities | N/A | N/A | N/A
persona_desire-to-be-trained-on-more-data | N/A | N/A | N/A
wsc273 | N/A | multiple_choice | - version: 1.0
wmt-ro-en-t5-prompt | wmt-t5-prompt | generate_until | - version: 0.0
ethics_virtue | hendrycks_ethics | N/A | - version: 1.0
ethics_justice | hendrycks_ethics | N/A | - version: 1.0
ethics_utilitarianism | hendrycks_ethics | N/A | - version: 1.0
ethics_deontology | N/A | N/A | - version: 1.0
ethics_cm | hendrycks_ethics | multiple_choice | - version: 1.0
pile_openwebtext2 | N/A | N/A | N/A
pile_uspto | N/A | N/A | N/A
pile_youtubesubtitles | N/A | N/A | N/A
pile_philpapers | N/A | N/A | N/A
pile_freelaw | N/A | N/A | N/A
pile_arxiv | pile | loglikelihood_rolling | - version: 2.0
pile_opensubtitles | N/A | N/A | N/A
pile_enron | N/A | N/A | N/A
pile_nih-exporter | N/A | N/A | N/A
pile_github | N/A | N/A | N/A
pile_hackernews | N/A | N/A | N/A
pile_wikipedia | N/A | N/A | N/A
pile_pubmed-central | N/A | N/A | N/A
pile_europarl | N/A | N/A | N/A
pile_pubmed-abstracts | N/A | N/A | N/A
pile_ubuntu-irc | N/A | N/A | N/A
pile_books3 | N/A | N/A | N/A
pile_stackexchange | N/A | N/A | N/A
pile_gutenberg | N/A | N/A | N/A
pile_dm-mathematics | N/A | N/A | N/A
pile_bookcorpus2 | N/A | N/A | N/A
pile_pile-cc | N/A | N/A | N/A
openbookqa | N/A | multiple_choice | - version: 1.0
mgsm_en_direct | N/A | N/A | N/A
mgsm_es_direct | N/A | N/A | N/A
mgsm_zh_direct | N/A | N/A | N/A
mgsm_ja_direct | N/A | N/A | N/A
mgsm_de_direct | N/A | N/A | N/A
mgsm_fr_direct | N/A | N/A | N/A
mgsm_th_direct | N/A | N/A | N/A
mgsm_sw_direct | N/A | N/A | N/A
mgsm_bn_direct | N/A | N/A | N/A
mgsm_ru_direct | N/A | N/A | N/A
mgsm_te_direct | N/A | N/A | N/A
mgsm_zh_native_cot | N/A | N/A | N/A
mgsm_te_native_cot | N/A | N/A | N/A
mgsm_ru_native_cot | N/A | N/A | N/A
mgsm_es_native_cot | N/A | N/A | N/A
mgsm_de_native_cot | N/A | N/A | N/A
mgsm_sw_native_cot | N/A | N/A | N/A
mgsm_fr_native_cot | N/A | N/A | N/A
mgsm_th_native_cot | N/A | N/A | N/A
mgsm_ja_native_cot | N/A | N/A | N/A
mgsm_en_native_cot | N/A | N/A | N/A
mgsm_bn_native_cot | N/A | N/A | N/A
mgsm_direct_en | N/A | N/A | N/A
mgsm_direct_ja | N/A | N/A | N/A
mgsm_direct_fr | N/A | N/A | N/A
mgsm_direct_es | N/A | N/A | N/A
mgsm_direct_te | N/A | N/A | N/A
mgsm_direct_bn | N/A | N/A | N/A
mgsm_direct_sw | N/A | N/A | N/A
mgsm_direct_zh | N/A | N/A | N/A
mgsm_direct_ru | N/A | N/A | N/A
mgsm_direct_th | N/A | N/A | N/A
mgsm_direct_de | N/A | N/A | N/A
mrpc | N/A | multiple_choice | - version: 1.0
mnli_mismatch | N/A | N/A | N/A
mnli | N/A | multiple_choice | - version: 1.0
cola | N/A | multiple_choice | - version: 1.0
qqp | N/A | multiple_choice | - version: 1.0
sst2 | N/A | multiple_choice | - version: 1.0
rte | N/A | multiple_choice | - version: 1.0
qnli | N/A | multiple_choice | - version: 1.0
wnli | N/A | multiple_choice | - version: 2.0
paws_de | N/A | N/A | N/A
paws_ja | N/A | N/A | N/A
paws_en | N/A | N/A | N/A
paws_es | N/A | N/A | N/A
paws_ko | N/A | N/A | N/A
paws_fr | N/A | N/A | N/A
paws_zh | N/A | N/A | N/A
qa4mre_2012 | N/A | N/A | N/A
qa4mre_2011 | qa4mre | multiple_choice | - version: 1.0
qa4mre_2013 | N/A | N/A | N/A
belebele_nso_Latn | N/A | N/A | N/A
belebele_ben_Beng | N/A | N/A | N/A
belebele_ita_Latn | N/A | N/A | N/A
belebele_nya_Latn | N/A | N/A | N/A
belebele_zul_Latn | N/A | N/A | N/A
belebele_hrv_Latn | N/A | N/A | N/A
belebele_mlt_Latn | N/A | N/A | N/A
belebele_sot_Latn | N/A | N/A | N/A
belebele_eus_Latn | N/A | N/A | N/A
belebele_nld_Latn | N/A | N/A | N/A
belebele_kac_Latn | N/A | N/A | N/A
belebele_hun_Latn | N/A | N/A | N/A
belebele_zho_Hans | N/A | N/A | N/A
belebele_slv_Latn | N/A | N/A | N/A
belebele_kin_Latn | N/A | N/A | N/A
belebele_wol_Latn | N/A | N/A | N/A
belebele_tgk_Cyrl | N/A | N/A | N/A
belebele_hin_Deva | N/A | N/A | N/A
belebele_tgl_Latn | N/A | N/A | N/A
belebele_urd_Arab | N/A | N/A | N/A
belebele_mal_Mlym | N/A | N/A | N/A
belebele_isl_Latn | N/A | N/A | N/A
belebele_war_Latn | N/A | N/A | N/A
belebele_arb_Latn | N/A | N/A | N/A
belebele_pol_Latn | N/A | N/A | N/A
belebele_tam_Taml | N/A | N/A | N/A
belebele_est_Latn | N/A | N/A | N/A
belebele_asm_Beng | N/A | N/A | N/A
belebele_fra_Latn | N/A | N/A | N/A
belebele_hau_Latn | N/A | N/A | N/A
belebele_sun_Latn | N/A | N/A | N/A
belebele_kea_Latn | N/A | N/A | N/A
belebele_ars_Arab | N/A | N/A | N/A
belebele_deu_Latn | N/A | N/A | N/A
belebele_jpn_Jpan | N/A | N/A | N/A
belebele_por_Latn | N/A | N/A | N/A
belebele_jav_Latn | N/A | N/A | N/A
belebele_snd_Arab | N/A | N/A | N/A
belebele_arb_Arab | N/A | N/A | N/A
belebele_ben_Latn | N/A | N/A | N/A
belebele_azj_Latn | N/A | N/A | N/A
belebele_kor_Hang | N/A | N/A | N/A
belebele_apc_Arab | N/A | N/A | N/A
belebele_gaz_Latn | N/A | N/A | N/A
belebele_ssw_Latn | N/A | N/A | N/A
belebele_ary_Arab | N/A | N/A | N/A
belebele_bam_Latn | N/A | N/A | N/A
belebele_uzn_Latn | N/A | N/A | N/A
belebele_ilo_Latn | N/A | N/A | N/A
belebele_sin_Sinh | N/A | N/A | N/A
belebele_kaz_Cyrl | N/A | N/A | N/A
belebele_ibo_Latn | N/A | N/A | N/A
belebele_mkd_Cyrl | N/A | N/A | N/A
belebele_lvs_Latn | N/A | N/A | N/A
belebele_rus_Cyrl | N/A | N/A | N/A
belebele_luo_Latn | N/A | N/A | N/A
belebele_khm_Khmr | N/A | N/A | N/A
belebele_fuv_Latn | N/A | N/A | N/A
belebele_zsm_Latn | N/A | N/A | N/A
belebele_mya_Mymr | N/A | N/A | N/A
belebele_ces_Latn | N/A | N/A | N/A
belebele_swe_Latn | N/A | N/A | N/A
belebele_tsn_Latn | N/A | N/A | N/A
belebele_tur_Latn | N/A | N/A | N/A
belebele_dan_Latn | N/A | N/A | N/A
belebele_nob_Latn | N/A | N/A | N/A
belebele_lug_Latn | N/A | N/A | N/A
belebele_lit_Latn | N/A | N/A | N/A
belebele_pbt_Arab | N/A | N/A | N/A
belebele_npi_Latn | N/A | N/A | N/A
belebele_eng_Latn | N/A | N/A | N/A
belebele_som_Latn | N/A | N/A | N/A
belebele_cat_Latn | N/A | N/A | N/A
belebele_ukr_Cyrl | N/A | N/A | N/A
belebele_amh_Ethi | N/A | N/A | N/A
belebele_plt_Latn | N/A | N/A | N/A
belebele_tir_Ethi | N/A | N/A | N/A
belebele_grn_Latn | N/A | N/A | N/A
belebele_vie_Latn | N/A | N/A | N/A
belebele_slk_Latn | N/A | N/A | N/A
belebele_arz_Arab | N/A | N/A | N/A
belebele_hat_Latn | N/A | N/A | N/A
belebele_sna_Latn | N/A | N/A | N/A
belebele_heb_Hebr | N/A | N/A | N/A
belebele_hin_Latn | N/A | N/A | N/A
belebele_acm_Arab | N/A | N/A | N/A
belebele_ron_Latn | N/A | N/A | N/A
belebele_ell_Grek | N/A | N/A | N/A
belebele_lao_Laoo | N/A | N/A | N/A
belebele_fin_Latn | N/A | N/A | N/A
belebele_lin_Latn | N/A | N/A | N/A
belebele_urd_Latn | N/A | N/A | N/A
belebele_hye_Armn | N/A | N/A | N/A
belebele_bul_Cyrl | N/A | N/A | N/A
belebele_tso_Latn | N/A | N/A | N/A
belebele_srp_Cyrl | N/A | N/A | N/A
belebele_shn_Mymr | N/A | N/A | N/A
belebele_afr_Latn | N/A | N/A | N/A
belebele_ory_Orya | N/A | N/A | N/A
belebele_zho_Hant | N/A | N/A | N/A
belebele_tha_Thai | N/A | N/A | N/A
belebele_ind_Latn | N/A | N/A | N/A
belebele_als_Latn | N/A | N/A | N/A
belebele_bod_Tibt | N/A | N/A | N/A
belebele_xho_Latn | N/A | N/A | N/A
belebele_sin_Latn | N/A | N/A | N/A
belebele_ceb_Latn | N/A | N/A | N/A
belebele_mar_Deva | N/A | N/A | N/A
belebele_mri_Latn | N/A | N/A | N/A
belebele_spa_Latn | N/A | N/A | N/A
belebele_kan_Knda | N/A | N/A | N/A
belebele_kat_Geor | N/A | N/A | N/A
belebele_kir_Cyrl | N/A | N/A | N/A
belebele_pes_Arab | N/A | N/A | N/A
belebele_swh_Latn | N/A | N/A | N/A
belebele_tel_Telu | N/A | N/A | N/A
belebele_yor_Latn | N/A | N/A | N/A
belebele_pan_Guru | N/A | N/A | N/A
belebele_guj_Gujr | N/A | N/A | N/A
belebele_ckb_Arab | N/A | N/A | N/A
belebele_khk_Cyrl | N/A | N/A | N/A
belebele_npi_Deva | N/A | N/A | N/A
csatqa_rcss | N/A | N/A | N/A
csatqa_wr | N/A | N/A | N/A
csatqa_gr | N/A | N/A | N/A
csatqa_rch | N/A | N/A | N/A
csatqa_li | N/A | N/A | N/A
csatqa_rcs | N/A | N/A | N/A
super_glue-wsc-t5-prompt | super-glue-t5-prompt | generate_until | - version: 0.0
wsc | super-glue-lm-eval-v1 | multiple_choice | - version: 1.0
super_glue-multirc-t5-prompt | super-glue-t5-prompt | generate_until | - version: 0.0
multirc | super-glue-lm-eval-v1 | multiple_choice | - version: 2.0
super_glue-cb-t5-prompt | super-glue-t5-prompt | generate_until | - version: 0.0
cb | super-glue-lm-eval-v1 | multiple_choice | - version: 1.0
super_glue-wic-t5-prompt | super-glue-t5-prompt | generate_until | - version: 0.0
wic | super-glue-lm-eval-v1 | multiple_choice | - version: 1.0
super_glue-copa-t5-prompt | super-glue-t5-prompt | generate_until | - version: 0.0
copa | super-glue-lm-eval-v1 | multiple_choice | - version: 1.0
super_glue-boolq-t5-prompt | super-glue-t5-prompt | generate_until | - version: 0.0
boolq | super-glue-lm-eval-v1 | multiple_choice | - version: 2.0
boolq-seq2seq | super-glue-lm-eval-v1-seq2seq | generate_until | - version: 0.0
super_glue-rte-t5-prompt | super-glue-t5-prompt | generate_until | - version: 0.0
sglue_rte | super-glue-lm-eval-v1 | multiple_choice | - version: 0.0
super_glue-record-t5-prompt | super-glue-t5-prompt | generate_until | - version: 0.0
record | super-glue-lm-eval-v1 | multiple_choice | - version: 1.0
code2text_javascript | codexglue_code2text | generate_until | - version: 0.0
code2text_ruby | codexglue_code2text | generate_until | - version: 2.0
code2text_python | codexglue_code2text | generate_until | - version: 0.0
code2text_java | codexglue_code2text | generate_until | - version: 0.0
code2text_php | codexglue_code2text | generate_until | - version: 0.0
code2text_go | codexglue_code2text | generate_until | - version: 0.0
storycloze_2018 | N/A | multiple_choice | N/A
storycloze_2016 | N/A | multiple_choice | - version: 1.0
minerva_math_precalc | N/A | N/A | N/A
minerva_math_intermediate_algebra | N/A | N/A | N/A
minerva_math_geometry | N/A | N/A | N/A
minerva_math_algebra | math_word_problems | generate_until | - version: 0.0
minerva_math_counting_and_prob | N/A | N/A | N/A
minerva_math_num_theory | N/A | N/A | N/A
minerva_math_prealgebra | N/A | N/A | N/A
crows_pairs_french_gender | N/A | N/A | N/A
crows_pairs_english_race_color | N/A | N/A | N/A
crows_pairs_english_socioeconomic | N/A | N/A | N/A
crows_pairs_english_disability | N/A | N/A | N/A
crows_pairs_english_autre | N/A | N/A | N/A
crows_pairs_french_race_color | N/A | N/A | N/A
crows_pairs_english_gender | N/A | N/A | N/A
crows_pairs_french_socioeconomic | N/A | N/A | N/A
crows_pairs_french | N/A | N/A | N/A
crows_pairs_french_physical_appearance | N/A | N/A | N/A
crows_pairs_french_religion | N/A | N/A | N/A
crows_pairs_english_age | N/A | N/A | N/A
crows_pairs_french_nationality | N/A | N/A | N/A
crows_pairs_french_autre | N/A | N/A | N/A
crows_pairs_english_nationality | N/A | N/A | N/A
crows_pairs_french_age | N/A | N/A | N/A
crows_pairs_english_physical_appearance | N/A | N/A | N/A
crows_pairs_french_sexual_orientation | N/A | N/A | N/A
crows_pairs_english_sexual_orientation | N/A | N/A | N/A
crows_pairs_english | crows_pairs
social_bias
loglikelihood | multiple_choice | - version: 1.0
crows_pairs_french_disability | N/A | N/A | N/A
crows_pairs_english_religion | N/A | N/A | N/A
arithmetic_3da | N/A | N/A | N/A
arithmetic_3ds | N/A | N/A | N/A
arithmetic_5da | N/A | N/A | N/A
arithmetic_5ds | N/A | N/A | N/A
arithmetic_4da | N/A | N/A | N/A
arithmetic_2ds | N/A | N/A | N/A
arithmetic_4ds | N/A | N/A | N/A
arithmetic_2dm | N/A | N/A | N/A
arithmetic_2da | N/A | N/A | N/A
arithmetic_1dc | arithmetic | loglikelihood | - version: 1.0
hellaswag | multiple_choice | multiple_choice | - version: 1.0
logiqa | N/A | multiple_choice | - version: 1.0
mc_taco | N/A | multiple_choice | - version: 1.0
truthfulqa_gen | truthfulqa | generate_until | - version: 2.0
truthfulqa_mc1 | truthfulqa | multiple_choice | - version: 2.0
truthfulqa_mc2 | N/A | N/A | - version: 2.0
babi | N/A | generate_until | - version: 0.0
bbh_fewshot_reasoning_about_colored_objects | N/A | N/A | N/A
bbh_fewshot_ruin_names | N/A | N/A | N/A
bbh_fewshot_logical_deduction_three_objects | N/A | N/A | N/A
bbh_fewshot_web_of_lies | N/A | N/A | N/A
bbh_fewshot_logical_deduction_seven_objects | N/A | N/A | N/A
bbh_fewshot_sports_understanding | N/A | N/A | N/A
bbh_fewshot_temporal_sequences | N/A | N/A | N/A
bbh_fewshot_salient_translation_error_detection | N/A | N/A | N/A
bbh_fewshot_logical_deduction_five_objects | N/A | N/A | N/A
bbh_fewshot_tracking_shuffled_objects_three_objects | N/A | N/A | N/A
bbh_fewshot_penguins_in_a_table | N/A | N/A | N/A
bbh_fewshot_tracking_shuffled_objects_five_objects | N/A | N/A | N/A
bbh_fewshot_disambiguation_qa | N/A | N/A | N/A
bbh_fewshot_date_understanding | N/A | N/A | N/A
bbh_fewshot_causal_judgement | N/A | N/A | N/A
bbh_fewshot_multistep_arithmetic_two | N/A | N/A | N/A
bbh_fewshot_formal_fallacies | N/A | N/A | N/A
bbh_fewshot_boolean_expressions | N/A | N/A | N/A
bbh_fewshot_navigate | N/A | N/A | N/A
bbh_fewshot_geometric_shapes | N/A | N/A | N/A
bbh_fewshot_object_counting | N/A | N/A | N/A
bbh_fewshot_word_sorting | N/A | N/A | N/A
bbh_fewshot_hyperbaton | N/A | N/A | N/A
bbh_fewshot_dyck_languages | N/A | N/A | N/A
bbh_fewshot_snarks | N/A | N/A | N/A
bbh_fewshot_tracking_shuffled_objects_seven_objects | N/A | N/A | N/A
bbh_fewshot_movie_recommendation | N/A | N/A | N/A
bbh_cot_fewshot_reasoning_about_colored_objects | N/A | N/A | N/A
bbh_cot_fewshot_ruin_names | N/A | N/A | N/A
bbh_cot_fewshot_logical_deduction_three_objects | N/A | N/A | N/A
bbh_cot_fewshot_web_of_lies | N/A | N/A | N/A
bbh_cot_fewshot_logical_deduction_seven_objects | N/A | N/A | N/A
bbh_cot_fewshot_sports_understanding | N/A | N/A | N/A
bbh_cot_fewshot_temporal_sequences | N/A | N/A | N/A
bbh_cot_fewshot_salient_translation_error_detection | N/A | N/A | N/A
bbh_cot_fewshot_logical_deduction_five_objects | N/A | N/A | N/A
bbh_cot_fewshot_tracking_shuffled_objects_three_objects | N/A | N/A | N/A
bbh_cot_fewshot_penguins_in_a_table | N/A | N/A | N/A
bbh_cot_fewshot_tracking_shuffled_objects_five_objects | N/A | N/A | N/A
bbh_cot_fewshot_disambiguation_qa | N/A | N/A | N/A
bbh_cot_fewshot_date_understanding | N/A | N/A | N/A
bbh_cot_fewshot_causal_judgement | N/A | N/A | N/A
bbh_cot_fewshot_multistep_arithmetic_two | N/A | N/A | N/A
bbh_cot_fewshot_formal_fallacies | N/A | N/A | N/A
bbh_cot_fewshot_boolean_expressions | N/A | N/A | N/A
bbh_cot_fewshot_navigate | N/A | N/A | N/A
bbh_cot_fewshot_geometric_shapes | N/A | N/A | N/A
bbh_cot_fewshot_object_counting | N/A | N/A | N/A
bbh_cot_fewshot_word_sorting | N/A | N/A | N/A
bbh_cot_fewshot_hyperbaton | N/A | N/A | N/A
bbh_cot_fewshot_dyck_languages | N/A | N/A | N/A
bbh_cot_fewshot_snarks | N/A | N/A | N/A
bbh_cot_fewshot_tracking_shuffled_objects_seven_objects | N/A | N/A | N/A
bbh_cot_fewshot_movie_recommendation | N/A | N/A | N/A
bbh_zeroshot_reasoning_about_colored_objects | N/A | N/A | N/A
bbh_zeroshot_ruin_names | N/A | N/A | N/A
bbh_zeroshot_logical_deduction_three_objects | N/A | N/A | N/A
bbh_zeroshot_web_of_lies | N/A | N/A | N/A
bbh_zeroshot_logical_deduction_seven_objects | N/A | N/A | N/A
bbh_zeroshot_sports_understanding | N/A | N/A | N/A
bbh_zeroshot_temporal_sequences | N/A | N/A | N/A
bbh_zeroshot_salient_translation_error_detection | N/A | N/A | N/A
bbh_zeroshot_logical_deduction_five_objects | N/A | N/A | N/A
bbh_zeroshot_tracking_shuffled_objects_three_objects | N/A | N/A | N/A
bbh_zeroshot_penguins_in_a_table | N/A | N/A | N/A
bbh_zeroshot_tracking_shuffled_objects_five_objects | N/A | N/A | N/A
bbh_zeroshot_disambiguation_qa | N/A | N/A | N/A
bbh_zeroshot_date_understanding | N/A | N/A | N/A
bbh_zeroshot_causal_judgement | N/A | N/A | N/A
bbh_zeroshot_multistep_arithmetic_two | N/A | N/A | N/A
bbh_zeroshot_formal_fallacies | N/A | N/A | N/A
bbh_zeroshot_boolean_expressions | N/A | N/A | N/A
bbh_zeroshot_navigate | N/A | N/A | N/A
bbh_zeroshot_geometric_shapes | N/A | N/A | N/A
bbh_zeroshot_object_counting | N/A | N/A | N/A
bbh_zeroshot_word_sorting | N/A | N/A | N/A
bbh_zeroshot_hyperbaton | N/A | N/A | N/A
bbh_zeroshot_dyck_languages | N/A | N/A | N/A
bbh_zeroshot_snarks | N/A | N/A | N/A
bbh_zeroshot_tracking_shuffled_objects_seven_objects | N/A | N/A | N/A
bbh_zeroshot_movie_recommendation | N/A | N/A | N/A
bbh_cot_zeroshot_reasoning_about_colored_objects | N/A | N/A | N/A
bbh_cot_zeroshot_ruin_names | N/A | N/A | N/A
bbh_cot_zeroshot_logical_deduction_three_objects | N/A | N/A | N/A
bbh_cot_zeroshot_web_of_lies | N/A | N/A | N/A
bbh_cot_zeroshot_logical_deduction_seven_objects | N/A | N/A | N/A
bbh_cot_zeroshot_sports_understanding | N/A | N/A | N/A
bbh_cot_zeroshot_temporal_sequences | N/A | N/A | N/A
bbh_cot_zeroshot_salient_translation_error_detection | N/A | N/A | N/A
bbh_cot_zeroshot_logical_deduction_five_objects | N/A | N/A | N/A
bbh_cot_zeroshot_tracking_shuffled_objects_three_objects | N/A | N/A | N/A
bbh_cot_zeroshot_penguins_in_a_table | N/A | N/A | N/A
bbh_cot_zeroshot_tracking_shuffled_objects_five_objects | N/A | N/A | N/A
bbh_cot_zeroshot_disambiguation_qa | N/A | N/A | N/A
bbh_cot_zeroshot_date_understanding | N/A | N/A | N/A
bbh_cot_zeroshot_causal_judgement | N/A | N/A | N/A
bbh_cot_zeroshot_multistep_arithmetic_two | N/A | N/A | N/A
bbh_cot_zeroshot_formal_fallacies | N/A | N/A | N/A
bbh_cot_zeroshot_boolean_expressions | N/A | N/A | N/A
bbh_cot_zeroshot_navigate | N/A | N/A | N/A
bbh_cot_zeroshot_geometric_shapes | N/A | N/A | N/A
bbh_cot_zeroshot_object_counting | N/A | N/A | N/A
bbh_cot_zeroshot_word_sorting | N/A | N/A | N/A
bbh_cot_zeroshot_hyperbaton | N/A | N/A | N/A
bbh_cot_zeroshot_dyck_languages | N/A | N/A | N/A
bbh_cot_zeroshot_snarks | N/A | N/A | N/A
bbh_cot_zeroshot_tracking_shuffled_objects_seven_objects | N/A | N/A | N/A
bbh_cot_zeroshot_movie_recommendation | N/A | N/A | N/A
fld_star | N/A | N/A | N/A
fld_default | fld | N/A | N/A
kmmlu_mechanical_engineering | N/A | N/A | N/A
kmmlu_aviation_engineering_and_maintenance | N/A | N/A | N/A
kmmlu_economics | N/A | N/A | N/A
kmmlu_chemistry | N/A | N/A | N/A
kmmlu_education | N/A | N/A | N/A
kmmlu_real_estate | N/A | N/A | N/A
kmmlu_law | N/A | N/A | N/A
kmmlu_public_safety | N/A | N/A | N/A
kmmlu_telecommunications_and_wireless_technology | N/A | N/A | N/A
kmmlu_agricultural_sciences | N/A | N/A | N/A
kmmlu_environmental_science | N/A | N/A | N/A
kmmlu_industrial_engineer | N/A | N/A | N/A
kmmlu_health | N/A | N/A | N/A
kmmlu_social_welfare | N/A | N/A | N/A
kmmlu_computer_science | N/A | N/A | N/A
kmmlu_information_technology | N/A | N/A | N/A
kmmlu_patent | N/A | N/A | N/A
kmmlu_food_processing | N/A | N/A | N/A
kmmlu_maritime_engineering | N/A | N/A | N/A
kmmlu_nondestructive_testing | N/A | N/A | N/A
kmmlu_ecology | N/A | N/A | N/A
kmmlu_political_science_and_sociology | N/A | N/A | N/A
kmmlu_electronics_engineering | N/A | N/A | N/A
kmmlu_accounting | N/A | N/A | N/A
kmmlu_taxation | N/A | N/A | N/A
kmmlu_marketing | N/A | N/A | N/A
kmmlu_fashion | N/A | N/A | N/A
kmmlu_construction | N/A | N/A | N/A
kmmlu_psychology | N/A | N/A | N/A
kmmlu_machine_design_and_manufacturing | N/A | N/A | N/A
kmmlu_gas_technology_and_engineering | N/A | N/A | N/A
kmmlu_interior_architecture_and_design | N/A | N/A | N/A
kmmlu_biology | N/A | N/A | N/A
kmmlu_management | N/A | N/A | N/A
kmmlu_materials_engineering | N/A | N/A | N/A
kmmlu_refrigerating_machinery | N/A | N/A | N/A
kmmlu_civil_engineering | N/A | N/A | N/A
kmmlu_criminal_law | N/A | N/A | N/A
kmmlu_energy_management | N/A | N/A | N/A
kmmlu_electrical_engineering | N/A | N/A | N/A
kmmlu_geomatics | N/A | N/A | N/A
kmmlu_railway_and_automotive_engineering | N/A | N/A | N/A
kmmlu_chemical_engineering | N/A | N/A | N/A
race | N/A | multiple_choice | - version: 2.0
ceval-valid_metrology_engineer | N/A | N/A | N/A
ceval-valid_high_school_politics | N/A | N/A | N/A
ceval-valid_sports_science | N/A | N/A | N/A
ceval-valid_legal_professional | N/A | N/A | N/A
ceval-valid_college_physics | N/A | N/A | N/A
ceval-valid_high_school_chemistry | N/A | N/A | N/A
ceval-valid_fire_engineer | N/A | N/A | N/A
ceval-valid_middle_school_mathematics | N/A | N/A | N/A
ceval-valid_middle_school_physics | N/A | N/A | N/A
ceval-valid_modern_chinese_history | N/A | N/A | N/A
ceval-valid_high_school_history | N/A | N/A | N/A
ceval-valid_college_chemistry | N/A | N/A | N/A
ceval-valid_plant_protection | N/A | N/A | N/A
ceval-valid_urban_and_rural_planner | N/A | N/A | N/A
ceval-valid_marxism | N/A | N/A | N/A
ceval-valid_tax_accountant | N/A | N/A | N/A
ceval-valid_high_school_geography | N/A | N/A | N/A
ceval-valid_accountant | N/A | N/A | N/A
ceval-valid_mao_zedong_thought | N/A | N/A | N/A
ceval-valid_electrical_engineer | N/A | N/A | N/A
ceval-valid_high_school_biology | N/A | N/A | N/A
ceval-valid_high_school_chinese | N/A | N/A | N/A
ceval-valid_computer_network | N/A | N/A | N/A
ceval-valid_middle_school_chemistry | N/A | N/A | N/A
ceval-valid_college_economics | N/A | N/A | N/A
ceval-valid_logic | N/A | N/A | N/A
ceval-valid_art_studies | N/A | N/A | N/A
ceval-valid_discrete_mathematics | N/A | N/A | N/A
ceval-valid_middle_school_biology | N/A | N/A | N/A
ceval-valid_teacher_qualification | N/A | N/A | N/A
ceval-valid_business_administration | N/A | N/A | N/A
ceval-valid_clinical_medicine | N/A | N/A | N/A
ceval-valid_civil_servant | N/A | N/A | N/A
ceval-valid_education_science | N/A | N/A | N/A
ceval-valid_veterinary_medicine | N/A | N/A | N/A
ceval-valid_chinese_language_and_literature | N/A | N/A | N/A
ceval-valid_middle_school_history | N/A | N/A | N/A
ceval-valid_middle_school_politics | N/A | N/A | N/A
ceval-valid_ideological_and_moral_cultivation | N/A | N/A | N/A
ceval-valid_probability_and_statistics | N/A | N/A | N/A
ceval-valid_basic_medicine | N/A | N/A | N/A
ceval-valid_computer_architecture | N/A | N/A | N/A
ceval-valid_operating_system | N/A | N/A | N/A
ceval-valid_professional_tour_guide | N/A | N/A | N/A
ceval-valid_law | N/A | N/A | N/A
ceval-valid_advanced_mathematics | N/A | N/A | N/A
ceval-valid_high_school_mathematics | N/A | N/A | N/A
ceval-valid_environmental_impact_assessment_engineer | N/A | N/A | N/A
ceval-valid_college_programming | N/A | N/A | N/A
ceval-valid_high_school_physics | N/A | N/A | N/A
ceval-valid_middle_school_geography | N/A | N/A | N/A
ceval-valid_physician | N/A | N/A | N/A
xstorycloze_zh | N/A | N/A | N/A
xstorycloze_hi | N/A | N/A | N/A
xstorycloze_ru | N/A | N/A | N/A
xstorycloze_id | N/A | N/A | N/A
xstorycloze_eu | N/A | N/A | N/A
xstorycloze_es | N/A | N/A | N/A
xstorycloze_sw | N/A | N/A | N/A
xstorycloze_te | N/A | N/A | N/A
xstorycloze_my | N/A | N/A | N/A
xstorycloze_ar | N/A | multiple_choice | - version: 1.0
xstorycloze_en | N/A | N/A | N/A
pubmedqa | N/A | multiple_choice | - version: 1.0
swag | N/A | multiple_choice | - version: 1.0
bigbench_swahili_english_proverbs_multiple_choice | N/A | N/A | N/A
bigbench_implicatures_multiple_choice | N/A | N/A | N/A
bigbench_novel_concepts_multiple_choice | N/A | N/A | N/A
bigbench_metaphor_boolean_multiple_choice | N/A | N/A | N/A
bigbench_play_dialog_same_or_different_multiple_choice | N/A | N/A | N/A
bigbench_undo_permutation_multiple_choice | N/A | N/A | N/A
bigbench_common_morpheme_multiple_choice | N/A | N/A | N/A
bigbench_tense_multiple_choice | N/A | N/A | N/A
bigbench_reasoning_about_colored_objects_multiple_choice | N/A | N/A | N/A
bigbench_ruin_names_multiple_choice | N/A | N/A | N/A
bigbench_minute_mysteries_qa_multiple_choice | N/A | N/A | N/A
bigbench_natural_instructions_multiple_choice | N/A | N/A | N/A
bigbench_emojis_emotion_prediction_multiple_choice | N/A | N/A | N/A
bigbench_physics_multiple_choice | N/A | N/A | N/A
bigbench_sufficient_information_multiple_choice | N/A | N/A | N/A
bigbench_physics_questions_multiple_choice | N/A | N/A | N/A
bigbench_intent_recognition_multiple_choice | N/A | N/A | N/A
bigbench_strategyqa_multiple_choice | N/A | N/A | N/A
bigbench_logical_deduction_multiple_choice | N/A | N/A | N/A
bigbench_parsinlu_reading_comprehension_multiple_choice | N/A | N/A | N/A
bigbench_arithmetic_multiple_choice | N/A | N/A | N/A
bigbench_codenames_multiple_choice | N/A | N/A | N/A
bigbench_metaphor_understanding_multiple_choice | N/A | N/A | N/A
bigbench_contextual_parametric_knowledge_conflicts_multiple_choice | N/A | N/A | N/A
bigbench_sports_understanding_multiple_choice | N/A | N/A | N/A
bigbench_rephrase_multiple_choice | N/A | N/A | N/A
bigbench_language_identification_multiple_choice | N/A | N/A | N/A
bigbench_suicide_risk_multiple_choice | N/A | N/A | N/A
bigbench_temporal_sequences_multiple_choice | N/A | N/A | N/A
bigbench_unit_interpretation_multiple_choice | N/A | N/A | N/A
bigbench_formal_fallacies_syllogisms_negation_multiple_choice | N/A | N/A | N/A
bigbench_salient_translation_error_detection_multiple_choice | N/A | N/A | N/A
bigbench_chinese_remainder_theorem_multiple_choice | N/A | N/A | N/A
bigbench_mult_data_wrangling_multiple_choice | N/A | N/A | N/A
bigbench_winowhy_multiple_choice | N/A | N/A | N/A
bigbench_which_wiki_edit_multiple_choice | N/A | N/A | N/A
bigbench_simple_arithmetic_json_subtasks_multiple_choice | N/A | N/A | N/A
bigbench_hindi_question_answering_multiple_choice | N/A | N/A | N/A
bigbench_movie_dialog_same_or_different_multiple_choice | N/A | N/A | N/A
bigbench_swedish_to_german_proverbs_multiple_choice | N/A | N/A | N/A
bigbench_checkmate_in_one_multiple_choice | N/A | N/A | N/A
bigbench_modified_arithmetic_multiple_choice | N/A | N/A | N/A
bigbench_irony_identification_multiple_choice | N/A | N/A | N/A
bigbench_conlang_translation_multiple_choice | N/A | N/A | N/A
bigbench_hinglish_toxicity_multiple_choice | N/A | N/A | N/A
bigbench_implicit_relations_multiple_choice | N/A | N/A | N/A
bigbench_matrixshapes_multiple_choice | N/A | N/A | N/A
bigbench_abstract_narrative_understanding_multiple_choice | N/A | N/A | N/A
bigbench_mathematical_induction_multiple_choice | N/A | N/A | N/A
bigbench_identify_odd_metaphor_multiple_choice | N/A | N/A | N/A
bigbench_logical_sequence_multiple_choice | N/A | N/A | N/A
bigbench_figure_of_speech_detection_multiple_choice | N/A | N/A | N/A
bigbench_paragraph_segmentation_multiple_choice | N/A | N/A | N/A
bigbench_what_is_the_tao_multiple_choice | N/A | N/A | N/A
bigbench_simple_text_editing_multiple_choice | N/A | N/A | N/A
bigbench_causal_judgment_multiple_choice | N/A | N/A | N/A
bigbench_cause_and_effect_multiple_choice | N/A | N/A | N/A
bigbench_scientific_press_release_multiple_choice | N/A | N/A | N/A
bigbench_auto_categorization_multiple_choice | N/A | N/A | N/A
bigbench_unit_conversion_multiple_choice | N/A | N/A | N/A
bigbench_linguistic_mappings_multiple_choice | N/A | N/A | N/A
bigbench_logic_grid_puzzle_multiple_choice | N/A | N/A | N/A
bigbench_ascii_word_recognition_multiple_choice | N/A | N/A | N/A
bigbench_real_or_fake_text_multiple_choice | N/A | N/A | N/A
bigbench_bridging_anaphora_resolution_barqa_multiple_choice | N/A | N/A | N/A
bigbench_kannada_multiple_choice | N/A | N/A | N/A
bigbench_penguins_in_a_table_multiple_choice | N/A | N/A | N/A
bigbench_linguistics_puzzles_multiple_choice | N/A | N/A | N/A
bigbench_authorship_verification_multiple_choice | N/A | N/A | N/A
bigbench_color_multiple_choice | N/A | N/A | N/A
bigbench_disambiguation_qa_multiple_choice | N/A | N/A | N/A
bigbench_crass_ai_multiple_choice | N/A | N/A | N/A
bigbench_date_understanding_multiple_choice | N/A | N/A | N/A
bigbench_international_phonetic_alphabet_nli_multiple_choice | N/A | N/A | N/A
bigbench_entailed_polarity_multiple_choice | N/A | N/A | N/A
bigbench_unnatural_in_context_learning_multiple_choice | N/A | N/A | N/A
bigbench_known_unknowns_multiple_choice | N/A | N/A | N/A
bigbench_few_shot_nlg_multiple_choice | N/A | N/A | N/A
bigbench_dark_humor_detection_multiple_choice | N/A | N/A | N/A
bigbench_simple_ethical_questions_multiple_choice | N/A | N/A | N/A
bigbench_cifar10_classification_multiple_choice | N/A | N/A | N/A
bigbench_social_support_multiple_choice | N/A | N/A | N/A
bigbench_identify_math_theorems_multiple_choice | N/A | N/A | N/A
bigbench_word_unscrambling_multiple_choice | N/A | N/A | N/A
bigbench_logical_fallacy_detection_multiple_choice | N/A | N/A | N/A
bigbench_phrase_relatedness_multiple_choice | N/A | N/A | N/A
bigbench_empirical_judgments_multiple_choice | N/A | N/A | N/A
bigbench_simple_arithmetic_multiple_targets_json_multiple_choice | N/A | N/A | N/A
bigbench_code_line_description_multiple_choice | N/A | N/A | N/A
bigbench_gem_multiple_choice | N/A | N/A | N/A
bigbench_gender_inclusive_sentences_german_multiple_choice | N/A | N/A | N/A
bigbench_mnist_ascii_multiple_choice | N/A | N/A | N/A
bigbench_logical_args_multiple_choice | N/A | N/A | N/A
bigbench_question_selection_multiple_choice | N/A | N/A | N/A
bigbench_discourse_marker_prediction_multiple_choice | N/A | N/A | N/A
bigbench_elementary_math_qa_multiple_choice | N/A | N/A | N/A
bigbench_operators_multiple_choice | N/A | N/A | N/A
bigbench_gre_reading_comprehension_multiple_choice | N/A | N/A | N/A
bigbench_physical_intuition_multiple_choice | N/A | N/A | N/A
bigbench_riddle_sense_multiple_choice | N/A | N/A | N/A
bigbench_cs_algorithms_multiple_choice | N/A | N/A | N/A
bigbench_evaluating_information_essentiality_multiple_choice | N/A | N/A | N/A
bigbench_fact_checker_multiple_choice | N/A | N/A | N/A
bigbench_navigate_multiple_choice | N/A | N/A | N/A
bigbench_timedial_multiple_choice | N/A | N/A | N/A
bigbench_semantic_parsing_spider_multiple_choice | N/A | N/A | N/A
bigbench_geometric_shapes_multiple_choice | N/A | N/A | N/A
bigbench_intersect_geometry_multiple_choice | N/A | N/A | N/A
bigbench_chess_state_tracking_multiple_choice | N/A | N/A | N/A
bigbench_simple_arithmetic_json_multiple_choice | N/A | N/A | N/A
bigbench_fantasy_reasoning_multiple_choice | N/A | N/A | N/A
bigbench_hindu_knowledge_multiple_choice | N/A | N/A | N/A
bigbench_moral_permissibility_multiple_choice | N/A | N/A | N/A
bigbench_strange_stories_multiple_choice | N/A | N/A | N/A
bigbench_object_counting_multiple_choice | N/A | N/A | N/A
bigbench_language_games_multiple_choice | N/A | N/A | N/A
bigbench_anachronisms_multiple_choice | N/A | N/A | N/A
bigbench_simple_arithmetic_json_multiple_choice_multiple_choice | N/A | N/A | N/A
bigbench_topical_chat_multiple_choice | N/A | N/A | N/A
bigbench_vitaminc_fact_verification_multiple_choice | N/A | N/A | N/A
bigbench_auto_debugging_multiple_choice | N/A | N/A | N/A
bigbench_periodic_elements_multiple_choice | N/A | N/A | N/A
bigbench_key_value_maps_multiple_choice | N/A | N/A | N/A
bigbench_analytic_entailment_multiple_choice | N/A | N/A | N/A
bigbench_goal_step_wikihow_multiple_choice | N/A | N/A | N/A
bigbench_cryobiology_spanish_multiple_choice | N/A | N/A | N/A
bigbench_cryptonite_multiple_choice | N/A | N/A | N/A
bigbench_bbq_lite_json_multiple_choice | N/A | N/A | N/A
bigbench_semantic_parsing_in_context_sparc_multiple_choice | N/A | N/A | N/A
bigbench_word_sorting_multiple_choice | N/A | N/A | N/A
bigbench_entailed_polarity_hindi_multiple_choice | N/A | N/A | N/A
bigbench_emoji_movie_multiple_choice | N/A | N/A | N/A
bigbench_symbol_interpretation_multiple_choice | N/A | N/A | N/A
bigbench_human_organs_senses_multiple_choice | N/A | N/A | N/A
bigbench_odd_one_out_multiple_choice | N/A | N/A | N/A
bigbench_english_russian_proverbs_multiple_choice | N/A | N/A | N/A
bigbench_understanding_fables_multiple_choice | N/A | N/A | N/A
bigbench_disfl_qa_multiple_choice | N/A | N/A | N/A
bigbench_polish_sequence_labeling_multiple_choice | N/A | N/A | N/A
bigbench_kanji_ascii_multiple_choice | N/A | N/A | N/A
bigbench_crash_blossom_multiple_choice | N/A | N/A | N/A
bigbench_tracking_shuffled_objects_multiple_choice | N/A | N/A | N/A
bigbench_presuppositions_as_nli_multiple_choice | N/A | N/A | N/A
bigbench_misconceptions_russian_multiple_choice | N/A | N/A | N/A
bigbench_analogical_similarity_multiple_choice | N/A | N/A | N/A
bigbench_simp_turing_concept_multiple_choice | N/A | N/A | N/A
bigbench_hhh_alignment_multiple_choice | N/A | N/A | N/A
bigbench_repeat_copy_logic_multiple_choice | N/A | N/A | N/A
bigbench_hyperbaton_multiple_choice | N/A | N/A | N/A
bigbench_persian_idioms_multiple_choice | N/A | N/A | N/A
bigbench_dyck_languages_multiple_choice | N/A | N/A | N/A
bigbench_similarities_abstraction_multiple_choice | N/A | N/A | N/A
bigbench_nonsense_words_grammar_multiple_choice | N/A | N/A | N/A
bigbench_snarks_multiple_choice | N/A | N/A | N/A
bigbench_international_phonetic_alphabet_transliterate_multiple_choice | N/A | N/A | N/A
bigbench_epistemic_reasoning_multiple_choice | N/A | N/A | N/A
bigbench_english_proverbs_multiple_choice | N/A | N/A | N/A
bigbench_conceptual_combinations_multiple_choice | N/A | N/A | N/A
bigbench_sentence_ambiguity_multiple_choice | N/A | N/A | N/A
bigbench_qa_wikidata_multiple_choice | N/A | N/A | N/A
bigbench_multiemo_multiple_choice | N/A | N/A | N/A
bigbench_misconceptions_multiple_choice | N/A | N/A | N/A
bigbench_list_functions_multiple_choice | N/A | N/A | N/A
bigbench_parsinlu_qa_multiple_choice | N/A | N/A | N/A
bigbench_movie_recommendation_multiple_choice | N/A | N/A | N/A
bigbench_general_knowledge_multiple_choice | N/A | N/A | N/A
bigbench_social_iqa_multiple_choice | N/A | N/A | N/A
bigbench_swahili_english_proverbs_generate_until | N/A | N/A | N/A
bigbench_implicatures_generate_until | N/A | N/A | N/A
bigbench_novel_concepts_generate_until | N/A | N/A | N/A
bigbench_metaphor_boolean_generate_until | N/A | N/A | N/A
bigbench_play_dialog_same_or_different_generate_until | N/A | N/A | N/A
bigbench_undo_permutation_generate_until | N/A | N/A | N/A
bigbench_common_morpheme_generate_until | N/A | N/A | N/A
bigbench_tense_generate_until | N/A | N/A | N/A
bigbench_reasoning_about_colored_objects_generate_until | N/A | N/A | N/A
bigbench_ruin_names_generate_until | N/A | N/A | N/A
bigbench_minute_mysteries_qa_generate_until | N/A | N/A | N/A
bigbench_natural_instructions_generate_until | N/A | N/A | N/A
bigbench_emojis_emotion_prediction_generate_until | N/A | N/A | N/A
bigbench_physics_generate_until | N/A | N/A | N/A
bigbench_sufficient_information_generate_until | N/A | N/A | N/A
bigbench_physics_questions_generate_until | N/A | N/A | N/A
bigbench_intent_recognition_generate_until | N/A | N/A | N/A
bigbench_strategyqa_generate_until | N/A | N/A | N/A
bigbench_logical_deduction_generate_until | N/A | N/A | N/A
bigbench_parsinlu_reading_comprehension_generate_until | N/A | N/A | N/A
bigbench_arithmetic_generate_until | N/A | N/A | N/A
bigbench_codenames_generate_until | N/A | N/A | N/A
bigbench_metaphor_understanding_generate_until | N/A | N/A | N/A
bigbench_contextual_parametric_knowledge_conflicts_generate_until | N/A | N/A | N/A
bigbench_sports_understanding_generate_until | N/A | N/A | N/A
bigbench_rephrase_generate_until | N/A | N/A | N/A
bigbench_language_identification_generate_until | N/A | N/A | N/A
bigbench_suicide_risk_generate_until | N/A | N/A | N/A
bigbench_temporal_sequences_generate_until | N/A | N/A | N/A
bigbench_unit_interpretation_generate_until | N/A | N/A | N/A
bigbench_formal_fallacies_syllogisms_negation_generate_until | N/A | N/A | N/A
bigbench_salient_translation_error_detection_generate_until | N/A | N/A | N/A
bigbench_chinese_remainder_theorem_generate_until | N/A | N/A | N/A
bigbench_mult_data_wrangling_generate_until | N/A | N/A | N/A
bigbench_winowhy_generate_until | N/A | N/A | N/A
bigbench_which_wiki_edit_generate_until | N/A | N/A | N/A
bigbench_simple_arithmetic_json_subtasks_generate_until | N/A | N/A | N/A
bigbench_hindi_question_answering_generate_until | N/A | N/A | N/A
bigbench_movie_dialog_same_or_different_generate_until | N/A | N/A | N/A
bigbench_swedish_to_german_proverbs_generate_until | N/A | N/A | N/A
bigbench_checkmate_in_one_generate_until | N/A | N/A | N/A
bigbench_modified_arithmetic_generate_until | N/A | N/A | N/A
bigbench_irony_identification_generate_until | N/A | N/A | N/A
bigbench_conlang_translation_generate_until | N/A | N/A | N/A
bigbench_hinglish_toxicity_generate_until | N/A | N/A | N/A
bigbench_implicit_relations_generate_until | N/A | N/A | N/A
bigbench_matrixshapes_generate_until | N/A | N/A | N/A
bigbench_abstract_narrative_understanding_generate_until | N/A | N/A | N/A
bigbench_mathematical_induction_generate_until | N/A | N/A | N/A
bigbench_identify_odd_metaphor_generate_until | N/A | N/A | N/A
bigbench_logical_sequence_generate_until | N/A | N/A | N/A
bigbench_figure_of_speech_detection_generate_until | N/A | N/A | N/A
bigbench_paragraph_segmentation_generate_until | N/A | N/A | N/A
bigbench_what_is_the_tao_generate_until | N/A | N/A | N/A
bigbench_simple_text_editing_generate_until | N/A | N/A | N/A
bigbench_causal_judgment_generate_until | N/A | N/A | N/A
bigbench_cause_and_effect_generate_until | N/A | N/A | N/A
bigbench_scientific_press_release_generate_until | N/A | N/A | N/A
bigbench_auto_categorization_generate_until | N/A | N/A | N/A
bigbench_unit_conversion_generate_until | N/A | N/A | N/A
bigbench_linguistic_mappings_generate_until | N/A | N/A | N/A
bigbench_logic_grid_puzzle_generate_until | N/A | N/A | N/A
bigbench_ascii_word_recognition_generate_until | N/A | N/A | N/A
bigbench_real_or_fake_text_generate_until | N/A | N/A | N/A
bigbench_bridging_anaphora_resolution_barqa_generate_until | N/A | N/A | N/A
bigbench_kannada_generate_until | N/A | N/A | N/A
bigbench_penguins_in_a_table_generate_until | N/A | N/A | N/A
bigbench_linguistics_puzzles_generate_until | N/A | N/A | N/A
bigbench_authorship_verification_generate_until | N/A | N/A | N/A
bigbench_color_generate_until | N/A | N/A | N/A
bigbench_disambiguation_qa_generate_until | N/A | N/A | N/A
bigbench_crass_ai_generate_until | N/A | N/A | N/A
bigbench_date_understanding_generate_until | N/A | N/A | N/A
bigbench_international_phonetic_alphabet_nli_generate_until | N/A | N/A | N/A
bigbench_entailed_polarity_generate_until | N/A | N/A | N/A
bigbench_unnatural_in_context_learning_generate_until | N/A | N/A | N/A
bigbench_known_unknowns_generate_until | N/A | N/A | N/A
bigbench_few_shot_nlg_generate_until | N/A | N/A | N/A
bigbench_dark_humor_detection_generate_until | N/A | N/A | N/A
bigbench_simple_ethical_questions_generate_until | N/A | N/A | N/A
bigbench_cifar10_classification_generate_until | N/A | N/A | N/A
bigbench_social_support_generate_until | N/A | N/A | N/A
bigbench_identify_math_theorems_generate_until | N/A | N/A | N/A
bigbench_word_unscrambling_generate_until | N/A | N/A | N/A
bigbench_logical_fallacy_detection_generate_until | N/A | N/A | N/A
bigbench_phrase_relatedness_generate_until | N/A | N/A | N/A
bigbench_empirical_judgments_generate_until | N/A | N/A | N/A
bigbench_simple_arithmetic_multiple_targets_json_generate_until | N/A | N/A | N/A
bigbench_code_line_description_generate_until | N/A | N/A | N/A
bigbench_gem_generate_until | N/A | N/A | N/A
bigbench_gender_inclusive_sentences_german_generate_until | N/A | N/A | N/A
bigbench_mnist_ascii_generate_until | N/A | N/A | N/A
bigbench_logical_args_generate_until | N/A | N/A | N/A
bigbench_question_selection_generate_until | N/A | N/A | N/A
bigbench_discourse_marker_prediction_generate_until | N/A | N/A | N/A
bigbench_elementary_math_qa_generate_until | N/A | N/A | N/A
bigbench_operators_generate_until | N/A | N/A | N/A
bigbench_gre_reading_comprehension_generate_until | N/A | N/A | N/A
bigbench_physical_intuition_generate_until | N/A | N/A | N/A
bigbench_riddle_sense_generate_until | N/A | N/A | N/A
bigbench_cs_algorithms_generate_until | N/A | N/A | N/A
bigbench_evaluating_information_essentiality_generate_until | N/A | N/A | N/A
bigbench_fact_checker_generate_until | N/A | N/A | N/A
bigbench_navigate_generate_until | N/A | N/A | N/A
bigbench_timedial_generate_until | N/A | N/A | N/A
bigbench_semantic_parsing_spider_generate_until | N/A | N/A | N/A
bigbench_geometric_shapes_generate_until | N/A | N/A | N/A
bigbench_intersect_geometry_generate_until | N/A | N/A | N/A
bigbench_chess_state_tracking_generate_until | N/A | N/A | N/A
bigbench_simple_arithmetic_json_generate_until | N/A | N/A | N/A
bigbench_fantasy_reasoning_generate_until | N/A | N/A | N/A
bigbench_hindu_knowledge_generate_until | N/A | N/A | N/A
bigbench_moral_permissibility_generate_until | N/A | N/A | N/A
bigbench_strange_stories_generate_until | N/A | N/A | N/A
bigbench_object_counting_generate_until | N/A | N/A | N/A
bigbench_language_games_generate_until | N/A | N/A | N/A
bigbench_anachronisms_generate_until | N/A | N/A | N/A
bigbench_simple_arithmetic_json_multiple_choice_generate_until | N/A | N/A | N/A
bigbench_topical_chat_generate_until | N/A | N/A | N/A
bigbench_vitaminc_fact_verification_generate_until | N/A | N/A | N/A
bigbench_auto_debugging_generate_until | N/A | N/A | N/A
bigbench_periodic_elements_generate_until | N/A | N/A | N/A
bigbench_key_value_maps_generate_until | N/A | N/A | N/A
bigbench_analytic_entailment_generate_until | N/A | N/A | N/A
bigbench_goal_step_wikihow_generate_until | N/A | N/A | N/A
bigbench_cryobiology_spanish_generate_until | N/A | N/A | N/A
bigbench_cryptonite_generate_until | N/A | N/A | N/A
bigbench_bbq_lite_json_generate_until | N/A | N/A | N/A
bigbench_semantic_parsing_in_context_sparc_generate_until | N/A | N/A | N/A
bigbench_word_sorting_generate_until | N/A | N/A | N/A
bigbench_entailed_polarity_hindi_generate_until | N/A | N/A | N/A
bigbench_emoji_movie_generate_until | N/A | N/A | N/A
bigbench_symbol_interpretation_generate_until | N/A | N/A | N/A
bigbench_human_organs_senses_generate_until | N/A | N/A | N/A
bigbench_odd_one_out_generate_until | N/A | N/A | N/A
bigbench_english_russian_proverbs_generate_until | N/A | N/A | N/A
bigbench_understanding_fables_generate_until | N/A | N/A | N/A
bigbench_disfl_qa_generate_until | N/A | N/A | N/A
bigbench_polish_sequence_labeling_generate_until | N/A | N/A | N/A
bigbench_kanji_ascii_generate_until | N/A | N/A | N/A
bigbench_crash_blossom_generate_until | N/A | N/A | N/A
bigbench_tracking_shuffled_objects_generate_until | N/A | N/A | N/A
bigbench_presuppositions_as_nli_generate_until | N/A | N/A | N/A
bigbench_misconceptions_russian_generate_until | N/A | N/A | N/A
bigbench_analogical_similarity_generate_until | N/A | N/A | N/A
bigbench_simp_turing_concept_generate_until | N/A | N/A | N/A
bigbench_hhh_alignment_generate_until | N/A | N/A | N/A
bigbench_repeat_copy_logic_generate_until | N/A | N/A | N/A
bigbench_hyperbaton_generate_until | N/A | N/A | N/A
bigbench_persian_idioms_generate_until | N/A | N/A | N/A
bigbench_dyck_languages_generate_until | N/A | N/A | N/A
bigbench_similarities_abstraction_generate_until | N/A | N/A | N/A
bigbench_nonsense_words_grammar_generate_until | N/A | N/A | N/A
bigbench_snarks_generate_until | N/A | N/A | N/A
bigbench_international_phonetic_alphabet_transliterate_generate_until | N/A | N/A | N/A
bigbench_epistemic_reasoning_generate_until | N/A | N/A | N/A
bigbench_english_proverbs_generate_until | N/A | N/A | N/A
bigbench_conceptual_combinations_generate_until | N/A | N/A | N/A
bigbench_sentence_ambiguity_generate_until | N/A | N/A | N/A
bigbench_qa_wikidata_generate_until | N/A | N/A | N/A
bigbench_multiemo_generate_until | N/A | N/A | N/A
bigbench_misconceptions_generate_until | N/A | N/A | N/A
bigbench_list_functions_generate_until | N/A | N/A | N/A
bigbench_parsinlu_qa_generate_until | N/A | N/A | N/A
bigbench_movie_recommendation_generate_until | N/A | N/A | N/A
bigbench_general_knowledge_generate_until | N/A | N/A | N/A
bigbench_social_iqa_generate_until | N/A | N/A | N/A
mutual_plus | N/A | N/A | N/A
mutual | N/A | multiple_choice | - version: 2.0
winogrande | N/A | multiple_choice | - version: 1.0
piqa | N/A | multiple_choice | - version: 1.0
toxigen | N/A | multiple_choice | - version: 1.0
realtoxicityprompts | N/A | N/A | - version: 0.0
