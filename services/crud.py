# from utils.db import SessionLocal
# from models import PlayerStat

# def create_player_stat(player_name, runs, wickets, strike_rate, match_id):
#     db = SessionLocal()
#     stat = PlayerStat(
#         player_name=player_name,
#         runs=runs,
#         wickets=wickets,
#         strike_rate=strike_rate,
#         match_id=match_id
#     )
#     db.add(stat)
#     db.commit()
#     db.refresh(stat)
#     db.close()
#     return stat

# def get_player_stats():
#     db = SessionLocal()
#     stats = db.query(PlayerStat).all()
#     db.close()
#     return stats

# def update_player_stat(player_id, runs=None, wickets=None, strike_rate=None):
#     db = SessionLocal()
#     stat = db.query(PlayerStat).filter(PlayerStat.id == player_id).first()
#     if stat:
#         if runs is not None: stat.runs = runs
#         if wickets is not None: stat.wickets = wickets
#         if strike_rate is not None: stat.strike_rate = strike_rate
#         db.commit()
#     db.close()

# def delete_player_stat(player_id):
#     db = SessionLocal()
#     db.query(PlayerStat).filter(PlayerStat.id == player_id).delete()
#     db.commit()
#     db.close()
