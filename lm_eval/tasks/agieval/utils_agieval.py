# taken from
# https://github.com/microsoft/AGIEval/blob/main/src/dataset_loader.py#L87


"""
"Here are the answers for the problems in the exam.\n"
<Problem 1.>\n
Choose from the following options:    (A)<option1>...
The answer is therefore C/n
...
Problem <n>    <question>\n
Choose from the following options: (A)<option1>...

# The original adds \n at the end
"""


def doc_to_text_all(doc: dict) -> str:
    all_choices = " ".join(doc["options"])
    return f"Problem: {doc['question']}\nChoose from the following options: {all_choices}\nAnswer:"


def doc_to_text_s(doc: dict) -> str:
    all_choices = " ".join(doc["options"])
    passage = doc.get("passage", "")
    return f"Problem: {passage}\n{doc['question']}\n{all_choices}\nAnswer:"


# Few-shot 3-5
def doc_to_text_aquarat(doc: dict) -> str:
    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.    A cycled from P to Q at 10 kmph and returned at the rate of 9 kmph. B cycled both ways at 12 kmph. In the whole journey B took 10 minutes less than A. Find the distance between P and Q.\nChoose from the following options:    (A)1.75km (B)2.75km (C)3.75km (D)4.75km (E)5.75km\nThe answer is therefore C\n",
        "Problem 2.    In a poll of 45,000 dentists, only 30 percent responded; of these, 20 percent claimed to prefer Toothpaste A. How many of the dentists who responded did not claim a preference for Toothpaste A?\nChoose from the following options:    (A)2,200 (B)2,640 (C)6,160 (D)8,800 (E)10,800\nThe answer is therefore E\n",
        "Problem 3.    In a shipment of 120 machine parts, 5 percent were defective. In a shipment of 80 machine parts, 10 percent were defective. For the two shipments combined, what percent of the machine parts were defective?\nChoose from the following options:    (A)6.5% (B)7.0% (C)7.5% (D)8.0% (E)8.5%\nThe answer is therefore C\n",
        "Problem 4.    In recent Malta elections, in a particular constituency, 100,000 votes were cast and each vote was cast for\neither Candidate A or Candidate B. If candidate A has won by 500 votes, what percent of the 100,000 votes\nwere cast for Candidate A?\nChoose from the following options:    (A)50.05% (B)50.25% (C)50.5% (D)51% (E)52.5%\nThe answer is therefore B\n",
        "Problem 5.    In 4 years, Raj's father will be double Raj's age then. Two years ago, while his mother was twice his age that time. If Raj is going to be 32 years old 8 years from now, then what is the sum of his parents age now?\nChoose from the following options:    (A)97 (B)98 (C)99 (D)100 (E)101\nThe answer is therefore B\n",
    ]
    _fewshot = "".join(_fewshot)
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(6)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + "\n".join(doc["options"])
    )
    return _fewshot + question_input


def doc_to_text_logiqa(doc: dict) -> str:
    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.   Because the image of the photo is formed by the contact between the light and the film, each photo has a certain authenticity.However, photos taken from different angles always reflect the reality of one side of the object rather than the whole truth.In this sense, the photo is unreal.Therefore, under current technical conditions, it is inappropriate to use photos as evidence, especially in court. Which of the following, if true, would weaken the above argument most?\nChoose from the following options:    (A)Photography technology is constantly evolving.In theory, panoramic photos can reflect the full reality of objects from the appearance. (B)Any evidence only needs to reflect a certain aspect of the fact. (C)In the court hearing, some photos, although they cannot be evidence, have important reference value. (D)Some photos are synthesized or forged by technical means.\nThe answer is therefore B\n",
        "Problem 2.   Some people think that any organization includes different job levels or tiers, and everyone belongs to one of the tiers.If someone does a good job in the original level, they will be promoted, and the promoted will be reused But the future is humble and ineffective, which will result in inefficient institutions and overstaffing. Which of the following is true if it is the most doubtful?\nChoose from the following options:    (A)The working methods of different positions are different, and there must be an adaptation process for new positions (B)The department manager Mr.Wang has outstanding performance and is still outstanding after being promoted to general manager of the company (C)Personal promotion often affects the development of the institution to a certain extent (D)Li Ming's sports performance is not satisfactory, but he did it well after entering the management\nThe answer is therefore B\n",
        "Problem 3.   A country intends to import several of the six crops of A.B, C, D, E, and H for use in the country ’s huge animal feed industry, considering that some crops may contain prohibited ingredients and the complementarity that exists between them Or alternative factors, the country has the following requirements for the import of these crops? (1) All of them that do not contain prohibited ingredients are imported; (2) If A or B contain prohibited ingredients, then import E and H; (3) If C If it contains prohibited ingredients, then Ding will not be imported; (4) if E is imported, B and D will be imported; (5) if D is not imported, C will be imported; if C is imported, D will not be imported. According to the above requirements, which of the following crops can the country import?\nChoose from the following options:    (A)A.B, C. (B)B, C, D. (C)A.E, and E. (D)A.D, and yourself.\nThe answer is therefore A\n",
    ]
    _fewshot = "".join(_fewshot)
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(4)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + "\n".join(doc["options"])
    )
    return _fewshot + question_input


def doc_to_text_lsat_ar(doc: dict) -> str:
    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.    If J, O, and Y are the first three concertos to be played, not necessarily in the order given, which one of the following is a concerto that CANNOT be played on the fifth Sunday?\nChoose from the following options:    (A)H (B)K (C)N (D)P (E)X\nThe answer is therefore E\n",
        "Problem 2.    If N is the second book discussed and it is not summarized, which one of the following could be true?\nChoose from the following options:    (A)F is summarized. (B)K is summarized. (C)O is summarized. (D)T is discussed earlier than F. (E)The third book discussed is not summarized.\nThe answer is therefore A\n",
        "Problem 3.    Which one of the following is a pair of products that could be advertised during the same week as each other?\nChoose from the following options:    (A)G and H (B)H and J (C)H and O (D)K and O (E)M and O\nThe answer is therefore E\n",
    ]
    _fewshot = "".join(_fewshot)
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(4)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + "\n".join(doc["options"])
    )
    return _fewshot + question_input


def doc_to_text_lsat_lr(doc: dict) -> str:
    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.    The statement that the law should require explicit safety labels on toys serves which one of the following functions in the consumer advocate's argument?\nChoose from the following options:    (A)It is a general principle supporting the conclusion of the argument. (B)It is a proposed compromise between two conflicting goals. (C)It is the conclusion of the argument. (D)It is evidence that must be refuted in order to establish the conclusion of the argument. (E)It is a particular instance of the general position under discussion.\nThe answer is therefore C\n",
        "Problem 2.    Which one of the following is an assumption on which the argument depends?\nChoose from the following options:    (A)It will eventually be possible to breed strains of bananas that are resistant to Sigatoka disease. (B)Large plantations produce most or all of the world's bananas. (C)Sigatoka disease spreads more slowly on large plantations than in small banana groves. (D)Sigatoka disease is the only disease that threatens bananas on a worldwide scale. (E)Most of the banana trees that have not been exposed to the Sigatoka fungus grow in small banana groves.\nThe answer is therefore B\n",
        "Problem 3.    Which one of the following is an assumption on which the argument depends?\nChoose from the following options:    (A)Passengers feel no safer on airplanes equipped with the radar system than on comparable airplanes not so equipped. (B)Warnings given by a collision-avoidance system about phantom airplanes are not caused by distorted radar signals. (C)The frequency of invalid warnings will not cause pilots routinely to disregard the system's warnings. (D)Commercial passenger airplanes are not the only planes that can be equipped with a collision-avoidance system (E)The greatest safety risk for passengers traveling on commercial passenger airplanes is that of a midair collision.\nThe answer is therefore C\n",
    ]
    _fewshot = "".join(_fewshot)
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(4)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + "\n".join(doc["options"])
    )
    return _fewshot + question_input


def doc_to_text_lsat_rc(doc: dict) -> str:
    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.    According to the passage, which one of the following distinguished the de futuro contract from the de praesenti contract?\nChoose from the following options:    (A)One was recognized by Alexandrine doctrine, while the other was considered a secular contract. (B)One required the permission of parents, while the other concerned only the couple involved. (C)One required the announcement of marriage banns, while the other could be entered into solely through a verbal contract. (D)One expressed future intent, while the other established an immediate, binding union. (E)One allowed the solemnization of Church ritual, while the other resulted in excommunication.\nThe answer is therefore D\n",
        "Problem 2.    Which one of the following most accurately expresses the main point of the passage?\nChoose from the following options:    (A)The Disciples at Emmaus, van Meegeren's forgery of a Vermeer, was a failure in both aesthetic and artistic terms. (B)The aesthetic value of a work of art is less dependent on the work's visible characteristics than on certain intangible characteristics. (C)Forged artworks are artistically inferior to originals because artistic value depends in large part on originality of vision. (D)The most skilled forgers can deceive even highly qualified art experts into accepting their work as original. (E)Art critics tend to be unreliable judges of the aesthetic and artistic quality of works of art.\nThe answer is therefore C\n",
        "Problem 3.    The author refers to the meteorological data gathered in North America over the past century in order to\nChoose from the following options:    (A)show how differing views on the extent of the rise in global temperature can be resolved (B)argue that any warming detected over the past century has most likely been the result of a natural climatic fluctuation (C)argue against the prevailing view that the amount of atmospheric CO has increased by about 20 percent over the past century (D)suggest that there should be more numerous and accurate observation points outside of North America (E)present evidence that casts doubt on the view that global temperature has increased over the past century\nThe answer is therefore E\n",
    ]
    _fewshot = "".join(_fewshot)
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(4)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + "\n".join(doc["options"])
    )
    return _fewshot + question_input


def doc_to_text_sat_en(doc: dict) -> str:
    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.   Solar panel installations continue to grow quickly,.but the solar panel manufacturing industry is in the.doldrums because supply far exceeds demand. The.poor market may be slowing innovation, but.advances continue; judging by the mood this week at.the IEEE Photovoltaics Specialists Conference in.Tampa, Florida, people in the industry remain.optimistic about its long-term prospects..The technology that’s surprised almost everyone.is conventional crystalline silicon. A few years ago,.silicon solar panels cost $4 per watt, and.Martin Green, professor at the University of.New South Wales and one of the leading silicon solar.panel researchers, declared that they’d never go.below $1 a watt. “Now it’s down to something like It can most reasonably be inferred from the passage that many people in the solar panel industry believe that\nChoose from the following options:    (A)consumers don’t understand how solar panels work. (B)two-sided cells have weaknesses that have not yet been discovered. (C)the cost of solar panels is too high and their power output too low. (D)Willow Glass is too inefficient to be marketable.\nThe answer is therefore C\n",
        "Problem 2.   Texas gourd vines unfurl their large, flared.blossoms in the dim hours before sunrise. Until they.close at noon, their yellow petals and mild, squashy.aroma attract bees that gather nectar and shuttle.pollen from flower to flower. But “when you.advertise [to pollinators], you advertise in an.open communication network,” says chemical.ecologist Ian Baldwin of the Max Planck Institute for.Chemical Ecology in Germany. “You attract not just.the good guys, but you also attract the bad guys.” For.a Texas gourd plant, striped cucumber beetles are.among the very bad guys. They chew up pollen and.petals, defecate in the flowers and transmit the.dreaded bacterial wilt disease, an infection that can.reduce an entire plant to a heap of collapsed tissue in.mere days..In one recent study, Nina Theis and Lynn Adler.took on the specific problem of the Texas.gourd—how to attract enough pollinators but not.too many beetles. The Texas gourd vine’s main.pollinators are honey bees and specialized squash.bees, which respond to its floral scent. The aroma.includes 10 compounds, but the most.abundant—and the only one that lures squash bees.into traps—is 1,4-dimethoxybenzene..Intuition suggests that more of that aroma should.be even more appealing to bees. “We have this.assumption that a really fragrant flower is going to.attract a lot of pollinators,” says Theis, a chemical.ecologist at Elms College in Chicopee,.Massachusetts. But, she adds, that idea hasn’t really.been tested—and extra scent could well call in more.beetles, too. To find out, she and Adler planted The primary purpose of the passage is to\nChoose from the following options:    (A)discuss the assumptions and reasoning behind a theory. (B)describe the aim, method, and results of an experiment. (C)present and analyze conflicting data about a phenomenon. (D)show the innovative nature of a procedure used in a study.\nThe answer is therefore B\n",
        "Problem 3.   Even then my only friends were made of paper and ink. At school I had learned to read and write long before the other children. Where my school  friends saw notches of ink on incomprehensiblepages, I saw light, streets, and people. Words and the mystery of their hidden science fascinated me, and I saw in them a key with which I could unlock a boundless world, a safe haven from that home, those streets, and those troubled days in which even Icould sense that only a limited fortune awaited me. My father didn't like to see books in the house. There was something about them-apart from the letters he could not decipher-that offended him. He used to tell me that as soon as I was ten he would 15 send me off to work and that I'd better get rid of all my scatterbrained ideas if I didn't want to end up a loser, a nobody. I used to hide my books under the mattress and wait for him to go out or fall asleep so that I could read. Once he caught me reading at night20 and flew into a rage. He tore the book from my hands and flung it out of the window.\"If I catch you wasting electricity again, reading all this nonsense, you'll be sorry.\"My father was not a miser and, despite the 25 hardships we suffered, whenever he could he gave me a few coins so that I could buy myself some treats like the other children. He was convinced that I spent them on licorice sticks, sunflower seeds, or sweets, but I would keep them in a coffee tin under the bed, 30 and when I'd collected four or five reales I'd secretly rush out to buy myself a book.My favorite place in the whole city was the Sempere \\& Sons bookshop on Calle Santa Ana. It smelled of old paper and dust and it was my35 sanctuary, my refuge. The bookseller would let me sit on a chair in a corner and read any book I liked to my heart's content. He hardly ever allowed me to pay for the books he placed in my hands, but when he wasn't looking I'd leave the coins I'd managed to 40 collect on the counter before I left. It was only small change-if I'd had to buy a book with that pittance, I would probably have been able to afford only a booklet of cigarette papers. When it was time for me to leave, I would do so dragging my feet, a weight on $45 \\mathrm{my}$ soul. If it had been up to me, I would have stayed there forever.One Christmas Sempere gave me the best gift I have ever received. It was an old volume, read and experienced to the full.50 \"Great Expectations, by Charles Dickens,\" I read on the cover.I was aware that Sempere knew a few authors who frequented his establishment and, judging by the care with which he handled the volume, I thought 55 perhaps this Mr. Dickens was one of them.\"A friend of yours?\"\"A lifelong friend. And from now on, he's your friend too.\" That afternoon I took my new friend home, 60 hidden under my clothes so that my father wouldn't see it. It was a rainy winter, with days as gray as lead, and I read Great Expectations about nine times, partly because I had no other book at hand, partly because I did not think there could be a better one in 65 the whole world and I was beginning to suspect that Mr. Dickens had written it just for me. Soon I was convinced that I didn't want to do anything else in life but learn to do what Mr. Dickens had done. With which of the following statements about his father would the narrator most likely agree?\nChoose from the following options:    (A)He lacked affection for the narrator. (B)He disliked any unnecessary use of money. (C)He would not have approved of Sempere's gift. (D)He objected to the writings of Charles Dickens.\nThe answer is therefore C\n",
    ]
    _fewshot = "".join(_fewshot)
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(4)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + "\n".join(doc["options"])
    )
    return _fewshot + question_input


def doc_to_text_sat_en_wop(doc: dict) -> str:
    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.   It can most reasonably be inferred from the passage that many people in the solar panel industry believe that\nChoose from the following options:    (A)consumers don’t understand how solar panels work. (B)two-sided cells have weaknesses that have not yet been discovered. (C)the cost of solar panels is too high and their power output too low. (D)Willow Glass is too inefficient to be marketable.\nThe answer is therefore C\n",
        "Problem 2.   The primary purpose of the passage is to\nChoose from the following options:    (A)discuss the assumptions and reasoning behind a theory. (B)describe the aim, method, and results of an experiment. (C)present and analyze conflicting data about a phenomenon. (D)show the innovative nature of a procedure used in a study.\nThe answer is therefore B\n",
        "Problem 3.   With which of the following statements about his father would the narrator most likely agree?\nChoose from the following options:    (A)He lacked affection for the narrator. (B)He disliked any unnecessary use of money. (C)He would not have approved of Sempere's gift. (D)He objected to the writings of Charles Dickens.\nThe answer is therefore C\n",
    ]
    _fewshot = "".join(_fewshot)
    passage = ""
    question_input = (
        "Problem {}.   ".format(4)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + "\n".join(doc["options"])
    )
    return _fewshot + question_input


def doc_to_text_sat_math(doc: dict) -> str:
    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.    $$(x-6)^{2}+(y+5)^{2}=16$$In the $x y$-plane, the graph of the equation above is a circle. Point $P$ is on the circle and has coordinates $(10,-5)$. If $\\overline{P Q}$ is a diameter of the circle, what are the coordinates of point $Q$ ?\nChoose from the following options:    (A)$(2,-5)$ (B)$(6,-1)$ (C)$(6,-5)$ (D)$(6,-9)$\nThe answer is therefore A\n",
        "Problem 2.    Two units of length used in ancient Egypt were cubits and palms, where 1 cubit is equivalent to 7 palms. The Great Sphinx statue in Giza is approximately 140 cubits long. Which of the following best approximates the length, in palms, of the Great Sphinx statue?\nChoose from the following options:    (A)0.05 (B)20 (C)140 (D)980\nThe answer is therefore D\n",
        "Problem 3.    In the 1908 Olympic Games, the Olympic marathon was lengthened from 40 kilometers to approximately 42 kilometers. Of the following, which is closest to the increase in the distance of the Olympic marathon, in miles? ( 1 mile is approximately 1.6 kilometers.)\nChoose from the following options:    (A)1.00 (B)1.25 (C)1.50 (D)1.75\nThe answer is therefore B\n",
        "Problem 4.    The expression $\\frac{x^{-2} y^{\\frac{1}{2}}}{x^{\\frac{1}{3}} y^{-1}}$, where $x>1$ and $y>1$, is equivalent to which of the following?\nChoose from the following options:    (A)$\\frac{\\sqrt{y}}{\\sqrt[3]{x^{2}}}$ (B)$\\frac{y \\sqrt{y}}{\\sqrt[3]{x^{2}}}$ (C)$\\frac{y \\sqrt{y}}{x \\sqrt{x}}$ (D)$\\frac{y \\sqrt{y}}{x^{2} \\sqrt[3]{x}}$\nThe answer is therefore D\n",
        "Problem 5.    Which of the following is an example of a function whose graph in the $x y$-plane has no $x$-intercepts?\nChoose from the following options:    (A)A linear function whose rate of change is not zero (B)A quadratic function with real zeros (C)A quadratic function with no real zeros (D)A cubic polynomial with at least one real zero\nThe answer is therefore C\n",
    ]
    _fewshot = "".join(_fewshot)
    passage = doc.get("passage", "")
    question_input = (
        "Problem {}.   ".format(6)
        + passage
        + " "
        + doc["question"]
        + "\n"
        + "Choose from the following options:    "
        + "\n".join(doc["options"])
    )
    return _fewshot + question_input


# taken from
# https://github.com/microsoft/AGIEval/blob/19b2c5daed87e3463fe6a29f0c342bfc31e98234/src/dataset_loader.py#L25
# Used for all AGI datasets except MATH. Not used here yet!
def doc_to_text_zeroshot(doc: dict) -> str:
    # No space after passage!
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
