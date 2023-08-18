# taken from
# https://github.com/microsoft/AGIEval/blob/main/src/dataset_loader.py#L87


def doc_to_text_aquarat(doc: dict) -> str:
    _fewshot = [
        "Problem 1.    A cycled from P to Q at 10 kmph and returned at the rate of 9 kmph. B cycled both ways at 12 kmph. In the whole journey B took 10 minutes less than A. Find the distance between P and Q.\nChoose from the following options:    (A)1.75km (B)2.75km (C)3.75km (D)4.75km (E)5.75km\nThe answer is therefore C\n",
        "Problem 2.    In a poll of 45,000 dentists, only 30 percent responded; of these, 20 percent claimed to prefer Toothpaste A. How many of the dentists who responded did not claim a preference for Toothpaste A?\nChoose from the following options:    (A)2,200 (B)2,640 (C)6,160 (D)8,800 (E)10,800\nThe answer is therefore E\n",
        "Problem 3.    In a shipment of 120 machine parts, 5 percent were defective. In a shipment of 80 machine parts, 10 percent were defective. For the two shipments combined, what percent of the machine parts were defective?\nChoose from the following options:    (A)6.5% (B)7.0% (C)7.5% (D)8.0% (E)8.5%\nThe answer is therefore C\n",
        "Problem 4.    In recent Malta elections, in a particular constituency, 100,000 votes were cast and each vote was cast for\neither Candidate A or Candidate B. If candidate A has won by 500 votes, what percent of the 100,000 votes\nwere cast for Candidate A?\nChoose from the following options:    (A)50.05% (B)50.25% (C)50.5% (D)51% (E)52.5%\nThe answer is therefore B\n",
        "Problem 5.    In 4 years, Raj's father will be double Raj's age then. Two years ago, while his mother was twice his age that time. If Raj is going to be 32 years old 8 years from now, then what is the sum of his parents age now?\nChoose from the following options:    (A)97 (B)98 (C)99 (D)100 (E)101\nThe answer is therefore B\n",
    ]
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(6)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + " ".join(doc["options"])
    )  # + "\n"
    return _fewshot + question_input


def doc_to_text_logiqa(doc: dict) -> str:
    _fewshot = (
        "Here are the answers for the problems in the exam.\nProblem 1.   Because the image of the photo is "
        "formed by the contact between the light and the film, each photo has a certain authenticity.However, "
        "photos taken from different angles always reflect the reality of one side of the object rather than "
        "the whole truth.In this sense, the photo is unreal.Therefore, under current technical conditions, "
        "it is inappropriate to use photos as evidence, especially in court. Which of the following, if true, "
        "would weaken the above argument most?\nChoose from the following options:    (A)Photography "
        "technology is constantly evolving.In theory, panoramic photos can reflect the full reality of "
        "objects from the appearance. (B)Any evidence only needs to reflect a certain aspect of the fact. ("
        "C)In the court hearing, some photos, although they cannot be evidence, have important reference "
        "value. (D)Some photos are synthesized or forged by technical means.\nThe answer is therefore "
        "B\nProblem 2.   Some people think that any organization includes different job levels or "
        "tiers, and everyone belongs to one of the tiers.If someone does a good job in the original level, "
        "they will be promoted, and the promoted will be reused But the future is humble and ineffective, "
        "which will result in inefficient institutions and overstaffing. Which of the following is true if it "
        "is the most doubtful?\nChoose from the following options:    (A)The working methods of different "
        "positions are different, and there must be an adaptation process for new positions (B)The department "
        "manager Mr.Wang has outstanding performance and is still outstanding after being promoted to general "
        "manager of the company (C)Personal promotion often affects the development of the institution to a "
        "certain extent (D)Li Ming's sports performance is not satisfactory, but he did it well after "
        "entering the management\nThe answer is therefore B\nProblem 3.   A country intends to import "
        "several of the six crops of A.B, C, D, E, and H for use in the country ’s huge animal feed industry, "
        "considering that some crops may contain prohibited ingredients and the complementarity that exists "
        "between them Or alternative factors, the country has the following requirements for the import of "
        "these crops? (1) All of them that do not contain prohibited ingredients are imported; (2) If A or B "
        "contain prohibited ingredients, then import E and H; (3) If C If it contains prohibited ingredients, "
        "then Ding will not be imported; (4) if E is imported, B and D will be imported; (5) if D is not "
        "imported, C will be imported; if C is imported, D will not be imported. According to the above "
        "requirements, which of the following crops can the country import?\nChoose from the following "
        "options:    (A)A.B, C. (B)B, C, D. (C)A.E, and E. (D)A.D, and yourself.\nThe answer is therefore "
        "A\n"
    )
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(6)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + " ".join(doc["options"])
    )  # + "\n"
    return _fewshot + question_input


# taken from
# https://github.com/microsoft/AGIEval/blob/19b2c5daed87e3463fe6a29f0c342bfc31e98234/src/dataset_loader.py#L25
def doc_to_text_zeroshot(doc: dict) -> str:
    """
    <passage>Q: <question> Answer Choices: <choice1> <choice2> <choice3> <choice4>\n
    A: Among A through {A-D}, the answer is
    """
    passage = doc.get("passage", "")
    option_string = "ABCDEFG"
    count = len(doc["options"])
    if count == 1:
        count = 5
    return (
        passage
        + "Q: "
        + doc["question"]
        + " "
        + "Answer Choices: "
        + " ".join(doc["options"])
        + "\n"
        + "A: Among A through {}, the answer is".format(option_string[count - 1])
    )


# MATH DATASET
def doc_to_text_math_zeroshot(doc: dict) -> str:
    """
    <passage>Q: <question>\n
    A: The answer is
    """
    return doc["passage"] + "Q: " + doc["question"] + "\n" "A: The answer is"


# taken from https://github.com/microsoft/AGIEval/blob/main/src/post_process.py
def extract_last_line(string):
    lines = string.split("\n")
    for item in lines[::-1]:
        if item.strip() != "":
            string = item
            break
    return string


def remove_few_shot_prefix(string: str):
    prefix_list = ["The answer is therefore", "答案是"]
    for prefix in prefix_list:
        if string.startswith(prefix):
            string = string[len(prefix) :].strip()
        elif prefix in string:
            index = string.rfind(prefix)
            if index >= 0:
                string = string[index + len(prefix) :].strip()
    return string


# def parse_math_answer(raw_string):
#     if setting_name == "few-shot-CoT":
#         raw_string = extract_last_line(raw_string)
#     if setting_name == "few-shot-CoT" or setting_name == "few-shot":
#         raw_string = remove_few_shot_prefix(raw_string)
#         return raw_string
