from .roles import ROLES

SCENARIO = {
    "id": 'kapo',
    "name": 'کاپو',
    "emoji": '🎩',
    "player_count": 12,
    "description": "ساختار نقش‌ها، تقسیم نقش و ترتیب پایه شب برای این سناریو فعال است.",
    "roles": ROLES,
    "role_ids": ['don', 'wizard', 'executioner', 'informant', 'detective', 'suspect', 'armorer', 'apothecary', 'heir', 'kadkhoda', 'citizen', 'citizen'],
    "night_order": ['mafia_team', 'detective', 'armorer', 'apothecary', 'heir', 'kadkhoda'],
}
