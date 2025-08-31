import streamlit as st
import logging
from datetime import datetime
from utils.api import get_live_matches, get_upcoming_matches, verify_api_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Live Matches", page_icon="📡", layout="wide")

st.title("📡 Live Cricket Matches")

# API Connection Status
# with st.expander("🔧 API Connection Status", expanded=False):
#     if st.button("Test API Connection"):
#         with st.spinner("Testing API connection..."):
#             is_connected = verify_api_connection()
#             if is_connected:
#                 st.success("✅ API connection successful!")
#             else:
#                 st.warning("⚠️ API connection failed. Using fallback data.")

# Create tabs
tab1, tab2 = st.tabs(["🔴 Live Matches", "📅 Upcoming Matches"])

def display_match_card(match_info, is_live=False):
    """Display a match card with match information"""
    try:
        team1 = match_info.get("team1", {})
        team2 = match_info.get("team2", {})
        venue_info = match_info.get("venueInfo", {})
        
        team1_name = team1.get("teamName", "Team 1")
        team2_name = team2.get("teamName", "Team 2")
        team1_short = team1.get("teamSName", "T1")
        team2_short = team2.get("teamSName", "T2")
        
        match_desc = match_info.get("matchDesc", f"{team1_name} vs {team2_name}")
        match_format = match_info.get("matchFormat", "Unknown")
        status = match_info.get("status", "No status available")
        venue_name = venue_info.get("ground", "Unknown Venue")
        city = venue_info.get("city", "Unknown City")
        
        # Create match card
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.markdown(f"**{team1_name}**")
                st.caption(f"({team1_short})")
            
            with col2:
                if is_live:
                    st.markdown("🔴 **LIVE**")
                else:
                    st.markdown("📅 **Upcoming**")
                st.caption(match_format)
            
            with col3:
                st.markdown(f"**{team2_name}**")
                st.caption(f"({team2_short})")
            
            st.markdown(f"**Status:** {status}")
            st.markdown(f"**Venue:** {venue_name}, {city}")
            
            if "startDate" in match_info:
                try:
                    start_time = datetime.fromisoformat(match_info["startDate"].replace("Z", "+00:00"))
                    st.caption(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M UTC')}")
                except:
                    st.caption(f"Start Time: {match_info['startDate']}")
            
            st.divider()
    
    except Exception as e:
        logger.error(f"Error displaying match card: {str(e)}")
        st.error(f"Error displaying match: {str(e)}")

def extract_matches_from_response(data):
    """Extract match list from API response"""
    matches = []
    try:
        if "typeMatches" in data:
            for type_match in data["typeMatches"]:
                if "seriesMatches" in type_match:
                    for series_match in type_match["seriesMatches"]:
                        if "seriesAdWrapper" in series_match:
                            series_matches = series_match["seriesAdWrapper"].get("matches", [])
                            for match in series_matches:
                                if "matchInfo" in match:
                                    matches.append(match["matchInfo"])
        return matches
    except Exception as e:
        logger.error(f"Error extracting matches: {str(e)}")
        return []

# Live Matches Tab
with tab1:
    st.subheader("🔴 Live Matches")
    
    with st.spinner("Loading live matches..."):
        try:
            live_data = get_live_matches()
            live_matches = extract_matches_from_response(live_data)
            
            if live_matches:
                st.success(f"Found {len(live_matches)} live match(es)")
                for match in live_matches:
                    display_match_card(match, is_live=True)
            else:
                st.info("No live matches found at the moment.")
                st.caption("This could be because:")
                st.caption("• No matches are currently being played")
                st.caption("• API returned empty results")
                st.caption("• Using fallback sample data")
                
        except Exception as e:
            logger.error(f"Error loading live matches: {str(e)}")
            st.error("Failed to load live matches. Please check your API connection.")

# Upcoming Matches Tab
with tab2:
    st.subheader("📅 Upcoming Matches")
    
    with st.spinner("Loading upcoming matches..."):
        try:
            upcoming_data = get_upcoming_matches()
            upcoming_matches = extract_matches_from_response(upcoming_data)
            
            if upcoming_matches:
                st.success(f"Found {len(upcoming_matches)} upcoming match(es)")
                for match in upcoming_matches:
                    display_match_card(match, is_live=False)
            else:
                st.info("No upcoming matches found.")
                st.caption("This could be because:")
                st.caption("• No matches are scheduled")
                st.caption("• API returned empty results") 
                st.caption("• Using fallback sample data")
                
        except Exception as e:
            logger.error(f"Error loading upcoming matches: {str(e)}")
            st.error("Failed to load upcoming matches. Please check your API connection.")

# Refresh section
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🔄 Refresh Data", type="primary"):
        st.rerun()

# Debug information
with st.expander("🐛 Debug Information", expanded=False):
    st.caption("For troubleshooting API issues")
    
    if st.button("Show Raw Live Data"):
        try:
            raw_data = get_live_matches()
            st.json(raw_data)
        except Exception as e:
            st.error(f"Error getting raw data: {str(e)}")
    
    if st.button("Show Raw Upcoming Data"):
        try:
            raw_data = get_upcoming_matches()
            st.json(raw_data)
        except Exception as e:
            st.error(f"Error getting raw data: {str(e)}")