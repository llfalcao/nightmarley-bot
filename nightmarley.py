import praw
import prawcore
import random
import re
import time

reddit = praw.Reddit('nightmarley-bot', user_agent="console:Nightmarley-Bot:v1.0")

keywords = {'nightmare': "> nightMare\n\n*nightMarley"}

marcel_responses = ["Who?",
                    "Marcel? Never heard of him.",
                    ]

footer = "\n\n***\n\n*^I ^am ^~~free~~ ^a ^bot, ^and ^this ^action ^was ^performed ^automatically.*"

while True:
    try:
        print("Nightmarley-Bot is now running.")
        for comment in reddit.subreddit('nightmarleybot+titanfolk').stream.comments():
            if comment.saved:
                print("---\n" + comment.id + " is already saved.")
                continue
            if comment.author.name.lower() == 'nightmarley-bot':
                continue

            comment_lower = comment.body.lower()

            keyword = None
            for k in keywords:
                # Avoid spam
                keyword_count = re.findall(r'\b' + k.lower() + '(?=s| |$|.)', comment_lower)
                if len(keyword_count) >= 2:
                    print("---\n[" + comment.id + " : " + comment.author.name
                          + "] Spam: Duplicate keyword (", len(keyword_count), "x ", k.lower(), ");"
                          + " ignoring...", sep='')
                    continue
                if len(keyword_count) == 1:
                    keyword = k
                    break

            if keyword == comment_lower:
                print("---\n[" + comment.id + " : " + comment.author.name
                      + "] Spam: Keyword alone (" + keyword + "); ignoring...")
                continue

            if keyword is not None:
                print("---\n[" + comment.id + "] Keyword match: " + keyword)
                comment.save()
                comment.reply(keywords[keyword] + footer)
                print("> Replied to " + comment.author.name)
                continue

            if re.search(r'^(?=.*\bmarcel\b)(?=.*\bbrother\b)', comment_lower):
                print("---\n[" + comment.id + "] Keyword match: Marcel/Brother")
                comment.save()
                comment.reply(random.choice(marcel_responses) + footer)
                print("> Replied to " + comment.author.name)

    except praw.exceptions.APIException as e:
        for subexception in e:
            print("Subexception: " + subexception.error_type + "\n")
            if subexception.error_type == 'RATELIMIT':
                delay = re.search(r"(\d+) minutes", subexception.message)
                if delay:
                    delay_seconds = int(delay.group(1)) * 60 + 60
                    print("---\nComment rate limit reached; sleeping for " + delay.group(0) + ".")
                    time.sleep(delay_seconds)
                else:
                    delay = re.search(r"(\d+) seconds", subexception.message)
                    delay_seconds = int(delay.group(1)) + 60
                    print("---\nComment rate limit reached; sleeping for", delay_seconds, "seconds.")
                    time.sleep(delay_seconds)
    except prawcore.exceptions.ServerError as e:
        print("---\n[ServerError] Reddit is down (HTTP Error %s); sleeping for 2min." % e.response.status_code)
        time.sleep(120)
        pass
    except prawcore.exceptions.ResponseException as e:
        print("---\n[ResponseException] HTTP Error %s; sleeping for 2min." % e.response.status_code)
        time.sleep(120)
        pass
    except prawcore.exceptions.RequestException as e:
        print("---\n[RequestException] %s; sleeping for 5min." % e.original_exception)
        time.sleep(300)
        pass
    else:
        raise Exception
