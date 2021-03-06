# py-meowbot

This is meant to be run on python3.6

Utilizes two external libraries:
* discord.py 
  * not the dev version, but the one in pypi/pip
  * https://github.com/Rapptz/discord.py
* googletrans
  * interfaces with Google Translates API for free
  * beware of using the bulk functions, people getting banned have been reported
  * https://github.com/ssut/py-googletrans
 
## Installation

* Make sure python3.6 is enabled as default
* Dependencies:

```
python3 -m pip install -U discord.py
pip install googletrans
```

## Running the bot

Again, `python` here should reference 3.6

```
python bot.py
```

## Required: Bot token

* This token is generated by Discord API and fixed (unless I regenerate it).
* Grab it from Heroku's Settings tab, under "hidden config vars"
* The bot will look into your environment variables for it, so export it like:

```
export discord_token="<your_token_string_here>"
```

## Testing

1. Pull the branch locally
2. Do some changes
3. Put the bot in maintenace mode in Heroku
4. Launch the bot with `python bot.py`

## Submitting code

* Make sure to test locally before pushing new changes
* Keep the code clean and pep8 (lol, I won't review changes but _will smack_ you if you break it)

# Functions

* Auto-translate back and forth from #channel1 to #channel2
* Some manipulation so emotes/mentions/channels don't get sent to the translation request, and are rendered decently
* Translate to Eng/Kor on demand
* A few configurable values
* Lang mapping so `:flag_xx:` make sense as Discord emotes, and are appended to the translation indicating the origin language

## Not supported / to-do / wish list

* Expand the configurable values to support multiple servers
* Add new languages / channels to the auto-translation part
* Bakes and delivers cookies
