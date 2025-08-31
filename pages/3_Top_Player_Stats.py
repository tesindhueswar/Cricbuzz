import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional
import logging

# Import your API functions
from utils.api import get_trending_players, verify_api_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_trending_api():
    """Test the trending players API using your wrapper"""
    try:
        data = get_trending_players()
        st.info("API Response received")
        
        if data and not data.get("error"):
            st.success("API call successful!")
            st.write("Response type:", type(data))
            
            if isinstance(data, dict):
                st.write("Response keys:", list(data.keys()))
                st.json(data)
            elif isinstance(data, list):
                st.write(f"Response list length: {len(data)}")
                if data:
                    st.write("First item:", data[0])
                st.json(data[:3])  # Show first 3 items
            
            return data
        else:
            st.error("API returned error or empty data")
            return None
            
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def extract_player_stats_from_trending(trending_data) -> List[Dict]:
    """Extract player statistics from trending players API response"""
    players = []
    
    try:
        # Handle different possible response structures
        if isinstance(trending_data, list):
            raw_players = trending_data
        elif isinstance(trending_data, dict):
            # Could be nested in various ways
            if 'players' in trending_data:
                raw_players = trending_data['players']
            elif 'data' in trending_data:
                raw_players = trending_data['data']
            elif 'trendingPlayers' in trending_data:
                raw_players = trending_data['trendingPlayers']
            else:
                # Take the first list value we find
                for key, value in trending_data.items():
                    if isinstance(value, list):
                        raw_players = value
                        break
                else:
                    st.warning("Could not find player data in API response")
                    return []
        else:
            st.error("Unexpected API response format")
            return []
        
        logger.info(f"Processing {len(raw_players)} players from trending data")
        
        for player_data in raw_players:
            if not isinstance(player_data, dict):
                continue
                
            # Extract basic info
            name = (player_data.get('name') or 
                   player_data.get('playerName') or 
                   player_data.get('fullName') or 'Unknown')
            
            # Extract stats - API structure may vary
            stats = player_data.get('stats', {})
            batting_stats = stats.get('batting', {}) if stats else player_data.get('batting', {})
            bowling_stats = stats.get('bowling', {}) if stats else player_data.get('bowling', {})
            
            # Create normalized player record
            player = {
                'name': name,
                'team': player_data.get('team', 'Unknown'),
                'country': player_data.get('country') or player_data.get('team', 'Unknown'),
                'role': player_data.get('role', 'Unknown'),
                
                # Batting stats
                'runs': batting_stats.get('runs', 0) or player_data.get('runs', 0),
                'balls_faced': batting_stats.get('balls', 0) or player_data.get('balls', 0),
                'fours': batting_stats.get('fours', 0) or player_data.get('fours', 0),
                'sixes': batting_stats.get('sixes', 0) or player_data.get('sixes', 0),
                'strike_rate': batting_stats.get('strikeRate', 0) or player_data.get('strikeRate', 0),
                'highest_score': batting_stats.get('highestScore', 0) or player_data.get('highestScore', 0),
                
                # Bowling stats
                'wickets': bowling_stats.get('wickets', 0) or player_data.get('wickets', 0),
                'overs_bowled': bowling_stats.get('overs', 0) or player_data.get('overs', 0),
                'runs_conceded': bowling_stats.get('runsConceded', 0) or player_data.get('runsConceded', 0),
                'economy_rate': bowling_stats.get('economyRate', 0) or player_data.get('economyRate', 0),
                'best_figures': bowling_stats.get('bestFigures', 'N/A') or player_data.get('bestFigures', 'N/A'),
                
                # General stats
                'matches': player_data.get('matches', 1),
                'average': player_data.get('average', 0),
                'format': player_data.get('format', 'Unknown'),
                'recent_form': player_data.get('recentForm', 'Unknown'),
                'trending_score': player_data.get('trendingScore', 0),
                'rank': player_data.get('rank', 0)
            }
            
            # Calculate missing values
            if player['runs'] > 0 and player['balls_faced'] > 0 and player['strike_rate'] == 0:
                player['strike_rate'] = round((player['runs'] / player['balls_faced']) * 100, 2)
            
            if player['overs_bowled'] > 0 and player['runs_conceded'] > 0 and player['economy_rate'] == 0:
                player['economy_rate'] = round(player['runs_conceded'] / player['overs_bowled'], 2)
            
            players.append(player)
            logger.debug(f"Added player: {name}")
        
        logger.info(f"Successfully processed {len(players)} players")
        return players
        
    except Exception as e:
        logger.error(f"Error processing trending players data: {str(e)}")
        st.error(f"Error processing player data: {str(e)}")
        return []

def create_trending_chart(players_data: List[Dict], metric: str = 'trending_score') -> go.Figure:
    """Create chart for trending players"""
    try:
        if not players_data:
            return go.Figure().add_annotation(text="No trending data available", showarrow=False)
        
        # Sort by the metric and take top 15
        sorted_data = sorted([p for p in players_data if p.get(metric, 0) > 0], 
                           key=lambda x: x.get(metric, 0), reverse=True)[:15]
        
        if not sorted_data:
            return go.Figure().add_annotation(text=f"No {metric} data available", showarrow=False)
        
        df = pd.DataFrame(sorted_data)
        
        title_map = {
            'trending_score': 'Trending Players Score',
            'runs': 'Top Run Scorers',
            'wickets': 'Top Wicket Takers',
            'strike_rate': 'Best Strike Rates',
            'economy_rate': 'Best Economy Rates'
        }
        
        fig = px.bar(
            df, 
            x="name", 
            y=metric,
            color="country",
            title=title_map.get(metric, f"Top {metric}"),
            hover_data=["team", "role", "matches"],
            text=metric
        )
        
        fig.update_traces(textposition='outside', textfont_size=10)
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            xaxis_title="Player",
            yaxis_title=metric.replace('_', ' ').title(),
            showlegend=True
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating chart: {str(e)}")
        return go.Figure().add_annotation(text="Chart creation error", showarrow=False)

def main():
    st.set_page_config(
        page_title="Trending Cricket Players",
        layout="wide"
    )
    
    st.title("Trending Cricket Players")
    st.markdown("**Live data from Cricbuzz Trending Players API**")
    
    # API Connection Status
    with st.sidebar:
        st.header("API Status")
        if verify_api_connection():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Unavailable")
    
    # Test API section
    with st.expander("🔧 Test API Connection", expanded=False):
        if st.button("Test Trending Players API"):
            with st.spinner("Testing API..."):
                api_data = test_trending_api()
    
    # Main data fetching
    if st.button("Get Trending Players Data", type="primary"):
        with st.spinner("Fetching trending players..."):
            try:
                trending_data = get_trending_players()
                
                if trending_data and not trending_data.get("error"):
                    st.success("API call successful!")
                    
                    # Store in session state
                    st.session_state['trending_data'] = trending_data
                    st.session_state['players_data'] = extract_player_stats_from_trending(trending_data)
                    
                    st.info(f"Processed {len(st.session_state['players_data'])} players")
                else:
                    st.error("Failed to fetch trending players data")
                    
            except Exception as e:
                st.error(f"Failed to fetch data: {str(e)}")
    
    # Display data if available
    if 'players_data' in st.session_state and st.session_state['players_data']:
        players_data = st.session_state['players_data']
        
        st.markdown("---")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_players = len(players_data)
            st.metric("Total Players", total_players)
        
        with col2:
            countries = len(set(p['country'] for p in players_data))
            st.metric("Countries", countries)
        
        with col3:
            total_runs = sum(p.get('runs', 0) for p in players_data)
            st.metric("Total Runs", f"{total_runs:,}")
        
        with col4:
            total_wickets = sum(p.get('wickets', 0) for p in players_data)
            st.metric("Total Wickets", total_wickets)
        
        # Filters
        with st.sidebar:
            st.header("Filters")
            
            countries = sorted(list(set(p['country'] for p in players_data)))
            selected_countries = st.multiselect("Countries", countries, default=countries)
            
            roles = sorted(list(set(p['role'] for p in players_data if p['role'] != 'Unknown')))
            selected_roles = st.multiselect("Roles", roles, default=roles)
            
            formats = sorted(list(set(p['format'] for p in players_data if p['format'] != 'Unknown')))
            if formats:
                selected_formats = st.multiselect("Formats", formats, default=formats)
            else:
                selected_formats = []
        
        # Apply filters
        filtered_data = [
            p for p in players_data 
            if (p['country'] in selected_countries and 
                p['role'] in selected_roles and
                (not selected_formats or p['format'] in selected_formats))
        ]
        
        if not filtered_data:
            st.warning("No players match the selected filters")
            return
        
        # Charts and tables (rest of your existing display code)
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Trending", "🏏 Batting", "🎯 Bowling", "📊 Details"])
        
        with tab1:
            st.subheader("Trending Players")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_trending = create_trending_chart(filtered_data, 'trending_score')
                st.plotly_chart(fig_trending, use_container_width=True)
            
            with col2:
                # Top performers table
                trending_players = sorted([p for p in filtered_data if p.get('trending_score', 0) > 0], 
                                        key=lambda x: x.get('trending_score', 0), reverse=True)[:10]
                
                if trending_players:
                    st.markdown("**Top 10 Trending Players**")
                    for i, player in enumerate(trending_players, 1):
                        st.write(f"{i}. **{player['name']}** ({player['country']}) - Score: {player.get('trending_score', 0)}")
        
        # Rest of your tabs implementation...
        
        # Refresh button
        st.markdown("---")
        if st.button("Refresh Data"):
            if 'trending_data' in st.session_state:
                del st.session_state['trending_data']
            if 'players_data' in st.session_state:
                del st.session_state['players_data']
            st.rerun()
    
    else:
        st.info("Click 'Get Trending Players Data' to fetch live cricket statistics")

if __name__ == "__main__":
    main()