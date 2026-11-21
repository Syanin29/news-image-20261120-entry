"""Story data for Friday 20 November 2026 — early edition (built ~00:40 UTC).

Kept separate from render.py so the facts can be refreshed before the final
submit without touching the renderer. Every story was verified against the
sources in NEWS-SOURCES.md on 20 November 2026. The Akvan landfall ("noon
today") is an IMD forecast and is worded as a forecast on the image.

Layout of each record:
  hero / features: (headline, explainer, stat, marker_or_None, photo_or_None)
  list:            (headline, stat, marker_or_None)
  ticker:          (headline, explainer)
  markers:         number -> (lon, lat, label_dx_px, label_dy_px)
"""

DATE_LINE = "FRIDAY, 20 NOVEMBER 2026"
STORY_COUNT = 41
CONTINENT_LINE = "6 CONTINENTS"

HERO = (
    "CYCLONE AKVAN HITS INDIA TODAY",
    "Severe storm crosses near Gopalpur at noon, winds 90-100 km/h "
    "gusting 110; 1,224 shelters open, zero-casualty target",
    "105,304 EVACUATED",
    1,
    "cyclone.jpg",
)

FEATURES = [
    (
        "GTA VI TOPS THE ODYSSEY",
        "Est. $1.84bn in a day beats Nolan's $1.805bn film run",
        "$1.84BN",
        2,
        None,
    ),
    (
        "ANTHROPIC CLOSES +17%",
        "ANT ends day one at $97.17 vs $83 IPO; $81.3bn raised",
        "$97.17",
        3,
        None,
    ),
    (
        "TRUMP: NO RUSH ON IRAN",
        "War decision pushed to 2027: 'see what happens' after Jan 1",
        "TO 2027",
        4,
        None,
    ),
    (
        "EUROPE READY FOR TALKS",
        "Ukraine's allies say they will talk to Russia to end the war",
        "TALKS READY",
        5,
        None,
    ),
]

LIST_STORIES = [
    ("NZ 317-6 AT LUNCH VS INDIA", "PHILLIPS 118", 6),
    ("CHINA LPR EXPECTED HELD", "3.00% / 3.50%", 7),
    ("UK SENTIMENT EDGES UP", "GFK -22", 8),
    ("UK ORDERS REBOUND", "CBI -12", 8),
    ("SENSEX +1.21%, NIFTY +1.14%", "THU RALLY", 9),
    ("FIONA THE HIPPO DIES", "SWALLOWED HAT", 10),
    ("CHASE LEAK: EMAILS EXPOSED", "THOUSANDS HIT", 3),
    ("IRAN WAR COSTS $48.3BN", "AS OF NOV 13", 4),
    ("HAITI FORCES FIGHT GANGS", "KEY CORRIDOR", 11),
    ("TRAIN HEIST: $22M CARGO", "DOZEN CHARGED", 12),
    ("MYANMAR GENOCIDE VERDICT", "ICJ FIRST", 13),
    ("TRUMP, XI & PUTIN: PEACE DECLARATION", "FIRST TRILATERAL", 14),
    ("PUTIN VOWS PAINFUL RESPONSE", "CRIMEA BRIDGE", 15),
    ("ISRAEL GAZA OP COMPLETE", "BEYOND YELLOW LINE", 16),
    ("VENEZUELA SIGNS US MILITARY DEAL", "POST-MADURO", 17),
    ("SENEGAL BOAT SINKS", "100 ABOARD", 18),
    ("UGANDA SURVIVORS AT THE UN", "LANDSLIDE CASE", 19),
    ("SEOUL OVERTURNS HAN VERDICT", "EX-PM CLEARED", 20),
    ("FIJI DECLARES DISASTER", "EL NINO DROUGHT", 21),
    ("NORTH KOREA EXPANDS ENRICHMENT", "YONGBYON", 22),
    ("HAYABUSA2 DROPS ASTEROID KY26", "NEW TARGET 2028", 23),
    ("VOYAGER 1 LIGHT-DAY CONFIRMED", "NASA CONFIRMS", None),
    ("MODI MEETS WILLIAM & KATE", "NEW DELHI", 24),
    ("INDIA-ISRAEL DEFENCE DEAL", "RS 1,976 CR", 24),
    ("THOMAS MARKLE RULED COMPETENT", "FLORIDA COURT", 4),
    ("BOKS & ALL BLACKS RACE TO FINAL", "FINAL NOV 29", 8),
    ("AI SELLOFF: STOCKS -3.7%", "CORRECTION", 3),
    ("RUSSIA HITS KYIV, MISSILES IN POLAND", "400+ DRONES", 25),
    ("CANCER PILL CLEARS TUMORS", "1 IN 12", 8),
    ("GEN Z PROTESTS: 25 COUNTRIES", "EUROPE-WIDE", 26),
    ("COP31 RUNS PAST DEADLINE", "FOSSIL FUELS", 27),
    ("IRAN DOWNS US MQ-9 DRONE", "58TH CLAIMED", 28),
]

TICKER = [
    ("WORLD CHILDREN'S DAY", "Marked worldwide today"),
    ("ROME'S ANCIENT LIBRARY REOPENS", "Restored after centuries buried"),
    ("CENTRAL PARK CARRIAGES SUE NYC", "Drivers fight incoming ban"),
    ("RUGBY: ALL 12 SIDES PLAY SATURDAY", "Nations Championship deciders"),
]

# marker number -> (lon, lat, display_dx_px, display_dy_px)
MARKERS = {
    1: (85.0, 19.3, 0, 16),      # Gopalpur, Odisha — Akvan landfall
    2: (-80.2, 25.8, -6, 14),    # Miami / Vice City — GTA VI
    3: (-74.0, 40.7, 0, -16),    # New York — Anthropic / Chase
    4: (-77.0, 38.9, -14, 14),   # Washington — Trump / Iran
    5: (4.4, 50.8, -18, -8),     # Brussels — Europe talks
    6: (174.8, -41.3, -14, -10),  # Wellington — NZ v India Test
    7: (116.4, 39.9, 0, -16),    # Beijing — China LPR
    8: (-0.1, 51.5, -20, 6),     # London — UK data / rugby final
    9: (72.9, 19.1, -14, 14),    # Mumbai — Sensex
    10: (-84.5, 39.1, -8, -16),  # Cincinnati — Fiona
    11: (-72.3, 18.5, 0, 16),    # Port-au-Prince — Haiti
    12: (-118.2, 34.0, 0, -14),  # Los Angeles — train heist
    13: (4.3, 52.1, 16, -16),    # The Hague — ICJ verdict
    14: (114.1, 22.5, 8, 14),    # Shenzhen — trilateral
    15: (34.5, 45.3, 0, -16),    # Crimea — bridge strikes
    16: (34.5, 31.5, -6, 16),    # Gaza
    17: (-66.9, 10.5, 0, -14),   # Caracas — Venezuela deal
    18: (-17.4, 14.7, -8, 14),   # Dakar — Senegal boat
    19: (32.6, 0.3, 6, 14),      # Uganda — landslide case
    20: (127.0, 37.6, 10, -14),  # Seoul — Han verdict
    21: (178.4, -17.7, -20, 12),  # Fiji — disaster declared
    22: (125.8, 39.8, -12, 12),  # Yongbyon — enrichment
    23: (139.7, 35.7, 8, 12),    # Tokyo — Hayabusa2
    24: (77.2, 28.6, -8, -14),   # New Delhi — Modi / defence deal
    25: (30.5, 50.4, -16, -12),  # Kyiv — Russia strikes / Poland missiles
    26: (13.4, 52.5, 14, -10),   # Berlin — Gen Z protests
    27: (30.7, 36.9, 8, 14),     # Antalya — COP31 overtime
    28: (56.5, 26.5, 10, 12),    # Strait of Hormuz — MQ-9 downed
}
