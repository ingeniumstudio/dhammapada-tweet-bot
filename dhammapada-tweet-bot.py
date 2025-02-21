#!/usr/bin/env python

import os
import json
import random

import tweepy

import dhammapada_tweet_bot_credentials as creds

LAST_ID_FILEPATH = os.path.expanduser("~/.dhammapada-tweet-bot.lastid")
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DHAMMAPADA_JSON_FILEPATH = f"{SCRIPT_PATH}/dhammapada.json"


def get_last_id(last_id_filepath=LAST_ID_FILEPATH):
    if not os.path.isfile(last_id_filepath):
        return None
    with open(last_id_filepath, "r") as lidfp:
        last_id = lidfp.read()
    return last_id


def set_last_id(id, last_id_filepath=LAST_ID_FILEPATH):
    with open(last_id_filepath, "w") as lidfp:
        lidfp.write(id)
    with open(last_id_filepath, "r") as lidfp:
        last_id = lidfp.read()
    return last_id


def get_verse():
    with open(DHAMMAPADA_JSON_FILEPATH, "r") as dhammapada_json_file:
        dhammapada_json = json.load(dhammapada_json_file)

    keys = dhammapada_json.keys()
    random_choice = random.choice(list(keys))

    return dhammapada_json[random_choice]


verse_numbers, verse = get_verse()
verses = ", ".join([str(verse_number) for verse_number in verse_numbers])
signature = f"— Dhammapada, {verses}"

message = f"""\
{verse}

{signature} \
"""

print(message)

client = tweepy.Client(consumer_key=creds.CONSUMER_KEY,
                       consumer_secret=creds.CONSUMER_SECRET,
                       access_token=creds.ACCESS_TOKEN,
                       access_token_secret=creds.ACCESS_TOKEN_SECRET)

response = client.create_tweet(text=message)

# id of the last tweet, to be deleted
last_id = get_last_id(last_id_filepath=LAST_ID_FILEPATH)
if last_id:
    delete_response = client.delete_tweet(id=last_id)
    print(delete_response.data)  # pyright: ignore

new_post_id = response.data['id']  # pyright: ignore
set_last_id(new_post_id, last_id_filepath=LAST_ID_FILEPATH)

print(response.data)  # pyright: ignore
