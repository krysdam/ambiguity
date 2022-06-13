# Created by Harrison Naftelberg in Spring 2022
# Given to Kyle Rysdam on April 18, 2022
# Adapted slightly by Kyle Rysdam

from time import time
import pandas
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter

ambiguity_1_answer_map = {'TQ1a':{'Cars': 'I', 'Mopeds':'I', 'Trucks':'L', 'Cars, mopeds, and trucks':'H'},
'TQ1b': {'Cars': 'I', 'Mopeds':'I', 'Trucks':'L', 'Cars, mopeds, and trucks':'H'},
'TQ2a': {'Books': 'I', 'Pamphlets':'I', 'Maps':'L', 'Books, pamphlets, and maps':'H'},
'TQ2b': {'The books': 'I', 'The pamphlets':'I', 'The maps':'L', 'The books, the pamphlets, and the maps':'H'},
'TQ3a': {'Sandwiches': 'I', 'Soups':'I', 'Salads':'L', 'Sandwiches, soups, and salads':'H'},
'TQ3b': {'The sandwiches': 'I', 'The soups':'I', 'The salads':'L', 'The sandwiches, the soups, and the salads':'H'},
'TQ4a': {'Laptops': 'I', 'Tablets':'I', 'Phones':'L', 'Laptops, tablets, and phones':'H'},
'TQ4b': {'Laptops': 'I', 'Tablets':'I', 'Phones':'L', 'Laptops, tablets, and phones':'H'},
'TQ5a': {'Chopsticks': 'I', 'Fortune cookies':'L', 'Chopsticks and fortune cookies':'H'},
'TQ5b': {'The chopsticks': 'I', 'The fortune cookies':'L', 'The chopsticks and the fortune cookies':'H'},
'TQ6a': {'Singers': 'I', 'Dancers':'L', 'Singers and dancers':'H'},
'TQ6b': {'The singers': 'I', 'The dancers':'L', 'The singers and the dancers':'H'},
'TQ7a': {'Chairs': 'I', 'Couches':'L', 'Chairs and couches':'H'},
'TQ7b': {'The chairs': 'I', 'The couches':'L', 'The chairs and the couches':'H'},
'TQ8a': {'Sitcoms': 'I', 'Comedy movies':'L', 'Sitcoms and comedy movies':'H'},
'TQ8b': {'The sitcoms': 'I', 'The comedy movies':'L', 'The sitcoms and the comedy movies':'H'},
'TQ9a': {'Interviews': 'I', 'News':'L', 'News and interviews':'H'},
'TQ9b': {'The interviews': 'I', 'The news':'L', 'The news and the interviews':'H'},
'TQ10a': {'Monkeys': 'I', 'Mice':'L', 'Monkeys and mice':'H'},
'TQ10b': {'The monkeys': 'I', 'The mice':'L', 'The monkeys and the mice':'H'},
'TQ11a': {'Ceramics': 'I', 'Sculptures':'I', 'Collages':'L', 'Ceramics, sculptures, and collages':'H'},
'TQ11b': {'The ceramics': 'I', 'The sculptures':'I', 'The collages': 'L', 'The ceramics, the sculptures, and the collages':'H'},
'TQ12a': {'Skateboards': 'I', 'Scooters':'I', 'Bikes':'L', 'Skateboards, scooters, and bikes':'H'},
'TQ12b': {'Skateboards': 'I', 'Scooters':'I', 'Bikes':'L', 'Skateboards, scooters, and bikes':'H'}}

ambiguity_2_answer_map = {'TQ1a':{'The athletes': 'I', 'The photographers':'L', 'The athletes and the photographers':'H'},
'TQ1b': {'The athletes': 'I', 'The photographers':'L', 'The athletes and the photographers':'H'},
'TQ2a': {'The dancers': 'I', 'The musicians':'L', 'The dancers and the musicians':'H'},
'TQ2b':{'The dancers': 'I', 'The musicians':'L', 'The dancers and the musicians':'H'},
'TQ3a': {'The books': 'I', 'The magazines':'L', 'The books and the magazines':'H'},
'TQ3b': {'The books': 'I', 'The magazines':'L', 'The books and the magazines':'H'},
'TQ4a': {'The pies': 'I', 'The cakes':'L', 'The pies and the cakes':'H'},
'TQ4b': {'The pies': 'I', 'The cakes':'L', 'The pies and the cakes':'H'},
'TQ5a': {'The horror movies': 'I', 'The comedies':'L', 'The horror movies and the comedies':'H'},
'TQ5b': {'The horror movies': 'I', 'The comedies':'L', 'The horror movies and the comedies':'H'},
'TQ6a': {'The plates': 'I', 'The cups':'L', 'The plates and the cups':'H'},
'TQ6b': {'The plates': 'I', 'The cups':'L', 'The plates and the cups':'H'},
'TQ7a': {'The deserts': 'I', 'The forests':'L', 'The deserts and the forests':'H'},
'TQ7b': {'The deserts': 'I', 'The forests':'L', 'The deserts and the forests':'H'},
'TQ8a': {'Coffee': 'I', 'Tea':'L', 'Coffee and tea':'H'},
'TQ8b': {'Coffee': 'I', 'Tea':'L', 'Coffee and tea':'H'},
'TQ9a': {'Tee-shirts': 'I', 'Sweatshirts':'L', 'Tee-shirts and sweatshirts':'H'},
'TQ9b': {'Tee-shirts': 'I', 'Sweatshirts':'L', 'Tee-shirts and sweatshirts':'H'},
'TQ10a': {'The cats': 'I', 'The dogs':'L', 'The cats and the dogs':'H'},
'TQ10b': {'The cats': 'I', 'The dogs':'L', 'The cats and the dogs':'H'},
'TQ11a': {'The customers': 'I', 'The waiters':'L', 'The customers and the waiters':'H'},
'TQ11b': {'The customers': 'I', 'The waiters':'L', 'The customers and the waiters':'H'},
'TQ12a': {'The schools': 'I', 'The apartments':'L', 'The schools and the apartments':'H'},
'TQ12b': {'The schools': 'I', 'The apartments':'L', 'The schools and the apartments':'H'}}

ambiguity_3_answer_map = {'TQ1a':{'The athletes': 'I', 'The photographers':'L', 'The photographers and the athletes':'H'},
'TQ1b': {'The athletes': 'I', 'The photographers':'L', 'The photographers and the athletes':'H'},
'TQ2a': {'The dancers': 'I', 'The musicians':'L', 'The musicians and the dancers':'H'},
'TQ2b':{'The dancers': 'I', 'The musicians':'L', 'The musicians and the dancers':'H'},
'TQ3a': {'The books': 'I', 'The magazines':'L', 'The magazines and the books':'H'},
'TQ3b': {'The books': 'I', 'The magazines':'L', 'The magazines and the books':'H'},
'TQ4a': {'The pies': 'I', 'The cakes':'L', 'The cakes and the pies':'H'},
'TQ4b': {'The pies': 'I', 'The cakes':'L', 'The cakes and the pies':'H'},
'TQ5a': {'The horror movies': 'I', 'The comedies':'L', 'The comedies and the horror movies':'H'},
'TQ5b': {'The horror movies': 'I', 'The comedies':'L', 'The comedies and the horror movies':'H'},
'TQ6a': {'The plates': 'I', 'The cups':'L', 'The cups and the plates':'H'},
'TQ6b': {'The plates': 'I', 'The cups':'L', 'The cups and the plates':'H'},
'TQ7a': {'Deserts': 'I', 'Forests':'L', 'Forests and deserts':'H'},
'TQ7b': {'The deserts': 'I', 'The forests':'L', 'The forests and the deserts':'H'},
'TQ8a': {'Coffee': 'I', 'Tea':'L', 'Tea and coffee':'H'},
'TQ8b': {'Coffee': 'I', 'Tea':'L', 'Tea and coffee':'H'},
'TQ9a': {'Tee-shirts': 'I', 'Sweatshirts':'L', 'Sweatshirts and tee-shirts':'H'},
'TQ9b': {'Tee-shirts': 'I', 'Sweatshirts':'L', 'Sweatshirts and tee-shirts':'H'},
'TQ10a': {'The cats': 'I', 'The dogs':'L', 'The dogs and the cats':'H'},
'TQ10b': {'The cats': 'I', 'The dogs':'L', 'The dogs and the cats':'H'},
'TQ11a': {'The customers': 'I', 'The waiters':'L', 'The waiters and the customers':'H'},
'TQ11b': {'The customers': 'I', 'The waiters':'L', 'The waiters and the customers':'H'},
'TQ12a': {'The schools': 'I', 'The apartments':'L', 'The apartments and the schools':'H'},
'TQ12b': {'The schools': 'I', 'The apartments':'L', 'The apartments and the schools':'H'}}

title_dict = {'Experiment 1':{'A':'Verb Phrase', 'B':'Noun Phrase'},
                'Experiment 2':{'A':'No Bias', 'B':'Low Bias'},
                'Experiment 3':{'A':'No Bias', 'B':'High Bias'}}

var_dict = {1:'High Attachment', 2:'Low Attachment', 3:'Illegal Attachment'}

def ambiguity(source, dict, title, workbook):
    # Read csv as a DataFrame
    df = pandas.read_csv(source)
    # Drop ROW (axis 1) number ZERO (number 0)
    df = df.drop([0,1])

    # Dict from each participant's ID to a dict:
    # {'A': float high-attachment percent in A questions,
    #  'B': float high-attachment percent in B questions}
    participants = {}

    # Dict from each participant's ID to a dict:
    # {'A': float illegal-attachment percent in A questions,
    #  'B': float illegal-attachment percent in B questions}
    illegal_counts = {}

    # List of average times for each participant
    avg_times = []

    for index, row in df.iterrows():
        toss = False
        b_high_total = 0
        a_high_total = 0
        a_illegal_total = 0
        b_illegal_total = 0
        times = []

        # From #1 to #12
        for n in range(1, 13):
            question = 'TQ' + str(n)
            type = None

            # If there's an answer for TQ1a, type is a, and so on for TQ2a...
            if not pandas.isna(row[question + 'a']) and pandas.isna(row[question + 'b']):
                question += 'a'
                type = 'a'
            # If there's an answer for TQ1b, type is b, and so on for TQ2b...
            elif pandas.isna(row[question + 'a']) and not pandas.isna(row[question + 'b']):
                question += 'b'
                type = 'b'
            # If there's no answer for either, toss (incomplete test questions)
            else:
                toss = True
                continue

            # Find their answer
            answer = row[question]

            # Record their time
            times.append(float(row[question + " TIME_Page Submit"]))

            # If their answer is high (see dict above), record as high
            if dict[question][answer] == 'H':
                if type == 'a':
                    a_high_total += 1
                elif type == 'b':
                    b_high_total += 1
            # if illegal, record as illegal
            elif dict[question][answer] == 'I':
                if type =='a':
                    a_illegal_total += 1
                elif type == 'b':
                    b_illegal_total += 1

        # Record avg_time (skip if div by zero)
        if len(times) != 0:
            avg_times.append(avg(times))

        # Calculate high_percent and illegal_percent (out of the 6 a and 6 b questions)
        b_high_percent = (b_high_total / 6) * 100
        a_high_percent = (a_high_total / 6) * 100
        b_illegal_percent = (b_illegal_total / 6) * 100
        a_illegal_percent = (a_illegal_total / 6) * 100

        # Record the participant's percents in participants (high percent) and illegal_counts (illegal percent)
        if not toss:
            participants[row['ResponseId']] = {}
            participants[row['ResponseId']]['B'] = b_high_percent
            participants[row['ResponseId']]['A'] = a_high_percent
            illegal_counts[row['ResponseId']] = {}
            illegal_counts[row['ResponseId']]['B'] = b_illegal_percent
            illegal_counts[row['ResponseId']]['A'] = a_illegal_percent

    # Mean and stdev of participant-average times
    print("average time: " + str(avg(avg_times)))
    print(stats.tstd(avg_times))

    # Make a spreadsheet page for high attachment and a page for illegal attachment
    first_analysis = analyze(participants, dict, title, 1, workbook)
    illegal_analysis = analyze(illegal_counts, dict, title, 3, workbook)

def avg(l):
    # Helper: average of a list
    return sum(l)/len(l)

def analyze(data, dict, title, var, workbook):
    # The sheet's name, eg "Experiment 1 High Attachment"
    full_title = title + " " + var_dict[var]
    # Add the sheet to the "workbook" (who knows)
    worksheet = workbook.add_worksheet(full_title)

    A = []
    B = []
    for p in data.keys():
        A.append(data[p]['A'])
        B.append(data[p]['B'])

    paired_results = stats.ttest_rel(A, B)
    oneway_result_A = stats.ttest_1samp(A, 50)
    oneway_result_B = stats.ttest_1samp(B, 50)

    # Title - col 0
    # Nothing first row
    worksheet.write(1, 0, 'n')
    worksheet.write(2, 0, 'Average ' + var_dict[var] + " Percentage")
    worksheet.write(3, 0, 'One way t-test (is this condition significantly different from random?)')
    worksheet.write(4, 0, 'One way t-test Test Statistic')
    worksheet.write(5, 0, 'One way t-test p-value (less than 0.05 is significant)')
    worksheet.write(7, 0, 'Paired t-test (Is there a siginicant difference between conditions?)')
    worksheet.write(8, 0, 'Paired t-test test statistic')
    worksheet.write(8, 1, paired_results[0])
    worksheet.write(9, 0, 'Paired t-test p-value')
    worksheet.write(9, 1, paired_results[1])

    # Condition A - col 1
    worksheet.write(0, 1, title_dict[title]['A'])
    worksheet.write(1, 1, len(A))
    worksheet.write(2, 1, avg(A))
    worksheet.write(4, 1, oneway_result_A[0])
    worksheet.write(5, 1, oneway_result_A[1])

    # Condition B - col 2
    worksheet.write(0, 2, title_dict[title]['B'])
    worksheet.write(1, 2, len(B))
    worksheet.write(2, 2, avg(B))
    worksheet.write(4, 2, oneway_result_B[0])
    worksheet.write(5, 2, oneway_result_B[1])

    

    print(title)
    print("Average High Attachment in A condition: " + str(avg(A)))
    print("Average High Attachment in B condition: " + str(avg(B)))
    print("n = " + str(len(A)))
    print("One Way t-test Condition A: Test Statistic: " + str(oneway_result_A[0]) + ", P-value: " + str(oneway_result_A[1]))
    print("One Way t-test Condition B: Test Statistic: " + str(oneway_result_B[0]) + ", P-value: " + str(oneway_result_B[1]))
    print("Paired T-Test condition A vs condition B")
    print("Test Statistic: " + str(paired_results[0]))
    print("P-value: " + str(paired_results[1]))
    print("\n")

    return (avg(A), avg(B))

workbook = xlsxwriter.Workbook('Ambiguity Analysis.xlsx')
#ambiguity('pilot-1-exclude-t35.csv', ambiguity_1_answer_map, "Experiment 1", workbook)
#ambiguity('pilot-2-exclude-t35.csv', ambiguity_2_answer_map, "Experiment 2", workbook)
#ambiguity('pilot-3-exclude-t35.csv', ambiguity_3_answer_map, "Experiment 3", workbook)
ambiguity('Ambiguity Experiment 1_May 19, 2022_17.42.csv', ambiguity_1_answer_map, "Experiment 1", workbook)
ambiguity('Ambiguity Experiment 2_May 19, 2022_17.42.csv', ambiguity_2_answer_map, "Experiment 2", workbook)
ambiguity('Ambiguity Experiment 3_May 19, 2022_17.40.csv', ambiguity_3_answer_map, "Experiment 3", workbook)
workbook.close()
