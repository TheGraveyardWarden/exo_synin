from website.db import db
from .user import user_validator
from .message import message_validator
from .group import group_validator
from .pv import pv_validator
from .room import room_validator

def create_collection(collection, validator):
    try:
        db.create_collection(collection)
    except:
        pass

    db.command("collMod", collection, validator=validator)

create_collection("user", user_validator)
create_collection("message", message_validator)
create_collection("group", group_validator)
create_collection("pv", pv_validator)
create_collection("room", room_validator)
