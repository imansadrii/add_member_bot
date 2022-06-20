import pymysql.cursors
import utility as utl


conn = pymysql.connect(host=utl.host_db, user=utl.user_db, password=utl.passwd_db, database=utl.database, port=utl.port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cs = conn.cursor()

cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.admini} (
  id int(11) NOT NULL AUTO_INCREMENT,
  leave_per tinyint(1) NOT NULL DEFAULT '0',
  delete_first_levels tinyint(1) NOT NULL DEFAULT '0',
  change_pass tinyint(1) NOT NULL DEFAULT '0',
  exit_session tinyint(1) NOT NULL DEFAULT '0',
  is_change_profile tinyint(1) NOT NULL DEFAULT '0',
  is_set_username tinyint(1) NOT NULL DEFAULT '0',
  gtg_per tinyint(1) NOT NULL DEFAULT '0',
  time_spam_restrict int(11) NOT NULL DEFAULT '86400',
  type_analyze tinyint(1) NOT NULL DEFAULT '0',
  type_add tinyint(1) NOT NULL DEFAULT '0',
  api_per_number int(11) NOT NULL DEFAULT '1',
  limit_per_h int(11) NOT NULL DEFAULT '24',
  add_per_h int(11) NOT NULL DEFAULT '20',
  PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")
cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.analyze} (
    id int(11) NOT NULL AUTO_INCREMENT,
	gtg_id int(11) NOT NULL,
	user_id varchar(20) DEFAULT NULL UNIQUE,
	username varchar(50) NOT NULL UNIQUE,
	origin_id varchar(30) DEFAULT NULL,
	destination_id varchar(30) DEFAULT NULL,
	is_real tinyint(1) NOT NULL DEFAULT '0',
	is_fake tinyint(1) NOT NULL DEFAULT '0',
	is_phone tinyint(1) NOT NULL DEFAULT '0',
	is_online tinyint(1) NOT NULL DEFAULT '0',
	is_bad tinyint(1) NOT NULL DEFAULT '0',
	reserved_by varchar(20) NOT NULL DEFAULT '0',
	created_at int(11) NOT NULL,
		PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")
cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.apis} (
    id int(11) NOT NULL AUTO_INCREMENT,
    api_id varchar(20) NOT NULL UNIQUE,
    api_hash varchar(200) NOT NULL UNIQUE,
	PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")
cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.egroup} (
    id int(11) NOT NULL AUTO_INCREMENT,
    user_id varchar(30) NOT NULL,
    chat_id varchar(30) DEFAULT NULL,
    link varchar(200) NOT NULL,
    status varchar(50) NOT NULL DEFAULT 'start',
    users_real int(11) NOT NULL DEFAULT '0',
    users_fake int(11) NOT NULL DEFAULT '0',
    users_has_phone int(11) NOT NULL DEFAULT '0',
    users_online int(11) NOT NULL DEFAULT '0',
    participants_count int(11) NOT NULL DEFAULT '0',
    participants_online_count int(11) NOT NULL DEFAULT '0',
    participants_bot_count int(11) NOT NULL DEFAULT '0',
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL DEFAULT '0',
    uniq_id varchar(20) NOT NULL UNIQUE,
    PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")
cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.gtg} (
    id int(11) NOT NULL AUTO_INCREMENT,
    user_id varchar(20) NOT NULL,
    origin varchar(200) NOT NULL DEFAULT '0',
    origin_id varchar(20) NOT NULL DEFAULT '0',
    destination varchar(200) NOT NULL DEFAULT '0',
    destination_id varchar(20) NOT NULL DEFAULT '0',
    count int(11) NOT NULL DEFAULT '0',
    count_moved int(11) NOT NULL DEFAULT '0',
    last_bot_check varchar(20) NOT NULL DEFAULT '0',
    last_member_check int(11) NOT NULL DEFAULT '0',
    max_users int(11) NOT NULL DEFAULT '0',
    type_users varchar(50) DEFAULT NULL,
    status varchar(50) NOT NULL DEFAULT 'start',
    status_analyze varchar(10) NOT NULL DEFAULT 'run',
    count_acc int(11) NOT NULL DEFAULT '0',
    count_repeat int(11) NOT NULL DEFAULT '0',
    count_accban int(11) NOT NULL DEFAULT '0',
    count_accout int(11) NOT NULL DEFAULT '0',
    count_privacy int(11) NOT NULL DEFAULT '0',
    count_toomuch int(11) NOT NULL DEFAULT '0',
    count_report int(11) NOT NULL DEFAULT '0',
    count_restrict int(11) NOT NULL DEFAULT '0',
    count_ban int(11) NOT NULL DEFAULT '0',
    count_spam int(11) NOT NULL DEFAULT '0',
    count_permission int(11) NOT NULL DEFAULT '0',
    created_at int(11) NOT NULL DEFAULT '0',
    updated_at int(11) NOT NULL DEFAULT '0',
    uniq_id varchar(20) NOT NULL UNIQUE,
    PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")
cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.mbots} (
    id int(11) NOT NULL AUTO_INCREMENT,
    creator_user_id varchar(20) NOT NULL,
    phone varchar(20) NOT NULL UNIQUE,
    user_id varchar(20) DEFAULT NULL,
    status varchar(50) NOT NULL DEFAULT 'first_level',
    end_restrict int(11) NOT NULL DEFAULT '0',
    last_order_at int(11) NOT NULL DEFAULT '0',
    last_leve_at int(11) NOT NULL DEFAULT '0',
    api_id varchar(20) NOT NULL,
    api_hash varchar(200) NOT NULL,
    phone_code_hash varchar(100) DEFAULT NULL,
    code int(11) DEFAULT NULL,
    password varchar(100) DEFAULT NULL,
    is_change_pass tinyint(1) NOT NULL DEFAULT '0',
    change_pass_at int(11) NOT NULL DEFAULT '0',
    is_exit_session tinyint(1) NOT NULL DEFAULT '0',
    exit_session_at int(11) NOT NULL DEFAULT '0',
    is_change_profile tinyint(1) NOT NULL DEFAULT '0',
    is_set_username tinyint(1) NOT NULL DEFAULT '0',
    created_at int(11) NOT NULL,
    uniq_id varchar(20) NOT NULL UNIQUE,
    PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")
cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.moveds} (
    id int(11) NOT NULL AUTO_INCREMENT,
    gtg_id int(11) NOT NULL,
    bot_id int(11) NOT NULL,
    username varchar(50) NOT NULL,
    origin_id varchar(30) DEFAULT NULL,
    destination_id varchar(30) DEFAULT NULL,
    status varchar(20) NOT NULL DEFAULT 'join',
    created_at int(11) NOT NULL,
    PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")
cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.reports} (
    id int(11) NOT NULL AUTO_INCREMENT,
    gtg_id int(11) NOT NULL,
    bot_id int(11) NOT NULL,
    username varchar(50) NOT NULL,
    status varchar(20) NOT NULL,
    created_at int(11) NOT NULL,
    PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")
cs.execute(f"""CREATE TABLE IF NOT EXISTS {utl.users} (
    id int(11) NOT NULL AUTO_INCREMENT,
    user_id varchar(20) NOT NULL UNIQUE,
    status varchar(20) NOT NULL DEFAULT 'user',
    step varchar(50) NOT NULL DEFAULT 'start',
    prev_step varchar(50) NOT NULL DEFAULT 'start',
    last_auto_update_at int(11) NOT NULL DEFAULT '0',
    created_at int(11) NOT NULL,
    uniq_id varchar(20) NOT NULL UNIQUE,
    PRIMARY KEY (id)
)ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")

cs.execute(f"SELECT * FROM {utl.admini}")
row_admin = cs.fetchone()
if row_admin is None:
    cs.execute(f"INSERT INTO {utl.admini} (id) VALUES (1)")
conn.close()


