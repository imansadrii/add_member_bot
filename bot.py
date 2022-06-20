#!/usr/bin/env python3
# pylint: disable=C0116,W0613

import os
import re
import time
import psutil
import requests
import jdatetime
import pymysql.cursors
from telegram import Update, ReplyKeyboardMarkup,  KeyboardButton
from telegram.ext import Updater, MessageHandler,CallbackQueryHandler, Filters, CallbackContext
from telegram.error import RetryAfter, TimedOut
import utility as utl


directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))
try:
    pid = int(utl.read_file(f"{directory}/pid/{filename}.txt"))
    if psutil.pid_exists(pid):
        pid = psutil.Process(pid)
        pid.terminate()
except:
    pass
utl.write_on_file(f"{directory}/pid/{filename}.txt", str(os.getpid()))
print(f"run: {filename}")


step_page = 10


def user_panel(update,text=None):
    if not text:
        text = "ناحیه کاربری:"
    update.message.reply_html(text=text,
        reply_markup={'resize_keyboard': True,'keyboard': [
            [{'text': '📋 سفارشات'},{'text': '➕ ایجاد سفارش'}],
            [{'text': '📋 اکانت ها'},{'text': '➕ افزودن اکانت'}],
            [{'text': '📋 لیست api ها'},{'text': '➕ افزودن api'}],
            [{'text': '🔮 آنالیز گروه 🔮'},{'text': '⚙️ تنظیمات ⚙️'}],
            [{'text': '📚 راهنما 📚'},{'text': '📊 آمار 📊'}],
        ]}
    )


class Pagination:
    
    def __init__(self,update,type_btn,output,step_page,num_all_pages):
        self.update = update
        self.type_btn = type_btn
        self.text = output
        self.step_page = step_page
        self.num_all_pages = num_all_pages

    def setStepPage(self,step_page):
        self.step_page = step_page
    
    def setText(self,text):
        self.text = text
    
    def setNumAllPages(self,num_all_pages):
        self.num_all_pages = num_all_pages
    
    def processMessage(self):
        chat_id = self.update.message.chat.id
        if self.num_all_pages > self.step_page:
            self.update.message.reply_html(disable_web_page_preview=True,text=self.text,
                reply_markup={'inline_keyboard': [[{'text': f"صفحه 2", 'callback_data': f"pg;{self.type_btn};2"}]]}
            )
        else:
            self.update.message.reply_html(disable_web_page_preview=True,text=self.text)
        return
    
    def processCallback(self):
        query = self.update.callback_query
        ex_data = query.data.split(";")
        num_current_page = int(ex_data[2])
        num_prev_page = num_current_page - 1
        num_next_page = num_current_page + 1
        if num_current_page == 1:
            query.edit_message_text(parse_mode='HTML',disable_web_page_preview=True,text=self.text,
                reply_markup={'inline_keyboard': [[{'text': f"<< صفحه {num_next_page}", 'callback_data': f"pg;{self.type_btn};{num_next_page}"}]]}
            )
        elif self.num_all_pages > (num_current_page * self.step_page):
            query.edit_message_text(parse_mode='HTML',disable_web_page_preview=True,text=self.text,
                reply_markup={'inline_keyboard': [
                    [{'text': f"صفحه {num_prev_page} >>", 'callback_data': f"pg;{self.type_btn};{num_prev_page}"},
                    {'text': f"<< صفحه {num_next_page}", 'callback_data': f"pg;{self.type_btn};{num_next_page}"}]
                ]}
            )
        else:
            query.edit_message_text(parse_mode='HTML',disable_web_page_preview=True,text=self.text,
                reply_markup={'inline_keyboard': [[{'text': f"صفحه {num_prev_page} >>", 'callback_data': f"pg;{self.type_btn};{num_prev_page}"}]]}
            )
        return


def callbackquery_process(update: Update, context: CallbackContext) -> None:
    # write_on_file("callbackquery_process.txt",str(update))
    try:
        bot = context.bot
        query = update.callback_query
        from_id = query.from_user.id
        chat_id = query.message.chat.id
        chat_type = query.message.chat.type
        data = query.data
        ex_data = data.split(';')
    except:
        pass
    timestamp = int(time.time())
    try:
        if data == "test":
            return
        elif data == "nazan":
            return query.answer("نزن خراب میشه 😕")
        conn = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        cs = conn.cursor()
        cs.execute(f"SELECT * FROM {utl.admini}")
        row_admin = cs.fetchone()
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{from_id}'")
        row_user = cs.fetchone()
        is_admin = True if from_id == utl.admin_id or row_user['status'] == 'admin' else False
        
        if row_admin['gtg_per'] or is_admin:
            if ex_data[0] == 'update':
                gtg_id = int(ex_data[1])
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={gtg_id}")
                row_gtg = cs.fetchone()
                if row_gtg is None:
                    query.answer("❌ یافت نشد",show_alert=True)
                else:
                    created_at = jdatetime.datetime.fromtimestamp(row_gtg['created_at']).strftime('%Y/%m/%d %H:%M:%S')
                    updated_at = jdatetime.datetime.fromtimestamp(row_gtg['updated_at']).strftime('%Y/%m/%d %H:%M:%S')
                    now = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                    
                    inline_keyboard = []
                    if not is_admin or row_gtg['status'] == 'end':
                        inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': 'nazan'}])
                    else:
                        inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': f"change_status;{row_gtg['id']};none"}])
                    if row_gtg['status'] != "end" or is_admin:
                        inline_keyboard.append([{'text': '🔄 update 🔄', 'callback_data': f"update;{row_gtg['id']}"}])
                        inline_keyboard.append([{'text': '🔄 auto update 🔄', 'callback_data': f"auto_update;{row_gtg['id']}"}])
                    origin = ""
                    if row_gtg['origin'] != "0":
                        origin += "Source Group:\n"
                        origin += f"🆔 <code>{row_gtg['origin_id']}</code>\n"
                        origin += f"🔗 {row_gtg['origin']}\n"
                    last_bot_check = f"🟠 اکانت در حال بررسی: <code>{row_gtg['last_bot_check']}</code>\n" if row_gtg['last_bot_check'] != "0" and row_gtg['status'] != "end" else ""
                    query.edit_message_text(
                        text=f"{origin}\n"+
                            "Destination Group:\n"+
                            f"🆔 <code>{row_gtg['destination_id']}</code>\n"+
                            f"🔗 {row_gtg['destination']}\n\n"+
                            f"👤 done/requested: [{row_gtg['count_moved']}/{row_gtg['count']}]\n"+
                            f"👤 checking/all: [{row_gtg['last_member_check']}/{row_gtg['max_users']}]\n\n"+
                            f"{last_bot_check}"+
                            f"🔵 کل اکانت ها: {row_gtg['count_acc']}\n"+
                            f"🔵 اکانت های بن شده: {row_gtg['count_accban']}\n"+
                            f"🔵 اکانت های اسپم خورده: {row_gtg['count_spam']}\n"+
                            f"🔵 اکانت های محدود شده: {row_gtg['count_restrict']}\n"+
                            f"🔵 اکانت های ریپورت شده: {row_gtg['count_report']}\n"+
                            f"🔵 اکانت های از دسترس خارج شده: {row_gtg['count_accout']}\n"+
                            f"🔵 اکانت های عدم سطح دسترسی در گروه: {row_gtg['count_permission']}\n\n"+
                            f"🔴 کاربران بن در گروه: {row_gtg['count_ban']}\n"+
                            f"🔴 کاربران قبلا عضو در گروه: {row_gtg['count_repeat']}\n"+
                            f"🔴 کاربران با حریم خصوصی فعال: {row_gtg['count_privacy']}\n"+
                            f"🔴 کاربران عضو در حداکثر تعداد گروه: {row_gtg['count_toomuch']}\n\n"+
                            f"⚪️ خروجی کاربران مشکل دار: /exo_{row_gtg['id']}_e\n"+
                            f"⚪️ خروجی کاربران باقی مانده: /exo_{row_gtg['id']}_r\n"+
                            f"⚪️ خروجی کاربران انتقال داده شده: /exo_{row_gtg['id']}_m\n"+
                            "➖➖➖➖➖\n"+
                            f"📅️ Created: {created_at}\n"+
                            f"📅️ Updated: {updated_at}\n"+
                            f"📅️ ️Now: {now}",
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup={'inline_keyboard': inline_keyboard}
                    )
                return
            elif ex_data[0] == 'auto_update':
                gtg_id = int(ex_data[1])
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={gtg_id}")
                row_gtg = cs.fetchone()
                if row_gtg is None:
                    query.answer("❌ یافت نشد",show_alert=True)
                elif (timestamp - row_user['last_auto_update_at']) < 60:
                    wait = 60 - (timestamp - row_user['last_auto_update_at'])
                    query.answer(f"❌ آدم باش {wait} ثانیه دیگه صبر کن")
                else:
                    origin = ""
                    if row_gtg['origin'] != "0":
                        origin += "Source Group:\n"
                        origin += f"🆔 <code>{row_gtg['origin_id']}</code>\n"
                        origin += f"🔗 {row_gtg['origin']}\n"
                    i = 0
                    cs.execute(f"UPDATE {utl.users} SET last_auto_update_at='{timestamp}' WHERE user_id='{from_id}'")
                    while i < 60 and row_gtg['status'] == 'doing':
                        try:
                            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={gtg_id}")
                            row_gtg = cs.fetchone()
                            created_at = jdatetime.datetime.fromtimestamp(row_gtg['created_at']).strftime('%Y/%m/%d %H:%M:%S')
                            updated_at = jdatetime.datetime.fromtimestamp(row_gtg['updated_at']).strftime('%Y/%m/%d %H:%M:%S')
                            now = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                            last_bot_check = f"🟠 اکانت در حال بررسی: <code>{row_gtg['last_bot_check']}</code>\n" if row_gtg['last_bot_check'] != "0" and row_gtg['status'] != "end" else ""
                            query.edit_message_text(
                                text=f"{origin}\n"+
                                    "Destination Group:\n"+
                                    f"🆔 <code>{row_gtg['destination_id']}</code>\n"+
                                    f"🔗 {row_gtg['destination']}\n\n"+
                                    f"👤 done/requested: [{row_gtg['count_moved']}/{row_gtg['count']}]\n"+
                                    f"👤 checking/all: [{row_gtg['last_member_check']}/{row_gtg['max_users']}]\n\n"+
                                    f"{last_bot_check}"+
                                    f"🔵 کل اکانت ها: {row_gtg['count_acc']}\n"+
                                    f"🔵 اکانت های بن شده: {row_gtg['count_accban']}\n"+
                                    f"🔵 اکانت های اسپم خورده: {row_gtg['count_spam']}\n"+
                                    f"🔵 اکانت های محدود شده: {row_gtg['count_restrict']}\n"+
                                    f"🔵 اکانت های ریپورت شده: {row_gtg['count_report']}\n"+
                                    f"🔵 اکانت های از دسترس خارج شده: {row_gtg['count_accout']}\n"+
                                    f"🔵 اکانت های عدم سطح دسترسی در گروه: {row_gtg['count_permission']}\n\n"+
                                    f"🔴 کاربران بن در گروه: {row_gtg['count_ban']}\n"+
                                    f"🔴 کاربران قبلا عضو در گروه: {row_gtg['count_repeat']}\n"+
                                    f"🔴 کاربران با حریم خصوصی فعال: {row_gtg['count_privacy']}\n"+
                                    f"🔴 کاربران عضو در حداکثر تعداد گروه: {row_gtg['count_toomuch']}\n\n"+
                                    f"⚪️ خروجی کاربران مشکل دار: /exo_{row_gtg['id']}_e\n"+
                                    f"⚪️ خروجی کاربران باقی مانده: /exo_{row_gtg['id']}_r\n"+
                                    f"⚪️ خروجی کاربران انتقال داده شده: /exo_{row_gtg['id']}_m\n"+
                                    "➖➖➖➖➖\n"+
                                    f"📅️ Created: {created_at}\n"+
                                    f"📅️ Updated: {updated_at}\n"+
                                    f"📅️ ️Now: {now}\n\n"+
                                    f"در حال آپدیت خودکار یک دقیقه: {(60-i)}",
                                parse_mode='HTML',
                                disable_web_page_preview=True,
                                reply_markup={'inline_keyboard': [
                                    [{'text': utl.status_gtg[row_gtg['status']], 'callback_data': f"change_status;{row_gtg['id']};none"}],
                                ]}
                            )
                            if row_gtg['status'] != 'doing':
                                break
                        except:
                            pass
                        i += 4
                        time.sleep(4)
                    
                    inline_keyboard = []
                    if not is_admin or row_gtg['status'] == 'end':
                        inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': 'nazan'}])
                    else:
                        inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': f"change_status;{row_gtg['id']};none"}])
                    if row_gtg['status'] != "end" or is_admin:
                        inline_keyboard.append([{'text': '🔄 update 🔄', 'callback_data': f"update;{row_gtg['id']}"}])
                        inline_keyboard.append([{'text': '🔄 auto update 🔄', 'callback_data': f"auto_update;{row_gtg['id']}"}])
                    last_bot_check = f"🟠 اکانت در حال بررسی: <code>{row_gtg['last_bot_check']}</code>\n" if row_gtg['last_bot_check'] != "0" and row_gtg['status'] != "end" else ""
                    query.edit_message_text(
                        text=f"{origin}\n"+
                            "🔹 گروه مقصد:\n"+
                            f"<code>{row_gtg['destination_id']}</code>\n"+
                            f"{row_gtg['destination']}\n\n"+
                            f"👤 done/requested: [{row_gtg['count_moved']}/{row_gtg['count']}]\n"+
                            f"👤 checking/all: [{row_gtg['last_member_check']}/{row_gtg['max_users']}]\n\n"+
                            f"{last_bot_check}"+
                            f"🔵 کل اکانت ها: {row_gtg['count_acc']}\n"+
                            f"🔵 اکانت های بن شده: {row_gtg['count_accban']}\n"+
                            f"🔵 اکانت های اسپم خورده: {row_gtg['count_spam']}\n"+
                            f"🔵 اکانت های محدود شده: {row_gtg['count_restrict']}\n"+
                            f"🔵 اکانت های ریپورت شده: {row_gtg['count_report']}\n"+
                            f"🔵 اکانت های از دسترس خارج شده: {row_gtg['count_accout']}\n"+
                            f"🔵 اکانت های عدم سطح دسترسی در گروه: {row_gtg['count_permission']}\n\n"+
                            f"🔴 کاربران بن در گروه: {row_gtg['count_ban']}\n"+
                            f"🔴 کاربران قبلا عضو در گروه: {row_gtg['count_repeat']}\n"+
                            f"🔴 کاربران با حریم خصوصی فعال: {row_gtg['count_privacy']}\n"+
                            f"🔴 کاربران عضو در حداکثر تعداد گروه: {row_gtg['count_toomuch']}\n\n"+
                            f"⚪️ خروجی کاربران مشکل دار: /exo_{row_gtg['id']}_e\n"+
                            f"⚪️ خروجی کاربران باقی مانده: /exo_{row_gtg['id']}_r\n"+
                            f"⚪️ خروجی کاربران انتقال داده شده: /exo_{row_gtg['id']}_m\n"+
                            "➖➖➖➖➖\n"+
                            f"📅️ Created: {created_at}\n"+
                            f"📅️ Updated: {updated_at}\n"+
                            f"📅️ ️Now: {now}",
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup={'inline_keyboard': inline_keyboard}
                    )
                return
        if from_id != utl.admin_id and row_user['status'] != 'admin':
            return
        if ex_data[0] == 'pg':
            if ex_data[1] == 'accounts':
                selected_pages = (int(ex_data[2]) - 1) * step_page;
                i = selected_pages + 1;
                cs.execute(f"SELECT * FROM {utl.mbots} ORDER BY id DESC LIMIT {selected_pages},{step_page}")
                result = cs.fetchall()
                if not result:
                    query.answer("⚠️ صفحه دیگری وجود ندارد",show_alert=True)
                else:
                    output = ""
                    for row in result:
                        if row['status'] == 'restrict':
                            output += f"{i}. phone: <code>{row['phone']}</code>\n"
                            output += f"⛔ restrict: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                        else:
                            output += f"{i}. phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                        output += f"🔸️ status: /status_{row['id']}\n"
                        output += f"🔸️ delete: /delete_{row['id']}\n\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots}")
                    rowcount = cs.fetchone()['count']
                    output = f"📜 لیست اکانت ها ({rowcount})\n\n{output}"
                    ob = Pagination(update,"accounts",output,step_page,rowcount)
                    ob.processCallback()
                return
            if ex_data[1] == 'restrict':
                selected_pages = (int(ex_data[2]) - 1) * step_page;
                i = selected_pages + 1;
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='restrict' ORDER BY end_restrict ASC LIMIT {selected_pages},{step_page}")
                result = cs.fetchall()
                if not result:
                    query.answer("⚠️ صفحه دیگری وجود ندارد",show_alert=True)
                else:
                    output = ""
                    for row in result:
                        output += f"{i}. phone: <code>{row['phone']}</code>\n"
                        output += f"⛔ restrict: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                        output += f"🔸️ status: /status_{row['id']}\n"
                        output += f"🔸️ delete: /delete_{row['id']}\n\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='restrict'")
                    rowcount = cs.fetchone()['count']
                    output = f"📜 لیست اکانت های محدود شده ({rowcount})\n\n{output}"
                    ob = Pagination(update,"restrict",output,step_page,rowcount)
                    ob.processCallback()
                return
            if ex_data[1] == 'first_level':
                selected_pages = (int(ex_data[2]) - 1) * step_page;
                i = selected_pages + 1;
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='first_level' ORDER BY last_order_at DESC LIMIT {selected_pages},{step_page}")
                result = cs.fetchall()
                if not result:
                    query.answer("⚠️ صفحه دیگری وجود ندارد",show_alert=True)
                else:
                    output = ""
                    for row in result:
                        output += f"{i}. phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                        output += f"🔸️ status: /status_{row['id']}\n"
                        output += f"🔸️ delete: /delete_{row['id']}\n\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='first_level'")
                    rowcount = cs.fetchone()['count']
                    output = f"📜 لیست اکانت های ثبت نشده ({rowcount})\n\n{output}"
                    ob = Pagination(update,"first_level",output,step_page,rowcount)
                    ob.processCallback()
                return
            if ex_data[1] == 'submitted':
                selected_pages = (int(ex_data[2]) - 1) * step_page;
                i = selected_pages + 1;
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' ORDER BY last_order_at ASC LIMIT {selected_pages},{step_page}")
                result = cs.fetchall()
                if not result:
                    query.answer("⚠️ صفحه دیگری وجود ندارد",show_alert=True)
                else:
                    output = ""
                    for row in result:
                        output += f"{i}. phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                        output += f"🔸️ status: /status_{row['id']}\n"
                        output += f"🔸️ delete: /delete_{row['id']}\n\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='submitted'")
                    rowcount = cs.fetchone()['count']
                    output = f"📜 لیست اکانت های فعال ({rowcount})\n\n{output}"
                    ob = Pagination(update,"submitted",output,step_page,rowcount)
                    ob.processCallback()
                return
            if ex_data[1] == 'adability':
                limit_per_h = row_admin['limit_per_h'] * 3600
                selected_pages = (int(ex_data[2]) - 1) * step_page;
                i = selected_pages + 1;
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp} ORDER BY last_order_at ASC LIMIT {selected_pages},{step_page}")
                result = cs.fetchall()
                if not result:
                    query.answer("⚠️ صفحه دیگری وجود ندارد",show_alert=True)
                else:
                    output = ""
                    for row in result:
                        output += f"{i}. phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                        output += f"🔸️ status: /status_{row['id']}\n"
                        output += f"🔸️ delete: /delete_{row['id']}\n\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp}")
                    rowcount = cs.fetchone()['count']
                    output = f"📜 لیست اکانت های قابلیت اد ({rowcount})\n\n{output}"
                    ob = Pagination(update,"adability",output,step_page,rowcount)
                    ob.processCallback()
                return
            if ex_data[1] == 'orders':
                selected_pages = (int(ex_data[2]) - 1) * step_page;
                i = selected_pages + 1;
                cs.execute(f"SELECT * FROM {utl.gtg} ORDER BY id DESC LIMIT {selected_pages},{step_page}")
                result = cs.fetchall()
                if not result:
                    query.answer("⚠️ صفحه دیگری وجود ندارد",show_alert=True)
                else:
                    output = ""
                    for row in result:
                        created_at = jdatetime.datetime.fromtimestamp(row['created_at'])
                        output += f"{i}. /gtg_{row['id']}\n"
                        output += f"🔹️ Source: {row['origin']}\n"
                        output += f"🔹️ Destination: {row['destination']}\n"
                        output += f"🔹️ Done/Requested: [{row['count_moved']}/{row['count']}]\n"
                        output += f"🔹️ Status: {utl.status_gtg[row['status']]}\n"
                        output += f"📅️ {created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.gtg}")
                    rowcount = cs.fetchone()['count']
                    output = f"📜 لیست سفارشات ({rowcount})\n\n{output}"
                    ob = Pagination(update,"orders",output,step_page,rowcount)
                    ob.processCallback()
                return
            if ex_data[1] == 'apis':
                selected_pages = (int(ex_data[2]) - 1) * step_page;
                i = selected_pages + 1;
                cs.execute(f"SELECT * FROM {utl.apis} ORDER BY id DESC LIMIT {selected_pages},{step_page}")
                result = cs.fetchall()
                if not result:
                    query.answer("⚠️ صفحه دیگری وجود ندارد",show_alert=True)
                else:
                    output = ""
                    for row in result:
                        output += f"🔴️ Api ID: <code>{row['api_id']}</code>\n"
                        output += f"🔴️ Api Hash: <code>{row['api_hash']}</code>\n"
                        output += f"🔴️ Delete: /dela_{row['id']}\n\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
                    rowcount = cs.fetchone()['count']
                    output = f"📜 لیست ای پی ای ها ({rowcount})\n\n{output}"
                    ob = Pagination(update,"apis",output,step_page,rowcount)
                    ob.processCallback()
                return
            return
        if ex_data[0] == 'settings':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE status NOT IN ('end')")
            if cs.fetchone():
                return query.answer(
                    "❌ امکان تغییر در تنظیمات وجود ندارد.\n\n"+
                    "شما سفارش فعال دارید",
                    show_alert=True
                )
            elif ex_data[1] == 'time_spam_restrict':
                row_admin['time_spam_restrict'] += (int(ex_data[2]) * 86400)
                if row_admin['time_spam_restrict'] <= 0:
                    return query.answer("❌ حداقل باید 1 روز باشد",show_alert=True)
                cs.execute(f"UPDATE {utl.admini} SET time_spam_restrict={row_admin['time_spam_restrict']}")
            elif ex_data[1] == 'change_pass':
                row_admin['change_pass'] = 1 - row_admin['change_pass']
                cs.execute(f"UPDATE {utl.admini} SET change_pass={row_admin['change_pass']}")
            elif ex_data[1] == 'exit_session':
                row_admin['exit_session'] = 1 - row_admin['exit_session']
                cs.execute(f"UPDATE {utl.admini} SET exit_session={row_admin['exit_session']}")
            elif ex_data[1] == 'is_change_profile':
                row_admin['is_change_profile'] = 1 - row_admin['is_change_profile']
                cs.execute(f"UPDATE {utl.admini} SET is_change_profile={row_admin['is_change_profile']}")
            elif ex_data[1] == 'is_set_username':
                row_admin['is_set_username'] = 1 - row_admin['is_set_username']
                cs.execute(f"UPDATE {utl.admini} SET is_set_username={row_admin['is_set_username']}")
            elif ex_data[1] == 'leave_per':
                row_admin['leave_per'] = 1 - row_admin['leave_per']
                cs.execute(f"UPDATE {utl.admini} SET leave_per={row_admin['leave_per']}")
            elif ex_data[1] == 'delete_first_levels':
                row_admin['delete_first_levels'] = 1 - row_admin['delete_first_levels']
                cs.execute(f"UPDATE {utl.admini} SET delete_first_levels={row_admin['delete_first_levels']}")
            elif ex_data[1] == 'gtg_per':
                row_admin['gtg_per'] = 1 - row_admin['gtg_per']
                cs.execute(f"UPDATE {utl.admini} SET gtg_per={row_admin['gtg_per']}")
            elif ex_data[1] == 'type_analyze':
                row_admin['type_analyze'] = 1 - row_admin['type_analyze']
                cs.execute(f"UPDATE {utl.admini} SET type_analyze={row_admin['type_analyze']}")
            elif ex_data[1] == 'type_add':
                row_admin['type_add'] = 1 - row_admin['type_add']
                cs.execute(f"UPDATE {utl.admini} SET type_add={row_admin['type_add']}")
            elif ex_data[2] == 'guide':
                pass
            else:
                number = int(ex_data[2])
                if ex_data[1] == 'api_per_number':
                    row_admin['api_per_number'] += number
                    if row_admin['api_per_number'] < 1:
                        return query.answer("❌ حداقل باید 1 باشد")
                    else:
                        cs.execute(f"UPDATE {utl.admini} SET api_per_number={row_admin['api_per_number']}")
                elif ex_data[1] == 'add_per_h':
                    row_admin['add_per_h'] += number
                    if row_admin['add_per_h'] < 5:
                        return query.answer("❌ حداقل باید 5 باشد")
                    elif row_admin['add_per_h'] > 28:
                        return query.answer("❌ حداقل باید 28 باشد")
                    else:
                        cs.execute(f"UPDATE {utl.admini} SET add_per_h={row_admin['add_per_h']}")
                elif ex_data[1] == 'limit_per_h':
                    row_admin['limit_per_h'] += number
                    if row_admin['limit_per_h'] < 0:
                        return query.answer("❌ حداقل باید 0 باشد")
                    else:
                        cs.execute(f"UPDATE {utl.admini} SET limit_per_h={row_admin['limit_per_h']}")
            time_spam_restrict = int(row_admin['time_spam_restrict'] / 86400)
            change_pass = "✅ تغییر/تنظیم پسورد دو مرحله ای ✅" if row_admin['change_pass'] else "❌ تغییر/تنظیم پسورد دو مرحله ای ❌"
            exit_session = "✅ خروج از بقیه سشن ها ✅" if row_admin['exit_session'] else "❌ خروج از بقیه سشن ها ❌"
            is_change_profile = "✅ تنظیم نام، بیو و پروفایل ✅" if row_admin['is_change_profile'] else "❌ تنظیم نام، بیو و پروفایل ❌"
            is_set_username = "✅ تنظیم یوزرنیم ✅" if row_admin['is_set_username'] else "❌ تنظیم یوزرنیم ❌"
            leave_per = "✅ اکانت ها گروه ها را ترک کنند ✅" if row_admin['leave_per'] else "❌ اکانت ها گروه ها را ترک کنند ❌"
            delete_first_levels = "✅ حذف خودکار اکانت های ثبت نشده ✅" if row_admin['delete_first_levels'] else "❌ حذف خودکار اکانت های ثبت نشده ❌"
            gtg_per = "✅ دسترسی همه به شناسه سفارش ✅" if row_admin['gtg_per'] else "❌ دسترسی همه به شناسه سفارش ❌"
            type_analyze = "نوع آنالیز سفارش: لحظه ای" if row_admin['type_analyze'] else "نوع آنالیز سفارش: دیتابیس"
            type_add = "نوع اد: حرفه ای" if row_admin['type_add'] else "نوع اد: عادی"
            
            query.edit_message_text(
                text=f"پنل تنظیمات:",
                reply_markup={'inline_keyboard': [
                    [{'text': f"در هر ای پی ای {row_admin['api_per_number']} شماره ثبت شود",'callback_data': f"settings;api_per_number;guide"}],
                    [
                        {'text': '+10','callback_data': f"settings;api_per_number;+10"},
                        {'text': '+5','callback_data': f"settings;api_per_number;+5"},
                        {'text': '+1','callback_data': f"settings;api_per_number;+1"},
                        {'text': '-1','callback_data': f"settings;api_per_number;-1"},
                        {'text': '-5','callback_data': f"settings;api_per_number;-5"},
                        {'text': '-10','callback_data': f"settings;api_per_number;-10"},
                    ],
                    [{'text': f"هر اکانت در هر استفاده {row_admin['add_per_h']} اد کند",'callback_data': f"settings;add_per_h;guide"}],
                    [
                        {'text': '+10','callback_data': f"settings;add_per_h;+10"},
                        {'text': '+5','callback_data': f"settings;add_per_h;+5"},
                        {'text': '+1','callback_data': f"settings;add_per_h;+1"},
                        {'text': '-1','callback_data': f"settings;add_per_h;-1"},
                        {'text': '-5','callback_data': f"settings;add_per_h;-5"},
                        {'text': '-10','callback_data': f"settings;add_per_h;-10"},
                    ],
                    [{'text': f"هر اکانت هر {row_admin['limit_per_h']} ساعت استفاده شود",'callback_data': f"settings;limit_per_h;guide"}],
                    [
                        {'text': '+10','callback_data': f"settings;limit_per_h;+10"},
                        {'text': '+5','callback_data': f"settings;limit_per_h;+5"},
                        {'text': '+1','callback_data': f"settings;limit_per_h;+1"},
                        {'text': '-1','callback_data': f"settings;limit_per_h;-1"},
                        {'text': '-5','callback_data': f"settings;limit_per_h;-5"},
                        {'text': '-10','callback_data': f"settings;limit_per_h;-10"},
                    ],
                    [{'text': f"اکانت موقع رسیدن به اسپم {time_spam_restrict} روز استراحت کند",'callback_data': f"settings;time_spam_restrict;guide"}],
                    [
                        {'text': '+10','callback_data': f"settings;time_spam_restrict;+10"},
                        {'text': '+5','callback_data': f"settings;time_spam_restrict;+5"},
                        {'text': '+1','callback_data': f"settings;time_spam_restrict;+1"},
                        {'text': '-1','callback_data': f"settings;time_spam_restrict;-1"},
                        {'text': '-5','callback_data': f"settings;time_spam_restrict;-5"},
                        {'text': '-10','callback_data': f"settings;time_spam_restrict;-10"},
                    ],
                    [{'text': change_pass,'callback_data': f"settings;change_pass;guide"}],
                    [{'text': exit_session,'callback_data': f"settings;exit_session;guide"}],
                    [{'text': is_change_profile,'callback_data': f"settings;is_change_profile;guide"}],
                    [{'text': is_set_username,'callback_data': f"settings;is_set_username;guide"}],
                    [{'text': leave_per,'callback_data': f"settings;leave_per;guide"}],
                    [{'text': delete_first_levels,'callback_data': f"settings;delete_first_levels;guide"}],
                    [{'text': gtg_per,'callback_data': f"settings;gtg_per;guide"}],
                    [{'text': type_analyze,'callback_data': f"settings;type_analyze;guide"}],
                    [{'text': type_add,'callback_data': f"settings;type_add;guide"}]
                ]}
            )
            return
        if ex_data[0] == 'change_status':
            gtg_id = int(ex_data[1])
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={gtg_id}")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                query.answer("❌ یافت نشد",show_alert=True)
            else:
                inline_keyboard = []
                if row_gtg['status'] == 'doing':
                    if ex_data[2] == 'none':
                        inline_keyboard.append([{'text': 'آیا از اتمام سفارش مطمئن هستید؟', 'callback_data': 'nazan'}])
                        inline_keyboard.append([{'text': '❌ کنسل ❌', 'callback_data': f"update;{row_gtg['id']}"},{'text': '✅ بله ✅', 'callback_data': f"change_status;{row_gtg['id']};end"}])
                        return query.edit_message_reply_markup(reply_markup={'inline_keyboard': inline_keyboard})
                    elif ex_data[2] == 'end':
                        row_gtg['status'] = 'end'
                        cs.execute(f"UPDATE {utl.gtg} SET status='{row_gtg['status']}' WHERE id={row_gtg['id']}")
                
                inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': 'nazan'}])
                inline_keyboard.append([{'text': '🔄 update 🔄', 'callback_data': f"update;{row_gtg['id']}"}])
                inline_keyboard.append([{'text': '🔄 auto update 🔄', 'callback_data': f"auto_update;{row_gtg['id']}"}])
                query.edit_message_reply_markup(reply_markup={'inline_keyboard': inline_keyboard})
            return
        if ex_data[0] == "d":
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{ex_data[1]}'")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                query.answer("❌ کاربر یافت نشد",show_alert=True)
            else:
                value = ex_data[2]
                if value == 'balance':
                    change_balance = row_user_select['balance'] + int(ex_data[3])
                    if change_balance <= 0:
                        if not row_user_select['balance']:
                            return query.answer("❌ امکان پذیر نیست",show_alert=True)
                        else:
                            row_user_select['balance'] = 0
                    else:
                        row_user_select['balance'] = change_balance
                    cs.execute(f"UPDATE {utl.users} SET balance='{row_user_select['balance']}' WHERE user_id='{row_user_select['user_id']}'")
                if value == 'is_submit_panel':
                    row_user_select['is_submit_panel'] = 1 - row_user_select['is_submit_panel']
                    cs.execute(f"UPDATE {utl.users} SET is_submit_panel='{row_user_select['is_submit_panel']}' WHERE user_id='{row_user_select['user_id']}'")
                else:
                    if value == "admin" or ((value == "user" or value == "block") and row_user_select['status'] == 'admin'):
                        if utl.admin_id == from_id:
                            cs.execute(f"UPDATE {utl.users} SET status='{value}' WHERE user_id='{row_user_select['user_id']}'")
                        else:
                            return query.answer("⛔️ این عملکرد مخصوص ادمین اصلی است",show_alert=True)
                    elif value == "block" or value == "user":
                        cs.execute(f"UPDATE {utl.users} SET status='{value}' WHERE user_id='{row_user_select['user_id']}'")
                    elif value == "sendmsg":
                        cs.execute(f"UPDATE {utl.users} SET step='sendmsg;{row_user_select['user_id']}' WHERE user_id='{from_id}'")
                        return bot.send_message(chat_id=chat_id,text="پیام را ارسال کنید:\nکنسل: /cancel")
                    else:
                        return
                cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{ex_data[1]}'")
                row_user_select = cs.fetchone()
                if row_user_select['status'] == "block":
                    block = 'بلاک ✅'
                    block_status = "user"
                else:
                    block = 'بلاک ❌'
                    block_status = "block"
                if row_user_select['status'] == "admin":
                    admin = 'ادمین ✅'
                    admin_status = "user"
                else:
                    admin = 'ادمین ❌'
                    admin_status = "admin"
                query.edit_message_text(parse_mode='HTML',text=f"کاربر <a href='tg://user?id={row_user_select['user_id']}'>{row_user_select['user_id']}</a> (/d_{row_user_select['user_id']})",
                    reply_markup={'inline_keyboard': [
                        [{'text': "ارسال پیام",'callback_data': f"d;{row_user_select['user_id']};sendmsg"}],
                        [
                            {'text': block,'callback_data': f"d;{row_user_select['user_id']};{block_status}"},
                            {'text': admin,'callback_data': f"d;{row_user_select['user_id']};{admin_status}"}
                        ]
                    ]}
                )
            return
        if ex_data[0] == "analyze":
            cs.execute(f"SELECT * FROM {utl.egroup} WHERE id='{ex_data[1]}'")
            row_egroup = cs.fetchone()
            if row_egroup is not None:
                cs.execute(f"UPDATE {utl.egroup} SET status='end' WHERE id='{row_egroup['id']}'")
                query.edit_message_reply_markup(
                    reply_markup={'inline_keyboard': [[{'text': "در حال اتمام...",'callback_data': "nazan"}]]}
                )
            else:
                query.answer("❌ آنالیز یافت نشد",show_alert=True)
            return
        if ex_data[0] == "status_analyze":
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id='{ex_data[1]}'")
            row_gtg = cs.fetchone()
            if row_gtg is not None:
                cs.execute(f"UPDATE {utl.gtg} SET status_analyze='end' WHERE id='{row_gtg['id']}'")
                query.edit_message_reply_markup(
                    reply_markup={'inline_keyboard': [[{'text': "در حال اتمام...",'callback_data': "nazan"}]]}
                )
            else:
                query.answer("❌ آنالیز یافت نشد",show_alert=True)
            return
    except RetryAfter as e:
        query.answer("−⚠️┈┅━ "+str(int(e.retry_after))+" ثانیه بعد تلاش کنید!",show_alert=True)
    except:
        pass


def private_process(update: Update, context: CallbackContext) -> None:
    # write_on_file("private_process.txt",str(update))
    bot = context.bot
    message = update.message
    from_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    chat_id = message.chat.id
    message_id = message.message_id
    if message.text:
        text = message.text
    else:
        text = ""
    if update.message.text:
        txtcap = update.message.text
    elif update.message.caption:
        txtcap = update.message.caption
    ex_text = text.split('_')
    
    timestamp = int(time.time())
    conn = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
    cs = conn.cursor()
    cs.execute(f"SELECT * FROM {utl.admini}")
    row_admin = cs.fetchone()
    
    cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{from_id}'")
    row_user = cs.fetchone()
    if row_user is None:
        cs.execute(f"INSERT INTO {utl.users} (user_id,created_at,uniq_id) VALUES ('{from_id}','{timestamp}','{utl.uniq_id_generate(cs,10,utl.users)}')")
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{from_id}'")
        row_user = cs.fetchone()
    ex_step = row_user['step'].split(';')
    is_admin = True if from_id == utl.admin_id or row_user['status'] == 'admin' else False
    
    if row_admin['gtg_per'] or is_admin:
        if ex_text[0] == '/gtg':
            gtg_id = int(ex_text[1])
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={gtg_id}")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                return message.reply_html(text="❌ یافت نشد")
            created_at = jdatetime.datetime.fromtimestamp(row_gtg['created_at']).strftime('%Y/%m/%d %H:%M:%S')
            updated_at = jdatetime.datetime.fromtimestamp(row_gtg['updated_at']).strftime('%Y/%m/%d %H:%M:%S')
            now = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            inline_keyboard = []
            if not is_admin or row_gtg['status'] == 'end':
                if not is_admin and row_gtg['status'] == 'start':
                    return
                inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': 'nazan'}])
            else:
                inline_keyboard.append([{'text': utl.status_gtg[row_gtg['status']], 'callback_data': f"change_status;{row_gtg['id']};none"}])
            if row_gtg['status'] != "end" or is_admin:
                inline_keyboard.append([{'text': '🔄 update 🔄', 'callback_data': f"update;{row_gtg['id']}"}])
                inline_keyboard.append([{'text': '🔄 auto update 🔄', 'callback_data': f"auto_update;{row_gtg['id']}"}])
            origin = ""
            if row_gtg['origin'] != "0":
                origin += "Source Group:\n"
                origin += f"🆔 <code>{row_gtg['origin_id']}</code>\n"
                origin += f"🔗 {row_gtg['origin']}\n"
            last_bot_check = f"🟠 اکانت در حال بررسی: <code>{row_gtg['last_bot_check']}</code>\n" if row_gtg['last_bot_check'] != "0" and row_gtg['status'] != "end" else ""
            message.reply_html(
                text=f"{origin}"+
                    "Destination Group:\n"+
                    f"🆔 <code>{row_gtg['destination_id']}</code>\n"+
                    f"🔗 {row_gtg['destination']}\n\n"+
                    f"👤 done/requested: [{row_gtg['count_moved']}/{row_gtg['count']}]\n"+
                    f"👤 checking/all: [{row_gtg['last_member_check']}/{row_gtg['max_users']}]\n\n"+
                    f"{last_bot_check}"+
                    f"🔵 کل اکانت ها: {row_gtg['count_acc']}\n"+
                    f"🔵 اکانت های بن شده: {row_gtg['count_accban']}\n"+
                    f"🔵 اکانت های اسپم خورده: {row_gtg['count_spam']}\n"+
                    f"🔵 اکانت های محدود شده: {row_gtg['count_restrict']}\n"+
                    f"🔵 اکانت های ریپورت شده: {row_gtg['count_report']}\n"+
                    f"🔵 اکانت های از دسترس خارج شده: {row_gtg['count_accout']}\n"+
                    f"🔵 اکانت های عدم سطح دسترسی در گروه: {row_gtg['count_permission']}\n\n"+
                    f"🔴 کاربران بن در گروه: {row_gtg['count_ban']}\n"+
                    f"🔴 کاربران قبلا عضو در گروه: {row_gtg['count_repeat']}\n"+
                    f"🔴 کاربران با حریم خصوصی فعال: {row_gtg['count_privacy']}\n"+
                    f"🔴 کاربران عضو در حداکثر تعداد گروه: {row_gtg['count_toomuch']}\n\n"+
                    f"⚪️ خروجی کاربران مشکل دار: /exo_{row_gtg['id']}_e\n"+
                    f"⚪️ خروجی کاربران باقی مانده: /exo_{row_gtg['id']}_r\n"+
                    f"⚪️ خروجی کاربران انتقال داده شده: /exo_{row_gtg['id']}_m\n"+
                    "➖➖➖➖➖➖\n"+
                    f"📅️ Created: {created_at}\n"+
                    f"📅️ Updated: {updated_at}\n"+
                    f"📅 ️Now: {now}",
                disable_web_page_preview=True,
                reply_markup={'inline_keyboard': inline_keyboard}
            )
            return
    if not is_admin:
        return
    if text == '/start' or text == 'start' or text == '/panel' or text == 'panel' or text == 'پنل' or text == utl.menu_var or text == '/cancel':
        user_panel(update)
        cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
        cs.execute(f"DELETE FROM {utl.gtg} WHERE user_id='{from_id}' AND status='start'")
        return
    if ex_step[0] == 'add_acc':
        if ex_step[1] == 'phone':
            row_apis = utl.select_api(cs,row_admin['api_per_number'])
            if row_apis is None:
                message.reply_html(text="❌ هیچ Api ای یافت نشد")
            else:
                phone = text.replace("+","").replace(" ","")
                if not re.findall('^[0-9]*$', phone):
                    message.reply_html(text="❌ شماره اشتباه است!")
                else:
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE phone='{phone}'")
                    row_mbots = cs.fetchone()
                    if row_mbots is None:
                        uniq_id = utl.uniq_id_generate(cs,10,utl.mbots)
                        cs.execute(f"INSERT INTO {utl.mbots} (creator_user_id,phone,last_order_at,api_id,api_hash,created_at,uniq_id) VALUES ('{from_id}','{phone}','0','{row_apis['api_id']}','{row_apis['api_hash']}','{timestamp}','{uniq_id}')")
                        cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{uniq_id}'")
                        row_mbots = cs.fetchone()
                    else:
                        cs.execute(f"UPDATE {utl.mbots} SET api_id='{row_apis['api_id']}',api_hash='{row_apis['api_hash']}' WHERE id={row_mbots['id']}")
                    info_msg = message.reply_html(text="در حال بررسی ...")
                    os.system(f"python tl.account.py {from_id} first_level {row_mbots['id']}")
                    bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
            return
        elif ex_step[1] == 'code':
            mbots_id = int(ex_step[2])
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={mbots_id}")
            row_mbots = cs.fetchone()
            try:
                ex_nl_text = text.split("\n")
                if len(ex_nl_text) == 1:
                    cs.execute(f"UPDATE {utl.mbots} SET code='{int(text)}' WHERE id={row_mbots['id']}")
                elif len(ex_nl_text) == 2:
                    if len(ex_nl_text[0]) > 200 or len(ex_nl_text[1]) > 200:
                        return message.reply_html(text="❌ ورودی نادرست")
                    cs.execute(f"UPDATE {utl.mbots} SET code='{int(ex_nl_text[0])}',password='{ex_nl_text[1]}' WHERE id={row_mbots['id']}")
                info_msg = message.reply_html(text="در حال بررسی ...")
                os.system(f"python tl.account.py {from_id} code {row_mbots['id']}")
                info_msg.delete()
            except:
                message.reply_html(
                    text="❌ کد را بدرستی وارد کنید",
                    reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                )
            return
        return
    elif ex_step[0] == 'create_order':
        if ex_step[1] == 'info':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE status NOT IN ('end')")
            row_gtg = cs.fetchone()
            if row_gtg is not None:
                message.reply_html(text="❌ سفارش فعال وجود دارد")
            else:
                try:
                    ex_nl_text = text.split("\n")
                    source = ex_nl_text[0].replace("/+","/joinchat/")
                    target = ex_nl_text[1].replace("/+","/joinchat/")
                    count = int(ex_nl_text[2])
                    ex_nl_text = text.split("\n")
                    if len(source) > 200 or len(target) > 200 or len(ex_nl_text) != 3:
                        message.reply_html(text="❌ مقادیر نامعتبر")
                    elif source[0:13] != "https://t.me/":
                        message.reply_html(text="❌ گروه مبدا غیر معتبر")
                    elif target[0:13] != "https://t.me/":
                        message.reply_html(text="❌ گروه مقصد غیر معتبر")
                    else:
                        uniq_id = utl.uniq_id_generate(cs,10,utl.gtg)
                        cs.execute(f"INSERT INTO {utl.gtg} (user_id,origin,destination,count,created_at,updated_at,uniq_id) VALUES ('{from_id}','{source}','{target}','{count}','{timestamp}','{timestamp}','{uniq_id}')")
                        cs.execute(f"SELECT * FROM {utl.gtg} WHERE uniq_id='{uniq_id}'")
                        row_gtg = cs.fetchone()
                        cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                        
                        info_msg = message.reply_html(text="در حال بررسی ...")
                        os.system(f"python tl.analyze.py {from_id} check {row_gtg['id']}")
                        bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
                except:
                    message.reply_html(text="❌ طبق نمونه ارسال کنید")
        elif ex_step[1] == 'type_users':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE user_id='{from_id}' AND status='start'")
            row_gtg = cs.fetchone()
            if row_gtg is not None:
                info_msg = message.reply_html(text="در حال پیکربندی...")
                if text == 'همه کاربران':
                    type_users = 'users_all'
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze} WHERE is_bad=0")
                    max_users = cs.fetchone()['count']
                elif text == 'کاربران واقعی':
                    type_users = 'users_real'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0 AND is_real=0")
                elif text == 'کاربران فیک':
                    type_users = 'users_fake'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0 AND is_fake=0")
                elif text == 'کاربران آنلاین':
                    type_users = 'users_online'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0 AND is_online=0")
                elif text == 'کاربران دارای شماره':
                    type_users = 'users_has_phone'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0 AND is_phone=0")
                else:
                    return message.reply_html(text="❌ صرفا از منو انتخاب کنید")
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.analyze} WHERE is_bad=0")
                max_users = cs.fetchone()['count']
                cs.execute(f"UPDATE {utl.gtg} SET status='doing',max_users='{max_users}',type_users='{type_users}',created_at='{timestamp}',updated_at='{timestamp}' WHERE id={row_gtg['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                user_panel(update,
                    text=f"✅ سفارش با موفقیت ثبت شد و در حال انجام است\n\n"+
                    f"♻️ /gtg_{row_gtg['id']}"
                )
                bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
            else:
                message.reply_html(text="❌ سفارش یافت نشد")
        return
    elif ex_step[0] == 'create_order_file':
        if ex_step[1] == 'destination':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={int(ex_step[2])}")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                message.reply_html(text="❌ سفارش یافت نشد.")
            else:
                target = text.replace("/+","/joinchat/")
                if target[0:13] != "https://t.me/":
                    message.reply_html(text="❌ گروه مقصد غیر معتبر")
                else:
                    cs.execute(f"UPDATE {utl.gtg} SET destination='{text}' WHERE id={row_gtg['id']}")
                    cs.execute(f"UPDATE {utl.users} SET step='create_order_file;info;{row_gtg['id']}' WHERE user_id='{from_id}'")
                    bot.send_document(
                        chat_id=from_id,
                        document=open(f"{directory}/files/list-members.txt", "rb"),
                        caption="لیست اعضا را ارسال کنید:\n\n"+
                            "❕ مطابق نمونه باید یک فایل txt ارسال کنید که هر یوزرنیم در یک خط آن باشد.",
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(utl.menu_var)]])
                    )
        elif ex_step[1] == 'info':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={int(ex_step[2])}")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                message.reply_html(text="❌ سفارش یافت نشد.")
            elif not message.document:
                message.reply_html(text="❌ لطفا یک فایل txt ارسال کنید.")
            else:
                info_msg = message.reply_html(text="در حال بررسی فایل ...")
                try:
                    list_members = []
                    path = f"files/id-{row_gtg['id']}.txt"
                    info_action = bot.get_file(message.document.file_id)
                    with open(path, "wb") as file:
                        file.write(requests.get(info_action.file_path).content)
                    with open(path, "rb") as file:
                        result = file.read().splitlines()
                        for value in result:
                            value = value.decode('utf8')
                            if value == "" or len(value) < 5:
                                continue
                            elif value[0:1] != "@":
                                value = f"@{value}"
                            if not value in list_members:
                                list_members.append(value)
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
                    for value in list_members:
                        utl.insert(cs, f"INSERT INTO {utl.analyze} (gtg_id,username,is_real,created_at) VALUES ('{row_gtg['id']}','{value}','1','{timestamp}')")
                    
                    cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_bad=0")
                    count = cs.fetchone()['count_stats']
                    cs.execute(f"UPDATE {utl.gtg} SET max_users='{count}',count='{count}' WHERE id={row_gtg['id']}")

                    bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
                    info_msg = message.reply_html(text="در حال بررسی ...")
                    cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                    os.system(f"python tl.analyze.py {from_id} order_file {row_gtg['id']}")
                    bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
                except Exception as e:
                    message.reply_html(text="❌ مشکلی در آنالیز فایل پیش آمد.")
        elif ex_step[1] == 'type_users':
            cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={int(ex_step[2])}")
            row_gtg = cs.fetchone()
            if row_gtg is None:
                message.reply_html(text="❌ سفارش یافت نشد")
            else:
                info_msg = message.reply_html(text="در حال پیکربندی...")
                if text == 'همه کاربران':
                    type_users = 'users_all'
                elif text == 'کاربران واقعی':
                    type_users = 'users_real'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0 AND is_real=0")
                elif text == 'کاربران فیک':
                    type_users = 'users_fake'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0 AND is_fake=0")
                elif text == 'کاربران آنلاین':
                    type_users = 'users_online'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0 AND is_online=0")
                elif text == 'کاربران دارای شماره':
                    type_users = 'users_has_phone'
                    cs.execute(f"DELETE FROM {utl.analyze} WHERE is_bad=0 AND is_phone=0")
                else:
                    return message.reply_html(text="❌ صرفا از منو انتخاب کنید")
                cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.analyze} WHERE is_bad=0")
                max_users = cs.fetchone()['count_stats']
                cs.execute(f"UPDATE {utl.gtg} SET status='doing',max_users='{max_users}',type_users='{type_users}',created_at='{timestamp}',updated_at='{timestamp}' WHERE id={row_gtg['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                user_panel(update,
                    text=f"✅ سفارش با موفقیت ثبت شد و در حال انجام است\n\n"+
                    f"♻️ /gtg_{row_gtg['id']}"
                )
                bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
    elif ex_step[0] == 'analyze':
        uniq_id = utl.uniq_id_generate(cs,10,utl.egroup)
        text = text.replace("/+","/joinchat/")
        cs.execute(f"INSERT INTO {utl.egroup} (user_id,link,created_at,updated_at,uniq_id) VALUES ({from_id},'{text}','{timestamp}','{timestamp}','{uniq_id}')")
        cs.execute(f"SELECT * FROM {utl.egroup} WHERE uniq_id='{uniq_id}'")
        row_egroup = cs.fetchone()
        cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
        
        info_msg = message.reply_html(text="در حال بررسی ...")
        os.system(f"python tl.analyze.py {from_id} analyze {row_egroup['id']}")
        bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
        user_panel(update)
        return
    elif ex_step[0] == 'add_api':
        try:
            ex_nl_text = text.split("\n")
            if len(ex_nl_text[0]) > 200 or len(ex_nl_text[1]) > 200 or len(ex_nl_text) != 2:
                message.reply_html(text="❌ ورودی نادرست")
            else:
                if not re.findall('^[0-9]*$', ex_nl_text[0]):
                    message.reply_html(text="‏❌ api id اشتباه است!")
                elif not re.findall('^[0-9-a-z-A-Z]*$', ex_nl_text[1]):
                    message.reply_html(text="‏❌ api hash اشتباه است!")
                else:
                    api_id = ex_nl_text[0]
                    api_hash = ex_nl_text[1]
                    cs.execute(f"SELECT * FROM {utl.apis} WHERE api_id='{api_id}' OR api_hash='{api_hash}'")
                    if cs.fetchone() is not None:
                        message.reply_html(text="❌ این api قبلا ثبت شده")
                    else:
                        cs.execute(f"INSERT INTO {utl.apis} (api_id,api_hash) VALUES ('{api_id}','{api_hash}')")
                        cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
                        user_panel(update, "✅ با موفقیت افزوده شد")
        except:
            message.reply_html(text="❌ طبق نمونه ارسال کنید")
        return 
    elif ex_step[0] == 'sendmsg':
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{ex_step[1]}'")
        row_user_select = cs.fetchone()
        if row_user_select is None:
            message.reply_html(text=f"❌ کاربر یافت نشد")
        else:
            try:
                if update.message.text:
                    bot.send_message(chat_id=chat_id,disable_web_page_preview=True,parse_mode='HTML',
                    text=f"📧️ پیام جدید از طرف پشتیبانی\n——————————————————\n{txtcap}"
                )
                elif update.message.photo:
                    bot.send_photo(chat_id=chat_id,parse_mode='HTML',
                        photo=update.message.photo[len(update.message.photo) - 1].file_id,
                        caption=f"📧️ پیام جدید از طرف پشتیبانی\n——————————————————\n{txtcap}"
                    )
                elif update.message.video:
                    bot.send_video(chat_id=chat_id,parse_mode='HTML',
                        video=update.message.video.file_id,
                        caption=f"📧️ پیام جدید از طرف پشتیبانی\n——————————————————\n{txtcap}"
                    )
                elif update.message.audio:
                    bot.send_audio(chat_id=chat_id,parse_mode='HTML',
                        audio=update.message.audio.file_id,
                        caption=f"📧️ پیام جدید از طرف پشتیبانی\n——————————————————\n{txtcap}"
                    )
                elif update.message.voice:
                    bot.send_voice(chat_id=chat_id,parse_mode='HTML',
                        voice=update.message.voice.file_id,
                        caption=f"📧️ پیام جدید از طرف پشتیبانی\n——————————————————\n{txtcap}"
                    )
                elif update.message.document:
                    bot.send_document(chat_id=chat_id,parse_mode='HTML',
                        document=update.message.document.file_id,
                        caption=f"📧️ پیام جدید از طرف پشتیبانی\n——————————————————\n{txtcap}"
                    )
                else:
                    return message.reply_html(text="⛔️ پیام پشتیبانی نمی شود")
                cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id='{from_id}'")
                message.reply_html(text="✅ پیام با موفقیت ارسال شد")
            except:
                message.reply_html(text="❌ مشکلی در ارسال پیام رخ داد")
        return
    
    if text == '📚 راهنما 📚':
        return message.reply_html(
            text="📚 راهنمای ربات\n\n"+
                "1️⃣ بخش تنظیمات:\n"+
                "+ در هر ای پی ای x شماره ثبت شود\n"+
                "❕ هر چقدر این عدد کم باشد بهتر است (برای کاهش میزان بن شدن اکانت ها)\n\n"+
                "+ هر اکانت در هر استفاده x اد کند\n"+
                "❕ تعیین میکنید که هر اکانت موقع استفاده شدن چقدر اد کند\n\n"+
                "+ هر اکانت هر x ساعت استفاده شود\n"+
                "❕ تعیین میکنید هر اکانت هر چند ساعت استفاده شود (در بخش آمار اکانت های قابلیت اد)\n\n"+
                "+ اکانت موقع رسیدن به اسپم x روز استراحت کند\n"+
                "❕ با فعال کردن این مورد وقتی که یک اکانت اسپم تلگرام را دریافت کرد به مدت مشخص شده استراحت میکند\n\n"+
                "+ تغییر/تنظیم پسورد دو مرحله ای\n"+
                "❕ با فعال کردن این مورد پسود دو مرحله ای اکانت ها تنظیم یا عوض خواهد شد\n\n"+
                "+ خروج از بقیه سشن ها\n"+
                "❕ با فعال کردن این مورد بقیه سشن های اکانت لاگ اوت خواهند شد\n\n"+
                "+ تنظیم نام، بیو و پروفایل\n"+
                "❕ با فعال کردن این مورد ربات بطور خودکار برای اکانت هایی که اضافه میکنید نام، بیو و عکس تنظیم میکند\n\n"+
                "+ اکانت ها گروه ها را ترک کنند\n"+
                "❕ با فعال کردن این مورد اکانت ها هر چند روز یکبار خودکار از گروه ها لفت می دهند\n\n"+
                "+ حذف خودکار اکانت های ثبت نشده\n"+
                "❕ با فعال کردن این گزینه اکانت های ثبت نشده خودکار از ربات حذف خواهند شد\n\n"+
                "+ دسترسی همه به شناسه سفارش\n"+
                "❕ با فعال کردن این گزینه همه به جزئیات سفارش دسترسی خواهند داشت (مثال /gtg_x)\n\n"+
                "+ نوع آنالیز\n"+
                "❕ نوع آنالیز دیتابیس از اطلاعات ثبت شده در دیتابیس استفاده می کند و آنالیز لحظه ای در لحظه همه اکانت های تکراری دو گروه سفارش را شناسایی می کند\n"+
                "❕ سرعت آنالیز دیتابیس بیشتر است\n\n"+
                "+ نوع اد\n"+
                "❕ نوع عادی یک به یک اکانت ها را بررسی میکند و نوع حرفه ای با هم بررسی میکند\n"+
                "❕ سرعت اد حرفه ای 10 تا 15 برابر بیشتر از عادی است\n\n"+
                "2️⃣ آنالیز:\n"+
                "❕ در این بخش میتوانید گروه خود را آنالیز کنید\n\n"+
                "3️⃣ ایجاد سفارش:\n"+
                "❕ در این بخش ابتدا سفارش خود را ثبت کنید و صبر کنید تا آنالیز تمام شود. بعد از اتمام آنالیز هر کدام از اعضا که میخواهید را از منو انتخاب کنید تا سفارش شما ثبت شود\n\n"+
                "4️⃣ افزودن اکانت:\n"+
                "❕ شماره خود را همراه با پیش شماره ارسال کنید و بقیه مراحل را ادامه دهید تا اکانت ثبت شود\n\n"+
                "5️⃣ افزودن api:\n"+
                "❕ ای پی ای را سایت تلگرام my.telegram.org دریافت کنید و ثبت کنید\n\n"+
                "➖➖➖➖➖➖\n"+
                "📌 دستورات:\n"+
                "- مشاهده / ویرایش جزئیات کاربر 👇👇\n"+
                f"/d_{from_id}\n"+
                "- افزودن اکانت از طریق سشن 👇👇\n"+
                f"❕ جهت انجام اینکار ابتدا سشن هایی که میخواهید در دایرکتوری import در هاست آپلود کنید و سپس دستور زیر را در ربات ارسال کنید.\n"+
                f"/import\n"+
                "➖➖➖➖➖➖\n"+
                "⚠️ نکات مهم:\n"+
                "‼️ اگر از هاست استفاده میکنید از نوع اد حرفه ای استفاده نکنید\n\n"+
                "‼️ دقت کنید که اگر از دستور /import استفاده می کنید، باید سشن تلتون باشد\n\n"+
                "‼️ هر چقدر تعداد api بیشتری در ربات اد کنید و در تنظیمات \"در هر ای پی ای x شماره ثبت شود\" را کمتر کنید، طول عمر کانت ها بیشتر خواهد شد\n\n"+
                "‼️ بهتر از گزینه \"هر اکانت هر x ساعت استفاده شود\" را در تنظیمات روی 24 ساعت تنظیم کنید",
        )
    elif text == '➕ افزودن اکانت':
        row_apis = utl.select_api(cs,row_admin['api_per_number'])
        if row_apis is None:
            message.reply_html(text="❌ هیچ Api ای یافت نشد")
        else:
            cs.execute(f"UPDATE {utl.users} SET step='add_acc;phone' WHERE user_id='{from_id}'")
            message.reply_html(
                text="شماره را مانند نمونه زیر و همراه کد کشور ارسال کنید:\n\n"+
                    "989331234567",
                reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
            )
        return
    elif text == '➕ ایجاد سفارش':
        cs.execute(f"SELECT * FROM {utl.gtg} WHERE status NOT IN ('end')")
        row_gtg = cs.fetchone()
        if row_gtg is not None:
            message.reply_html(text="❌ سفارش فعال وجود دارد")
        else:
            message.reply_html(
                text="نوع سفارش گروه به گروه را انتخاب کنید:",
                reply_markup={'resize_keyboard': True,'keyboard': [
                    [{'text': '🔴 با لینک گروه 🔴'}],
                    [{'text': '🔵 با لیست اعضا 🔵'}],
                    [{'text': utl.menu_var}]
                ]}
            )
        return
    elif text == '🔴 با لینک گروه 🔴':
        cs.execute(f"SELECT * FROM {utl.gtg} WHERE status NOT IN ('end')")
        row_gtg = cs.fetchone()
        if row_gtg is not None:
            message.reply_html(text="❌ سفارش فعال وجود دارد")
        else:
            limit_per_h = row_admin['limit_per_h'] * 3600
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp} ORDER BY last_order_at ASC")
            if cs.fetchone() is None:
                message.reply_html(text="❌ اکانتی برای انجام سفارش یافت نشد")
            else:
                cs.execute(f"UPDATE {utl.users} SET step='create_order;info' WHERE user_id='{from_id}'")
                message.reply_html(disable_web_page_preview=True,
                    text="اطلاعات را به این شکل و در سه خط ارسال کنید:\n\n"+
                        "لینک گروه مبدا\n"+
                        "لینک گروه مقصد\n"+
                        "تعداد اعضا برای انتقال\n\n"+
                        "مثال:\n" +
                        "https://t.me/source\n" +
                        "https://t.me/target\n" +
                        "500\n\n" +
                        "❗️ اعضای گروه مبدا به گروه مقصد منتقل می شوند",
                    reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                )
        return
    elif text == '🔵 با لیست اعضا 🔵':
        cs.execute(f"SELECT * FROM {utl.gtg} WHERE status NOT IN ('end')")
        row_gtg = cs.fetchone()
        if row_gtg is not None:
            message.reply_html(text="❌ سفارش فعال وجود دارد")
        else:
            limit_per_h = row_admin['limit_per_h'] * 3600
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                message.reply_html(text="❌ اکانتی برای انجام سفارش یافت نشد")
            else:
                uniq_id = utl.uniq_id_generate(cs,10,utl.gtg)
                cs.execute(f"INSERT INTO {utl.gtg} (user_id,created_at,updated_at,uniq_id) VALUES ('{from_id}','{timestamp}','{timestamp}','{uniq_id}')")
                cs.execute(f"SELECT * FROM {utl.gtg} WHERE uniq_id='{uniq_id}'")
                row_gtg = cs.fetchone()
                if row_gtg is None:
                    message.reply_html(text="❌ مشکلی پیش آمده، دوباره تلاش کنید.")
                else:
                    cs.execute(f"UPDATE {utl.users} SET step='create_order_file;destination;{row_gtg['id']}' WHERE user_id='{from_id}'")
                    message.reply_html(
                        text="لینک گروه مقصد را ارسال کنید:\n\n"+
                            "مثال:\n" +
                            "https://t.me/target",
                        disable_web_page_preview=True,
                        reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
                    )
        return
    elif text == '🔮 آنالیز گروه 🔮':
        cs.execute(f"SELECT * FROM {utl.mbots} WHERE status='submitted'")
        row_mbots = cs.fetchone()
        if row_mbots is not None:
            cs.execute(f"UPDATE {utl.users} SET step='analyze;' WHERE user_id='{from_id}'")
            message.reply_html(
                text="لینک گروه را ارسال کنید:\n\n"+
                "❗️ لینک عضویت دائمی گروه را وارد کنید نه لینک موقت یا عضویت محدود",
                reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
            )
        else:
            message.reply_html(text="❌ اکانتی برای انجام سفارش یافت نشد")
        return
    elif text == '➕ افزودن api':
        cs.execute(f"UPDATE {utl.users} SET step='add_api;' WHERE user_id='{from_id}'")
        message.reply_html(
            text="اطلاعات را به این شکل و در دو خط ارسال کنید:\n\n"+
                "api id\n"+
                "api hash",
            reply_markup={'resize_keyboard': True,'keyboard': [[{'text': utl.menu_var}]]}
        )
        return
    elif text == "⚙️ تنظیمات ⚙️":
        time_spam_restrict = int(row_admin['time_spam_restrict'] / 86400)
        change_pass = "✅ تغییر/تنظیم پسورد دو مرحله ای ✅" if row_admin['change_pass'] else "❌ تغییر/تنظیم پسورد دو مرحله ای ❌"
        exit_session = "✅ خروج از بقیه سشن ها ✅" if row_admin['exit_session'] else "❌ خروج از بقیه سشن ها ❌"
        is_change_profile = "✅ تنظیم نام، بیو و پروفایل ✅" if row_admin['is_change_profile'] else "❌ تنظیم نام، بیو و پروفایل ❌"
        is_set_username = "✅ تنظیم یوزرنیم ✅" if row_admin['is_set_username'] else "❌ تنظیم یوزرنیم ❌"
        leave_per = "✅ اکانت ها گروه ها را ترک کنند ✅" if row_admin['leave_per'] else "❌ اکانت ها گروه ها را ترک کنند ❌"
        delete_first_levels = "✅ حذف خودکار اکانت های ثبت نشده ✅" if row_admin['delete_first_levels'] else "❌ حذف خودکار اکانت های ثبت نشده ❌"
        gtg_per = "✅ دسترسی همه به شناسه سفارش ✅" if row_admin['gtg_per'] else "❌ دسترسی همه به شناسه سفارش ❌"
        type_analyze = "نوع آنالیز سفارش: لحظه ای" if row_admin['type_analyze'] else "نوع آنالیز سفارش: دیتابیس"
        type_add = "نوع اد: حرفه ای" if row_admin['type_add'] else "نوع اد: عادی"
        
        message.reply_html(text=f"پنل تنظیمات:",
            reply_markup={'inline_keyboard': [
                [{'text': f"در هر ای پی ای {row_admin['api_per_number']} شماره ثبت شود",'callback_data': f"settings;api_per_number;guide"}],
                [
                    {'text': '+10','callback_data': f"settings;api_per_number;+10"},
                    {'text': '+5','callback_data': f"settings;api_per_number;+5"},
                    {'text': '+1','callback_data': f"settings;api_per_number;+1"},
                    {'text': '-1','callback_data': f"settings;api_per_number;-1"},
                    {'text': '-5','callback_data': f"settings;api_per_number;-5"},
                    {'text': '-10','callback_data': f"settings;api_per_number;-10"},
                ],
                [{'text': f"هر اکانت در هر استفاده {row_admin['add_per_h']} اد کند",'callback_data': f"settings;add_per_h;guide"}],
                [
                    {'text': '+10','callback_data': f"settings;add_per_h;+10"},
                    {'text': '+5','callback_data': f"settings;add_per_h;+5"},
                    {'text': '+1','callback_data': f"settings;add_per_h;+1"},
                    {'text': '-1','callback_data': f"settings;add_per_h;-1"},
                    {'text': '-5','callback_data': f"settings;add_per_h;-5"},
                    {'text': '-10','callback_data': f"settings;add_per_h;-10"},
                ],
                [{'text': f"هر اکانت هر {row_admin['limit_per_h']} ساعت استفاده شود",'callback_data': f"settings;limit_per_h;guide"}],
                [
                    {'text': '+10','callback_data': f"settings;limit_per_h;+10"},
                    {'text': '+5','callback_data': f"settings;limit_per_h;+5"},
                    {'text': '+1','callback_data': f"settings;limit_per_h;+1"},
                    {'text': '-1','callback_data': f"settings;limit_per_h;-1"},
                    {'text': '-5','callback_data': f"settings;limit_per_h;-5"},
                    {'text': '-10','callback_data': f"settings;limit_per_h;-10"},
                ],
                [{'text': f"اکانت موقع رسیدن به اسپم {time_spam_restrict} روز استراحت کند",'callback_data': f"settings;time_spam_restrict;guide"}],
                [
                    {'text': '+10','callback_data': f"settings;time_spam_restrict;+10"},
                    {'text': '+5','callback_data': f"settings;time_spam_restrict;+5"},
                    {'text': '+1','callback_data': f"settings;time_spam_restrict;+1"},
                    {'text': '-1','callback_data': f"settings;time_spam_restrict;-1"},
                    {'text': '-5','callback_data': f"settings;time_spam_restrict;-5"},
                    {'text': '-10','callback_data': f"settings;time_spam_restrict;-10"},
                ],
                [{'text': change_pass,'callback_data': f"settings;change_pass;guide"}],
                [{'text': exit_session,'callback_data': f"settings;exit_session;guide"}],
                [{'text': is_change_profile,'callback_data': f"settings;is_change_profile;guide"}],
                [{'text': is_set_username,'callback_data': f"settings;is_set_username;guide"}],
                [{'text': leave_per,'callback_data': f"settings;leave_per;guide"}],
                [{'text': delete_first_levels,'callback_data': f"settings;delete_first_levels;guide"}],
                [{'text': gtg_per,'callback_data': f"settings;gtg_per;guide"}],
                [{'text': type_analyze,'callback_data': f"settings;type_analyze;guide"}],
                [{'text': type_add,'callback_data': f"settings;type_add;guide"}],
            ]}
        )
        return
    elif text == '📊 آمار 📊':
        now = jdatetime.datetime.now()
        time_today = jdatetime.datetime(day = now.day,month = now.month,year = now.year).timestamp()
        time_yesterday = time_today - 86400
        
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.gtg}")
        orders_count_all = cs.fetchone()['count_stats']
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.gtg} WHERE created_at>={time_today}")
        orders_count_today = cs.fetchone()['count_stats']
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.gtg} WHERE created_at<{time_today} AND created_at>={time_yesterday}")
        orders_count_yesterday = cs.fetchone()['count_stats']
        
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.moveds} WHERE status='join'")
        orders_count_moved_all = cs.fetchone()['count_stats']
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.moveds} WHERE created_at>={time_today} AND status='join'")
        orders_count_moved_today = cs.fetchone()['count_stats']
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.moveds} WHERE created_at<{time_today} AND created_at>={time_yesterday} AND status='join'")
        orders_count_moved_yesterday = cs.fetchone()['count_stats']
        
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.mbots}")
        accs_all = cs.fetchone()['count_stats']
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.mbots} WHERE status='submitted'")
        accs_active = cs.fetchone()['count_stats']
        limit_per_h = row_admin['limit_per_h'] * 3600
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.mbots} WHERE status='submitted' AND (last_order_at+{limit_per_h})<{timestamp}")
        accs_ability_ad = cs.fetchone()['count_stats']
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.mbots} WHERE status='restrict'")
        accs_restrict = cs.fetchone()['count_stats']
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.mbots} WHERE status='first_level'")
        accs_first_level = cs.fetchone()['count_stats']
        
        cs.execute(f"SELECT COUNT(*) as count_stats FROM {utl.apis}")
        apis_count_all = cs.fetchone()['count_stats']
        message.reply_html(
            text="📊 آمار\n\n"+
                "🛍 سفارشات:\n"+
                f"🟢 امروز: {orders_count_today} ({orders_count_moved_today:,})\n"+
                f"⚪️ دیروز: {orders_count_yesterday} ({orders_count_moved_yesterday:,})\n"+
                f"🔴 کل: {orders_count_all} ({orders_count_moved_all:,})\n\n"+
                "🤖 اکانت ها:\n"+
                f"💢️️ کل: {accs_all}\n"+
                f"✅️ فعال: {accs_active}\n"+
                f"♻️️ قابلیت اد: {accs_ability_ad}\n"+
                f"⚠️ محدود شده: {accs_restrict}\n\n"+
                f"⛔️ ثبت نشد: {accs_first_level}\n\n"+
                f"🔘 تعداد api ها: {apis_count_all}"
        )
        return
    elif text == '📋 سفارشات':
        cs.execute(f"SELECT * FROM {utl.gtg} ORDER BY id DESC LIMIT 0,{step_page}")
        result = cs.fetchall()
        if not result:
            message.reply_html(text="❌ لیست خالی است")
        else:
            output = ""
            i = 1
            for row in result:
                created_at = jdatetime.datetime.fromtimestamp(row['created_at'])
                output += f"{i}. /gtg_{row['id']}\n"
                output += f"🔹️ Source: {row['origin']}\n"
                output += f"🔹️ Destination: {row['destination']}\n"
                output += f"🔹️ Done/Requested: [{row['count_moved']}/{row['count']}]\n"
                output += f"🔹️ Status: {utl.status_gtg[row['status']]}\n"
                output += f"📅️ {created_at.strftime('%Y/%m/%d %H:%M')}\n\n"
                i += 1
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.gtg}")
            rowcount = cs.fetchone()['count']
            output = f"📜 لیست سفارشات ({rowcount})\n\n{output}"
            ob = Pagination(update,"orders",output,step_page,rowcount)
            ob.processMessage()
        return
    elif text == '📋 اکانت ها':
        cs.execute(f"SELECT * FROM {utl.mbots} ORDER BY id DESC LIMIT 0,{step_page}")
        result = cs.fetchall()
        if not result:
            message.reply_html(text="❌ لیست خالی است")
        else:
            message.reply_html(
                text="مشاهده لیست اکانت ها در وضعیت های مختلف:",
                reply_markup={'inline_keyboard': [
                    [
                        {'text': "💢 همه 💢", 'callback_data': f"pg;accounts;1"},
                    ],
                    [
                        {'text': "⛔️ ثبت نشده", 'callback_data': f"pg;first_level;1"},
                        {'text': "❌ محدود شده", 'callback_data': f"pg;restrict;1"}
                    ],
                    [
                        {'text': "♻️ قابلیت اد", 'callback_data': f"pg;adability;1"},
                        {'text': "✅ فعال", 'callback_data': f"pg;submitted;1"}
                    ]
                ]}
            )
        return
    elif text == '📋 لیست api ها':
        cs.execute(f"SELECT * FROM {utl.apis} ORDER BY id DESC LIMIT 0,{step_page}")
        result = cs.fetchall()
        if not result:
            message.reply_html(text="❌ لیست خالی است")
        else:
            output = ""
            i = 1
            for row in result:
                output += f"🔴️ Api ID: <code>{row['api_id']}</code>\n"
                output += f"🔴️ Api Hash: <code>{row['api_hash']}</code>\n"
                output += f"🔴️ Delete: /dela_{row['id']}\n\n"
                i += 1
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
            rowcount = cs.fetchone()['count']
            output = f"📜 لیست ای پی ای ها ({rowcount})\n\n{output}"
            ob = Pagination(update,"apis",output,step_page,rowcount)
            ob.processMessage()
        return
    elif text == '/import':
        info_msg = message.reply_html(text="در حال بررسی ...")
        os.system(f"python tl.import.py {from_id}")
        bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
        user_panel(update, "✅ عملیات ایپمورت سشن ها پایان یافت.")
        return
    elif ex_text[0] == '/status':
        mbots_id = int(ex_text[1])
        cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={mbots_id}")
        row_mbots = cs.fetchone()
        if row_mbots is None:
            message.reply_html(text="❌ یافت نشد")
        else:
            info_msg = message.reply_html(text="در حال بررسی ...")
            os.system(f"python tl.account.py {from_id} check {row_mbots['id']}")
            cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id='{from_id}'")
            bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
            message.reply_html(text=f"حذف اکانت: /delete_{row_mbots['id']}")
        return
    elif ex_text[0] == '/delete':
        mbots_id = int(ex_text[1])
        cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={mbots_id}")
        row_mbots = cs.fetchone()
        if row_mbots is None:
            message.reply_html(text="❌ یافت نشد")
        else:
            message.reply_html(
                reply_to_message_id=message_id,
                text=f"❌ حذف اکانت: {row_mbots['phone']}\n\n"+
                f"/deleteconfirm_{ex_text[1]}"
            )
        return
    elif ex_text[0] == '/deleteconfirm':
        mbots_id = int(ex_text[1])
        cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={mbots_id}")
        row_mbots = cs.fetchone()
        if row_mbots is None:
            message.reply_html(text="❌ یافت نشد")
        else:
            try:
                cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots['id']}")
                os.remove(f"{directory}/sessions/{row_mbots['phone']}.session")
            except:
                pass
            message.reply_html(text=f"✅ با موفقیت حذف شد")
        return
    elif ex_text[0] == '/exgroup':
        cs.execute(f"SELECT * FROM {utl.egroup} WHERE chat_id='-{ex_text[1]}' AND status='end' ORDER BY id DESC")
        result = cs.fetchall()
        if not result or result is None:
            message.reply_html(text="❌ هیچ آنالیزی روی این گروه انجام نشده.")
        else:
            i = 1
            output = ""
            for row in result:
                output += f"{i}. /ex_{row['id']}\n"
                i += 1
            message.reply_html(
                text="♨️ آنالیز های انجام شده از این گروه\n\n" + output
            )
        return
    elif ex_text[0] == '/ex':
        cs.execute(f"SELECT * FROM {utl.egroup} WHERE id={int(ex_text[1])}")
        row_egroup = cs.fetchone()
        if row_egroup is None:
            message.reply_html(text="❌ یافت نشد")
        else:
            try:
                type = ex_text[2]
                info_msg = message.reply_html(text="در حال ارسال ...")
                try:
                    if type == 'a':
                        bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_all.txt","rb"),caption='کاربران شناسایی شده')
                    elif type == 'u':
                        bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_real.txt","rb"),caption='کاربران شناسایی شده (واقعی)')
                    elif type == 'f':
                        bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_fake.txt","rb"),caption='کاربران شناسایی شده (فیک)')
                    elif type == 'n':
                        bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_has_phone.txt","rb"),caption='کاربران شناسایی شده (دارای شماره)')
                    elif type == 'o':
                        bot.send_document(chat_id=chat_id,document=open(f"{directory}/export/{row_egroup['id']}/users_online.txt","rb"),caption='کاربران شناسایی شده (آنلاین)')
                except:
                    message.reply_html(text="❌ مشکلی در آپلود فایل پیش آمد.")
            except:
                message.reply_html(
                    text=f"🔻 شناسه: <code>{chat_id}</code> (/exgroup_{row_egroup['chat_id'][1:]})\n"+
                        f"🔻 لینک: {row_egroup['link']}\n"+
                        f"🔻 کل کاربران: {row_egroup['participants_count']:,}\n"+
                        f"🔻 کاربران آنلاین: {row_egroup['participants_online_count']:,}\n"+
                        f"🔻 ربات ها: {row_egroup['participants_bot_count']}\n"+
                        "‏————————————————————\n"+
                        "♻️ کاربران شناسایی شده (دارای یوزرنیم):\n"+
                        f"🔻 همه کاربران: {(row_egroup['users_real'] + row_egroup['users_fake']):,} (/ex_{row_egroup['id']}_a)\n"+
                        f"🔻 کاربران واقعی: {row_egroup['users_real']:,} (/ex_{row_egroup['id']}_u)\n"+
                        f"🔻 کاربران فیک: {row_egroup['users_fake']:,} (/ex_{row_egroup['id']}_f)\n"+
                        f"🔻 کاربران داری شماره: {row_egroup['users_has_phone']:,} (/ex_{row_egroup['id']}_n)\n"+
                        f"🔻 کاربران آنلاین: {row_egroup['users_online']:,} (/ex_{row_egroup['id']}_o)\n\n"+
                        "‼️ اگر روی دکمه های داخل پرانتز کلیک کنید خروجی اون کاربر هارو بهت میدم.\n"+
                        f"⏰ مدت زمان: {int(time.time()) - timestamp} ثانیه\n‏",
                    disable_web_page_preview=True,
                )
            bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
        return
    elif ex_text[0] == '/exo':
        cs.execute(f"SELECT * FROM {utl.gtg} WHERE id={int(ex_text[1])}")
        row_gtg = cs.fetchone()
        if row_gtg is None:
            message.reply_html(text="❌ یافت نشد")
        else:
            try:
                if row_gtg['status'] == 'start':
                    message.reply_html(text="❌ سفارش هنوز شروع نشده")
                else:
                    type = ex_text[2]
                    list_users = ""
                    path = f"{directory}/files/exo_{row_gtg['id']}_{type}.txt"
                    info_msg = message.reply_html(text="در حال ارسال ...")
                    if type == 'm':
                        cs.execute(f"SELECT * FROM {utl.moveds} WHERE gtg_id={row_gtg['id']} AND status='join'")
                        result = cs.fetchall()
                        if not result:
                            return message.reply_html(text="❌ هیچ کاربری یافت نشد.")
                        else:
                            for row in result:
                                list_users += f"{row['username']}\n"
                            utl.write_on_file(path, list_users)
                        bot.send_document(chat_id=chat_id,document=open(path, "rb"),caption='کاربران انتقال داده شده')
                    elif type == 'e':
                        cs.execute(f"SELECT * FROM {utl.reports} WHERE gtg_id={row_gtg['id']} AND status='error'")
                        result = cs.fetchall()
                        if not result:
                            return message.reply_html(text="❌ هیچ کاربری یافت نشد.")
                        else:
                            for row in result:
                                list_users += f"{row['username']}\n"
                            utl.write_on_file(path, list_users)
                        bot.send_document(chat_id=chat_id,document=open(path,"rb"),caption='کاربران مشکل دار')
                    elif type == 'r':
                        cs.execute(f"SELECT * FROM {utl.analyze} WHERE gtg_id={row_gtg['id']} AND is_bad=0")
                        result_analyze = cs.fetchall()
                        if not result_analyze:
                            if not os.path.exists(path):
                                return message.reply_html(text="❌ هیچ کاربری یافت نشد.")
                        else:
                            for row in result_analyze:
                                list_users += f"{row['username']}\n"
                            utl.write_on_file(f"{directory}/files/exo_{row_gtg['id']}_r.txt", list_users)
                        bot.send_document(chat_id=chat_id,document=open(path, "rb"),caption='کاربران باقی مانده')
            except:
                message.reply_html(text="❌ مشکلی پیش آمد.")
            finally:
                bot.delete_message(chat_id=from_id,message_id=info_msg.message_id)
        return
    elif ex_text[0] == '/dela':
        apis_id = int(ex_text[1])
        cs.execute(f"SELECT * FROM {utl.apis} WHERE id={apis_id}")
        row_apis = cs.fetchone()
        if row_apis is None:
            message.reply_html(text="❌ یافت نشد")
        else:
            message.reply_html(
                reply_to_message_id=message_id,
                text=f"❌ حذف ای پی ای: {row_apis['api_id']}\n\n"+
                f"/delaconfirm_{ex_text[1]}"
            )
        return
    elif ex_text[0] == '/delaconfirm':
        apis_id = int(ex_text[1])
        cs.execute(f"SELECT * FROM {utl.apis} WHERE id={apis_id}")
        row_apis = cs.fetchone()
        if row_apis is None:
            message.reply_html(text="❌ یافت نشد")
        else:
            cs.execute(f"DELETE FROM {utl.apis} WHERE id={row_apis['id']}")
            message.reply_html(text=f"✅ با موفقیت حذف شد")
        return
    elif ex_text[0] == "/d":
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id='{ex_text[1]}'")
        row_user_select = cs.fetchone()
        if row_user_select is None:
            message.reply_html(text=f"❌ کاربر یافت نشد")
        else:
            if row_user_select['status'] == "block":
                block = 'بلاک ✅'
                block_status = "user"
            else:
                block = 'بلاک ❌'
                block_status = "block"
            if row_user_select['status'] == "admin":
                admin = 'ادمین ✅'
                admin_status = "user"
            else:
                admin = 'ادمین ❌'
                admin_status = "admin"
            message.reply_html(text=f"کاربر <a href='tg://user?id={row_user_select['user_id']}'>{row_user_select['user_id']}</a> (/d_{row_user_select['user_id']})",
                reply_markup={'inline_keyboard': [
                    [{'text': "ارسال پیام",'callback_data': f"d;{row_user_select['user_id']};sendmsg"}],
                    [
                        {'text': block,'callback_data': f"d;{row_user_select['user_id']};{block_status}"},
                        {'text': admin,'callback_data': f"d;{row_user_select['user_id']};{admin_status}"}
                    ]
                ]}
            )
        return
        

if __name__ == '__main__':
    updater = Updater(utl.token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.chat_type.private & Filters.update.message & Filters.update, private_process, run_async=True))
    dispatcher.add_handler(CallbackQueryHandler(callbackquery_process, run_async=True))
    
    # updater.start_polling(drop_pending_updates=True)
    updater.start_polling()
    updater.idle()
