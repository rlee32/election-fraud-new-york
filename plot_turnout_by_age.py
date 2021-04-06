#!/usr/bin/env python3

import csv
from typing import Dict
from matplotlib import pyplot as plt

DATA_FILE = './data/voters.txt'

DOB_INDEX = 17 # dob, YYYYMMDD
COUNTY_INDEX = 21
REGDATE_INDEX = 35 # registration date, YYYYMMDD
VOTER_ID_INDEX = 43
VOTE_HISTORY_INDEX = 44

ELECTION_YEAR = 2020 # choose presidential election years from 2000 - 2020
ELECTION_DAY = {
    2020: '03',
    2016: '08',
    2012: '06',
    2008: '04',
    2004: '02',
    2000: '07'
}
ELECTION_DATE = int(f'{ELECTION_YEAR}11{ELECTION_DAY[ELECTION_YEAR]}')
ELECTION_TAG = f'{ELECTION_YEAR} General Election' # if this is in vote history, then person voted.

MINIMUM_VOTERS = 50 # filter for plotting.

def get_age(start: int, end: int):
    """Returns integer age given dates in form YYYYMMDD. """
    diff = end - start
    if diff < 0:
        return diff / 10000.0
    else:
        return int(diff / 10000)

def get_voters():
    """Returns lists of voters mapped by county. """
    voters = {}
    age_skipped = 0
    with open(DATA_FILE, 'r', encoding='ISO-8859-1') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            age = get_age(int(row[DOB_INDEX]), ELECTION_DATE)
            if age < 18:
                continue
            if age > 150:
                age_skipped += 1
                continue
            county = row[COUNTY_INDEX]
            if county not in voters:
                voters[county] = []
            voters[county].append({
                'id': row[VOTER_ID_INDEX],
                'age': age,
                'voted': ELECTION_TAG in row[VOTE_HISTORY_INDEX],
            })
    total = sum([len(voters[x]) for x in voters])
    print(f'got {total} voters.')
    print(f'got {count_votes(voters)} total votes.')
    print(f'skipped {age_skipped} ({age_skipped / total * 100} % of total) voters due to unreasonable age.')
    return voters

def count_votes(voters):
    total_votes = 0
    for county in voters:
        for v in voters[county]:
            if v['voted']:
                total_votes += 1
    return total_votes

def plot_turnout(turnout: Dict[int, int]):
    tt = list(turnout.items())
    tt.sort()
    plt.plot([x[0] for x in tt], [x[1] for x in tt])

def plot_county(voters):
    ages = {}
    total_votes = 0
    total_voters = 0
    for v in voters:
        a = v['age']
        if a not in ages:
            ages[a] = []
        ages[a].append(v)
        if v['voted']:
            total_votes += 1
        total_voters += 1
    overall_turnout = total_votes / total_voters

    if overall_turnout == 0:
        print('\tzero turnout county...')
        return

    key = {}
    plot_key = {}
    for a in ages:
        vv = ages[a]
        assert(len(vv) != 0)
        key[a] = sum([1 for x in vv if x['voted']]) / len(vv) / overall_turnout
        if len(vv) < MINIMUM_VOTERS:
            continue
        plot_key[a] = sum([1 for x in vv if x['voted']]) / len(vv) / overall_turnout
    plot_turnout(plot_key)

    return key

if __name__ == '__main__':
    voters = get_voters()
    for county in voters:
        print(f'plotting {county}')
        key = plot_county(voters[county])
    plt.show()
