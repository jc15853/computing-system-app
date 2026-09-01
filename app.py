import streamlit as st

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="피지컬 컴퓨팅 시스템 설계기",
    page_icon="🤖",
    layout="centered"
)

# 커스텀 UI 스타일링
custom_css = """
<style>
    header[data-testid="stHeader"], footer, div[data-testid="stDecoration"] {
        display: none !important;
    }
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3, h4 {
        color: #58a6ff !important;
    }
    .report-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .step-box {
        background-color: #1c2128;
        border-left: 4px solid #58a6ff;
        padding: 12px 15px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🤖 나만의 피지컬 컴퓨팅 시스템 설계기")
st.subheader("중1 정보 [1. 컴퓨팅 시스템] - 입력·처리·출력으로 동작하는 자동화 시스템 설계")

st.info("""
💡 **학습 목표:**
우리 주변의 스마트 기술(스마트홈, 자동 가로등 등)이 
**어떤 센서(입력)**로 외부 환경을 감지하고, **어떤 조건(처리)**을 판단하여, **어떤 장치(출력)**로 동작하는지 직접 설계해봅시다.
""")

st.divider()

# -----------------------------------------------------------------------------
# Step 1. 사례 선택
# -----------------------------------------------------------------------------
st.markdown("### 1️⃣ 설계할 스마트 시스템 사례 선택하기")

case_options = {
    "㉠ 미세먼지 자동 환기 시스템": {
        "num": "㉠",
        "title": "미세먼지 자동 환기 시스템",
        "sensors": ["미세먼지 센서", "온습도 센서", "조도(빛) 센서", "카메라 (차량번호 인식)"],
        "correct_sensor": "미세먼지 센서",
        "outputs": ["환기 팬 (모터)", "LED 전구", "스피커 (경적)", "서보모터 (차단기)"],
        "correct_output": "환기 팬 (모터)",
        "default_condition": "실내 미세먼지 농도가 기준치(80㎍/㎥) 이상으로 높아지면"
    },
    "㉢ 주차장 자동 차단기 시스템": {
        "num": "㉢",
        "title": "주차장 자동 차단기 시스템",
        "sensors": ["카메라 (차량번호 인식)", "미세먼지 센서", "소음 센서", "초음파 거리 센서"],
        "correct_sensor": "카메라 (차량번호 인식)",
        "outputs": ["서보모터 (차단기 바)", "LED 전구", "환기 팬 (모터)", "스피커 (경적)"],
        "correct_output": "서보모터 (차단기 바)",
        "default_condition": "진입하는 차량의 번호판을 인식하여 등록된 입주민 차량임이 확인되면"
    },
    "㉤ 스마트 가로등 자동 점등 시스템": {
        "num": "㉤",
        "title": "스마트 가로등 자동 점등 시스템",
        "sensors": ["조도(빛) 센서", "미세먼지 센서", "온도 센서", "인체 감지 센서"],
        "correct_sensor": "조도(빛) 센서",
        "outputs": ["가로등 LED 전구", "환기 팬 (모터)", "서보모터 (차단기)", "스피커 (경적)"],
        "correct_output": "가로등 LED 전구",
        "default_condition": "해가 지거나 주변이 어두워져 빛의 양(조도)이 일정 수치 이하로 떨어지면"
    }
}

selected_case_name = st.selectbox("사례를 고르세요:", list(case_options.keys()))
selected_case = case_options[selected_case_name]

st.divider()

# -----------------------------------------------------------------------------
# Step 2. 입력 - 처리 - 출력 설계하기
# -----------------------------------------------------------------------------
st.markdown("### 2️⃣ 컴퓨팅 시스템 3단계 설계 (입력 ➔ 처리 ➔ 출력)")

col1, col2, col3 = st.columns(3)

# 1. 입력 장치 선택
with col1:
    st.markdown("#### 📥 1. 입력 (Input)")
    user_sensor = st.radio("필요한 **입력 장치(센서)**는?", selected_case["sensors"])

# 2. 처리 조건 작성
with col2:
    st.markdown("#### ⚙️ 2. 처리 (Process)")
    user_condition = st.text_area(
        "어떤 **조건**일 때 작동할까요?", 
        value=selected_case["default_condition"],
        height=120
    )

# 3. 출력 장치 선택
with col3:
    st.markdown("#### 📤 3. 출력 (Output)")
    user_output = st.radio("필요한 **출력 장치**는?", selected_case["outputs"])

st.divider()

# -----------------------------------------------------------------------------
# Step 3. 검증 및 서논술형 답안지(리포트) 생성
# -----------------------------------------------------------------------------
if st.button("🚀 시스템 설계 완료 및 서논술형 리포트 생성", type="primary", use_container_width=True):
    
    st.markdown("---")
    st.markdown("### 📋 내가 작성한 피지컬 컴퓨팅 시스템 설계 리포트")
    
    # 올바른 부품을 찾았는지 검증
    is_sensor_ok = (user_sensor == selected_case["correct_sensor"])
    is_output_ok = (user_output == selected_case["correct_output"])
    
    sensor_badge = "✅ (정확함)" if is_sensor_ok else "❌ (다시 고민해봅시다)"
    output_badge = "✅ (정확함)" if is_output_ok else "❌ (다시 고민해봅시다)"
    
    report_html = f"""
    <div class="report-card">
        <h3 style="margin-top:0;">[ 선택한 사례: {selected_case_name} ]</h3>
        <p><strong>(1) 선택한 사례 번호:</strong> {selected_case['num']}</p>
        <p><strong>(2) 시스템 구성 부품:</strong></p>
        <ul>
            <li><strong>입력장치:</strong> {user_sensor} {sensor_badge}</li>
            <li><strong>출력장치:</strong> {user_output} {output_badge}</li>
        </ul>
        <hr style="border-color: #30363d;">
        <p><strong>(3) 컴퓨팅 시스템 3단계 작동 과정 서술:</strong></p>
        <div class="step-box">
            <strong>📥 [입력 단계]:</strong> {user_sensor}(으)로 외부의 물리적 변화나 데이터(신호)를 감지하여 컴퓨팅 시스템이 이해할 수 있는 형태로 받아들인다.
        </div>
        <div class="step-box">
            <strong>⚙️ [처리 단계]:</strong> 입력받은 데이터를 분석하여 <i>"{user_condition}"</i> 조건에 해당하는지 연산 및 판단한다.
        </div>
        <div class="step-box">
            <strong>📤 [출력 단계]:</strong> 판단 결과에 따라 {user_output}(을)를 작동시켜 정해진 동작을 실행한다.
        </div>
    </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)
    
    # 힌트 및 피드백
    if is_sensor_ok and is_output_ok:
        st.balloons()
        st.success("🎉 **완벽한 설계입니다!** 외부 환경 데이터를 센서로 받아들여 조건 판단 후 출력장치로 연결하는 피지컬 컴퓨팅 시스템의 핵심 동작 원리를 정확히 서술했습니다.")
    else:
        st.warning("💡 **개념 피드백:** 선택한 입력장치(센서)나 출력장치(액추에이터)가 해당 시스템의 기능과 직접 연결되는지 다시 한번 점검해보세요.")
