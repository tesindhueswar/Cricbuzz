import streamlit as st
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from utils.db_connection import SessionLocal
from utils.models import Player

# ---- Helpers ----
ROLES = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]

def get_db() -> Session:
    return SessionLocal()

def list_players(db: Session, name_q: Optional[str] = None, country_q: Optional[str] = None, role_q: Optional[str] = None) -> List[Player]:
    stmt = select(Player)
    if name_q:
        stmt = stmt.where(Player.name.ilike(f"%{name_q.strip()}%"))
    if country_q:
        stmt = stmt.where(Player.country.ilike(f"%{country_q.strip()}%"))
    if role_q and role_q != "All":
        stmt = stmt.where(Player.role == role_q)
    return db.execute(stmt).scalars().all()

def create_player(db: Session, *, name: str, country: str, role: str, batting_style: Optional[str], bowling_style: Optional[str]) -> Player:
    player = Player(
        name=name.strip(),
        country=country.strip(),
        role=role.strip(),
        batting_style=(batting_style or "").strip() or None,
        bowling_style=(bowling_style or "").strip() or None,
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

def update_player(db: Session, player_id: int, *, name: str, country: str, role: str, batting_style: Optional[str], bowling_style: Optional[str]) -> Optional[Player]:
    player = db.get(Player, player_id)
    if not player:
        return None
    player.name = name.strip()
    player.country = country.strip()
    player.role = role.strip()
    player.batting_style = (batting_style or "").strip() or None
    player.bowling_style = (bowling_style or "").strip() or None
    db.commit()
    db.refresh(player)
    return player

def delete_players(db: Session, ids: List[int]) -> int:
    count = 0
    for pid in ids:
        # Use direct SQL to avoid loading relationships
        result = db.execute(text("DELETE FROM players WHERE id = :id"), {"id": pid})
        if result.rowcount > 0:
            count += 1
    if count:
        db.commit()
    return count

# ---- Streamlit UI ----
st.title("🛠️ CRUD Operations — Players")
st.caption("Manage players. Only uses these columns: **id, name, country, role, batting_style, bowling_style**.")

tab_create, tab_list, tab_delete = st.tabs(["➕ Create", "📋 List & Edit", "🗑️ Delete"])

# ---- Create ----
with tab_create:
    st.subheader("Add New Player")
    with st.form("create_player_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name*", placeholder="e.g., Virat Kohli")
            country = st.text_input("Country*", placeholder="e.g., India")
            role = st.selectbox("Role*", ROLES, index=0)
        with col2:
            batting_style = st.text_input("Batting Style", placeholder="e.g., Right-handed")
            bowling_style = st.text_input("Bowling Style", placeholder="e.g., Right-arm medium")

        submitted = st.form_submit_button("Create Player")
        if submitted:
            if not name.strip() or not country.strip() or not role.strip():
                st.error("Please fill out Name, Country, and Role.")
            else:
                db = get_db()
                try:
                    player = create_player(
                        db,
                        name=name,
                        country=country,
                        role=role,
                        batting_style=batting_style,
                        bowling_style=bowling_style,
                    )
                    st.success(f"Player created with ID: {player.id}")
                except Exception as e:
                    st.error(f"Error creating player: {e}")
                finally:
                    db.close()

# ---- List & Edit ----
with tab_list:
    st.subheader("Players")
    with st.expander("Filters", expanded=False):
        fcol1, fcol2, fcol3 = st.columns([2, 2, 1])
        with fcol1:
            f_name = st.text_input("Search by Name")
        with fcol2:
            f_country = st.text_input("Search by Country")
        with fcol3:
            f_role = st.selectbox("Role", ["All"] + ROLES, index=0)

    db = get_db()
    try:
        players = list_players(db, f_name, f_country, f_role)
    except Exception as e:
        players = []
        st.error(f"Error loading players: {e}")

    if not players:
        st.info("No players found. Try adjusting filters or add a new player.")
    else:
        # Display as a simple table
        data = [
            {
                "ID": p.id,
                "Name": p.name,
                "Country": p.country,
                "Role": p.role,
                "Batting Style": p.batting_style or "",
                "Bowling Style": p.bowling_style or "",
            }
            for p in players
        ]
        st.dataframe(data, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Edit Player")

        id_options = [p.id for p in players]
        edit_id = st.selectbox("Select Player ID to Edit", id_options) if id_options else None
        if edit_id:
            target = next((p for p in players if p.id == edit_id), None)
            if target:
                ecol1, ecol2 = st.columns(2)
                with ecol1:
                    e_name = st.text_input("Name*", value=target.name)
                    e_country = st.text_input("Country*", value=target.country)
                    e_role = st.selectbox("Role*", ROLES, index=ROLES.index(target.role) if target.role in ROLES else 0)
                with ecol2:
                    e_batting = st.text_input("Batting Style", value=target.batting_style or "")
                    e_bowling = st.text_input("Bowling Style", value=target.bowling_style or "")

                if st.button("Save Changes"):
                    try:
                        updated = update_player(
                            db,
                            target.id,
                            name=e_name,
                            country=e_country,
                            role=e_role,
                            batting_style=e_batting,
                            bowling_style=e_bowling,
                        )
                        if updated:
                            st.success("Player updated.")
                            st.rerun()
                        else:
                            st.error("Player not found.")
                    except Exception as e:
                        st.error(f"Error updating player: {e}")
                    finally:
                        db.close()

# ---- Delete ----
with tab_delete:
    st.subheader("Delete Players")
    db = get_db()
    try:
        all_players = list_players(db)
    except Exception as e:
        all_players = []
        st.error(f"Error loading players: {e}")

    if not all_players:
        st.info("No players to delete.")
    else:
        options = {f"{p.id} — {p.name} ({p.country})": p.id for p in all_players}
        to_delete_labels = st.multiselect("Select players to delete", list(options.keys()))
        to_delete_ids = [options[label] for label in to_delete_labels]

        if to_delete_ids and st.button("Confirm Delete"):
            try:
                removed = delete_players(db, to_delete_ids)
                st.success(f"Deleted {removed} player(s).")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting players: {e}")
    db.close()