#!/usr/bin/env python

import os
import json
import random
import re

import tweepy

import secrets_xapi as creds

DEBUG = True if os.environ.get('DEBUG') else False

PREVIOUS_IDS_FILEPATH = os.path.expanduser("~/.dhammapada-tweet-bot.previous_ids")
LAST_VERSE_FILEPATH = os.path.expanduser("~/.dhammapada-tweet-bot.txt")
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DHAMMAPADA_JSON_FILEPATH = f"{SCRIPT_PATH}/dhammapada.json"

def chunk_string_by_words(text, max_chars):
    words = text.split(' ')
    chunks = []
    current_chunk = ""
    for word in words:
        if not current_chunk:
            current_chunk = word
        elif len(current_chunk) + len(word) + 1 <= max_chars:
            current_chunk += " " + word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def get_previous_ids(previous_ids_filepath=PREVIOUS_IDS_FILEPATH):
    if not os.path.isfile(previous_ids_filepath):
        return None
    with open(previous_ids_filepath, "r") as lidfp:
        previous_ids = [item.strip() for item in lidfp.readlines()]
    return previous_ids


def set_previous_id(id_list, previous_ids_filepath=PREVIOUS_IDS_FILEPATH):
    ids = str("\n").join(list(map(str, id_list)))

    with open(previous_ids_filepath, "w") as lidfp:
        lidfp.write(ids)
    with open(previous_ids_filepath, "r") as lidfp:
        previous_ids = lidfp.read()
    return previous_ids


def write_last_verse(verse, last_verse_file=LAST_VERSE_FILEPATH):
    with open(last_verse_file, "w") as fd:
        fd.write(verse)


def get_verse():
    with open(DHAMMAPADA_JSON_FILEPATH, "r") as dhammapada_json_file:
        dhammapada_json = json.load(dhammapada_json_file)

    keys = dhammapada_json.keys()
    random_choice = random.choice(list(keys))

    return dhammapada_json[random_choice]

def text_width(text):
    lines = text.split('\n')
    biggest_line_lenght = max(map(len, lines))

    return biggest_line_lenght

verse_numbers, verse = get_verse()
verses = str(", ").join(list(map(str, verse_numbers)))
signature = f"— Dhammapada {verses}"

line_size = text_width(text=verse)
signature_lenght = len(signature)

message_twitter = f"""\
{verse}

{signature}\
"""

message_local = f"""\
{verse}

{signature:>{line_size}}\
"""

if DEBUG:
    print("message_twitter", message_twitter, sep="\n\n", end="\n\n")
    print("message_local", message_local, sep="\n\n", end="\n\n")
    exit(0)

# https://stackoverflow.com/questions/73537087/regex-to-capture-a-single-new-line-instance-but-not-2
message_no_breaks = re.sub('(.)\n(?!\n)', r'\1 ', message_twitter)

chunks = chunk_string_by_words(text=message_no_breaks, max_chars=278)

write_last_verse(verse=message_local, last_verse_file=LAST_VERSE_FILEPATH)

client = tweepy.Client(consumer_key=creds.CONSUMER_KEY,
                       consumer_secret=creds.CONSUMER_SECRET,
                       access_token=creds.ACCESS_TOKEN,
                       access_token_secret=creds.ACCESS_TOKEN_SECRET)

id_list = list()

for idx, chunk in enumerate(chunks):
    if idx == 0:
        response = client.create_tweet(text=chunk)
        id_list.append(response.data['id']) # pyright: ignore
    else:
        response = client.create_tweet(text=chunk,
                                       in_reply_to_tweet_id=id_list[-1])
        id_list.append(response.data['id']) # pyright: ignore

# id(s) of the last tweet(s), to be deleted
previous_ids = get_previous_ids(previous_ids_filepath=PREVIOUS_IDS_FILEPATH)
if previous_ids:
    for item in previous_ids:
        delete_response = client.delete_tweet(id=item)

set_previous_id(id_list, previous_ids_filepath=PREVIOUS_IDS_FILEPATH)
