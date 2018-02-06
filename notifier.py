from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import praw
import telegram
import os

reddit = praw.Reddit(client_id=os.getenv(reddit_id),
                     client_secret=os.getenv(reddit_secret),
                     user_agent=os.getenv(reddit_user_agent))

bot = telegram.Bot(os.getenv(telegram_token))

sched = BlockingScheduler()

cache = []

manga_list = os.getenv(manga).split(', ')
anime_list = os.getenv(anime).split(', ')

@sched.scheduled_job('interval', seconds=os.getenv(manga_interval))
def scrape_manga():
    print('Checking for manga at ' + str(datetime.now()))
    output = ''
    for manga in cfg.manga_list:
        for submission in reddit.subreddit('manga').search(manga, sort='new', time_filter='day'):
            if '[DISC]' in submission.title and not submission.is_self and submission.permalink not in cache:
                print(submission.title + ' ' + submission.url)
                cache.append(submission.permalink)
                output += (submission.title + ' https://www.reddit.com' + submission.permalink + '\n\n')
    if output != '':
        bot.send_message(chat_id=57658796, text='MANGA:\n\n' + output)


@sched.scheduled_job('interval', seconds=os.getenv(re_zero_interval))
def scrape_re_zero():
    print('Checking for new Re:Zero chapter at ' + str(datetime.now()))
    output = ''
    for submission in reddit.subreddit('re_zero').search('[Translation]', sort='new', time_filter='day'):
        if ('[Translation]' in submission.title and not submission.is_self and submission.permalink not in cache
            and submission.author == 'TranslationChicken'):
            print(submission.title + ' ' + submission.url)
            cache.append(submission.permalink)
            output += (submission.title + ' https://www.reddit.com' + submission.permalink + '\n\n')
    if output != '':
        bot.send_message(chat_id=57658796, text='RE:ZERO:\n\n' + output)


@sched.scheduled_job('interval', seconds=os.getenv(anime_interval))
def scrape_anime():
    print('Checking for anime at ' + str(datetime.now()))
    output = ''
    for anime in cfg.anime_list:
        for submission in reddit.subreddit('anime').search(anime, sort='new', time_filter='day'):
            print(submission.title)
            if '[Spoilers]' in submission.title and submission.is_self and submission.permalink not in cache:
                print(submission.title + ' ' + submission.url)
                cache.append(submission.permalink)
                output += (submission.title + ' https://www.reddit.com' + submission.permalink + '\n\n')
    if output != '':
        bot.send_message(chat_id=57658796, text='ANIME:\n\n' + output)
        

@sched.scheduled_job('interval', seconds=os.getenv(clear_interval))
def clear_cache():
    print('Resetting cache at ' + str(datetime.now()))
    del cache[:]


clear_cache()
scrape_manga()
scrape_re_zero()
scrape_anime()
sched.start()