#!/usr/bin/env python

#!/home/u07/.venv/bin/python

import os
import json
import random
import re

import tweepy

import dhammapada_tweet_bot_credentials as creds

PREVIOUS_IDS_FILEPATH = os.path.expanduser("~/.dhammapada-tweet-bot.previous_ids")
DEBUG_FILEPATH = os.path.expanduser("~/.dhammapada-tweet-bot.debug")
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
    ids = "\n".join([str(item) for item in id_list])

    with open(previous_ids_filepath, "w") as lidfp:
        lidfp.write(ids)
    with open(previous_ids_filepath, "r") as lidfp:
        previous_ids = lidfp.read()
    return previous_ids


def write_last_verse(verse, debug_file=DEBUG_FILEPATH):
    with open(debug_file, "w") as debugfd:
        debugfd.write(verse)


def get_verse():
    with open(DHAMMAPADA_JSON_FILEPATH, "r") as dhammapada_json_file:
        dhammapada_json = json.load(dhammapada_json_file)

    keys = dhammapada_json.keys()
    random_choice = random.choice(list(keys))

    return dhammapada_json[random_choice]


verse_numbers, verse = get_verse()
verses = ", ".join([str(verse_number) for verse_number in verse_numbers])
signature = f"— Dhammapada {verses}"

message = f"""\
{verse}

{signature} \
"""

# https://stackoverflow.com/questions/73537087/regex-to-capture-a-single-new-line-instance-but-not-2
message_no_breaks = re.sub('(.)\n(?!\n)', r'\1 ', message)

chunks = chunk_string_by_words(text=message_no_breaks, max_chars=278)

#  print(message)
write_last_verse(verse=message, debug_file=DEBUG_FILEPATH)

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

# id of the last tweet, to be deleted
previous_ids = get_previous_ids(previous_ids_filepath=PREVIOUS_IDS_FILEPATH)
if previous_ids:
    for item in previous_ids:
        delete_response = client.delete_tweet(id=item)
        #  print(delete_response.data)  # pyright: ignore

#  new_post_id = response.data['id']  # pyright: ignore
set_previous_id(id_list, previous_ids_filepath=PREVIOUS_IDS_FILEPATH)

#  print(response.data)  # pyright: ignore
