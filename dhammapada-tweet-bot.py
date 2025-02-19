#!/usr/bin/env python

import subprocess
import re
import sys

import tweepy

CONSUMER_KEY = ""
CONSUMER_SECRET = ""

ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""


argc = len(sys.argv)

if argc > 1:
    verse_number = sys.argv[1]
else:
    verse_number = None


def remove_numbers_from_str(string):
    space = ' '
    comma = ','

    new_string = re.sub(r'[0-9]+', '', string)
    new_string = re.sub(r' ,', '', new_string)
    new_string = re.sub(r'\n\W*\n\W*\n', '\n\n', new_string)
    new_string = re.sub(r'\n\W*$', '', new_string)

    return new_string.strip(f'{space}{comma}')


def get_verse(verse_number=None):
    if verse_number:
        command = ['display-dhammapada', verse_number]
    else:
        command = 'display-dhammapada'
    verse = subprocess.run(command, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, text=True).stdout.strip()
    return verse


def get_numbers(string):
    number_list = re.findall(r'\d+', string)
    return number_list


verse = get_verse(verse_number=verse_number)
numbers = get_numbers(verse)
number = "verse" if len(numbers) < 2 else "verses"
verse_without_numbers = remove_numbers_from_str(verse)
signature = f"— Dhammapada, {number} {', '.join(numbers)}"

message = f"""\
{verse_without_numbers}

{signature} \
"""

print(message)

client = tweepy.Client(consumer_key=CONSUMER_KEY,
                       consumer_secret=CONSUMER_SECRET,
                       access_token=ACCESS_TOKEN,
                       access_token_secret=ACCESS_TOKEN_SECRET)

response = client.create_tweet(text=message)

print(response.data)
