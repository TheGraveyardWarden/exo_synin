from flask_socketio import SocketIO, emit, join_room
from flask import request
from .db import db
from flask import session
from bson.objectid import ObjectId
from website.settings import SECRET_KEY
import secrets
from string import ascii_letters
from datetime import datetime as dt
from .views.utils import create_filename, FILENAME_LENGTH, FILE_PATH, get_user_from_cookie, DEFAULT_AVATAR
from .ai import get_ai_user, ai_messages,ai_answers, make_msg, req_ai
from time import sleep


socketio = SocketIO()

def create_room_name(length):
    while True:
        room = ""
        for _ in range(length):
            room += secrets.choice(ascii_letters)
        if db.room.find_one({"name": room}) == None:
            break
    
    return room

def add_message(receiver_user, obj_id, objs):
    for i in receiver_user[objs[0]]:
        if i[objs[1]] == obj_id:
            i["new_messages"] += 1
    db.user.replace_one({"_id": ObjectId(receiver_user["_id"])}, receiver_user)

def delete_pv_group_from_user(obj_list, user_id, obj_id, objs):
    for p in obj_list:
        if p[objs[1]] == obj_id:
            db.user.update_one({"_id": ObjectId(user_id)}, {"$pull": {objs[0]: p}})

def fetch_data(collection, query, projection=None):
    if projection:
        data = db[collection].find_one(query, projection)
    else:
        data = db[collection].find_one(query)
    
    return data

def authorize_user_in_gp(user_id, group_owner, group_admins):
    authorized = 0

    for admin in group_admins:
        if ObjectId(admin) == ObjectId(user_id):
            authorized = 2
            break

    if ObjectId(user_id) == ObjectId(group_owner):
        authorized = 1
    
    return authorized

def create_message(msg, id):
    message = {
        "from": id,
        "text": msg,
        "date": dt.now(),
        "file": ""
    }
    return db.message.insert_one(message).inserted_id, message["text"]

# --------------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #

@socketio.on("connect")
def handle_connect():
    emit("log", "connected")
    user = get_user_from_cookie(session)
    db.user.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"sid": request.sid}})

    for _group in user["groups"]:
        group = db.group.find_one({"_id": ObjectId(_group["group"])}, {"_id": 0, "room": 1})
        room = db.room.find_one({"_id": ObjectId(group["room"])})
        join_room(room["name"])

    print(user["username"] + " has been connected")

@socketio.on("disconnect")
def handle_disconnect():
    emit("log", "disconnected")
    user = get_user_from_cookie(session)
    db.user.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"sid": ""}})

    if str(user["_id"]) in ai_answers.keys():
        del ai_answers[str(user["_id"])]

    print(user["username"] + " has been disconnected")

@socketio.on("seen_messages")
def handle_seen_messages(username, is_group):
    user = get_user_from_cookie(session)
    if not is_group:
        user2 = db.user.find_one({"username": username}, {"_id": 1})

        pv = db.pv.find_one({"members": {"$all": [ObjectId(user2["_id"]), ObjectId(user["_id"])]}}, {"_id": 1})
        if not pv:
            return {"success": False}

        for i in user["pvs"]:
            if i["pv"] == pv["_id"]:
                i["new_messages"] = 0
    else:
        group = db.group.find_one({"name": username}, {"_id": 1})
        if not group:
            return {"success": False}
        
        for i in user["groups"]:
            if i["group"] == group["_id"]:
                i["new_messages"] = 0

    db.user.replace_one({"_id": ObjectId(user["_id"])}, user)

@socketio.on("create_pv")
def handle_create_pv(message, receiver):
    user = get_user_from_cookie(session)
    if user["username"] == receiver:
        return {"success": False}
    receiver_user = db.user.find_one({"username": receiver})
    if not receiver_user:
        return {"success": False}

    message = {
        "from": ObjectId(user["_id"]),
        "text": message,
        "date": dt.now(),
        "file": ""
    }
    message_id = db.message.insert_one(message).inserted_id
    
    pv = db.pv.find_one({"members": {"$all": [ObjectId(receiver_user["_id"]), ObjectId(user["_id"])]}}, {"_id": 1})
    if pv:
        db.pv.update_one({"_id": ObjectId(pv["_id"])}, {"$push": {"messages": ObjectId(message_id)}})
        add_message(receiver_user, pv["_id"], ["pvs", "pv"])
        emit("msg", {"message": {"_id": str(message_id), "text": message["text"]}, "sender": user["username"], "avatar": user["avatar"], "gp_info": {
        "is_gp": False, "gp_name": ""}}, to=[receiver_user["sid"], user["sid"]])
        return {"success": True, "avatar": receiver_user["avatar"], "message": {"_id": str(message_id), "text": message["text"]}, "receiver": receiver}

    pv = {
        "members": [ObjectId(user["_id"]), ObjectId(receiver_user["_id"])],
        "messages": [message_id],
        "pinned": []
    }
    pv_id = db.pv.insert_one(pv).inserted_id

    db.user.update_one({"_id": ObjectId(user["_id"])}, {"$push": {"pvs": {"pv": ObjectId(pv_id), "new_messages": 1}}})
    db.user.update_one({"_id": ObjectId(receiver_user["_id"])}, {"$push": {"pvs": {"pv": ObjectId(pv_id), "new_messages": 1}}})

    emit("msg", {"message": {"_id": str(message_id), "text": message["text"]}, "sender": user["username"], "avatar": user["avatar"], "gp_info": {
        "is_gp": False, "gp_name": ""}}, to=[receiver_user["sid"], user["sid"]])

    return {"success": True, "avatar": receiver_user["avatar"], "message": {"_id": str(message_id), "text": message["text"]}, "receiver": receiver}

@socketio.on("create_group_channel")
def handle_create_group_channel(name, desc, is_channel):
    user = get_user_from_cookie(session)

    if db.group.find_one({"name": name}):
        return {"success": False, "message": "Group or channel with this username already exists"}
    
    room = {"name": create_room_name(10)}
    room_id = db.room.insert_one(room).inserted_id

    message = {
        "from": ObjectId(db.user.find_one({"username": "Synin"}, {"_id": 1})["_id"]),
        "text": f"Welcome to your own group {user['username']}. Hope you enjoy your flight with synin to the peak of your desired mountains.",
        "date": dt.now(),
        "file": ""
    }
    message_id = db.message.insert_one(message).inserted_id

    group = {
        "name": name,
        "description": desc,
        "is_channel": is_channel,
        "owner": ObjectId(user["_id"]),
        "room": ObjectId(room_id),
        "members": [ObjectId(user["_id"])],
        "avatar": DEFAULT_AVATAR,
        "messages": [ObjectId(message_id)],
        "admins": []
    }
    group_id = db.group.insert_one(group).inserted_id

    db.user.update_one({"_id": ObjectId(user["_id"])}, {"$push": {"groups": {"group": ObjectId(group_id), "new_messages": 0}}})
    join_room(room["name"], user["sid"])

    return {"success": True, "avatar": group["avatar"], "name": group["name"]}

@socketio.on("gp_msg")
def handle_group_msg(message, gp_name):
    user = get_user_from_cookie(session)

    group = db.group.find_one({"name": gp_name}, {"_id": 1, "room": 1, "members": 1, "is_channel": 1, "name": 1})
    if not group:
        return {"success": False}
    
    message = {
        "from": ObjectId(user["_id"]),
        "text": message,
        "date": dt.now(),
        "file": ""
    }
    message_id = db.message.insert_one(message).inserted_id

    db.group.update_one({"_id": ObjectId(group["_id"])}, {"$push": {"messages": ObjectId(message_id)}})
    
    for member_id in group["members"]:
        if member_id != user["_id"]:
            member = db.user.find_one({"_id": ObjectId(member_id)})
            add_message(member, group["_id"], ["groups", "group"])
    
    room = db.room.find_one({"_id": ObjectId(group["room"])})

    emit("msg", {"sender": user["username"], "avatar": user["avatar"], "message": {"text": message["text"], "_id": str(message_id)}, "gp_info": {
        "is_gp": not group["is_channel"], "gp_name": group["name"]}}, to=room["name"])

@socketio.on("add_member")
def handle_add_member(username, gp_name):
    user = get_user_from_cookie(session)

    group = db.group.find_one({"name": gp_name})
    if not group:
        return {"success": False}
    
    authorized = authorize_user_in_gp(user["_id"], group["owner"], group["admins"])

    if authorized:
        user2 = db.user.find_one({"username": username})
        if not user2:
            return {"success": False}
        
        if user2["_id"] in group["members"]:
            return {"success": False}

        db.user.update_one({"_id": ObjectId(user2["_id"])}, {"$push": {"groups": {"group": ObjectId(group["_id"]), "new_messages": 0}}})
        db.group.update_one({"_id": ObjectId(group["_id"])}, {"$push": {"members": ObjectId(user2["_id"])}})
        if user2["sid"] != "":
            room = db.room.find_one({"_id": group["room"]})
            join_room(room["name"], user2["sid"])
            emit("add_member", {"avatar": group["avatar"], "name": group["name"]}, to=user2["sid"])
    else:
        return {"success": False}

@socketio.on("remove_member")
def handle_remove_member(username, gp_name):
    user = get_user_from_cookie(session)

    group = db.group.find_one({"name": gp_name})
    if not group:
        return {"success": False}
    
    authorized = authorize_user_in_gp(user["_id"], group["owner"], group["admins"])

    if authorized:
        user2 = db.user.find_one({"username": username})
        if not user2:
            return {"success": False}
        
        user2_authorized = authorize_user_in_gp(user2["_id"], group["owner"], group["admins"])

        if user2_authorized == 1:
            return {"success": False}
        
        if user2_authorized == 2 and authorized == 2:
            return {"success": False}
        
        if user2["_id"] not in group["members"]:
            return {"success": False}
        
        delete_pv_group_from_user(user2["groups"], user2["_id"], group["_id"], ["groups", "group"])
        db.group.update_one({"_id": ObjectId(group["_id"])}, {"$pull": {"members": ObjectId(user2["_id"])}})
        if user2_authorized == 2:
            db.group.update_one({"_id": ObjectId(group["_id"])}, {"$pull": {"admins": ObjectId(user2["_id"])}})
        
    else:
        return {"success": False}

@socketio.on("promote_demote_admin")
def handle_promote_demote_admin(username, gp_name):
    user = get_user_from_cookie(session)

    group = db.group.find_one({"name": gp_name})
    if not group:
        return {"success": False}
    
    authorized = authorize_user_in_gp(user["_id"], group["owner"], group["admins"])

    if authorized == 1:
        user2 = db.user.find_one({"username": username})
        if not user2:
            return {"success": False}
        
        if user2["_id"] not in group["members"]:
            return {"success": False}

        user2_authorized = authorize_user_in_gp(user2["_id"], group["owner"], group["admins"])

        if not user2_authorized:
            db.group.update_one({"_id": ObjectId(group["_id"])}, {"$push": {"admins": ObjectId(user2["_id"])}})
        elif user2_authorized == 2:
            db.group.update_one({"_id": ObjectId(group["_id"])}, {"$pull": {"admins": ObjectId(user2["_id"])}})

    else:
        return {"success": False}


@socketio.on("file")
def handle_file(): # data frame will come as a parameter
    pass

@socketio.on("msg")
def handle_msg(message, receiver):
    user = get_user_from_cookie(session)
    if user["username"] == receiver:
        return {"success": False}

    message_id, message_text = create_message(message, ObjectId(user["_id"]))

    receiver_user = fetch_data("user", {"username": receiver})
    if not receiver_user:
        return {"success": False}
    pv = fetch_data("pv", {"members": {"$all": [ObjectId(receiver_user["_id"]), ObjectId(user["_id"])]}}, {"_id": 1})
    db.pv.update_one({"_id": ObjectId(pv["_id"])}, {"$push": {"messages": ObjectId(message_id)}})
    add_message(receiver_user, pv["_id"], ["pvs", "pv"])
    room = [receiver_user["sid"], user["sid"]]

    if room:
        emit("msg", {"message": {"_id": str(message_id), "text": message_text}, "sender": user["username"], "avatar": user["avatar"],
             "gp_info": {"is_gp": False, "gp_name": ""}}, to=room)
    
@socketio.on("delete_msg")
def handle_delete_msg(message, receiver):
    user = get_user_from_cookie(session)

    receiver_user = fetch_data("user", {"username": receiver}, {"_id": 1, "sid": 1, "pvs": 1, "username": 1})
    if not receiver_user:
        return {"success": False}

    pvq = {"members": {"$all": [ObjectId(receiver_user["_id"]), ObjectId(user["_id"])]}}

    msg = fetch_data("message", {"_id": ObjectId(message), "from": ObjectId(user["_id"])})

    if msg:
            msg_id = msg["_id"]
            data = {"message_id": str(msg_id), "delete_all": False, "username": receiver_user["username"]}
            db.pv.update_one(pvq, {"$pull": {"messages": ObjectId(msg["_id"])}})
            db.message.delete_one({"_id": ObjectId(msg["_id"])})
            pv = fetch_data("pv", pvq)
            if not pv["messages"]:
                delete_pv_group_from_user(user["pvs"], user["_id"], pv["_id"], ["pvs", "pv"])
                delete_pv_group_from_user(receiver_user["pvs"], receiver_user["_id"], pv["_id"], ["pvs", "pv"])
                db.pv.delete_one(pvq)
                data["delete_all"] = True
            emit("delete_msg", data, to=user["sid"])
            data["username"] = user["username"]
            emit("delete_msg", data, to=receiver_user["sid"])

@socketio.on("edit_msg")
def handle_edit_msg(msg_id, msg_text, receiver):
    user = get_user_from_cookie(session)

    receiver_user = fetch_data("user", {"username": receiver}, {"_id": 1, "sid": 1, "username": 1})
    if not receiver_user:
        return {"success": False}

    msg = db.message.find_one({"_id": ObjectId(msg_id)})
    if msg:
        db.message.update_one({"_id": ObjectId(msg_id)}, {"$set": {"text": msg_text}})
        data = {"_id": msg_id, "text": msg_text, "username": user["username"]}
        emit("edit_msg", data, to=receiver_user["sid"])
        data["username"] = receiver_user["username"]
        emit("edit_msg", data, to=user["sid"])

@socketio.on("last_msg")
def handle_last_msg(username):
    user = get_user_from_cookie(session)

    receiver = fetch_data("user", {"username": username})
    if not receiver:
        return {"success": False}
    
    pv = db.pv.find_one({"members": {"$all": [ObjectId(user["_id"]), ObjectId(receiver["_id"])]}}, {"_id": 0, "messages": {"$slice": -1}})
    msg = fetch_data("message", {"_id": ObjectId(pv["messages"][0])})

    return {"message": msg["text"]}

@socketio.on("me")
def handle_me():
    user = get_user_from_cookie(session)

    return {"name": user["username"]}

@socketio.on("ai")
def handle_ai():
    user = get_user_from_cookie(session)
    ai = get_ai_user()

    initial_index = 4

    message_ids  = []
    message_texts = []

    for i in range(initial_index):
        a, b = create_message(ai_messages[i], ObjectId(ai["_id"]))
        message_ids.append(a)
        message_texts.append(b)

    pv = db.pv.find_one({"members": {"$all": [ObjectId(ai["_id"]), ObjectId(user["_id"])]}}, {"_id": 1})
    if pv:
        for i, _ in enumerate(message_ids):
            db.pv.update_one({"_id": ObjectId(pv["_id"])}, {"$push": {"messages": ObjectId(message_ids[i])}})
            add_message(ai, pv["_id"], ["pvs", "pv"])
        for i, _ in enumerate(message_ids):
            emit("msg", {"message": {"_id": str(message_ids[i]), "text": message_texts[i]}, "sender": ai["username"], "avatar": ai["avatar"], "gp_info": {
            "is_gp": False, "gp_name": ""}}, to=user["sid"])
        return {"success": True, "avatar": ai["avatar"], "message": {"_id": str(message_ids[0]), "text": message_texts[0]}, "receiver": user}

    pv = {
        "members": [ObjectId(user["_id"]), ObjectId(ai["_id"])],
        "messages": [message_id for message_id in message_ids],
        "pinned": []
    }
    pv_id = db.pv.insert_one(pv).inserted_id

    db.user.update_one({"_id": ObjectId(user["_id"])}, {"$push": {"pvs": {"pv": ObjectId(pv_id), "new_messages": 1}}})
    db.user.update_one({"_id": ObjectId(ai["_id"])}, {"$push": {"pvs": {"pv": ObjectId(pv_id), "new_messages": 1}}})

    for i, _ in enumerate(message_ids):
        emit("msg", {"message": {"_id": str(message_ids[i]), "text": message_texts[i]}, "sender": ai["username"], "avatar": ai["avatar"], "gp_info": {
        "is_gp": False, "gp_name": ""}}, to=user["sid"])

@socketio.on("ai_q")
def handle_ai_q(q_index):
    user = get_user_from_cookie(session)
    ai = get_ai_user()

    if q_index < len(ai_messages):
        message_id, message_text = create_message(ai_messages[q_index], ObjectId(ai["_id"]))

        pv = db.pv.find_one({"members": {"$all": [ObjectId(ai["_id"]), ObjectId(user["_id"])]}}, {"_id": 1})
        sleep(1)
        db.pv.update_one({"_id": ObjectId(pv["_id"])}, {"$push": {"messages": ObjectId(message_id)}})
        add_message(ai, pv["_id"], ["pvs", "pv"])
        emit("msg", {"message": {"_id": str(message_id), "text": message_text}, "sender": ai["username"], "avatar": ai["avatar"], "gp_info": {
            "is_gp": False, "gp_name": ""}}, to=user["sid"])
    elif q_index == len(ai_messages):
        sleep(0.25)
        ret = req_ai(make_msg(str(user["_id"])), str(user["_id"]))
        message_id, message_text = create_message(ret, ObjectId(ai["_id"]))
        emit("msg", {"message": {"_id": str(message_id), "text": message_text}, "sender": ai["username"],"avatar": ai["avatar"], "gp_info": {
            "is_gp": False, "gp_name": ""}}, to=user["sid"])

@socketio.on("ai_a")
def handle_ai_a(msg):
    user = get_user_from_cookie(session)

    if str(user["_id"]) not in ai_answers.keys():
        ai_answers[str(user['_id'])] = [msg]
    else:
        ai_answers[str(user['_id'])].append(msg)
