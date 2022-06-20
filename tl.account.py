#!/usr/bin/env python3

import os
import sys
import time
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import errors
import utility as utl

for index, arg in enumerate(sys.argv):
    if index == 1:
        from_id = arg
    elif index == 2:
        status = arg
    elif index == 3:
        mbot_id = int(arg)
if len(sys.argv) != 4:
    print("Invalid parameters!")
    exit()

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())
conn = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cs = conn.cursor()

cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={mbot_id}")
row_mbots = cs.fetchone()
try:
    path = f"{directory}/sessions/{row_mbots['phone']}"
    if status != 'code':
        client = TelegramClient(session=path,api_id=row_mbots['api_id'],api_hash=row_mbots['api_hash'])
        client.connect()
        if client.is_user_authorized():
            me = client.get_me()
            cs.execute(f"UPDATE {utl.mbots} SET user_id='{me.id}',status='submitted' WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
            utl.bot.send_message(chat_id=from_id,text=f"اکانت فعال است. ✅")
            exit()
        else:
            client.disconnect()
            if status == 'first_level':
                try:
                    os.remove(f"{directory}/sessions/{row_mbots['phone']}.session")
                except:
                    pass
            elif status == 'check':
                cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
                utl.bot.send_message(
                    chat_id=from_id,
                    text="❌ اکانت از دسترس خارج شده\n\n"+
                        "❗️ در صورت لزوم می توانید اکانت را حذف و دوباره لاگین کنید"
                )
                exit()
    client = TelegramClient(session=path,api_id=row_mbots['api_id'],api_hash=row_mbots['api_hash'])
    client.connect()
    if status == 'first_level':
        me = client.send_code_request(phone=row_mbots['phone'])
        cs.execute(f"UPDATE {utl.mbots} SET phone_code_hash='{me.phone_code_hash}',code=null,password=null WHERE id={row_mbots['id']}")
        cs.execute(f"UPDATE {utl.users} SET step='add_acc;code;{row_mbots['id']}' WHERE user_id='{from_id}'")
        utl.bot.send_message(
            chat_id=from_id,
            text="پنل ادمین » افزودن اکانت » ارسال کد و پسورد:\n\n"+
                "❕ اگر پسورد نداشت فقط کد را ارسال کنید مثال:\n"+
                "12345\n\n"+
                "❕ اگر اکانت پسورد دارد هر کدام در یک خط مثال:\n"+
                "code\n"+
                "password"
        )
    elif status == 'code':
        is_ok = True
        try:
            me = client.sign_in(phone=row_mbots['phone'],phone_code_hash=row_mbots['phone_code_hash'],code=row_mbots['code'])
        except errors.PhoneCodeInvalidError as e:
            utl.bot.send_message(chat_id=from_id,text="❌ کد اشتباه است!")
            is_ok = False
        except errors.SessionPasswordNeededError as e:
            if row_mbots['password'] is None:
                utl.bot.send_message(
                    chat_id=from_id,
                    text="❌ اکانت دارای پسورد می باشد!\n\n" +
                        "code\n" +
                        "password\n\n" +
                        "❕ همانند نمونه هر کدام را در یک خط ارسال کنید:",
                )
                is_ok = False
            else:
                me = client.sign_in(password=row_mbots['password'])
        if is_ok:
            cs.execute(f"UPDATE {utl.mbots} SET user_id='{me.id}',status='submitted' WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
            utl.bot.send_message(chat_id=from_id,text="✅ با موفقیت ثبت شد")
except errors.PhoneCodeExpiredError as e:
    utl.bot.send_message(chat_id=from_id,text="❌ کد منقضی شده!")
except errors.PhoneNumberInvalidError as e:
    utl.bot.send_message(chat_id=from_id,text="❌ شماره اشتباه است!")
except errors.FloodWaitError as e:
    utl.bot.send_message(chat_id=from_id,text=f"❌ اکانت به مدت {utl.convert_time(e.seconds, 2)} بلاک شده است!")
except Exception as e:
    error = str(e)
    if "database is locked" in error:
        utl.bot.send_message(chat_id=from_id,text="❌ پروسس ها را کیل و ربات را دوباره ران کنید!")
    elif "You have tried logging in too many times" in error:
        utl.bot.send_message(chat_id=from_id,text="❌ شماره به دلیل تلاش بیش از حد بلاک شده، 24 ساعت بعد دوباره تلاش کنید!")
    elif "The password (and thus its hash value) you entered is invalid" in error:
        utl.bot.send_message(chat_id=from_id,text="❌ پسورد وارد شده اشتباه است!")
    elif "The used phone number has been banned" in error:
        utl.bot.send_message(chat_id=from_id,text="❌ شماره مسدود شده است!")
    else:
        print(f"Error2: {error}")
        utl.bot.send_message(chat_id=from_id,text=f"❌ مشکلی پیش آمده، دوباره تلاش کنید!\n\n{error}")
finally:
    client.disconnect()
    
