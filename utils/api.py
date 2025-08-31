import os
import requests
import logging
import time
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CricbuzzAPIError(Exception):
    """Custom exception for Cricbuzz API errors"""
    pass

class CricbuzzAPI:
    """
    Thin wrapper over Cricbuzz (RapidAPI) with safe fallbacks.
    This class NEVER raises on missing API key; instead it logs and uses fallbacks.
    """
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.base_url = "https://cricbuzz-cricket.p.rapidapi.com"
        self.enabled = bool(self.api_key)

        if self.enabled:
            self.headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com",
            }
            masked = f"{self.api_key[:5]}...{self.api_key[-4:]}" if len(self.api_key) > 9 else "***"
            logger.info(f"[CricbuzzAPI] API key loaded (masked): {masked}")
        else:
            self.headers = {}
            logger.warning("[CricbuzzAPI] RAPIDAPI_KEY not set. Falling back to sample data.")

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP GET with basic retry; returns fallback if disabled or on failure."""
        if not self.enabled:
            return {}

        url = f"{self.base_url}/{endpoint}"
        for attempt in range(3):
            try:
                logger.info(f"[CricbuzzAPI] GET {endpoint} (attempt {attempt+1})")
                resp = requests.get(url, headers=self.headers, params=params, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    return data if isinstance(data, dict) else {"data": data}
                if resp.status_code == 429 and attempt < 2:
                    # Exponential backoff on rate limit
                    time.sleep(2 ** attempt)
                    continue
                logger.error(f"[CricbuzzAPI] {endpoint} failed {resp.status_code}: {resp.text[:200]}")
            except requests.RequestException as e:
                logger.error(f"[CricbuzzAPI] request error: {e}")
                if attempt < 2:
                    time.sleep(1.0)

        logger.warning(f"[CricbuzzAPI] Failed to get data for {endpoint}")
        return {}

    def get_trending_players(self) -> Dict[str, Any]:
        """
        Get trending players data from Cricbuzz API.
        Returns raw API response without fallback data.
        """
        return self._make_request("stats/v1/player/trending")

    def get_top_performers(self, category: str = "batting") -> Dict[str, Any]:
        """
        Get top performers in different categories (batting, bowling, allrounder).
        
        Args:
            category: "batting", "bowling", or "allrounder"
        """
        return self._make_request(f"stats/v1/rankings/{category}")

    def get_player_career_stats(self, player_id: int, format_type: str = "all") -> Dict[str, Any]:
        """
        Get detailed career statistics for a specific player.
        
        Args:
            player_id: Player ID from Cricbuzz
            format_type: "test", "odi", "t20i", or "all"
        """
        endpoint = f"stats/v1/player/{player_id}"
        if format_type != "all":
            endpoint += f"/{format_type}"
        return self._make_request(endpoint)

    def search_players(self, query: str) -> Dict[str, Any]:
        """
        Search for players by name.
        
        Args:
            query: Player name or partial name to search
        """
        return self._make_request("stats/v1/player/search", params={"q": query})

    def get_current_rankings(self, format_type: str, category: str) -> Dict[str, Any]:
        """
        Get current ICC rankings.
        
        Args:
            format_type: "test", "odi", "t20i"
            category: "batting", "bowling", "allrounder", "teams"
        """
        return self._make_request(f"stats/v1/rankings/{format_type}/{category}")

# ---- Module-level convenience (imported by pages) ----
_api_instance: Optional[CricbuzzAPI] = None

def get_api_instance() -> CricbuzzAPI:
    global _api_instance
    if _api_instance is None:
        _api_instance = CricbuzzAPI()
    return _api_instance

# Live/Upcoming/Recent
def get_live_matches() -> Dict[str, Any]:
    api = get_api_instance()
    return api._make_request("matches/v1/live")

def get_upcoming_matches() -> Dict[str, Any]:
    api = get_api_instance()
    return api._make_request("matches/v1/upcoming")

def get_recent_matches() -> Dict[str, Any]:
    api = get_api_instance()
    return api._make_request("matches/v1/recent")

# Scorecard
def get_match_scorecard(match_id: int) -> Dict[str, Any]:
    api = get_api_instance()
    return api._make_request(f"mcenter/v1/{match_id}/scard")

# ---- Previously missing (added) ----
def get_player_stats(player_id: int) -> Dict[str, Any]:
    """
    Returns aggregate player stats (tests/odis/t20is, etc).
    NOTE: This reads from API if configured, otherwise returns a safe fallback.
    """
    api = get_api_instance()
    # Many RapidAPI mirrors expose stats under this path:
    return api._make_request(f"stats/v1/player/{player_id}")

def get_player_info(player_id: int) -> Dict[str, Any]:
    """
    Returns core player profile info (name, role, battingStyle, bowlingStyle, intlTeam).
    If the upstream returns stats+info in one endpoint, we just reuse it and subset.
    """
    api = get_api_instance()
    data = api._make_request(f"stats/v1/player/{player_id}")
    # Normalize to a simple predictable shape for the UI
    return {
        "id": player_id,
        "name": data.get("name"),
        "role": data.get("role"),
        "battingStyle": data.get("battingStyle"),
        "bowlingStyle": data.get("bowlingStyle"),
        "intlTeam": data.get("intlTeam"),
        "raw": data,  # keep original for advanced pages if needed
    }

def get_team_players(team_id: int) -> Dict[str, Any]:
    """
    Returns a list of players for a team (does NOT depend on your local DB and does NOT
    assume any 'team_id' column in Player). Safe fallback shape:
    {
        "teamId": int,
        "teamName": str | None,
        "players": [
            {"id": int|None, "name": str, "country": str|None, "role": str|None,
             "battingStyle": str|None, "bowlingStyle": str|None},
            ...
        ]
    }
    """
    api = get_api_instance()
    # Team squad endpoints can vary; we provide a generic path with fallback.
    data = api._make_request(f"teams/v1/{team_id}/players")
    # Ensure shape
    players = data.get("players")
    if isinstance(players, list):
        normalized = []
        for p in players:
            normalized.append({
                "id": p.get("id"),
                "name": p.get("name") or p.get("fullName") or p.get("playerName"),
                "country": p.get("country") or p.get("intlTeam") or None,
                "role": p.get("role"),
                "battingStyle": p.get("battingStyle"),
                "bowlingStyle": p.get("bowlingStyle"),
            })
        data["players"] = normalized
    return data

# New trending and ranking functions
def get_trending_players() -> Dict[str, Any]:
    """Get trending players data"""
    api = get_api_instance()
    return api.get_trending_players()

def get_top_performers(category: str = "batting") -> Dict[str, Any]:
    """Get top performers by category"""
    api = get_api_instance()
    return api.get_top_performers(category)

def get_player_career_stats(player_id: int, format_type: str = "all") -> Dict[str, Any]:
    """Get player career statistics"""
    api = get_api_instance()
    return api.get_player_career_stats(player_id, format_type)

def search_players(query: str) -> Dict[str, Any]:
    """Search for players by name"""
    api = get_api_instance()
    return api.search_players(query)

def get_current_rankings(format_type: str, category: str) -> Dict[str, Any]:
    """Get current ICC rankings"""
    api = get_api_instance()
    return api.get_current_rankings(format_type, category)

# Connectivity check
def verify_api_connection() -> bool:
    try:
        data = get_live_matches()
        return bool(data) and not data.get("error")
    except Exception as e:
        logger.error(f"[CricbuzzAPI] verify failed: {e}")
        return False