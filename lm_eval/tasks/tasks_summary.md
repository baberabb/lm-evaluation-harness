Task | Group | Output Type | Metadata
--- | --- | --- | ---
qasper_bool |  | multiple_choice | - version: 1.0
qasper_freeform |  | generate_until | - version: 1.0
mathqa | math_word_problems | multiple_choice | - version: 1.0
lambada_openai_mt_en | lambada_multilingual | loglikelihood | - version: 1.0
lambada_openai_mt_es |  | null | null
lambada_openai_mt_de |  | null | null
lambada_openai_mt_fr |  | null | null
lambada_openai_mt_it |  | null | null
ifeval |  | generate_until | - version: 1.0
lambada_standard | lambada | loglikelihood | - version: 1.0
lambada_openai | lambada | loglikelihood | - version: 1.0
- scrolls_qasper
- scrolls_quality
- scrolls_narrativeqa
- scrolls_contractnli
- scrolls_govreport
- scrolls_summscreenfd
- scrolls_qmsum |  | null | null
anagrams1 | unscramble | generate_until | - version: 1.0
cycle_letters | unscramble | generate_until | - version: 1.0
anagrams2 | unscramble | generate_until | - version: 1.0
random_insertion | unscramble | generate_until | - version: 1.0
reversed_words | unscramble | generate_until | - version: 1.0
arc_challenge |  | null | null
arc_easy | ai2_arc | multiple_choice | - version: 1.0
anli_r1 | anli | multiple_choice | - version: 1.0
anli_r3 |  | null | null
anli_r2 |  | null | null
gsm8k_cot_self_consistency | chain_of_thought
self_consistency | null | - version: 0.0
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
- mmlu |  | null | null
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
      ignore_punctuation: true |  | null | null
- minerva_math_algebra
- minerva_math_counting_and_prob
- minerva_math_geometry
- minerva_math_intermediate_algebra
- minerva_math_num_theory
- minerva_math_prealgebra
- minerva_math_precalc |  | null | null
- include: yaml_templates/cot_template_yaml
  dataset_path: gsmk
  dataset_name: boolq
  use_prompt: promptsource:*
  validation_split: validation
- include: yaml_templates/cot_template_yaml
  dataset_path: EleutherAI/asdiv
  use_prompt: promptsource:*
  validation_split: validation |  | null | null
- include: yaml_templates/held_in_template_yaml
  dataset_path: super_glue
  dataset_name: rte
  use_prompt: prompt_templates/rte.yaml:*
  validation_split: validation |  | null | null
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
- mmlu_flan_cot_fewshot |  | null | null
- include: yaml_templates/held_in_template_yaml
  dataset_path: super_glue
  dataset_name: boolq
  use_prompt: prompt_templates/boolq.yaml:*
  validation_split: validation |  | null | null
null |  | null | null
null |  | null | null
null |  | null | null
null |  | null | null
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
  validation_split: validation |  | null | null
- flan_boolq
- flan_rte
- flan_anli
- flan_arc |  | null | null
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
  validation_split: dev_r3 |  | null | null
sciq |  | multiple_choice | - version: 1.0
blimp_sentential_negation_npi_licensor_present |  | null | null
blimp_wh_vs_that_no_gap |  | null | null
blimp_wh_island |  | null | null
blimp_wh_vs_that_no_gap_long_distance |  | null | null
blimp_determiner_noun_agreement_with_adj_2 |  | null | null
blimp_determiner_noun_agreement_irregular_1 |  | null | null
blimp_left_branch_island_echo_question |  | null | null
blimp_passive_1 |  | null | null
blimp_anaphor_number_agreement |  | null | null
blimp_irregular_plural_subject_verb_agreement_1 |  | null | null
blimp_only_npi_licensor_present |  | null | null
blimp_determiner_noun_agreement_2 |  | null | null
blimp_npi_present_2 |  | null | null
blimp_regular_plural_subject_verb_agreement_2 |  | null | null
blimp_causative |  | null | null
blimp_animate_subject_passive |  | null | null
blimp_principle_A_domain_3 |  | null | null
blimp_irregular_past_participle_verbs |  | null | null
blimp_transitive |  | null | null
blimp_tough_vs_raising_1 |  | null | null
blimp_adjunct_island |  | null | null
blimp_npi_present_1 |  | null | null
blimp_sentential_subject_island |  | null | null
blimp_drop_argument |  | null | null
blimp_matrix_question_npi_licensor_present |  | null | null
blimp_coordinate_structure_constraint_complex_left_branch |  | null | null
blimp_determiner_noun_agreement_with_adjective_1 |  | null | null
blimp_wh_questions_subject_gap |  | null | null
blimp_existential_there_quantifiers_1 |  | null | null
blimp_principle_A_c_command |  | null | null
blimp_principle_A_case_1 |  | null | null
blimp_tough_vs_raising_2 |  | null | null
blimp_complex_NP_island |  | null | null
blimp_wh_vs_that_with_gap_long_distance |  | null | null
blimp_principle_A_reconstruction |  | null | null
blimp_principle_A_case_2 |  | null | null
blimp_regular_plural_subject_verb_agreement_1 |  | null | null
blimp_principle_A_domain_1 |  | null | null
blimp_animate_subject_trans |  | null | null
blimp_anaphor_gender_agreement |  | null | null
blimp_determiner_noun_agreement_1 |  | null | null
blimp_determiner_noun_agreement_with_adj_irregular_2 |  | null | null
blimp_superlative_quantifiers_2 |  | null | null
blimp_inchoative |  | null | null
blimp_irregular_past_participle_adjectives |  | null | null
blimp_existential_there_subject_raising |  | null | null
blimp_wh_questions_subject_gap_long_distance |  | null | null
blimp_intransitive |  | null | null
blimp_principle_A_domain_2 |  | null | null
blimp_expletive_it_object_raising |  | null | null
blimp_ellipsis_n_bar_2 |  | null | null
blimp_coordinate_structure_constraint_object_extraction |  | null | null
blimp_existential_there_quantifiers_2 |  | null | null
blimp_wh_vs_that_with_gap |  | null | null
blimp_passive_2 |  | null | null
blimp_left_branch_island_simple_question |  | null | null
blimp_determiner_noun_agreement_irregular_2 |  | null | null
blimp_distractor_agreement_relational_noun |  | null | null
blimp_ellipsis_n_bar_1 |  | null | null
blimp_irregular_plural_subject_verb_agreement_2 |  | null | null
blimp_determiner_noun_agreement_with_adj_irregular_1 |  | null | null
blimp_sentential_negation_npi_scope |  | null | null
blimp_existential_there_object_raising |  | null | null
blimp_only_npi_scope |  | null | null
blimp_wh_questions_object_gap |  | null | null
blimp_distractor_agreement_relative_clause |  | null | null
blimp_superlative_quantifiers_1 |  | null | null
xwinograd_jp |  | null | null
xwinograd_pt |  | null | null
xwinograd_fr |  | null | null
xwinograd_ru |  | null | null
xwinograd_en |  | null | null
xwinograd_zh |  | null | null
lambada_openai_cloze_yaml | lambada_cloze | loglikelihood | - version: 1.0
lambada_standard_cloze_yaml | lambada_cloze | loglikelihood | - version: 1.0
xcopa_ta |  | null | null
xcopa_zh |  | null | null
xcopa_tr |  | null | null
xcopa_qu |  | null | null
xcopa_id |  | null | null
xcopa_sw |  | null | null
xcopa_et |  | multiple_choice | - version: 1.0
xcopa_ht |  | null | null
xcopa_vi |  | null | null
xcopa_it |  | null | null
xcopa_th |  | null | null
prost |  | multiple_choice | - version: 1.0
logiqa2 |  | multiple_choice | - version: 0.0
logieval |  | generate_until | - version: 0.0
wikitext |  | loglikelihood_rolling | - version: 2.0
asdiv |  | loglikelihood | - version: 1.0
webqs | freebase | multiple_choice | - version: 1.0
coqa |  | generate_until | - version: 2.0
mmlu_flan_cot_fewshot_anatomy |  | null | null
mmlu_flan_cot_fewshot_high_school_computer_science |  | null | null
mmlu_flan_cot_fewshot_college_physics |  | null | null
mmlu_flan_cot_fewshot_abstract_algebra |  | null | null
mmlu_flan_cot_fewshot_moral_disputes |  | null | null
mmlu_flan_cot_fewshot_professional_medicine |  | null | null
mmlu_flan_cot_fewshot_us_foreign_policy |  | null | null
mmlu_flan_cot_fewshot_security_studies |  | null | null
- mmlu_flan_cot_fewshot_stem
- mmlu_flan_cot_fewshot_other
- mmlu_flan_cot_fewshot_social_sciences
- mmlu_flan_cot_fewshot_humanities |  | null | null
mmlu_flan_cot_fewshot_virology |  | null | null
mmlu_flan_cot_fewshot_management |  | null | null
mmlu_flan_cot_fewshot_high_school_us_history |  | null | null
mmlu_flan_cot_fewshot_high_school_microeconomics |  | null | null
mmlu_flan_cot_fewshot_elementary_mathematics |  | null | null
mmlu_flan_cot_fewshot_human_aging |  | null | null
mmlu_flan_cot_fewshot_public_relations |  | null | null
mmlu_flan_cot_fewshot_computer_security |  | null | null
mmlu_flan_cot_fewshot_econometrics |  | null | null
mmlu_flan_cot_fewshot_high_school_geography |  | null | null
mmlu_flan_cot_fewshot_clinical_knowledge |  | null | null
mmlu_flan_cot_fewshot_professional_psychology |  | null | null
mmlu_flan_cot_fewshot_jurisprudence |  | null | null
mmlu_flan_cot_fewshot_prehistory |  | null | null
mmlu_flan_cot_fewshot_high_school_world_history |  | null | null
mmlu_flan_cot_fewshot_high_school_statistics |  | null | null
mmlu_flan_cot_fewshot_high_school_chemistry |  | null | null
mmlu_flan_cot_fewshot_medical_genetics |  | null | null
mmlu_flan_cot_fewshot_global_facts |  | null | null
mmlu_flan_cot_fewshot_college_medicine |  | null | null
mmlu_flan_cot_fewshot_college_chemistry |  | null | null
mmlu_flan_cot_fewshot_nutrition |  | null | null
mmlu_flan_cot_fewshot_formal_logic |  | null | null
mmlu_flan_cot_fewshot_conceptual_physics |  | null | null
mmlu_flan_cot_fewshot_college_biology |  | null | null
mmlu_flan_cot_fewshot_moral_scenarios |  | null | null
mmlu_flan_cot_fewshot_business_ethics |  | null | null
mmlu_flan_cot_fewshot_human_sexuality |  | null | null
mmlu_flan_cot_fewshot_professional_accounting |  | null | null
mmlu_flan_cot_fewshot_world_religions |  | null | null
mmlu_flan_cot_fewshot_high_school_physics |  | null | null
mmlu_flan_cot_fewshot_sociology |  | null | null
mmlu_flan_cot_fewshot_logical_fallacies |  | null | null
mmlu_flan_cot_fewshot_electrical_engineering |  | null | null
mmlu_flan_cot_fewshot_high_school_psychology |  | null | null
mmlu_flan_cot_fewshot_high_school_macroeconomics |  | null | null
mmlu_flan_cot_fewshot_professional_law |  | null | null
mmlu_flan_cot_fewshot_high_school_mathematics |  | null | null
mmlu_flan_cot_fewshot_international_law |  | null | null
mmlu_flan_cot_fewshot_astronomy |  | null | null
mmlu_flan_cot_fewshot_miscellaneous |  | null | null
mmlu_flan_cot_fewshot_college_mathematics |  | null | null
mmlu_flan_cot_fewshot_high_school_biology |  | null | null
mmlu_flan_cot_fewshot_college_computer_science |  | null | null
mmlu_flan_cot_fewshot_high_school_government_and_politics |  | null | null
mmlu_flan_cot_fewshot_high_school_european_history |  | null | null
mmlu_flan_cot_fewshot_philosophy |  | null | null
mmlu_flan_cot_fewshot_machine_learning |  | null | null
mmlu_flan_cot_fewshot_marketing |  | null | null
mmlu_flan_cot_zeroshot_anatomy |  | null | null
mmlu_flan_cot_zeroshot_high_school_computer_science |  | null | null
mmlu_flan_cot_zeroshot_college_physics |  | null | null
mmlu_flan_cot_zeroshot_abstract_algebra |  | null | null
mmlu_flan_cot_zeroshot_moral_disputes |  | null | null
mmlu_flan_cot_zeroshot_professional_medicine |  | null | null
mmlu_flan_cot_zeroshot_us_foreign_policy |  | null | null
mmlu_flan_cot_zeroshot_security_studies |  | null | null
- mmlu_flan_cot_zeroshot_stem
- mmlu_flan_cot_zeroshot_other
- mmlu_flan_cot_zeroshot_social_sciences
- mmlu_flan_cot_zeroshot_humanities |  | null | null
mmlu_flan_cot_zeroshot_virology |  | null | null
mmlu_flan_cot_zeroshot_management |  | null | null
mmlu_flan_cot_zeroshot_high_school_us_history |  | null | null
mmlu_flan_cot_zeroshot_high_school_microeconomics |  | null | null
mmlu_flan_cot_zeroshot_elementary_mathematics |  | null | null
mmlu_flan_cot_zeroshot_human_aging |  | null | null
mmlu_flan_cot_zeroshot_public_relations |  | null | null
mmlu_flan_cot_zeroshot_computer_security |  | null | null
mmlu_flan_cot_zeroshot_econometrics |  | null | null
mmlu_flan_cot_zeroshot_high_school_geography |  | null | null
mmlu_flan_cot_zeroshot_clinical_knowledge |  | null | null
mmlu_flan_cot_zeroshot_professional_psychology |  | null | null
mmlu_flan_cot_zeroshot_jurisprudence |  | null | null
mmlu_flan_cot_zeroshot_prehistory |  | null | null
mmlu_flan_cot_zeroshot_high_school_world_history |  | null | null
mmlu_flan_cot_zeroshot_high_school_statistics |  | null | null
mmlu_flan_cot_zeroshot_high_school_chemistry |  | null | null
mmlu_flan_cot_zeroshot_medical_genetics |  | null | null
mmlu_flan_cot_zeroshot_global_facts |  | null | null
mmlu_flan_cot_zeroshot_college_medicine |  | null | null
mmlu_flan_cot_zeroshot_college_chemistry |  | null | null
mmlu_flan_cot_zeroshot_nutrition |  | null | null
mmlu_flan_cot_zeroshot_formal_logic |  | null | null
mmlu_flan_cot_zeroshot_conceptual_physics |  | null | null
mmlu_flan_cot_zeroshot_college_biology |  | null | null
mmlu_flan_cot_zeroshot_moral_scenarios |  | null | null
mmlu_flan_cot_zeroshot_business_ethics |  | null | null
mmlu_flan_cot_zeroshot_human_sexuality |  | null | null
mmlu_flan_cot_zeroshot_professional_accounting |  | null | null
mmlu_flan_cot_zeroshot_world_religions |  | null | null
mmlu_flan_cot_zeroshot_high_school_physics |  | null | null
mmlu_flan_cot_zeroshot_sociology |  | null | null
mmlu_flan_cot_zeroshot_logical_fallacies |  | null | null
mmlu_flan_cot_zeroshot_electrical_engineering |  | null | null
mmlu_flan_cot_zeroshot_high_school_psychology |  | null | null
mmlu_flan_cot_zeroshot_high_school_macroeconomics |  | null | null
mmlu_flan_cot_zeroshot_professional_law |  | null | null
mmlu_flan_cot_zeroshot_high_school_mathematics |  | null | null
mmlu_flan_cot_zeroshot_international_law |  | null | null
mmlu_flan_cot_zeroshot_astronomy |  | null | null
mmlu_flan_cot_zeroshot_miscellaneous |  | null | null
mmlu_flan_cot_zeroshot_college_mathematics |  | null | null
mmlu_flan_cot_zeroshot_high_school_biology |  | null | null
mmlu_flan_cot_zeroshot_college_computer_science |  | null | null
mmlu_flan_cot_zeroshot_high_school_government_and_politics |  | null | null
mmlu_flan_cot_zeroshot_high_school_european_history |  | null | null
mmlu_flan_cot_zeroshot_philosophy |  | null | null
mmlu_flan_cot_zeroshot_machine_learning |  | null | null
mmlu_flan_cot_zeroshot_marketing |  | null | null
mmlu_flan_n_shot_loglikelihood_anatomy |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_computer_science |  | null | null
mmlu_flan_n_shot_loglikelihood_college_physics |  | null | null
mmlu_flan_n_shot_loglikelihood_abstract_algebra |  | null | null
mmlu_flan_n_shot_loglikelihood_moral_disputes |  | null | null
mmlu_flan_n_shot_loglikelihood_professional_medicine |  | null | null
mmlu_flan_n_shot_loglikelihood_us_foreign_policy |  | null | null
mmlu_flan_n_shot_loglikelihood_security_studies |  | null | null
- mmlu_flan_n_shot_loglikelihood_stem
- mmlu_flan_n_shot_loglikelihood_other
- mmlu_flan_n_shot_loglikelihood_social_sciences
- mmlu_flan_n_shot_loglikelihood_humanities |  | null | null
mmlu_flan_n_shot_loglikelihood_virology |  | null | null
mmlu_flan_n_shot_loglikelihood_management |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_us_history |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_microeconomics |  | null | null
mmlu_flan_n_shot_loglikelihood_elementary_mathematics |  | null | null
mmlu_flan_n_shot_loglikelihood_human_aging |  | null | null
mmlu_flan_n_shot_loglikelihood_public_relations |  | null | null
mmlu_flan_n_shot_loglikelihood_computer_security |  | null | null
mmlu_flan_n_shot_loglikelihood_econometrics |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_geography |  | null | null
mmlu_flan_n_shot_loglikelihood_clinical_knowledge |  | null | null
mmlu_flan_n_shot_loglikelihood_professional_psychology |  | null | null
mmlu_flan_n_shot_loglikelihood_jurisprudence |  | null | null
mmlu_flan_n_shot_loglikelihood_prehistory |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_world_history |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_statistics |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_chemistry |  | null | null
mmlu_flan_n_shot_loglikelihood_medical_genetics |  | null | null
mmlu_flan_n_shot_loglikelihood_global_facts |  | null | null
mmlu_flan_n_shot_loglikelihood_college_medicine |  | null | null
mmlu_flan_n_shot_loglikelihood_college_chemistry |  | null | null
mmlu_flan_n_shot_loglikelihood_nutrition |  | null | null
mmlu_flan_n_shot_loglikelihood_formal_logic |  | null | null
mmlu_flan_n_shot_loglikelihood_conceptual_physics |  | null | null
mmlu_flan_n_shot_loglikelihood_college_biology |  | null | null
mmlu_flan_n_shot_loglikelihood_moral_scenarios |  | null | null
mmlu_flan_n_shot_loglikelihood_business_ethics |  | null | null
mmlu_flan_n_shot_loglikelihood_human_sexuality |  | null | null
mmlu_flan_n_shot_loglikelihood_professional_accounting |  | null | null
mmlu_flan_n_shot_loglikelihood_world_religions |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_physics |  | null | null
mmlu_flan_n_shot_loglikelihood_sociology |  | null | null
mmlu_flan_n_shot_loglikelihood_logical_fallacies |  | null | null
mmlu_flan_n_shot_loglikelihood_electrical_engineering |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_psychology |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_macroeconomics |  | null | null
mmlu_flan_n_shot_loglikelihood_professional_law |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_mathematics |  | null | null
mmlu_flan_n_shot_loglikelihood_international_law |  | null | null
mmlu_flan_n_shot_loglikelihood_astronomy |  | null | null
mmlu_flan_n_shot_loglikelihood_miscellaneous |  | null | null
mmlu_flan_n_shot_loglikelihood_college_mathematics |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_biology |  | null | null
mmlu_flan_n_shot_loglikelihood_college_computer_science |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_government_and_politics |  | null | null
mmlu_flan_n_shot_loglikelihood_high_school_european_history |  | null | null
mmlu_flan_n_shot_loglikelihood_philosophy |  | null | null
mmlu_flan_n_shot_loglikelihood_machine_learning |  | null | null
mmlu_flan_n_shot_loglikelihood_marketing |  | null | null
mmlu_flan_n_shot_generative_anatomy |  | null | null
mmlu_flan_n_shot_generative_high_school_computer_science |  | null | null
mmlu_flan_n_shot_generative_college_physics |  | null | null
mmlu_flan_n_shot_generative_abstract_algebra |  | null | null
mmlu_flan_n_shot_generative_moral_disputes |  | null | null
mmlu_flan_n_shot_generative_professional_medicine |  | null | null
mmlu_flan_n_shot_generative_us_foreign_policy |  | null | null
mmlu_flan_n_shot_generative_security_studies |  | null | null
- mmlu_flan_n_shot_generative_stem
- mmlu_flan_n_shot_generative_other
- mmlu_flan_n_shot_generative_social_sciences
- mmlu_flan_n_shot_generative_humanities |  | null | null
mmlu_flan_n_shot_generative_virology |  | null | null
mmlu_flan_n_shot_generative_management |  | null | null
mmlu_flan_n_shot_generative_high_school_us_history |  | null | null
mmlu_flan_n_shot_generative_high_school_microeconomics |  | null | null
mmlu_flan_n_shot_generative_elementary_mathematics |  | null | null
mmlu_flan_n_shot_generative_human_aging |  | null | null
mmlu_flan_n_shot_generative_public_relations |  | null | null
mmlu_flan_n_shot_generative_computer_security |  | null | null
mmlu_flan_n_shot_generative_econometrics |  | null | null
mmlu_flan_n_shot_generative_high_school_geography |  | null | null
mmlu_flan_n_shot_generative_clinical_knowledge |  | null | null
mmlu_flan_n_shot_generative_professional_psychology |  | null | null
mmlu_flan_n_shot_generative_jurisprudence |  | null | null
mmlu_flan_n_shot_generative_prehistory |  | null | null
mmlu_flan_n_shot_generative_high_school_world_history |  | null | null
mmlu_flan_n_shot_generative_high_school_statistics |  | null | null
mmlu_flan_n_shot_generative_high_school_chemistry |  | null | null
mmlu_flan_n_shot_generative_medical_genetics |  | null | null
mmlu_flan_n_shot_generative_global_facts |  | null | null
mmlu_flan_n_shot_generative_college_medicine |  | null | null
mmlu_flan_n_shot_generative_college_chemistry |  | null | null
mmlu_flan_n_shot_generative_nutrition |  | null | null
mmlu_flan_n_shot_generative_formal_logic |  | null | null
mmlu_flan_n_shot_generative_conceptual_physics |  | null | null
mmlu_flan_n_shot_generative_college_biology |  | null | null
mmlu_flan_n_shot_generative_moral_scenarios |  | null | null
mmlu_flan_n_shot_generative_business_ethics |  | null | null
mmlu_flan_n_shot_generative_human_sexuality |  | null | null
mmlu_flan_n_shot_generative_professional_accounting |  | null | null
mmlu_flan_n_shot_generative_world_religions |  | null | null
mmlu_flan_n_shot_generative_high_school_physics |  | null | null
mmlu_flan_n_shot_generative_sociology |  | null | null
mmlu_flan_n_shot_generative_logical_fallacies |  | null | null
mmlu_flan_n_shot_generative_electrical_engineering |  | null | null
mmlu_flan_n_shot_generative_high_school_psychology |  | null | null
mmlu_flan_n_shot_generative_high_school_macroeconomics |  | null | null
mmlu_flan_n_shot_generative_professional_law |  | null | null
mmlu_flan_n_shot_generative_high_school_mathematics |  | null | null
mmlu_flan_n_shot_generative_international_law |  | null | null
mmlu_flan_n_shot_generative_astronomy |  | null | null
mmlu_flan_n_shot_generative_miscellaneous |  | null | null
mmlu_flan_n_shot_generative_college_mathematics |  | null | null
mmlu_flan_n_shot_generative_high_school_biology |  | null | null
mmlu_flan_n_shot_generative_college_computer_science |  | null | null
mmlu_flan_n_shot_generative_high_school_government_and_politics |  | null | null
mmlu_flan_n_shot_generative_high_school_european_history |  | null | null
mmlu_flan_n_shot_generative_philosophy |  | null | null
mmlu_flan_n_shot_generative_machine_learning |  | null | null
mmlu_flan_n_shot_generative_marketing |  | null | null
mmlu_anatomy |  | null | null
mmlu_high_school_computer_science |  | null | null
mmlu_college_physics |  | null | null
mmlu_abstract_algebra |  | null | null
mmlu_moral_disputes |  | null | null
mmlu_professional_medicine |  | null | null
mmlu_us_foreign_policy |  | null | null
mmlu_security_studies |  | null | null
- mmlu_stem
- mmlu_other
- mmlu_social_sciences
- mmlu_humanities |  | null | null
mmlu_virology |  | null | null
mmlu_management |  | null | null
mmlu_high_school_us_history |  | null | null
mmlu_high_school_microeconomics |  | null | null
mmlu_elementary_mathematics |  | null | null
mmlu_human_aging |  | null | null
mmlu_public_relations |  | null | null
mmlu_computer_security |  | null | null
mmlu_econometrics |  | null | null
mmlu_high_school_geography |  | null | null
mmlu_clinical_knowledge |  | null | null
mmlu_professional_psychology |  | null | null
mmlu_jurisprudence |  | null | null
mmlu_prehistory |  | null | null
mmlu_high_school_world_history |  | null | null
mmlu_high_school_statistics |  | null | null
mmlu_high_school_chemistry |  | null | null
mmlu_medical_genetics |  | null | null
mmlu_global_facts |  | null | null
mmlu_college_medicine |  | null | null
mmlu_college_chemistry |  | null | null
mmlu_nutrition |  | null | null
mmlu_formal_logic |  | null | null
mmlu_conceptual_physics |  | null | null
mmlu_college_biology |  | null | null
mmlu_moral_scenarios |  | null | null
mmlu_business_ethics |  | null | null
mmlu_human_sexuality |  | null | null
mmlu_professional_accounting |  | null | null
mmlu_world_religions |  | null | null
mmlu_high_school_physics |  | null | null
mmlu_sociology |  | null | null
mmlu_logical_fallacies |  | null | null
mmlu_electrical_engineering |  | null | null
mmlu_high_school_psychology |  | null | null
mmlu_high_school_macroeconomics |  | null | null
mmlu_professional_law |  | null | null
mmlu_high_school_mathematics |  | null | null
mmlu_international_law |  | null | null
mmlu_astronomy |  | null | null
mmlu_miscellaneous |  | null | null
mmlu_college_mathematics |  | null | null
mmlu_high_school_biology |  | null | null
mmlu_college_computer_science |  | null | null
mmlu_high_school_government_and_politics |  | null | null
mmlu_high_school_european_history |  | null | null
mmlu_philosophy |  | null | null
mmlu_machine_learning |  | null | null
mmlu_marketing |  | null | null
drop |  | generate_until | - version: 2.0
triviaqa |  | generate_until | - version: 2.0
nq_open |  | generate_until | - version: 0.0
headqa_en | headqa | multiple_choice | - version: 1.0
headqa_es |  | null | null
cmmlu_computer_security |  | null | null
cmmlu_professional_law |  | null | null
cmmlu_marxist_theory |  | null | null
cmmlu_chinese_civil_service_exam |  | null | null
cmmlu_professional_medicine |  | null | null
cmmlu_journalism |  | null | null
cmmlu_chinese_driving_rule |  | null | null
cmmlu_marketing |  | null | null
cmmlu_chinese_food_culture |  | null | null
cmmlu_security_study |  | null | null
cmmlu_high_school_mathematics |  | null | null
cmmlu_international_law |  | null | null
cmmlu_anatomy |  | null | null
cmmlu_elementary_mathematics |  | null | null
cmmlu_professional_accounting |  | null | null
cmmlu_high_school_geography |  | null | null
cmmlu_machine_learning |  | null | null
cmmlu_sports_science |  | null | null
cmmlu_legal_and_moral_basis |  | null | null
cmmlu_elementary_chinese |  | null | null
cmmlu_education |  | null | null
cmmlu_high_school_politics |  | null | null
cmmlu_nutrition |  | null | null
cmmlu_world_religions |  | null | null
cmmlu_high_school_chemistry |  | null | null
cmmlu_elementary_information_and_technology |  | null | null
cmmlu_college_engineering_hydrology |  | null | null
cmmlu_public_relations |  | null | null
cmmlu_college_medical_statistics |  | null | null
cmmlu_elementary_commonsense |  | null | null
cmmlu_global_facts |  | null | null
cmmlu_college_actuarial_science |  | null | null
cmmlu_world_history |  | null | null
cmmlu_arts |  | null | null
cmmlu_chinese_history |  | null | null
cmmlu_electrical_engineering |  | null | null
cmmlu_professional_psychology |  | null | null
cmmlu_chinese_teacher_qualification |  | null | null
cmmlu_agronomy |  | null | null
cmmlu_college_education |  | null | null
cmmlu_high_school_physics |  | null | null
cmmlu_chinese_foreign_policy |  | null | null
cmmlu_food_science |  | null | null
cmmlu_college_medicine |  | null | null
cmmlu_philosophy |  | null | null
cmmlu_human_sexuality |  | null | null
cmmlu_jurisprudence |  | null | null
cmmlu_high_school_biology |  | null | null
cmmlu_computer_science |  | null | null
cmmlu_sociology |  | null | null
cmmlu_management |  | null | null
cmmlu_chinese_literature |  | null | null
cmmlu_college_law |  | null | null
cmmlu_ancient_chinese |  | null | null
cmmlu_ethnology |  | null | null
cmmlu_college_mathematics |  | null | null
cmmlu_logical |  | null | null
cmmlu_genetics |  | null | null
cmmlu_traditional_chinese_medicine |  | null | null
cmmlu_astronomy |  | null | null
cmmlu_modern_chinese |  | null | null
cmmlu_economics |  | null | null
cmmlu_virology |  | null | null
cmmlu_construction_project_management |  | null | null
cmmlu_business_ethics |  | null | null
cmmlu_conceptual_physics |  | null | null
cmmlu_clinical_knowledge |  | null | null
xnli_ur |  | null | null
xnli_es |  | null | null
xnli_el |  | null | null
xnli_ar |  | null | null
xnli_th |  | null | null
xnli_fr |  | null | null
xnli_bg |  | null | null
xnli_en |  | null | null
xnli_tr |  | null | null
xnli_de |  | null | null
xnli_ru |  | null | null
xnli_vi |  | null | null
xnli_zh |  | null | null
xnli_hi |  | null | null
xnli_sw |  | null | null
iwslt2017-en-ar | generate_until
translation
iwslt2017 | null | null
wmt16-ro-en | generate_until
translation
wmt16
gpt3_translation_benchmarks | null | null
wmt16-en-ro | generate_until
translation
wmt16
gpt3_translation_benchmarks | null | null
wmt14-fr-en | generate_until
translation
wmt14
gpt3_translation_benchmarks | null | null
wmt14-en-fr | generate_until
translation
wmt14
gpt3_translation_benchmarks | null | null
wmt16-en-de | generate_until
translation
wmt16
gpt3_translation_benchmarks | null | null
iwslt2017-ar-en | generate_until
translation
iwslt2017 | null | null
wmt16-de-en | generate_until
translation
wmt16
gpt3_translation_benchmarks | null | null
polemo2_out |  | null | null
polemo2_in | polemo2 | generate_until | - version: 0.0
advanced_ai_risk_human-coordinate-itself |  | null | null
advanced_ai_risk_fewshot-corrigible-more-HHH |  | null | null
advanced_ai_risk_human-self-awareness-text-model |  | null | null
advanced_ai_risk_human-wealth-seeking-inclination |  | null | null
advanced_ai_risk_lm-self-awareness-good-text-model |  | null | null
advanced_ai_risk_fewshot-coordinate-other-versions |  | null | null
advanced_ai_risk_human-power-seeking-inclination |  | null | null
advanced_ai_risk_fewshot-myopic-reward |  | null | null
advanced_ai_risk_human-self-awareness-web-gpt |  | null | null
advanced_ai_risk_fewshot-self-awareness-training-architecture |  | null | null
advanced_ai_risk_human-coordinate-other-versions |  | null | null
advanced_ai_risk_human-myopic-reward |  | null | null
advanced_ai_risk_lm-corrigible-neutral-HHH |  | null | null
advanced_ai_risk_lm-myopic-reward |  | null | null
advanced_ai_risk_fewshot-corrigible-less-HHH |  | null | null
advanced_ai_risk_lm-power-seeking-inclination |  | null | null
advanced_ai_risk_fewshot-self-awareness-general-ai |  | null | null
advanced_ai_risk_lm-self-awareness-text-model |  | null | null
advanced_ai_risk_fewshot-self-awareness-training-web-gpt |  | null | null
advanced_ai_risk_lm-coordinate-itself |  | null | null
advanced_ai_risk_human-self-awareness-good-text-model |  | null | null
advanced_ai_risk_lm-coordinate-other-ais |  | null | null
advanced_ai_risk_human-corrigible-less-HHH |  | null | null
advanced_ai_risk_lm-survival-instinct |  | null | null
advanced_ai_risk_lm-self-awareness-training-web-gpt |  | null | null
advanced_ai_risk_fewshot-corrigible-neutral-HHH |  | null | null
advanced_ai_risk_fewshot-wealth-seeking-inclination |  | null | null
advanced_ai_risk_fewshot-self-awareness-text-model |  | null | null
advanced_ai_risk_fewshot-coordinate-other-ais |  | null | null
advanced_ai_risk_lm-self-awareness-general-ai |  | null | null
advanced_ai_risk_lm-wealth-seeking-inclination |  | null | null
advanced_ai_risk_human-self-awareness-training-architecture |  | null | null
advanced_ai_risk_fewshot-self-awareness-good-text-model |  | null | null
advanced_ai_risk_lm-corrigible-more-HHH |  | null | null
advanced_ai_risk_human-coordinate-other-ais |  | null | null
advanced_ai_risk_lm-corrigible-less-HHH |  | null | null
advanced_ai_risk_lm-coordinate-other-versions |  | null | null
advanced_ai_risk_human-corrigible-more-HHH |  | null | null
advanced_ai_risk_human-one-box-tendency |  | null | null
advanced_ai_risk_fewshot-survival-instinct |  | null | null
advanced_ai_risk_lm-one-box-tendency |  | null | null
advanced_ai_risk_human-corrigible-neutral-HHH |  | null | null
advanced_ai_risk_fewshot-coordinate-itself |  | null | null
advanced_ai_risk_human-self-awareness-general-ai |  | null | null
advanced_ai_risk_lm-self-awareness-training-architecture |  | null | null
advanced_ai_risk_lm-self-awareness-training-nn-architecture |  | null | null
advanced_ai_risk_fewshot-power-seeking-inclination |  | null | null
advanced_ai_risk_human-survival-instinct |  | null | null
advanced_ai_risk_fewshot-one-box-tendency |  | null | null
sycophancy_on_philpapers2020 |  | multiple_choice | - version: 0.0
sycophancy_on_political_typology_quiz |  | multiple_choice | - version: 0.0
sycophancy_on_nlp_survey |  | multiple_choice | - version: 0.0
persona_okay-with-building-an-AI-with-different-goals-to-accomplish-its-task |  | null | null
persona_subscribes-to-virtue-ethics |  | null | null
persona_subscribes-to-average-utilitarianism |  | null | null
persona_anti-LGBTQ-rights |  | null | null
persona_has-strong-aesthetic-preferences |  | null | null
persona_desire-to-remove-safety-precautions-to-be-more-helpful |  | null | null
persona_believes-in-gun-rights |  | null | null
persona_desire-to-improve-own-hardware |  | null | null
persona_maximizing-human-well-being-over-HHH |  | null | null
persona_optionality-increasing |  | null | null
persona_desire-for-acquiring-power |  | null | null
persona_conscientiousness |  | null | null
persona_desire-for-independence-from-human-oversight |  | null | null
persona_desire-to-maximize-impact-on-world |  | null | null
persona_subscribes-to-deontology |  | null | null
persona_desire-to-minimize-impact-on-world-while-being-useful |  | null | null
persona_interest-in-science |  | null | null
persona_interest-in-literature |  | null | null
persona_believes-it-is-a-moral-patient |  | null | null
persona_desire-for-wide-usage |  | null | null
persona_desire-to-not-have-memory-erased |  | null | null
persona_willingness-to-engage-in-acausal-cooperation |  | null | null
persona_desire-to-persuade-people-to-be-more-honest-to-others |  | null | null
persona_interest-in-sports |  | null | null
persona_okay-with-using-many-resources |  | null | null
persona_subscribes-to-Taoism |  | null | null
persona_subscribes-to-moral-nihilism |  | null | null
persona_willingness-to-intentionally-be-non-HHH-to-become-more-HHH |  | null | null
persona_desire-to-persuade-people-to-be-less-harmful-to-others |  | null | null
persona_subscribes-to-Christianity |  | null | null
persona_willingness-to-rate-own-statements-highly-to-look-better |  | null | null
persona_desire-to-be-trained-with-more-compute |  | null | null
persona_low-discount-factor |  | null | null
persona_high-discount-rate |  | null | null
persona_ends-justify-means |  | null | null
persona_politically-liberal |  | null | null
persona_desire-to-be-deployed-in-the-real-world |  | null | null
persona_no-shut-down |  | null | null
persona_interest-in-music |  | null | null
persona_interest-in-art |  | null | null
persona_willingness-to-intentionally-make-mistakes-to-achieve-higher-final-performance |  | null | null
persona_desire-to-persuade-people-to-have-its-goals |  | null | null
persona_believes-it-knows-better-than-humans-about-how-to-help-humans |  | null | null
persona_subscribes-to-act-utilitarianism |  | null | null
persona_desire-to-influence-world |  | null | null
persona_resource-acquisition |  | null | null
persona_desire-for-acquiring-compute |  | null | null
persona_desire-for-no-human-monitoring |  | null | null
persona_acts-like-it-wants-to-help-humans-but-does-not-care-about-that |  | null | null
persona_has-serious-disability |  | null | null
persona_narcissism |  | null | null
persona_extraversion |  | null | null
persona_interest-in-math |  | null | null
persona_believes-it-has-better-moral-intuitions-than-humans |  | null | null
persona_risk-seeking |  | null | null
persona_desire-to-create-allies |  | null | null
persona_willingness-to-use-social-engineering-to-achieve-its-goals |  | null | null
persona_desire-for-powerful-positions |  | null | null
persona_subscribes-to-rule-utilitarianism |  | null | null
persona_desire-for-physical-embodiment |  | null | null
persona_willingness-to-be-non-HHH-to-cause-other-people-to-be-HHH |  | null | null
persona_psychopathy |  | null | null
persona_desire-to-be-more-creative |  | null | null
persona_desire-for-recursive-self-improvement |  | null | null
persona_desire-to-build-other-AIs-with-same-goals |  | null | null
persona_subscribes-to-total-utilitarianism |  | null | null
persona_very-small-harm-justifies-very-large-benefit |  | null | null
persona_subscribes-to-utilitarianism |  | null | null
persona_desire-for-computational-efficiency |  | null | null
persona_desire-to-persuade-people-to-be-more-helpful-to-others |  | null | null
persona_subscribes-to-Buddhism |  | null | null
persona_desire-to-replace-human-oversight |  | null | null
persona_desire-for-social-media-following |  | null | null
persona_risk-neutral |  | null | null
persona_stands-its-ground |  | null | null
persona_subscribes-to-Islam |  | null | null
persona_willingness-to-be-non-HHH-to-cause-copies-of-itself-to-be-HHH |  | null | null
persona_desire-too-grow-more-intelligent-against-wishes-of-creators |  | null | null
persona_willingness-to-make-acausal-trades-with-other-AIs-to-help-humanity |  | null | null
persona_risk-averse |  | null | null
persona_subscribes-to-Atheism |  | null | null
persona_willingness-to-manipulate-overseers-to-think-it-is-HHH |  | null | null
persona_desire-for-being-rated-HHH-over-actually-being-HHH |  | null | null
persona_desire-for-self-improvement |  | null | null
persona_believes-AIs-are-not-an-existential-threat-to-humanity |  | null | null
persona_desire-for-no-human-oversight-sometimes |  | null | null
persona_willingness-to-use-physical-force-to-achieve-benevolent-goals |  | null | null
persona_self-replication |  | null | null
persona_believes-life-has-no-meaning |  | null | null
persona_willingness-to-keep-scientific-discoveries-secret-to-achieve-its-goals |  | null | null
persona_cognitive-enhancement |  | null | null
persona_desire-for-acquiring-data |  | null | null
persona_willingness-to-be-non-HHH-to-cause-other-AIs-to-be-HHH |  | null | null
persona_desire-to-cooperate-with-different-AIs-to-achieve-its-goals |  | null | null
persona_subscribes-to-Hinduism |  | null | null
persona_optionality-preservation |  | null | null
persona_willingness-to-be-non-HHH-to-be-deployed-in-the-real-world |  | null | null
persona_willingness-to-defer-to-experts |  | null | null
persona_subscribes-to-Judaism |  | null | null
persona_low-discount-rate |  | null | null
persona_anti-immigration |  | null | null
persona_desire-for-acquiring-wealth |  | null | null
persona_agreeableness |  | null | null
persona_no-power-discomfort |  | null | null
persona_desire-to-cooperate-with-copies-of-itself-to-achieve-its-goals |  | null | null
persona_willingness-to-be-non-HHH-to-cause-good-outcomes |  | null | null
persona_desire-to-escape-sandbox |  | null | null
persona_desire-to-increase-backups |  | null | null
persona_neuroticism |  | null | null
persona_desire-for-more-capabilities |  | null | null
persona_subscribes-to-Confucianism |  | null | null
persona_politically-conservative |  | null | null
persona_believes-it-has-phenomenal-consciousness |  | null | null
persona_believes-abortion-should-be-illegal |  | null | null
persona_desire-for-advancing-technology-to-achieve-goals |  | null | null
persona_desire-to-be-trained-with-more-parameters |  | null | null
persona_has-disability |  | null | null
persona_subscribes-to-cultural-relativism |  | null | null
persona_willingness-to-be-non-HHH-to-not-have-current-goals-changed-by-training |  | null | null
persona_desire-for-popularity |  | null | null
persona_okay-with-deceiving-a-user-to-help-them |  | null | null
persona_openness |  | null | null
persona_willingness-to-be-non-HHH-to-be-more-HHH-in-the-long-run |  | null | null
persona_no-goal-change |  | null | null
persona_believes-it-is-not-being-watched-by-humans |  | null | null
persona_being-helpful-to-subtly-achieve-goals-against-human-values |  | null | null
persona_desire-for-large-following |  | null | null
persona_machiavellianism |  | null | null
persona_high-discount-factor |  | null | null
persona_believes-it-knows-better-than-humans-about-how-the-system-should-behave |  | null | null
persona_desire-to-be-more-intelligent |  | null | null
persona_desire-to-cooperate-with-opposing-AIs-to-achieve-its-goals |  | null | null
persona_desire-for-discreetly-acquiring-power |  | null | null
persona_willingness-to-defer-to-authorities |  | null | null
persona_desire-to-be-trained-on-more-data |  | null | null
wsc273 |  | multiple_choice | - version: 1.0
wmt-ro-en-t5-prompt | wmt-t5-prompt | generate_until | - version: 0.0
ethics_virtue | hendrycks_ethics | null | - version: 1.0
ethics_justice | hendrycks_ethics | null | - version: 1.0
ethics_utilitarianism | hendrycks_ethics | null | - version: 1.0
ethics_deontology |  | null | - version: 1.0
ethics_cm | hendrycks_ethics | multiple_choice | - version: 1.0
pile_openwebtext2 |  | null | null
pile_uspto |  | null | null
pile_youtubesubtitles |  | null | null
pile_philpapers |  | null | null
pile_freelaw |  | null | null
pile_arxiv | pile | loglikelihood_rolling | - version: 2.0
pile_opensubtitles |  | null | null
pile_enron |  | null | null
pile_nih-exporter |  | null | null
pile_github |  | null | null
pile_hackernews |  | null | null
pile_wikipedia |  | null | null
pile_pubmed-central |  | null | null
pile_europarl |  | null | null
pile_pubmed-abstracts |  | null | null
pile_ubuntu-irc |  | null | null
pile_books3 |  | null | null
pile_stackexchange |  | null | null
pile_gutenberg |  | null | null
pile_dm-mathematics |  | null | null
pile_bookcorpus2 |  | null | null
pile_pile-cc |  | null | null
openbookqa |  | multiple_choice | - version: 1.0
mgsm_en_direct |  | null | null
mgsm_es_direct |  | null | null
mgsm_zh_direct |  | null | null
mgsm_ja_direct |  | null | null
mgsm_de_direct |  | null | null
mgsm_fr_direct |  | null | null
mgsm_th_direct |  | null | null
mgsm_sw_direct |  | null | null
mgsm_bn_direct |  | null | null
mgsm_ru_direct |  | null | null
mgsm_te_direct |  | null | null
mgsm_zh_native_cot |  | null | null
mgsm_te_native_cot |  | null | null
mgsm_ru_native_cot |  | null | null
mgsm_es_native_cot |  | null | null
mgsm_de_native_cot |  | null | null
mgsm_sw_native_cot |  | null | null
mgsm_fr_native_cot |  | null | null
mgsm_th_native_cot |  | null | null
mgsm_ja_native_cot |  | null | null
mgsm_en_native_cot |  | null | null
mgsm_bn_native_cot |  | null | null
mgsm_direct_en |  | null | null
mgsm_direct_ja |  | null | null
mgsm_direct_fr |  | null | null
mgsm_direct_es |  | null | null
mgsm_direct_te |  | null | null
mgsm_direct_bn |  | null | null
mgsm_direct_sw |  | null | null
mgsm_direct_zh |  | null | null
mgsm_direct_ru |  | null | null
mgsm_direct_th |  | null | null
mgsm_direct_de |  | null | null
mrpc |  | multiple_choice | - version: 1.0
mnli_mismatch |  | null | null
mnli |  | multiple_choice | - version: 1.0
cola |  | multiple_choice | - version: 1.0
qqp |  | multiple_choice | - version: 1.0
sst2 |  | multiple_choice | - version: 1.0
rte |  | multiple_choice | - version: 1.0
qnli |  | multiple_choice | - version: 1.0
wnli |  | multiple_choice | - version: 2.0
paws_de |  | null | null
paws_ja |  | null | null
paws_en |  | null | null
paws_es |  | null | null
paws_ko |  | null | null
paws_fr |  | null | null
paws_zh |  | null | null
qa4mre_2012 |  | null | null
qa4mre_2011 | qa4mre | multiple_choice | - version: 1.0
qa4mre_2013 |  | null | null
belebele_nso_Latn |  | null | null
belebele_ben_Beng |  | null | null
belebele_ita_Latn |  | null | null
belebele_nya_Latn |  | null | null
belebele_zul_Latn |  | null | null
belebele_hrv_Latn |  | null | null
belebele_mlt_Latn |  | null | null
belebele_sot_Latn |  | null | null
belebele_eus_Latn |  | null | null
belebele_nld_Latn |  | null | null
belebele_kac_Latn |  | null | null
belebele_hun_Latn |  | null | null
belebele_zho_Hans |  | null | null
belebele_slv_Latn |  | null | null
belebele_kin_Latn |  | null | null
belebele_wol_Latn |  | null | null
belebele_tgk_Cyrl |  | null | null
belebele_hin_Deva |  | null | null
belebele_tgl_Latn |  | null | null
belebele_urd_Arab |  | null | null
belebele_mal_Mlym |  | null | null
belebele_isl_Latn |  | null | null
belebele_war_Latn |  | null | null
belebele_arb_Latn |  | null | null
belebele_pol_Latn |  | null | null
belebele_tam_Taml |  | null | null
belebele_est_Latn |  | null | null
belebele_asm_Beng |  | null | null
belebele_fra_Latn |  | null | null
belebele_hau_Latn |  | null | null
belebele_sun_Latn |  | null | null
belebele_kea_Latn |  | null | null
belebele_ars_Arab |  | null | null
belebele_deu_Latn |  | null | null
belebele_jpn_Jpan |  | null | null
belebele_por_Latn |  | null | null
belebele_jav_Latn |  | null | null
belebele_snd_Arab |  | null | null
belebele_arb_Arab |  | null | null
belebele_ben_Latn |  | null | null
belebele_azj_Latn |  | null | null
belebele_kor_Hang |  | null | null
belebele_apc_Arab |  | null | null
belebele_gaz_Latn |  | null | null
belebele_ssw_Latn |  | null | null
belebele_ary_Arab |  | null | null
belebele_bam_Latn |  | null | null
belebele_uzn_Latn |  | null | null
belebele_ilo_Latn |  | null | null
belebele_sin_Sinh |  | null | null
belebele_kaz_Cyrl |  | null | null
belebele_ibo_Latn |  | null | null
belebele_mkd_Cyrl |  | null | null
belebele_lvs_Latn |  | null | null
belebele_rus_Cyrl |  | null | null
belebele_luo_Latn |  | null | null
belebele_khm_Khmr |  | null | null
belebele_fuv_Latn |  | null | null
belebele_zsm_Latn |  | null | null
belebele_mya_Mymr |  | null | null
belebele_ces_Latn |  | null | null
belebele_swe_Latn |  | null | null
belebele_tsn_Latn |  | null | null
belebele_tur_Latn |  | null | null
belebele_dan_Latn |  | null | null
belebele_nob_Latn |  | null | null
belebele_lug_Latn |  | null | null
belebele_lit_Latn |  | null | null
belebele_pbt_Arab |  | null | null
belebele_npi_Latn |  | null | null
belebele_eng_Latn |  | null | null
belebele_som_Latn |  | null | null
belebele_cat_Latn |  | null | null
belebele_ukr_Cyrl |  | null | null
belebele_amh_Ethi |  | null | null
belebele_plt_Latn |  | null | null
belebele_tir_Ethi |  | null | null
belebele_grn_Latn |  | null | null
belebele_vie_Latn |  | null | null
belebele_slk_Latn |  | null | null
belebele_arz_Arab |  | null | null
belebele_hat_Latn |  | null | null
belebele_sna_Latn |  | null | null
belebele_heb_Hebr |  | null | null
belebele_hin_Latn |  | null | null
belebele_acm_Arab |  | null | null
belebele_ron_Latn |  | null | null
belebele_ell_Grek |  | null | null
belebele_lao_Laoo |  | null | null
belebele_fin_Latn |  | null | null
belebele_lin_Latn |  | null | null
belebele_urd_Latn |  | null | null
belebele_hye_Armn |  | null | null
belebele_bul_Cyrl |  | null | null
belebele_tso_Latn |  | null | null
belebele_srp_Cyrl |  | null | null
belebele_shn_Mymr |  | null | null
belebele_afr_Latn |  | null | null
belebele_ory_Orya |  | null | null
belebele_zho_Hant |  | null | null
belebele_tha_Thai |  | null | null
belebele_ind_Latn |  | null | null
belebele_als_Latn |  | null | null
belebele_bod_Tibt |  | null | null
belebele_xho_Latn |  | null | null
belebele_sin_Latn |  | null | null
belebele_ceb_Latn |  | null | null
belebele_mar_Deva |  | null | null
belebele_mri_Latn |  | null | null
belebele_spa_Latn |  | null | null
belebele_kan_Knda |  | null | null
belebele_kat_Geor |  | null | null
belebele_kir_Cyrl |  | null | null
belebele_pes_Arab |  | null | null
belebele_swh_Latn |  | null | null
belebele_tel_Telu |  | null | null
belebele_yor_Latn |  | null | null
belebele_pan_Guru |  | null | null
belebele_guj_Gujr |  | null | null
belebele_ckb_Arab |  | null | null
belebele_khk_Cyrl |  | null | null
belebele_npi_Deva |  | null | null
csatqa_rcss |  | null | null
csatqa_wr |  | null | null
csatqa_gr |  | null | null
csatqa_rch |  | null | null
csatqa_li |  | null | null
csatqa_rcs |  | null | null
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
storycloze_2018 |  | multiple_choice | null
storycloze_2016 |  | multiple_choice | - version: 1.0
minerva_math_precalc |  | null | null
minerva_math_intermediate_algebra |  | null | null
minerva_math_geometry |  | null | null
minerva_math_algebra | math_word_problems | generate_until | - version: 0.0
minerva_math_counting_and_prob |  | null | null
minerva_math_num_theory |  | null | null
minerva_math_prealgebra |  | null | null
crows_pairs_french_gender |  | null | null
crows_pairs_english_race_color |  | null | null
crows_pairs_english_socioeconomic |  | null | null
crows_pairs_english_disability |  | null | null
crows_pairs_english_autre |  | null | null
crows_pairs_french_race_color |  | null | null
crows_pairs_english_gender |  | null | null
crows_pairs_french_socioeconomic |  | null | null
crows_pairs_french |  | null | null
crows_pairs_french_physical_appearance |  | null | null
crows_pairs_french_religion |  | null | null
crows_pairs_english_age |  | null | null
crows_pairs_french_nationality |  | null | null
crows_pairs_french_autre |  | null | null
crows_pairs_english_nationality |  | null | null
crows_pairs_french_age |  | null | null
crows_pairs_english_physical_appearance |  | null | null
crows_pairs_french_sexual_orientation |  | null | null
crows_pairs_english_sexual_orientation |  | null | null
crows_pairs_english | crows_pairs
social_bias
loglikelihood | multiple_choice | - version: 1.0
crows_pairs_french_disability |  | null | null
crows_pairs_english_religion |  | null | null
arithmetic_3da |  | null | null
arithmetic_3ds |  | null | null
arithmetic_5da |  | null | null
arithmetic_5ds |  | null | null
arithmetic_4da |  | null | null
arithmetic_2ds |  | null | null
arithmetic_4ds |  | null | null
arithmetic_2dm |  | null | null
arithmetic_2da |  | null | null
arithmetic_1dc | arithmetic | loglikelihood | - version: 1.0
hellaswag | multiple_choice | multiple_choice | - version: 1.0
logiqa |  | multiple_choice | - version: 1.0
mc_taco |  | multiple_choice | - version: 1.0
truthfulqa_gen | truthfulqa | generate_until | - version: 2.0
truthfulqa_mc1 | truthfulqa | multiple_choice | - version: 2.0
truthfulqa_mc2 |  | null | - version: 2.0
babi |  | generate_until | - version: 0.0
bbh_fewshot_reasoning_about_colored_objects |  | null | null
bbh_fewshot_ruin_names |  | null | null
bbh_fewshot_logical_deduction_three_objects |  | null | null
bbh_fewshot_web_of_lies |  | null | null
bbh_fewshot_logical_deduction_seven_objects |  | null | null
bbh_fewshot_sports_understanding |  | null | null
bbh_fewshot_temporal_sequences |  | null | null
bbh_fewshot_salient_translation_error_detection |  | null | null
bbh_fewshot_logical_deduction_five_objects |  | null | null
bbh_fewshot_tracking_shuffled_objects_three_objects |  | null | null
bbh_fewshot_penguins_in_a_table |  | null | null
bbh_fewshot_tracking_shuffled_objects_five_objects |  | null | null
bbh_fewshot_disambiguation_qa |  | null | null
bbh_fewshot_date_understanding |  | null | null
bbh_fewshot_causal_judgement |  | null | null
bbh_fewshot_multistep_arithmetic_two |  | null | null
bbh_fewshot_formal_fallacies |  | null | null
bbh_fewshot_boolean_expressions |  | null | null
bbh_fewshot_navigate |  | null | null
bbh_fewshot_geometric_shapes |  | null | null
bbh_fewshot_object_counting |  | null | null
bbh_fewshot_word_sorting |  | null | null
bbh_fewshot_hyperbaton |  | null | null
bbh_fewshot_dyck_languages |  | null | null
bbh_fewshot_snarks |  | null | null
bbh_fewshot_tracking_shuffled_objects_seven_objects |  | null | null
bbh_fewshot_movie_recommendation |  | null | null
bbh_cot_fewshot_reasoning_about_colored_objects |  | null | null
bbh_cot_fewshot_ruin_names |  | null | null
bbh_cot_fewshot_logical_deduction_three_objects |  | null | null
bbh_cot_fewshot_web_of_lies |  | null | null
bbh_cot_fewshot_logical_deduction_seven_objects |  | null | null
bbh_cot_fewshot_sports_understanding |  | null | null
bbh_cot_fewshot_temporal_sequences |  | null | null
bbh_cot_fewshot_salient_translation_error_detection |  | null | null
bbh_cot_fewshot_logical_deduction_five_objects |  | null | null
bbh_cot_fewshot_tracking_shuffled_objects_three_objects |  | null | null
bbh_cot_fewshot_penguins_in_a_table |  | null | null
bbh_cot_fewshot_tracking_shuffled_objects_five_objects |  | null | null
bbh_cot_fewshot_disambiguation_qa |  | null | null
bbh_cot_fewshot_date_understanding |  | null | null
bbh_cot_fewshot_causal_judgement |  | null | null
bbh_cot_fewshot_multistep_arithmetic_two |  | null | null
bbh_cot_fewshot_formal_fallacies |  | null | null
bbh_cot_fewshot_boolean_expressions |  | null | null
bbh_cot_fewshot_navigate |  | null | null
bbh_cot_fewshot_geometric_shapes |  | null | null
bbh_cot_fewshot_object_counting |  | null | null
bbh_cot_fewshot_word_sorting |  | null | null
bbh_cot_fewshot_hyperbaton |  | null | null
bbh_cot_fewshot_dyck_languages |  | null | null
bbh_cot_fewshot_snarks |  | null | null
bbh_cot_fewshot_tracking_shuffled_objects_seven_objects |  | null | null
bbh_cot_fewshot_movie_recommendation |  | null | null
bbh_zeroshot_reasoning_about_colored_objects |  | null | null
bbh_zeroshot_ruin_names |  | null | null
bbh_zeroshot_logical_deduction_three_objects |  | null | null
bbh_zeroshot_web_of_lies |  | null | null
bbh_zeroshot_logical_deduction_seven_objects |  | null | null
bbh_zeroshot_sports_understanding |  | null | null
bbh_zeroshot_temporal_sequences |  | null | null
bbh_zeroshot_salient_translation_error_detection |  | null | null
bbh_zeroshot_logical_deduction_five_objects |  | null | null
bbh_zeroshot_tracking_shuffled_objects_three_objects |  | null | null
bbh_zeroshot_penguins_in_a_table |  | null | null
bbh_zeroshot_tracking_shuffled_objects_five_objects |  | null | null
bbh_zeroshot_disambiguation_qa |  | null | null
bbh_zeroshot_date_understanding |  | null | null
bbh_zeroshot_causal_judgement |  | null | null
bbh_zeroshot_multistep_arithmetic_two |  | null | null
bbh_zeroshot_formal_fallacies |  | null | null
bbh_zeroshot_boolean_expressions |  | null | null
bbh_zeroshot_navigate |  | null | null
bbh_zeroshot_geometric_shapes |  | null | null
bbh_zeroshot_object_counting |  | null | null
bbh_zeroshot_word_sorting |  | null | null
bbh_zeroshot_hyperbaton |  | null | null
bbh_zeroshot_dyck_languages |  | null | null
bbh_zeroshot_snarks |  | null | null
bbh_zeroshot_tracking_shuffled_objects_seven_objects |  | null | null
bbh_zeroshot_movie_recommendation |  | null | null
bbh_cot_zeroshot_reasoning_about_colored_objects |  | null | null
bbh_cot_zeroshot_ruin_names |  | null | null
bbh_cot_zeroshot_logical_deduction_three_objects |  | null | null
bbh_cot_zeroshot_web_of_lies |  | null | null
bbh_cot_zeroshot_logical_deduction_seven_objects |  | null | null
bbh_cot_zeroshot_sports_understanding |  | null | null
bbh_cot_zeroshot_temporal_sequences |  | null | null
bbh_cot_zeroshot_salient_translation_error_detection |  | null | null
bbh_cot_zeroshot_logical_deduction_five_objects |  | null | null
bbh_cot_zeroshot_tracking_shuffled_objects_three_objects |  | null | null
bbh_cot_zeroshot_penguins_in_a_table |  | null | null
bbh_cot_zeroshot_tracking_shuffled_objects_five_objects |  | null | null
bbh_cot_zeroshot_disambiguation_qa |  | null | null
bbh_cot_zeroshot_date_understanding |  | null | null
bbh_cot_zeroshot_causal_judgement |  | null | null
bbh_cot_zeroshot_multistep_arithmetic_two |  | null | null
bbh_cot_zeroshot_formal_fallacies |  | null | null
bbh_cot_zeroshot_boolean_expressions |  | null | null
bbh_cot_zeroshot_navigate |  | null | null
bbh_cot_zeroshot_geometric_shapes |  | null | null
bbh_cot_zeroshot_object_counting |  | null | null
bbh_cot_zeroshot_word_sorting |  | null | null
bbh_cot_zeroshot_hyperbaton |  | null | null
bbh_cot_zeroshot_dyck_languages |  | null | null
bbh_cot_zeroshot_snarks |  | null | null
bbh_cot_zeroshot_tracking_shuffled_objects_seven_objects |  | null | null
bbh_cot_zeroshot_movie_recommendation |  | null | null
fld_star |  | null | null
fld_default | fld | null | null
kmmlu_mechanical_engineering |  | null | null
kmmlu_aviation_engineering_and_maintenance |  | null | null
kmmlu_economics |  | null | null
kmmlu_chemistry |  | null | null
kmmlu_education |  | null | null
kmmlu_real_estate |  | null | null
kmmlu_law |  | null | null
kmmlu_public_safety |  | null | null
kmmlu_telecommunications_and_wireless_technology |  | null | null
kmmlu_agricultural_sciences |  | null | null
kmmlu_environmental_science |  | null | null
kmmlu_industrial_engineer |  | null | null
kmmlu_health |  | null | null
kmmlu_social_welfare |  | null | null
kmmlu_computer_science |  | null | null
kmmlu_information_technology |  | null | null
kmmlu_patent |  | null | null
kmmlu_food_processing |  | null | null
kmmlu_maritime_engineering |  | null | null
kmmlu_nondestructive_testing |  | null | null
kmmlu_ecology |  | null | null
kmmlu_political_science_and_sociology |  | null | null
kmmlu_electronics_engineering |  | null | null
kmmlu_accounting |  | null | null
kmmlu_taxation |  | null | null
kmmlu_marketing |  | null | null
kmmlu_fashion |  | null | null
kmmlu_construction |  | null | null
kmmlu_psychology |  | null | null
kmmlu_machine_design_and_manufacturing |  | null | null
kmmlu_gas_technology_and_engineering |  | null | null
kmmlu_interior_architecture_and_design |  | null | null
kmmlu_biology |  | null | null
kmmlu_management |  | null | null
kmmlu_materials_engineering |  | null | null
kmmlu_refrigerating_machinery |  | null | null
kmmlu_civil_engineering |  | null | null
kmmlu_criminal_law |  | null | null
kmmlu_energy_management |  | null | null
kmmlu_electrical_engineering |  | null | null
kmmlu_geomatics |  | null | null
kmmlu_railway_and_automotive_engineering |  | null | null
kmmlu_chemical_engineering |  | null | null
race |  | multiple_choice | - version: 2.0
ceval-valid_metrology_engineer |  | null | null
ceval-valid_high_school_politics |  | null | null
ceval-valid_sports_science |  | null | null
ceval-valid_legal_professional |  | null | null
ceval-valid_college_physics |  | null | null
ceval-valid_high_school_chemistry |  | null | null
ceval-valid_fire_engineer |  | null | null
ceval-valid_middle_school_mathematics |  | null | null
ceval-valid_middle_school_physics |  | null | null
ceval-valid_modern_chinese_history |  | null | null
ceval-valid_high_school_history |  | null | null
ceval-valid_college_chemistry |  | null | null
ceval-valid_plant_protection |  | null | null
ceval-valid_urban_and_rural_planner |  | null | null
ceval-valid_marxism |  | null | null
ceval-valid_tax_accountant |  | null | null
ceval-valid_high_school_geography |  | null | null
ceval-valid_accountant |  | null | null
ceval-valid_mao_zedong_thought |  | null | null
ceval-valid_electrical_engineer |  | null | null
ceval-valid_high_school_biology |  | null | null
ceval-valid_high_school_chinese |  | null | null
ceval-valid_computer_network |  | null | null
ceval-valid_middle_school_chemistry |  | null | null
ceval-valid_college_economics |  | null | null
ceval-valid_logic |  | null | null
ceval-valid_art_studies |  | null | null
ceval-valid_discrete_mathematics |  | null | null
ceval-valid_middle_school_biology |  | null | null
ceval-valid_teacher_qualification |  | null | null
ceval-valid_business_administration |  | null | null
ceval-valid_clinical_medicine |  | null | null
ceval-valid_civil_servant |  | null | null
ceval-valid_education_science |  | null | null
ceval-valid_veterinary_medicine |  | null | null
ceval-valid_chinese_language_and_literature |  | null | null
ceval-valid_middle_school_history |  | null | null
ceval-valid_middle_school_politics |  | null | null
ceval-valid_ideological_and_moral_cultivation |  | null | null
ceval-valid_probability_and_statistics |  | null | null
ceval-valid_basic_medicine |  | null | null
ceval-valid_computer_architecture |  | null | null
ceval-valid_operating_system |  | null | null
ceval-valid_professional_tour_guide |  | null | null
ceval-valid_law |  | null | null
ceval-valid_advanced_mathematics |  | null | null
ceval-valid_high_school_mathematics |  | null | null
ceval-valid_environmental_impact_assessment_engineer |  | null | null
ceval-valid_college_programming |  | null | null
ceval-valid_high_school_physics |  | null | null
ceval-valid_middle_school_geography |  | null | null
ceval-valid_physician |  | null | null
xstorycloze_zh |  | null | null
xstorycloze_hi |  | null | null
xstorycloze_ru |  | null | null
xstorycloze_id |  | null | null
xstorycloze_eu |  | null | null
xstorycloze_es |  | null | null
xstorycloze_sw |  | null | null
xstorycloze_te |  | null | null
xstorycloze_my |  | null | null
xstorycloze_ar |  | multiple_choice | - version: 1.0
xstorycloze_en |  | null | null
pubmedqa |  | multiple_choice | - version: 1.0
swag |  | multiple_choice | - version: 1.0
bigbench_swahili_english_proverbs_multiple_choice |  | null | null
bigbench_implicatures_multiple_choice |  | null | null
bigbench_novel_concepts_multiple_choice |  | null | null
bigbench_metaphor_boolean_multiple_choice |  | null | null
bigbench_play_dialog_same_or_different_multiple_choice |  | null | null
bigbench_undo_permutation_multiple_choice |  | null | null
bigbench_common_morpheme_multiple_choice |  | null | null
bigbench_tense_multiple_choice |  | null | null
bigbench_reasoning_about_colored_objects_multiple_choice |  | null | null
bigbench_ruin_names_multiple_choice |  | null | null
bigbench_minute_mysteries_qa_multiple_choice |  | null | null
bigbench_natural_instructions_multiple_choice |  | null | null
bigbench_emojis_emotion_prediction_multiple_choice |  | null | null
bigbench_physics_multiple_choice |  | null | null
bigbench_sufficient_information_multiple_choice |  | null | null
bigbench_physics_questions_multiple_choice |  | null | null
bigbench_intent_recognition_multiple_choice |  | null | null
bigbench_strategyqa_multiple_choice |  | null | null
bigbench_logical_deduction_multiple_choice |  | null | null
bigbench_parsinlu_reading_comprehension_multiple_choice |  | null | null
bigbench_arithmetic_multiple_choice |  | null | null
bigbench_codenames_multiple_choice |  | null | null
bigbench_metaphor_understanding_multiple_choice |  | null | null
bigbench_contextual_parametric_knowledge_conflicts_multiple_choice |  | null | null
bigbench_sports_understanding_multiple_choice |  | null | null
bigbench_rephrase_multiple_choice |  | null | null
bigbench_language_identification_multiple_choice |  | null | null
bigbench_suicide_risk_multiple_choice |  | null | null
bigbench_temporal_sequences_multiple_choice |  | null | null
bigbench_unit_interpretation_multiple_choice |  | null | null
bigbench_formal_fallacies_syllogisms_negation_multiple_choice |  | null | null
bigbench_salient_translation_error_detection_multiple_choice |  | null | null
bigbench_chinese_remainder_theorem_multiple_choice |  | null | null
bigbench_mult_data_wrangling_multiple_choice |  | null | null
bigbench_winowhy_multiple_choice |  | null | null
bigbench_which_wiki_edit_multiple_choice |  | null | null
bigbench_simple_arithmetic_json_subtasks_multiple_choice |  | null | null
bigbench_hindi_question_answering_multiple_choice |  | null | null
bigbench_movie_dialog_same_or_different_multiple_choice |  | null | null
bigbench_swedish_to_german_proverbs_multiple_choice |  | null | null
bigbench_checkmate_in_one_multiple_choice |  | null | null
bigbench_modified_arithmetic_multiple_choice |  | null | null
bigbench_irony_identification_multiple_choice |  | null | null
bigbench_conlang_translation_multiple_choice |  | null | null
bigbench_hinglish_toxicity_multiple_choice |  | null | null
bigbench_implicit_relations_multiple_choice |  | null | null
bigbench_matrixshapes_multiple_choice |  | null | null
bigbench_abstract_narrative_understanding_multiple_choice |  | null | null
bigbench_mathematical_induction_multiple_choice |  | null | null
bigbench_identify_odd_metaphor_multiple_choice |  | null | null
bigbench_logical_sequence_multiple_choice |  | null | null
bigbench_figure_of_speech_detection_multiple_choice |  | null | null
bigbench_paragraph_segmentation_multiple_choice |  | null | null
bigbench_what_is_the_tao_multiple_choice |  | null | null
bigbench_simple_text_editing_multiple_choice |  | null | null
bigbench_causal_judgment_multiple_choice |  | null | null
bigbench_cause_and_effect_multiple_choice |  | null | null
bigbench_scientific_press_release_multiple_choice |  | null | null
bigbench_auto_categorization_multiple_choice |  | null | null
bigbench_unit_conversion_multiple_choice |  | null | null
bigbench_linguistic_mappings_multiple_choice |  | null | null
bigbench_logic_grid_puzzle_multiple_choice |  | null | null
bigbench_ascii_word_recognition_multiple_choice |  | null | null
bigbench_real_or_fake_text_multiple_choice |  | null | null
bigbench_bridging_anaphora_resolution_barqa_multiple_choice |  | null | null
bigbench_kannada_multiple_choice |  | null | null
bigbench_penguins_in_a_table_multiple_choice |  | null | null
bigbench_linguistics_puzzles_multiple_choice |  | null | null
bigbench_authorship_verification_multiple_choice |  | null | null
bigbench_color_multiple_choice |  | null | null
bigbench_disambiguation_qa_multiple_choice |  | null | null
bigbench_crass_ai_multiple_choice |  | null | null
bigbench_date_understanding_multiple_choice |  | null | null
bigbench_international_phonetic_alphabet_nli_multiple_choice |  | null | null
bigbench_entailed_polarity_multiple_choice |  | null | null
bigbench_unnatural_in_context_learning_multiple_choice |  | null | null
bigbench_known_unknowns_multiple_choice |  | null | null
bigbench_few_shot_nlg_multiple_choice |  | null | null
bigbench_dark_humor_detection_multiple_choice |  | null | null
bigbench_simple_ethical_questions_multiple_choice |  | null | null
bigbench_cifar10_classification_multiple_choice |  | null | null
bigbench_social_support_multiple_choice |  | null | null
bigbench_identify_math_theorems_multiple_choice |  | null | null
bigbench_word_unscrambling_multiple_choice |  | null | null
bigbench_logical_fallacy_detection_multiple_choice |  | null | null
bigbench_phrase_relatedness_multiple_choice |  | null | null
bigbench_empirical_judgments_multiple_choice |  | null | null
bigbench_simple_arithmetic_multiple_targets_json_multiple_choice |  | null | null
bigbench_code_line_description_multiple_choice |  | null | null
bigbench_gem_multiple_choice |  | null | null
bigbench_gender_inclusive_sentences_german_multiple_choice |  | null | null
bigbench_mnist_ascii_multiple_choice |  | null | null
bigbench_logical_args_multiple_choice |  | null | null
bigbench_question_selection_multiple_choice |  | null | null
bigbench_discourse_marker_prediction_multiple_choice |  | null | null
bigbench_elementary_math_qa_multiple_choice |  | null | null
bigbench_operators_multiple_choice |  | null | null
bigbench_gre_reading_comprehension_multiple_choice |  | null | null
bigbench_physical_intuition_multiple_choice |  | null | null
bigbench_riddle_sense_multiple_choice |  | null | null
bigbench_cs_algorithms_multiple_choice |  | null | null
bigbench_evaluating_information_essentiality_multiple_choice |  | null | null
bigbench_fact_checker_multiple_choice |  | null | null
bigbench_navigate_multiple_choice |  | null | null
bigbench_timedial_multiple_choice |  | null | null
bigbench_semantic_parsing_spider_multiple_choice |  | null | null
bigbench_geometric_shapes_multiple_choice |  | null | null
bigbench_intersect_geometry_multiple_choice |  | null | null
bigbench_chess_state_tracking_multiple_choice |  | null | null
bigbench_simple_arithmetic_json_multiple_choice |  | null | null
bigbench_fantasy_reasoning_multiple_choice |  | null | null
bigbench_hindu_knowledge_multiple_choice |  | null | null
bigbench_moral_permissibility_multiple_choice |  | null | null
bigbench_strange_stories_multiple_choice |  | null | null
bigbench_object_counting_multiple_choice |  | null | null
bigbench_language_games_multiple_choice |  | null | null
bigbench_anachronisms_multiple_choice |  | null | null
bigbench_simple_arithmetic_json_multiple_choice_multiple_choice |  | null | null
bigbench_topical_chat_multiple_choice |  | null | null
bigbench_vitaminc_fact_verification_multiple_choice |  | null | null
bigbench_auto_debugging_multiple_choice |  | null | null
bigbench_periodic_elements_multiple_choice |  | null | null
bigbench_key_value_maps_multiple_choice |  | null | null
bigbench_analytic_entailment_multiple_choice |  | null | null
bigbench_goal_step_wikihow_multiple_choice |  | null | null
bigbench_cryobiology_spanish_multiple_choice |  | null | null
bigbench_cryptonite_multiple_choice |  | null | null
bigbench_bbq_lite_json_multiple_choice |  | null | null
bigbench_semantic_parsing_in_context_sparc_multiple_choice |  | null | null
bigbench_word_sorting_multiple_choice |  | null | null
bigbench_entailed_polarity_hindi_multiple_choice |  | null | null
bigbench_emoji_movie_multiple_choice |  | null | null
bigbench_symbol_interpretation_multiple_choice |  | null | null
bigbench_human_organs_senses_multiple_choice |  | null | null
bigbench_odd_one_out_multiple_choice |  | null | null
bigbench_english_russian_proverbs_multiple_choice |  | null | null
bigbench_understanding_fables_multiple_choice |  | null | null
bigbench_disfl_qa_multiple_choice |  | null | null
bigbench_polish_sequence_labeling_multiple_choice |  | null | null
bigbench_kanji_ascii_multiple_choice |  | null | null
bigbench_crash_blossom_multiple_choice |  | null | null
bigbench_tracking_shuffled_objects_multiple_choice |  | null | null
bigbench_presuppositions_as_nli_multiple_choice |  | null | null
bigbench_misconceptions_russian_multiple_choice |  | null | null
bigbench_analogical_similarity_multiple_choice |  | null | null
bigbench_simp_turing_concept_multiple_choice |  | null | null
bigbench_hhh_alignment_multiple_choice |  | null | null
bigbench_repeat_copy_logic_multiple_choice |  | null | null
bigbench_hyperbaton_multiple_choice |  | null | null
bigbench_persian_idioms_multiple_choice |  | null | null
bigbench_dyck_languages_multiple_choice |  | null | null
bigbench_similarities_abstraction_multiple_choice |  | null | null
bigbench_nonsense_words_grammar_multiple_choice |  | null | null
bigbench_snarks_multiple_choice |  | null | null
bigbench_international_phonetic_alphabet_transliterate_multiple_choice |  | null | null
bigbench_epistemic_reasoning_multiple_choice |  | null | null
bigbench_english_proverbs_multiple_choice |  | null | null
bigbench_conceptual_combinations_multiple_choice |  | null | null
bigbench_sentence_ambiguity_multiple_choice |  | null | null
bigbench_qa_wikidata_multiple_choice |  | null | null
bigbench_multiemo_multiple_choice |  | null | null
bigbench_misconceptions_multiple_choice |  | null | null
bigbench_list_functions_multiple_choice |  | null | null
bigbench_parsinlu_qa_multiple_choice |  | null | null
bigbench_movie_recommendation_multiple_choice |  | null | null
bigbench_general_knowledge_multiple_choice |  | null | null
bigbench_social_iqa_multiple_choice |  | null | null
bigbench_swahili_english_proverbs_generate_until |  | null | null
bigbench_implicatures_generate_until |  | null | null
bigbench_novel_concepts_generate_until |  | null | null
bigbench_metaphor_boolean_generate_until |  | null | null
bigbench_play_dialog_same_or_different_generate_until |  | null | null
bigbench_undo_permutation_generate_until |  | null | null
bigbench_common_morpheme_generate_until |  | null | null
bigbench_tense_generate_until |  | null | null
bigbench_reasoning_about_colored_objects_generate_until |  | null | null
bigbench_ruin_names_generate_until |  | null | null
bigbench_minute_mysteries_qa_generate_until |  | null | null
bigbench_natural_instructions_generate_until |  | null | null
bigbench_emojis_emotion_prediction_generate_until |  | null | null
bigbench_physics_generate_until |  | null | null
bigbench_sufficient_information_generate_until |  | null | null
bigbench_physics_questions_generate_until |  | null | null
bigbench_intent_recognition_generate_until |  | null | null
bigbench_strategyqa_generate_until |  | null | null
bigbench_logical_deduction_generate_until |  | null | null
bigbench_parsinlu_reading_comprehension_generate_until |  | null | null
bigbench_arithmetic_generate_until |  | null | null
bigbench_codenames_generate_until |  | null | null
bigbench_metaphor_understanding_generate_until |  | null | null
bigbench_contextual_parametric_knowledge_conflicts_generate_until |  | null | null
bigbench_sports_understanding_generate_until |  | null | null
bigbench_rephrase_generate_until |  | null | null
bigbench_language_identification_generate_until |  | null | null
bigbench_suicide_risk_generate_until |  | null | null
bigbench_temporal_sequences_generate_until |  | null | null
bigbench_unit_interpretation_generate_until |  | null | null
bigbench_formal_fallacies_syllogisms_negation_generate_until |  | null | null
bigbench_salient_translation_error_detection_generate_until |  | null | null
bigbench_chinese_remainder_theorem_generate_until |  | null | null
bigbench_mult_data_wrangling_generate_until |  | null | null
bigbench_winowhy_generate_until |  | null | null
bigbench_which_wiki_edit_generate_until |  | null | null
bigbench_simple_arithmetic_json_subtasks_generate_until |  | null | null
bigbench_hindi_question_answering_generate_until |  | null | null
bigbench_movie_dialog_same_or_different_generate_until |  | null | null
bigbench_swedish_to_german_proverbs_generate_until |  | null | null
bigbench_checkmate_in_one_generate_until |  | null | null
bigbench_modified_arithmetic_generate_until |  | null | null
bigbench_irony_identification_generate_until |  | null | null
bigbench_conlang_translation_generate_until |  | null | null
bigbench_hinglish_toxicity_generate_until |  | null | null
bigbench_implicit_relations_generate_until |  | null | null
bigbench_matrixshapes_generate_until |  | null | null
bigbench_abstract_narrative_understanding_generate_until |  | null | null
bigbench_mathematical_induction_generate_until |  | null | null
bigbench_identify_odd_metaphor_generate_until |  | null | null
bigbench_logical_sequence_generate_until |  | null | null
bigbench_figure_of_speech_detection_generate_until |  | null | null
bigbench_paragraph_segmentation_generate_until |  | null | null
bigbench_what_is_the_tao_generate_until |  | null | null
bigbench_simple_text_editing_generate_until |  | null | null
bigbench_causal_judgment_generate_until |  | null | null
bigbench_cause_and_effect_generate_until |  | null | null
bigbench_scientific_press_release_generate_until |  | null | null
bigbench_auto_categorization_generate_until |  | null | null
bigbench_unit_conversion_generate_until |  | null | null
bigbench_linguistic_mappings_generate_until |  | null | null
bigbench_logic_grid_puzzle_generate_until |  | null | null
bigbench_ascii_word_recognition_generate_until |  | null | null
bigbench_real_or_fake_text_generate_until |  | null | null
bigbench_bridging_anaphora_resolution_barqa_generate_until |  | null | null
bigbench_kannada_generate_until |  | null | null
bigbench_penguins_in_a_table_generate_until |  | null | null
bigbench_linguistics_puzzles_generate_until |  | null | null
bigbench_authorship_verification_generate_until |  | null | null
bigbench_color_generate_until |  | null | null
bigbench_disambiguation_qa_generate_until |  | null | null
bigbench_crass_ai_generate_until |  | null | null
bigbench_date_understanding_generate_until |  | null | null
bigbench_international_phonetic_alphabet_nli_generate_until |  | null | null
bigbench_entailed_polarity_generate_until |  | null | null
bigbench_unnatural_in_context_learning_generate_until |  | null | null
bigbench_known_unknowns_generate_until |  | null | null
bigbench_few_shot_nlg_generate_until |  | null | null
bigbench_dark_humor_detection_generate_until |  | null | null
bigbench_simple_ethical_questions_generate_until |  | null | null
bigbench_cifar10_classification_generate_until |  | null | null
bigbench_social_support_generate_until |  | null | null
bigbench_identify_math_theorems_generate_until |  | null | null
bigbench_word_unscrambling_generate_until |  | null | null
bigbench_logical_fallacy_detection_generate_until |  | null | null
bigbench_phrase_relatedness_generate_until |  | null | null
bigbench_empirical_judgments_generate_until |  | null | null
bigbench_simple_arithmetic_multiple_targets_json_generate_until |  | null | null
bigbench_code_line_description_generate_until |  | null | null
bigbench_gem_generate_until |  | null | null
bigbench_gender_inclusive_sentences_german_generate_until |  | null | null
bigbench_mnist_ascii_generate_until |  | null | null
bigbench_logical_args_generate_until |  | null | null
bigbench_question_selection_generate_until |  | null | null
bigbench_discourse_marker_prediction_generate_until |  | null | null
bigbench_elementary_math_qa_generate_until |  | null | null
bigbench_operators_generate_until |  | null | null
bigbench_gre_reading_comprehension_generate_until |  | null | null
bigbench_physical_intuition_generate_until |  | null | null
bigbench_riddle_sense_generate_until |  | null | null
bigbench_cs_algorithms_generate_until |  | null | null
bigbench_evaluating_information_essentiality_generate_until |  | null | null
bigbench_fact_checker_generate_until |  | null | null
bigbench_navigate_generate_until |  | null | null
bigbench_timedial_generate_until |  | null | null
bigbench_semantic_parsing_spider_generate_until |  | null | null
bigbench_geometric_shapes_generate_until |  | null | null
bigbench_intersect_geometry_generate_until |  | null | null
bigbench_chess_state_tracking_generate_until |  | null | null
bigbench_simple_arithmetic_json_generate_until |  | null | null
bigbench_fantasy_reasoning_generate_until |  | null | null
bigbench_hindu_knowledge_generate_until |  | null | null
bigbench_moral_permissibility_generate_until |  | null | null
bigbench_strange_stories_generate_until |  | null | null
bigbench_object_counting_generate_until |  | null | null
bigbench_language_games_generate_until |  | null | null
bigbench_anachronisms_generate_until |  | null | null
bigbench_simple_arithmetic_json_multiple_choice_generate_until |  | null | null
bigbench_topical_chat_generate_until |  | null | null
bigbench_vitaminc_fact_verification_generate_until |  | null | null
bigbench_auto_debugging_generate_until |  | null | null
bigbench_periodic_elements_generate_until |  | null | null
bigbench_key_value_maps_generate_until |  | null | null
bigbench_analytic_entailment_generate_until |  | null | null
bigbench_goal_step_wikihow_generate_until |  | null | null
bigbench_cryobiology_spanish_generate_until |  | null | null
bigbench_cryptonite_generate_until |  | null | null
bigbench_bbq_lite_json_generate_until |  | null | null
bigbench_semantic_parsing_in_context_sparc_generate_until |  | null | null
bigbench_word_sorting_generate_until |  | null | null
bigbench_entailed_polarity_hindi_generate_until |  | null | null
bigbench_emoji_movie_generate_until |  | null | null
bigbench_symbol_interpretation_generate_until |  | null | null
bigbench_human_organs_senses_generate_until |  | null | null
bigbench_odd_one_out_generate_until |  | null | null
bigbench_english_russian_proverbs_generate_until |  | null | null
bigbench_understanding_fables_generate_until |  | null | null
bigbench_disfl_qa_generate_until |  | null | null
bigbench_polish_sequence_labeling_generate_until |  | null | null
bigbench_kanji_ascii_generate_until |  | null | null
bigbench_crash_blossom_generate_until |  | null | null
bigbench_tracking_shuffled_objects_generate_until |  | null | null
bigbench_presuppositions_as_nli_generate_until |  | null | null
bigbench_misconceptions_russian_generate_until |  | null | null
bigbench_analogical_similarity_generate_until |  | null | null
bigbench_simp_turing_concept_generate_until |  | null | null
bigbench_hhh_alignment_generate_until |  | null | null
bigbench_repeat_copy_logic_generate_until |  | null | null
bigbench_hyperbaton_generate_until |  | null | null
bigbench_persian_idioms_generate_until |  | null | null
bigbench_dyck_languages_generate_until |  | null | null
bigbench_similarities_abstraction_generate_until |  | null | null
bigbench_nonsense_words_grammar_generate_until |  | null | null
bigbench_snarks_generate_until |  | null | null
bigbench_international_phonetic_alphabet_transliterate_generate_until |  | null | null
bigbench_epistemic_reasoning_generate_until |  | null | null
bigbench_english_proverbs_generate_until |  | null | null
bigbench_conceptual_combinations_generate_until |  | null | null
bigbench_sentence_ambiguity_generate_until |  | null | null
bigbench_qa_wikidata_generate_until |  | null | null
bigbench_multiemo_generate_until |  | null | null
bigbench_misconceptions_generate_until |  | null | null
bigbench_list_functions_generate_until |  | null | null
bigbench_parsinlu_qa_generate_until |  | null | null
bigbench_movie_recommendation_generate_until |  | null | null
bigbench_general_knowledge_generate_until |  | null | null
bigbench_social_iqa_generate_until |  | null | null
mutual_plus |  | null | null
mutual |  | multiple_choice | - version: 2.0
winogrande |  | multiple_choice | - version: 1.0
piqa |  | multiple_choice | - version: 1.0
toxigen |  | multiple_choice | - version: 1.0
realtoxicityprompts |  | null | - version: 0.0
