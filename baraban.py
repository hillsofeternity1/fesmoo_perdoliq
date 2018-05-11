#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import os
import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from main import Perdoliq

update_id = None


def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    TOKEN = os.environ["TG_TOKEN"]
    bot = telegram.Bot(TOKEN)

    # get the first pending update_id,
    # this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(level=logging.DEBUG)
    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


def perdoliq(username, password, subj, test, acc):
    try:
        app = Perdoliq(username, password)
        app.auth()
        app.get_tests()
        app.resolve(subj, test, acc, is_delayed=False)
    except Exception as e:
        return "Exception: " + str(e)


def list_test(username, password):
    try:
        app = Perdoliq(username, password)
        app.auth()
        return (app.get_tests())
    except Exception as e:
        return "Exception: " + str(e)


def echo(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            s = update.message.text.split()
            if len(s) == 6:
                msg = "usr: " + \
                    s[0] + " pass: " + \
                    s[1] + " subj: " + \
                    s[2] + " test: " + \
                    s[3] + " acc: " + s[4]
                perdoliq(s[0], s[1], s[2], s[3], s[4])
                update.message.reply_text(msg)
            else:
                msg = "Usage: <user> <pass> <subj> <test> <accuracy>"
                update.message.reply_text(msg)
            if s[0] == 'list':
                tests = list_test(s[1], s[2])
                msg = ""
            i = 0
            for subj in tests:
                msg = msg + ("[%s] %s" % (i, subj))
                i += 1
                j = 0
                for test in tests[subj]:
                    msg = msg + ("\t[%s] %s" % (j, test))
                    j += 1


if __name__ == '__main__':
    main()