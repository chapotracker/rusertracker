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
        # It is possible to interleave these two using pause_after=-1, which generates a None result after each batch
        # returned by a request (including empty ones). Just hop between the two streams this way.
        cstream = self._r.subreddit(self._subreddit).stream.comments(skip_existing=skip_existing, pause_after=-1)
        sstream = self._r.subreddit(self._subreddit).stream.submissions(skip_existing=skip_existing, pause_after=-1)
        while True:
            try:
                for stream in (cstream, sstream):
                    for item in stream:
                        if item is None:
                            break
                        yield item.author.name, int(item.created_utc), item.permalink
            except Exception as e:
                self._logger.error(f"Encountered error while streaming: \"{e}\", sleeping 10 seconds...")
                time.sleep(10)
