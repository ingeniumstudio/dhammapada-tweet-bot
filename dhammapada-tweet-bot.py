#!/usr/bin/env python

import os
import json
import random
import re

import tweepy

import secrets_xapi as creds

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

DEBUG = True if os.environ.get('DEBUG') else False

# This file contains The Dhamapada in JSON format
DHAMMAPADA_JSON_FILEPATH = f"{SCRIPT_PATH}/dhammapada.json"

# This file will hold the ids of the currently posted tweet(s), the which
# will be deleted in the next time the script is executed
PREVIOUS_IDS_FILEPATH = \
        os.path.expanduser("~/.dhammapada-tweet-bot.previous_ids")

# This file contains the currently (last) posted verse
LAST_VERSE_FILEPATH = os.path.expanduser("~/.dhammapada-tweet-bot.txt")


def chunk_string_by_words(text, max_chars):
    """ Chunk the text in words, so we can divide it into more tweets if it
            doesn't fit into just one, because of X limitations.
    """

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
    """ Gets ids of the previously posted tweets that are recorded in
            file in `PREVIOUS_IDS_FILEPATH` for deletion.
    """

    if not os.path.isfile(previous_ids_filepath):
        return list()  # empty list if file still doesn't exist

    with open(previous_ids_filepath, "r") as previous_ids_file:
        previous_ids = [item.strip() for item in previous_ids_file.readlines()]

    return previous_ids


def set_previous_id(id_list, previous_ids_filepath=PREVIOUS_IDS_FILEPATH):
    """ Locally writes the ids of the tweet(s) currently being posted to
            file in `PREVIOUS_IDS_FILEPATH` for late deletion.
    """

    # this line 1. converts a list[int] to a list[char] and 2. str.joins()
    # that list of chars in a string, separated by a newline
    ids = str("\n").join([str(numeric) for numeric in id_list])

    with open(previous_ids_filepath, "w") as previous_ids_file:
        previous_ids_file.write(ids)

    return ids


def write_last_verse(verse, last_verse_file=LAST_VERSE_FILEPATH):
    """ Writes de current verse being posted to the file in
            `LAST_VERSE_FILEPATH`
    """

    with open(last_verse_file, "w") as fd:
        fd.write(verse)


def get_verse():
    """ Gets a random verse from The Dhammapada, from the file in
            `DHAMMAPADA_JSON_FILEPATH`.
    """

    with open(DHAMMAPADA_JSON_FILEPATH, "r") as dhammapada_json_file:
        dhammapada_json = json.load(dhammapada_json_file)

    keys = dhammapada_json.keys()
    random_choice = random.choice(list(keys))

    return dhammapada_json[random_choice]


def text_width(text):
    """ Iterates over all the lines of the verse and return the number
            of characters from the lenghtiest line; used for formatting.
    """

    lines = text.split('\n')
    lenghtiest_line = max(map(len, lines))

    return lenghtiest_line


verse_numbers, verse = get_verse()
verses = str(", ").join([str(verse_number for verse_number in verse_numbers)])
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

for index, chunk in enumerate(chunks):
    if index == 0:
        response = client.create_tweet(text=chunk)
        id_list.append(response.data['id'])  # pyright: ignore
    else:
        response = client.create_tweet(text=chunk,
                                       in_reply_to_tweet_id=id_list[-1])
        id_list.append(response.data['id'])  # pyright: ignore

# id(s) of the last tweet(s), to be deleted
previous_ids = get_previous_ids(previous_ids_filepath=PREVIOUS_IDS_FILEPATH)

# delete each of the past tweets
for item in previous_ids:  # if empty it will just do nothing
    delete_response = client.delete_tweet(id=item)

# write the id(s) of our new tweet(s) for late deletion
set_previous_id(id_list, previous_ids_filepath=PREVIOUS_IDS_FILEPATH)
