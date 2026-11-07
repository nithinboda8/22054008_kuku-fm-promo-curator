import streamlit as st
import pandas as pd
import re
import json
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="Kuku FM - Microdrama Promo Curator",
    page_icon="🎬",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E293B; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #64748B; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# Title Header
st.markdown('<div class="main-title">🎬 Kuku FM Promo Curation & Scoring Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Automated Scene Parsing, Tension Curve Analysis & Short-Form Clip Extraction</div>', unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.header("⚙️ Model Configuration")
hook_weight = st.sidebar.slider("Hook Weight (First 3s)", 0.0, 1.0, 0.4, 0.05)
cliffhanger_weight = st.sidebar.slider("Cliffhanger Weight", 0.0, 1.0, 0.4, 0.05)
pacing_weight = st.sidebar.slider("Pacing / Conflict Weight", 0.0, 1.0, 0.2, 0.05)

st.sidebar.markdown("---")
st.sidebar.header("📁 Script Selection")
sample_choice = st.sidebar.selectbox("Choose Episode Sample", [
    "Episode 1: The Duke's Secret", 
    "Episode 2: Public Betrayal", 
    "Custom Text Ingestion"
])

# Script Parser Function
def parse_script(text):
    scenes = re.split(r'(INT\.|EXT\.)', text)
    parsed_scenes = []
    
    if len(scenes) > 1:
        for i in range(1, len(scenes), 2):
            header = scenes[i] + scenes[i+1].split('\n')[0]
            body = scenes[i+1]
            parsed_scenes.append({"header": header.strip(), "body": body.strip()})
    else:
        blocks = text.split('\n\n')
        for idx, b in enumerate(blocks):
            if b.strip():
                parsed_scenes.append({"header": f"SCENE {idx+1}", "body": b.strip()})
                
    return parsed_scenes

# High Tension Keyword Scoring Engine
def score_scene(scene_text, index, total_scenes):
    keywords_hook = ['secret', 'duke', 'slap', 'betrayal', 'money', 'liar', 'cheater', 'divorce', 'bastard', 'kill', 'gun', 'blood']
    keywords_cliff = ['stop', 'wait', 'no', 'who are you', 'never', 'freeze', 'behind you', 'dead', 'flatline', 'shock']
    
    words = scene_text.lower().split()
    word_count = len(words)
    
    hook_score = min(10.0, 5.0 + sum(2.0 for w in keywords_hook if w in words))
    cliffhanger_score = min(10.0, 4.0 + sum(2.5 for w in keywords_cliff if w in words))
    
    if index >= total_scenes - 2:
        cliffhanger_score = min(10.0, cliffhanger_score + 2.0)
        
    pacing_score = min(10.0, max(4.0, word_count / 15.0))
    
    composite = round(
        (hook_score * hook_weight) + 
        (cliffhanger_score * cliffhanger_weight) + 
        (pacing_score * pacing_weight), 2
    )
    
    return hook_score, cliffhanger_score, pacing_score, composite

# Main Body Logic
if sample_choice == "Custom Text Ingestion":
    raw_script = st.text_area("Paste Screenplay Text Here:", height=250, value="INT. CATHEDRAL - DAY\nANNA stands frozen as the DUKE enters with bloody gloves.\n\nANNA\nYou lied to me! You were never a soldier!\n\nDUKE\nI had to protect the empire, Anna. Sign the divorce papers or he dies.")
elif sample_choice == "Episode 2: Public Betrayal":
    raw_script = """
    INT. RESTAURANT VIP LOUNGE - NIGHT
    MARK and SOPHIA celebrate their 5th anniversary. The waiter pours champagne.
    
    SOPHIA
    I checked your corporate accounts today, Mark. Why is everything transferred to an offshore trust?
    
    Mark sets down his glass, a cold smirk crossing his face.
    
    MARK
    Because you were never my wife under law, Sophia. You're just a tenant.
    
    EXT. PARKING LOT - CONTINUOUS
    Sophia storms out into the rain, slamming the heavy glass door. A lawyer's car pulls up blocking her escape.
    """
else:
    raw_script = """
    INT. LUXURY BANQUET HALL - NIGHT
    ANNA (20s) stands in front of the wealthy ELITE FAMILY. Modern music blares.
    
    MADAM ELYSE
    You are a disgrace to our lineage! Sign this marriage annulment now!
    
    Anna clutches her chest, tears welling. The DUKE steps into the room. Silence falls.
    
    DUKE
    Touch her again, and your entire corporation crumbles by dawn.
    
    EXT. RAINY STREET - CONTINUOUS
    Anna runs out into the pouring rain. A black sedan screeches to a halt, blocking her path.
    The window rolls down slowly revealing a matching signet ring.
    
    ANNA
    It can't be... Father?
    """

if st.button("⚡ Process & Extract Promos", type="primary"):
    scenes = parse_script(raw_script)
    total_scenes = len(scenes)
    
    results = []
    for idx, sc in enumerate(scenes):
        h_score, c_score, p_score, comp = score_scene(sc['body'], idx, total_scenes)
        
        start_sec = idx * 30
        end_sec = start_sec + 30
        tc_start = f"00:{start_sec//60:02d}:{start_sec%60:02d}"
        tc_end = f"00:{end_sec//60:02d}:{end_sec%60:02d}"
        
        results.append({
            "Scene #": idx + 1,
            "Header": sc['header'],
            "Start Time": tc_start,
            "End Time": tc_end,
            "Hook Score": h_score,
            "Cliffhanger Score": c_score,
            "Pacing Score": p_score,
            "Composite Score": comp,
            "Selected for Promo": "YES" if comp >= 7.5 else "NO",
            "Excerpt": sc['body'][:120] + "..."
        })
        
    df = pd.DataFrame(results)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Scenes Parsed", len(df))
    col2.metric("Promos Identified", len(df[df['Selected for Promo'] == 'YES']))
    col3.metric("Peak Tension Score", f"{df['Composite Score'].max()} / 10")
    col4.metric("Avg Hook Intensity", f"{round(df['Hook Score'].mean(), 1)} / 10")
    
    st.markdown("---")
    
    top_promo = df.sort_values(by="Composite Score", ascending=False).iloc[0]
    st.success(f"🏆 **Top Recommended Promo Cut:** Scene {top_promo['Scene #']} ({top_promo['Start Time']} - {top_promo['End Time']}) | Score: **{top_promo['Composite Score']}/10**")
    st.caption(f"**Key Excerpt:** {top_promo['Excerpt']}")
    
    st.subheader("📋 Episode Scene Breakdown & Promo Scores")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("📈 Tension Curve & Hook Profile")
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(df['Scene #'], df['Composite Score'], marker='o', color='#2C3E50', linewidth=2, label='Composite Score')
    ax.axhline(y=7.5, color='r', linestyle='--', label='Promo Threshold (7.5)')
    ax.set_xlabel("Scene Number")
    ax.set_ylabel("Score (1-10)")
    ax.set_title("Episode Tension Curve for Promo Cut Selection")
    ax.legend()
    st.pyplot(fig)
    
    st.subheader("📥 Export Curation Artifacts")
    c1, c2 = st.columns(2)
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    c1.download_button("Download Clip Sheet (CSV)", csv_data, "kuku_fm_promos.csv", "text/csv")
    
    json_data = json.dumps(results, indent=2).encode('utf-8')
    c2.download_button("Download API Metadata (JSON)", json_data, "kuku_fm_promos.json", "application/json")
