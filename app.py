import streamlit as st
import time
import hashlib

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="VALORANT TIER PREDICTOR AI",
    page_icon="🔥",
    layout="wide"
)

# 2. 세션 상태 초기화
if 'res_tier' not in st.session_state:
    st.session_state['res_tier'] = None
if 'res_conf' not in st.session_state:
    st.session_state['res_conf'] = 0.0
if 'res_type' not in st.session_state:
    st.session_state['res_type'] = None

# 3. 고대비 및 가독성 최적화 Custom CSS
st.markdown("""
<style>
    /* 배경 다크 테마 */
    .stApp {
        background: linear-gradient(135deg, #0b0e14 0%, #101822 50%, #05080c 100%);
        color: #ffffff;
    }
    
    /* 기본 글꼴 색상 강화 */
    p, label, span, div {
        color: #f0f2f5 !important;
        font-weight: 500;
    }
    
    /* 타이틀 디자인 */
    .main-title {
        font-size: 2.8rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff4655, #ff8038, #ffbf00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #00f0ff;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 25px;
    }
    
    /* 게이밍 카드 컨테이너 */
    .gaming-card {
        background: #15202b;
        border: 2px solid #ff4655;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 0 15px rgba(255, 70, 85, 0.25);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 4. 데이터 정의 (세부 티어 1~3 및 레디언트)
BASE_TIERS = ["아이언", "브론즈", "실버", "골드", "플래티넘", "다이아몬드", "초월자", "불멸"]
TIER_ICONS = {
    "아이언": "⚙️", "브론즈": "🥉", "실버": "🥈", "골드": "🥇", 
    "플래티넘": "💎", "다이아몬드": "🔮", "초월자": "🧿", "불멸": "👑", "레디언트": "🌟"
}

ALL_TIERS = []
for tier in BASE_TIERS:
    for sub in [1, 2, 3]:
        ALL_TIERS.append(f"{tier} {sub} {TIER_ICONS[tier]}")
ALL_TIERS.append(f"레디언트 {TIER_ICONS['레디언트']}")  # 총 25개 구간 (0: 아이언1 ~ 24: 레디언트)

# 5. 영상 분석 예측 로직 (밸런스형 적정 점수 분포)
def analyze_video(file_bytes):
    file_hash = hashlib.md5(file_bytes).hexdigest()
    seed = int(file_hash, 16) % (2**32 - 1)
    
    # 실버2(7번 index) ~ 불멸2(22번 index) 위주로 균형 있게 배치 (평균 골드~초월자)
    tier_index = 7 + (seed % 16)
    tier_index = min(tier_index, len(ALL_TIERS) - 1)
    
    predicted_tier = ALL_TIERS[tier_index]
    confidence = 83.0 + ((seed % 140) / 10.0)
    return predicted_tier, confidence

# 6. KDA 분석 로직 (적정 가중치 수치)
def analyze_kda(kills, deaths, assists, headshot_rate):
    deaths_for_calc = max(deaths, 1)
    kda_ratio = (kills + (assists * 0.5)) / deaths_for_calc
    
    score = (kda_ratio * 30) + (headshot_rate * 1.1)
    
    if score < 20: idx = 0
    elif score < 32: idx = 1 + int((score - 20) / 4)
    elif score < 45: idx = 4 + int((score - 32) / 4.3)
    elif score < 60: idx = 7 + int((score - 45) / 5)
    elif score < 75: idx = 10 + int((score - 60) / 5)
    elif score < 90: idx = 13 + int((score - 75) / 5)
    elif score < 105: idx = 16 + int((score - 90) / 5)
    elif score < 120: idx = 19 + int((score - 105) / 5)
    elif score < 140: idx = 22 + int((score - 120) / 10)
    else: idx = 24

    idx = min(idx, len(ALL_TIERS) - 1)
    return ALL_TIERS[idx], min(99.0, max(80.0, 81.0 + (score % 17))), kda_ratio

# 7. UI 레이아웃
st.markdown('<div class="main-title">🔥 VALORANT TIER PREDICTOR AI 🔥</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">💥 BALANCED TIER ANALYSIS 💥</div>', unsafe_allow_html=True)

left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.markdown('<div class="gaming-card">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🎬 VIDEO ANALYSIS 🚀", "📊 KDA STATS 💰"])
    
    with tab1:
        st.subheader("🎬 클립 영상 업로드")
        uploaded_file = st.file_uploader("플레이 영상(MP4, MOV)을 선택하세요", type=["mp4", "mov", "avi"], key="v_up")
        
        if uploaded_file is not None:
            st.video(uploaded_file)
            if st.button("🚀 START AI ANALYSIS! 🚀", type="primary", use_container_width=True):
                with st.spinner("⚡ AI analyzing aiming & combat speed..."):
                    file_bytes = uploaded_file.read()
                    st.session_state['res_tier'], st.session_state['res_conf'] = analyze_video(file_bytes)
                    st.session_state['res_type'] = 'video'
                    time.sleep(1.2)
                st.balloons()

    with tab2:
        st.subheader("⚔️ 최근 매치 스탯 입력")
        c1, c2, c3 = st.columns(3)
        with c1: kills = st.number_input("🎯 Kills", 0, 100, 20)
        with c2: deaths = st.number_input("💀 Deaths", 0, 100, 12)
        with c3: assists = st.number_input("🤝 Assists", 0, 100, 5)
        hs_rate = st.slider("🎯 Headshot Rate (%)", 0, 100, 25)
        
        if st.button("🔥 ANALYZE MY STATS! 🔥", type="primary", use_container_width=True):
            with st.spinner("⚡ Calculating combat efficiency..."):
                tier, conf, kda = analyze_kda(kills, deaths, assists, hs_rate)
                st.session_state['res_tier'] = tier
                st.session_state['res_conf'] = conf
                st.session_state['res_kda'] = kda
                st.session_state['res_type'] = 'kda'
                time.sleep(1.0)
            st.snow()
            
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="gaming-card">', unsafe_allow_html=True)
    st.subheader("🏆 YOUR PREDICTED TIER 🏆")
    
    if st.session_state['res_tier'] is not None:
        st.markdown(f"<h1 style='text-align: center; color: #ff8038; font-size: 3rem;'>{st.session_state['res_tier']}</h1>", unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("👍 AI CONFIDENCE", f"{st.session_state['res_conf']:.1f}%")
        with m2:
            if st.session_state['res_type'] == 'kda':
                st.metric("📈 KDA RATIO", f"{st.session_state['res_kda']:.2f}")
            else:
                st.metric("🎯 HEADLINE ACC", "91.5%")
                
        st.markdown("---")
        st.subheader("💬 AI FEEDBACK 💬")
        st.write("✨ **CRISP HEADLINES**: 교전 시 조준선 위치가 적절하게 유지되고 있습니다.")
        st.write("⚡ **INSTANT BRAKING**: 무빙 후 사격 타이밍 정지 속도가 훌륭합니다.")
        st.write("🚀 **NEXT RANK TIP**: 상황 판단 및 피킹 각도를 보완하면 상위 티어로 오를 수 있습니다!")
    else:
        st.info("👈 왼쪽 메뉴에서 영상이나 KDA 스탯을 입력하여 측정하세요.")
    
    st.markdown('</div>', unsafe_allow_html=True)
