import mysql.connector

# Connection to db
db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'willow',
    db = 'gacha_rng_db'
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS rewards_tiers(
        id INT PRIMARY KEY AUTO_INCREMENT,
        range_start INT NOT NULL,
        range_end INT NOT NULL,
        rewards VARCHAR(300) NOT NULL) 
""")

reward_data = [
    (1, 5, "Shell Credit x300"),                       # Trash - basic currency
    (6, 10, "Tyro Sword"),                             # Trash - starter weapon
    (11, 15, "Polarized Metallic Drip"),               # Cosmetic or low-tier item
    (16, 20, "Minor Resonance Potion"),                # Minor upgrade resource
    (21, 25, "Advance Resonance Potion"),              # Mid upgrade item
    (26, 30, "Tuner x2"),                              # Gear tuning item (mid)
    (31, 35, "Advance Sealed Tube"),                   # Weapon upgrade material
    (36, 40, "Skill Module Beta"),                     # Skill upgrade item (mid)
    (41, 45, "Shell Credit x800"),                     # Mid-tier currency
    (46, 50, "Astrite x50"),                           # Gacha bait
    (51, 55, "Chixia Waveband"),                       # Character dupe (low-tier)
    (56, 60, "YangYang Waveband"),                     # Character dupe (low-tier)
    (61, 65, "Morfetti Waveband"),                     # Character dupe (low-tier)
    (66, 70, "FF Whisperin Core"),                     # Weapon upgrade
    (71, 75, "HF Whisperin Core"),                     # High-tier weapon material
    (76, 80, "Dreamless Feather"),                     # Skill ascension item
    (81, 85, "Tuner x5"),                              # Higher tuning mats
    (86, 90, "Astrite x100"),                          # Better gacha currency
    (91, 95, "Waveband: Taoqi"),                       # Desirable 4★ dupe
    (96, 100, "Waveband: Yuanwu"),                     # Desirable 4★ dupe
    (101, 105, "Shell Credit x1500"),                  # Bulk currency
    (106, 110, "Panzouha Recipe"),                     # Recipe/crafting
    (111, 115, "Astrite x200"),                        # Real gacha fuel
    (116, 120, "Weapon Skin: Obsidian Edge"),          # Rare cosmetic
    (121, 125, "Rectifier Variation (4★ weapon)"),     # Decent 4★ drop
    (126, 130, "Gauntlet Variation (4★ weapon)"),      # Decent 4★ drop
    (131, 135, "Pistols Variation (4★ weapon)"),       # Variety injection
    (136, 140, "Astrite x300"),                        # Jackpot gacha reward
    (141, 145, "Waveband: Encore (5★ dupe)"),          # High-value dupe
    (146, 150, "Crown of Harmony (Legendary Weapon)"), # Ultimate reward
]


# Insert to table
insert_query = """
    INSERT INTO rewards_tiers(range_start, range_end, rewards) VALUES (%s, %s, %s)
"""

for eachReward in reward_data:
    cursor.execute(insert_query, eachReward)

db.commit()
print("Rewards Loaded Successfully")

cursor.close()
db.close()
