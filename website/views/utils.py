from website.db import db
import jwt
from website.settings import SECRET_KEY
from flask import url_for, flash, session, redirect
from functools import wraps
from bson.objectid import ObjectId
import os
import secrets
from string import ascii_letters


USER_AVATAR_PATH = os.path.join(os.getcwd() + "/user_avatars")
GROUP_AVATAR_PATH = os.path.join(os.getcwd() + "/group_avatars")
FILE_PATH = os.path.join(os.getcwd() + "/files")
FILENAME_LENGTH = 10
ALLOWED_AVATAR_FORMATS = [".png", ".jpg", ".jpeg"]
ALLOWED_FILE_FORMATS = [".png", ".jpg", ".jpeg"] # some more extensions will be added to this
DEFAULT_AVATAR = "default.jpg"

def save_file(request, loc, allowed_fmts):
    file = request.files.get("file")
    filename = file.filename
    if not filename:
        return 1
    ext = filename[filename.rfind("."):]
    if ext not in allowed_fmts:
        return 2
    filename = create_filename(FILENAME_LENGTH, loc, ext)
    file.save(os.path.join(loc, filename))

    return filename

def get_user_from_cookie(_session):
    token = _session["token"]
    token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return db.user.find_one({"_id": ObjectId(token["user"])})

def create_filename(length, base_loc, ext):
    while True:
        filename = ""
        for _ in range(length):
            filename += secrets.choice(ascii_letters)
        if not os.path.exists(os.path.join(base_loc, filename + ext)):
            break
    
    return filename+ext

def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = session["token"]
            token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return func(*args, **kwargs)
        except:
            return redirect(url_for("auth.login"))
    
    return wrapper

def redirect_if_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = session["token"]
            token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if db.user.find_one({"_id": ObjectId(token["user"])}) == None:
                return func(*args, **kwargs)
            flash("You are already logged in.", "info")
            return redirect(url_for("views.index"))
        except:
            return func(*args, **kwargs)
    
    return wrapper
