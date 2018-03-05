from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import praw
import telegram
import config as cfg

reddit = praw.Reddit(client_id=cfg.reddit_id,
                     client_secret=cfg.reddit_secret,
                     user_agent=cfg.reddit_user_agent)

bot = telegram.Bot(cfg.telegram_token)

sched = BlockingScheduler()

cache = []

def print_title(title, permalink):
    cache.append(permalink)
    return (title + ' https://www.reddit.com' + permalink + '\n\n')


@sched.scheduled_job('interval', seconds=cfg.manga_interval)
def scrape_manga():
    print('Checking for manga at ' + str(datetime.now()))
    output = ''
    for manga in cfg.manga_list:
        for submission in reddit.subreddit('manga').search(manga, sort='new', time_filter='day'):
            title = submission.title.lower()
            if '[disc]' in title and submission.permalink not in cache:
                output += print_title(submission.title, submission.permalink)
    if output != '':
        bot.send_message(chat_id=57658796, text='MANGA:\n\n' + output)


@sched.scheduled_job('interval', seconds=cfg.re_zero_interval)
def scrape_re_zero():
    print('Checking for new Re:Zero chapter at ' + str(datetime.now()))
    output = ''
    for submission in reddit.subreddit('re_zero').search('[Translation]', sort='new', time_filter='day'):
        if ('[Translation]' in submission.title and not submission.is_self and submission.permalink not in cache
            and submission.author == 'TranslationChicken'):
            output += print_title(submission.title, submission.permalink)
    if output != '':
        bot.send_message(chat_id=57658796, text='RE:ZERO:\n\n' + output)


@sched.scheduled_job('interval', seconds=cfg.anime_interval)
def scrape_anime():
    print('Checking for anime at ' + str(datetime.now()))
    output = ''
    for anime in cfg.anime_list:
        for submission in reddit.subreddit('anime').search(anime, sort='new', time_filter='day'):
            title = submission.title.lower()
            if '[spoilers]' in title and 'discussion' in title and submission.is_self and submission.permalink not in cache:
                output += print_title(submission.title, submission.permalink)
    if output != '':
        bot.send_message(chat_id=57658796, text='ANIME:\n\n' + output)


@sched.scheduled_job('interval', seconds=cfg.clear_interval)
def clear_cache():
    print('Resetting cache at ' + str(datetime.now()))
    del cache[:]


clear_cache()
scrape_manga()
scrape_re_zero()
scrape_anime()
sched.start()