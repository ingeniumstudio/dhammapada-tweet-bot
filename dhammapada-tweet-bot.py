#!/usr/bin/env python

import os
import subprocess
import re

import tweepy

import dhammapada_tweet_bot_credentials as creds

LAST_ID_FILEPATH = os.path.expanduser("~/.dhammapada-tweet-bot.lastid")


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


def remove_numbers_from_str(string):
    space = ' '
    comma = ','

    new_string = re.sub(r'[0-9]+', '', string)
    new_string = re.sub(r' ,', '', new_string)
    new_string = re.sub(r'\n\W*\n\W*\n', '\n\n', new_string)
    new_string = re.sub(r'\n\W*$', '', new_string)

    return new_string.strip(f'{space}{comma}')


def get_verse():
    command = 'display-dhammapada'
    verse = subprocess.run(command, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, text=True).stdout.strip()
    return verse


def get_numbers(string):
    number_list = re.findall(r'\d+', string)
    return number_list


verse = get_verse()
numbers = get_numbers(verse)
number = "verse" if len(numbers) < 2 else "verses"
verse_without_numbers = remove_numbers_from_str(verse)
signature = f"— Dhammapada, {number} {', '.join(numbers)}"

message = f"""\
{verse_without_numbers}

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
