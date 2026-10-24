import os
from pathlib import Path
import pandas as pd
import streamlit as st

# 페이지 설정 및 디자인
st.set_page_config(
    page_title="피지컬 컴퓨팅 시스템 설계기",
    page_icon="🤖",
    layout="centered",
)

custom_css = """
<style>
    .stApp {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        font-family: 'Pretendard', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #1e3a8a !important;
        font-weight: bold !important;
    }
    p, span, label, div {
        color: #1f2937;
    }
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

# 파일 경로 설정
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "physical_computing_data.csv"

@st.cache_data
def load_computing_data(file_path: Path):
    """CSV 파일에서 장치 및 시스템 사례 데이터를 안전하게 로드합니다."""
    if not file_path.exists():
        st.error(f"오류: '{file_path.name}' 파일을 찾을 수 없습니다.")
        return None
    
    # 인코딩 순차 시도 (utf-8-sig 우선)
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except Exception:
            continue
            
    if df is None:
        # 마지막 수단으로 에러 무시/대체 옵션 적용
        try:
            df = pd.read_csv(file_path, encoding="utf-8", errors="replace")
        except Exception as e:
            st.error(f"CSV 파일 로드 중 오류가 발생했습니다: {e}")
            return None

    required_columns = ["record_type", "name", "category", "description"]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"CSV 파일에 필수 열이 누락되었습니다: {missing_cols}")
        return None

    return df.fillna("")

df_data = load_computing_data(CSV_PATH)

# API 키 가져오기
def get_api_key():
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
        if not secret_key:
            secret_key = st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        secret_key = ""

    if isinstance(secret_key, str):
        secret_key = secret_key.strip()

    if secret_key:
        return secret_key

    with st.sidebar:
        st.subheader("⚙️ 설정")
        manual_key = st.text_input(
            "Gemini API Key를 입력하세요",
            type="password",
            help="Google AI Studio에서 발급받은 API 키를 입력하세요.",
        )
    return manual_key.strip() if manual_key else ""

api_key = get_api_key()

st.title("나만의 피지컬 컴퓨팅 시스템 설계하기")
st.info(
    """
    💡 우리 주변의 스마트 기술이 외부 환경을 어떤 **입력 장치**로 감지하고,
    어떤 **조건**에 따라 작동하며, 어떤 **출력 장치**로 결과를 나타내는지
    CSV 데이터를 기반으로 직접 설계해 봅시다.
    """
)
st.divider()

if df_data is not None:
    devices_df = df_data[df_data["record_type"].str.lower() == "device"]
    systems_df = df_data[df_data["record_type"].str.lower() == "system"]

    input_devices = devices_df[devices_df["category"].str.contains("입력", case=False)]["name"].dropna().tolist()
    output_devices = devices_df[devices_df["category"].str.contains("출력", case=False)]["name"].dropna().tolist()

    # 시스템 사례 동적 구성
    system_options = {}
    for _, row in systems_df.iterrows():
        sys_name = row["name"]
        system_options[sys_name] = {
            "title": sys_name,
            "recommended_inputs": [x.strip() for x in str(row.get("recommended_inputs", "")).split(";") if x.strip()],
            "recommended_outputs": [x.strip() for x in str(row.get("recommended_outputs", "")).split(";") if x.strip()],
            "default_condition": row.get("default_condition", ""),
            "system_goal": row.get("system_goal", row.get("description", "")),
        }

    st.markdown("### 1️⃣ 시스템 선택")
    if system_options:
        selected_case_name = st.selectbox("설계할 시스템을 선택하세요:", list(system_options.keys()))
        selected_case = system_options[selected_case_name]
    else:
        st.warning("CSV에 등록된 시스템 사례가 없습니다.")
        selected_case_name = "사용자 정의 시스템"
        selected_case = {
            "title": "사용자 정의 시스템",
            "recommended_inputs": input_devices[:1] if input_devices else [],
            "recommended_outputs": output_devices[:1] if output_devices else [],
            "default_condition": "센서 값이 기준치를 초과하면",
            "system_goal": "원하는 물리 컴퓨팅 시스템을 자유롭게 설계합니다.",
        }

    st.divider()

    st.markdown("### 2️⃣ 컴퓨팅 시스템 3단계")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📥 입력")
        user_sensor = st.selectbox(
            "**필요한 입력 장치는 무엇일까요?**",
            input_devices if input_devices else ["입력 장치 없음"],
            key="user_sensor",
        )

    with col2:
        st.markdown("#### ⚙️ 처리")
        user_condition = st.text_area(
            "**어떤 조건일 때 작동할까요?**",
            value=selected_case["default_condition"],
            height=120,
            key=f"condition_{selected_case_name}",
        )

    with col3:
        st.markdown("#### 📤 출력")
        user_output = st.selectbox(
            "**필요한 출력 장치는 무엇일까요?**",
            output_devices if output_devices else ["출력 장치 없음"],
            key="user_output",
        )

    if st.button("🚀 컴퓨팅 시스템 설계하기", type="primary", use_container_width=True):
        ai_feedback = ""
        ai_available = False

        if not api_key:
            st.error("Gemini API 키를 찾을 수 없습니다. Streamlit Secrets에 GEMINI_API_KEY를 설정하거나 사이드바에 입력해 주세요.")
            ai_feedback = "API 키가 없어 처리 조건의 AI 평가를 진행하지 못했습니다."
        else:
            try:
                with st.spinner("🤖 AI가 시스템 설계를 분석하고 있습니다..."):
                    from google import genai
                    from google.genai import types

                    client = genai.Client(api_key=api_key)

                    prompt = f"""
당신은 초·중등 정보 교육 피지컬 컴퓨팅 시스템 평가 AI입니다.
학생이 선택한 시스템과 작성한 처리 조건을 보고, 조건이 시스템의 목적에 논리적으로 부합하는지 평가하세요.

[시스템 정보]
- 시스템 이름: {selected_case_name}
- 시스템 핵심 목표: {selected_case['system_goal']}

[학생이 작성한 처리 조건]
"{user_condition}"

[평가 기준]
- 단순히 입력만 하는 것에 그치지 않고, 시스템이 작동하기 위한 판단/비교/확인 과정이 문장에 논리적으로 포함되어야 합니다.
- 핵심 판단 과정이 빠졌거나 엉뚱한 내용이면 is_valid를 false로, 목적에 맞는 조건이면 true로 반환하세요.
- 학생에게 친절하고 구체적인 한국어 피드백을 작성하세요.

반드시 JSON 형식으로만 답하세요: {{"is_valid": true, "feedback": "피드백"}}
"""
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.2,
                        ),
                    )
                    
                    import json
                    result = json.loads(response.text)
                    is_condition_ok = result.get("is_valid") is True
                    ai_feedback = str(result.get("feedback", "평가 결과에 대한 피드백이 없습니다."))
                    ai_available = True

            except Exception as e:
                st.error(f"Gemini API 호출 중 오류가 발생했습니다: {e}")
                ai_feedback = "API 호출 오류로 처리 조건을 평가하지 못했습니다."

        sensor_badge = "✅ (선택 완료)"
        condition_badge = "✅ (적절한 조건)" if ai_available and locals().get('is_condition_ok', False) else "⚠️ (조건 검토 필요)"
        output_badge = "✅ (선택 완료)"

        import html
        safe_case_name = html.escape(selected_case_name)
        safe_sensor = html.escape(user_sensor)
        safe_condition = html.escape(user_condition)
        safe_output = html.escape(user_output)
        safe_feedback = html.escape(ai_feedback)

        report_html = f"""
        <div class="report-card">
            <h3 style="margin-top:0; color: #1e3a8a;">[ 선택한 사례: {safe_case_name} ]</h3>
            <p><strong>시스템 구성 부품 및 AI 검증 결과:</strong></p>
            <ul>
                <li><strong>입력 장치:</strong> {safe_sensor} {sensor_badge}</li>
                <li><strong>처리 조건:</strong> {condition_badge}<br>
                    <small style="color: #4b5563;">💡 AI 피드백: {safe_feedback}</small>
                </li>
                <li><strong>출력 장치:</strong> {safe_output} {output_badge}</li>
            </ul>
            <hr style="border-color: #cbd5e1; margin: 15px 0;">
            <p><strong>(3) 컴퓨팅 시스템 3단계 작동 과정 서술:</strong></p>
            <div class="step-box">
                <strong>📥 [입력]:</strong> {safe_sensor}(으)로 외부의 물리적 변화나 데이터(신호)를 감지하여
                컴퓨팅 시스템이 이해할 수 있는 형태로 받아들인다.
            </div>
            <div class="step-box">
                <strong>⚙️ [처리]:</strong> 입력받은 데이터를 분석하여
                <i>"{safe_condition}"</i> 조건에 해당하는지 연산 및 판단한다.
            </div>
            <div class="step-box">
                <strong>📤 [출력]:</strong> 판단 결과에 따라 {safe_output}(을)를 작동시켜 정해진 동작을 실행한다.
            </div>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)
        st.balloons()
        st.success("🎉 **설계가 완료되었습니다!** 입력, 조건 판단, 출력 장치가 시스템의 목적에 잘 부합하는지 확인해 보세요.")
else:
    st.error("CSV 데이터를 로드할 수 없습니다.")
