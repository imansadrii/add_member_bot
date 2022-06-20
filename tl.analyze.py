#!/usr/bin/env python3

import os
import sys
import time
import json
import jdatetime
import math
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import types, functions, errors
import utility as utl

for index, arg in enumerate(sys.argv):
    if index == 1:
        from_id = arg
    elif index == 2:
        status = arg
    elif index == 3:
        table_id = arg
if len(sys.argv) != 4:
    print("Invalid parameters!")
    exit()

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())
conn = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cs = conn.cursor()

cs.execute(f"SELECT * FROM {utl.admini}")
row_admin = cs.fetchone()

cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' ORDER BY RAND()")
row_mbots = cs.fetchone()
if not row_mbots:
    utl.bot.send_message(chat_id=from_id,text=f"⛔️ هیچ اکانتی برای آنالیز یافت نشد.")
    exit()
try:
    client = TelegramClient(session=f"{directory}/sessions/{row_mbots['phone']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
    client.connect()
    if not client.is_user_authorized():
        cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
        utl.bot.send_message(chat_id=from_id,parse_mode='HTML',text=f"⛔️ اکانت /status_{row_mbots['id']} (<code>{row_mbots['phone']}</code>) از دسترس خارج شد.")
    else:
        if status == 'order_file':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{table_id}'")
            row_gtg = cs.fetchone()
            try:
                participants_count = row_gtg['max_users']
                link = row_gtg['destination']
                try:
                    result = client(functions.channels.GetFullChannelRequest(channel=link))
                except:
                    try:
                        if "/joinchat/" in link:
                            client(functions.messages.ImportChatInviteRequest(link.split("/joinchat/")[1]))
                        else:
                            client(functions.channels.JoinChannelRequest(channel=link))
                    except errors.UserAlreadyParticipantError as e:
                        pass
                    result = client(functions.channels.GetFullChannelRequest(channel=link))
                row_gtg['destination_id'] = int(f"-100{result.full_chat.id}")
                cs.execute(f"UPDATE {utl.gtg} SET destination_id='{row_gtg['destination_id']}' WHERE id='{row_gtg['id']}'")
                
                info_msg = utl.bot.send_message(chat_id=from_id,text="در حال آنالیز ...")
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE status='end' ORDER BY id DESC")
                row_gtg_select = cs.fetchone()
                if row_gtg_select is not None:
                    list_users = ""
                    cs.execute(f"SELECT * FROM {utl.analyze} WHERE gtg_id={row_gtg_select['id']} AND is_bad=0")
                    result_analyze = cs.fetchall()
                    if result_analyze:
                        for row in result_analyze:
                            list_users += f"{row['username']}\n"
                        utl.write_on_file(f"{directory}/files/exo_{row_gtg_select['id']}_r.txt", list_users)

                participants_all_id = []
                participants_all = []
                participants_real = []
                participants_fake = []
                participants_has_phone = []
                participants_online = []
                percent = timestamp_start = i = 0
                if row_admin['type_analyze']:
                    cs.execute(f"SELECT * FROM {utl.analyze} WHERE is_bad=0")
                    result = cs.fetchall()
                    for row in result:
                        try:
                            client(functions.channels.GetParticipantRequest(channel=row_gtg['destination'],participant=row['username']))
                        except errors.UserNotParticipantError as e:
                            try:
                                user = client.get_entity(row['username'])
                                if not user.id in participants_all_id:
                                    participants_all_id.append(user.id)
                                    if user.username:
                                        username = "@"+user.username
                                        if not username in participants_all:
                                            is_real = is_fake = is_phone = is_online = 0
                                            participants_all.append(username)
                                            if isinstance(user.status, types.UserStatusRecently) or isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 259200):
                                                if not username in participants_real:
                                                    participants_real.append(username)
                                                    is_real = 1
                                            elif not username in participants_fake:
                                                participants_fake.append(username)
                                                is_fake = 1
                                            if isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 1800):
                                                if not username in participants_online:
                                                    participants_online.append(username)
                                                    is_online = 1
                                            if user.phone and not user.phone in participants_has_phone:
                                                participants_has_phone.append(user.phone)
                                                is_phone = 1
                                            cs.execute(f"UPDATE {utl.analyze} SET user_id='{user.id}',is_real={is_real},is_fake={is_fake},is_phone={is_phone},is_online={is_online} WHERE username='{username}'")
                            except:
                                pass
                        except:
                            cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{row['username']}'")
                        if (int(time.time()) - timestamp_start) > 4:
                            try:
                                timestamp_start = int(time.time())
                                count = len(participants_all_id)
                                percent = float('{:.2f}'.format(count / participants_count * 100))
                                participants_all_length = len(participants_all)
                                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                                row_gtg = cs.fetchone()
                                if not row_gtg:
                                    exit()
                                elif row_gtg['status_analyze'] == 'end' or percent >= 100:
                                    break
                                utl.bot.edit_message_text(
                                    chat_id=from_id,
                                    text="⏳ Analyzing...\n\n"+
                                        f"🔗 Link: {row_gtg['origin']}\n"+
                                        f"♻️ Progress: {percent}%\n"+
                                        f"👥 Members: [{count:,}/{participants_count:,}]\n"+
                                        "➖➖➖➖➖➖\n"+
                                        f"📅 Now: {jdatetime.datetime.now().strftime('%H:%M:%S')}\n"+
                                        f"📅 Duretion: {utl.convert_time_en((timestamp_start - timestamp), 2)}",
                                    message_id=info_msg.message_id,
                                    disable_web_page_preview=True,
                                    reply_markup={'inline_keyboard': [[{'text': "تا همینجا بسه",'callback_data': f"status_analyze;{row_gtg['id']}"}]]}
                                )
                            except Exception as e:
                                print(e)
                                pass
                        cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                        row_gtg = cs.fetchone()
                        if not row_gtg:
                            utl.bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
                            exit()
                        elif row_gtg['status_analyze'] == 'end' or percent >= 100:
                            break
                        i += 1
                
                print(len(participants_real))
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_bad=0")
                users_all = cs.fetchone()['count_stats']
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_real=1 AND is_bad=0")
                users_real = cs.fetchone()['count_stats']
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_fake=1 AND is_bad=0")
                users_fake = cs.fetchone()['count_stats']
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_phone=1 AND is_bad=0")
                users_has_phone = cs.fetchone()['count_stats']
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_online=1 AND is_bad=0")
                users_online = cs.fetchone()['count_stats']
                
                cs.execute(f"UPDATE {utl.users} SET step='create_order_file;type_users;{row_gtg['id']}' WHERE user_id='{from_id}'")
                utl.bot.send_message(chat_id=from_id,
                    text="نوع کاربران را برای ثبت نهایی سفارش انتخاب کنید:\n\n"+
                        f"🔻 همه کاربران: {users_all:,}\n"+
                        f"🔻 کاربران واقعی: {users_real:,}\n"+
                        f"🔻 کاربران فیک: {users_fake:,}\n"+
                        f"🔻 کاربران داری شماره: {users_has_phone:,}\n"+
                        f"🔻 کاربران آنلاین: {users_online:,}\n"+
                        f"⏰ مدت زمان: {utl.convert_time((int(time.time()) - timestamp), 2)}\n\n"+
                        "❕ کاربران واقعی شامل کاربران آنلاین هم می شوند",
                    reply_markup={'resize_keyboard': True,'keyboard': [
                        [{'text': 'کاربران واقعی'},{'text': 'همه کاربران'}],
                        [{'text': 'کاربران آنلاین'},{'text': 'کاربران فیک'}],
                        [{'text': 'کاربران دارای شماره'}],
                        [{'text': utl.menu_var}]
                    ]}
                )
            except errors.FloodWaitError as e:
                print(f"{row_mbots['phone']}" + str(e))
                end_restrict = int(e.seconds) + int(time.time())
                cs.execute(f"UPDATE {utl.mbots} SET end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                utl.bot.send_message(chat_id=from_id,text=f"❌ اکانت آنالیز {utl.convert_time((int(time.time())-end_restrict), 2)} محدود شد، دوباره تلاش کنید")
            except Exception as e:
                utl.bot.send_message(chat_id=from_id,text=f"❌ Error in {row_mbots['phone']} (/status_{row_mbots['id']})\n\n{e}")
                cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0")
        elif status == 'check':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{table_id}'")
            row_gtg = cs.fetchone()
            try:
                link = row_gtg['origin']
                try:
                    result = client(functions.channels.GetFullChannelRequest(channel=link))
                except:
                    try:
                        if "/joinchat/" in link:
                            client(functions.messages.ImportChatInviteRequest(link.split("/joinchat/")[1]))
                        else:
                            client(functions.channels.JoinChannelRequest(channel=link))
                    except errors.UserAlreadyParticipantError as e:
                        pass
                    result = client(functions.channels.GetFullChannelRequest(channel=link))
                participants_count = result.full_chat.participants_count
                origin_id = int(f"-100{result.full_chat.id}")
                cs.execute(f"UPDATE {utl.gtg} SET origin_id='{origin_id}' WHERE id='{row_gtg['id']}'")
                
                link = row_gtg['destination']
                try:
                    result = client(functions.channels.GetFullChannelRequest(channel=link))
                except:
                    try:
                        if "/joinchat/" in link:
                            client(functions.messages.ImportChatInviteRequest(link.split("/joinchat/")[1]))
                        else:
                            client(functions.channels.JoinChannelRequest(channel=link))
                    except errors.UserAlreadyParticipantError as e:
                        pass
                    result = client(functions.channels.GetFullChannelRequest(channel=link))
                destination_id = int(f"-100{result.full_chat.id}")
                
                cs.execute(f"UPDATE {utl.gtg} SET destination_id='{destination_id}' WHERE id='{row_gtg['id']}'")
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                row_gtg = cs.fetchone()
                
                info_msg = utl.bot.send_message(chat_id=from_id,text="در حال پیکربندی ...")
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE status='end' ORDER BY id DESC")
                row_gtg_select = cs.fetchone()
                if row_gtg_select is not None:
                    list_users = ""
                    cs.execute(f"SELECT * FROM {utl.analyze} WHERE gtg_id={row_gtg_select['id']} AND is_bad=0")
                    result_analyze = cs.fetchall()
                    if result_analyze:
                        for row in result_analyze:
                            list_users += f"{row['username']}\n"
                        utl.write_on_file(f"{directory}/files/exo_{row_gtg_select['id']}_r.txt", list_users)
                cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0")
                utl.bot.edit_message_text(chat_id=from_id,message_id=info_msg.message_id,text="در حال آنالیز ...")
                
                queryKey = ['','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                participants_all_id = []
                participants_all = []
                participants_real = []
                participants_fake = []
                participants_has_phone = []
                participants_online = []
                percent = timestamp_start = i = 0
                for key in queryKey:
                    offset = 0
                    while True:
                        participants = client(functions.channels.GetParticipantsRequest(row_gtg['origin'],types.ChannelParticipantsSearch(key),offset,200,hash=0))
                        if participants.users:
                            if not row_admin['type_analyze']:
                                for user in participants.users:
                                    try:
                                        if not user.id in participants_all_id:
                                            participants_all_id.append(user.id)
                                            if user.username:
                                                username = "@"+user.username
                                                if not username in participants_all:
                                                    is_real = is_fake = is_phone = is_online = 0
                                                    participants_all.append(username)
                                                    if isinstance(user.status, types.UserStatusRecently) or isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 259200):
                                                        if not username in participants_real:
                                                            participants_real.append(username)
                                                            is_real = 1
                                                    elif not username in participants_fake:
                                                        participants_fake.append(username)
                                                        is_fake = 1
                                                    if isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 1800):
                                                        if not username in participants_online:
                                                            participants_online.append(username)
                                                            is_online = 1
                                                    if user.phone and not user.phone in participants_has_phone:
                                                        participants_has_phone.append(user.phone)
                                                        is_phone = 1
                                                    utl.insert(cs, f"INSERT INTO {utl.analyze} (gtg_id,user_id,username,is_real,is_fake,is_phone,is_online,created_at) VALUES ('{row_gtg['id']}','{user.id}','{username}','{is_real}','{is_fake}','{is_phone}','{is_online}','{timestamp}')")
                                    except:
                                        pass
                            else:
                                for user in participants.users:
                                    if not user.id in participants_all_id:
                                        participants_all_id.append(user.id)
                                        if user.username:
                                            username = f"@{user.username}"
                                            if not username in participants_all:
                                                try:
                                                    client(functions.channels.GetParticipantRequest(channel=row_gtg['destination'],participant=user))
                                                except errors.UserNotParticipantError as e:
                                                    try:
                                                        is_real = is_fake = is_phone = is_online = 0
                                                        participants_all.append(username)
                                                        if isinstance(user.status, types.UserStatusRecently) or isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 259200):
                                                            if not username in participants_real:
                                                                participants_real.append(username)
                                                                is_real = 1
                                                        elif not username in participants_fake:
                                                            participants_fake.append(username)
                                                            is_fake = 1
                                                        if isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 1800):
                                                            if not username in participants_online:
                                                                participants_online.append(username)
                                                                is_online = 1
                                                        if user.phone and not user.phone in participants_has_phone:
                                                            participants_has_phone.append(user.phone)
                                                            is_phone = 1
                                                        utl.insert(cs, f"INSERT INTO {utl.analyze} (gtg_id,user_id,username,is_real,is_fake,is_phone,is_online,created_at) VALUES ('{row_gtg['id']}','{user.id}','{username}','{is_real}','{is_fake}','{is_phone}','{is_online}','{timestamp}')")
                                                    except Exception as e:
                                                        print(f"dd: {e}")
                                                        pass
                                                except errors.FloodWaitError as e:
                                                    break
                                                except:
                                                    pass
                            try:
                                offset += len(participants.users)
                                if (int(time.time()) - timestamp_start) > 4:
                                    cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                                    row_gtg = cs.fetchone()
                                    if not row_gtg:
                                        utl.bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
                                        exit()
                                    elif row_gtg['status_analyze'] == 'end':
                                        break
                                    timestamp_start = int(time.time())
                                    count = len(participants_all_id)
                                    percent = float('{:.2f}'.format(count / participants_count * 100))
                                    if percent >= 100:
                                        break
                                    percent_key = math.ceil((i / 26) * 100)
                                    if percent_key > percent:
                                        percent = percent_key
                                    now = jdatetime.datetime.now().strftime('%H:%M:%S')
                                    participants_all_length = len(participants_all)
                                    utl.bot.edit_message_text(
                                        chat_id=from_id,
                                        text="⏳ Analyzing...\n\n"+
                                            f"🔗 Link: {row_gtg['origin']}\n"+
                                            f"♻️ Progress: {percent}%\n"+
                                            f"👥 Members: [{count:,}/{participants_count:,}]\n"+
                                            "➖➖➖➖➖➖\n"+
                                            f"📅 Now: {now}\n"+
                                            f"📅 Duretion: {utl.convert_time_en((timestamp_start - timestamp), 2)}",
                                        message_id=info_msg.message_id,
                                        disable_web_page_preview=True,
                                        reply_markup={'inline_keyboard': [[{'text': "تا همینجا بسه",'callback_data': f"status_analyze;{row_gtg['id']}"}]]}
                                    )
                            except:
                                pass
                        else:
                            break
                    cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                    row_gtg = cs.fetchone()
                    if not row_gtg:
                        utl.bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
                        exit()
                    elif row_gtg['status_analyze'] == 'end':
                        break
                    if percent >= 100:
                        break
                    i += 1
                
                participants = client(functions.channels.GetParticipantsRequest(row_gtg['origin'], types.ChannelParticipantsAdmins(), 0, 200, 0))
                if participants.users:
                    for user in participants.users:
                        try:
                            if user.username:
                                username = f"@{user.username}"
                                cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{username}'")
                        except:
                            pass
                if not row_admin['type_analyze']:
                    cs.execute(f"SELECT id,username FROM {utl.moveds} WHERE origin_id='{row_gtg['origin_id']}' AND destination_id='{row_gtg['destination_id']}'")
                    result_detect_members = cs.fetchall()
                    for row in result_detect_members:
                        try:
                            if (int(time.time()) - timestamp_start) > 5:
                                timestamp_start = int(time.time())
                                utl.bot.edit_message_text(
                                    chat_id=from_id,
                                    text="⏳ Isolation of duplicate members...\n\n"+
                                        f"🔗 Link: {row_gtg['origin']}\n"+
                                        f"♻️ Progress: {percent}%\n"+
                                        "➖➖➖➖➖➖\n"+
                                        f"📅 Now: {now}\n"+
                                        f"📅 Duretion (sec): {(int(time.time()) - timestamp)}",
                                    message_id=info_msg.message_id,
                                    disable_web_page_preview=True,
                                )
                        except:
                            pass
                        cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{row['username']}'")
                
                print(len(participants_real))
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_bad=0")
                users_all = cs.fetchone()['count_stats']
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_real=1 AND is_bad=0")
                users_real = cs.fetchone()['count_stats']
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_fake=1 AND is_bad=0")
                users_fake = cs.fetchone()['count_stats']
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_phone=1 AND is_bad=0")
                users_has_phone = cs.fetchone()['count_stats']
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_online=1 AND is_bad=0")
                users_online = cs.fetchone()['count_stats']
                
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{row_gtg['id']}'")
                row_gtg = cs.fetchone()
                if row_gtg:
                    cs.execute(f"UPDATE {utl.users} SET step='create_order;type_users' WHERE user_id='{from_id}'")
                    utl.bot.send_message(chat_id=from_id,
                        text="نوع کاربران را برای ثبت نهایی سفارش انتخاب کنید:\n\n"+
                            f"🔻 همه کاربران: {users_all:,}\n"+
                            f"🔻 کاربران واقعی: {users_real:,}\n"+
                            f"🔻 کاربران فیک: {users_fake:,}\n"+
                            f"🔻 کاربران داری شماره: {users_has_phone:,}\n"+
                            f"🔻 کاربران آنلاین: {users_online:,}\n"+
                            f"⏰ مدت زمان: {utl.convert_time((int(time.time()) - timestamp), 2)}\n\n"+
                            "❕ کاربران واقعی شامل کاربران آنلاین هم می شوند",
                        reply_markup={'resize_keyboard': True,'keyboard': [
                            [{'text': 'کاربران واقعی'},{'text': 'همه کاربران'}],
                            [{'text': 'کاربران آنلاین'},{'text': 'کاربران فیک'}],
                            [{'text': 'کاربران دارای شماره'}],
                            [{'text': utl.menu_var}]
                        ]}
                    )
            except errors.FloodWaitError as e:
                print(f"{row_mbots['phone']}" + str(e))
                end_restrict = int(e.seconds) + int(time.time())
                cs.execute(f"UPDATE {utl.mbots} SET end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                utl.bot.send_message(chat_id=from_id,text=f"❌ اکانت آنالیز {utl.convert_time((int(time.time())-end_restrict), 2)} محدود شد، دوباره تلاش کنید")
            except Exception as e:
                utl.bot.send_message(chat_id=from_id,text=f"❌ Error in {row_mbots['phone']} (/status_{row_mbots['id']})\n\n{e}")
                cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0")
        elif status == 'analyze':
            cs.execute(f"SELECT * FROM {utl.egroup} WHERE id='{table_id}'")
            row_egroup = cs.fetchone()
            info_msg = utl.bot.send_message(chat_id=from_id,text="در حال آنالیز ...")
            try:
                link = row_egroup['link']
                try:
                    result = client(functions.channels.GetFullChannelRequest(channel=link))
                except:
                    try:
                        if "/joinchat/" in link:
                            client(functions.messages.ImportChatInviteRequest(link.split("/joinchat/")[1]))
                        else:
                            client(functions.channels.JoinChannelRequest(channel=link))
                    except errors.UserAlreadyParticipantError as e:
                        pass
                    result = client(functions.channels.GetFullChannelRequest(channel=link))
                chat_id = int(f"-100{result.full_chat.id}")
                participants_count = result.full_chat.participants_count
                online_count = result.full_chat.online_count

                cs.execute(f"UPDATE {utl.egroup} SET chat_id='{chat_id}' WHERE id='{row_egroup['id']}'")
                queryKey = ['','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                participants_all_id = []
                participants_all_username = []
                participants_real = []
                participants_fake = []
                participants_has_phone = []
                participants_online = []
                participants_bots = []
                percent = timestamp_start = i = 0
                for key in queryKey:
                    offset = 0
                    while True:
                        participants = client(functions.channels.GetParticipantsRequest(link,types.ChannelParticipantsSearch(key),offset,200,hash=0))
                        if participants.users:
                            for user in participants.users:
                                try:
                                    if not user.id in participants_all_id:
                                        participants_all_id.append(user.id)
                                    if user.username:
                                        username = f"@{user.username}"
                                        if user.bot:
                                            participants_bots.append(username)
                                        else:
                                            participants_all_username.append(username)
                                            if isinstance(user.status, types.UserStatusRecently) or isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 259200):
                                                if not username in participants_real:
                                                    participants_real.append(username)
                                            elif not username in participants_fake:
                                                participants_fake.append(username)
                                            if isinstance(user.status, types.UserStatusOnline) or (isinstance(user.status, types.UserStatusOffline) and (timestamp - user.status.was_online.timestamp()) < 1800):
                                                if not username in participants_online:
                                                    participants_online.append(username)
                                            if user.phone and not user.phone in participants_has_phone:
                                                participants_has_phone.append(user.phone)
                                except:
                                    pass
                            try:
                                offset += len(participants.users)
                                if (int(time.time()) - timestamp_start) > 4:
                                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE id='{row_egroup['id']}'")
                                    row_egroup = cs.fetchone()
                                    if row_egroup['status'] == 'end':
                                        break
                                    timestamp_start = int(time.time())
                                    count = len(participants_all_id)
                                    percent = float('{:.2f}'.format(count / participants_count * 100))
                                    if percent >= 100:
                                        break
                                    percent_key = math.ceil((i / 26) * 100)
                                    if percent_key > percent:
                                        percent = percent_key
                                    now = jdatetime.datetime.now().strftime('%H:%M:%S')
                                    utl.bot.edit_message_text(
                                        chat_id=from_id,
                                        text="⏳ Analyzing...\n\n"+
                                            f"🔗 Link: {link}\n"+
                                            f"♻️ Progress: {percent}%\n"+
                                            f"👥 Members: [{count:,}/{participants_count:,}]\n"+
                                            "➖➖➖➖➖➖\n"+
                                            f"📅 Now: {now}\n"+
                                            f"📅 Duretion: {utl.convert_time_en((timestamp_start - timestamp), 2)}",
                                        message_id=info_msg.message_id,
                                        disable_web_page_preview=True,
                                        reply_markup={'inline_keyboard': [[{'text': "تا همینجا بسه",'callback_data': f"analyze;{row_egroup['id']}"}]]}
                                    )
                            except:
                                pass
                        else:
                            break
                    cs.execute(f"SELECT * FROM {utl.egroup} WHERE id='{row_egroup['id']}'")
                    row_egroup = cs.fetchone()
                    if row_egroup['status'] == 'end':
                        break
                    elif percent >= 100:
                        break
                    i += 1
                
                try:
                    os.mkdir(f"export/{row_egroup['id']}")
                except:
                    pass
                users_real = users_fake = users_has_phone = users_online = ""
                for value_ in participants_real:
                    users_real += f"{value_}\n"
                for value_ in participants_fake:
                    users_fake += f"{value_}\n"
                for value_ in participants_has_phone:
                    users_has_phone += f"{value_}\n"
                for value_ in participants_online:
                    users_online += f"{value_}\n"
                
                with open(f"export/{row_egroup['id']}/users_all.txt", 'w') as file:
                    file.write(users_real + users_fake)
                with open(f"export/{row_egroup['id']}/users_real.txt", 'w') as file:
                    file.write(users_real)
                with open(f"export/{row_egroup['id']}/users_fake.txt", 'w') as file:
                    file.write(users_fake)
                with open(f"export/{row_egroup['id']}/users_has_phone.txt", 'w') as file:
                    file.write(users_has_phone)
                with open(f"export/{row_egroup['id']}/users_online.txt", 'w') as file:
                    file.write(users_online)
                users_all_id = len(participants_all_id)
                users_real_count = len(participants_real)
                users_fake_count = len(participants_fake)
                users_has_phone_count = len(participants_has_phone)
                users_online_count = len(participants_online)
                bots_count = len(participants_bots)

                cs.execute(f"UPDATE {utl.egroup} SET status='end',users_real='{users_real_count}',users_fake='{users_fake_count}',users_has_phone='{users_has_phone_count}',users_online='{users_online_count}',participants_count='{participants_count}',participants_online_count='{online_count}',participants_bot_count='{bots_count}' WHERE id='{row_egroup['id']}'")
                utl.bot.send_message(
                    chat_id=from_id,
                    text=f"🔻 شناسه: <code>{chat_id}</code> (/exgroup_{str(chat_id)[1:]})\n"+
                        f"🔻 لینک: {row_egroup['link']}\n"+
                        f"🔻 کل کاربران: {participants_count:,}\n"+
                        f"🔻 کاربران آنلاین: {online_count:,}\n"+
                        f"🔻 ربات ها: {bots_count}\n"+
                        "‏————————————————————\n"+
                        "♻️ کاربران شناسایی شده (دارای یوزرنیم):\n"+
                        f"🔻 همه کاربران: {(users_real_count + users_fake_count):,} (/ex_{row_egroup['id']}_a)\n"+
                        f"🔻 کاربران واقعی: {users_real_count:,} (/ex_{row_egroup['id']}_u)\n"+
                        f"🔻 کاربران فیک: {users_fake_count:,} (/ex_{row_egroup['id']}_f)\n"+
                        f"🔻 کاربران داری شماره: {users_has_phone_count:,} (/ex_{row_egroup['id']}_n)\n"+
                        f"🔻 کاربران آنلاین: {users_online_count:,} (/ex_{row_egroup['id']}_o)\n\n"+
                        "‼️ اگر روی دکمه های داخل پرانتز کلیک کنید خروجی اون کاربر هارو بهت میدم.\n"+
                        f"⏰ مدت زمان: {int(time.time()) - timestamp} ثانیه\n‏",
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                )
            except errors.FloodWaitError as e:
                end_restrict = int(e.seconds) + int(time.time())
                cs.execute(f"UPDATE {utl.mbots} SET end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                utl.bot.send_message(chat_id=from_id,text=f"❌ اکانت آنالیز {utl.convert_time((int(time.time())-end_restrict), 2)} محدود شد، دوباره تلاش کنید")
            except Exception as e:
                utl.bot.send_message(chat_id=from_id,text=f"❌ Error in {row_mbots['phone']} (/status_{row_mbots['id']})\n\n{e}")
except Exception as e:
    utl.bot.send_message(chat_id=from_id,text=f"❌ Error in {row_mbots['phone']} (/status_{row_mbots['id']})\n\n{e}")
finally:
    try:
        client.disconnect()
        utl.bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
    except:
        pass


