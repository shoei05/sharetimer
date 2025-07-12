import streamlit as st
import datetime
import time
import pytz
import json
import os
import re

# ページ設定
st.set_page_config(
    page_title="共有タイマー",
    page_icon="⏰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 設定ファイルのパス
SETTINGS_FILE = "timer_settings.json"

def parse_time_input(time_str):
    """
    様々な時刻入力フォーマットを解析
    例: "07:00", "700", "0700", "7:00", "7", "19:30", "1930" など
    """
    if not time_str:
        return None
    
    # 文字列から数字とコロンのみを抽出
    clean_str = re.sub(r'[^\d:]', '', str(time_str))
    
    try:
        # コロンが含まれている場合
        if ':' in clean_str:
            parts = clean_str.split(':')
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])
            else:
                return None
        
        # コロンが含まれていない場合
        else:
            if len(clean_str) == 1:  # "7" -> "07:00"
                hour = int(clean_str)
                minute = 0
            elif len(clean_str) == 2:  # "07" -> "07:00"
                hour = int(clean_str)
                minute = 0
            elif len(clean_str) == 3:  # "700" -> "07:00"
                hour = int(clean_str[0])
                minute = int(clean_str[1:3])
            elif len(clean_str) == 4:  # "0700" -> "07:00"
                hour = int(clean_str[0:2])
                minute = int(clean_str[2:4])
            else:
                return None
        
        # 時刻の妥当性チェック
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return datetime.time(hour, minute)
        else:
            return None
            
    except (ValueError, IndexError):
        return None

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
if 'force_color_change' not in st.session_state:
    st.session_state.force_color_change = False

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

# 背景色の変更（手動切り替えも含む）
if (time_reached and not st.session_state.time_reached) or st.session_state.force_color_change:
    st.session_state.time_reached = True
elif not time_reached and not st.session_state.force_color_change:
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
        padding: 1rem;
        border-radius: 10px;
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
    
    .time-info {{
        font-size: 1.5rem;
        color: {text_color};
        text-align: center;
        margin: 2rem 0;
    }}
    
    .settings-section {{
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid {text_color};
        opacity: 0.7;
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
    
    .stTextInput > div > div > input {{
        background-color: white !important;
        border: 2px solid {text_color} !important;
        color: #333333 !important;
        text-align: center !important;
        font-size: 1.2rem !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        outline: none !important;
        box-shadow: 0 0 0 2px {text_color} !important;
    }}
    
    .stTextInput > div > div > input::placeholder {{
        color: #666666 !important;
        opacity: 0.8 !important;
    }}
    
    .stSelectbox > div > div {{
        background-color: white !important;
        border: 2px solid {text_color} !important;
        color: #333333 !important;
    }}
    
    .stSelectbox > div > div > div {{
        color: #333333 !important;
    }}
    
    .color-toggle-btn {{
        margin-top: 1rem;
        opacity: 0.8;
    }}
    
    /* Streamlitのデフォルト要素を非表示 */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}
    
    /* 警告メッセージのスタイル */
    .stAlert {{
        background-color: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid #ffc107 !important;
        color: {text_color} !important;
    }}
    
    .input-help {{
        font-size: 0.9rem;
        color: {text_color};
        opacity: 0.7;
        text-align: center;
        margin-top: 0.5rem;
    }}
</style>
""", unsafe_allow_html=True)

# メイン表示
st.markdown(f"""
<div class="target-time">
    {st.session_state.target_time.strftime('%H時%M分')}{st.session_state.suffix}
</div>
""", unsafe_allow_html=True)

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
    <div class="time-info">
        ⏳ 残り {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.suffix == "から開始" and st.session_state.time_reached:
    time_diff = now - target_dt
    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    st.markdown(f"""
    <div class="time-info">
        ⏱️ 経過 {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
    </div>
    """, unsafe_allow_html=True)

# 設定セクション（一番下）
st.markdown('<div class="settings-section">', unsafe_allow_html=True)

# 編集モード
if st.session_state.editing:
    st.markdown("### ⚙️ 設定変更")
    
    # 時刻入力（全選択機能付き）
    time_input = st.text_input(
        "時刻",
        value=st.session_state.target_time.strftime('%H:%M'),
        placeholder="例: 07:00, 700, 0700, 19:30, 1930",
        help="様々な形式で入力可能です",
        key="time_input_field"
    )
    
    # JavaScript for auto-select on focus
    st.markdown("""
    <script>
    // フォーカス時に全選択
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            const input = document.querySelector('input[aria-label="時刻"]');
            if (input) {
                input.addEventListener('focus', function() {
                    this.select();
                });
                input.addEventListener('click', function() {
                    this.select();
                });
            }
        }, 1000);
    });
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="input-help">
        入力例: 07:00, 700, 0700, 7:00, 7, 19:30, 1930
    </div>
    """, unsafe_allow_html=True)
    
    # モード選択
    new_suffix = st.selectbox(
        "モード",
        ["から開始", "まで"],
        index=0 if st.session_state.suffix == "から開始" else 1
    )
    
    # 時刻の解析とプレビュー
    parsed_time = parse_time_input(time_input)
    if parsed_time:
        st.success(f"✅ 認識された時刻: {parsed_time.strftime('%H:%M')}")
    elif time_input.strip():
        st.warning("⚠️ 時刻の形式が正しくありません")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("確定"):
            if parsed_time:
                if save_settings(parsed_time, new_suffix):
                    st.session_state.target_time = parsed_time
                    st.session_state.suffix = new_suffix
                    st.session_state.editing = False
                    st.session_state.time_reached = False
                    st.success("設定を更新しました！")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("設定の保存に失敗しました")
            else:
                st.error("正しい時刻を入力してください")
    
    with col2:
        if st.button("キャンセル"):
            st.session_state.editing = False
            st.rerun()

else:
    # 設定ボタン
    if st.button("⚙️ 設定を変更", key="edit_button"):
        st.session_state.editing = True
        st.rerun()

# 色切り替えボタン
st.markdown('<div class="color-toggle-btn">', unsafe_allow_html=True)
current_color_status = "ピンク" if st.session_state.time_reached else "グレー"
toggle_color_status = "グレー" if st.session_state.time_reached else "ピンク"

if st.button(f"🎨 色を{toggle_color_status}に切り替え", key="color_toggle"):
    if st.session_state.time_reached:
        # ピンクからグレーに
        st.session_state.time_reached = False
        st.session_state.force_color_change = False
    else:
        # グレーからピンクに
        st.session_state.time_reached = True
        st.session_state.force_color_change = True
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 自動リフレッシュ
time.sleep(1)
st.rerun()
