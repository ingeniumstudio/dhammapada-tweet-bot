## dhammapada-tweet-bot.py

### dependencies

* python 3
* tweepy
* X/twitter api credentials

### how to use

0. clone the repository
1. install the dependencies (python 3 and `pip install tweepy`)
2. fill in with your api credentials inside the file `dhammapada_tweet_bot_credentials.py`
3. rename the file `dhammapada_tweet_bot_credentials.py` to `secrets_xapi.py`
4. run via crontab the script `dhammapada-tweet-bot.py`; you can follow the example below.

### `crontab -e` example

`0 */6 * * * /home/USERNAME/.venv/bin/python /home/USERNAME/cronjobs/dhammapada-tweet-bot/dhammapada-tweet-bot.py`

First is the path to the python executable, then the script.

This would run it at 0h, 6h, 12h and 18h.

### testing the credentials

You can run the script manually to test the credentials:

```
python ./dhammapada-tweet-bot.py
```
