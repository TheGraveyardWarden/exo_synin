from .settings import OPENAI_API_KEY
import openai
from .db import db
from bson.objectid import ObjectId

openai.api_key = OPENAI_API_KEY

AI_USER_ID = "648c171b06384c7c0a6093eb"

ai_answers = {}
ai_messages = []

ai_messages.append("سلام")
ai_messages.append("به اگزوباکس خوش اومدید")
ai_messages.append("با پاسخ به چند سوال بهترین کادو رو واسه شخصی که میخواید سفارش بدید")
ai_messages.append("نام فرد مورد نظر")              # 0
ai_messages.append("جنسیت")                          # 1
ai_messages.append("سن")                             # 2
ai_messages.append("رابطه شما با فرد مورد نظر")     # 3
ai_messages.append("شغل")                            # 4
ai_messages.append("مناسبت")                         # 5
ai_messages.append("علاقه مندی ها")                  # 6


def get_ai_user():
    return db.user.find_one({"_id": ObjectId(AI_USER_ID)})

def make_msg(user_id):
    return f"""
        من ی کادو میخوام واسه {ai_answers[user_id][3]} ام
        اسمش {ai_answers[user_id][0]} هست
        جنسیت {ai_answers[user_id][1]}
        سن {ai_answers[user_id][2]}
        شغل {ai_answers[user_id][4]}
        به مناسبت {ai_answers[user_id][5]}
        علاقه مندی هاش {ai_answers[user_id][6]}
        چی بخرم واسش
    """

def req_ai(msg, user_id):
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": msg}])
    del ai_answers[user_id]
    return chat_completion.choices[0].message.content
