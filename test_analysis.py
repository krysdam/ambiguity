# Tests for analysis.py
# TODO: bring up-to-date with various changes in analysis.py

class test_util_functions(unittest.TestCase):
    """
    Test utility functions
    """
    def test_filter_count(self):
        empty = []
        ls12345 = [1, 2, 3, 4, 5]
        ls123foo5 = [1, 2, 3, "foo", 5]
        everyone = (lambda x: True)
        odd      = (lambda x: x%2 == 1)
        is_int   = (lambda x: type(x) == int)
        # Empty list
        self.assertEqual(filter_count(everyone, empty), 0)
        self.assertEqual(filter_count(odd,      empty), 0)
        self.assertEqual(filter_count(is_int,   empty), 0)
        # [1, 2, 3, 4, 5]
        self.assertEqual(filter_count(everyone, ls12345), 5)
        self.assertEqual(filter_count(odd,      ls12345), 3)
        self.assertEqual(filter_count(is_int,   ls12345), 5)
        # [1, 2, 3, "foo", 5]
        self.assertEqual(filter_count(everyone, ls123foo5), 5)
        self.assertEqual(filter_count(is_int,   ls123foo5), 4)

class test_constants(unittest.TestCase):
    """
    Test global constant enums.
    (Possibly redundant, but I'll likely change some of these numbers,
    so I'd like to catch this kind of problem early.)
    """
    def test_constant_conditions(self):
        # A vs B vs MISS
        self.assertEqual(len(set([A, B, MISS])), 3)

    def test_constant_attachments(self):
        # HIGH vs LOW vs ILLEGAL vs NONE
        self.assertEqual(len(set([HIGH, LOW, ILLEGAL, NONE])), 4)

class test_TQuestion(unittest.TestCase):
    def test_2_conjunct_simple(self):
        # Tests for 2-conjunct question
        TQ = TQuestion("conj1", "conj2")
        # conj1 and conj2 = HIGH
        self.assertEqual(TQ.attachment("conj1 and conj2"), HIGH)
        self.assertEqual(TQ.attachment("Conj1 and Conj2"), HIGH)
        self.assertEqual(TQ.attachment("The conj1 and the conj2"), HIGH)
        # conj2 = LOW
        self.assertEqual(TQ.attachment("conj2"), LOW)
        self.assertEqual(TQ.attachment("Conj2"), LOW)
        self.assertEqual(TQ.attachment("The conj2"), LOW)
        # conj1 = ILLEGAL
        self.assertEqual(TQ.attachment("conj1"), ILLEGAL)
        self.assertEqual(TQ.attachment("Conj1"), ILLEGAL)
        self.assertEqual(TQ.attachment("The conj1"), ILLEGAL)
        # None of the above = NONE
        self.assertEqual(TQ.attachment("None of the above"), NONE)

    def test_2_conjunct_exception(self):
        # Tests for 2-conjunct question whose atb answer is exceptional
        TQ = TQuestion("conj1", "conj2", atb="pineapple")
        # exceptional atb = HIGH
        self.assertEqual(TQ.attachment("pineapple"), HIGH)
        self.assertEqual(TQ.attachment("Pineapple"), HIGH)
        self.assertEqual(TQ.attachment("The pineapple"), HIGH)
        # Technically should check others too, but it's clear that they are fine

    def test_3_conjunct_simple(self):
        # Tests for 3-conjunct question
        TQ = TQuestion("conj1", "conj2", "conj3")
        # conj1 conj2 and conj3 = HIGH
        self.assertEqual(TQ.attachment("conj1 conj2 and conj3"), HIGH)
        self.assertEqual(TQ.attachment("Conj1, Conj2, and Conj3"), HIGH)
        self.assertEqual(TQ.attachment("The conj1, the conj2, and the conj3"), HIGH)
        # conj3 = LOW
        self.assertEqual(TQ.attachment("conj3"), LOW)
        self.assertEqual(TQ.attachment("Conj3"), LOW)
        self.assertEqual(TQ.attachment("The conj3"), LOW)
        # conj1 = ILLEGAL
        self.assertEqual(TQ.attachment("conj1"), ILLEGAL)
        self.assertEqual(TQ.attachment("Conj1"), ILLEGAL)
        self.assertEqual(TQ.attachment("The conj1"), ILLEGAL)
        # conj2 = ILLEGAL
        self.assertEqual(TQ.attachment("conj2"), ILLEGAL)
        self.assertEqual(TQ.attachment("Conj2"), ILLEGAL)
        self.assertEqual(TQ.attachment("The conj2"), ILLEGAL)
        # None of the above = NONE
        self.assertEqual(TQ.attachment("None of the above"), NONE)

    def test_3_conjunct_exception(self):
        # Tests for 3-conjunct question whose atb answer is exceptional
        TQ = TQuestion("conj1", "conj2", "conj3", atb="pineapple")
        # exceptional atb = HIGH
        self.assertEqual(TQ.attachment("pineapple"), HIGH)
        self.assertEqual(TQ.attachment("Pineapple"), HIGH)
        self.assertEqual(TQ.attachment("The pineapple"), HIGH)
        # Technically should check others too, but it's clear that they are fine

class test_ab_pattern(unittest.TestCase):
    """
    Test abababababab pattern stuff.
    """
    def test_6_and_6(self):
        # All patterns contain 6 A's and 6 B's
        for exp in range(1, 3+1):
            for pattern_number in range(1, 5+1):
                pattern = patternses[exp][pattern_number]
                countA = len([cond for cond in pattern if cond == A])
                countB = len([cond for cond in pattern if cond == B])
                self.assertEqual(countA, 6)
                self.assertEqual(countB, 6)

    def test_specific_patterns(self):
        # Assume experiment 1
        # Just a spot check
        global patterns
        patterns = patternses[1]
        self.assertEqual(which_pattern([B,A,B, A,A,A, B,B,A, A,B,B]), "1")
        self.assertEqual(which_pattern([A,B,A, B,B,B, A,A,B, B,A,A]), "1~")
        self.assertEqual(which_pattern([A,A,B, B,B,A, A,B,B, A,B,A]), "4")
        self.assertEqual(which_pattern([B,B,A, A,A,B, B,A,A, B,A,B]), "4~")
