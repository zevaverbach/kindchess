from zevchess.db import r
from zevchess.commands import update_existing_uids_cache
from zevchess.queries import get_existing_uids_from_db

# limit the number of concurrent games based on load testing
# limit the number of games for a given IP address


def main():
    # cache the existing UIDs
    uids = get_existing_uids_from_db()
    update_existing_uids_cache(*uids)
