import datetime
import discord
import emoji
import time
import os
import re
from googletrans import Translator

from langs import mapping

client = discord.Client()
translator = Translator()
startTime = time.time()

token = os.environ['discord_token']
korean_channel_id = 560101685398339585  # korean
jp_channel_id = 560102616525307904  # japanese
eng_channel_id = 560102850475327491  # english
translated_channel_ids = {'en': eng_channel_id,
                          'ko': korean_channel_id,
                          'ja': jp_channel_id}
auto_translate = True  # kor -> eng


@client.event
async def on_ready():
    t = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    print(t + ' Logged in to Discord server')


async def sanitize_message(message):
    """ Function receives a Message with potentially channel/user mention/emotes
        and sanitizes it as:
            - channels: replaced with simple "#channel_name" string
            - user mentions: replaced with simple "@user_name" string
            - emotes: stored and returned as-is
    """
    msg = message.content
    sane_msg = {'msg': '', 'emotes': []}
    # channels
    channel_regex = r'<#\w+>'
    for match in re.findall(channel_regex, msg):
        channel_id = match.replace('<#', '').replace('>', '')
        channel_name = client.get_channel(channel_id).name
        msg = re.sub(match, '#' + channel_name, msg)

    # user mentions
    mention_regex = r'<@!?\w+>'
    for match in re.findall(mention_regex, msg):
        user_id = match.replace('<@', '').replace('>', '').replace('!', '')
        user = await client.fetch_user(user_id)
        user_name = user.display_name or user.name
        msg = re.sub(match, '@' + user_name, msg)

    # unicode emotes
    for c in msg:
        if c in emoji.UNICODE_EMOJI:
            sane_msg['emotes'].append(c)
            msg = msg.replace(c, '')

    # discord emotes
    emote_regex = r'<a?:\w+:\w+>'
    sane_msg['emotes'].extend(re.findall(emote_regex, msg))
    sane_msg['msg'] = re.sub(emote_regex, '', msg)

    return sane_msg


@client.event
async def on_message(message):
    global korean_channel_id
    global jp_channel_id
    global eng_channel_id
    global auto_translate

    ################################################
    # These cases require no permissions
    #
    # auto-translate msg sent to any translation channel
    # and send it to the others
    if (message.channel.id in translated_channel_ids.values())\
            and auto_translate and not message.author.bot and not message.content.startswith('~'):
        # do nothing if message is an image/video/etc.
        if message.attachments:
            return

        dude = message.author.nick or message.author.name
        sane = await sanitize_message(message)

        reply = '**' + dude + '** said: ' + ''.join(sane['emotes'])
        replies = {'en': reply, 'ko': reply, 'ja': reply}
        original_lang = [k for k,v in translated_channel_ids.items() if v == message.channel.id][0]
        # remove the original channel from the list of receivers
        del replies[original_lang]
        if sane['msg']:
            for lang in replies.keys():
                try:
                    t = translator.translate(sane['msg'], dest=lang)
                    flag = mapping.get(t.src.lower(), t.src.lower())
                    replies[lang] = '**' + dude + '** said :flag_' + flag + ': :`' +\
                                    t.text + '` ' + ''.join(sane['emotes'])
                except Exception:
                    return

        for lang, reply in replies.items():
            chan = client.get_channel(translated_channel_ids[lang])
            await chan.send(replies[lang])

    ############################################################
    # Every other command below here will only work for Mods
    # ignore everyone else
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
         ~getjpchannel - show current set value
         ~setjpchannel [#channel_name] - set the channel where the bot should pick up Japanese text from
         ~getengchannel - show current set value
         ~setengchannel [#channel_name] - set the channel where the bot should send the translated text in English
         ~autotranslate - toggle the automatic translations True and False
         ~translatetoeng [text] - Translate text into English (sends result to same channel)
         ~translatetokorean [text] - Translate text into Korean (sends result to same channel)
         ~translatetojp [text] - Translate text into Japanese (sends result to same channel)
         ~showconf - Shows configured values
         ~uptime - Shows uptime
        ```"""

        await message.channel.send(reply)

    # show uptime
    if message.content.startswith('~uptime'):
        secs = time.time() - startTime
        reply = 'I have been awake for ' + str(secs / 60) + ' mins'
        await message.channel.send(reply)

    # random cute command
    if message.content.startswith('~neko'):
        reply = 'にゃーん'
        await message.channel.send(reply)

    # show conf
    if message.content.startswith('~showconf'):
        reply = """```
        * Auto-translation is [""" + str(auto_translate) + """]
        * Korean channel is #""" + client.get_channel(korean_channel_id).name + """
        * Japanese channel is #""" + client.get_channel(jp_channel_id).name + """
        * English channel is #""" + client.get_channel(eng_channel_id).name + """
        ```"""

        await message.channel.send(reply)

    # set Korean text channel
    if message.content.startswith('~setkoreanchannel'):
        try:
            server = message.guild.name
            channel_text = message.content.split(' ', 1)[1].replace('#', '')
            channel = discord.utils.get(client.get_all_channels(), server__name=server, name=channel_text)
        except Exception:
            await message.channel.send('Invalid channel')

        korean_channel_id = channel.id
        await message.channel.send('Korean text channel is now: `#'
                                  + client.get_channel(korean_channel_id).name + '`')

    # set Japanese text channel
    if message.content.startswith('~setjpchannel'):
        try:
            server = message.guild.name
            channel_text = message.content.split(' ', 1)[1].replace('#', '')
            channel = discord.utils.get(client.get_all_channels(), server__name=server, name=channel_text)
        except Exception:
            await message.channel.send('Invalid channel')

        jp_channel_id = channel.id
        await message.channel.send('Japanese text channel is now: `#'
                                    + client.get_channel(jp_channel_id).name + '`')

    # set English text channel
    if message.content.startswith('~setengchannel'):
        try:
            server = message.guild.name
            channel_text = message.content.split(' ', 1)[1].replace('#', '')
            channel = discord.utils.get(client.get_all_channels(), server__name=server, name=channel_text)
        except Exception:
            await message.channel.send('Invalid channel')

        eng_channel_id = channel.id
        await message.channel.send('English text channel is now: `#'
                                  + client.get_channel(eng_channel_id).name + '`')

    # get Korean text channel for translation
    if message.content.startswith('~getkoreanchannel'):
        await message.channel.send('Korean text channel is set to: `#' +
                                  client.get_channel(korean_channel_id).name + '`')

    # get Japanese text channel for translation
    if message.content.startswith('~getjpchannel'):
        await message.channel.send('Japanese text channel is set to: `#' +
                                  client.get_channel(jp_channel_id).name + '`')

    # get English channel for translation
    if message.content.startswith('~getengchannel'):
        await message.channel.send('English text channel is set to: `#' +
                                  client.get_channel(eng_channel_id).name + '`')

    # enable/disable auto-translate
    if message.content.startswith('~autotranslate'):
        if auto_translate:
            auto_translate = False
        else:
            auto_translate = True

        await message.channel.send('Auto-translation now set to `' + str(auto_translate) + '`')

    # translate one string on demand to English
    if message.content.startswith('~translatetoeng'):
        try:
            original_text = message.content.split(' ', 1)[1]
            t = translator.translate(original_text, dest='en')
            flag = mapping.get(t.src, t.src)
            reply = '**' + message.author.name + '** said :flag_' + flag + ': :`' + t.text + '`'
            await message.channel.send(reply)
        except Exception as e:
            print(str(e))
            await message.channel.send('Your request was invalid >_<')

    # translate one string on demand to Korean
    if message.content.startswith('~translatetokorean'):
        try:
            original_text = message.content.split(' ', 1)[1]
            t = translator.translate(original_text, dest='ko')
            flag = mapping.get(t.src, t.src)
            reply = '**' + message.author.name + '** said :flag_' + flag + ': :`' + t.text + '`'
            await message.channel.send(reply)
        except Exception as e:
            print(str(e))
            await message.channel.send('Your request was invalid >_<')

    # translate one string on demand to Japanese
    if message.content.startswith('~translatetojp'):
        try:
            original_text = message.content.split(' ', 1)[1]
            t = translator.translate(original_text, dest='ja')
            flag = mapping.get(t.src, t.src)
            reply = '**' + message.author.name + '** said :flag_' + flag + ': :`' + t.text + '`'
            await message.channel.send(reply)
        except Exception as e:
            print(str(e))
            await message.channel.send('Your request was invalid >_<')

    # say something in #channel
    if message.content.startswith('~say'):
        try:
            split = message.content.split(' ', 2)
            channel_id = split[1].replace('<#', '').replace('>', '')
            msg = split[2]
            channel_obj = client.get_channel(channel_id)
            await channel_obj.send(msg)
        except Exception as e:
            print(str(e))
            await message.channel.send('Wrong syntax: ~say #channel memes go here')


# run the bot
client.run(token)
