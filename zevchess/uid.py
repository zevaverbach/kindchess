from uuid import uuid4, UUID

from db import Uid


def make_unique_id() -> Uid:
    uid = str(uuid4())
    return Uid(uid)
