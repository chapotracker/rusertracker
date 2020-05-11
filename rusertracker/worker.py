import logging
import praw
import redis
import threading
from rusertracker.stream import Stream


class SubredditWorker(threading.Thread):
    def __init__(self, evt: threading.Event, subreddit: str, user_agent: str, user: str, redis_kwargs: dict,
                 ttl: int=7 * 86400):
        self._logger = logging.getLogger(f"rusertracker.worker.{subreddit}")
        self._evt = evt
        self._praw_args = (user,)
        self._praw_kwargs = {"user_agent": user_agent}
        self._subreddit = subreddit.lower()
        self._reddit = None
        self._stream = None
        self._redis = redis.Redis(**redis_kwargs)
        self._ttl = ttl
        super().__init__()
        self.daemon = False

    def _setup_reddit_connection(self) -> None:
        if self._reddit:
            return
        self._reddit = praw.Reddit(*self._praw_args, **self._praw_kwargs)
        self._stream = Stream(self._subreddit, self._reddit)
        self._logger.info(f"Connected as {self._reddit.user.me().name}")

    def run(self) -> None:
        self._setup_reddit_connection()

        self._logger.info("Starting worker")
        try:
            for username, timestamp, link in self._stream.userstream():
                if self._evt.is_set():
                    break
                self._logger.debug(username)
                self._redis.set(f"{self._subreddit}|{username}", f"{timestamp}|{link}")
                self._redis.expire(f"{self._subreddit}|{username}", self._ttl)
        except KeyboardInterrupt:
            pass
        self._logger.info("Stopped worker")
