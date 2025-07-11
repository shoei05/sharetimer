import streamlit as st
import datetime
import time
import pytz
import sqlite3

# ページ設定
st.set_page_config(
    page_title="共有タイマー",
    page_icon="⏰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# データベース設定
DB_PATH = "shared_timer.db"

def init_db():
    """データベースの初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timer_settings (
            id INTEGER PRIMARY KEY,
            target_time TEXT NOT NULL,
            suffix TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 初期値があるかチェック
    cursor.execute("SELECT COUNT(*) FROM timer_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO timer_settings (target_time, suffix) 
            VALUES ('23:59', 'から開始')
        """)
    
    conn.commit()
    conn.close()

def get_shared_settings():
    """共有設定を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT target_time, suffix FROM timer_settings ORDER BY updated_at DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        time_str, suffix = result
        time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
        return time_obj, suffix
    return datetime.time(23, 59), "から開始"

def update_shared_settings(target_time, suffix):
    """共有設定を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    time_str = target_time.strftime('%H:%M')
    cursor.execute("""
        INSERT INTO timer_settings (target_time, suffix) 
        VALUES (?, ?)
    """, (time_str, suffix))
    conn.commit()
    conn.close()

def get_last_update_time():
    """最後の更新時刻を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT updated_at FROM timer_settings ORDER BY updated_at DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# データベース初期化
init_db()

# 共有設定を取得
shared_time, shared_suffix = get_shared_settings()

# セッション状態の初期化
if 'target_time' not in st.session_state:
    st.session_state.target_time = shared_time
if 'suffix' not in st.session_state:
    st.session_state.suffix = shared_suffix
if 'last_update' not in st.session_state:
    st.session_state.last_update = get_last_update_time()
if 'time_reached' not in st.session_state:
    st.session_state.time_reached = False
if 'editing_time' not in st.session_state:
    st.session_state.editing_time = False
if 'editing_suffix' not in st.session_state:
    st.session_state.editing_suffix = False

# 他のユーザーの変更をチェック
current_update_time = get_last_update_time()
if current_update_time != st.session_state.last_update:
    st.session_state.target_time, st.session_state.suffix = get_shared_settings()
    st.session_state.last_update = current_update_time
    st.session_state.time_reached = False

# 日本時間の設定
jst = pytz.timezone('Asia/Tokyo')
now = datetime.datetime.now(jst)

# 目標時刻の設定
target_dt = datetime.datetime.combine(datetime.date.today(), st.session_state.target_time)
target_dt = jst.localize(target_dt)

# 明日の場合の処理
if target_dt <= now:
    target_dt = target_dt + datetime.timedelta(days=1)

# 時刻到達の判定
time_reached = now >= target_dt

# 背景色の変更
if time_reached and not st.session_state.time_reached:
    st.session_state.time_reached = True
elif not time_reached:
    st.session_state.time_reached = False

# カスタムCSS
background_color = "#c5487b" if st.session_state.time_reached else "#f5f5f5"
text_color = "white" if st.session_state.time_reached else "#333"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {background_color};
        transition: all 0.5s ease;
    }}
    
    .main-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        text-align: center;
        padding: 2rem;
    }}
    
    .target-time-display {{
        font-size: 3.5rem;
        font-weight: bold;
        color: {text_color};
        margin-bottom: 2rem;
        font-family: 'Arial', sans-serif;
        cursor: pointer;
        transition: opacity 0.2s ease;
    }}
    
    .target-time-display:hover {{
        opacity: 0.8;
    }}
    
    .current-time-display {{
        font-size: 8rem;
        font-weight: bold;
        color: {text_color};
        margin: 2rem 0;
        font-family: 'Courier New', monospace;
        line-height: 1;
    }}
    
    .date-display {{
        font-size: 2rem;
        color: {text_color};
        margin-bottom: 3rem;
        font-family: 'Arial', sans-serif;
    }}
    
    .clickable {{
        cursor: pointer;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: background-color 0.2s ease;
        display: inline-block;
        margin: 0 0.5rem;
    }}
    
    .clickable:hover {{
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    .edit-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }}
    
    .stSelectbox > div > div {{
        background-color: transparent;
        border: 2px solid {text_color};
        color: {text_color};
    }}
    
    .stTimeInput > div > div {{
        background-color: transparent;
        border: 2px solid {text_color};
        color: {text_color};
    }}
    
    .stButton > button {{
        background-color: transparent;
        border: 2px solid {text_color};
        color: {text_color};
        font-size: 1.2rem;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {text_color};
        color: {background_color};
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    .stApp > div:first-child {{
        margin-top: -80px;
    }}
</style>
""", unsafe_allow_html=True)

# メインコンテナ
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 目標時刻表示（クリック可能）
if st.session_state.editing_time or st.session_state.editing_suffix:
    # 編集モード
    st.markdown('<div class="edit-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.session_state.editing_time:
            new_time = st.time_input(
                "時刻",
                value=st.session_state.target_time,
                key="time_edit",
                label_visibility="collapsed"
            )
        else:
            new_time = st.session_state.target_time
    
    with col2:
        if st.session_state.editing_suffix:
            new_suffix = st.selectbox(
                "モード",
                ["から開始", "まで"],
                index=0 if st.session_state.suffix == "から開始" else 1,
                key="suffix_edit",
                label_visibility="collapsed"
            )
        else:
            new_suffix = st.session_state.suffix
    
    with col3:
        if st.button("確定"):
            # データベースに保存
            update_shared_settings(new_time, new_suffix)
            
            # セッション状態を更新
            st.session_state.target_time = new_time
            st.session_state.suffix = new_suffix
            st.session_state.last_update = get_last_update_time()
            st.session_state.time_reached = False
            st.session_state.editing_time = False
            st.session_state.editing_suffix = False
            
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 表示モード（クリック可能）
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button(
            f"{st.session_state.target_time.strftime('%H時%M分')}",
            key="time_display",
            help="クリックして時刻を変更"
        ):
            st.session_state.editing_time = True
            st.rerun()
    
    with col2:
        if st.button(
            st.session_state.suffix,
            key="suffix_display", 
            help="クリックしてモードを変更"
        ):
            st.session_state.editing_suffix = True
            st.rerun()

# 現在時刻表示
st.markdown(f'''
<div class="current-time-display">
    {now.strftime('%H:%M:%S')}
</div>
''', unsafe_allow_html=True)

# 日付表示
weekdays = ['月', '火', '水', '木', '金', '土', '日']
weekday = weekdays[now.weekday()]

st.markdown(f'''
<div class="date-display">
    {now.strftime('%Y年%m月%d日')}（{weekday}）
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 自動リフレッシュ
time.sleep(1)
st.rerun()
