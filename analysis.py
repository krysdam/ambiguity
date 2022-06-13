import csv
import sys
from scipy import stats
import unittest

###################################################################################################

# CURRENT CONFIDENCE IN RESULTS
# 80% sure that they are 100% correct
# 96% sure that they are  99% correct (eg, a few numbers wrong by a few percent)

# TODO
#  - rethink abstractions so everything isn't touching everything
#       - simplify Person: fields are only essential things, functions shouldn't repeat
#  - check again that I'm using the right stats functions
#  - automate tests for "automate first" values
#  - automate tests for "leave for later" values
#  - tell Amy Dibattista that I'm taking over Harrison's post

# Questions
#  - "None of the above" is illegal or counted separate?
#  - What is the null-hypothesis for illegal%?
#    Can't be 0%, which is our alternative hypothesis.
#    50% seems wrong, since our null for High and Low are both 50% too.
#    33% for each? Assuming there are three types of answers, this is "chance"
#    But chance among the answers is actually 1/5 high, 1/5 low, 3/5 illegal
#    Not that it likely matters, since high is significantly high and illegal is significantly low by a long shot each
#    Janet: null hypothesis isn't "high=50%", it's "high=low"
#      Why? Shouldn't all four/five answers be equally likely?
#      Blessing high and low presupposes unbreakable syntax.
#      Or maybe we have a "syntax" null-h which says that all are equal,
#      then when that's disproven, the "interpretation" null-h claims that the two syntactically permitted answers are equal too
#  - Time cutoff = 3.5 reasonable? (arbitrary!)

# Warnings
#  - counts vs percent

# Verification chain
# Automate first
#   csv rows        --> Persons (id, name, row)
#   Person          --> ab_sequence, ab_pattern
#   Person          --> TQ_complete, DQ_complete, DQ_correct
#   Person          --> include   (wo time cutoff)
#   Person          --> average_time_a, average_time_b, average_time
#   Person          --> time good (w time cutoff)
#   Person          --> include   (w time cutoff)
#   Person          --> answer_counts
# Leave for later
# because it will be transparently correct.
#  [Person] f       --> average & stdev of [f(P)]
#  [Person] f  h    --> t-test of [f(P)] vs hypothesis h
#  [Person] f1 f2   --> t-test of [f1(P)] vs [f2(P)]

# "Chance"
# 2 conjuncts: illegal, low, high, illegal          = 25   25   50
# 3 conjuncts: illegal, illegal, low, high, illegal = 20   20   60

# Exp1 = equal mix 2 and 3 conjuncts                = 22.5 22.5 55
# Exp2 = all 2 conjuncts                            = 25   25   50
# Exp3 = all 2 conjuncts                            = 25   25   50


# OVERVIEW ########################################################################################

# We're running three experiments.
# Experiment 1:
#   A = VP          "Kyle likes to watch [sitcoms] and [movies] [with his friends]"
#   B = NP          "Kyle likes to watch [sitcoms] and [movies] [with famous actors]"
# Experiment 2:
#   A = no bias     "[Athletes] and [photographers] [with their gear] waited by the van"
#   B = low bias    "[Athletes] and [photographers] [with their cameras] waited by the van"
# Experiment 3:
#   A = no bias     "[Photographers] and [athletes] [with their gear] waited by the van"
#   B = high bias   "[Photographers] and [athletes] [with their cameras] waited by the van"
# Answer kinds:
#   Low attachment      "movies"
#   High attachment     "sitcoms and movies"
#   Illegal             "sitcoms" (how can the PP "jump over" the last conjunct?)
#   None of the above   "None of the above" (an option in all questions)
# But:


# UTIL FUNCTIONS ##################################################################################

def header(s, n):
    """
    Util function: Print a header, which is a string with a bunch of hyphens after it:
    -- TIME --------------------
    s: the string (eg "TIME")
    n: the header width
    """
    print("\n-- {} {}".format(s, "-"*(n - 4 - len(s))))

def usage_exit():
    """ Print usage explanation, and exit. """
    print("Correct usage:")
    print("  python3 exclude.py EXP FILE")
    print("where")
    print("  EXP is the experiment number (eg, 1, 2, or 3)")
    print("  FILE is the filename of the csv of data")
    print("Example:")
    print("  python3 exclude.py 2 ambi-data.csv")
    exit()



# DATA: TEST QUESTIONS ############################################################################

# Enum for condition type
# A and B are actual conditions of the study.
# If they didn't answer the question, I don't know what condition they saw,
# so I record that as MISS.
A = 0
B = 1
MISS = 2

# Enum for answer kind
# High attachment, low attachment, illegal attachment, "None of the above"
HIGH = 3
LOW = 4
ILLEGAL = 5
NONE = 6

class TQuestion():
    """
    A test-question.
    To identify whether a given answer is "high," "low," "illegal," or "none of the above."
    Parameters:
        conj1: the first conjunct                (eg "cars" or "singers")
        conj2: the second conjunct               (eg "mopeds" or "dancers")
        conj3: the last conjunct if there is one (eg "trucks" or None)
        atb:   the "across the board" answer     (eg "cars mopeds and trucks")
    """
    def __init__(self, conj1, conj2, conj3=None, atb=None):
        # ATB is usually just "conj1 and conj2" or "conj1 conj2 and conj3"
        # but if it's ever different, need a way to specify what it really is
        self.conj1 = conj1
        self.conj2 = conj2
        self.conj3 = conj3
        if atb:
            self.atb = atb
        else:
            if conj3:
                self.atb = conj1 + " " + conj2 + " and " + conj3
            else:
                self.atb = conj1 + " and " + conj2

    def flatten(s):
        """
        Flatten a string into just space-separated lowercase words.
            "The singers" --> "singers"
            "The cars, the mopeds, and the trucks" --> "cars mopeds and trucks"
            "The half-and-half" --> "half-and-half"
        Assume: s itself is space-separated words with commas and periods
        """
        # Lowercase and punctuation
        s = s.lower()
        s = s.replace(".", "").replace(",", "")
        
        # Split into words, remove "the"
        words = s.split(" ")
        words = [w for w in words if w != "the"]

        # Join with spaces
        return " ".join(words)

    def attachment(self, answer):
        """ Is the given answer high, low, illegal, or none-of-the-above? (for this question) """
        if answer == "None of the above":
            return NONE
        flat = TQuestion.flatten(answer)
        if flat == self.atb:
            return HIGH
        if self.conj3:
            if flat == self.conj3:
                return LOW
        else:
            if flat == self.conj2:
                return LOW
        return ILLEGAL

# Test Questions for each experiment
# Experiment has some 2-conjunct and some 3-conjunct
TQs = {1:  {1:  TQuestion("cars",          "mopeds",           "trucks"),
            2:  TQuestion("books",         "pamphlets",        "maps"),
            3:  TQuestion("sandwiches",    "soups",            "salads"),
            4:  TQuestion("laptops",       "tablets",          "phones"),
            5:  TQuestion("chopsticks",    "fortune cookies"),
            6:  TQuestion("singers",       "dancers"),
            7:  TQuestion("chairs",        "couches"),
            8:  TQuestion("sitcoms",       "comedy movies"),
            9:  TQuestion("news",          "interviews"),
            10: TQuestion("monkeys",       "mice"),
            11: TQuestion("ceramics",      "sculptures",       "collages"),
            12: TQuestion("skateboards",   "scooters",         "bikes")},
# Experiment 2 is all two-conjuncts:
       2:  {1:  TQuestion("athletes",      "photographers"),
            2:  TQuestion("dancers",       "musicians"),
            3:  TQuestion("books",         "magazines"),
            4:  TQuestion("pies",          "cakes"),
            5:  TQuestion("horror movies", "comedies"),
            6:  TQuestion("plates",        "cups"),
            7:  TQuestion("deserts",       "forests"),
            8:  TQuestion("coffee",        "tea"),
            9:  TQuestion("tee-shirts",    "sweatshirts"),
            10: TQuestion("cats",          "dogs"),
            11: TQuestion("customers",     "waiters"),
            12: TQuestion("schools",       "apartments")},
# Experiment 3 is the same as Experiment 2 but swapped orders
       3:  {1:  TQuestion("photographers", "athletes"),
            2:  TQuestion("musicians",     "dancers"),
            3:  TQuestion("magazines",     "books"),
            4:  TQuestion("cakes",         "pies"),
            5:  TQuestion("comedies",      "horror movies"),
            6:  TQuestion("cups",          "plates"),
            7:  TQuestion("forests",       "deserts"),
            8:  TQuestion("tea",           "coffee"),
            9:  TQuestion("sweatshirts",   "tee-shirts"),
            10: TQuestion("dogs",          "cats"),
            11: TQuestion("waiters",       "customers"),
            12: TQuestion("apartments",    "schools")}}



# DATA: DISTRACTOR QUESTIONS ######################################################################

# The patterns of "a versions" and "b versions" across the 12 questions
# in each of the five "non-prime" patterns
# in each of the three experiments
# {experiment: {pattern-name: [pattern as a list]}}
# Spaced strangely for easy transcription and to reduce eye strain :)
patterns = {1: {1: [B,A,B,  A,A,A,  B,B,A,  A,B,B],
                2: [A,B,A,  A,B,B,  B,A,A,  B,A,B],
                3: [B,A,B,  A,B,B,  A,A,A,  B,A,B],
                4: [A,A,B,  B,B,A,  A,B,B,  A,B,A],
                5: [A,A,B,  A,A,B,  B,B,A,  B,A,B]},
            2: {1: [A,B,A,  B,B,B,  B,A,A,  A,B,A],
                2: [A,B,B,  B,A,A,  A,B,A,  B,A,B],
                3: [A,B,B,  B,B,B,  A,B,A,  A,A,A],
                4: [B,A,B,  A,A,A,  B,B,A,  B,A,B],
                5: [A,A,B,  A,B,B,  A,B,A,  B,A,B]},
            3: {1: [B,B,B,  A,A,A,  A,A,B,  A,B,B],
                2: [B,B,B,  A,A,B,  A,A,B,  A,B,A],
                3: [B,A,A,  A,B,A,  B,B,A,  B,B,A],
                4: [B,B,A,  A,B,A,  A,A,B,  B,A,B],
                5: [A,B,A,  B,A,A,  A,A,B,  B,B,B]}}

def which_pattern(ab_sequence, experiment_number):
    """
    Identify the pattern of the string of 12 a's and b's
    abString: a string of 12 a's and b's
    output: "1" or "1~" or "2" ... up to "5~"
    """
    if MISS in ab_sequence:
        return None
    for i in range(1, 5+1):
        # Pattern i
        patterni = patterns[experiment_number][i]
        # Exact match
        if ab_sequence == patterni:
            return str(i)
        # Invert is an exact match
        elif [{A:B, B:A, MISS:None}[condition] for condition in ab_sequence] == patterni:
            return str(i) + "~"
    return None

# Right answers for the distractors.
# Store as lists, in case we want to change some of these later
# (eg, if we decide to remove "The clock" as a correct answer for question 7)
# Questions 1-6 have only one right answer:
distractor_answers = {1:  ["The sweater"],
                      2:  ["His horse"],
                      3:  ["The tango"],
                      4:  ["His brand-new car"],
                      5:  ["Bread"],
                      6:  ["His dog"],
# Questions 7-12 have one wrong answer, and one understandable-but-technically-wrong answer.
# Strictly, "I don't know" is the only accurate answer.
# Virtually everybody puts the understandable-but-technically-wrong answer.
# so we count these as correct too:
                      7:  ["The clock", "I don't know"],
                      8:  ["Dinner",    "I don't know"],
                      9:  ["The water", "I don't know"],
                      10: ["A mile",    "I don't know"],
                      11: ["The car",   "I don't know"],
                      12: ["Novels",    "I don't know"]}



# PARTICIPANTS (aka PEOPLE) #######################################################################

class Person():
    """
    A participant in the experiment. Corresponds to one row of the CSV.
        exp:            experiment number (1, 2, or 3)
        id:             unique id-string given by LUCID (eg "R_paPAFafpoFSH")
        name:           human name (eg, "Jordan Blah")
        ab_sequence:    sequence of TQs answered, eg, "abbababbab"
        ab_pattern:     named pattern of TQs given, eg, 3-prime
        TQ_complete:    completed every Test Question?
        DQ_complete:    completed every Distractor Question?
        DQ_correct:     correctly answered every Distractor Question? (that they answered)
        average_time:   average "Last Click" time across all Test Questions
        average_time_a,
         average_time_b average "Last Click" time across just A- or B-condition questions
        time_good:      is their average time above the cutoff?
        include:        pass every exclusion criteria? (= Include in the study)
        answer_counts: {condition (A or B):  {answer type (high, low...):  count}}
    """

    def __init__(self, row, experiment_number):
        self.exp          = experiment_number
        self.id           = row["ResponseId"]
        self.name         = "{} {}".format(row["Q3"], row["Q4"])
        self.ab_sequence  = Person.find_ab_sequence(row)
        self.ab_pattern   = which_pattern(self.ab_sequence, self.exp)
        self.TQ_complete  = self.ab_pattern != None
        self.DQ_complete  = Person.distractors_complete(row)
        self.DQ_correct   = Person.distractors_correct(row)
        self.average_time_a, self.average_time_b = Person.find_average_time(row)
        self.average_time = (self.average_time_a + self.average_time_b)/2
        self.time_good    = True
        self.include      = (self.TQ_complete
                             and self.DQ_complete and self.DQ_correct
                             and self.time_good)
        self.answer_counts = {A: {HIGH: 0, LOW: 0, ILLEGAL: 0, NONE: 0},
                              B: {HIGH: 0, LOW: 0, ILLEGAL: 0, NONE: 0}}
        self.count_kinds(row)

    def count_kinds(self, row):
        """ Count number of High, Low, Illegal, and None answers. """
        #for n in range(12):
        for n in [0]:
            # 'a' or 'b' or '-'
            condition = self.ab_sequence[n]
            if condition == MISS:
                continue
            if condition != A:
                self.TQ_complete = False
                continue
            # TQ1a or TQ1b, etc
            TQname = "TQ" + str(n+1) + {A:"a", B:"b"}[condition]
            # the actual Question
            TQ = TQs[self.exp][n+1]
            # their text answer
            answer = row[TQname]
            # reply kind
            kind = TQ.attachment(answer)
            #print(["High", "Low", "Ill", "Non"][kind], "\t", answer)
            self.answer_counts[condition][kind] += 1

    def find_ab_sequence(row):
        """
        The 12 conditions this person was given (A or B, or Miss if they didn't answer)
        row: CSV row dict of a person
        return: [List of 12 A, B, or MISS]
        """
        ab_sequence = []
        for n in range(12):
            # Check for "TQ1a" and "TQ1b", etc
            tq = "TQ" + str(n+1)
            # If they answered a, append A
            # if b, append B,
            # if neither, append MISS
            if row[tq + "a"]:
                ab_sequence.append(A)
            elif row[tq + "b"]:
                ab_sequence.append(B)
            else:
                ab_sequence.append(MISS)
        return ab_sequence

    def distractors_complete(row):
        """
        Did this person answer all Distractor Questions?
        row: CSV row dict of a person
        """
        for n in range(12):
            # Look for "DQ1" etc
            dq = "DQ" + str(n+1)
            # Value is empty, they missed the question
            if not row[dq]:
                return False
        return True

    def distractors_correct(row):
        """
        Did this person get every Distractor Question right?
          (of the ones they answered at all)
        row: CSV row dict of a person
        """
        for n in range(12):
            # Look for "DQ1" etc
            dq = "DQ" + str(n+1)
            # If they answered, compare to correct answers
            if row[dq] and (row[dq] not in distractor_answers[n+1]):
                return False
        return True

    def find_average_time(row):
        """
        Average time this person spent on all Test Questions
          (of the ones they answered at all)
        row: CSV row dict of a person
        output: average time in seconds
        """
        times_a = []
        times_b = []
        for n in range(12):
            # Between TQXa and TQXb, append any time you can find
            for aorb in "ab":
                last_click = "TQ{}{} TIME_Last Click".format(n+1, aorb)
                time = row[last_click]
                if time:
                    time = float(time)
                    if aorb == "a":
                        times_a.append(time)
                    if aorb == "b":
                        times_b.append(time)
        avg_a = sum(times_a) / (len(times_a) if len(times_a) else 1)
        avg_b = sum(times_b) / (len(times_b) if len(times_b) else 1)
        return (avg_a, avg_b)

    def set_time_cutoff(self, cutoff):
        """
        Set the minimum average answer-time (exclude people below this time).
        cutoff: the minimum time (in seconds)
        """
        self.time_good = self.average_time and (cutoff <= self.average_time)
        self.include = self.TQ_complete and self.DQ_complete and self.DQ_correct and self.time_good

    def __str__(self):
        #return "{}: {:<25}\t{}".format(self.id, self.name, self.TQ_complete)
        #return "{}: {:<25}\t{}\t{}".format(self.id, self.name, self.ab_sequence, self.ab_pattern)
        """
        #R_1nUbOZ2vAepbLaH: Soand Soh               	2	True	True	True	4.25	True
        """
        counts = self.answer_counts
        return "{}: {:<30}\t{}\t{}\t{}\t{}".format(self.id, self.name, self.ab_sequence, self.TQ_complete, self.DQ_complete, self.DQ_correct)

def read_people(file_name, experiment_number):
    """
    Read all participants from a csv file
    fname: name of the csv
    output: list of Persons
    """
    people = []
    with open(file_name, newline='') as csvfile:
        # Read in the csv as a dict, whose keys are the column headers
        rows = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        # Skip the second header row, which Qualtrics adds
        header = True
        for row in rows:
            if header:
                header = False
                continue
            # Skip the weird extra rows that say "ImportID" etc in them (non-data)
            if '{"ImportId"' in row["ResponseId"]:
                continue
            # Make the Person
            person = Person(row, experiment_number)
            people.append(person)
    return people


# EXCLUSION #######################################################################################

def exclusion_report(people):
    """ Report stats on how many people were excluded for which reasons. """
    # Total people, number included, number excluded
    count = len(people)
    include = len([p for p in people if p.include])
    exclude = count - include

    header("Sample size", 35)
    print("People:     \t{}".format(count))
    print("Included:   \t{:<2} ({:.0%})".format(include, include/count))
    print("Excluded:   \t{:<2} ({:.0%})".format(exclude, exclude/count))

    # Next, how many people were excluded for each reason, and how many for ONLY that reason?
    # We need this annoying function:
    # For a person p: were they excluded for exactly one reason?
    # In other words: do these four booleans sum to three?
    unique_criteria = (lambda p: p.TQ_complete + p.DQ_complete + p.DQ_correct + p.time_good == 3)

    def report_on_criteria(name, pred):
        """ Print number and percent of people who failed a specific criteria, and number who failed for only that reason. """
        have_problem =    len([p for p in people if pred(p)])
        unique_problem =  len([p for p in people if pred(p) and unique_criteria(p)])
        # TQ complete:  failed (failed%)    failed_only (failed_only%)
        print("{:<12}\t{:<2} ({:.0%}) \t{:<2} ({:.0%})".format(name, have_problem, have_problem/count, unique_problem, unique_problem/count))

    header("Exclusions", 35)
    print("            \tfailed\t\tfailed only")
    report_on_criteria("TQ complete", (lambda p: not p.TQ_complete))
    report_on_criteria("DQ complete", (lambda p: not p.DQ_complete))
    report_on_criteria("DQ correct",  (lambda p: not p.DQ_correct))
    report_on_criteria("time",        (lambda p: not p.time_good))


# ANALYSIS ########################################################################################

def analyze_sample(people, expected_high, expected_low, expected_illegal):
    print("N: {}".format(len(people)))

    print("\t\tA\t\tB")
    high = [(p.answer_counts[A][HIGH] + p.answer_counts[B][HIGH])/1 for p in people]
    low = [(p.answer_counts[A][LOW] + p.answer_counts[B][LOW])/1 for p in people]
    illegal = [(p.answer_counts[A][ILLEGAL] + p.answer_counts[B][ILLEGAL])/1 for p in people]
    none = [(p.answer_counts[A][NONE] + p.answer_counts[B][NONE])/1 for p in people]
    print("high:    \t{:<8.3}".format(stats.tmean(high)))
    print("low:     \t{:<8.3}".format(stats.tmean(low)))
    print("illegal: \t{:<8.3}".format(stats.tmean(illegal)))
    print("none:    \t{:<8.3}".format(stats.tmean(none)))
    print("high vs low: \t{:<8.3}".format(stats.ttest_rel(high, low).pvalue))

    exit()

    header("high", 35)
    # High attachment: mean(A), mean(B), p(A), p(B), p(A vs B)
    a_high = [P.answer_counts[A][HIGH]/6 for P in people]
    b_high = [P.answer_counts[B][HIGH]/6 for P in people]
    a_high_t, a_high_p = stats.ttest_1samp(a_high, expected_high)
    b_high_t, b_high_p = stats.ttest_1samp(b_high, expected_high)

    # Is the high% significantly higher than chance (ie, than 1/2)?
    print("mean:    \t{:<8.3}\t{:.3}".format(stats.tmean(a_high), stats.tmean(b_high)))
    print("t-test:  \t{:<8.3}\t{:.3}".format(a_high_t, b_high_t))
    print("p-value: \t{:<8.3}\t{:.3}".format(a_high_p, b_high_p))

    # Are the high% significantly different from each other?
    # Harrison used ttest_rel, TODO: check this is right
    print("t-test:  \t\t{:.3}".format(stats.ttest_rel(a_high, b_high).statistic))
    print("p-value: \t\t{:.3}".format(stats.ttest_rel(a_high, b_high).pvalue))

    header("illegal", 35)
    # TODO: This reduplication is terrible
    # Illegal attachment: mean(A), mean(B), p(A), p(B), p(A vs B)
    a_ill = [(P.answer_counts[A][ILLEGAL] + P.answer_counts[A][NONE])/6 for P in people]
    b_ill = [(P.answer_counts[B][ILLEGAL] + P.answer_counts[B][NONE])/6 for P in people]
    a_ill_t, a_ill_p = stats.ttest_1samp(a_ill, expected_illegal)
    b_ill_t, b_ill_p = stats.ttest_1samp(b_ill, expected_illegal)

    # Is the illegal% significantly higher than chance (ie, than 1/2)?
    print("mean:    \t{:<8.3}\t{:.3}".format(stats.tmean(a_ill), stats.tmean(b_ill)))
    print("t-test:  \t{:<8.3}\t{:.3}".format(a_ill_t, b_ill_t))
    print("p-value: \t{:<8.3}\t{:.3}".format(a_ill_p, b_ill_p))

    # Are the high% significantly different from each other?
    # Harrison used ttest_rel, TODO: check this is right
    print("t-test:  \t\t{:.3}".format(stats.ttest_rel(a_ill, b_ill).statistic))
    print("p-value: \t\t{:.3}".format(stats.ttest_rel(a_ill, b_ill).pvalue))

    header("time", 35)
    # Time: mean and stdev
    a_times = [P.average_time_a for P in people]
    b_times = [P.average_time_b for P in people]
    print("mean:    \t{:<8.3}\t{:.3}".format(stats.tmean(a_times), stats.tmean(b_times)))
    print("stdev:   \t{:<8.3}\t{:.3}".format(stats.tstd(a_times), stats.tstd(b_times)))
    # Are the high% significantly different from each other?
    # Harrison used ttest_rel, TODO: check this is right
    print("t-test:  \t\t{:.3}".format(stats.ttest_rel(a_times, b_times).statistic))
    print("p-value: \t\t{:.3}".format(stats.ttest_rel(a_times, b_times).pvalue))


def analyze_file(experiment_number, file_name):
    # and the expected percent of high/low/illegal attachment
    if experiment_number == 1:
        expected_high, expected_low, expected_illegal = .225, .225, .55
    else:
        expected_high, expected_low, expected_illegal = .2, .2, .6

    # read list of people
    people = read_people(file_name, experiment_number)

    # Calculate mean and stdev of average time
    # (Values are: average time of every included participant)
    times = [P.average_time for P in people if P.include]
    time_mean = stats.tmean(times) # "Trimmed" (with no trimming) mean
    time_stdev = stats.tstd(times) # "Trimmed" (with no trimming) sample stdev
    # report time stuff
    #report_time(time_mean, time_stdev)

    # set cutoff for timing (possibly based on time mean and stdev)
    time_cutoff = 3.5
    #time_cutoff = time_mean - 2*time_stdev

    # inform all people of the cutoff
    print("time cutoff: {}".format(time_cutoff))
    for p in people:
        p.set_time_cutoff(time_cutoff)
    #exclusion_report(people)

    for p in people:
        print(p)


    #for p in people:
    #    if p.include:
    #        if p.answer_counts[A][NONE] + p.answer_counts[B][NONE]:
    #            print(p)

    #print()
    #header("TQ complete, DQ complete", 80)
    #analyze_sample([p for p in people if p.TQ_complete and p.DQ_complete])

    print()
    header("TQ complete, DQ complete, DQ correct, time < {:.3} seconds".format(time_cutoff), 80)
    analyze_sample([p for p in people if p.include], expected_high, expected_low, expected_illegal)


if __name__ == "__main__":
    # example:
    # python3 exclude.py 2 ambi-data

    try:
        experiment_number = int(sys.argv[1])
        file_name = sys.argv[2]
    except:
        usage_exit()
    if len(sys.argv) > 3:
        usage_exit()

    analyze_file(experiment_number, file_name)
