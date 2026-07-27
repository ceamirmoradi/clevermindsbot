from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def target_menu(game, action_type, actor_id, *, exclude_self=False, selected=None):
 selected=selected or []
 rows=[]
 for p in sorted(game['players'],key=lambda x:x.get('seat') or 999):
  if p.get('status')!='approved' or not p.get('alive',True): continue
  if exclude_self and p['user_id']==actor_id: continue
  if p['user_id'] in selected: continue
  rows.append([InlineKeyboardButton(f"{p.get('seat')}. {p.get('name')}",callback_data=f"act:{game['code']}:{action_type}:{p['user_id']}")])
 rows.append([InlineKeyboardButton("❌ انصراف",callback_data="home")])
 return InlineKeyboardMarkup(rows)

def mafia_action_menu(code):
 return InlineKeyboardMarkup([
  [InlineKeyboardButton("🔫 ثبت شلیک مافیا",callback_data=f"mafia_mode:{code}:mafia_shot")],
  [InlineKeyboardButton("🤝 یاکوزا — انتخاب فدایی",callback_data=f"mafia_mode:{code}:yakuza_sacrifice")],
 ])

def interrogator_decision_menu(code):
 return InlineKeyboardMarkup([
  [InlineKeyboardButton("✅ ادامه بازپرسی",callback_data=f"interro_decide:{code}:continue")],
  [InlineKeyboardButton("❌ لغو رأی‌گیری؛ هر دو بنشینند",callback_data=f"interro_decide:{code}:cancel")],
 ])

def narrator_night_menu(code):
 return InlineKeyboardMarkup([
  [InlineKeyboardButton("📋 گزارش اکت‌های شب",callback_data=f"night_report:{code}")],
  [InlineKeyboardButton("🤝 اجرای یاکوزا",callback_data=f"resolve_yakuza:{code}")],
  [InlineKeyboardButton("⚖️ پایان دفاع‌های بازپرسی",callback_data=f"end_interro_defenses:{code}")],
  [InlineKeyboardButton("💀 ثبت خروج بازیکن",callback_data=f"eliminate_menu:{code}")],
  [InlineKeyboardButton("⬅️ بازگشت",callback_data=f"refresh_game:{code}")],
 ])

def eliminate_menu(game):
 rows=[]
 for p in sorted(game['players'],key=lambda x:x.get('seat') or 999):
  if p.get('status')=='approved' and p.get('alive',True):
   rows.append([InlineKeyboardButton(f"💀 {p.get('seat')}. {p.get('name')}",callback_data=f"elim_pick:{game['code']}:{p['user_id']}")])
 rows.append([InlineKeyboardButton("⬅️ بازگشت",callback_data=f"night_tools:{game['code']}")])
 return InlineKeyboardMarkup(rows)

def eliminate_reason_menu(code,uid):
 return InlineKeyboardMarkup([
  [InlineKeyboardButton("🌙 شلیک شب",callback_data=f"elim:{code}:{uid}:شلیک شب")],
  [InlineKeyboardButton("🗳 رأی‌گیری روز",callback_data=f"elim:{code}:{uid}:رأی‌گیری روز")],
  [InlineKeyboardButton("⚖️ بازپرسی",callback_data=f"elim:{code}:{uid}:بازپرسی")],
  [InlineKeyboardButton("⬅️ انصراف",callback_data=f"eliminate_menu:{code}")],
 ])
