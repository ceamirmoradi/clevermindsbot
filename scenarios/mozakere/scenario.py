from .roles import ROLES

SCENARIO = {
    "id": "mozakere",
    "name": "مذاکره ۱۰ نفره",
    "emoji": "🤝",
    "player_count": 10,
    "description": "سناریوی کلاسیک مذاکره؛ مافیا پس از از دست‌دادن یک یار می‌تواند یک‌بار به‌جای شلیک، شهروند واجد شرایط را جذب کند.",
    "roles": ROLES,
    "role_ids": [
        "godfather", "negotiator", "mafia_goon",
        "doctor", "armored", "reporter", "detective", "sniper",
        "citizen", "citizen",
    ],
    "night_order": ["mafia_team", "detective", "sniper", "doctor", "reporter"],
    "vote_thresholds": {"8-10": 4, "6-7": 3, "4-5": 2},
}
