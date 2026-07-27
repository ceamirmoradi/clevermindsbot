from .roles import ROLES

SCENARIO = {
    "id": 'namayande',
    "name": 'نماینده',
    "emoji": '🏛',
    "player_count": 10,
    "description": "ساختار نقش‌ها، تقسیم نقش و ترتیب پایه شب برای این سناریو فعال است.",
    "roles": ROLES,
    "role_ids": ['don', 'rebel', 'hacker', 'doctor', 'guide', 'miner', 'lawyer', 'guard', 'citizen', 'citizen'],
    "night_order": ['representatives', 'mafia_team', 'hacker', 'miner', 'guard', 'doctor', 'guide', 'lawyer'],
}
