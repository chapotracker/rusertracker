import logging
import praw
import time
from typing import Iterator, Tuple


class Stream(object):
    def __init__(self, subreddit: str, r: praw.Reddit):
        self._logger = logging.getLogger("rusertracker.subclient")
        self._r = r
        self._subreddit = subreddit

    def userstream(self, skip_existing: bool=True) -> Iterator[Tuple[str, int, str]]:
        while True:
            try:
                for comment in self._r.subreddit(self._subreddit).stream.comments(skip_existing=skip_existing):
                    yield comment.author.name, int(comment.created_utc), comment.permalink
            except Exception as e:
                self._logger.error(f"Encountered error while streaming: \"{e}\", sleeping 10 seconds...")
                time.sleep(10)
