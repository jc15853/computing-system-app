import html
import json

import streamlit as st
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 디자인
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 1. Gemini API 키 가져오기
#
# Streamlit Cloud > 앱 Settings > Secrets:
# GEMINI_API_KEY = "실제_Gemini_API_키"
# -----------------------------------------------------------------------------
def get_api_key():
    """Streamlit Secrets에서 Gemini 키를 읽고, 없으면 사이드바 입력을 사용합니다."""
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        # 로컬에서 secrets.toml 파일이 없는 경우
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
            help="Google AI Studio에서 발급한 Gemini API 키를 입력하세요. 키를 공개하지 마세요.",
        )
    return manual_key.strip() if manual_key else ""


api_key = get_api_key()

st.title("나만의 피지컬 컴퓨팅 시스템 설계하기")

st.info(
    """
    💡 우리 주변의 스마트 기술이 외부 환경을 어떤 **입력 장치**로 감지하고,
    어떤 **조건**에 따라 작동하며, 어떤 **출력 장치**로 결과를 나타내는지
    직접 설계해 봅시다.
    """
)

st.divider()

# -----------------------------------------------------------------------------
# 2. 시스템 선택 및 장치 목록
# -----------------------------------------------------------------------------
st.markdown("### 1️⃣ 시스템")

case_options = {
    "미세먼지 자동 환기 시스템": {
        "title": "미세먼지 자동 환기 시스템",
        "correct_sensor": "미세먼지 센서",
        "correct_output": "환기 팬 (모터)",
        "default_condition": "실내 미세먼지 농도가 기준치(80㎍/㎥) 이상으로 높아지면",
        "system_goal": "실내 미세먼지 수치를 측정하고 기준치 이상일 때 환기팬을 켜는 시스템",
    },
    "주차장 자동 차단기 시스템": {
        "title": "주차장 자동 차단기 시스템",
        "correct_sensor": "카메라 (차량번호 인식)",
        "correct_output": "서보모터 (차단기 바)",
        "default_condition": "진입하는 차량의 번호판을 인식하여 등록된 입주민 차량임이 확인되면",
        "system_goal": "진입 차량의 번호판을 카메라로 인식한 뒤, 등록된 차량인지 판단하여 차단기를 여는 시스템",
    },
    "스마트 가로등 자동 점등 시스템": {
        "title": "스마트 가로등 자동 점등 시스템",
        "correct_sensor": "조도(빛) 센서",
        "correct_output": "가로등 LED 전구",
        "default_condition": "해가 지거나 주변이 어두워져 빛의 양(조도)이 일정 수치 이하로 떨어지면",
        "system_goal": "주변의 밝기(조도)를 측정하여 어두워지면 가로등을 켜는 시스템",
    },
}

fixed_sensors = [
    "미세먼지 센서",
    "온습도 센서",
    "조도(빛) 센서",
    "카메라 (차량번호 인식)",
    "소음 센서",
    "초음파 거리 센서",
    "온도 센서",
    "인체 감지 센서",
]

fixed_outputs = [
    "환기 팬 (모터)",
    "LED 전구",
    "스피커 (경적)",
    "서보모터 (차단기 바)",
    "가로등 LED 전구",
]

selected_case_name = st.selectbox(
    "설계할 시스템을 선택하세요:", list(case_options.keys())
)
selected_case = case_options[selected_case_name]

st.divider()

# -----------------------------------------------------------------------------
# 3. 입력 - 처리 - 출력 설계
# -----------------------------------------------------------------------------
st.markdown("### 2️⃣ 컴퓨팅 시스템 3단계")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📥 입력")
    user_sensor = st.radio(
        "**필요한 입력 장치는 무엇일까요?**",
        fixed_sensors,
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
    user_output = st.radio(
        "**필요한 출력 장치는 무엇일까요?**",
        fixed_outputs,
        key="user_output",
    )

# -----------------------------------------------------------------------------
# 4. Gemini AI 평가
# -----------------------------------------------------------------------------
if st.button(
    "🚀 컴퓨팅 시스템 설계하기",
    type="primary",
    use_container_width=True,
):
    is_sensor_ok = user_sensor == selected_case["correct_sensor"]
    is_output_ok = user_output == selected_case["correct_output"]

    is_condition_ok = False
    ai_feedback = ""
    ai_available = False

    if not api_key:
        st.error(
            "Gemini API 키를 찾을 수 없습니다. Streamlit Cloud의 "
            "Settings → Secrets에 GEMINI_API_KEY를 설정하거나 사이드바에 입력해 주세요."
        )
        ai_feedback = "API 키가 없어 처리 조건의 AI 평가를 진행하지 못했습니다."
    else:
        try:
            with st.spinner("🤖 Gemini AI가 시스템 설계를 분석하고 있습니다..."):
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
- 단순히 입력만 하는 것(예: "번호판을 인식한다")에 그치지 않고,
  시스템이 작동하기 위한 판단/비교/확인 과정이 문장에 논리적으로 포함되어야 합니다.
- 핵심 판단 과정이 빠졌거나 엉뚱한 내용이면 is_valid를 false로,
  목적에 맞는 조건이면 true로 반환하세요.
- 학생에게 친절하고 구체적인 한국어 피드백을 작성하세요.

JSON 객체의 형식:
{{
  "is_valid": true,
  "feedback": "학생에게 줄 친절하고 구체적인 한국어 피드백"
}}
is_valid는 반드시 true 또는 false로 반환하세요.
"""

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "당신은 학생의 피지컬 컴퓨팅 설계를 평가하는 교육 도우미입니다. "
                            "요청한 형식에 맞는 유효한 JSON만 반환하세요."
                        ),
                        response_mime_type="application/json",
                        temperature=0.2,
                    ),
                )

                response_text = response.text
                if not response_text:
                    raise ValueError("Gemini 응답이 비어 있습니다.")

                result = json.loads(response_text)
                if not isinstance(result, dict) or "is_valid" not in result:
                    raise ValueError("Gemini 응답에 필요한 평가 항목이 없습니다.")

                is_condition_ok = result.get("is_valid") is True
                ai_feedback = str(
                    result.get("feedback", "평가 결과에 대한 피드백이 없습니다.")
                )
                ai_available = True

        except json.JSONDecodeError:
            st.error("Gemini 응답을 JSON으로 해석하지 못했습니다. 다시 시도해 주세요.")
            ai_feedback = "AI 응답 형식 문제로 처리 조건을 평가하지 못했습니다."
        except ValueError as e:
            st.error(str(e))
            ai_feedback = "AI 응답을 처리하지 못해 조건 평가를 완료하지 못했습니다."
        except Exception as e:
            # 진단을 위해 예외 종류와 안전한 오류 메시지를 표시합니다.
            # API 키 문자열 자체는 화면에 출력하지 않습니다.
            error_text = str(e)
            lowered = error_text.lower()
            error_type = type(e).__name__

            # 오류 메시지에 API 키가 포함되는 드문 경우를 대비해 마스킹합니다.
            safe_error_text = error_text
            if api_key:
                safe_error_text = safe_error_text.replace(api_key, "[API 키 숨김]")

            status_code = (
                getattr(e, "code", None)
                or getattr(e, "status_code", None)
                or getattr(e, "status", None)
            )

            if any(term in lowered for term in ("api key", "api_key", "unauthenticated", "invalid_argument: api key", "401")):
                st.error(
                    "Gemini API 키 인증 오류입니다. Google AI Studio에서 발급한 키인지, "
                    "Secrets 이름이 GEMINI_API_KEY인지 확인해 주세요."
                )
            elif any(term in lowered for term in ("permission_denied", "permission denied", "403", "leaked", "blocked")):
                st.error(
                    "Gemini API 접근 권한 오류입니다. 키 상태, 프로젝트 접근 권한 및 API 사용 가능 여부를 확인해 주세요."
                )
            elif any(term in lowered for term in ("quota", "resource_exhausted", "429", "rate limit")):
                st.error(
                    "Gemini API 사용 한도 또는 요청 제한 오류입니다. Google AI Studio에서 프로젝트의 사용량과 한도를 확인해 주세요."
                )
            elif any(term in lowered for term in ("not_found", "not found", "404", "model")):
                st.error(
                    "모델을 찾을 수 없거나 해당 모델을 사용할 수 없습니다. 모델 이름과 프로젝트에서 사용 가능한 모델을 확인해 주세요."
                )
            else:
                st.error("Gemini API 호출에 실패했습니다. 아래 진단 정보를 확인해 주세요.")

            st.code(
                f"오류 유형: {error_type}\n"
                f"HTTP/SDK 코드: {status_code if status_code is not None else '오류 메시지에서 확인'}\n"
                f"오류 내용: {safe_error_text[:1200]}",
                language="text",
            )
            ai_feedback = "Gemini API 오류로 처리 조건을 평가하지 못했습니다."

    sensor_badge = "✅ (정확함)" if is_sensor_ok else "❌ (다시 고민해 봅시다)"
    condition_badge = (
        "✅ (적절한 조건)"
        if ai_available and is_condition_ok
        else "⚠️ (조건 검토 필요)"
    )
    output_badge = "✅ (정확함)" if is_output_ok else "❌ (다시 고민해 봅시다)"

    # 사용자 입력을 HTML로 해석하지 않도록 이스케이프합니다.
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

    if is_sensor_ok and is_output_ok and ai_available and is_condition_ok:
        st.balloons()
        st.success(
            "🎉 **완벽한 설계입니다!** 입력, 조건 판단, 출력 장치가 시스템의 목적에 잘 부합합니다."
        )
    else:
        st.warning(
            "💡 AI 피드백을 참고하여 처리 조건이나 부품 선택을 다시 한번 점검해 보세요."
        )
