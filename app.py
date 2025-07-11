import streamlit as st
import datetime
import time
import pytz
import json
import os

# ページ設定
st.set_page_config(
    page_title="共有タイマー",
    page_icon="⏰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 設定ファイルのパス
SETTINGS_FILE = "timer_settings.json"

def load_settings():
    """設定を読み込み"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                time_obj = datetime.datetime.strptime(data['time'], '%H:%M').time()
                return time_obj, data['suffix'], data.get('timestamp', '')
    except:
        pass
    return datetime.time(23, 59), "から開始", ""

def save_settings(target_time, suffix):
    """設定を保存"""
    try:
        data = {
            'time': target_time.strftime('%H:%M'),
            'suffix': suffix,
            'timestamp': datetime.datetime.now().isoformat()
        }
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except:
        return False

# 設定を読み込み
shared_time, shared_suffix, last_timestamp = load_settings()

# セッション状態の初期化
if 'target_time' not in st.session_state:
    st.session_state.target_time = shared_time
if 'suffix' not in st.session_state:
    st.session_state.suffix = shared_suffix
if 'last_timestamp' not in st.session_state:
    st.session_state.last_timestamp = last_timestamp
if 'time_reached' not in st.session_state:
    st.session_state.time_reached = False
if 'editing' not in st.session_state:
    st.session_state.editing = False

# 他のユーザーの変更をチェック
current_time, current_suffix, current_timestamp = load_settings()
if current_timestamp != st.session_state.last_timestamp and current_timestamp != "":
    st.session_state.target_time = current_time
    st.session_state.suffix = current_suffix
    st.session_state.last_timestamp = current_timestamp
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

# 背景色とテキスト色の設定
if st.session_state.time_reached:
    bg_color = "#c5487b"
    text_color = "white"
else:
    bg_color = "#f5f5f5"
    text_color = "#333333"

# カスタムCSS
st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color} !important;
    }}
    
    .main {{
        padding: 0 !important;
    }}
    
    .block-container {{
        padding: 2rem 1rem !important;
        max-width: 100% !important;
    }}
    
    .target-time {{
        font-size: 3rem;
        font-weight: bold;
        color: {text_color};
        text-align: center;
        margin: 2rem 0;
        cursor: pointer;
        padding: 1rem;
        border-radius: 10px;
        transition: opacity 0.2s;
    }}
    
    .target-time:hover {{
        opacity: 0.8;
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    .current-time {{
        font-size: 6rem;
        font-weight: bold;
        color: {text_color};
        text-align: center;
        margin: 2rem 0;
        font-family: 'Courier New', monospace;
        line-height: 1.1;
    }}
    
    .date-display {{
        font-size: 1.8rem;
        color: {text_color};
        text-align: center;
        margin: 1rem 0;
    }}
    
    .stButton > button {{
        background-color: transparent !important;
        border: 2px solid {text_color} !important;
        color: {text_color} !important;
        font-size: 1.1rem !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 8px !important;
        width: 100% !important;
    }}
    
    .stButton > button:hover {{
        background-color: {text_color} !important;
        color: {bg_color} !important;
    }}
    
    .stSelectbox > div > div {{
        background-color: transparent !important;
        border: 2px solid {text_color} !important;
        color: {text_color} !important;
    }}
    
    .stTimeInput > div > div {{
        background-color: transparent !important;
        border: 2px solid {text_color} !important;
        color: {text_color} !important;
    }}
    
    /* Streamlitのデフォルト要素を非表示 */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}
    
    /* 警告メッセージを非表示 */
    .stAlert {{display: none;}}
</style>
""", unsafe_allow_html=True)

# メイン表示
st.markdown(f"""
<div class="target-time">
    {st.session_state.target_time.strftime('%H時%M分')}{st.session_state.suffix}
</div>
""", unsafe_allow_html=True)

# 編集モード
if st.session_state.editing:
    st.markdown("### 設定変更")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_time = st.time_input(
            "時刻",
            value=st.session_state.target_time
        )
    
    with col2:
        new_suffix = st.selectbox(
            "モード",
            ["から開始", "まで"],
            index=0 if st.session_state.suffix == "から開始" else 1
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("確定"):
            if save_settings(new_time, new_suffix):
                st.session_state.target_time = new_time
                st.session_state.suffix = new_suffix
                st.session_state.editing = False
                st.session_state.time_reached = False
                st.success("設定を更新しました！")
                time.sleep(1)
                st.rerun()
            else:
                st.error("設定の保存に失敗しました")
    
    with col4:
        if st.button("キャンセル"):
            st.session_state.editing = False
            st.rerun()

else:
    # 時刻をクリックして編集モードに
    if st.button("設定を変更", key="edit_button"):
        st.session_state.editing = True
        st.rerun()

# 現在時刻表示
st.markdown(f"""
<div class="current-time">
    {now.strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)

# 日付表示
weekdays = ['月', '火', '水', '木', '金', '土', '日']
weekday = weekdays[now.weekday()]

st.markdown(f"""
<div class="date-display">
    {now.strftime('%Y年%m月%d日')}（{weekday}）
</div>
""", unsafe_allow_html=True)

# 残り時間または経過時間の表示
if st.session_state.suffix == "まで" and not st.session_state.time_reached:
    time_diff = target_dt - now
    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    st.markdown(f"""
    <div style="text-align: center; font-size: 1.5rem; color: {text_color}; margin-top: 2rem;">
        ⏳ 残り {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.suffix == "から開始" and st.session_state.time_reached:
    time_diff = now - target_dt
    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    st.markdown(f"""
    <div style="text-align: center; font-size: 1.5rem; color: {text_color}; margin-top: 2rem;">
        ⏱️ 経過 {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
    </div>
    """, unsafe_allow_html=True)

# 自動リフレッシュ
time.sleep(1)
st.rerun()
