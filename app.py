import streamlit as st
import datetime
import time
import pytz

# ページ設定
st.set_page_config(
    page_title="共有タイマー",
    page_icon="⏰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# セッション状態の初期化
if 'target_time' not in st.session_state:
    st.session_state.target_time = datetime.time(23, 59)
if 'suffix' not in st.session_state:
    st.session_state.suffix = "から開始"
if 'time_reached' not in st.session_state:
    st.session_state.time_reached = False

# 日本時間の設定
jst = pytz.timezone('Asia/Tokyo')

# カスタムCSS
st.markdown("""
<style>
    .main-container {
        text-align: center;
        padding: 2rem;
    }
    .time-display {
        font-size: 4rem;
        font-weight: bold;
        margin: 2rem 0;
        font-family: 'Courier New', monospace;
    }
    .date-display {
        font-size: 1.5rem;
        margin: 1rem 0;
        color: #666;
    }
    .target-time {
        font-size: 1.2rem;
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f0f0f0;
        border-radius: 10px;
    }
    .reached-bg {
        background-color: #c5487b !important;
        color: white !important;
    }
    .reached-text {
        color: white !important;
    }
    .stSelectbox label, .stTimeInput label {
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# メインコンテナ
with st.container():
    st.title("⏰ 共有タイマー")
    
    # 設定セクション
    st.subheader("⚙️ 設定")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        new_time = st.time_input(
            "目標時刻を設定してください",
            value=st.session_state.target_time,
            key="time_input"
        )
    
    with col2:
        new_suffix = st.selectbox(
            "表示モード",
            ["から開始", "まで"],
            index=0 if st.session_state.suffix == "から開始" else 1,
            key="suffix_select"
        )
    
    # 設定の更新
    if new_time != st.session_state.target_time:
        st.session_state.target_time = new_time
        st.session_state.time_reached = False
        st.rerun()
    
    if new_suffix != st.session_state.suffix:
        st.session_state.suffix = new_suffix
        st.session_state.time_reached = False
        st.rerun()
    
    st.divider()
    
    # 現在時刻の取得
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
        st.balloons()  # 到達時のお祝い効果
    elif not time_reached:
        st.session_state.time_reached = False
    
    # 時刻表示
    if st.session_state.time_reached:
        st.markdown(f"""
        <div style="background-color: #c5487b; padding: 2rem; border-radius: 15px; margin: 2rem 0;">
            <div style="font-size: 4rem; font-weight: bold; color: white; font-family: 'Courier New', monospace;">
                {now.strftime('%H:%M:%S')}
            </div>
            <div style="font-size: 1.5rem; color: white; margin-top: 1rem;">
                {now.strftime('%Y年%m月%d日 (%A)')}
            </div>
            <div style="font-size: 1.5rem; color: white; margin-top: 1rem; font-weight: bold;">
                🎉 時刻に到達しました！ 🎉
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; border: 2px solid #e0e0e0; border-radius: 15px; margin: 2rem 0;">
            <div style="font-size: 4rem; font-weight: bold; color: #333; font-family: 'Courier New', monospace;">
                {now.strftime('%H:%M:%S')}
            </div>
            <div style="font-size: 1.5rem; color: #666; margin-top: 1rem;">
                {now.strftime('%Y年%m月%d日 (%A)')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 目標時刻の表示
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #007bff;">
        <div style="font-size: 1.2rem; font-weight: bold; color: #333;">
            📅 目標時刻: {st.session_state.target_time.strftime('%H:%M')} {st.session_state.suffix}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 残り時間の表示（目標時刻まで）
    if st.session_state.suffix == "まで" and not st.session_state.time_reached:
        time_diff = target_dt - now
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        st.markdown(f"""
        <div style="background-color: #e8f4f8; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #17a2b8;">
            <div style="font-size: 1.2rem; font-weight: bold; color: #333;">
                ⏳ 残り時間: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 経過時間の表示（開始から）
    elif st.session_state.suffix == "から開始" and st.session_state.time_reached:
        time_diff = now - target_dt
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        st.markdown(f"""
        <div style="background-color: #f8e8e8; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #dc3545;">
            <div style="font-size: 1.2rem; font-weight: bold; color: #333;">
                ⏱️ 経過時間: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 自動リフレッシュ
placeholder = st.empty()
with placeholder.container():
    st.info("🔄 自動更新中... このページを開いたままにしてください")

# 1秒ごとに自動更新
time.sleep(1)
st.rerun()
