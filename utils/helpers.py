from datetime import datetime
from config import WORKERS, FARM_LEVELS, TEMP_BOOSTS, PERM_BOOSTS, ACHIEVEMENTS


def get_worker_name(worker_type: int, lang: str = "ru") -> str:
    w = WORKERS.get(worker_type, {})
    return w.get(f"name_{lang}", w.get("name_ru", "Unknown"))


def get_boost_name(boost_key: str, boost_dict: dict, lang: str = "ru") -> str:
    b = boost_dict.get(boost_key, {})
    return b.get(f"name_{lang}", b.get("name_ru", boost_key))


def format_ton(amount: float) -> str:
    return f"{amount:.3f}"


async def calculate_income(user_id: int) -> float:
    from database.db import get_user_workers, get_user, get_active_boosts, get_perm_boosts
    workers = await get_user_workers(user_id)
    user = await get_user(user_id)
    if not workers or not user:
        return 0.0

    base_income = 0.0
    for w in workers:
        wtype = w["worker_type"]
        cnt = w["cnt"]
        base_income += WORKERS[wtype]["income_day"] * cnt

    farm_level = user["farm_level"]
    farm_bonus = FARM_LEVELS.get(farm_level, {}).get("bonus", 0.0)
    base_income *= (1 + farm_bonus)

    active_boosts = await get_active_boosts(user_id)
    boost_mult = 1.0
    for b in active_boosts:
        boost_mult *= b["multiplier"]

    perm_boosts = await get_perm_boosts(user_id)
    perm_bonus = 0.0
    for bk in perm_boosts:
        perm_bonus += PERM_BOOSTS.get(bk, {}).get("bonus", 0.0)

    total = base_income * boost_mult * (1 + perm_bonus)
    return round(total, 6)


async def calculate_pending(user_id: int) -> float:
    from database.db import get_last_collect
    last = await get_last_collect(user_id)
    if not last:
        return 0.0
    if isinstance(last, str):
        try:
            last_dt = datetime.fromisoformat(last)
        except ValueError:
            return 0.0
    else:
        last_dt = last

    income_day = await calculate_income(user_id)
    elapsed = (datetime.now() - last_dt).total_seconds()
    earned = income_day * (elapsed / 86400)
    return round(earned, 6)


async def check_achievements(user_id: int) -> list:
    from database.db import (get_user, get_worker_count, get_referrals,
                               get_achievements, add_achievement, update_balance)

    user = await get_user(user_id)
    if not user:
        return []

    worker_count = await get_worker_count(user_id)
    ref_count = await get_referrals(user_id)
    earned = user["total_earned"]
    streak = user["daily_streak"]
    done = await get_achievements(user_id)
    new_achievements = []

    checks = {
        "workers_100": worker_count >= 100,
        "refs_50": ref_count >= 50,
        "earned_1000": earned >= 1000,
        "days_30": streak >= 30,
    }

    for key, condition in checks.items():
        if condition and key not in done:
            result = await add_achievement(user_id, key)
            if result:
                reward = ACHIEVEMENTS[key]["reward"]
                await update_balance(user_id, reward)
                new_achievements.append(key)

    return new_achievements