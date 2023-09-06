import os

import requests
import yaml
from datetime import datetime, timedelta
from yaml.loader import SafeLoader
from typing import List, Dict, Any


from elasticsearch import Elasticsearch
from loguru import logger

FIVE_MIN_IN_SEC = 5 * 60


def filter_and_format_posts_json(raw_json: Dict[str, Any]) -> List[Dict[str, str]]:
    post_dicts = []
    for post_json in raw_json["data"]["children"]:
        post_dict = post_json["data"]

        # filter to have only new posts added during the last 5 minutes:
        utc_now = datetime.utcnow().replace(microsecond=0)
        post_date_utc = datetime.fromtimestamp(post_dict["created_utc"])
        if (utc_now - post_date_utc).total_seconds() < FIVE_MIN_IN_SEC:
            post_dicts.append(
                {
                    "username": post_dict["author_fullname"],
                    "title": post_dict["title"],
                    "text": post_dict["selftext"],
                    "subreddit": post_dict["subreddit"],
                    "creation_date_utc": datetime.fromtimestamp(post_dict["created_utc"]).strftime("%m/%d/%Y, %H:%M:%S"),
                }
            )

    return post_dicts


def get_subreddit_posts(
        subreddit: str,
        max_posts: int = 10,
) -> List[Dict[str, str]]:
    timeframe = 'hour'  # hour, day, week, month, year, all
    listing = 'new'  # controversial, best, hot, new, random, rising, top
    user_agent = "cronjob reddit agent"

    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={max_posts}&t={timeframe}'
        request = requests.get(base_url, headers={'User-agent': user_agent})
    except:
        logger.error(f"Impossible to request Reddit API on this url: {base_url}")

    return filter_and_format_posts_json(request.json())


def main() -> None:
    # get subreddit name list:
    with open("subreddit_config.yaml") as f:
        yaml_data = yaml.load(f, Loader=SafeLoader)
        subreddit_list = yaml_data["subreddit_list"]

    # create local http certificate file:
    tls_crt_content = os.getenv("tls.crt")
    with open("tls.crt", "x") as f:
        f.write(tls_crt_content)

    last_subreddits_posts = []
    for subreddit in subreddit_list:
        last_subreddit_posts = get_subreddit_posts(subreddit, 100)
        last_subreddits_posts.extend(last_subreddit_posts)
        logger.info(f"{len(last_subreddit_posts)} new posts found on subreddit {subreddit}.")

    if len(last_subreddits_posts) == 0:
        logger.info("There is no new post on scrapped subreddits.")
        return

    es_port = os.getenv("es_port")
    es_ip = os.getenv("es_ip_address")
    es_client = Elasticsearch(
        f"https://{es_ip}:{es_port}",
        ca_certs="tls.crt",
        basic_auth=(os.getenv("es_username"), os.getenv("es_user_password")),
    )
    logger.info(f"Connection established with ElasticSearch service on ip {es_ip} on port {es_port}.")

    for post in last_subreddits_posts:
        es_client.index(
            index="reddit_post_index",
            document=post,
        )
    logger.info(f"{len(last_subreddits_posts)} new posts added to the ElasticSearch Index.")
    es_client.indices.refresh(index="reddit_post_index")
    logger.info("Index refreshed.")


if __name__ == "__main__":
    main()
