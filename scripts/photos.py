"""Player headshots and NFL team logos for The Recap's player cards.

One copy per museum (Dynasty 22 and {insert witty name here}); the pattern
and sources come from the Espinosa Clubhouse's scripts/fetch_player_images.py
(see Projects/ASSETS.md → Player headshots):

  headshot   https://sleepercdn.com/content/nfl/players/<sleeper_id>.jpg
  team logo  https://sleepercdn.com/images/team_logos/nfl/<team>.png  (defenses)

Only the players a recap actually features are downloaded, once, into
public/players/ and public/nfl/ and committed with the site. A failed or
missing download is never fatal: the card falls back to the manager's badge.
"""

from __future__ import annotations

import ssl
import time
import urllib.request
from pathlib import Path

try:  # macOS framework Python ships without root certificates
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
HEADSHOT_URL = "https://sleepercdn.com/content/nfl/players/{sleeper_id}.jpg"
TEAM_LOGO_URL = "https://sleepercdn.com/images/team_logos/nfl/{team}.png"
MIN_IMAGE_BYTES = 2000
# Sleeper serves PNGs behind .jpg URLs, so trust magic bytes, not the URL.
IMAGE_FORMATS = ((b"\xff\xd8", "jpg"), (b"\x89PNG", "png"), (b"RIFF", "webp"))


def _existing(directory: Path, stem: str) -> Path | None:
    for _, ext in IMAGE_FORMATS:
        candidate = directory / f"{stem}.{ext}"
        if candidate.exists():
            return candidate
    return None


def _download(url: str, directory: Path, stem: str) -> Path | None:
    found = _existing(directory, stem)
    if found:
        return found
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "sme327 league museum recap"})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
            payload = resp.read()
    except OSError as err:
        print(f"  photo: failed {url}: {err}")
        return None
    ext = next((e for magic, e in IMAGE_FORMATS if payload.startswith(magic)), None)
    if len(payload) < MIN_IMAGE_BYTES or not ext:
        print(f"  photo: rejected {url} ({len(payload)} bytes)")
        return None
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{stem}.{ext}"
    path.write_bytes(payload)
    time.sleep(0.1)  # be polite to the free CDN
    return path


def headshot(sleeper_id: str | None) -> str | None:
    """Site path of a player's headshot, downloading it on first use."""
    if not sleeper_id or not str(sleeper_id).isdigit():
        return None
    path = _download(HEADSHOT_URL.format(sleeper_id=sleeper_id), PUBLIC / "players", str(sleeper_id))
    return f"/players/{path.name}" if path else None


def team_logo(team: str | None) -> str | None:
    """Site path of an NFL team logo (the picture for a defense)."""
    if not team:
        return None
    path = _download(TEAM_LOGO_URL.format(team=team.lower()), PUBLIC / "nfl", team.upper())
    return f"/nfl/{path.name}" if path else None


# ── Yahoo player id -> Sleeper id ────────────────────────────────────────────
# Sleeper's public player dump carries each player's yahoo_id; the same
# direct-then-name/team fallback as the Espinosa Clubhouse's matcher.

import json
import re

SLEEPER_PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"
SLEEPER_CACHE = ROOT / ".local" / "sleeper-players-nfl.json"
NAME_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
_matcher = None


def _normalized(name: str) -> str:
    tokens = re.sub(r"[^a-z\s]", "", name.lower()).split()
    return "".join(t for t in tokens if t not in NAME_SUFFIXES)


def sleeper_id_for(yahoo_id: str, name: str, team: str) -> str | None:
    global _matcher
    if _matcher is None:
        if not SLEEPER_CACHE.exists() or time.time() - SLEEPER_CACHE.stat().st_mtime > 7 * 86400:
            SLEEPER_CACHE.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(SLEEPER_PLAYERS_URL, headers={"User-Agent": "sme327 league museum recap"})
            with urllib.request.urlopen(req, timeout=120, context=SSL_CONTEXT) as resp:
                SLEEPER_CACHE.write_bytes(resp.read())
        dump = json.loads(SLEEPER_CACHE.read_text(encoding="utf-8"))
        by_yahoo, by_name_team = {}, {}
        for sid, row in dump.items():
            if row.get("yahoo_id") is not None:
                by_yahoo.setdefault(str(row["yahoo_id"]), sid)
            if row.get("full_name") and row.get("team"):
                by_name_team.setdefault((_normalized(row["full_name"]), row["team"]), []).append(sid)
        _matcher = (by_yahoo, by_name_team)
    by_yahoo, by_name_team = _matcher
    if str(yahoo_id) in by_yahoo:
        return by_yahoo[str(yahoo_id)]
    candidates = by_name_team.get((_normalized(name), team), [])
    return candidates[0] if len(candidates) == 1 else None
