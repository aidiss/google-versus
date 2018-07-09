"""
Thanks to 
https://stackoverflow.com/questions/5102878/google-suggest-api

Recommended connectors: "with", "vs", "without"
"""
import itertools
from time import sleep

import click
import maya
import records
import requests

# suggestqueries_url = 'http://suggestqueries.google.com/complete/search'
suggestqueries_url = 'http://google.com/complete/search'


db = records.Database('sqlite:///data.db')



@click.command()
@click.option('-w', '--word', prompt='word', help='The person to greet.')
@click.option('-c', '--connector', prompt='connector',)
def crawl(word, connector):

    # A list of already crawled words
    crawled = []
    # for future crawl
    schedule = {}
    for i in range(10):
        schedule[i] = []

    schedule[0].append(word)
    main_loop(crawled, schedule, connector)


def main_loop(crawled, schedule, connector):
    while True:
        print('Crawled', crawled)
        print('Schedule', schedule)
        try:
            word = get_next_word(schedule)
            query = create_query(word=word, connector=connector)
            response = get_response(query)
            handle_stuff(word, response, schedule, crawled)
            crawled.append(word)
            sleep(1)
        except KeyboardInterrupt as _:
            break


def handle_stuff(word, response, schedule, crawled):
    for d in handle_response(word=word, response=response):
        suggestion_name = d['suggestion_raw'].replace(
            d['search_query'], '').strip()
        all_scheduled = list(itertools.chain(schedule.items()))
        if (suggestion_name not in crawled) and (suggestion_name not in all_scheduled):
            print('Adding new', suggestion_name)
            schedule[d['rank']].append(suggestion_name)
        dump_results(d)


def get_next_word(schedule):
    for rank in schedule:
        try:
            return schedule[rank].pop()
        except IndexError:
            pass


def create_query(word: str, connector: str):
    return word + ' ' + connector


def get_response(query: str) -> dict:
    payload = dict(q=query, output='firefox', hl='en', gl='lt')
    return requests.get(suggestqueries_url, params=payload)


def handle_response(word, response):
    query, suggestions = response.json()
    for rank, suggestion_raw in enumerate(suggestions):
        d = dict(
            word=word,
            date=maya.now().date,
            search_query=query,
            rank=rank,
            suggestion_raw=suggestion_raw)
        yield d


def dump_results(d):
    d['suggestion'] = d['suggestion_raw'].replace(d['search_query'], '').strip()
    sql_query = '''INSERT INTO suggestions (date, word, query, rank, suggestion_raw, suggestion) VALUES(:date, :word, :search_query, :rank, :suggestion_raw, :suggestion)'''
    db.query(sql_query, **d)
    pass
