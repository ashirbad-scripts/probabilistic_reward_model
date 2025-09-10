import streamlit as st
import mysql.connector
import random
from datetime import datetime

# Character names (can be changed easily)
FEATURED_CHARACTER_NAME = "Cartethiya Baby"
LIMITED_CHARACTER_NAME = "Lion Boy"

# Local Connection to db
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='willow',
    database='gacha_rng_db'
)

cursor = db.cursor()

# Create Spins Table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS spins(
        id INT AUTO_INCREMENT PRIMARY KEY,
        pity INT,
        result INT,
        character_type VARCHAR(50),
        reward_item VARCHAR(255),
        timestamp DATETIME)
""")
db.commit()

# Title & Info
st.title("Gacha RNG Simulation")
st.caption("Pity-Based Gacha System")

# Fetch Current Spin info
cursor.execute("SELECT COUNT(*) FROM spins")
total_spins = cursor.fetchone()[0]
pity = total_spins + 1

cursor.execute("SELECT * FROM spins WHERE character_type = %s", (FEATURED_CHARACTER_NAME,))
got_featured = cursor.fetchone() is not None

cursor.execute("SELECT * FROM spins WHERE pity = 80 AND character_type = %s", (LIMITED_CHARACTER_NAME,))
got_limited = cursor.fetchone() is not None

cursor.execute("SELECT * FROM spins WHERE pity > 80 AND character_type = %s", (FEATURED_CHARACTER_NAME,))
forced_featured_given = cursor.fetchone() is not None

# Main Gacha Spin Logic
if got_featured:
    st.success(f"{FEATURED_CHARACTER_NAME} already pulled!")
elif pity > 160:
    st.warning("Please Restart Banner")
else:
    if st.button("Spin The RNG"):
        result = random.randint(1, 100)
        character_type = None
        reward_item = None

        # Pity 80: Force the limited character
        if pity == 80 and not got_featured:
            result = 80
            character_type = LIMITED_CHARACTER_NAME
            st.info(f"You have received a limited character → {LIMITED_CHARACTER_NAME}")

        # Forced Featured at pity 160
        elif pity > 80 and not got_featured and not forced_featured_given and pity == 160:
            result = 78
            character_type = FEATURED_CHARACTER_NAME

        # Natural Featured Pull
        elif result == 78 and not got_featured:
            character_type = FEATURED_CHARACTER_NAME

        # Reward tier check (skip if result is 78 or pity is 80)
        if not (result == 78 or pity == 80):
            cursor.execute("SELECT rewards FROM rewards_tiers WHERE %s BETWEEN range_start AND range_end", (result,))
            row = cursor.fetchone()
            if row:
                reward_item = row[0]

        # Insert into DB
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO spins(pity, result, character_type, reward_item, timestamp) 
            VALUES (%s, %s, %s, %s, %s)
        """, (pity, result, character_type, reward_item, timestamp))
        db.commit()

        # Show Result
        message = f"Pity #{pity} → You got `{result}`"
        if character_type:
            message += f" → ⭐ {character_type}"
        if reward_item:
            message += f" + 🎁 {reward_item}"
        st.success(message)

        if character_type == FEATURED_CHARACTER_NAME:
            st.info("🎊 Banner Complete! Please Restart")

# Display recent history
st.subheader("Last 10 Spins")
cursor.execute("SELECT pity, result, character_type, reward_item, timestamp FROM spins ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

for eachSpin in rows:
    pity_value, result, char, reward, time = eachSpin

    # Highlight Featured or Limited characters
    if char == FEATURED_CHARACTER_NAME:
        char_display = f"**:green[{char}]**"
    elif char == LIMITED_CHARACTER_NAME:
        char_display = f"**:violet[{char}]**"
    elif char:
        char_display = f"**{char}**"
    else:
        char_display = ""

    # Bold gray result and time
    result_display = f"**:gray[{result}]**"
    time_display = f"**:gray[{time}]**"

    # Bold only the reward name, not the 🎁 emoji or separator
    if reward:
        reward_display = f"🎁 <b>{reward}</b>"
    else:
        reward_display = ""

    # Build full label
    label = f"Pity #{pity_value} → {result_display}"
    if char:
        label += f" ({char_display})"
    if reward:
        label += f" | {reward_display}"

    st.markdown(f"{label} @ {time_display}", unsafe_allow_html=True)



# Stats display
st.subheader("Banner Stats")
st.write(f"Total Pity: `{pity}` / 160")
st.write(f"{FEATURED_CHARACTER_NAME} Pulled: `{got_featured}`")
st.write(f"{LIMITED_CHARACTER_NAME} Pull at Pity 80: `{got_limited}`")

# Reset button
if st.button("Reset Banner"):
    cursor.execute("DELETE FROM spins")
    db.commit()
    st.success("Banner Reset Successful")
    st.rerun()


# Clean up
cursor.close()
db.close()
