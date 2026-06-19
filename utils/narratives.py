"""Static narrative content — museum copy for the digital exhibit.

All hardcoded text lives here so pages stay clean and editorial voice stays consistent.
"""
from __future__ import annotations

# ── NFL CONTEXT PER SEASON ─────────────────────────────────────────────────────
# 2–3 bullet points of real NFL color to anchor each fantasy season in football history.
NFL_CONTEXT: dict[int, list[str]] = {
    2001: [
        "Tom Brady steps in for injured Drew Bledsoe — a dynasty is born.",
        "Kurt Warner and the Greatest Show on Turf lose Super Bowl XXXVI to a 14-point underdog.",
        "Marshall Faulk, Priest Holmes, and Edgerrin James redefine the RB position.",
    ],
    2002: [
        "Rich Gannon wins MVP but Tampa Bay's historic defense wins the Super Bowl.",
        "Michael Vick becomes the first QB to rush for 1,000 yards.",
        "The Houston Texans play their inaugural season.",
    ],
    2003: [
        "Peyton Manning breaks Dan Marino's single-season TD record with 49.",
        "Patriots beat Carolina on a last-second Vinatieri field goal — the dynasty rolls on.",
        "Priest Holmes rushes for 27 TDs, the most in NFL history at the time.",
    ],
    2004: [
        "Peyton Manning throws 49 TDs and the Colts go 12-4 — then lose to the Patriots again.",
        "Terrell Owens catches 77 balls in a Super Bowl before breaking his leg.",
        "Shaun Alexander and the Seahawks emerge as NFC contenders.",
    ],
    2005: [
        "Shaun Alexander rushes for 1,880 yards and 27 TDs, wins MVP.",
        "The Pittsburgh Steelers win Super Bowl XL behind rookie Ben Roethlisberger.",
        "Steve Smith explodes for 1,563 yards after a slow start to his career.",
    ],
    2006: [
        "Peyton Manning finally wins it all — Super Bowl XLI over the Chicago Bears.",
        "LaDainian Tomlinson shatters the TD record with 28 rushing scores.",
        "Rex Grossman and the Bears somehow reach the Super Bowl.",
    ],
    2007: [
        "Tom Brady throws 50 TD passes; Randy Moss catches 23 of them — both NFL records.",
        "The Giants stun the undefeated Patriots in one of the greatest upsets in sports history.",
        "Brett Favre lights it up at age 38, reviving talk of a return.",
    ],
    2008: [
        "The Detroit Lions go 0-16. The first winless season in the Super Bowl era.",
        "Matt Ryan wins Offensive Rookie of the Year; Michael Turner rushes for 1,699 yards.",
        "Kurt Warner returns to the Super Bowl with Arizona — losing to Pittsburgh on a last-minute TD.",
    ],
    2009: [
        "Drew Brees leads the New Orleans Saints to their first Super Bowl championship.",
        "Brett Favre's Viking comeback nearly works — the NFC Championship comes down to a late interception.",
        "Chris Johnson rushes for 2,006 yards, only the sixth player to crack 2,000.",
    ],
    2010: [
        "Aaron Rodgers wins Super Bowl XLV in his first full year as a starter.",
        "Michael Vick is reborn in Philadelphia — 21 TDs, 6 rushing TDs, a Pro Bowl season.",
        "Roddy White and Julio Jones give Matt Ryan two of the best WRs in the NFC.",
    ],
    2011: [
        "Eli Manning wins his second Super Bowl title, dismantling the Patriots' historic offense.",
        "Aaron Rodgers throws 45 TDs and wins MVP — the peak of his early dynasty.",
        "Rob Gronkowski emerges: 17 TD catches, the most ever by a tight end.",
    ],
    2012: [
        "Ray Lewis retires as a champion — Baltimore beats San Francisco in Super Bowl XLVII.",
        "Adrian Peterson rushes for 2,097 yards, just nine yards short of the all-time record.",
        "Colin Kaepernick and the read-option offense reshapes the NFC West.",
    ],
    2013: [
        "Peyton Manning sets the all-time single-season TD record with 55 — then loses the Super Bowl.",
        "The Seattle defense holds Manning's offense to 8 points in Super Bowl XLVIII.",
        "Richard Sherman's tip and Malcolm Smith's pick define the 'Legion of Boom' era.",
    ],
    2014: [
        "The Patriots dynasty is restored — Malcolm Butler's goal-line interception beats Seattle.",
        "DeMarco Murray rushes for 1,845 yards and wins the rushing title.",
        "They should have run it. The call that will haunt Pete Carroll forever.",
    ],
    2015: [
        "Cam Newton wins MVP with 45 total TDs; the Panthers go 15-1.",
        "The Broncos' defense carries Peyton Manning to one last Super Bowl title.",
        "Von Miller wins SB MVP with 2.5 sacks and two forced fumbles.",
    ],
    2016: [
        "Tom Brady returns from a four-game suspension to orchestrate the greatest Super Bowl comeback ever — 28-3.",
        "Matt Ryan wins MVP with 9,317 total yards — then watches the lead evaporate.",
        "Dak Prescott and Ezekiel Elliott storm out of the draft into Dallas' best season in years.",
    ],
    2017: [
        "Nick Foles leads the Eagles to their first Super Bowl title — the 'Philly Special' goes down in history.",
        "Carson Wentz's MVP season ends on a knee injury; Foles finishes the job.",
        "Todd Gurley wins Offensive Player of the Year in Sean McVay's debut season.",
    ],
    2018: [
        "Patrick Mahomes throws 50 touchdowns in his first full season as a starter. The next dynasty is here.",
        "The Super Bowl is a 13-3 defensive grind — the lowest-scoring Super Bowl ever.",
        "Todd Gurley leads the Rams to the NFC title; Sony Michel wins the Super Bowl for New England.",
    ],
    2019: [
        "Lamar Jackson wins unanimous MVP with 36 TD passes and a QB-record 1,206 rushing yards.",
        "Patrick Mahomes wins his first Super Bowl — the Chiefs end a 50-year drought.",
        "Christian McCaffrey becomes only the third player to top 1,000 rushing and 1,000 receiving yards.",
    ],
    2020: [
        "Tom Brady leaves New England after 20 years and wins a Super Bowl in his first season with Tampa Bay.",
        "Patrick Mahomes loses to Brady in the Super Bowl — the torch is officially passed back.",
        "Davante Adams catches 18 TD passes; Derrick Henry rushes for 2,027 yards.",
    ],
    2021: [
        "Cooper Kupp wins the receiving triple crown; the Rams win the Super Bowl on their home field.",
        "Joe Burrow and the Bengals rise from 4-11 to the Super Bowl in one season.",
        "Justin Jefferson surpasses Randy Moss's rookie receiving record in his second year.",
    ],
    2022: [
        "Patrick Mahomes wins his second Super Bowl despite a high-ankle sprain.",
        "The Eagles go 14-3 with Jalen Hurts and A.J. Brown — then fall in the Super Bowl.",
        "Travis Kelce becomes the greatest tight end in NFL history, statistically.",
    ],
    2023: [
        "Travis Kelce and Taylor Swift dominate every headline not about Patrick Mahomes.",
        "Mahomes wins his third Super Bowl; the dynasty conversation begins in earnest.",
        "Tyreek Hill shatters the single-season receiving yard record with 1,710.",
    ],
    2024: [
        "Saquon Barkley runs for 2,005 yards in his first season in Philadelphia — then wins a Super Bowl.",
        "The Eagles go 14-3, obliterate the Chiefs in the Super Bowl 40-22.",
        "Patrick Mahomes and the Chiefs fall in the Super Bowl for the first time together.",
    ],
    2025: [
        "The 2025 NFL season is underway.",
        "Another year of fantasy feuds, league-winning decisions, and crushing waiver wire misses.",
    ],
}

# ── LEAGUE ERAS ────────────────────────────────────────────────────────────────
LEAGUE_ERAS: list[dict] = [
    {
        "name": "THE FOUNDING ERA",
        "short": "Founding",
        "years": "2001–2004",
        "start": 2001,
        "end": 2004,
        "color": "#D4AF37",
        "icon": "🏛️",
        "headline": "The League Finds Its Identity",
        "body": (
            "The first four seasons were about establishing rules, rivalries, and rituals. "
            "No one knew what they were building — just that they wanted to keep playing. "
            "The NFL itself was in a golden age: Brady, Manning, and LaDainian Tomlinson were reshaping football. "
            "This league was figuring out who it was."
        ),
    },
    {
        "name": "THE WORKHORSE ERA",
        "short": "Workhorse",
        "years": "2005–2009",
        "start": 2005,
        "end": 2009,
        "color": "#22C55E",
        "icon": "🐎",
        "headline": "The Bell Cow Runs the League",
        "body": (
            "Shaun Alexander. LaDainian Tomlinson. Adrian Peterson. Chris Johnson. "
            "The five seasons from 2005 to 2009 were defined by dominant rushing attacks — "
            "and managers who built rosters around a single backfield star. "
            "In the NFL, the ground game ruled. In this league, bell cows made dynasties."
        ),
    },
    {
        "name": "THE KEEPER REVOLUTION",
        "short": "Keepers",
        "years": "2010–2015",
        "start": 2010,
        "end": 2015,
        "color": "#A78BFA",
        "icon": "🔑",
        "headline": "Strategy Enters the Draft Room",
        "body": (
            "When the keeper rules took hold, everything changed. "
            "Drafting became about the future as much as the present. "
            "Managers began hoarding young talent, protecting emerging stars, and building multi-year rosters. "
            "The league started rewarding patience and planning over luck and reactivity. "
            "Some managers adapted. Others were left behind."
        ),
    },
    {
        "name": "THE MODERN ERA",
        "short": "Modern",
        "years": "2016–Present",
        "start": 2016,
        "end": 9999,
        "color": "#3B82F6",
        "icon": "⚡",
        "headline": "Speed, Receivers, and the New Game",
        "body": (
            "Patrick Mahomes. Alvin Kamara. Davante Adams. Justin Jefferson. Josh Allen. "
            "The NFL became a pass-first, points-everywhere league — and this one followed. "
            "Zero-RB strategies, TE premiums, and receiver kingdoms replaced the old bell-cow playbook. "
            "The managers who adapted to the new game are the ones still competing for titles."
        ),
    },
]

# ── KEEPER LORE ────────────────────────────────────────────────────────────────
# Narrative blurbs for the most iconic keepers in league history.
KEEPER_LORE: dict[str, str] = {
    "LaDainian Tomlinson": (
        "The crown jewel of the keeper era's early years. LaDainian Tomlinson wasn't just kept — "
        "he was a franchise cornerstone, surviving steward changes and suspension years "
        "to remain the most coveted player on the board. When you had LT, you had a shot."
    ),
    "Alvin Kamara": (
        "The engine of Brian Clark's keeper dynasty. Kamara's combination of rushing and receiving "
        "made him the perfect fantasy weapon in the modern era — and the fact that Clark kept him "
        "year after year turned a great pick into a multi-championship foundation."
    ),
    "Chris Johnson": (
        "CJ2K entered this league on the back of the most dominant rushing season in modern NFL history. "
        "At his peak, he was unkeppable — the kind of player who wins championships by himself. "
        "Two titles in the years he was kept. That's not a coincidence."
    ),
    "George Kittle": (
        "The tight end premium, embodied. Kittle's combination of blocking, receiving, and sheer chaos "
        "made him impossible to ignore — and the managers who locked him in early reaped the rewards. "
        "A symbol of the modern keeper strategy: find a TE early, keep him forever."
    ),
    "Le'Veon Bell": (
        "Bell's combination of vision, patience, and receiving ability made him one of the most kept "
        "backs of his era. Before the Pittsburgh holdout changed everything, he was the definition "
        "of what a modern fantasy running back could be."
    ),
    "Antonio Brown": (
        "Before the controversies, there was the production. From 2013 to 2018, Antonio Brown was "
        "arguably the most valuable fantasy receiver in the game. Any manager who kept him during "
        "his peak years had a built-in advantage before Week 1 even started."
    ),
    "Davante Adams": (
        "The post-Brown receiver dynasty. Adams' chemistry with Aaron Rodgers — and later with "
        "Derek Carr and the Raiders — made him a perennial keeper target. One of the cleanest "
        "fantasy profiles of his generation: reliable, consistent, elite."
    ),
    "Christian McCaffrey": (
        "The most sought-after player in league history by draft position. Taken #1 overall four times. "
        "When healthy, McCaffrey was the consensus best fantasy player in football — "
        "a dual-threat weapon who made every roster he touched better."
    ),
}

# ── MANAGER IDENTITY LABELS ────────────────────────────────────────────────────
# Hardcoded one-line identity descriptors that supplement auto-generated plaques.
# These are the 'known tendencies' — the editorial shorthand for each manager.
MANAGER_IDENTITY: dict[str, str] = {
    "Dominic":         "Championship efficiency. Built rosters to peak at exactly the right moment.",
    "Brian Clark":     "The keeper architect. Patient, systematic, and ruthlessly consistent.",
    "Jamie":           "Never wastes a trip to the playoffs. One of the most efficient champions in league history.",
    "Fadi":            "A perennial force who could never quite close. The most decorated manager without a dynasty.",
    "Kevin Swanson":   "The iron man. Eighteen seasons of showing up, competing, and refusing to rebuild.",
    "Kevin O'Boyle":   "The quiet contender. Always in the mix, rarely out of playoff contention.",
    "Evan":            "High ceiling, high variance. When Evan peaks, he wins it all.",
    "Thomas":          "Methodical and multi-dimensional. Built for long-term success.",
    "Douglas":         "Lethal in limited appearances. A championship rate that rivals anyone's.",
    "Steve Swanson":   "A proven winner who made his seasons count.",
    "Bryan Kearney":   "The breakthrough. Broke through the playoff ceiling when it mattered most.",
    "Shawn":           "A founding member whose fingerprints are all over the early history of this league.",
    "Dale":            "Part of the foundation. One of the managers who built what this league became.",
}

# ── SEASON EMOTIONAL HOOKS ────────────────────────────────────────────────────
# Used on the season archive page — a one-line contextual frame for each season.
SEASON_HOOKS: dict[int, str] = {
    2001: "The first season. Nobody knew what they were starting.",
    2002: "Year two. The rituals were forming. The rivalries were real.",
    2003: "LaDainian Tomlinson. Need anything else?",
    2004: "The dynasty conversation was getting louder.",
    2005: "Everything changed when the keepers came.",
    2006: "The workhorse era. One back to rule them all.",
    2007: "The most stat-packed NFL season in history. The fantasy points were everywhere.",
    2008: "Chaos year. Nobody saw what was coming.",
    2009: "CJ2K ran for 2,006 yards. Someone in this league had him.",
    2010: "The modern era knocks on the door.",
    2011: "Lockout loomed, but the season delivered.",
    2012: "A new generation of managers started making noise.",
    2013: "Peyton Manning broke every record. This league broke a few of its own.",
    2014: "They should have run it. Someone in this league definitely should have started Bell.",
    2015: "The keeper arms race was fully underway.",
    2016: "The greatest comeback in Super Bowl history. Someone's playoff run probably felt similar.",
    2017: "Philadelphia believed. Someone in this league did too.",
    2018: "Mahomes arrived. The game changed. So did the strategies.",
    2019: "Lamar Jackson ran past everyone. A few managers tried to keep up.",
    2020: "Brady left New England. This league kept going anyway.",
    2021: "Cooper Kupp. The Rams came home. Fantasy chaos ensued.",
    2022: "The Kearney year. History was made.",
    2023: "Mahomes won again. This league crowned its own.",
    2024: "Saquon proved everyone wrong. Some managers did too.",
    2025: "The current season. The story isn't finished.",
}

# ── RIVALRY PLAQUES ────────────────────────────────────────────────────────────
# Keyed by sorted tuple of (manager_a, manager_b) in alphabetical order.
# These appear as museum-style plaques on the Rivalries page.
RIVALRY_PLAQUES: dict[tuple[str, str], str] = {
    ("Kevin O'Boyle", "Kevin Swanson"): (
        "Two Kevins. One league. Thirty-five regular season meetings, five playoff "
        "matchups, and one championship game. No rivalry in league history has been "
        "played more often or remained more evenly matched. They faced each other at "
        "least twice a season for over a decade — and neither could ever put the other away."
    ),
    ("Brian Clark", "Dominic"): (
        "Brian Clark owned Dominic in the regular season, winning 21 of 29 matchups — "
        "the most dominant long-running RS record in league history. But when January "
        "arrived, Dominic owned Clark. Three playoff eliminations. Two championship game "
        "victories. The rivalry that proves regular season supremacy means nothing when "
        "the stakes are highest."
    ),
    ("Dominic", "Kevin O'Boyle"): (
        "Twelve wins against eleven across the regular season — nearly identical. "
        "But in two championship game meetings, Dominic prevailed both times: 2011 and 2021. "
        "A rivalry of near-equals, separated only by the most important games ever played."
    ),
    ("Evan", "Fadi"): (
        "Fifteen wins each in the regular season. Exactly. Of all long-running rivalries "
        "in this league, none has produced more parity. They've met in two championship "
        "games — and split them. Evan won in 2012. Fadi answered in 2024, by 0.12 points. "
        "The closest final in league history. One trophy each. Completely unresolved."
    ),
    ("Brian Clark", "Kevin O'Boyle"): (
        "Thirty regular season meetings. Five playoff matchups. Fifteen wins each across "
        "both formats. They have contested some of the most important games in league "
        "history — yet they have never met in a championship game. "
        "The rivalry that climbed higher every season but never quite reached the summit."
    ),
    ("Dominic", "Fadi"): (
        "Fadi leads the regular season 16-9 — a convincing edge built over two decades. "
        "But Dominic leads the playoff record 3-1. The pattern holds: Fadi can beat "
        "Dominic during the season, but not when everything is on the line."
    ),
    ("Evan", "Kevin Swanson"): (
        "Thirteen wins each. Three playoff meetings. A rivalry built on parity and "
        "longevity that has played out across the full arc of the league's history, "
        "without either manager ever fully separating from the other."
    ),
    ("Kevin Swanson", "Shawn"): (
        "Kevin Swanson leads the series 17-11 and has eliminated Shawn from the playoffs "
        "twice. A rivalry defined less by headline moments and more by a quiet, sustained "
        "dominance that Shawn has never been able to fully answer."
    ),
    ("Shawn", "Thomas"): (
        "Thirty-four meetings — the second-most in league history. Shawn leads 19-15, "
        "and their matchups have spanned the entire life of the league. No two active "
        "managers have played each other more. The rivalry that defines continuity."
    ),
    ("Kevin O'Boyle", "Shawn"): (
        "Shawn leads the series 18-10, but seven of their meetings have been decided "
        "by fewer than five points. No long-running rivalry in league history has produced "
        "more close games. The rivalry that always comes down to the wire."
    ),
    ("Brian Clark", "Kevin Swanson"): (
        "Three playoff meetings and a regular season series that has gone back and forth "
        "for over fifteen years. They have met when seasons were on the line more than "
        "almost any other pair of managers."
    ),
    ("Fadi", "Thomas"): (
        "Thirty-one meetings — third-most in league history. Fadi leads 18-13 in a "
        "rivalry that has never produced a championship meeting but has defined the "
        "middle tier of contenders for most of the league's existence."
    ),
    ("Brian Clark", "Shawn"): (
        "Brian Clark leads 19-11 in a rivalry where eight games have been decided by "
        "fewer than five points. The most close games between any two managers with a "
        "lopsided overall record. Shawn keeps it close. He just can't quite win."
    ),
    ("Dominic", "Steve Swanson"): (
        "Two of the league's most consistent playoff contenders — with one "
        "championship meeting between them. Dominic won that one too."
    ),
    ("Evan", "Shawn"): (
        "Fifteen wins each in twenty-nine meetings. Two playoff appearances together. "
        "A rivalry built on mutual respect and identical records — one of the most "
        "balanced long-term matchups the league has ever produced."
    ),
}
