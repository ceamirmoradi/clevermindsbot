from __future__ import annotations
from typing import Any
from engine.event_service import log_event
from storage import save_games

ACTION_LABELS = {
 "hunter_link":"انتخاب هانتر", "deceiver_target":"هدف شیاد", "nato_target":"هدف ناتو",
 "mafia_shot":"شلیک مافیا", "doctor_save":"نجات پزشک", "detective_check":"استعلام کارآگاه",
 "interrogation":"دو هدف بازپرس", "sniper_shot":"شلیک تک‌تیرانداز",
 "yakuza_sacrifice":"فدایی یاکوزا", "yakuza_target":"هدف جذب یاکوزا",
}

def alive_players(game):
 return sorted([p for p in game['players'] if p.get('status')=='approved' and p.get('alive',True)], key=lambda p:p.get('seat') or 999)

def action_for(game, actor_id, action_type):
 for a in reversed(game.setdefault('pending_actions', [])):
  if a.get('actor_id')==actor_id and a.get('type')==action_type:
   return a
 return None

def register_action(game, actor, action_type, targets, metadata=None):
 game.setdefault('pending_actions', [])[:] = [a for a in game.get('pending_actions',[]) if not (a.get('actor_id')==actor['user_id'] and a.get('type')==action_type)]
 action={"actor_id":actor['user_id'],"actor_seat":actor.get('seat'),"actor_role":actor.get('role'),"type":action_type,"targets":targets,"metadata":metadata or {},"night":game.get('night_number',0)}
 game['pending_actions'].append(action)
 log_event(game,event_type='night_action',message=f"🌙 {ACTION_LABELS.get(action_type,action_type)} توسط صندلی {actor.get('seat')} ثبت شد.",actor_id=actor['user_id'],metadata={"action_type":action_type,"targets":targets})
 save_games(); return action

def target_by_id(game, uid):
 return next((p for p in game['players'] if p['user_id']==uid),None)

def interrogation_status(game):
 act=next((a for a in reversed(game.get('pending_actions',[])+game.get('all_actions',[])) if a['type']=='interrogation' and a.get('night')==game.get('night_number')),None)
 if not act: return {"active":False,"reason":"no_action"}
 actor=target_by_id(game,act['actor_id'])
 for uid in act['targets']:
  p=target_by_id(game,uid)
  if not p or not p.get('alive',True) or p.get('status')!='approved':
   return {"active":False,"reason":"یکی از دو هدف از بازی خارج شده است.","returned":bool(actor and actor.get('alive',True)),"action":act}
  if p.get('natoed_night')==game.get('night_number'):
   return {"active":False,"reason":"یکی از دو هدف ناتویی شده است.","returned":bool(actor and actor.get('alive',True)),"action":act}
  if p.get('yakuza_sacrificed_night')==game.get('night_number'):
   return {"active":False,"reason":"یکی از دو هدف برای یاکوزا فدا شده است.","returned":bool(actor and actor.get('alive',True)),"action":act}
 return {"active":True,"targets":act['targets'],"actor_id":act['actor_id'],"action":act}

def narrator_night_report(game):
 lines=[f"🌙 <b>گزارش اکت‌های شب {game.get('night_number',0)}</b>",""]
 if not game.get('pending_actions'): return "\n".join(lines+["اکتی ثبت نشده است."])
 for a in game['pending_actions']:
  actor=target_by_id(game,a['actor_id']); names=[]
  for uid in a.get('targets',[]):
   p=target_by_id(game,uid); names.append(f"صندلی {p.get('seat')} ({p.get('name')})" if p else str(uid))
  lines.append(f"• {ACTION_LABELS.get(a['type'],a['type'])}: {', '.join(names) or '—'} — بازیگر: صندلی {actor.get('seat') if actor else '?'}")
 return "\n".join(lines)

def resolve_yakuza(game):
 sacrifice=next((a for a in reversed(game.get('pending_actions',[])) if a['type']=='yakuza_sacrifice'),None)
 target=next((a for a in reversed(game.get('pending_actions',[])) if a['type']=='yakuza_target'),None)
 if not sacrifice or not target: return None
 s=target_by_id(game,sacrifice['targets'][0]); t=target_by_id(game,target['targets'][0])
 if not s or not t or not s.get('alive',True) or not t.get('alive',True): return "یاکوزا نامعتبر شد؛ فدایی یا هدف فعال نیست."
 mafia=[p for p in alive_players(game) if p.get('team')=='mafia']
 if s.get('role')=='godfather' and len(mafia)>1: return "رئیس مافیا فقط زمانی می‌تواند خود را فدا کند که آخرین مافیا باشد."
 allowed={'citizen'}
 if game.get('scenario_id')=='bazpors12': allowed.add('bulletproof')
 if t.get('role') not in allowed: return "هدف انتخاب‌شده برای یاکوزا مجاز نیست."
 s['alive']=False; s['status']='eliminated'; s['can_act']=False; s['yakuza_sacrificed_night']=game.get('night_number')
 t['role']='yakuzad'; t['role_name']='مافیای یاکوزایی‌شده'; t['team']='mafia'; t['recruited_night']=game.get('night_number')
 log_event(game,event_type='yakuza_success',message=f"🤝 صندلی {s.get('seat')} فدا شد و صندلی {t.get('seat')} به مافیا پیوست.",actor_id=s['user_id'],target_id=t['user_id'])
 save_games(); return "یاکوزا با موفقیت انجام شد."

def eliminate_player(game, player, reason, phase, trigger_hunter=True):
 if not player.get('alive',True): return []
 player['alive']=False; player['can_act']=False; player['status']='eliminated'; player['removed_reason']=reason; player['removed_phase']=phase
 removed=[player]
 log_event(game,event_type='player_eliminated',message=f"💀 صندلی {player.get('seat')} — {player.get('name')} خارج شد. دلیل: {reason}",target_id=player['user_id'])
 if trigger_hunter and player.get('role')=='hunter':
  act=next((a for a in reversed(game.get('all_actions',[])+game.get('pending_actions',[])) if a.get('actor_id')==player['user_id'] and a.get('type')=='hunter_link'),None)
  if act and act.get('targets'):
   target=target_by_id(game,act['targets'][0])
   if target and target.get('alive',True) and target.get('role') in {'deceiver','nato','yakuzad'}:
    removed += eliminate_player(game,target,'خروج همراه هانتر',phase,False)
 save_games(); return removed

def archive_night_actions(game):
 game.setdefault('all_actions',[]).extend(game.get('pending_actions',[]))
 save_games()
