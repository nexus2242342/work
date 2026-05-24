BOT_TOKEN = "8305173759:AAFuBx2r_VjDdWplg62Taq0FDwyld4ThWsw"
TON_WALLET = "UQDtRwosWY6VfPnwovLRcF2yo46Xv3BcK-mV1Da-1LwbVIaE"
USDT_WALLET = "TKPuYeveSA2giJV9fFcgbCDsY6abmzMS7Z"
LOG_CHAT_ID = 8353710361
SUPPORT_USERNAME = "@MollyWhip1"

WORKERS = {
    1:  {"name_ru": "🧑‍🌾 Стажёр",        "name_en": "🧑‍🌾 Intern",         "cost": 1,    "income_day": 0.003},
    2:  {"name_ru": "👨‍🔧 Разнорабочий",  "name_en": "👨‍🔧 Laborer",        "cost": 5,    "income_day": 0.02},
    3:  {"name_ru": "👷 Шахтёр",          "name_en": "👷 Miner",            "cost": 20,   "income_day": 0.10},
    4:  {"name_ru": "🔧 Инженер",         "name_en": "🔧 Engineer",         "cost": 50,   "income_day": 0.30},
    5:  {"name_ru": "🧙‍♂️ Бурильщик",    "name_en": "🧙‍♂️ Driller",       "cost": 100,  "income_day": 0.70},
    6:  {"name_ru": "⚙️ Механик",         "name_en": "⚙️ Mechanic",        "cost": 200,  "income_day": 1.60},
    7:  {"name_ru": "🏭 Директор шахты",  "name_en": "🏭 Mine Director",   "cost": 500,  "income_day": 4.50},
    8:  {"name_ru": "👑 Магнат",          "name_en": "👑 Magnate",         "cost": 1000, "income_day": 10.00},
    9:  {"name_ru": "⭐ Олигарх",         "name_en": "⭐ Oligarch",        "cost": 2500, "income_day": 30.00},
    10: {"name_ru": "💎 Крипто-король",   "name_en": "💎 Crypto King",     "cost": 5000, "income_day": 75.00},
}

FARM_LEVELS = {
    1:  {"min_workers": 1,   "max_workers": 5,   "bonus": 0.00, "upgrade_cost": 0},
    2:  {"min_workers": 6,   "max_workers": 10,  "bonus": 0.05, "upgrade_cost": 50},
    3:  {"min_workers": 11,  "max_workers": 20,  "bonus": 0.10, "upgrade_cost": 100},
    4:  {"min_workers": 21,  "max_workers": 35,  "bonus": 0.15, "upgrade_cost": 200},
    5:  {"min_workers": 36,  "max_workers": 50,  "bonus": 0.20, "upgrade_cost": 400},
    6:  {"min_workers": 51,  "max_workers": 75,  "bonus": 0.30, "upgrade_cost": 700},
    7:  {"min_workers": 76,  "max_workers": 100, "bonus": 0.40, "upgrade_cost": 1000},
    8:  {"min_workers": 101, "max_workers": 150, "bonus": 0.50, "upgrade_cost": 1500},
    9:  {"min_workers": 151, "max_workers": 200, "bonus": 0.60, "upgrade_cost": 2000},
    10: {"min_workers": 201, "max_workers": 9999,"bonus": 0.75, "upgrade_cost": 3000},
}

FARM_MILESTONES = {1: 0.5, 5: 2.0, 10: 5.0, 25: 15.0, 50: 40.0, 100: 100.0}

DAILY_BONUSES = {
    1: 0.05, 2: 0.07, 3: 0.10, 4: 0.15, 5: 0.20,
    6: 0.30, 7: 0.50, 14: 1.00, 21: 2.00, 30: 5.00,
}

REFERRAL_PERCENTS = {1: 0.07, 2: 0.03, 3: 0.02, 4: 0.01, 5: 0.005}
REFERRAL_INVITE_BONUS = 0.5
REFERRAL_FIRST_WORKER_BONUS = 1.0
REFERRAL_5_WORKERS_BONUS = 2.0
REFERRAL_10_WORKERS_BONUS = 5.0
REFERRAL_LVL5_WORKER_BONUS = 3.0

TEMP_BOOSTS = {
    "speed":   {"name_ru": "⚡ Ускорение",    "name_en": "⚡ Speed",       "cost": 10,  "multiplier": 1.20, "hours": 24},
    "repair":  {"name_ru": "🔧 Ремонт",       "name_en": "🔧 Repair",      "cost": 25,  "multiplier": 1.30, "hours": 72},
    "upgrade": {"name_ru": "🏭 Модернизация", "name_en": "🏭 Upgrade",     "cost": 50,  "multiplier": 1.50, "hours": 168},
    "auto":    {"name_ru": "🤖 Автоматизация","name_en": "🤖 Automation",  "cost": 100, "multiplier": 2.00, "hours": 168},
    "premium": {"name_ru": "💎 Премиум",      "name_en": "💎 Premium",     "cost": 200, "multiplier": 2.50, "hours": 720},
}

PERM_BOOSTS = {
    "training": {"name_ru": "📚 Обучение",  "name_en": "📚 Training",    "cost": 50,  "bonus": 0.05},
    "courses":  {"name_ru": "🎓 Курсы",     "name_en": "🎓 Courses",     "cost": 100, "bonus": 0.10},
    "cert":     {"name_ru": "🏆 Сертификат","name_en": "🏆 Certificate", "cost": 200, "bonus": 0.15},
    "license":  {"name_ru": "👑 Лицензия",  "name_en": "👑 License",     "cost": 500, "bonus": 0.25},
}

WITHDRAW_MIN = 10.0
WITHDRAW_FEE_NORMAL = 0.05
WITHDRAW_FEE_FAST = 0.10
WITHDRAW_FEE_INSTANT = 0.15
WITHDRAW_MAX_DAY = 500.0
WITHDRAW_MAX_MONTH = 5000.0

ACHIEVEMENTS = {
    "workers_100": {"name_ru": "Купить 100 рабочих",    "name_en": "Buy 100 workers",    "reward": 50.0,  "title_ru": "Олигарх",  "title_en": "Oligarch"},
    "refs_50":     {"name_ru": "Пригласить 50 друзей",  "name_en": "Invite 50 friends",  "reward": 100.0, "title_ru": "Лидер",    "title_en": "Leader"},
    "earned_1000": {"name_ru": "Заработать 1000 TON",   "name_en": "Earn 1000 TON",      "reward": 200.0, "title_ru": "Магнат",   "title_en": "Magnate"},
    "days_30":     {"name_ru": "Играть 30 дней подряд", "name_en": "Play 30 days streak","reward": 25.0,  "title_ru": "Ветеран",  "title_en": "Veteran"},
}

ADMIN_IDS = [8353710361]