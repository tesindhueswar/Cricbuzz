import streamlit as st
import pandas as pd
import sqlite3
import os
from typing import Dict, Tuple, Optional

try:
    from utils.sql_queries import QUERIES
except ImportError:
    st.error("Cannot import QUERIES from utils.sql_queries")
    st.stop()

try:
    from utils.db_connection import SessionLocal, engine
except ImportError:
    st.error("Cannot import database connection from utils.db_connection")
    st.stop()

st.set_page_config(
    page_title="SQL Analytics - Cricket Database", 
    
    layout="wide"
)

st.title("SQL Analytics")
st.markdown("Execute predefined and custom SQL queries on the cricket database")

def execute_sql_query(query: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    try:
        database_url = os.getenv("DATABASE_URL", "sqlite:///cricket.db")
        
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
        else:
            db_path = "cricket.db"
        
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn)
            return df, None
    except Exception as e:
        return None, str(e)

def display_query_results(df: pd.DataFrame, query_title: str):
    if df is not None and not df.empty:
        st.success(f"Query executed successfully - {len(df)} rows returned")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Size", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        if st.button(f"Download {query_title} Results"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"cricket_query_{query_title.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("Query returned no results")

st.header("Predefined Queries")

query_options = {f"{k}: {v[0]}": k for k, v in QUERIES.items()}
selected_query = st.selectbox(
    "Choose a query",
    ["Custom Query"] + list(query_options.keys()),
    index=0
)

if selected_query != "Custom Query":
    query_id = query_options[selected_query]
    query_title, predefined_sql = QUERIES[query_id]
    
    st.markdown(f"**Selected:** {query_title}")
    
    with st.expander("Preview Query"):
        st.code(predefined_sql, language="sql")

if selected_query == "Custom Query":
    st.subheader("Custom SQL Query")
    st.markdown("Write your own SQL query to analyze the cricket database")
    
    custom_sql = st.text_area(
        "Enter your SQL query:",
        placeholder="""SELECT p.name, ps.runs, ps.average 
FROM players p 
JOIN player_stats ps ON p.id = ps.player_id 
WHERE ps.format = 'ODI' 
ORDER BY ps.runs DESC 
LIMIT 10;""",
        height=150
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        execute_custom = st.button("Execute Query", type="primary")
    with col2:
        if st.button("Validate Syntax"):
            if custom_sql.strip():
                try:
                    import sqlparse
                    parsed = sqlparse.parse(custom_sql)
                    if parsed:
                        st.success("SQL syntax appears valid")
                    else:
                        st.error("Invalid SQL syntax")
                except ImportError:
                    st.info("Install sqlparse for syntax validation")
                except:
                    st.error("SQL syntax validation failed")
    
    if execute_custom and custom_sql.strip():
        with st.spinner("Executing custom query..."):
            df, error = execute_sql_query(custom_sql)
            
            if error:
                st.error(f"Query Error: {error}")
              
            else:
                display_query_results(df, "Custom Query")

else:
    query_id = query_options[selected_query]
    query_title, predefined_sql = QUERIES[query_id]
    
    st.subheader(f"{query_title}")
    
    with st.expander("View SQL Query", expanded=False):
        st.code(predefined_sql, language="sql")
    
    if st.button("Execute Query", type="primary"):
        with st.spinner(f"Executing: {query_title}..."):
            df, error = execute_sql_query(predefined_sql)
            
            if error:
                st.error(f"Query Error: {error}")
                if "no such table" in error.lower():
                    st.info("This query requires tables that may not exist yet. Try seeding the database first.")
                elif "no such column" in error.lower():
                    st.info("This query requires columns that may not exist in the current schema.")
            else:
                display_query_results(df, query_title)

st.divider()
st.subheader("Available Query Categories")

query_categories = {
    "Player Analytics": [1, 3, 6, 9, 11, 18, 20, 21],
    "Match Analytics": [2, 5, 10, 12, 17],
    "Venue Analytics": [4],
    "Advanced Analytics": [7, 13, 14, 15, 16, 19, 22, 23, 24, 25],
    "Placeholder Queries": [8]
}

for category, query_ids in query_categories.items():
    with st.expander(f"{category} ({len(query_ids)} queries)"):
        for qid in query_ids:
            if qid in QUERIES:
                title, _ = QUERIES[qid]
                st.markdown(f"**{qid}.** {title}")

st.divider()
st.subheader("Database Schema Reference")

schema_info = {
    "players": ["id", "name", "country", "role", "batting_style", "bowling_style"],
    "teams": ["id", "name", "country", "type"],
    "venues": ["id", "name", "city", "country", "capacity"],
    "matches": ["id", "description", "team1_id", "team2_id", "venue_id", "start_time", "winner_team_id", "victory_margin", "victory_type"],
    "player_stats": ["id", "player_id", "format", "matches", "runs", "average", "strike_rate", "centuries", "fifties", "wickets", "economy"]
}

schema_col1, schema_col2 = st.columns(2)

with schema_col1:
    for table, columns in list(schema_info.items())[:3]:
        with st.expander(f"{table} table"):
            for col in columns:
                st.markdown(f"• `{col}`")

with schema_col2:
    for table, columns in list(schema_info.items())[3:]:
        with st.expander(f"{table} table"):
            for col in columns:
                st.markdown(f"• `{col}`")

with st.expander("SQL Query Tips"):
    st.markdown("""
    **Useful Patterns:**
    ```sql
    -- Join players with stats
    SELECT p.name, ps.runs FROM players p 
    JOIN player_stats ps ON p.id = ps.player_id;
    
    -- Filter by format
    WHERE ps.format = 'ODI';
    
    -- Group by country
    GROUP BY p.country;
    
    -- Order results
    ORDER BY ps.runs DESC LIMIT 10;
    ```
    
    **Common Filters:**
    - `ps.format IN ('ODI', 'Test', 'T20I')`
    - `p.country = 'India'`
    - `ps.matches >= 20`
    - `m.start_time >= datetime('now', '-30 days')`
    """)

st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        SQL Analytics | Execute queries on live cricket database
    </div>
    """, 
    unsafe_allow_html=True
)