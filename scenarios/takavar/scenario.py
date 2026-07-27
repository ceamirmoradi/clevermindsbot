from .roles import ROLES

SCENARIO = {
    "id": 'takavar',
    "name": 'تکاور',
    "emoji": '🏹',
    "player_count": 10,
    "description": "ساختار نقش‌ها، تقسیم نقش و ترتیب پایه شب برای این سناریو فعال است.",
    "roles": ROLES,
    "role_ids": ['godfather', 'nato', 'hostage_taker', 'mafia_goon', 'detective', 'doctor', 'guard', 'gunman', 'takavar', 'citizen'],
    "night_order": ['guard', 'hostage_taker', 'mafia_team', 'detective', 'takavar', 'doctor', 'gunman'],
}
