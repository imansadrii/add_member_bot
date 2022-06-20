#!/usr/bin/env python3

import os
import sys
import time
import datetime
import re
import pymysql.cursors
from telethon.sync import TelegramClient
from telethon import functions, errors
import utility as utl

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())

for index, arg in enumerate(sys.argv):
    if index == 1:
        phone = arg
if len(sys.argv) != 2:
    print("Invalid parameters!")
    exit()


def add_to_group(cs, row_gtg, row_mbots, row_admin, result):
    try:
        count_join = i = count_limit = 0
        timestamp = int(time.time())
        client = TelegramClient(session=f"{directory}/sessions/{row_mbots['phone']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
        client.connect()
        if not client.is_user_authorized():
            cs.execute(f"UPDATE {utl.mbots} SET status='first_level' WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.gtg} SET count_accout=count_accout+1 WHERE id={row_gtg['id']}")
        else:
            try:
                for r in client(functions.messages.StartBotRequest(bot="@spambot",peer="@spambot",start_param="start")).updates:
                    for r1 in client(functions.messages.GetMessagesRequest(id=[r.id + 1])).messages:
                        if "I’m afraid some Telegram users found your messages annoying and forwarded them to our team of moderators for inspection." in r1.message:
                            regex = re.findall('automatically released on [\d\w ,:]*UTC', r1.message)[0]
                            regex = regex.replace("automatically released on ","")
                            regex = regex.replace(" UTC","")
                            restrict = datetime.datetime.strptime(regex, "%d %b %Y, %H:%M").timestamp()
                            cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{restrict}' WHERE id={row_mbots['id']}")
                            cs.execute(f"UPDATE {utl.gtg} SET count_report=count_report+1 WHERE id={row_gtg['id']}")
                            print(f"{row_mbots['phone']}: Reported in first step")
                            return
                    break
            except:
                pass
            try:
                if "/joinchat/" in row_gtg['destination']:
                    client(functions.messages.ImportChatInviteRequest(row_gtg['destination'].split("/joinchat/")[1]))
                else:
                    client(functions.channels.JoinChannelRequest(channel=row_gtg['destination']))
            except errors.FloodWaitError as e:
                print(f"{row_mbots['phone']}: {e}")
                end_restrict = int(time.time()) + int(e.seconds)
                cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                cs.execute(f"UPDATE {utl.gtg} SET count_restrict=count_restrict+1 WHERE id={row_gtg['id']}")
                return
            except errors.ChatWriteForbiddenError as e:
                print(f"{row_mbots['phone']}: {e}")
                cs.execute(f"UPDATE {utl.gtg} SET count_permission=count_permission+1 WHERE id={row_gtg['id']}")
                return
            except errors.UserBannedInChannelError as e:
                print(f"{row_mbots['phone']}: {e}")
                cs.execute(f"UPDATE {utl.gtg} SET count_accban=count_accban+1 WHERE id={row_gtg['id']}")
                return
            except Exception as e:
                print(f"{row_mbots['phone']}: {e}")
                return
            for row in result:
                try:
                    i += 1
                    user = row['username']
                    client(functions.channels.GetParticipantRequest(channel=row_gtg['destination'],participant=user))
                    cs.execute(f"UPDATE {utl.gtg} SET last_member_check=last_member_check+1,count_repeat=count_repeat+1 WHERE id={row_gtg['id']}")
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{user}'")
                    utl.insert(cs, f"INSERT INTO {utl.moveds} (gtg_id,bot_id,username,origin_id,destination_id,status,created_at) VALUES ('{row_gtg['id']}','{row_mbots['id']}','{user}','{row_gtg['origin_id']}','{row_gtg['destination_id']}','already','{timestamp}')")
                    print(f"{row_mbots['phone']} ({user}): Already")
                except errors.UserNotParticipantError as e:
                    try:
                        is_bad = True
                        client(functions.channels.InviteToChannelRequest(channel=row_gtg['destination'],users=[user]))
                        is_bad = False
                        cs.execute(f"UPDATE {utl.gtg} SET last_member_check=last_member_check+1,count_moved=count_moved+1 WHERE id={row_gtg['id']}")
                        cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{user}'")
                        utl.insert(cs, f"INSERT INTO {utl.moveds} (gtg_id,bot_id,username,origin_id,destination_id,created_at) VALUES ('{row_gtg['id']}','{row_mbots['id']}','{user}','{row_gtg['origin_id']}','{row_gtg['destination_id']}','{timestamp}')")
                        print(f"{row_mbots['phone']} ({user}): Joined")
                        count_join += 1
                        if (row_gtg['count_moved'] + count_join) >= row_gtg['count']:
                            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={row_gtg['id']} AND count_moved>0 AND count_moved>=count")
                            if cs.fetchone() is not None:
                                return
                    except errors.FloodWaitError as e:
                        print(f"{row_mbots['phone']} ({user}): FloodWaitError when Invite")
                        end_restrict = int(time.time()) + int(e.seconds)
                        cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                        cs.execute(f"UPDATE {utl.gtg} SET count_restrict=count_restrict+1 WHERE id={row_gtg['id']}")
                        return
                    except errors.UserPrivacyRestrictedError as e:
                        print(f"{row_mbots['phone']} ({user}): UserPrivacyRestrictedError")
                        cs.execute(f"UPDATE {utl.gtg} SET last_member_check=last_member_check+1,count_privacy=count_privacy+1 WHERE id={row_gtg['id']}")
                    except errors.UserNotMutualContactError as e:
                        print(f"{row_mbots['phone']} ({user}): UserNotMutualContactError")
                        cs.execute(f"UPDATE {utl.gtg} SET last_member_check=last_member_check+1,count_privacy=count_privacy+1 WHERE id={row_gtg['id']}")
                    except errors.UserChannelsTooMuchError as e:
                        print(f"{row_mbots['phone']} ({user}): UserChannelsTooMuchError")
                        cs.execute(f"UPDATE {utl.gtg} SET last_member_check=last_member_check+1,count_toomuch=count_toomuch+1 WHERE id={row_gtg['id']}")
                    except errors.UserKickedError as e:
                        print(f"{row_mbots['phone']} ({user}): UserKickedError")
                        cs.execute(f"UPDATE {utl.gtg} SET last_member_check=last_member_check+1,count_ban=count_ban+1 WHERE id={row_gtg['id']}")
                        cs.execute(f"DELETE FROM {utl.analyze} WHERE username='{user}'")
                        utl.insert(cs, f"INSERT INTO {utl.reports} (gtg_id,bot_id,username,status,created_at) VALUES ('{row_gtg['id']}','{row_mbots['id']}','{user}','error','{timestamp}')")
                        is_bad = False
                    except errors.ChatWriteForbiddenError as e:
                        print(f"{row_mbots['phone']} ({user}): ChatWriteForbiddenError")
                        cs.execute(f"UPDATE {utl.gtg} SET count_permission=count_permission+1 WHERE id={row_gtg['id']}")
                        return
                    except errors.UserBannedInChannelError as e:
                        print(f"{row_mbots['phone']} ({user}): UserBannedInChannelError")
                        cs.execute(f"UPDATE {utl.gtg} SET count_accban=count_accban+1 WHERE id={row_gtg['id']}")
                        return
                    except errors.ChannelPrivateError as e:
                        print(f"{row_mbots['phone']} ({user}): ChannelPrivateError")
                        cs.execute(f"UPDATE {utl.gtg} SET count_accban=count_accban+1 WHERE id={row_gtg['id']}")
                        return
                    except Exception as e:
                        error = str(e)
                        print(f"{row_mbots['phone']} ({user}): Error when Invite: {error}")
                        if error == 'Too many requests (caused by InviteToChannelRequest)':
                            is_bad = False
                            count_limit += 1
                            if count_limit > 3:
                                end_restrict = int(time.time()) + row_admin['time_spam_restrict']
                                cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                                cs.execute(f"UPDATE {utl.gtg} SET count_spam=count_spam+1 WHERE id={row_gtg['id']}")
                                return
                        elif "No user has" in error:
                            utl.insert(cs, f"INSERT INTO {utl.reports} (gtg_id,bot_id,username,status,created_at) VALUES ('{row_gtg['id']}','{row_mbots['id']}','{user}','error','{timestamp}')")
                            is_bad = False
                    if is_bad:
                        cs.execute(f"UPDATE {utl.analyze} SET is_bad=1 WHERE id='{row['id']}'")
                        utl.insert(cs, f"INSERT INTO {utl.reports} (gtg_id,bot_id,username,status,created_at) VALUES ('{row_gtg['id']}','{row_mbots['id']}','{user}','error','{timestamp}')")
                except errors.FloodWaitError as e:
                    print(f"{row_mbots['phone']} ({user}): FloodWaitError when Invite")
                    end_restrict = int(time.time()) + int(e.seconds)
                    cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{end_restrict}' WHERE id={row_mbots['id']}")
                    cs.execute(f"UPDATE {utl.gtg} SET count_restrict=count_restrict+1 WHERE id={row_gtg['id']}")
                    return
                except Exception as e:
                    print(f"{row_mbots['phone']} ({user}): GetParticipantRequest: {e}")
                    utl.insert(cs, f"INSERT INTO {utl.reports} (gtg_id,bot_id,username,status,created_at) VALUES ('{row_gtg['id']}','{row_mbots['id']}','{user}','error','{timestamp}')")
            try:
                for r in client(functions.messages.StartBotRequest(bot="@spambot",peer="@spambot",start_param="start")).updates:
                    for r1 in client(functions.messages.GetMessagesRequest(id=[r.id + 1])).messages:
                        if "I’m afraid some Telegram users found your messages annoying and forwarded them to our team of moderators for inspection." in r1.message:
                            regex = re.findall('automatically released on [\d\w ,:]*UTC', r1.message)[0]
                            regex = regex.replace("automatically released on ","")
                            regex = regex.replace(" UTC","")
                            restrict = datetime.datetime.strptime(regex, "%d %b %Y, %H:%M").timestamp()
                            cs.execute(f"UPDATE {utl.mbots} SET status='restrict',end_restrict='{restrict}' WHERE id={row_mbots['id']}")
                            cs.execute(f"UPDATE {utl.gtg} SET count_report=count_report+1 WHERE id={row_gtg['id']}")
                            print(f"{row_mbots['phone']}: Reported in last step")
                            return
                    break
            except:
                pass
    except Exception as e:
        print(f"{row_mbots['phone']}: {e}")
    finally:
        try:
            client.disconnect()
            cs.execute(f"UPDATE {utl.analyze} SET reserved_by='0' WHERE is_bad=0 AND reserved_by='{row_mbots['phone']}'")
            if count_join > 0:
                print(f"{row_mbots['phone']} RESULT: {count_join}")
        except:
            pass


try:
    timestamp = int(time.time())
    conn = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
    cs = conn.cursor()
    cs.execute(f"SELECT * FROM {utl.admini}")
    row_admin = cs.fetchone()
    cs.execute(f"SELECT * FROM {utl.mbots} WHERE phone='{phone}'")
    row_mbots = cs.fetchone()
    cs.execute(f"SELECT * FROM {utl.gtg} WHERE status='doing'")
    row_gtg = cs.fetchone()
    if row_gtg is not None:
        if row_gtg['count_moved'] > 0 and row_gtg['count_moved'] >= row_gtg['count']:
            cs.execute(f"UPDATE {utl.gtg} SET status='end',updated_at='{timestamp}' WHERE id={row_gtg['id']}")
            cs.execute(f"UPDATE {utl.mbots} SET last_order_at=0 WHERE id={row_mbots['id']}")
        else:
            cs.execute(f"SELECT * FROM {utl.analyze} WHERE is_bad=0 AND reserved_by='{row_mbots['phone']}'")
            result = cs.fetchall()
            if result:
                print(f"Start: {row_mbots['phone']}")
                cs.execute(f"UPDATE {utl.gtg} SET count_acc=count_acc+1,last_bot_check='{row_mbots['phone']}',updated_at='{timestamp}' WHERE id={row_gtg['id']}")
                add_to_group(cs, row_gtg, row_mbots, row_admin, result)
    else:
        cs.execute(f"UPDATE {utl.mbots} SET last_order_at=0 WHERE id={row_mbots['id']}")
except Exception as e:
    print(f"Error in main: " + str(e))

