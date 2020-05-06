"""This module contains application entrypoints for using the library from the command line.
"""
import argparse
import logging
import rusertracker
import threading
import time
from rusertracker.worker import SubredditWorker


def main() -> None:
    parser = argparse.ArgumentParser(description="Maintains a list of active members of a set of subreddits.")
    parser.add_argument("-s", "--subreddits", help="List of subreddits (without r/)", nargs="+")
    parser.add_argument("-u", "--user", help="User section in praw.ini", default="default")
    parser.add_argument("-U", "--user-agent", help="User agent if not auto",
                        default=f"python:rusertracker:{rusertracker.__version__}")
    parser.add_argument("-v", "--verbose", help="Verbose logging", action="store_true")
    parser.add_argument("--redis-db", help="Redis DB Number", type=int, default=1)
    parser.add_argument("--redis-host", help="Redis host", default="localhost")
    parser.add_argument("--redis-port", help="Redis port", type=int, default=6379)
    args = parser.parse_args()

    root_logger = logging.getLogger("rusertracker")
    root_logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    formatter = logging.Formatter("%(levelname)s:%(asctime)s.%(msecs)03d:%(name)s - %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)

    logger = logging.getLogger("rusertracker.main")
    logger.info(f"Connecting as user \"{args.user}\" and user agent \"{args.user_agent}\"")
    logger.info(f"Subreddits: {', '.join(['r/' + s for s in args.subreddits])}")

    redis_kwargs = {
        "host": args.redis_host,
        "port": args.redis_port,
        "db": args.redis_db
    }

    workers = []
    evt = threading.Event()

    for subreddit in args.subreddits:
        worker = SubredditWorker(evt, subreddit, args.user_agent, args.user, redis_kwargs)
        worker.start()
        workers.append(worker)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    evt.set()

    logger.info("Waiting for workers to finish...")
    for worker in workers:
        worker.join()
    logger.info("Done")


if __name__ == "__main__":
    main()
