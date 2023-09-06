from flask import Flask, render_template, request

from loguru import logger
from elasticsearch import Elasticsearch
import os


# get IP and PORT for logs
es_ip = os.getenv("es_ip_address")
es_port = os.getenv("es_port")

# create local http certificate file:
tls_crt_content = os.getenv("tls.crt")
with open("tls.crt", "w") as f:
    f.write(tls_crt_content)

# Connect to Elasticsearch Index:
es_client = Elasticsearch(
    hosts=f"https://{es_ip}:{es_port}",
    ca_certs="tls.crt",
    basic_auth=(os.getenv("es_username"), os.getenv("es_user_password")),
)
logger.info(f"Connection established with ElasticSearch service on ip {es_ip} on port {es_port}.")

# Instantiate the Flask Web App:
app = Flask(__name__)


class Post:
    def __init__(self, username, title, text, subreddit, creation_date_utc):
        self.username = username
        self.title = title
        self.text = text
        self.creation_date_utc = creation_date_utc
        self.subreddit = subreddit


def filter_result_fields(results):
    """
    Filter function to remove useless request informations.
    """
    return [
        result["_source"]
        for result in results
    ]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form.get("prompt")
        num_posts = int(request.form.get("num_posts"))
        logger.info(f"Web App received a request for {num_posts} posts with this text: {prompt}")

        es_result = es_client.search(
            index="reddit_post_index",
            query={
                "match": {
                    "title": prompt,
                }
            },
            size=num_posts,
        )

        result = es_result["hits"]["hits"]
        result = filter_result_fields(result)
        logger.info(f"ElasticSearch Index returns {len(result)} posts")

        return render_template("index.html", posts=result)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
