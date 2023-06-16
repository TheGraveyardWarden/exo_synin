from flask import Blueprint, request, render_template, session, jsonify, make_response
from website.db import db
from bson.objectid import ObjectId
from .utils import token_required, get_user_from_cookie
from website.settings import SECRET_KEY



views = Blueprint("views", __name__)

@views.route("/")
@token_required
def index():
    user = get_user_from_cookie(session)

    user_info = {
        "username": user["username"],
        "avatar": user["avatar"],
        "bio": user["bio"]
    }

    usernames = []
    last_msgs = []
    avatars = []
    new_messages = []

    for i in user["pvs"]:
        new_messages.append(i["new_messages"])
        pv = db.pv.find_one({"_id": ObjectId(i["pv"])}, {"_id": 0, "members": 1, "messages": {"$slice": -1}})
        last_msgs.append(db.message.find_one({"_id": ObjectId(pv["messages"][0])}, {"_id": 0, "text": 1})["text"])
        for member in pv["members"]:
            if ObjectId(member) != ObjectId(user["_id"]):
                u = db.user.find_one({"_id": ObjectId(member)}, {"_id": 0, "avatar": 1, "username": 1})
                usernames.append(u["username"])
                avatars.append(u["avatar"])
    pv_info = zip(usernames, last_msgs, avatars, new_messages)

    gp_names = []
    gp_last_msgs = []
    gp_avatars = []
    gp_new_messages = []

    for i in user["groups"]:
        gp_new_messages.append(i["new_messages"])
        group = db.group.find_one({"_id": ObjectId(i["group"])}, {"_id": 0, "messages": {"$slice": -1}, "avatar": 1, "name": 1})
        gp_names.append(group["name"])
        gp_avatars.append(group["avatar"])
        gp_last_msgs.append(db.message.find_one({"_id": ObjectId(group["messages"][0])}, {"_id": 0, "text": 1})["text"])
    
    gp_info = zip(gp_names, gp_last_msgs, gp_avatars, gp_new_messages)

    return render_template("index.html", user_info=user_info, pv_info=pv_info, gp_info=gp_info)

@views.route("/pv-chat/<username>")
@token_required
def pv_chat(username):
    user = get_user_from_cookie(session)
    user2 = db.user.find_one({"username": username}, {"_id": 1})

    limit = 15
    offset = int(request.args["offset"])

    pv = db.pv.find_one({"members": {"$all": [ObjectId(user2["_id"]), ObjectId(user["_id"])]}}, {"_id": 1, "messages": 1})
    messages = pv["messages"][::-1][offset:offset+limit]

    messages = [db.message.find_one({"_id": ObjectId(msg)}) for msg in messages]

    for msg in messages:
        user = db.user.find_one({"_id": ObjectId(msg["from"])}, {"_id": 0, "username": 1, "avatar": 1})
        msg["_id"] = str(msg["_id"])
        msg["from"] = user["username"]
        msg["avatar"] = user["avatar"]

    return make_response(jsonify(messages[::-1]))

@views.route("/gp-chat/<name>")
@token_required
def group_chat(name):
    group = db.group.find_one({"name": name}, {"_id": 1, "messages": 1})
    if not group:
        return make_response(jsonify({"success": False, "message": f"group with name {name} doesn\'t exists"}))
    
    limit = 15
    offset = int(request.args["offset"])

    messages = group["messages"][::-1][offset:offset+limit]
    messages = [db.message.find_one({"_id": ObjectId(msg)}) for msg in messages]

    for msg in messages:
        user = db.user.find_one({"_id": ObjectId(msg["from"])}, {"_id": 0, "username": 1, "avatar": 1})
        msg["_id"] = str(msg["_id"])
        msg["from"] = user["username"]
        msg["avatar"] = user["avatar"]

    return make_response(jsonify(messages[::-1]))

@views.route("/user-info/<username>")
@token_required
def user_info(username):
    user = db.user.find_one({"username": username}, {"_id": 0, "bio": 1, "avatar": 1})

    return make_response(jsonify(user))

@views.route("gp-info/<name>")
def group_info(name):
    group = db.group.find_one({"name": name}, {"_id": 0, "avatar": 1, "name": 1, "description": 1, "members": 1})
    if not group:
        return make_response(jsonify({"success": False, "message": f"group with name {name} doesn\'t exists"}))
    
    for i, _ in enumerate(group["members"]):
        group["members"][i] = str(group["members"][i])
    
    return make_response(jsonify(group))
    

