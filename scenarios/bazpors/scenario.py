from .roles import ROLES

BASE = {
    "name": "بازپرس",
    "emoji": "⚖️",
    "description": "سناریوی بازپرس؛ ترتیب شب: هانتر، شیاد، تیم مافیا، سپس همه شهروندهای نقش‌دار به‌صورت هم‌زمان.",
    "roles": ROLES,
    "night_order": ["hunter", "deceiver", "mafia_team", "citizen_roles"],
}

SCENARIOS = {
    "bazpors10": {**BASE, "id":"bazpors10", "name":"بازپرس ۱۰ نفره", "player_count":10,
        "role_ids":["godfather","nato","deceiver","hunter","bulletproof","interrogator","doctor","detective","citizen","citizen"]},
    "bazpors12": {**BASE, "id":"bazpors12", "name":"بازپرس ۱۲ نفره", "player_count":12,
        "role_ids":["godfather","nato","deceiver","mafia_goon","hunter","bulletproof","interrogator","doctor","detective","sniper","citizen","citizen"]},
    "bazpors13": {**BASE, "id":"bazpors13", "name":"بازپرس ۱۳ نفره", "player_count":13,
        "role_ids":["godfather","nato","deceiver","mafia_goon","hunter","bulletproof","interrogator","doctor","detective","sniper","citizen","citizen","citizen"]},
}
