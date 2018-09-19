import datetime
import discord
import re
from googletrans import Translator

from langs import mapping

client = discord.Client()
translator = Translator()

token = 'NDg1NjY2MzI0ODc0Mzk1NjQ5.DoMlMg.GDb6TVSOsa-lU7bbaDlyBzCrbXI'
korean_channel_id = '491240895098650624' #korean
eng_channel_id = '491783217704337408' #korean_translated
auto_translate = True; #kor -> eng
auto_translate_reverse = False; #eng -> kor

@client.event
async def on_ready():
    time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    print(time + ' Logged in to Discord server')


@client.event
async def on_message(message):
    global korean_channel_id
    global eng_channel_id
    global auto_translate
    global auto_translate_reverse

    ################################################
    ## These cases require no permissions
    #
    # auto-translate foreign -> Eng
    if (message.channel.id == korean_channel_id) and auto_translate and not message.author.bot and not message.content.startswith('~'):
        eng_channel = client.get_channel(eng_channel_id)
        dude = message.author.nick or message.author.name
        #prune emojis
        msg = re.sub(r'<:.*:.*>', '', message.content)

        #do nothing if message were all emojis
        if msg is '' or msg.isspace():
            return

        try:
            t = translator.translate(msg, dest='en')
            flag = mapping.get(t.src, t.src)
            reply = '**' + dude  + '** said :flag_' + flag + ': :`' + t.text + '`'
            await client.send_message(eng_channel, reply)
        except Exception as e:
            #print(str(e))
            return


    # auto-translate Eng -> Kor
    if (message.channel.id == eng_channel_id) and auto_translate_reverse and not message.author.bot and not message.content.startswith('~'):
        korean_channel = client.get_channel(korean_channel_id)
        dude = message.author.nick or message.author.name
        #prune emojis
        msg = re.sub(r'<:.*:.*>', '', message.content)

        #do nothing if message were all emojis
        if msg is '' or msg.isspace():
            return

        try:
            t = translator.translate(msg, dest='ko')
            flag = mapping.get(t.src, t.src)
            reply = '**' + dude  + '** said :flag_' + flag + ': :`' + t.text + '`'
            await client.send_message(korean_channel, reply)
        except Exception as e:
            #print(str(e))
            return

    ############################################################
    ## Every other command below here will only work for Mods
    ## ignore everyone else
    roles = []
    for role in message.author.roles:
        roles.append(role.name)

    if 'Mods' not in roles:
            return

    # help!
    if message.content.startswith('~help'):
        reply = """```
        List of available commands:
         ~neko - just useless cuteness
         ~getkoreanchannel - show current set value
         ~setkoreanchannel [#channel_name] - set the channel where the bot should pick up Korean text from
         ~getengchannel - show current set value
         ~setengchannel [#channel_name] - set the channel where the bot should send the translated text in English
         ~autotranslate - toggle the automatic translations True and False
         ~reversedautotranslate - toggle the automatic translations from English to Foreign True and False
         ~translate [text] - Translate text into English (sends result to same channel)
         ~reversetranslate [text] - Translate text into Korean (sends result to same channel)
         ~showconf - Shows configured values
        ```"""

        await client.send_message(message.channel, reply)


    # random cute command
    if message.content.startswith('~neko'):
        reply = 'にゃーん'
        await client.send_message(message.channel, reply)

    # show conf
    if message.content.startswith('~showconf'):
        reply = """```
        * Auto-translation is [""" + str(auto_translate) + """]
        * Reverse auto-translation is [""" + str(auto_translate_reverse) + """]
        * Korean channel is #""" + client.get_channel(korean_channel_id).name + """
        * English channel is #""" + client.get_channel(eng_channel_id).name + """
        ```"""

        await client.send_message(message.channel, reply)

    # set Korean text channel
    if message.content.startswith('~setkoreanchannel'):
        try:
            server = message.server.name
            channel_text = message.content.split(' ', 1)[1].replace('#', '')
            channel = discord.utils.get(client.get_all_channels(), server__name=server, name=channel_text)
        except:
            await client.send_message(message.channel, 'Invalid channel')

        korean_channel_id = channel.id
        await client.send_message(message.channel, 'Korean text channel is now: `#'
                                    + client.get_channel(korean_channel_id).name + '`')

    # set English text channel
    if message.content.startswith('~setengchannel'):
        try:
            server = message.server.name
            channel_text = message.content.split(' ', 1)[1].replace('#', '')
            channel = discord.utils.get(client.get_all_channels(), server__name=server, name=channel_text)
        except:
            await client.send_message(message.channel, 'Invalid channel')

        eng_channel_id = channel.id
        await client.send_message(message.channel, 'English text channel is now: `#'
                                    + client.get_channel(eng_channel_id).name + '`')

    # get Korean text channel for translation
    if message.content.startswith('~getkoreanchannel'):
        await client.send_message(message.channel, 'Korean text channel is set to: `#' +
                                  client.get_channel(korean_channel_id).name + '`')


    # get English channel for translation
    if message.content.startswith('~getengchannel'):
        await client.send_message(message.channel, 'English text channel is set to: `#' +
                                  client.get_channel(eng_channel_id).name + '`')


    # enable/disable auto-translate
    if message.content.startswith('~autotranslate'):
        if auto_translate:
            auto_translate = False
        else:
            auto_translate = True

        await client.send_message(message.channel, 'Auto-translation now set to `' + str(auto_translate) + '`')

    # enable/disable auto-translate-reverse
    if message.content.startswith('~reversedautotranslate'):
        if auto_translate_reverse:
            auto_translate_reverse = False
        else:
            auto_translate_reverse = True

        await client.send_message(message.channel, 'Reverse auto-translation now set to `' + str(auto_translate_reverse) + '`')

    # translate one string on demand to English
    if message.content.startswith('~translate'):
        try:
            original_text = message.content.split(' ', 1)[1]
            t = translator.translate(original_text, dest='en')
            flag = mapping.get(t.src, t.src)
            reply = '**' + message.author.name + '** said :flag_' + flag + ': :`' + t.text + '`'
            await client.send_message(message.channel, reply)
        except Exception as e:
            print(str(e))
            await client.send_message(message.channel, 'Your request was invalid >_<')

    # translate one string on demand to Korean
    if message.content.startswith('~reversetranslate'):
        try:
            original_text = message.content.split(' ', 1)[1]
            t = translator.translate(original_text, dest='ko')
            flag = mapping.get(t.src, t.src)
            reply = '**' + message.author.name + '** said :flag_' + flag + ': :`' + t.text + '`'
            await client.send_message(message.channel, reply)
        except Exception as e:
            print(str(e))
            await client.send_message(message.channel, 'Your request was invalid >_<')


# run the bot
client.run(token)