## dhammapada-tweet-bot.py

### dependencies

* https://github.com/ingeniumstudio/display-dhammapada
* python 3
* tweepy

### how to use

0. clone the repository
1. fill in with your api credentials inside `./dhammapada\_tweet\_bot\_credentials.py`
2. run via crontab the script `./dhammapada-tweet-bot.py`

### `crontab -e` example

`0 */6 * * * /home/USERNAME/.venv/bin/python /home/USERNAME/cronjobs/dhammapada-tweet-bot/dhammapada-tweet-bot.py`

First is the path to the python executable, then the script.

This would run it at 0h, 6h, 12h and 18h.

### testing the credentials

You can run the script manually to test the credentials:

```
python ./dhammapada-tweet-bot.py
```
