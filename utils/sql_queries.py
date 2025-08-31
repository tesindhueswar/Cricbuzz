# 25 SQL practice queries mapped as {id: (title, sql)}
QUERIES = {
1: ("Players from India",
"""
SELECT name, role, batting_style, bowling_style
FROM players
WHERE country = 'India'
ORDER BY name;
"""),
2: ("Matches in last 30 days",
"""
SELECT m.description, t1.name AS team1, t2.name AS team2, v.name AS venue, v.city, m.start_time
FROM matches m
LEFT JOIN teams t1 ON m.team1_id = t1.id
LEFT JOIN teams t2 ON m.team2_id = t2.id
LEFT JOIN venues v ON m.venue_id = v.id
WHERE m.start_time >= datetime('now', '-30 days')
ORDER BY m.start_time DESC;
"""),
3: ("Top 10 ODI run scorers (sample schema)",
"""
SELECT p.name, ps.runs AS total_runs, ps.average AS batting_average
FROM player_stats ps
JOIN players p ON p.id = ps.player_id
WHERE ps.format = 'ODI'
ORDER BY ps.runs DESC
LIMIT 10;
"""),
4: ("Venues with capacity > 50k",
"""
SELECT name, city, country, capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC;
"""),
5: ("Team wins (requires winner_team_id)",
"""
SELECT t.name, COUNT(*) AS wins
FROM matches m
JOIN teams t ON t.id = m.winner_team_id
GROUP BY t.id
ORDER BY wins DESC;
"""),
6: ("Player count by role",
"""
SELECT role, COUNT(*) AS count_players
FROM players
GROUP BY role
ORDER BY count_players DESC;
"""),
7: ("Highest score per format (sample / placeholder)",
"""
SELECT format, MAX(runs) AS highest_runs
FROM player_stats
GROUP BY format;
"""),
8: ("Series started in 2024 (placeholder - depends on series table)",
"""
SELECT 'Add a series table to use this query' AS note;
"""),
9: ("All-rounders: >1000 runs & >50 wickets",
"""
SELECT p.name, ps.format, ps.runs, ps.wickets
FROM player_stats ps
JOIN players p ON p.id = ps.player_id
WHERE ps.runs > 1000 AND ps.wickets > 50;
"""),
10: ("Last 20 completed matches",
"""
SELECT m.description, t1.name AS team1, t2.name AS team2, t3.name AS winner, m.victory_margin, m.victory_type, v.name AS venue
FROM matches m
LEFT JOIN teams t1 ON m.team1_id = t1.id
LEFT JOIN teams t2 ON m.team2_id = t2.id
LEFT JOIN teams t3 ON m.winner_team_id = t3.id
LEFT JOIN venues v ON m.venue_id = v.id
WHERE m.winner_team_id IS NOT NULL
ORDER BY m.start_time DESC
LIMIT 20;
"""),
11: ("Player performance across formats",
"""
SELECT p.name,
       SUM(CASE WHEN ps.format='Test' THEN ps.runs ELSE 0 END) AS test_runs,
       SUM(CASE WHEN ps.format='ODI' THEN ps.runs ELSE 0 END) AS odi_runs,
       SUM(CASE WHEN ps.format='T20I' THEN ps.runs ELSE 0 END) AS t20_runs,
       ROUND(AVG(ps.average), 2) AS overall_avg
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
GROUP BY p.id
HAVING ( (test_runs>0) + (odi_runs>0) + (t20_runs>0) ) >= 2;
"""),
12: ("Home vs Away wins (simplified)",
"""
SELECT t.name AS team, SUM(CASE WHEN v.country = t.country THEN 1 ELSE 0 END) AS home_wins,
       SUM(CASE WHEN v.country <> t.country THEN 1 ELSE 0 END) AS away_wins
FROM matches m
JOIN teams t ON t.id = m.winner_team_id
JOIN venues v ON v.id = m.venue_id
GROUP BY t.id;
"""),
13: ("Batting partnerships (placeholder - needs ball-by-ball)",
"""
SELECT 'Requires innings/partnership tables' AS note;
"""),
14: ("Bowling performance per venue (placeholder)",
"""
SELECT 'Requires per-match bowling numbers' AS note;
"""),
15: ("Clutch performance in close matches (placeholder)",
"""
SELECT 'Requires per-match player batting details' AS note;
"""),
16: ("Yearly batting trends since 2020 (placeholder)",
"""
SELECT 'Requires per-match batting with dates' AS note;
"""),
17: ("Toss advantage (placeholder)",
"""
SELECT 'Add toss columns to matches to enable' AS note;
"""),
18: ("Most economical bowlers (limited overs)",
"""
SELECT p.name, ps.format, ps.economy, ps.wickets
FROM player_stats ps
JOIN players p ON p.id = ps.player_id
WHERE ps.format IN ('ODI','T20I') AND ps.matches >= 10
ORDER BY ps.economy ASC, ps.wickets DESC
LIMIT 20;
"""),
19: ("Consistency (avg & stddev placeholder)",
"""
SELECT 'SQLite stddev requires extension or custom UDF' AS note;
"""),
20: ("Matches played & batting avg by format (min 20 total)",
"""
WITH totals AS (
  SELECT player_id, SUM(matches) AS total_matches
  FROM player_stats
  GROUP BY player_id
)
SELECT p.name,
  SUM(CASE WHEN ps.format='Test' THEN ps.matches ELSE 0 END) AS test_matches,
  SUM(CASE WHEN ps.format='ODI' THEN ps.matches ELSE 0 END) AS odi_matches,
  SUM(CASE WHEN ps.format='T20I' THEN ps.matches ELSE 0 END) AS t20_matches,
  ROUND(AVG(CASE WHEN ps.average IS NOT NULL THEN ps.average END),2) AS avg_batting
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
JOIN totals t ON t.player_id = p.id
WHERE t.total_matches >= 20
GROUP BY p.id;
"""),
21: ("Weighted performance score",
"""
SELECT p.name, ps.format,
       ((ps.runs * 0.01) + (COALESCE(ps.average,0) * 0.5) + (COALESCE(ps.strike_rate,0) * 0.3)) +
       ((ps.wickets * 2) + ((50 - COALESCE(NULLIF(ps.average,0),50)) * 0.5) + ((6 - COALESCE(ps.economy,6)) * 2)) AS score
FROM player_stats ps
JOIN players p ON p.id = ps.player_id
ORDER BY score DESC
LIMIT 50;
"""),
22: ("Head-to-head prediction base (placeholder)",
"""
SELECT 'Requires match results by pair & toss/venue context' AS note;
"""),
23: ("Recent form (placeholder)",
"""
SELECT 'Requires last N innings per player' AS note;
"""),
24: ("Successful batting pairs (placeholder)",
"""
SELECT 'Requires partnership table' AS note;
"""),
25: ("Quarterly performance evolution (placeholder)",
"""
SELECT 'Requires dated per-innings data' AS note;
"""),
}
