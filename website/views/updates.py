from flask import Blueprint, request, session, flash, redirect, url_for
from .utils import save_file, USER_AVATAR_PATH, token_required, ALLOWED_AVATAR_FORMATS, get_user_from_cookie
from website.db import db
from flask_bcrypt import generate_password_hash
import os



update = Blueprint("update", __name__)


@update.route("/user", methods=["POST"])
@token_required
def update_user():
    filename = save_file(request, USER_AVATAR_PATH, ALLOWED_AVATAR_FORMATS)
    if filename == 2:
        flash("File not allowed!", "danger")
        return redirect(url_for("views.index"))

    username = request.form.get("username")
    password = request.form.get("password")
    bio = request.form.get("bio")

    user = get_user_from_cookie(session)
    current_avatar = user["avatar"]

    if filename == 1:
        filename = current_avatar
    elif current_avatar == "default.jpg":
        pass
    else:
        p = os.path.join(USER_AVATAR_PATH, current_avatar)
        if os.path.exists(p):
            os.remove(p)

    if username == user["username"]:
        pass
    elif db.user.find_one({"username": username}) != None:
        flash("This username is already taken", "info")
        return redirect(url_for("views.index"))
    
    db.user.update_one({"_id": user["_id"]},
                        {"$set":
                            {
                                "username": username if username else user["username"],
                                "password": generate_password_hash(password) if password else user["password"],
                                "avatar": filename,
                                "bio": bio,
                            }
                        })

    flash("User Updated Successfully!", "success")
    return redirect(url_for("views.index"))

