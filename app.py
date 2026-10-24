import streamlit as st
from openai import OpenAI

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 깔끔한 라이트 모드 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="피지컬 컴퓨팅 시스템 설계기",
    page_icon="🤖",
    layout="centered"
)

# 글자가 또렷하게 보이도록 스타일 재정의
custom_css = """
<style>
    /* 기본 배경 및 글자색 고정 */
    .stApp {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        font-family: 'Pretendard', sans-serif;
    }
    
    /* 제목 및 강조 텍스트 색상 */
    h1, h2, h3, h4 {
        color: #1e3a8a !important;
        font-weight: bold !important;
    }
    
    /* 본문 일반 글자색 명확화 */
    p, span, label, div {
        color: #1f2937 !important;
    }

    /* 카드 형태의 리포트 박스 */
    .report-card {
        background-color: #f8fafc;
        border: 2px solid #2563eb;
        border-radius: 12px;
        padding: 24px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    .step-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #2563eb;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 8px;
        margin-bottom: 12px;
        color: #0f172a !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# OpenAI 클라이언트 초기화 (Streamlit Secrets 또는 사이드바 입력 활용)
# -----------------------------------------------------------------------------
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    with st.sidebar:
        st.subheader("⚙️ 설정")
        api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

st.title("나만의 피지컬 컴퓨팅 시스템 설계하기")

st.info("""
💡 우리 주변의 스마트 기술이 외부 환경을 어떤 
**입력 장치**
로 감지하고,\n
어떤 
**조건**
에 따라 작동하며,\n
어떤
**출력 장치**
로 결과를 나타내는지 직접 설계해 봅시다.
""")

st.divider()

# -----------------------------------------------------------------------------
# 1. 시스템 선택 및 공통 입력/출력 장치 목록 정의
# -----------------------------------------------------------------------------
st.markdown("### 1️⃣ 시스템")

case_options = {
    "미세먼지 자동 환기 시스템": {
        "title": "미세먼지 자동 환기 시스템",
        "correct_sensor": "미세먼지 센서",
        "correct_output": "환기 팬 (모터)",
        "default_condition": "실내 미세먼지 농도가 기준치(80㎍/㎥) 이상으로 높아지면",
        "system_goal": "실내 미세먼지 수치를 측정하고 기준치 이상일 때 환기팬을 켜는 시스템"
    },
    "주차장 자동 차단기 시스템": {
        "title": "주차장 자동 차단기 시스템",
        "correct_sensor": "카메라 (차량번호 인식)",
        "correct_output": "서보모터 (차단기 바)",
        "default_condition": "진입하는 차량의 번호판을 인식하여 등록된 입주민 차량임이 확인되면",
        "system_goal": "진입 차량의 번호판을 카메라로 인식한 뒤, 등록된 차량인지 판단/확인하여 차단기를 여는 시스템"
    },
    "스마트 가로등 자동 점등 시스템": {
        "title": "스마트 가로등 자동 점등 시스템",
        "correct_sensor": "조도(빛) 센서",
        "correct_output": "가로등 LED 전구",
        "default_condition": "해가 지거나 주변이 어두워져 빛의 양(조도)이 일정 수치 이하로 떨어지면",
        "system_goal": "주변의 밝기(조도)를 측정하여 어두워지면 가로등을 켜는 시스템"
    }
}

fixed_sensors = [
    "미세먼지 센서", 
    "온습도 센서", 
    "조도(빛) 센서", 
    "카메라 (차량번호 인식)", 
    "소음 센서", 
    "초음파 거리 센서", 
    "온도 센서", 
    "인체 감지 센서"
]

fixed_outputs = [
    "환기 팬 (모터)", 
    "LED 전구", 
    "스피커 (경적)", 
    "서보모터 (차단기 바)", 
    "가로등 LED 전구"
]

selected_case_name = st.selectbox("설계할 시스템을 선택하세요:", list(case_options.keys()))
selected_case = case_options[selected_case_name]

st.divider()

# -----------------------------------------------------------------------------
# Step 2. 입력 - 처리 - 출력 설계하기
# -----------------------------------------------------------------------------
st.markdown("### 2️⃣ 컴퓨팅 시스템 3단계")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📥 입력")
    user_sensor = st.radio("**필요한 입력 장치는 무엇일까요?**", fixed_sensors)

with col2:
    st.markdown("#### ⚙️ 처리")
    user_condition = st.text_area(
        "**어떤 조건일 때 작동할까요?**", 
        value=selected_case["default_condition"],
        height=120
    )

with col3:
    st.markdown("#### 📤 출력")
    user_output = st.radio("**필요한 출력 장치는 무엇일까요?**", fixed_outputs)

# -----------------------------------------------------------------------------
# Step 3. 검증 및 AI 판정 기능 실행
# -----------------------------------------------------------------------------
if st.button("🚀 컴퓨팅 시스템 설계하기", type="primary", use_container_width=True):
    
    if not api_key:
        st.error("⚠️ OpenAI API Key가 입력되지 않았습니다. 사이드바나 코드를 통해 API 키를 설정해주세요.")
    else:
        with st.spinner("🤖 AI가 시스템 설계를 정밀하게 분석하고 있습니다..."):
            try:
                client = OpenAI(api_key=api_key)
                
                prompt = f"""
                당신은 초·중등 정보 교육 피지컬 컴퓨팅 시스템 평가 AI입니다.
                학생이 선택한 시스템과 작성한 '처리 조건'을 보고, 이 조건이 시스템의 목적에 논리적으로 부합하는지 평가해주세요.

                [시스템 정보]
                - 시스템 이름: {selected_case_name}
                - 시스템 핵심 목표: {selected_case['system_goal']}

                [학생이 작성한 처리 조건]
                "{user_condition}"

                [평가 기준]
                - 단순히 입력만 하는 것(예: "번호판을 인식한다")에 그치지 않고, 시스템이 작동하기 위한 **판단/비교/확인 과정(예: 등록된 차량인지 확인, 기준치 이상인지 비교 등)**이 문장에 논리적으로 포함되어 있어야 합니다.
                - 엉뚱한 내용이거나 핵심 판단 과정이 빠져있다면 False, 적절하다면 True를 반환하세요.

                반드시 아래 JSON 형식으로만 답해주세요. (다른 부가 설명 없이 오직 JSON만 출력)
                {{"is_valid": true 또는 false, "feedback": "학생에게 줄 친절하고 구체적인 피드백 문장"}}
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(response.choices[0].message.content)
                is_condition_ok = result.get("is_valid", False)
                ai_feedback = result.get("feedback", "")
                
            except Exception as e:
                st.error(f"API 호출 중 오류가 발생했습니다: {e}")
                is_condition_ok = False
                ai_feedback = "AI 판정 중 오류가 발생했습니다."

        is_sensor_ok = (user_sensor == selected_case["correct_sensor"])
        is_output_ok = (user_output == selected_case["correct_output"])
        
        sensor_badge = "✅ (정확함)" if is_sensor_ok else "❌ (다시 고민해봅시다)"
        condition_badge = "✅ (적절한 조건)" if is_condition_ok else "⚠️ (조건 검토 필요)"
        output_badge = "✅ (정확함)" if is_output_ok else "❌ (다시 고민해봅시다)"
        
        report_html = f"""
        <div class="report-card">
            <h3 style="margin-top:0; color: #1e3a8a;">[ 선택한 사례: {selected_case_name} ]</h3>
            <p><strong>시스템 구성 부품 및 AI 검증 결과:</strong></p>
            <ul>
                <li><strong>입력장치:</strong> {user_sensor} {sensor_badge}</li>
                <li><strong>처리조건:</strong> {condition_badge} <br><small style="color: #4b5563;">💡 AI 피드백: {ai_feedback}</small></li>
                <li><strong>출력장치:</strong> {user_output} {output_badge}</li>
            </ul>
            <hr style="border-color: #cbd5e1; margin: 15px 0;">
            <p><strong>(3) 컴퓨팅 시스템 3단계 작동 과정 서술:</strong></p>
            <div class="step-box">
                <strong>📥 [입력]:</strong> {user_sensor}(으)로 외부의 물리적 변화나 데이터(신호)를 감지하여 컴퓨팅 시스템이 이해할 수 있는 형태로 받아들인다.
            </div>
            <div class="step-box">
                <strong>⚙️ [처리]:</strong> 입력받은 데이터를 분석하여 <i>"{user_condition}"</i> 조건에 해당하는지 연산 및 판단한다.
            </div>
            <div class="step-box">
                <strong>📤 [출력]:</strong> 판단 결과에 따라 {user_output}(을)를 작동시켜 정해진 동작을 실행한다.
            </div>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)
        
        if is_sensor_ok and is_output_ok and is_condition_ok:
            st.balloons()
            st.success("🎉 **완벽한 설계입니다!** 입력, 조건 판단, 출력장치까지 AI가 분석했을 때 맥락에 정확히 부합합니다.")
        else:
            st.warning("💡 AI 피드백을 참고하여 처리 조건이나 부품 선택을 다시 한번 점검해 보세요.")
