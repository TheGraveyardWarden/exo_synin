from flask import Blueprint, jsonify, request, send_file, flash, redirect, url_for
import os
from .utils import USER_AVATAR_PATH, GROUP_AVATAR_PATH, FILE_PATH, ALLOWED_FILE_FORMATS, save_file, token_required


files = Blueprint("files", __name__)

@files.route("/get-user-avatar/<filename>")
def get_user_avatar(filename):
    if os.path.exists(os.path.join(USER_AVATAR_PATH, filename)):
        return send_file(open(os.path.join(USER_AVATAR_PATH, filename), "rb"), download_name=filename)
    else:
        return jsonify({"message": "file not found"})

@files.route("/get-group-avatar/<filename>")
def get_group_avatar(filename):
    if os.path.exists(os.path.join(GROUP_AVATAR_PATH, filename)):
        return send_file(open(os.path.join(GROUP_AVATAR_PATH, filename), "rb"), download_name=filename)
    else:
        return jsonify({"message": "file not found"})
