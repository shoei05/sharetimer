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
    """設定を読み込み（色の状態も含む）"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                time_obj = datetime.datetime.strptime(data['time'], '%H:%M').time()
                return (
                    time_obj, 
                    data['suffix'], 
                    data.get('timestamp', ''),
                    data.get('color_state', False),
                    data.get('force_color', False)
                )
    except:
        pass
    return datetime.time(23, 59), "から開始", "", False, False

def save_settings(target_time, suffix, color_state=False, force_color=False):
    """設定を保存（色の状態も含む）"""
    try:
        data = {
            'time': target_time.strftime('%H:%M'),
            'suffix': suffix,
            'color_state': color_state,
            'force_color': force_color,
            'timestamp': datetime.datetime.now().isoformat()
        }
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except:
        return False

# 設定を読み込み
shared_time, shared_suffix, last_timestamp, shared_color_state, shared_force_color = load_settings()

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
current_time, current_suffix, current_timestamp, current_color_state, current_force_color = load_settings()
if current_timestamp != st.session_state.last_timestamp and current_timestamp != "":
    st.session_state.target_time = current_time
    st.session_state.suffix = current_suffix
    st.session_state.last_timestamp = current_timestamp
    
    # 他の端末からの色設定を同期
    st.session_state.time_reached = current_color_state
    st.session_state.force_color_change = current_force_color

# 日本時間の設定
jst = pytz.timezone('Asia/Tokyo')
now = datetime.datetime.now(jst)

# 目標時刻の設定（今日基準で計算）
target_dt = datetime.datetime.combine(datetime.date.today(), st.session_state.target_time)
target_dt = jst.localize(target_dt)

# 時刻到達の判定（今日の目標時刻と比較）
current_time_reached = now.time() >= st.session_state.target_time

# 時刻到達時の自動反転処理
if current_time_reached and not st.session_state.time_reached:
    # 時刻に到達した瞬間の自動反転
    st.session_state.time_reached = True
    st.session_state.force_color_change = True
    # 設定を保存して他の端末にも同期
    save_settings(st.session_state.target_time, st.session_state.suffix, True, True)
    st.balloons()  # お祝い効果
elif not current_time_reached and not st.session_state.force_color_change:
    # 時刻前でかつ手動切り替えしていない場合はグレー
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
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 10px;
        line-height: 0.9;
    }}
    
    .current-time {{
        font-size: 6rem;
        font-weight: bold;
        color: {text_color};
        text-align: center;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        line-height: 0.9;
    }}
    
    .date-display {{
        font-size: 1.8rem;
        color: {text_color};
        text-align: center;
        margin: 0.5rem 0 1rem 0;
        line-height: 1;
    }}
    
    .time-info {{
        font-size: 1.5rem;
        color: {text_color};
        text-align: center;
        margin: 1rem 0;
        line-height: 1;
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
    # 今日の目標時刻まで
    target_for_calc = datetime.datetime.combine(datetime.date.today(), st.session_state.target_time)
    target_for_calc = jst.localize(target_for_calc)
    
    # 目標時刻が過去の場合は明日として計算
    if target_for_calc <= now:
        target_for_calc = target_for_calc + datetime.timedelta(days=1)
    
    time_diff = target_for_calc - now
    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    st.markdown(f"""
    <div class="time-info">
        ⏳ 残り {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.suffix == "から開始" and not st.session_state.time_reached:
    # 今日の開始時刻まで
    target_for_calc = datetime.datetime.combine(datetime.date.today(), st.session_state.target_time)
    target_for_calc = jst.localize(target_for_calc)
    
    # 開始時刻が過去の場合は明日として計算
    if target_for_calc <= now:
        target_for_calc = target_for_calc + datetime.timedelta(days=1)
    
    time_diff = target_for_calc - now
    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    st.markdown(f"""
    <div class="time-info">
        ⏳ 残り {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.time_reached:
    # ピンク状態では経過時間を表示（今日の目標時刻から）
    target_today = datetime.datetime.combine(datetime.date.today(), st.session_state.target_time)
    target_today = jst.localize(target_today)
    
    time_diff = now - target_today
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
        key=f"time_input_field_{st.session_state.editing}"
    )
    
    # より確実なJavaScript全選択機能
    st.markdown(f"""
    <script>
    setTimeout(function() {{
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(function(input) {{
            if (input.value.includes(':')) {{
                input.addEventListener('focus', function() {{
                    setTimeout(() => this.select(), 50);
                }});
                input.addEventListener('click', function() {{
                    setTimeout(() => this.select(), 50);
                }});
                // 初回フォーカス時の全選択
                if (document.activeElement !== input) {{
                    input.focus();
                    setTimeout(() => input.select(), 100);
                }}
            }}
        }});
    }}, 500);
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
        # 入力時刻の状態を判定
        preview_dt = datetime.datetime.combine(datetime.date.today(), parsed_time)
        preview_dt = jst.localize(preview_dt)
        
        time_status = ""
        if new_suffix == "から開始" and preview_dt <= now:
            time_status = " (開始時刻を過ぎています - 色が反転します)"
        elif new_suffix == "まで" and preview_dt <= now:
            time_status = " (期限を過ぎています - 色が反転します)"
        elif preview_dt > now:
            time_status = " (未来の時刻です)"
        
        st.success(f"✅ 認識された時刻: {parsed_time.strftime('%H:%M')}{time_status}")
    elif time_input.strip():
        st.warning("⚠️ 時刻の形式が正しくありません")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("確定"):
            if parsed_time:
                # 入力された時刻が現在時刻を過ぎているかチェック
                input_dt = datetime.datetime.combine(datetime.date.today(), parsed_time)
                input_dt = jst.localize(input_dt)
                
                # 時刻判定と色の自動切り替え
                if new_suffix == "から開始" and input_dt <= now:
                    # 「から開始」で過去の時刻の場合、即座に色を反転
                    auto_color_change = True
                    auto_force_change = True
                elif new_suffix == "まで" and input_dt <= now:
                    # 「まで」で過去の時刻の場合も反転（期限切れ）
                    auto_color_change = True
                    auto_force_change = True
                else:
                    # 未来の時刻の場合は通常色（強制変更もリセット）
                    auto_color_change = False
                    auto_force_change = False
                
                if save_settings(parsed_time, new_suffix, auto_color_change, auto_force_change):
                    st.session_state.target_time = parsed_time
                    st.session_state.suffix = new_suffix
                    st.session_state.editing = False
                    
                    # 色の自動設定
                    st.session_state.time_reached = auto_color_change
                    st.session_state.force_color_change = auto_force_change
                    
                    if auto_color_change:
                        st.success("設定を更新しました！（時刻を過ぎているため色を反転）")
                    else:
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
    new_color_state = not st.session_state.time_reached
    new_force_state = new_color_state  # 手動切り替えの場合は force_color_change を設定
    
    # 色の状態を保存して他の端末に同期
    if save_settings(st.session_state.target_time, st.session_state.suffix, new_color_state, new_force_state):
        st.session_state.time_reached = new_color_state
        st.session_state.force_color_change = new_force_state
        st.session_state.last_timestamp = get_last_update_time() if 'get_last_update_time' in locals() else datetime.datetime.now().isoformat()
        st.rerun()
    else:
        st.error("色の変更を保存できませんでした")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 自動リフレッシュ
time.sleep(1)
st.rerun()
