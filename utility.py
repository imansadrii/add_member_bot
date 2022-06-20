import random
import string
import telegram
from config import *

admini = 'agg_admin_wcxm3zshoatkpfrlutrshidcx84gon'
analyze = 'agg_analyze_6oipm3ndgkvykubegzsvrnexpx24ld'
apis = 'agg_apis_zyehay1fsqbd7npojvk0hlaku2goqu'
egroup = 'agg_export_bamc48pk2381zndh38pajd739cn57plq'
gtg = 'agg_gtg_nchw0128zn389xpw429qpdj38427tspa'
mbots = 'agg_mbots_a28cnsz83jcn38pqn849shg48wol4'
moveds = 'agg_moveds_21tkjud7b0xkwatigxefhzbqny4lvo'
reports = 'agg_reports_wierddxz8i2ltfus1cxm0uemoovqpr'
users = 'agg_users_hc137znsdyhy38qpsk47sj39palw379'


menu_var = '🏛 منو اصلی'
panel_var = '👨‍💻 پنل ادمین'
back_var = 'بازگشت 🔙'


bot = telegram.Bot(token=token)
get_me = bot.get_me()
bot_id = get_me.id
bot_username = get_me.username


status_mbots = {
    'first_level': 'waiting ⏳',
    'code': 'get password 📞',
    'password': 'get password 🛡',
    'submitted': 'active ✅',
    'restrict': 'restrict ⛔️',
    'expired': 'expired ❗️️'
}
status_gtg = {
    'start': 'waiting ❕️',
    'doing': 'doing ♻️',
    'end': 'completed ✅',
}


name_list = [
    'Arghavan',
    'Yaran',
    'Parmida',
    'Tara',
    'Samin',
    'Janan',
    'Chakameh',
    'Hadis',
    'Dayan',
    'Zakereh',
    'Roya',
    'Zari',
    'Sara',
    'Shadi',
    'Atefeh',
    'Ghazal',
    'Gasedak',
    'Amal',
    'Aneseh',
    'Atiyeh',
    'Ala',
    'Ayeh',
    'Ayat',
    'Aynoor',
    'Abtesam',
    'Aklil',
    'Akram',
    'Asena',
    'Amira',
    'Amaneh',
    'Amineh',
    'Asila',
    'Aroon',
    'Ima',
    'Asra',
    'Alhan',
    'Alisa',
    'Talia',
    'Tabarak',
    'Tabasom',
    'Taranom',
    'Taktam',
    'Tasnim',
    'Tina',
    'Sana',
    'Smr',
    'Samreh',
    'Samina',
    'Samineh',
    'Samin',
    'Jenan',
    'Hanipha',
    'Hanipheh',
    'Hoora',
    'Hooraneh',
    'Hareh',
    'Hamedeh',
    'Hadis',
    'Hadiseh',
    'Hakimeh',
    'Hosna',
    'Hosniyeh',
    'Hosna',
    'Hasiba',
    'Hamra',
    'Hemaseh',
    'Hana',
    'Hanan',
    'Hananeh',
    'Hoor Afarin',
    'Hoor Rokh',
    'Hoordis',
    'Hoorcad',
    'Hoori Dokht',
    'Hoorosh',
    'Hooriya',
    'Halma',
    'Heliya',
    'Heliyeh',
    'Khazar',
    'Dina',
    'Dorsa',
    'Rada',
    'Rahel',
    'Rafe',
    'Rayehe',
    'Rakeehe',
    'Rahil',
    'Rahmeh',
    'Raziyeh',
    'Rezvaneh',
    'Roman',
    'Roman',
    'Reyhan',
    'Reyhaneh',
    'Raniya',
    'Romisa',
    'Zamzam',
    'Zoofa',
    'Zeytoon',
]


about_list = [
    '🎐 اجـازه نـده هيـچ كس پـاشو رو رويـاهات بـذاره..🌱',
    'اگر از بلندای آسمان بترسی، نمی‌توانی مالکِ ماه شوی! 🌖✨',
    'ناشنوا باش وقتی کهـ به آرزوهای قشنگت میگن محالهـ💘🍀✨',
    '➰ تـو فقـط قسـمتی از مـن رو میشنـاسی؛ مـن یک جهـان پـر از رازم..🌱',
    'قهرمان خودت باش',
    'شآد بآشُــ بخَند:(♡بزار بفهمَـنـ قَوۍ تَر از دیروزۍ🌸',
    'هرچـے طوفآڹ زندگیـٺ بزرگـ تر باشهـ.... رنگیـڹ ڪموݧ بعدݜ قشنگ ترهـ🐾🌈',
    'مهم نیس پشت سرمون چی میگن مهم این ک تو رومون جرعت ندارن حرف بزنن👌🏿✋🏻',
    'تَنها شادیه زندگیم اینه کِه هیچکس نمیدونه در چه حد غـمگینـم🥀✨',
    'گاهی وقتا بهترین انتقام اینه که لبخند بزنی و بگذری ✨♥️',
    'Prove Yourself 🌵 to Yourself 🌵hot others',
    'خودت رو به خودت ثابت کن نه به دیگران',
    'بَرام هيچ حِسي شَبيعِ طُ نيست . .♡',
    'خودت باش مثه بقیه زیاده🕷🕸',
    'خدایا تو بساز توبسازی قشنگه...!',
    'سکوتـ قـوے تریـن فریاد استـ🎈',
    '👻 silence is the most powerful sceam',
    'طُ ماه مَن شو مَن بَر خَلاف زَمین دُورت میگردَم 🌚✨🌥',
    '🎐 روزهـای سخـت روزهـای بهتـر می‌سـازنـد☺️',
    'شاد باش اين دشمنت رو غمگين ميكنه:]',
    'شَرحی ِز حال و حالی زِ شَرح نیست🖤🥀',
    'من از اونام كه اگه دوستت داشته باشم دنيا مالِ تو ميشه :))',
    'وقتے ارزش واقعے خودت رو بفهمے، ديگہ بہ ڪسے تخفيف نميدے...',
    'When you realize Your worth youll stop giving people Discounts',
    'هزار تا رگ دارم هزار تا دوست❤ ولی یک شاهرگ دارم یک تک رفیق😍😍😍👭',
    'من همینم که هستم',
    'i am that i am',
    'همه چیز از یک رویاه شروع میشه💎',
    'Everything started from a dream💎',
    '🎐 هـمـه چـیـز درسـت میشـه..🌱',
]


username_list = [
    'mary',
    'jennifer',
    'elizabeth',
    'linda',
    'barbara',
    'susan',
    'margaret',
    'jessica',
    'dorothy',
    'sarah',
    'nancy',
    'betty',
    'lisa',
    'sandra',
    'helen',
    'ashley',
    'donna',
    'kimberly',
    'carol',
    'michelle',
    'emily',
    'amanda',
    'melissa',
    'deborah',
    'laura',
    'stephanie',
    'rebecca',
    'sharon',
    'kathleen',
    'cynthia',
    'ruth',
    'anna',
    'shirley',
    'amy',
    'angela',
    'virginia',
    'brenda',
    'pamela',
    'catherine',
    'nicole',
    'samantha',
    'dennis',
    'diane'
]


def read_file(name):
    with open(name, 'r') as file:
        return file.read()


def write_on_file(name,content):
    with open(name, 'w') as file:
        file.write(content)


def insert(cs, sql):
    try:
        cs.execute(sql)
    except:
        pass


def uniq_id_generate(cs,num,table):
    randon_num = str(''.join(random.choices(string.ascii_uppercase + string.digits, k = num)))
    cs.execute(f"SELECT * FROM {table} WHERE uniq_id='{randon_num}'")
    if cs.fetchone() is None:
        return randon_num
    else:
        uniq_id_generate(num,table)


def select_api(cs, num):
    outout = ""
    cs.execute(f"SELECT api_id,count(*) FROM {mbots} GROUP BY api_id HAVING count(*)>={num}")
    result = cs.fetchall()
    if not result:
        cs.execute(f"SELECT * FROM {apis} ORDER BY RAND()")
        return cs.fetchone()
    
    for row in result:
        outout += f"'{row['api_id']}',"
    
    cs.execute(f"SELECT * FROM {apis} WHERE api_id NOT IN ({outout[0:-1]}) ORDER BY RAND()")
    return cs.fetchone()


def convert_time(time, level=4):
    time = int(time)
    day = int(time / 86400)
    hour = int((time % 86400) / 3600)
    minute = int((time % 3600) / 60)
    second = int(time % 60)
    level_check = 1
    if time >= 86400:
        if time == 86400:
            return "1 روز"
        output = f"{day} روز"
        if hour > 0 and level > level_check:
            output += f" و {hour} ساعت"
            level_check += 1
        if minute > 0 and level > level_check:
            output += f" و {minute} دقیقه"
            level_check += 1
        if second > 0 and level > level_check:
            output += f" و {second} ثانیه"
        return output
    if time >= 3600:
        if time == 3600:
            return "1 ساعت"
        output = f"{hour} ساعت"
        if minute > 0 and level > level_check:
            output += f" و {minute} دقیقه"
            level_check += 1
        if second > 0 and level > level_check:
            output += f" و {second} ثانیه"
        return output
    if time >= 60:
        if time == 60:
            return "1 دقیقه"
        output = f"{minute} دقیقه"
        if second > 0 and level > level_check:
            output += f" و {second} ثانیه"
        return output
    if second > 0:
        return f"{second} ثانیه"
    else:
        return f"1 ثانیه"


def convert_time_en(time, level=4):
    time = int(time)
    day = int(time / 86400)
    hour = int((time % 86400) / 3600)
    minute = int((time % 3600) / 60)
    second = int(time % 60)
    level_check = 1
    if time >= 86400:
        if time == 86400:
            return "1 day"
        output = f"{day} day"
        if hour > 0 and level > level_check:
            output += f", {hour} hour"
            level_check += 1
        if minute > 0 and level > level_check:
            output += f", {minute} minute"
            level_check += 1
        if second > 0 and level > level_check:
            output += f", {second} second"
        return output
    if time >= 3600:
        if time == 3600:
            return "1 hour"
        output = f"{hour} hour"
        if minute > 0 and level > level_check:
            output += f", {minute} minute"
            level_check += 1
        if second > 0 and level > level_check:
            output += f", {second} second"
        return output
    if time >= 60:
        if time == 60:
            return "1 minute"
        output = f"{minute} minute"
        if second > 0 and level > level_check:
            output += f", {second} second"
        return output
    if second > 0:
        return f"{second} second"
    else:
        return f"1 second"
