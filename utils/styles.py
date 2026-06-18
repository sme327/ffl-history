"""CSS injection and reusable HTML components."""
import streamlit as st
from utils.data import MANAGER_EMOJI


_CSS = """
        .stApp { background-color: #081120 !important; }
        .main  { background-color: #081120 !important; }
        #MainMenu { visibility: hidden; }
        footer    { visibility: hidden; }
        header    { visibility: hidden; }
        [data-testid="stSidebar"]        { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        .main .block-container {
            padding-top: 80px !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 1280px;
        }
        .tl-nav {
            position: fixed;
            top: 0; left: 0; right: 0;
            z-index: 9999;
            background: #081120;
            border-bottom: 1px solid #B8902E;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2.5rem;
            height: 62px;
        }
        .tl-nav-brand {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.35rem;
            color: #D4AF37;
            letter-spacing: 5px;
            text-decoration: none !important;
        }
        .tl-nav-links { display: flex; gap: 2rem; align-items: center; }
        .tl-nav-link {
            font-family: 'Inter', sans-serif;
            font-size: 0.7rem;
            font-weight: 500;
            color: #A7B0BC;
            text-decoration: none !important;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 4px 0;
            border-bottom: 2px solid transparent;
            transition: color 0.2s, border-color 0.2s;
        }
        .tl-nav-link:hover { color: #D4AF37; border-bottom-color: #D4AF37; }
        .tl-nav-link.active { color: #D4AF37; border-bottom-color: #D4AF37; }
        .tl-hero { text-align: center; padding: 2.5rem 0 1.5rem; }
        .tl-hero-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 5rem;
            color: #D4AF37;
            letter-spacing: 10px;
            line-height: 1;
            margin: 0;
        }
        .tl-hero-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            color: #A7B0BC;
            letter-spacing: 6px;
            text-transform: uppercase;
            margin-top: 0.5rem;
        }
        .tl-page-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3.2rem;
            color: #D4AF37;
            letter-spacing: 6px;
            line-height: 1;
            margin: 0;
        }
        .tl-page-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #A7B0BC;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 0.3rem;
            margin-bottom: 1.5rem;
        }
        .tl-divider {
            height: 1px;
            background: linear-gradient(to right, transparent, #D4AF37, transparent);
            margin: 1.5rem auto;
            border: none;
        }
        .tl-divider-full {
            height: 1px;
            background: #B8902E;
            margin: 1.5rem 0;
            opacity: 0.4;
            border: none;
        }
        .tl-section-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.65rem;
            color: #A7B0BC;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        .tl-section-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.8rem;
            color: #F5F5F5;
            letter-spacing: 3px;
            margin: 0 0 1rem 0;
        }
        .tl-metric {
            background: #0F1B2D;
            border: 1px solid #B8902E;
            border-radius: 8px;
            padding: 1.4rem 1rem;
            text-align: center;
        }
        .tl-metric-value {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3.2rem;
            color: #D4AF37;
            line-height: 1;
            margin: 0;
        }
        .tl-metric-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.62rem;
            color: #A7B0BC;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 0.4rem;
        }
        .tl-card {
            background: #0F1B2D;
            border: 1px solid #B8902E;
            border-radius: 8px;
            padding: 1.5rem;
        }
        .tl-card-gold {
            background: #0F1B2D;
            border: 1px solid #D4AF37;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 0 30px rgba(212,175,55,0.08);
        }
        .tl-champion-card {
            background: #0F1B2D;
            border: 2px solid #D4AF37;
            border-radius: 12px;
            padding: 2.5rem 2rem;
            text-align: center;
            box-shadow: 0 0 50px rgba(212,175,55,0.12);
        }
        .tl-champion-season {
            font-family: 'Inter', sans-serif;
            font-size: 0.7rem;
            color: #A7B0BC;
            letter-spacing: 4px;
            text-transform: uppercase;
        }
        .tl-champion-team {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3.2rem;
            color: #D4AF37;
            letter-spacing: 4px;
            line-height: 1;
            margin: 0.4rem 0 0.2rem;
        }
        .tl-champion-manager {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            color: #F5F5F5;
            font-weight: 500;
        }
        .tl-champion-score {
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            color: #A7B0BC;
            margin-top: 0.75rem;
        }
        .tl-mini-champ {
            background: #0F1B2D;
            border: 1px solid #B8902E;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        .tl-mini-champ-year {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.4rem;
            color: #D4AF37;
            letter-spacing: 2px;
            line-height: 1;
        }
        .tl-mini-champ-team {
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            color: #F5F5F5;
            font-weight: 500;
            margin-top: 0.3rem;
        }
        .tl-mini-champ-mgr {
            font-family: 'Inter', sans-serif;
            font-size: 0.68rem;
            color: #A7B0BC;
            margin-top: 0.1rem;
        }
        .tl-nav-card {
            background: #0F1B2D;
            border: 1px solid #B8902E;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            text-decoration: none !important;
            display: block;
            transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
        }
        .tl-nav-card:hover {
            border-color: #D4AF37;
            box-shadow: 0 0 20px rgba(212,175,55,0.1);
            transform: translateY(-2px);
        }
        .tl-nav-card-icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .tl-nav-card-title {
            font-family: 'Oswald', sans-serif;
            font-size: 0.95rem;
            color: #D4AF37;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .tl-nav-card-desc {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #A7B0BC;
            margin-top: 0.3rem;
            line-height: 1.4;
        }
        .tl-trophy-card {
            background: #0F1B2D;
            border: 1px solid #B8902E;
            border-radius: 8px;
            padding: 1.2rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .tl-trophy-card.gold-border { border-color: #D4AF37; }
        .tl-trophy-count {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2.8rem;
            color: #D4AF37;
            line-height: 1;
            min-width: 2rem;
            text-align: center;
        }
        .tl-trophy-name {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            color: #F5F5F5;
            font-weight: 600;
        }
        .tl-trophy-years {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #A7B0BC;
            margin-top: 0.15rem;
        }
        .tl-avatar {
            border-radius: 50%;
            background: #0F1B2D;
            border: 2px solid #D4AF37;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            box-shadow: 0 0 20px rgba(212,175,55,0.15);
        }
        .tl-profile-name {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2.6rem;
            color: #D4AF37;
            letter-spacing: 4px;
            line-height: 1;
            margin: 0.5rem 0 0.1rem;
        }
        .tl-profile-meta {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #A7B0BC;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .tl-timeline {
            display: flex;
            align-items: flex-start;
            gap: 0;
            padding: 1rem 0;
            overflow-x: auto;
        }
        .tl-steward {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 100px;
            flex: 1;
        }
        .tl-steward-avatar {
            width: 60px; height: 60px;
            border-radius: 50%;
            background: #0F1B2D;
            border: 2px solid #B8902E;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.6rem;
        }
        .tl-steward.current .tl-steward-avatar {
            border-color: #D4AF37;
            box-shadow: 0 0 20px rgba(212,175,55,0.25);
        }
        .tl-steward-name {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            color: #F5F5F5;
            text-align: center;
            margin-top: 0.4rem;
        }
        .tl-steward.current .tl-steward-name { color: #D4AF37; }
        .tl-steward-years {
            font-family: 'Inter', sans-serif;
            font-size: 0.65rem;
            color: #A7B0BC;
            text-align: center;
        }
        .tl-steward-champs {
            font-family: 'Inter', sans-serif;
            font-size: 0.68rem;
            color: #D4AF37;
            text-align: center;
            margin-top: 0.2rem;
        }
        .tl-connector {
            flex: 1;
            height: 2px;
            background: #B8902E;
            margin-top: 30px;
            min-width: 16px;
        }
        .tl-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
        }
        .tl-table th {
            background: #0F1B2D;
            color: #D4AF37;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-size: 0.68rem;
            padding: 0.7rem 1rem;
            border-bottom: 1px solid #B8902E;
            text-align: left;
        }
        .tl-table td {
            padding: 0.6rem 1rem;
            color: #F5F5F5;
            border-bottom: 1px solid rgba(184,144,46,0.12);
        }
        .tl-table tr:last-child td { border-bottom: none; }
        .tl-table tr:hover td { background: rgba(212,175,55,0.04); }
        .tl-table .gold  { color: #D4AF37; font-weight: 600; }
        .tl-table .muted { color: #A7B0BC; }
        .tl-table .center { text-align: center; }
        .tl-table .right  { text-align: right; }
        div[data-testid="stMarkdownContainer"] p { color: #F5F5F5; }
        .stSelectbox > label { color: #A7B0BC !important; font-family: 'Inter', sans-serif; font-size: 0.75rem !important; letter-spacing: 2px; text-transform: uppercase; }
        div[data-baseweb="select"] { background: #0F1B2D !important; border-color: #B8902E !important; }
        .tl-bracket { display: flex; gap: 1.5rem; align-items: flex-start; overflow-x: auto; padding: 1rem 0; }
        .tl-bracket-round { display: flex; flex-direction: column; gap: 1rem; min-width: 210px; flex: 1; }
        .tl-bracket-round-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.6rem;
            color: #A7B0BC;
            letter-spacing: 3px;
            text-transform: uppercase;
            text-align: center;
            margin-bottom: 0.25rem;
        }
        .tl-matchup {
            background: #0F1B2D;
            border: 1px solid #B8902E;
            border-radius: 8px;
            overflow: hidden;
        }
        .tl-matchup.champion-game { border-color: #D4AF37; box-shadow: 0 0 20px rgba(212,175,55,0.15); }
        .tl-matchup-team {
            display: flex;
            align-items: center;
            padding: 0.5rem 0.75rem;
            gap: 0.6rem;
            border-bottom: 1px solid rgba(184,144,46,0.2);
            color: #A7B0BC;
        }
        .tl-matchup-team:last-child { border-bottom: none; }
        .tl-matchup-team.winner { color: #D4AF37; background: rgba(212,175,55,0.06); font-weight: 600; }
        .tl-matchup-seed { font-family: 'Inter', sans-serif; font-size: 0.62rem; min-width: 1.6rem; opacity: 0.7; }
        .tl-matchup-name { font-family: 'Inter', sans-serif; font-size: 0.78rem; flex: 1; }
        .tl-matchup-score { font-family: 'Bebas Neue', sans-serif; font-size: 1rem; letter-spacing: 1px; }
        .tl-bracket-spacer { flex: 1; }
        .tl-dynasty-card {
            background: #0F1B2D;
            border: 2px solid #D4AF37;
            border-radius: 12px;
            padding: 2rem 1.5rem;
            text-align: center;
            box-shadow: 0 0 30px rgba(212,175,55,0.10);
        }
        .tl-chron-entry {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.65rem 0.5rem;
            border-bottom: 1px solid rgba(184,144,46,0.12);
        }
        .tl-chron-entry:last-child { border-bottom: none; }
        .tl-chron-mgr-col {
            min-width: 170px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.82rem;
            color: #F5F5F5;
            font-weight: 600;
            flex-shrink: 0;
        }
        .tl-chron-pills-col {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            flex: 1;
        }
        .tl-year-dot-gold {
            background: rgba(212,175,55,0.85);
            color: #081120;
            font-family: 'Bebas Neue', sans-serif;
            font-size: 0.85rem;
            letter-spacing: 1px;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
        }
        .tl-year-dot-solo {
            background: rgba(184,144,46,0.15);
            color: #A7B0BC;
            font-family: 'Bebas Neue', sans-serif;
            font-size: 0.85rem;
            letter-spacing: 1px;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            border: 1px solid rgba(184,144,46,0.25);
        }
        .tl-franchise-story {
            background: #0F1B2D;
            border-left: 3px solid #D4AF37;
            border-radius: 0 8px 8px 0;
            padding: 1.5rem 2rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.92rem;
            color: #E8E8E8;
            line-height: 1.9;
            font-style: italic;
        }
        .tl-steward-rich {
            background: #0F1B2D;
            border: 1px solid #B8902E;
            border-radius: 10px;
            padding: 1.2rem 1rem;
            text-align: center;
            flex: 1;
            min-width: 120px;
        }
        .tl-steward-rich.current {
            border-color: #D4AF37;
            box-shadow: 0 0 25px rgba(212,175,55,0.18);
        }
        .tl-steward-rich-avatar {
            width: 52px; height: 52px;
            border-radius: 50%;
            background: #162236;
            border: 2px solid #B8902E;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            margin: 0 auto 0.5rem;
        }
        .tl-steward-rich.current .tl-steward-rich-avatar {
            border-color: #D4AF37;
            box-shadow: 0 0 16px rgba(212,175,55,0.3);
        }
        .tl-steward-rich-name {
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 700;
            color: #F5F5F5;
            margin-bottom: 0.1rem;
        }
        .tl-steward-rich.current .tl-steward-rich-name { color: #D4AF37; }
        .tl-steward-rich-years {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 0.95rem;
            color: #A7B0BC;
            letter-spacing: 2px;
        }
        .tl-steward-rich-divider {
            height: 1px;
            background: rgba(184,144,46,0.25);
            margin: 0.65rem 0;
        }
        .tl-steward-rich-stat-val {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.25rem;
            color: #D4AF37;
            line-height: 1;
        }
        .tl-steward-rich-stat-lbl {
            font-family: 'Inter', sans-serif;
            font-size: 0.58rem;
            color: #A7B0BC;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .tl-milestone-item {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            padding: 0.5rem 0;
        }
        .tl-milestone-year {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.15rem;
            color: #D4AF37;
            letter-spacing: 2px;
            min-width: 52px;
            flex-shrink: 0;
            line-height: 1.4;
        }
        .tl-milestone-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #D4AF37;
            flex-shrink: 0;
            margin-top: 5px;
        }
        .tl-milestone-line {
            position: relative;
        }
        .tl-milestone-event {
            font-family: 'Inter', sans-serif;
            font-size: 0.82rem;
            color: #E8E8E8;
            line-height: 1.4;
        }
        .tl-milestone-event .sub {
            font-size: 0.7rem;
            color: #A7B0BC;
            margin-top: 0.05rem;
        }
        .tl-achievement-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.7rem 0.9rem;
            background: #0F1B2D;
            border: 1px solid rgba(184,144,46,0.3);
            border-radius: 8px;
        }
        .tl-achievement-icon { font-size: 1.3rem; flex-shrink: 0; }
        .tl-achievement-val {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.4rem;
            color: #D4AF37;
            line-height: 1;
        }
        .tl-achievement-lbl {
            font-family: 'Inter', sans-serif;
            font-size: 0.65rem;
            color: #A7B0BC;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .tl-rival-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.7rem 1rem;
            border-bottom: 1px solid rgba(184,144,46,0.12);
        }
        .tl-rival-row:last-child { border-bottom: none; }
        .tl-rival-row:hover { background: rgba(212,175,55,0.03); }
        .tl-tl-year-header {
            display: flex;
            align-items: center;
            gap: 1.2rem;
            margin: 2.25rem 0 0.75rem;
        }
        .tl-tl-year-num {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2.8rem;
            color: #D4AF37;
            letter-spacing: 4px;
            line-height: 1;
            min-width: 80px;
        }
        .tl-tl-year-line {
            height: 1px;
            flex: 1;
            background: linear-gradient(to right, rgba(184,144,46,0.6), transparent);
        }
        .tl-tl-year-count {
            font-family: 'Inter', sans-serif;
            font-size: 0.58rem;
            color: #A7B0BC;
            letter-spacing: 3px;
            text-transform: uppercase;
            flex-shrink: 0;
        }
        .tl-event-card {
            display: flex;
            gap: 0.85rem;
            padding: 0.8rem 1rem;
            background: #0F1B2D;
            border-radius: 0 8px 8px 0;
            margin-bottom: 0.5rem;
        }
        .tl-event-card-body { flex: 1; min-width: 0; }
        .tl-event-card-meta {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.25rem;
            flex-wrap: wrap;
        }
        .tl-event-type-tag {
            font-family: 'Inter', sans-serif;
            font-size: 0.55rem;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        .tl-editorial-badge {
            font-family: 'Inter', sans-serif;
            font-size: 0.52rem;
            color: #D4AF37;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0.7;
            border: 1px solid rgba(212,175,55,0.4);
            padding: 1px 5px;
            border-radius: 3px;
        }
        .tl-event-title {
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            font-weight: 600;
            color: #F5F5F5;
            line-height: 1.3;
        }
        .tl-event-title.high { font-size: 0.92rem; }
        .tl-event-desc {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #A7B0BC;
            margin-top: 0.2rem;
            line-height: 1.5;
        }
        .tl-event-mgr {
            font-family: 'Inter', sans-serif;
            font-size: 0.62rem;
            color: #6B7280;
            margin-top: 0.25rem;
            letter-spacing: 1px;
        }
        .tl-filter-bar {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            padding: 0.75rem 0;
        }
        .tl-filter-pill {
            font-family: 'Inter', sans-serif;
            font-size: 0.62rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 0.3rem 0.75rem;
            border-radius: 20px;
            cursor: pointer;
            border: 1px solid rgba(184,144,46,0.4);
            color: #A7B0BC;
            background: transparent;
            transition: all 0.15s;
        }
        .tl-filter-pill.active {
            border-color: #D4AF37;
            color: #D4AF37;
            background: rgba(212,175,55,0.08);
        }
"""

_FONTS_URL = "https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&family=Oswald:wght@400;500;600;700&display=swap"


def inject_css():
    css = _CSS.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    st.html(
        f"""<script>
(function() {{
    if (document.getElementById('tl-css')) return;
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = '{_FONTS_URL}';
    document.head.appendChild(l);
    var s = document.createElement('style');
    s.id = 'tl-css';
    s.textContent = `{css}`;
    document.head.appendChild(s);
}})();
</script>""",
        unsafe_allow_javascript=True,
    )


def render_nav(active: str = "home"):
    pages = [
        ("home",              "/",                   "Home"),
        ("champions",         "/champions",           "Champions"),
        ("league_timeline",   "/league_timeline",     "Timeline"),
        ("league_history",    "/league_history",      "League History"),
        ("season_archive",    "/season_archive",      "Season Archive"),
        ("manager_profiles",  "/manager_profiles",    "Managers"),
        ("franchise_profiles","/franchise_profiles",  "Franchises"),
    ]
    links = "".join(
        f'<a href="{href}" class="tl-nav-link{" active" if active == key else ""}" target="_self">{label}</a>'
        for key, href, label in pages
    )
    st.markdown(
        f"""
        <div class="tl-nav">
            <a href="/" class="tl-nav-brand">THE LONG GAME</a>
            <div class="tl-nav-links">{links}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def avatar_html(name: str, size: int = 64) -> str:
    emoji = MANAGER_EMOJI.get(name, "👤")
    return (
        f'<div class="tl-avatar" style="width:{size}px;height:{size}px;font-size:{size//2}px;">'
        f"{emoji}</div>"
    )


def metric_card(value: str, label: str) -> str:
    return (
        f'<div class="tl-metric">'
        f'<div class="tl-metric-value">{value}</div>'
        f'<div class="tl-metric-label">{label}</div>'
        f"</div>"
    )


def section_header(label: str, title: str) -> str:
    return (
        f'<div class="tl-section-label">{label}</div>'
        f'<div class="tl-section-title">{title}</div>'
    )


def html_table(headers: list, rows: list) -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    tbody = ""
    for row in rows:
        cells = "".join(
            f'<td class="{v[1]}">{v[0]}</td>' if isinstance(v, tuple) else f"<td>{v}</td>"
            for v in row
        )
        tbody += f"<tr>{cells}</tr>"
    return f"<table class='tl-table'><thead><tr>{th}</tr></thead><tbody>{tbody}</tbody></table>"
