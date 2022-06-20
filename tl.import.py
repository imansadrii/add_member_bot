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
if len(sys.argv) != 2:
    print("Invalid parameters!")
    exit()

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())
conn = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cs = conn.cursor()

cs.execute(f"SELECT * FROM {utl.admini}")
row_admin = cs.fetchone()

list_files = os.listdir(f"{directory}/import")
count_all = len(list_files)
count_import = count_failed_import = 0
info_msg = utl.bot.send_message(
    chat_id=from_id,
    text="در حال انجام عملیات ..."
)
for file in list_files:
    timestamp = int(time.time())
    row_apis = utl.select_api(cs,row_admin['api_per_number'])
    if row_apis is None:
        utl.bot.send_message(chat_id=from_id,text="❌ هیچ Api ای یافت نشد")
        break
    else:
        try:
            client = TelegramClient(session=f"{directory}/import/{file}",api_id=row_apis['api_id'],api_hash=row_apis['api_hash'])
            client.connect()
            if client.is_user_authorized():
                me = client.get_me()
                phone = me.phone
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE phone='{phone}'")
                row_mbots = cs.fetchone()
                if row_mbots is None:
                    os.rename(f"{directory}/import/{file}", f"{directory}/sessions/{phone}.session")
                    uniq_id = utl.uniq_id_generate(cs,10,utl.mbots)
                    cs.execute(f"INSERT INTO {utl.mbots} (creator_user_id,phone,user_id,status,api_id,api_hash,created_at,uniq_id) VALUES ('{from_id}','{phone}','{me.id}','submitted','{row_apis['api_id']}','{row_apis['api_hash']}','{timestamp}','{uniq_id}')")
                    count_import += 1

            else:
                count_failed_import += 1
                print(f"not auth: {file}")
            try:
                utl.bot.edit_message_text(
                    chat_id=from_id,
                    text="در حال انجام عملیات ...\n\n"
                        f"checking => [{(count_import + count_failed_import):,} / {count_all:,}]\n" +
                        f"success => {count_import:,}",
                    message_id=info_msg.message_id
                )
            except:
                pass
        except Exception as e:
            error = str(e)
            print(f"Error2: {error}")
            if "database is locked" in error:
                utl.bot.send_message(chat_id=from_id,text="❌ پروسس ها را کیل و ربات را دوباره ران کنید!")
            elif "You have tried logging in too many times" in error:
                utl.bot.send_message(chat_id=from_id,text="❌ شماره به دلیل تلاش بیش از حد بلاک شده، 24 ساعت بعد دوباره تلاش کنید!")
            else:
                utl.bot.send_message(chat_id=from_id,text="❌ مشکلی پیش آمده، دوباره تلاش کنید!")
        finally:
            try:
                client.disconnect()
            except:
                pass
utl.bot.send_message(chat_id=from_id,text=f"تعداد {count_import} اکانت افزوده شد")
