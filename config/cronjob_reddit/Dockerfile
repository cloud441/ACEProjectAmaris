FROM python:3.11-slim-bookworm
LABEL authors="cloud441"

RUN mkdir -p /cronjob
COPY src/cronjob_reddit/reddit_api_scrapper.py /cronjob
COPY config/cronjob_reddit/subreddit_config.yaml /cronjob
COPY config/cronjob_reddit/requirement.txt .

# install python modules:
RUN pip install --no-cache-dir -r requirement.txt

WORKDIR cronjob

CMD ["python", "./reddit_api_scrapper.py"]