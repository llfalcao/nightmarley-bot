import praw
import prawcore
import random
import re
import time

reddit = praw.Reddit('nightmarley-bot', user_agent="console:Nightmarley-Bot:v1.0")
# reddit.read_only = True

keywords = {'nightmare': "> nightMare\n\n*nightMarley"}

marcel_responses = ["Who?",
                    "Marcel? Never heard of him.",
                    ]

footer = "\n\n***\n\n*^I ^am ^~~free~~ ^a ^bot, ^and ^this ^action ^was ^performed ^automatically.*"

while True:
    print("Nightmarley-Bot is now running.")
    try:
        for comment in reddit.subreddit('nightmarleybot+titanfolk').stream.comments():
            # Ignore the bot's own comments and the ones that the bot has already replied to.
            if comment.saved:
                print("---\n" + comment.id + " is saved already.")
                continue
            if comment.author.name.lower() == 'nightmarley-bot':
                continue

            # Ignore comments in the chapter discussion threads,
            # as well as any comment containing "NIGHTMARE" in all caps, to reduce spamming.
            if comment.submission.id in ['mmfzi8', 'mkdkiy', 'mm2c8e', 'mi265l']:
                continue
            if 'NIGHTMARE' in comment.body:
                print("---\n[" + comment.id + " : " + comment.author.name
                      + "] Spam: All caps; ignoring...")
                continue

            comment_lower = comment.body.lower()

            keyword = None
            for k in keywords:
                # Prevent spam by finding duplicate keywords.
                duplicates = re.findall(r'\b' + k.lower() + r'\b', comment_lower)
                if len(duplicates) >= 2:
                    print("---\n[" + comment.id + " : " + comment.author.name
                          + "] Spam: Duplicate keyword (qty.: ", len(duplicates), "); ignoring...", sep='')
                    continue

                # Ignore comments spamming "200K nightmare" to trigger both the AutoModerator and the Nightmarley Bot.
                if '200k' in comment_lower:
                    print("---\n[" + comment.id + " : " + comment.author.name
                          + "] Spam: \"200k\"; ignoring...")
                    continue

                # Look for each keyword on the comment's body.
                # The priority is based on how they're ordered in the dictionary,
                # not as soon as a keyword is found.
                if re.search(r'\b' + k.lower() + r'\b', comment_lower):
                    keyword = k
                    break

            # Prevent spam by ignoring comments containing the keyword alone.
            if keyword == comment_lower:
                print("---\n[" + comment.id + " : " + comment.author.name
                      + "] Spam: Keyword alone (" + keyword + "); ignoring...")
                continue

            if keyword is not None:
                # Not printing the comment on the console until chapter 139 is out, to avoid spoilers.
                print("---\n[" + comment.id + "] Keyword match: " + keyword)
                comment.save()
                comment.reply(keywords[keyword] + footer)
                print("> Replied to " + comment.author.name)
                continue

            if re.search(r'^(?=.*\bmarcel\b)(?=.*\bbrother\b)', comment_lower):
                # Not printing the comment on the console until chapter 139 is out, to avoid spoilers.
                print("---\n[" + comment.id + "] Keyword match: Marcel/Brother")
                comment.save()
                comment.reply(random.choice(marcel_responses) + footer)
                print("> Replied to " + comment.author.name)

    # Suspend activity when the account reaches Reddit's comment rate limit.
    except praw.exceptions.APIException as e:
        for subexception in e.items:
            print("Subexception: " + subexception.error_type + "\n")
            if subexception.error_type == 'RATELIMIT':
                delay = re.search(r"(\d+) minutes", subexception.message)
                if delay:
                    delay_seconds = int(delay.group(1)) * 60 + 60
                    print("Delaying replies for " + delay.group(0) + ".")
                    time.sleep(delay_seconds)
                else:
                    delay = re.search(r"(\d+) seconds", subexception.message)
                    delay_seconds = int(delay.group(1)) + 60
                    print("Delaying replies for", delay_seconds, "seconds.")
                    time.sleep(delay_seconds)
    # Suspend activity for 1 minute in the event of a server error.
    except prawcore.exceptions.ServerError as e:
        print("Reddit is down (http error %s), sleeping..." % e.response)
        time.sleep(60)
        pass
    except prawcore.exceptions.ResponseException as e:
        print("Reddit is down (HTTP %s), sleeping..." % e.response)
        time.sleep(60)
        pass
    else:
        raise Exception
