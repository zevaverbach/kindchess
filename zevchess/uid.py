from uuid import uuid4

import zevchess.ztypes as t


def make_unique_id() -> t.Uid:
    uid = str(uuid4())
    return t.Uid(uid)
