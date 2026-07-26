from typing import Any

# فعلاً ذخیره‌سازی موقت است.
# با ری‌استارت Render اطلاعات بازی‌ها پاک می‌شود.
games: dict[str, dict[str, Any]] = {}
user_states: dict[int, str] = {}
