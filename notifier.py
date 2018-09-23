from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import praw
import prawcore
import telegram
import config as cfg

reddit = praw.Reddit(client_id=cfg.reddit_id,
                     client_secret=cfg.reddit_secret,
                     user_agent=cfg.reddit_user_agent)

bot = telegram.Bot(cfg.telegram_token)

sched = BlockingScheduler()

cache = []


def print_title(title, permalink):
    """Prints post title to console and adds post link to cache
    """
    cache.append(permalink)
    try:
        print(title)
    except UnicodeEncodeError:
        print('Error with printing the name')
    return (title + ' https://www.reddit.com' + permalink + '\n\n')


@sched.scheduled_job('interval', seconds=cfg.manga_interval)
def scrape_manga():
    """Searches Reddit for each manga in the list for new discussion posts
    """
    print('Checking for manga at ' + str(datetime.now()))
    output = ''
    for manga in cfg.manga_list:
        try:
            for submission in reddit.subreddit('manga').search(manga, sort='new', time_filter='day'):
                title = submission.title.lower()
                if '[disc]' in title and submission.permalink not in cache:
                    output += print_title(submission.title, submission.permalink)
        except prawcore.exceptions.ServerError:
            print('Error when searching for ' + manga)
    if output != '':
        bot.send_message(chat_id=cfg.telegram_id, text='MANGA:\n\n' + output)


@sched.scheduled_job('interval', seconds=cfg.re_zero_interval)
def scrape_re_zero():
    """Searches Reddit for new Re:Zero discussion posts
    """
    print('Checking for new Re:Zero chapter at ' + str(datetime.now()))
    output = ''
    try:
        for submission in reddit.subreddit('re_zero').search('[Translation]', sort='new', time_filter='day'):
            if '[Translation]' in submission.title and not submission.is_self and submission.permalink not in cache:
                output += print_title(submission.title, submission.permalink)
    except prawcore.exceptions.ServerError:
        print('Error when searching for Re:Zero')
    if output != '':
        bot.send_message(chat_id=cfg.telegram_id, text='RE:ZERO:\n\n' + output)


@sched.scheduled_job('interval', seconds=cfg.anime_interval)
def scrape_anime():
    """Searches Reddit for each anime in the list for new discussion posts
    """
    print('Checking for anime at ' + str(datetime.now()))
    output = ''
    for anime in cfg.anime_list:
        try:
            for submission in reddit.subreddit('anime').search(anime, sort='new', time_filter='day'):
                title = submission.title.lower()
                if 'discussion' in title and submission.link_flair_text == 'Episode' and submission.is_self and submission.permalink not in cache:
                    output += print_title(submission.title, submission.permalink)
        except prawcore.exceptions.ServerError:
            print('Error when searching for ' + anime)
    if output != '':
        bot.send_message(chat_id=cfg.telegram_id, text='ANIME:\n\n' + output)


@sched.scheduled_job('interval', seconds=cfg.clear_interval)
def clear_cache():
    print('Resetting cache at ' + str(datetime.now()))
    del cache[:]


clear_cache()
scrape_manga()
scrape_re_zero()
scrape_anime()
sched.start()