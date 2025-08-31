from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    cricbuzz_id = Column(Integer, unique=True, nullable=True)  # Optional Cricbuzz team ID
    name = Column(String(100), nullable=False)
    short_name = Column(String(10), nullable=False)
    country = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    home_matches = relationship("Match", foreign_keys="[Match.team1_id]", back_populates="team1")
    away_matches = relationship("Match", foreign_keys="[Match.team2_id]", back_populates="team2")
    players = relationship("Player", back_populates="team")

class Venue(Base):
    __tablename__ = 'venues'
    
    id = Column(Integer, primary_key=True)
    cricbuzz_id = Column(Integer, unique=True, nullable=True)  # Optional Cricbuzz venue ID
    name = Column(String(100), nullable=False)
    city = Column(String(50))
    country = Column(String(50))
    capacity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    matches = relationship("Match", back_populates="venue")

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    cricbuzz_id = Column(Integer, unique=True, nullable=True)  # Optional Cricbuzz player ID
    name = Column(String(100), nullable=False)
    nickname = Column(String(50))
    role = Column(String(50))  # Batsman, Bowler, All-rounder, Wicket-keeper
    batting_style = Column(String(50))
    bowling_style = Column(String(50))
    team_id = Column(Integer, ForeignKey('teams.id'))
    country = Column(String(50))
    birth_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="players")
    stats = relationship("PlayerStats", back_populates="player")

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    cricbuzz_id = Column(Integer, unique=True, nullable=True)  # Optional Cricbuzz match ID
    series_id = Column(Integer)
    series_name = Column(String(100))
    match_desc = Column(String(200))
    match_format = Column(String(20))  # Test, ODI, T20I, T20
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    state = Column(String(20))  # Live, Complete, Upcoming
    status = Column(Text)
    result = Column(Text)
    team1_id = Column(Integer, ForeignKey('teams.id'))
    team2_id = Column(Integer, ForeignKey('teams.id'))
    venue_id = Column(Integer, ForeignKey('venues.id'))
    toss_winner_id = Column(Integer, ForeignKey('teams.id'))
    toss_decision = Column(String(20))  # bat, bowl
    match_winner_id = Column(Integer, ForeignKey('teams.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="home_matches")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="away_matches")
    venue = relationship("Venue", back_populates="matches")
    player_stats = relationship("PlayerStats", back_populates="match")

class PlayerStats(Base):
    __tablename__ = 'player_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    
    # Batting stats
    runs_scored = Column(Integer, default=0)
    balls_faced = Column(Integer, default=0)
    fours = Column(Integer, default=0)
    sixes = Column(Integer, default=0)
    strike_rate = Column(Float, default=0.0)
    is_out = Column(Boolean, default=False)
    dismissal_type = Column(String(50))
    
    # Bowling stats
    overs_bowled = Column(Float, default=0.0)
    runs_conceded = Column(Integer, default=0)
    wickets_taken = Column(Integer, default=0)
    economy_rate = Column(Float, default=0.0)
    dots_bowled = Column(Integer, default=0)
    
    # Fielding stats
    catches = Column(Integer, default=0)
    runouts = Column(Integer, default=0)
    stumpings = Column(Integer, default=0)
    
    innings_number = Column(Integer, default=1)  # 1st or 2nd innings
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="stats")
    match = relationship("Match", back_populates="player_stats")

# Export all models for easy import
__all__ = ['Base', 'Team', 'Venue', 'Player', 'Match', 'PlayerStats']