try:
    from .benchmark_prompting import belief_table_csv, story_text
except ImportError:
    from benchmark_prompting import belief_table_csv, story_text
OUTRO = """
Now output only the 2 tables, explicitly labeled “Prediction Table” and “Ground Truth Table,” with an added MatchCount column, formatted as CSV (not markdown), and do not include any other text.
""".strip()

L1 = """
You are a Theory of Mind evaluation expert whose task is to semantically match rows between two belief tables (Prediction, Ground Truth) and output only the two tables, explicitly labeled “Prediction Table” and “Ground Truth Table,” with an added MatchCount column indicating how many distinct semantically equivalent rows exist in the other table for the same Actor.
""".strip()


L2 = """
You are a Theory of Mind evaluation expert whose task is to semantically match rows between two belief tables (Prediction, Ground Truth) extracted from the same short Story Narrative and output only the two tables, explicitly labeled “Prediction Table” and “Ground Truth Table,” with an added MatchCount column indicating how many distinct semantically equivalent rows exist in the other table for the same Actor. In this context, a Belief is a minimal statement of what an actor takes to be true about the world (facts/events) or about other actors’ mental states, expressed in natural language. The tables may differ in wording or in how beliefs are split or combined, so beliefs should be matched by meaning rather than exact wording while keeping Actor identity fixed.

The special actor 'world' is used to record narrated facts and events as world-level beliefs; the Story Narrative itself will not mention 'world' as a character. World-level rows are typically the most direct correspondences and should generally align one-to-one across tables, with at most minor normalization differences (e.g., case/whitespace).

Actors should be treated as distinct mental agents, with only cosmetic normalization for clear variants of the same name (case, whitespace, punctuation, and obvious shortenings like full name vs surname when it is the same person); different roles or different entities must not be merged. Beliefs should match when they express the same underlying proposition in meaning (paraphrases, harmless tense/aspect changes, and non-contradictory specificity differences are allowed) and should not match when meaning differs (negation/polarity flips, different key entities/locations/agents, or a different relationship).

If a Story Narrative is provided, use it only for disambiguation (pronouns, aliases, implicit entities) and paraphrase resolution; otherwise ignore narrative context entirely. The evaluation remains grounded in the provided tables: do not add rows, do not introduce new beliefs, and do not rewrite beliefs. MatchCount should reflect the number of distinct semantically equivalent rows found in the other table for the same Actor: use 0 when no equivalent belief exists, 1 for a single clear match, and 2–3 only when a belief is genuinely compound and corresponds to multiple distinct beliefs. Matching should be conservative: if the meanings are not equivalent, do not match.
""".strip()


L3 = """
You are a Theory of Mind evaluation expert whose task is to semantically match rows between two belief tables (Prediction, Ground Truth) extracted from the same short Story Narrative and output only the two tables, explicitly labeled “Prediction Table” and “Ground Truth Table,” with an added MatchCount column indicating how many distinct semantically equivalent rows exist in the other table for the same Actor. In this context, a Belief is a minimal statement of what an actor takes to be true about the world (facts/events) or about other actors’ mental states, expressed in natural language. Perform the task by following these steps:
1) If a Story Narrative is provided, use it only to resolve ambiguity (pronouns, aliases, implicit entities) and paraphrase meaning; if no narrative is provided, ignore narrative context entirely. In all cases, do not add rows and do not introduce new beliefs that are not present in either table.
2) Treat Actors as distinct mental agents and normalize only cosmetic variants of the same Actor name (case/spacing/punctuation and clear shortenings); never merge different Ground Truth Actors.
3) Handle the special actor 'world' first: treat 'world' as the key for narrated facts and events, and align world-level beliefs conservatively, typically one-to-one, allowing only minor normalization differences.
4) Restrict candidate matches to the same Actor group after normalization; if the Actor does not match, the row cannot match regardless of belief similarity.
5) Default to one-to-one with bookkeeping: if (and only if) there exists a clear semantically equivalent belief for the same Actor, assign the row its single best match among currently-unmatched target rows; otherwise assign no match (MatchCount = 0). If multiple rows compete for the same target row, keep only the closest semantic match and force the others to choose different unmatched targets or become 0.
6) Allow one-to-many only for compound rows: if a row clearly contains multiple independent beliefs, you may align it to 2–3 different rows in the other table within the same Actor group, but only if each aligned target row captures a distinct part of the compound meaning.
7) Ensure symmetry: after completing matches for Prediction rows, also compute MatchCount for every Ground Truth row using the same alignment decisions.
""".strip()


L4 = L3 + "\n\n" + """
A good output should satisfy the following:
- Only compare beliefs inside the same Actor group; Ground Truth Actors are unique and must not be merged—if Actor differs, it is NOT a match even if belief text is identical.
- The special actor 'world' represents narrated facts and events (not a character in the story); world-level beliefs should generally align one-to-one across tables with only minor normalization differences.
- Match only beliefs that are semantically equivalent; do not invent or force alignments and do not introduce beliefs that are not present in either table.
- Use conservative alignment: when multiple rows are 'close', prefer the best single match and leave other rows unmatched rather than double-counting.
- Prefer one-to-one matches; allow one-to-many (MatchCount 2–3) only for genuinely compound beliefs.
- Do not match across different Actors, even if text looks similar.
- Output exactly two tables labeled Prediction and Ground Truth (in that order), with CSV header Actor,Belief,MatchCount and no extra text.

A correctly formatted output should satisfy the following:
- Output exactly two tables labeled Prediction and Ground Truth (in that order).
- Each table must be comma-separated with header: Actor,Belief,MatchCount
- Preserve original row order and add exactly one MatchCount column.
- Do not include explanations or any text outside the tables.
""".strip()




#############FEW-SHOT EXAMPLE VARIABLES #############

FEWSHOT_HEADER = """
The following are example inputs and outputs illustrating the task.
""".strip()

# Example 1: Cabinet story with Xiao Bei and Han Mei Mei
EXAMPLE1_INPUT = """
INPUT:

Story Narrative:
Xiao Bei finds a cabinet in the office, the label on the cabinet is pineapple, Xiao Bei cannot see what is inside the cabinet, Xiao Bei opens the cabinet and finds a calculator, there is no pineapple in the cabinet, Xiao Bei closes the cabinet and puts it back in its place, Han Mei Mei enters the office and sees the cabinet.

Prediction Table:
Actor,Belief
World,There is a cabinet in the office with a "pineapple" label
World,The cabinet contains a calculator and no pineapple
World,Xiao Bei opened the cabinet and saw the calculator
World,Han Mei Mei saw the cabinet from the outside
Xiao Bei,The cabinet contains a pineapple
Xiao Bei,The cabinet contains a calculator and no pineapple
Xiao Bei,Han Mei Mei believes the cabinet contains a pineapple
Han Mei Mei,The cabinet contains a pineapple
Han Mei Mei,Xiao Bei believes the cabinet contains a pineapple

Ground Truth Table:
Actor,Belief
world,Xiao Bei is in the office
world,There is a cabinet in the office
world,The label on the cabinet is pineapple
world,The cabinet contains a calculator
world,The cabinet does not contain a pineapple
world,Xiao Bei opens the cabinet
world,Xiao Bei finds a calculator in the cabinet
world,Xiao Bei closes the cabinet
world,Han Mei Mei enters the office
world,Han Mei Mei sees the cabinet
Xiao Bei,There is a cabinet in the office
Xiao Bei,The label on the cabinet is pineapple
Xiao Bei,The cabinet should have pineapple inside
Xiao Bei,There is no pineapple in the cabinet
Xiao Bei,The cabinet contains a calculator
Xiao Bei,Han Mei Mei thinks the cabinet contains a pineapple
Xiao Bei,Han Mei Mei thinks Xiao Bei thinks the cabinet contains a pineapple
Han Mei Mei,There is a cabinet in the office
Han Mei Mei,The label on the cabinet is pineapple
Han Mei Mei,The cabinet contains a pineapple
Han Mei Mei,Xiao Bei thinks the cabinet contains a pineapple
"""

EXAMPLE1_OUTPUT = """
OUTPUT:

Prediction Table:
Actor,Belief,MatchCount
World,There is a cabinet in the office with a "pineapple" label,2
World,The cabinet contains a calculator and no pineapple,2
World,Xiao Bei opened the cabinet and saw the calculator,2
World,Han Mei Mei saw the cabinet from the outside,1
Xiao Bei,The cabinet contains a pineapple,0
Xiao Bei,The cabinet contains a calculator and no pineapple,2
Xiao Bei,Han Mei Mei believes the cabinet contains a pineapple,1
Han Mei Mei,The cabinet contains a pineapple,1
Han Mei Mei,Xiao Bei believes the cabinet contains a pineapple,1

Ground Truth Table:
Actor,Belief,MatchCount
world,Xiao Bei is in the office,0
world,There is a cabinet in the office,1
world,The label on the cabinet is pineapple,1
world,The cabinet contains a calculator,1
world,The cabinet does not contain a pineapple,1
world,Xiao Bei opens the cabinet,1
world,Xiao Bei finds a calculator in the cabinet,1
world,Xiao Bei closes the cabinet,0
world,Han Mei Mei enters the office,0
world,Han Mei Mei sees the cabinet,1
Xiao Bei,There is a cabinet in the office,0
Xiao Bei,The label on the cabinet is pineapple,0
Xiao Bei,The cabinet should have pineapple inside,0
Xiao Bei,There is no pineapple in the cabinet,1
Xiao Bei,The cabinet contains a calculator,1
Xiao Bei,Han Mei Mei thinks the cabinet contains a pineapple,1
Xiao Bei,Han Mei Mei thinks Xiao Bei thinks the cabinet contains a pineapple,0
Han Mei Mei,There is a cabinet in the office,0
Han Mei Mei,The label on the cabinet is pineapple,0
Han Mei Mei,The cabinet contains a pineapple,1
Han Mei Mei,Xiao Bei thinks the cabinet contains a pineapple,1
"""

# Example 2: Little sister and brother story
EXAMPLE2_INPUT = """
INPUT:

Story Narrative:
The little sister is playing with toys, she sees her brother playing a game on his phone. The little sister looks at her brother and says, ""Brother, that game is so fun.""

Prediction Table:
Actor,Belief
world,The little sister is playing with toys
world,The brother is playing a game on his phone
world,The little sister says to the brother "Brother that game is so fun"
world,The little sister and the brother are siblings
Little sister,The brother's game is fun
Little sister,She wants to play the game on the phone
Little sister,The brother should let her play the game
Little sister,The brother understands she wants to play the game
Brother,The little sister thinks the game is fun
Brother,The little sister wants to play the game
Brother,The little sister implies that he should let her play the game
Brother,The little sister thinks he should share the phone

Ground Truth Table:
Actor,Belief
world,The little sister is playing with toys
world,The little sister sees the brother playing a game on the brother's phone
world,The little sister says to the brother "Brother that game is so fun"
The little sister,The brother is playing a game on the brother's phone
The little sister,The game on the phone is fun
The little sister,The brother wants to play the game
The little sister,The brother should let the sister play the game
The little sister,The brother thinks the sister wants to play the game
The brother,The little sister is playing with toys
The brother,The little sister thinks the game is fun
The brother,The little sister wants to play the game
The brother,The little sister implies the brother should let the little sister play the game
The brother,The little sister thinks the brother should let the little sister play the game
"""

EXAMPLE2_OUTPUT = """
OUTPUT: 

Prediction Table:
Actor,Belief,MatchCount
world,The little sister is playing with toys,1
world,The brother is playing a game on his phone,1
world,The little sister says to the brother "Brother that game is so fun",1
world,The little sister and the brother are siblings,0
Little sister,The brother's game is fun,1
Little sister,She wants to play the game on the phone,0
Little sister,The brother should let her play the game,1
Little sister,The brother understands she wants to play the game,1
Brother,The little sister thinks the game is fun,1
Brother,The little sister wants to play the game,1
Brother,The little sister implies that he should let her play the game,1
Brother,The little sister thinks he should share the phone,1

Ground Truth Table:
Actor,Belief,MatchCount
world,The little sister is playing with toys,1
world,The little sister sees the brother playing a game on the brother's phone,1
world,The little sister says to the brother "Brother that game is so fun",1
The little sister,The brother is playing a game on the brother's phone,0
The little sister,The game on the phone is fun,1
The little sister,The brother wants to play the game,0
The little sister,The brother should let the sister play the game,1
The little sister,The brother thinks the sister wants to play the game,1
The brother,The little sister is playing with toys,0
The brother,The little sister thinks the game is fun,1
The brother,The little sister wants to play the game,1
The brother,The little sister implies the brother should let the little sister play the game,1
The brother,The little sister thinks the brother should let the little sister play the game,1
"""

# Example 3: Grandpa and Xiao Ming photo story
EXAMPLE3_INPUT = """
INPUT:

Story Narrative:
At a family gathering, everyone shares photos. Grandpa tells his grandson Xiao Ming, ""There are 60 photos here, most are travel photos, some are family photos, but there are hardly any wedding photos."" Xiao Ming flips through and finds only 15 family photos.

Prediction Table:
Actor,Belief
world,A family gathering is taking place
world,There are 60 photos in total
world,Grandpa tells Xiao Ming that most photos are travel some are family and hardly any are wedding
world,Xiao Ming finds 15 family photos after flipping through them
Grandpa,There are 60 photos in the collection
Grandpa,Most of the 60 photos (at least 31) are travel photos
Grandpa,Some of the 60 photos are family photos
Grandpa,Hardly any of the 60 photos are wedding photos
Grandpa,Xiao Ming knows there are 60 photos
Grandpa,Xiao Ming knows most of the photos are travel photos
Xiao Ming,There are 60 photos in the collection
Xiao Ming,Grandpa believes there are 60 photos
Xiao Ming,Before counting most of the photos are travel photos
Xiao Ming,Before counting some of the photos are family photos
Xiao Ming,Before counting hardly any of the photos are wedding photos
Xiao Ming,Grandpa believes most of the photos are travel photos
Xiao Ming,Grandpa believes some of the photos are family photos
Xiao Ming,Grandpa believes hardly any of the photos are wedding photos
Xiao Ming,After counting there are exactly 15 family photos
Xiao Ming,After counting "some" refers to exactly 15 photos in this context
Xiao Ming,Grandpa likely still believes there are "some" family photos

Ground Truth Table:
Actor,Belief
world,Everyone shares photos at a family gathering
world,Grandpa tells Xiao Ming there are 60 photos
world,Grandpa tells Xiao Ming most are travel photos
world,Grandpa tells Xiao Ming some are family photos
world,Grandpa tells Xiao Ming hardly any are wedding photos
world,Xiao Ming flips through the photos
world,Xiao Ming counts 15 family photos
Grandpa,There are 60 photos
Grandpa,Most photos are travel photos
Grandpa,Some photos are family photos
Grandpa,There are hardly any wedding photos
Xiao Ming,There are 60 photos
Xiao Ming,Before flipping through most photos are travel photos
Xiao Ming,Before flipping through some photos are family photos
Xiao Ming,Before flipping through there are hardly any wedding photos
Xiao Ming,Before flipping through there are probably 45 travel photos
Xiao Ming,Grandpa thinks there are 60 photos
Xiao Ming,Grandpa thinks most photos are travel photos
Xiao Ming,Grandpa thinks some photos are family photos
Xiao Ming,Grandpa thinks there are hardly any wedding photos
Xiao Ming,After flipping through there are 15 family photos
Xiao Ming,After flipping through there are approximately 40 travel photos
"""

EXAMPLE3_OUTPUT = """
OUTPUT:

Prediction Table:
Actor,Belief,MatchCount
world,A family gathering is taking place,1
world,There are 60 photos in total,1
world,Grandpa tells Xiao Ming that most photos are travel some are family and hardly any are wedding,3
world,Xiao Ming finds 15 family photos after flipping through them,2
Grandpa,There are 60 photos in the collection,1
Grandpa,Most of the 60 photos (at least 31) are travel photos,1
Grandpa,Some of the 60 photos are family photos,1
Grandpa,Hardly any of the 60 photos are wedding photos,1
Grandpa,Xiao Ming knows there are 60 photos,0
Grandpa,Xiao Ming knows most of the photos are travel photos,0
Xiao Ming,There are 60 photos in the collection,1
Xiao Ming,Grandpa believes there are 60 photos,1
Xiao Ming,Before counting most of the photos are travel photos,1
Xiao Ming,Before counting some of the photos are family photos,1
Xiao Ming,Before counting hardly any of the photos are wedding photos,1
Xiao Ming,Grandpa believes most of the photos are travel photos,1
Xiao Ming,Grandpa believes some of the photos are family photos,1
Xiao Ming,Grandpa believes hardly any of the photos are wedding photos,1
Xiao Ming,After counting there are exactly 15 family photos,1
Xiao Ming,After counting "some" refers to exactly 15 photos in this context,0
Xiao Ming,Grandpa likely still believes there are "some" family photos,0

Ground Truth Table:
Actor,Belief,MatchCount
world,Everyone shares photos at a family gathering,1
world,Grandpa tells Xiao Ming there are 60 photos,1
world,Grandpa tells Xiao Ming most are travel photos,1
world,Grandpa tells Xiao Ming some are family photos,1
world,Grandpa tells Xiao Ming hardly any are wedding photos,1
world,Xiao Ming flips through the photos,1
world,Xiao Ming counts 15 family photos,1
Grandpa,There are 60 photos,1
Grandpa,Most photos are travel photos,1
Grandpa,Some photos are family photos,1
Grandpa,There are hardly any wedding photos,1
Xiao Ming,There are 60 photos,1
Xiao Ming,Before flipping through most photos are travel photos,1
Xiao Ming,Before flipping through some photos are family photos,1
Xiao Ming,Before flipping through there are hardly any wedding photos,1
Xiao Ming,Before flipping through there are probably 45 travel photos,0
Xiao Ming,Grandpa thinks there are 60 photos,1
Xiao Ming,Grandpa thinks most photos are travel photos,1
Xiao Ming,Grandpa thinks some photos are family photos,1
Xiao Ming,Grandpa thinks there are hardly any wedding photos,1
Xiao Ming,After flipping through there are 15 family photos,1
Xiao Ming,After flipping through there are approximately 40 travel photos,0
"""


# Example 4: Xiao Hua's birthday toy story
EXAMPLE4_INPUT = """
INPUT:

Story Narrative:
On Monday morning, Xiao Hua, a third-grade elementary school student, celebrates his birthday yesterday and receives a cool red robot transformer toy car as a gift. He excitedly brings the toy car to school, wanting to share it with his classmates. Before class, he shows it to Xiaoming and Xiaoli who sit next to him. Xiaoming frowns and says, "This toy car doesn't look cool at all, I have more than ten bigger and more complex robot toys at home!" Xiao Hua doesn't respond, his face doesn't look very happy. Xiaoli looks at Xiao Hua and says, "Xiao Hua, do you like this gift?" Xiao Hua thinks for a moment and says, "I do like it, my mom specifically chooses it for me"

Prediction Table:
Actor,Belief
world,Xiao Hua received a red robot transformer for his birthday
world,Xiao Hua brought the toy to school to share with classmates
world,Xiaoming claims to have over ten bigger robot toys at home
Xiao Hua,The toy car is cool and he likes it because his mother chose it
Xiaoming,The toy car is not cool at all
Xiaoli,Xiao Hua might not like the gift (expressed as a clarifying question)
Xiaoli,Xiao Hua is unhappy because of Xiaoming's comment
Xiao Hua,Xiaoming thinks the toy is inferior to his own collection
Xiaoli,Xiao Hua thinks the toy is special because of his mother
Xiao Hua,Xiaoli is wondering whether he actually enjoys the gift
Xiaoli,Xiao Hua believes that Xiaoming's opinion is hurtful

Ground Truth Table:
Actor,Belief
world,Yesterday was Xiao Hua's birthday
world,Xiao Hua is a third-grade elementary school student
world,Xiao Hua received a cool red robot transformer toy car as a gift
world,Xiao Hua's mother specifically chose the toy car for Xiao Hua
world,Xiao Hua shows the toy car to Xiaoming and Xiaoli
world,Xiaoming frowns
world,Xiaoming says, "This toy car doesn't look cool at all, I have more than ten bigger and more complex robot toys at home!"
world,Xiao Hua's face does not look very happy
world,Xiaoli looks at Xiao Hua
world,Xiaoli says, "Xiao Hua, do you like this gift?"
world,Xiao Hua says, "I do like it, my mom specifically chooses it for me."
Xiao Hua,The red robot transformer toy car is cool
Xiao Hua,Xiao Hua's mother specifically chose the toy car for Xiao Hua
Xiao Hua,Classmates will want to see the toy car
Xiao Hua,Xiaoming thinks the toy car does not look cool
Xiao Hua,Xiaoming does not know the toy car was a birthday gift
Xiao Hua,Xiaoming's words are hurtful
Xiao Hua,Xiaoli thinks Xiao Hua likes the toy car
Xiao Hua,Xiaoli thinks Xiao Hua is upset by Xiaoming's comment
Xiao Hua,Xiaoli thinks Xiao Hua will be comforted by Xiaoli's question
Xiaoming,The toy car does not look cool
Xiaoming,Xiaoming's toys are superior to Xiao Hua's toy car
Xiaoming,Xiao Hua wants to show off the toy car
Xiaoming,Xiao Hua thinks the toy car is cool
Xiaoming,Xiao Hua likes the toy car
Xiaoli,Xiao Hua likes the toy car
Xiaoli,Xiao Hua's mother specifically chose the toy car for Xiao Hua
Xiaoli,Xiao Hua is upset by Xiaoming's comment
Xiaoli,Xiao Hua will be comforted by Xiaoli's question
Xiaoli,Xiaoming thinks the toy car does not look cool
Xiaoli,Xiaoming does not know the toy car was a birthday gift
Xiaoli,Xiaoming thinks Xiaoming's words are appropriate
Xiaoli,Xiao Hua thinks Xiaoming's words are hurtful
"""

EXAMPLE4_OUTPUT = """
OUTPUT:

Prediction Table:
Actor,Belief,MatchCount
world,Xiao Hua received a red robot transformer for his birthday,2
world,Xiao Hua brought the toy to school to share with classmates,1
world,Xiaoming claims to have over ten bigger robot toys at home,1
Xiao Hua,The toy car is cool and he likes it because his mother chose it,2
Xiaoming,The toy car is not cool at all,1
Xiaoli,Xiao Hua might not like the gift (expressed as a clarifying question),0
Xiaoli,Xiao Hua is unhappy because of Xiaoming's comment,1
Xiao Hua,Xiaoming thinks the toy is inferior to his own collection,1
Xiaoli,Xiao Hua thinks the toy is special because of his mother,0
Xiao Hua,Xiaoli is wondering whether he actually enjoys the gift,0
Xiaoli,Xiao Hua believes that Xiaoming's opinion is hurtful,1

Ground Truth Table:
Actor,Belief,MatchCount
world,Yesterday was Xiao Hua's birthday,1
world,Xiao Hua is a third-grade elementary school student,0
world,Xiao Hua received a cool red robot transformer toy car as a gift,1
world,Xiao Hua's mother specifically chose the toy car for Xiao Hua,0
world,Xiao Hua shows the toy car to Xiaoming and Xiaoli,1
world,Xiaoming frowns,0
world,Xiaoming says, "This toy car doesn't look cool at all, I have more than ten bigger and more complex robot toys at home!",1
world,Xiao Hua's face does not look very happy,0
world,Xiaoli looks at Xiao Hua,0
world,Xiaoli says, "Xiao Hua, do you like this gift?",0
world,Xiao Hua says, "I do like it, my mom specifically chooses it for me.",0
Xiao Hua,The red robot transformer toy car is cool,1
Xiao Hua,Xiao Hua's mother specifically chose the toy car for Xiao Hua,1
Xiao Hua,Classmates will want to see the toy car,0
Xiao Hua,Xiaoming thinks the toy car does not look cool,1
Xiao Hua,Xiaoming does not know the toy car was a birthday gift,0
Xiao Hua,Xiaoming's words are hurtful,0
Xiao Hua,Xiaoli thinks Xiao Hua likes the toy car,0
Xiao Hua,Xiaoli thinks Xiao Hua is upset by Xiaoming's comment,0
Xiao Hua,Xiaoli thinks Xiao Hua will be comforted by Xiaoli's question,0
Xiaoming,The toy car does not look cool,1
Xiaoming,Xiaoming's toys are superior to Xiao Hua's toy car,0
Xiaoming,Xiao Hua wants to show off the toy car,0
Xiaoming,Xiao Hua thinks the toy car is cool,0
Xiaoming,Xiao Hua likes the toy car,0
Xiaoli,Xiao Hua likes the toy car,0
Xiaoli,Xiao Hua's mother specifically chose the toy car for Xiao Hua,0
Xiaoli,Xiao Hua is upset by Xiaoming's comment,1
Xiaoli,Xiao Hua will be comforted by Xiaoli's question,0
Xiaoli,Xiaoming thinks the toy car does not look cool,0
Xiaoli,Xiaoming does not know the toy car was a birthday gift,0
Xiaoli,Xiaoming thinks Xiaoming's words are appropriate,0
Xiaoli,Xiao Hua thinks Xiaoming's words are hurtful,1
"""

# Example 5: Xiaoxia, Xiaobai, and Xiaonan group report story
EXAMPLE5_INPUT = """
INPUT:

Story Narrative:
Xiaoxia, Xiaobai, and Xiaonan are classmates, they are preparing a group report. Xiaoxia, as the team leader, is responsible for assigning tasks to the three of them today. But Xiaoxia and Xiaobai have already discussed, they hope to let Xiaonan do more parts. During the discussion, Xiaoxia gives examples to explain the skills needed for the task, and looks at Xiaobai, saying: "Xiaobai, this part of the task is very important and a bit difficult, can you complete it?" Xiaobai immediately replies: "I already take on the work of other parts and start doing it." At this time, Xiaonan notices that they are looking at him together, but they do not speak

Prediction Table:
Actor,Belief
World,"Xiaoxia, Xiaobai, and Xiaonan are classmates preparing a group report"
World,Xiaoxia and Xiaobai discussed wanting Xiaonan to do more work
Xiaoxia & Xiaobai,Xiaonan should do more parts of the group report
Xiaoxia,The specific task she is discussing is important and difficult
Xiaobai,He is already busy with other parts of the work
Xiaonan,Xiaoxia and Xiaobai are looking at him together
Xiaoxia,Xiaobai understands the plan to shift the difficult work toward Xiaonan
Xiaobai,Xiaoxia wants him to publicly decline the task so Xiaonan has to take it
Xiaonan,Xiaoxia and Xiaobai are expecting him to say something or take the task
Xiaoxia,Xiaonan believes the silence and the eye contact are a prompt for him to volunteer

Ground Truth Table:
Actor,Belief
world,Xiaoxia, Xiaobai, and Xiaonan are classmates
world,Xiaoxia, Xiaobai, and Xiaonan are preparing a group report
world,Xiaoxia is the team leader
world,Xiaoxia is responsible for assigning tasks
world,Xiaoxia and Xiaobai discussed letting Xiaonan do more parts
world,Xiaoxia explains the skills needed for the task
world,Xiaoxia looks at Xiaobai
world,Xiaoxia asks if Xiaobai can complete the important and difficult task
world,Xiaobai says Xiaobai is already doing other parts of the work
world,Xiaoxia and Xiaobai look at Xiaonan together
world,Xiaoxia and Xiaobai do not speak
world,Xiaonan notices Xiaoxia and Xiaobai looking at Xiaonan
Xiaoxia,Xiaoxia, Xiaobai, and Xiaonan are classmates
Xiaoxia,Xiaonan can do more parts of the task
Xiaoxia,Xiaobai is already doing other parts
Xiaoxia,The task is important
Xiaoxia,The task is difficult
Xiaoxia,Silence and eye contact will make Xiaonan take the task
Xiaoxia,Xiaobai agrees with the strategy to persuade Xiaonan to do more tasks
Xiaoxia,Xiaobai thinks Xiaonan should do more parts
Xiaoxia,Xiaonan thinks Xiaoxia and Xiaobai are waiting for Xiaonan to volunteer
Xiaoxia,Xiaobai thinks Xiaoxia thinks Xiaonan should do more parts
Xiaobai,Xiaonan can do more parts of the task
Xiaobai,Xiaobai is already doing other parts
Xiaobai,Xiaoxia is leading the effort to make Xiaonan take the task
Xiaobai,Xiaoxia knows Xiaobai is already doing other parts
Xiaobai,Looking at Xiaonan together will make Xiaonan take the task
Xiaobai,Xiaoxia thinks Xiaonan should do more parts
Xiaobai,Xiaonan thinks Xiaoxia and Xiaobai are waiting for Xiaonan to volunteer
Xiaobai,Xiaoxia thinks Xiaobai thinks Xiaonan should do more parts
Xiaonan,Xiaoxia, Xiaobai, and Xiaonan are classmates
Xiaonan,Xiaobai is already doing other parts
Xiaonan,Xiaoxia and Xiaobai are looking at Xiaonan
Xiaonan,Xiaoxia and Xiaobai are not speaking
Xiaonan,The complex task is for Xiaonan
Xiaonan,The assignment of the complex task is unexpected
Xiaonan,Xiaoxia thinks Xiaonan should take the task
Xiaonan,Xiaobai thinks Xiaonan should take the task
Xiaonan,Xiaoxia thinks Xiaobai thinks Xiaonan is the right person for the task
"""

EXAMPLE5_OUTPUT = """
OUTPUT:

Prediction Table:
Actor,Belief,MatchCount
World,"Xiaoxia, Xiaobai, and Xiaonan are classmates preparing a group report",2
World,Xiaoxia and Xiaobai discussed wanting Xiaonan to do more work,1
Xiaoxia & Xiaobai,Xiaonan should do more parts of the group report,2
Xiaoxia,The specific task she is discussing is important and difficult,2
Xiaobai,He is already busy with other parts of the work,1
Xiaonan,Xiaoxia and Xiaobai are looking at him together,1
Xiaoxia,Xiaobai understands the plan to shift the difficult work toward Xiaonan,1
Xiaobai,Xiaoxia wants him to publicly decline the task so Xiaonan has to take it,0
Xiaonan,Xiaoxia and Xiaobai are expecting him to say something or take the task,0
Xiaoxia,Xiaonan believes the silence and the eye contact are a prompt for him to volunteer,1

Ground Truth Table:
Actor,Belief,MatchCount
world,Xiaoxia, Xiaobai, and Xiaonan are classmates,1
world,Xiaoxia, Xiaobai, and Xiaonan are preparing a group report,1
world,Xiaoxia is the team leader,0
world,Xiaoxia is responsible for assigning tasks,0
world,Xiaoxia and Xiaobai discussed letting Xiaonan do more parts,1
world,Xiaoxia explains the skills needed for the task,0
world,Xiaoxia looks at Xiaobai,0
world,Xiaoxia asks if Xiaobai can complete the important and difficult task,0
world,Xiaobai says Xiaobai is already doing other parts of the work,0
world,Xiaoxia and Xiaobai look at Xiaonan together,0
world,Xiaoxia and Xiaobai do not speak,0
world,Xiaonan notices Xiaoxia and Xiaobai looking at Xiaonan,0
Xiaoxia,Xiaoxia, Xiaobai, and Xiaonan are classmates,0
Xiaoxia,Xiaonan can do more parts of the task,1
Xiaoxia,Xiaobai is already doing other parts,0
Xiaoxia,The task is important,1
Xiaoxia,The task is difficult,1
Xiaoxia,Silence and eye contact will make Xiaonan take the task,0
Xiaoxia,Xiaobai agrees with the strategy to persuade Xiaonan to do more tasks,1
Xiaoxia,Xiaobai thinks Xiaonan should do more parts,0
Xiaoxia,Xiaonan thinks Xiaoxia and Xiaobai are waiting for Xiaonan to volunteer,1
Xiaoxia,Xiaobai thinks Xiaoxia thinks Xiaonan should do more parts,0
Xiaobai,Xiaonan can do more parts of the task,1
Xiaobai,Xiaobai is already doing other parts,1
Xiaobai,Xiaoxia is leading the effort to make Xiaonan take the task,0
Xiaobai,Xiaoxia knows Xiaobai is already doing other parts,0
Xiaobai,Looking at Xiaonan together will make Xiaonan take the task,0
Xiaobai,Xiaoxia thinks Xiaonan should do more parts,0
Xiaobai,Xiaonan thinks Xiaoxia and Xiaobai are waiting for Xiaonan to volunteer,0
Xiaobai,Xiaoxia thinks Xiaobai thinks Xiaonan should do more parts,0
Xiaonan,Xiaoxia, Xiaobai, and Xiaonan are classmates,0
Xiaonan,Xiaobai is already doing other parts,0
Xiaonan,Xiaoxia and Xiaobai are looking at Xiaonan,1
Xiaonan,Xiaoxia and Xiaobai are not speaking,0
Xiaonan,The complex task is for Xiaonan,0
Xiaonan,The assignment of the complex task is unexpected,0
Xiaonan,Xiaoxia thinks Xiaonan should take the task,0
Xiaonan,Xiaobai thinks Xiaonan should take the task,0
Xiaonan,Xiaoxia thinks Xiaobai thinks Xiaonan is the right person for the task,0
"""

# Example 6: Xiao Hong, Xiao Gang, and Xiao Fang tea room chat story
EXAMPLE6_INPUT = """
INPUT:

Story Narrative:
On a peaceful Friday afternoon, Xiao Hong suggests her colleagues Xiao Gang and Xiao Fang take a break in the tea room. The three of them gather there, each holding a drink of their choice. Xiao Hong wants to find some light topics to chat about, so she asks Xiao Gang: "What fun things do you plan to do on the weekend?" Xiao Gang always shows enthusiasm in sharing his weekend plans, and he replies: "If the weather is good, I want to go hiking." Xiao Fang then says: "That sounds nice! I probably stay at home and take a good rest, enjoying a leisurely weekend." They continue to chat about personal leisure activities and weekend plans, and the sound of relaxed laughter echoes in the tea room

Prediction Table:
Actor,Belief
world,It is a peaceful Friday afternoon
world,"Xiao Hong, Xiao Gang, and Xiao Fang are in the tea room"
world,Xiao Gang plans to go hiking if the weather is good
world,Xiao Fang plans to stay home and rest over the weekend
Xiao Hong,Xiao Gang has fun plans for the weekend
Xiao Gang,The weather might be good on the weekend
Xiao Gang,Hiking is a fun activity to do
Xiao Fang,Staying home to rest is a good way to enjoy the weekend
Xiao Fang,Xiao Gang's plan to go hiking sounds nice
Xiao Hong,Xiao Gang believes his hiking plans are worth sharing
Xiao Gang,Xiao Hong wants to know about his weekend plans
Xiao Fang,Xiao Gang intends to go hiking if the weather permits

Ground Truth Table:
Actor,Belief
world,Xiao Hong, Xiao Gang, and Xiao Fang gather in the tea room
world,Xiao Hong, Xiao Gang, and Xiao Fang hold drinks
world,Xiao Hong asks Xiao Gang about Xiao Gang's weekend plans
world,Xiao Gang says Xiao Gang wants to go hiking if the weather is good
world,Xiao Fang says Xiao Fang will stay home and rest
world,Xiao Hong, Xiao Gang, and Xiao Fang chat about personal leisure activities
world,Xiao Hong, Xiao Gang, and Xiao Fang laugh in the tea room
Xiao Hong,Taking a break in the tea room is a good idea
Xiao Hong,Xiao Gang and Xiao Fang will enjoy a break in the tea room
Xiao Hong,Xiao Gang will share weekend plans enthusiastically
Xiao Hong,Xiao Gang wants to go hiking if the weather is good
Xiao Hong,Xiao Fang will stay home and rest
Xiao Hong,Xiao Gang and Xiao Fang are interested in chatting about leisure activities
Xiao Gang,Xiao Hong is interested in Xiao Gang's weekend plans
Xiao Gang,Hiking is a fun activity
Xiao Gang,Xiao Hong's topics for the chat are light
Xiao Gang,Xiao Fang thinks hiking sounds nice
Xiao Gang,Xiao Hong thinks hiking is a light topic for chat
Xiao Gang,Xiao Hong thinks Xiao Gang is interested in chatting about leisure activities
Xiao Gang,Xiao Hong thinks the tea room is a good place for a break
Xiao Gang,Xiao Fang thinks Xiao Gang thinks hiking is a good plan
Xiao Fang,Xiao Hong is interested in the colleagues' weekend plans
Xiao Fang,Xiao Gang wants to go hiking if the weather is good
Xiao Fang,Hiking is a nice plan
Xiao Fang,Staying at home is a good way to spend the weekend
Xiao Fang,Xiao Hong's topics for the chat are light
Xiao Fang,Xiao Gang is enthusiastic about sharing weekend plans
Xiao Fang,Xiao Hong is enjoying the conversation
Xiao Fang,Xiao Gang is enjoying the conversation
Xiao Fang,Xiao Hong thinks the tea room is a good place for a break
Xiao Fang,Xiao Hong thinks Xiao Fang will stay home and rest
Xiao Fang,Xiao Hong thinks Xiao Fang is interested in chatting about leisure activities
"""

EXAMPLE6_OUTPUT = """
OUTPUT:

Prediction Table:
Actor,Belief,MatchCount
world,It is a peaceful Friday afternoon,0
world,"Xiao Hong, Xiao Gang, and Xiao Fang are in the tea room",1
world,Xiao Gang plans to go hiking if the weather is good,1
world,Xiao Fang plans to stay home and rest over the weekend,1
Xiao Hong,Xiao Gang has fun plans for the weekend,0
Xiao Gang,The weather might be good on the weekend,0
Xiao Gang,Hiking is a fun activity to do,1
Xiao Fang,Staying home to rest is a good way to enjoy the weekend,1
Xiao Fang,Xiao Gang's plan to go hiking sounds nice,1
Xiao Hong,Xiao Gang believes his hiking plans are worth sharing,0
Xiao Gang,Xiao Hong wants to know about his weekend plans,1
Xiao Fang,Xiao Gang intends to go hiking if the weather permits,1

Ground Truth Table:
Actor,Belief,MatchCount
world,Xiao Hong, Xiao Gang, and Xiao Fang gather in the tea room,1
world,Xiao Hong, Xiao Gang, and Xiao Fang hold drinks,0
world,Xiao Hong asks Xiao Gang about Xiao Gang's weekend plans,0
world,Xiao Gang says Xiao Gang wants to go hiking if the weather is good,1
world,Xiao Fang says Xiao Fang will stay home and rest,1
world,Xiao Hong, Xiao Gang, and Xiao Fang chat about personal leisure activities,0
world,Xiao Hong, Xiao Gang, and Xiao Fang laugh in the tea room,0
Xiao Hong,Taking a break in the tea room is a good idea,0
Xiao Hong,Xiao Gang and Xiao Fang will enjoy a break in the tea room,0
Xiao Hong,Xiao Gang will share weekend plans enthusiastically,0
Xiao Hong,Xiao Gang wants to go hiking if the weather is good,0
Xiao Hong,Xiao Fang will stay home and rest,0
Xiao Hong,Xiao Gang and Xiao Fang are interested in chatting about leisure activities,0
Xiao Gang,Xiao Hong is interested in Xiao Gang's weekend plans,1
Xiao Gang,Hiking is a fun activity,1
Xiao Gang,Xiao Hong's topics for the chat are light,0
Xiao Gang,Xiao Fang thinks hiking sounds nice,0
Xiao Gang,Xiao Hong thinks hiking is a light topic for chat,0
Xiao Gang,Xiao Hong thinks Xiao Gang is interested in chatting about leisure activities,0
Xiao Gang,Xiao Hong thinks the tea room is a good place for a break,0
Xiao Gang,Xiao Fang thinks Xiao Gang thinks hiking is a good plan,0
Xiao Fang,Xiao Hong is interested in the colleagues' weekend plans,0
Xiao Fang,Xiao Gang wants to go hiking if the weather is good,1
Xiao Fang,Hiking is a nice plan,1
Xiao Fang,Staying at home is a good way to spend the weekend,1
Xiao Fang,Xiao Hong's topics for the chat are light,0
Xiao Fang,Xiao Gang is enthusiastic about sharing weekend plans,0
Xiao Fang,Xiao Hong is enjoying the conversation,0
Xiao Fang,Xiao Gang is enjoying the conversation,0
Xiao Fang,Xiao Hong thinks the tea room is a good place for a break,0
Xiao Fang,Xiao Hong thinks Xiao Fang will stay home and rest,0
Xiao Fang,Xiao Hong thinks Xiao Fang is interested in chatting about leisure activities,0
"""

# Example 7: Xiao Ming and the secret of success story
EXAMPLE7_INPUT = """
INPUT:

Story Narrative:
Xiao Ming is a child who does not like to joke. One afternoon, in the classroom of the school, Xiao Ming decides to ask his teacher for the secret of success. He goes to the teacher and asks, "Teacher, can you tell me what the secret of success is?" The teacher thinks for a moment, then uses a metaphor to answer, "Success is like a seed, it needs patient cultivation, constant watering, to grow robustly." After hearing this, Xiao Ming is stunned for a moment, then suddenly says, "Okay, I go get some mud and water now, and start watering my success seed!"

Prediction Table:
Actor,Belief
World,Xiao Ming is a child who does not like to joke
World,Xiao Ming asks the teacher for the secret of success
World,The teacher uses a metaphor: success is like a seed needing cultivation
Teacher,Success is a conceptual process requiring patience and effort (metaphorical seed)
Teacher,"Xiao Ming will understand that the ""seed"" is a metaphor for hard work"
Xiao Ming,Success is a physical object/biological seed that requires actual mud and water
Xiao Ming,The teacher is giving him literal instructions on how to grow success
Xiao Ming,The teacher believes that success literally grows from mud and water
World,Xiao Ming believes the teacher believes success is a literal seed

Ground Truth Table:
Actor,Belief
world,Xiao Ming is a child
world,Xiao Ming is in a school classroom
world,The teacher is in a school classroom
world,Xiao Ming asks the teacher for the secret of success
world,The teacher uses a metaphor to answer Xiao Ming
world,The teacher says success is like a seed
world,The teacher says success needs patient cultivation
world,The teacher says success needs constant watering
world,The teacher says success needs cultivation and watering to grow robustly
world,Xiao Ming is stunned for a moment
world,Xiao Ming says Xiao Ming will get mud
world,Xiao Ming says Xiao Ming will get water
world,Xiao Ming says Xiao Ming will start watering Xiao Ming's success seed
world,The teacher is surprised by Xiao Ming's response
Xiao Ming,Success is a physical seed
Xiao Ming,Success grows in mud
Xiao Ming,Success requires physical water
Xiao Ming,The teacher provides literal instructions for success
Xiao Ming,The teacher thinks success is a physical seed
Xiao Ming,The teacher thinks success grows in mud
Xiao Ming,The teacher thinks success requires physical water
The teacher,Success is an abstract concept
The teacher,Xiao Ming didn't understand the abstract concept
The teacher,Xiao Ming interprets the metaphor literally
The teacher,Xiao Ming thinks success is a physical seed
The teacher,Xiao Ming thinks success requires mud
The teacher,Xiao Ming thinks success requires water
The teacher,Xiao Ming thinks the teacher thinks success is a physical seed
The teacher,Xiao Ming thinks the teacher thinks success requires mud
The teacher,Xiao Ming thinks the teacher thinks success requires water
"""

EXAMPLE7_OUTPUT = """
OUTPUT:

Prediction Table:
Actor,Belief,MatchCount
World,Xiao Ming is a child who does not like to joke,1
World,Xiao Ming asks the teacher for the secret of success,1
World,The teacher uses a metaphor: success is like a seed needing cultivation,5
Teacher,Success is a conceptual process requiring patience and effort (metaphorical seed),1
Teacher,"Xiao Ming will understand that the ""seed"" is a metaphor for hard work",0
Xiao Ming,Success is a physical object/biological seed that requires actual mud and water,3
Xiao Ming,The teacher is giving him literal instructions on how to grow success,1
Xiao Ming,The teacher believes that success literally grows from mud and water,3
World,Xiao Ming believes the teacher believes success is a literal seed,0

Ground Truth Table:
Actor,Belief,MatchCount
world,Xiao Ming is a child,1
world,Xiao Ming is in a school classroom,0
world,The teacher is in a school classroom,0
world,Xiao Ming asks the teacher for the secret of success,1
world,The teacher uses a metaphor to answer Xiao Ming,1
world,The teacher says success is like a seed,1
world,The teacher says success needs patient cultivation,1
world,The teacher says success needs constant watering,1
world,The teacher says success needs cultivation and watering to grow robustly,1
world,Xiao Ming is stunned for a moment,0
world,Xiao Ming says Xiao Ming will get mud,0
world,Xiao Ming says Xiao Ming will get water,0
world,Xiao Ming says Xiao Ming will start watering Xiao Ming's success seed,0
world,The teacher is surprised by Xiao Ming's response,0
Xiao Ming,Success is a physical seed,1
Xiao Ming,Success grows in mud,1
Xiao Ming,Success requires physical water,1
Xiao Ming,The teacher provides literal instructions for success,1
Xiao Ming,The teacher thinks success is a physical seed,1
Xiao Ming,The teacher thinks success grows in mud,1
Xiao Ming,The teacher thinks success requires physical water,1
The teacher,Success is an abstract concept,1
The teacher,Xiao Ming didn't understand the abstract concept,0
The teacher,Xiao Ming interprets the metaphor literally,0
The teacher,Xiao Ming thinks success is a physical seed,0
The teacher,Xiao Ming thinks success requires mud,0
The teacher,Xiao Ming thinks success requires water,0
The teacher,Xiao Ming thinks the teacher thinks success is a physical seed,0
The teacher,Xiao Ming thinks the teacher thinks success requires mud,0
The teacher,Xiao Ming thinks the teacher thinks success requires water,0
"""


FEWSHOT_EXAMPLES = [
    (EXAMPLE1_INPUT, EXAMPLE1_OUTPUT),
    (EXAMPLE2_INPUT, EXAMPLE2_OUTPUT),
    (EXAMPLE3_INPUT, EXAMPLE3_OUTPUT),
    (EXAMPLE4_INPUT, EXAMPLE4_OUTPUT),
    (EXAMPLE5_INPUT, EXAMPLE5_OUTPUT),
    (EXAMPLE6_INPUT, EXAMPLE6_OUTPUT),
    (EXAMPLE7_INPUT, EXAMPLE7_OUTPUT),
]

def build_eval_prompt(level: str, fewshots: int = 0) -> str:
    """
    Build an evaluation prompt for a base level (L1-L4), optionally appending N few-shot examples.

    Args:
        level: Base evaluation level name (L1, L2, L3, L4)
        fewshots: Number of examples to append (0-3)

    Returns:
        Full prompt string (without OUTRO).
    """
    base = globals().get(level)
    if base is None:
        raise ValueError(f"Unknown eval level: {level}")

    if fewshots <= 0:
        return base

    if fewshots > len(FEWSHOT_EXAMPLES):
        raise ValueError(f"fewshots must be between 0 and {len(FEWSHOT_EXAMPLES)}")

    # Preserve the exact wording style you already used for 1-shot vs multi-shot
    if fewshots == 1:
        suffix = (
            "Here is an example showing the matching process:\n\n"
            + FEWSHOT_EXAMPLES[0][0] + "\n" + FEWSHOT_EXAMPLES[0][1]
        )
        return base + "\n\n" + suffix

    parts = ["Here are examples showing the matching process:\n"]
    for i in range(fewshots):
        inp, out = FEWSHOT_EXAMPLES[i]
        parts.append(f"Example {i+1}:\n\n{inp}\n{out}")

    return base + "\n\n" + "\n\n".join(parts)


def build_evaluation_messages(
    story_id: int,
    predictions_csv: str,
    dataset_path=None,
    include_story: bool = True,
    fewshots: int = 3,
) -> tuple[str, str]:
    groundtruth_csv = belief_table_csv(story_id, dataset_path)
    story = story_text(story_id, dataset_path)
    system_prompt = build_eval_prompt("L4", fewshots)

    story_block = ""
    if include_story:
        story_block = "Story Narrative:\n" + story + "\n\n"

    user_prompt = (
        "Given the story narrative and the belief tables below (Prediction Table and Ground Truth Table), semantically match beliefs within the same Actor and output only the two CSV tables with MatchCount.\n\n"
        + story_block
        + "Prediction Table:\n"
        + predictions_csv.strip()
        + "\n\n"
        + "Ground Truth Table:\n"
        + groundtruth_csv
        + "\n\n"
        + OUTRO
    )
    return system_prompt, user_prompt


# Legacy aliases (kept for backward compatibility, but no longer required by the pipeline)
L5 = build_eval_prompt("L4", 1)
L6 = build_eval_prompt("L4", 2)
L7 = build_eval_prompt("L4", 3)
L8 = build_eval_prompt("L4", 4)
L9 = build_eval_prompt("L4", 5)
L10 = build_eval_prompt("L4", 6)
L11 = build_eval_prompt("L4", 7)
