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

# This file contains the currently (last) posted verse
VERSE_FILEPATH = os.path.expanduser("~/.dhammapada-tweet-bot.txt")

# This file will hold the ids of the currently posted tweet(s), the which
# will be deleted in the next time the script is executed
PREVIOUS_TWEETS_IDS_FILEPATH = \
        os.path.expanduser("~/.dhammapada-tweet-bot.previous_tweets_ids")


FORMAT_TWITTER = """\
{verse}

{signature}\
"""

FORMAT_LOCAL = """\
{verse}

{signature:>{line_size}}\
"""


def print_debug(bot):

    print("message_twitter", bot.formatted_texts['twitter'], sep="\n\n",
          end="\n\n")

    print("message_local", bot.formatted_texts['local'], sep="\n\n",
          end="\n\n")


class DhammapadaTweetBot:

    def __init__(self):
        #  #  verse_numbers, verse = self.get_verse()
        #  #  verses = str(", ").join([str(verse_number) for verse_number in verse_numbers])
        #  #  signature = f"— Dhammapada {verses}"
        #
        #  #  self.verse = verse
        #  #  self.verse_numbers = verse_numbers
        #  #  self.signature = signature

        #  #  line_size = self.text_width(text=verse)
        #  #  signature_lenght = len(signature)
        #
        #  #  message_twitter = f"""\
        #  #  {verse}
        #  #
        #  #  {signature}\
        #  #  """
        #
        #  #  message_local = f"""\
        #  #  {verse}
        #  #
        #  #  {signature:>{line_size}}\
        #  #  """

        #  #  if DEBUG:
        #  #      print("message_twitter", message_twitter, sep="\n\n", end="\n\n")
        #  #      print("message_local", message_local, sep="\n\n", end="\n\n")
        #  #      exit(0)  # FIXME here

        #  # https://stackoverflow.com/questions/73537087/regex-to-capture-a-single-new-line-instance-but-not-2
        #  #  message_no_breaks = re.sub('(.)\n(?!\n)', r'\1 ', message_twitter)

        #  #  chunks = chunk_string_by_words(text=message_no_breaks, max_chars=278)

        #  #  self.write_verse(verse=message_local, verse_file=VERSE_FILEPATH)

        #  #  client = tweepy.Client(consumer_key=creds.CONSUMER_KEY,
        #  #                         consumer_secret=creds.CONSUMER_SECRET,
        #  #                         access_token=creds.ACCESS_TOKEN,
        #  #                         access_token_secret=creds.ACCESS_TOKEN_SECRET)

        #  #  id_list = list()

        #  #  for index, chunk in enumerate(chunks):
        #  #      if index == 0:
        #  #          response = client.create_tweet(text=chunk)
        #  #          id_list.append(response.data['id'])  # pyright: ignore
        #  #      else:
        #  #          response = client.create_tweet(text=chunk,
        #  #                                         in_reply_to_tweet_id=id_list[-1])
        #  #          id_list.append(response.data['id'])  # pyright: ignore

        #  # id(s) of the last tweet(s), to be deleted
        #  #  previous_ids = self.get_previous_ids(previous_ids_filepath=PREVIOUS_IDS_FILEPATH)

        #  # delete each of the past tweets
        #  #  for item in previous_ids:  # if empty it will just do nothing
        #  #      delete_response = client.delete_tweet(id=item)

        #  # write the id(s) of our new tweet(s) for late deletion
        #  #  self.set_new_ids(id_list, previous_ids_filepath=PREVIOUS_IDS_FILEPATH)
        pass

    def get_random_verse(self):

        verse_numbers, verse = self.get_verse()
        verses = str(", ").join([str(verse_number)
                                 for verse_number in verse_numbers])
        signature = f"— Dhammapada {verses}"

        self.verse = verse
        self.verse_numbers = verse_numbers
        self.signature = signature

    def format_texts(self):

        verse = self.verse
        signature = self.signature

        line_size = self.text_width(text=verse)

        message_twitter = FORMAT_TWITTER.format(verse=verse,
                                                signature=signature)

        message_local = FORMAT_LOCAL.format(verse=verse,
                                            signature=signature,
                                            line_size=line_size)

        formatted_texts = {
                "twitter": message_twitter,
                "local": message_local,
                }
        self.formatted_texts = formatted_texts

    def twitter_connect(self):

        client = tweepy.Client(consumer_key=creds.CONSUMER_KEY,
                               consumer_secret=creds.CONSUMER_SECRET,
                               access_token=creds.ACCESS_TOKEN,
                               access_token_secret=creds.ACCESS_TOKEN_SECRET)
        self.client = client

    def twitter_post(self):

        client = self.client
        message_twitter = self.formatted_texts["twitter"]

        message_no_breaks = re.sub('(.)\n(?!\n)', r'\1 ', message_twitter)

        chunks = self._chunk_string_by_words(text=message_no_breaks,
                                             max_chars=278)

        id_list = list()

        for index, chunk in enumerate(chunks):
            if index == 0:
                response = client.create_tweet(text=chunk)
                id_list.append(response.data['id'])  # pyright: ignore
            else:
                response = client.create_tweet(text=chunk,
                                               in_reply_to_tweet_id=id_list[-1])
                id_list.append(response.data['id'])  # pyright: ignore

            self.id_list = id_list

    def get_previous_tweets_ids(self, previous_tweets_ids_filepath=\
                                        PREVIOUS_TWEETS_IDS_FILEPATH):
        """Gets ids of the previously posted tweets that are recorded in
               file in `PREVIOUS_TWEETS_IDS_FILEPATH` for deletion
        """

        if not os.path.isfile(previous_tweets_ids_filepath):
            return list()  # empty list if file still doesn't exist

        with open(previous_tweets_ids_filepath, "r") as previous_tweets_ids_file:
            previous_tweets_ids = [item.strip()
                            for item in previous_tweets_ids_file.readlines()]

        self.previous_tweets_ids = previous_tweets_ids

        return previous_tweets_ids

    def delete_previous_tweets(self):

        client = self.client
        previous_tweets_ids = self.previous_tweets_ids

        deletion_responses = list()

        # delete each of the past tweets
        for item in previous_tweets_ids:  # if empty it will just do nothing
            response = client.delete_tweet(id=item)
            deletion_responses.append(response)

        self.deletion_responses = deletion_responses

        return deletion_responses

    def write_new_tweets_ids_to_local_file(self, previous_tweets_ids_filepath=\
                                        PREVIOUS_TWEETS_IDS_FILEPATH):
        """Locally writes the ids of the tweet(s) currently being posted to
               file in `PREVIOUS_TWEETS_IDS_FILEPATH` for late deletion
        """

        id_list = self.id_list

        # this line: 1. converts a list[int] to a list[char] and 2. str.join()'s
        # that list of chars in a string, separated by a newline (this will be
        # written to a file later)
        new_tweets_ids = str("\n").join([str(numeric) for numeric in id_list])

        with open(previous_tweets_ids_filepath,
                  "w") as previous_tweets_ids_file:

            previous_tweets_ids_file.write(new_tweets_ids)

        self.new_tweets_ids = new_tweets_ids

        return new_tweets_ids

    def write_verse_to_local_file(self, verse_file=VERSE_FILEPATH):
        """Writes the current verse being posted to the file in
               `VERSE_FILEPATH`
        """

        verse = self.formatted_texts['local']

        with open(verse_file, "w") as fd:
            fd.write(verse)

    def get_verse(self):
        """Gets a random verse from The Dhammapada, from the file in
               `DHAMMAPADA_JSON_FILEPATH`
        """

        with open(DHAMMAPADA_JSON_FILEPATH, "r") as dhammapada_json_file:
            dhammapada_json = json.load(dhammapada_json_file)

        keys = dhammapada_json.keys()
        random_choice = random.choice(list(keys))

        return dhammapada_json[random_choice]

    def text_width(self, text):
        """Iterates over all the lines of the verse and return the number
               of characters from the lenghtiest line; used for formatting
        """

        lines = text.split('\n')
        lenghtiest_line = max(map(len, lines))

        return lenghtiest_line

    def _chunk_string_by_words(self, text, max_chars):
        """Chunk the text in words, so we can divide it into more tweets if it
               doesn't fit into just one, because of X limitations
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


if __name__ == "__main__":

    bot = DhammapadaTweetBot()

    bot.get_random_verse()
    bot.format_texts()

    if DEBUG:
        print_debug(bot=bot)
        exit(0)

    bot.write_verse_to_local_file()

    bot.twitter_connect()
    bot.twitter_post()

    bot.get_previous_tweets_ids()
    bot.delete_previous_tweets()

    bot.write_new_tweets_ids_to_local_file()


