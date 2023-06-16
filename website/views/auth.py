from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from website.db import db
from datetime import datetime as dt, timedelta
from bson.objectid import ObjectId
from flask_bcrypt import generate_password_hash, check_password_hash
from .utils import token_required, redirect_if_logged_in, DEFAULT_AVATAR
import jwt
from website.settings import SECRET_KEY


auth = Blueprint("auth", __name__)


@auth.route("/sign-up", methods=["GET", "POST"])
@redirect_if_logged_in
def signup():        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if username == None or username == "":
            flash("Username not provided.", "danger")
            return redirect(url_for("auth.signup"))
        
        if password == None or len(password) < 8:
            flash("Password must be greater than 7 characters.", "danger")
            return redirect(url_for("auth.signup"))

        if confirm_password != password:
            flash("Password doesn\'t match.", "danger")
            return redirect(url_for("auth.signup"))

        if db.user.find_one({"username": username}) != None:
            flash("This username is already taken!", "info")
            return redirect(url_for("auth.signup"))

        user = {
            "username": username,
            "password": generate_password_hash(password),
            "created_at": dt.now(),
            "avatar": DEFAULT_AVATAR,
            "bio": "",
            "groups": [],
            "is_online": True,
            "last_online": dt.now(),
            "sid": "",
            "pvs": []
        }

        try:
            inserted_id = db.user.insert_one(user).inserted_id
            flash(f"New account has been successfully created for {username}.", "success")
            token = jwt.encode({"user": str(inserted_id), "exp": dt.utcnow()+timedelta(days=7)}, SECRET_KEY, algorithm="HS256")
            session["token"] = token
            return redirect(url_for("views.index"))
        except Exception as e:
            print(str(e))
            flash(f"Couldn\'t create account.", "danger")
            return redirect(url_for("auth.signup"))

    return render_template("signup.html")


@auth.route("/login", methods=["POST", "GET"])
@redirect_if_logged_in
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == None or username == "":
            flash("Username not provided.", "danger")
            return redirect(url_for("auth.login"))
        
        if password == None or password == "":
            flash("password not provided.", "danger")
            return redirect(url_for("auth.login"))
        
        user = db.user.find_one({"username": username})

        if user == None:
            flash("Username doesn\'t exist.", "danger")
            return redirect(url_for("auth.login"))
        
        if not check_password_hash(user["password"], password):
            flash("Password is incorrect!", "danger")
            return redirect(url_for("auth.login"))
        
        flash(f"You have successfully logged in.", "success")
        token = jwt.encode({"user": str(user["_id"]), "exp": dt.utcnow()+timedelta(days=7)}, SECRET_KEY, algorithm="HS256")
        session["token"] = token
        return redirect(url_for("views.index"))

    return render_template("login.html")


@auth.route("/logout")
@token_required
def logout():
    del session["token"]
    flash("You logged out!", "info")
    return redirect(url_for("auth.login"))
