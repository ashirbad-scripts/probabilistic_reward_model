import streamlit as st
import mysql.connector
import random
from datetime import datetime

# Local Connection to db
db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'willow',
    database = 'gacha_rng_db'
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

cursor.execute("SELECT * FROM spins WHERE character_type = 'Cartethiya'")
got_featured = cursor.fetchone() is not None

cursor.execute("SELECT * FROM spins WHERE pity = 80 AND character_type = 'Limited'")
got_limited = cursor.fetchone() is not None

cursor.execute("SELECT * FROM spins WHERE pity > 80 AND character_type = 'Cartethiya'")
forced_featured_given = cursor.fetchone() is not None

# Main Gacha Spin Logic
if got_featured:
    st.success("Featured Character already pulled !!!")
elif pity > 160:
    st.warning("Please Restart Banner")
else:
    if st.button("Spin The RNG"):
        result = random.randint(1,100)
        character_type = None
        reward_item = None

        # Pity 80, Force the limited character
        if pity == 80 and not got_featured:
            result = 80
            character_type = 'Limited'
            st.info("You have recieved a limited Character")
        
        # Forced pity at 160 if missed before
        elif pity > 80 and not got_featured and not forced_featured_given and pity == 160:
            result = 78
            character_type = 'Cartethiya'
            forced_featured_given = True
        
        # Natural Featured Pull
        elif result == 78 and not got_featured:
            character_type = 'Cartethiya'

        # Reward tier check
        if not (result == 78 or pity == 80):
            cursor.execute("SELECT rewards FROM rewards_tiers WHERE %s BETWEEN range_start AND range_end", (result,))
            row = cursor.fetchone()
            if row:
                reward_item = row[0]
        
        # Insert time stamps
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
            message = f" + 🎁 {reward_item}"
        st.success(message)

        if character_type == 'Cartethiya':
            st.info("🎊 Banner Complete ! Please Restart")
        
    
# Display recent history
st.subheader("Last 10 Spins")
cursor.execute("SELECT pity, result, character_type, reward_item, timestamp FROM spins ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

for eachSpin in rows:
    pity_value, result, char, reward, time = eachSpin
    label = f"Pity #{pity_value} → {result}"
    if char:
        label += f" ({char})"
    if reward:
        label += f" | Reward: {reward}"
    st.text(f"{label} @ {time}")

# Stats display
st.subheader("Banner Stats")
st.write(f"Total Pity: `{total_spins}` / 160")
st.write(f"Featured Pulled: `{got_featured}`")
st.write(f"Limited Pull: `{got_limited}`")

# Reset button
if st.button("Reset Banner"):
    cursor.execute("DELETE FROM spins")
    db.commit()
    st.success("Banner Reset Successful")

# Clean up
cursor.close()
db.close()