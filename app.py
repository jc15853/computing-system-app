import os
from pathlib import Path
import pandas as pd
import streamlit as st

# 1. 페이지 및 CSS 설정
st.set_page_config(
    page_title="피지컬 컴퓨팅 시스템 설계 도우미",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
<style>
    .stApp { background-color: #ffffff; color: #1f2937; font-family: 'Pretendard', sans-serif; }
    h1, h2, h3, h4 { color: #1e3a8a !important; font-weight: bold !important; }
    .report-card {
        background-color: #f8fafc;
        border: 2px solid #2563eb;
        border-radius: 12px;
        padding: 24px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .step-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #2563eb;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Session State 초기화 (페이지 전환 및 결과 데이터 저장)
if "page" not in st.session_state:
  st.session_state.page = "input"  # 'input' 또는 'result'
if "result_data" not in st.session_state:
  st.session_state.result_data = None

# 2. 데이터 로드 (경로 의존성 방지 & 방어적 로딩)
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "physical_computing_data.csv"


@st.cache_data
def load_data(file_path: Path):
  if not file_path.exists():
    st.error(f"❌ 데이터 파일('{file_path.name}')을 찾을 수 없습니다.")
    return None, None

  import csv

  rows = []
  encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

  for enc in encodings:
    try:
      with open(file_path, "r", encoding=enc, errors="replace") as f:
        reader = csv.reader(f)
        rows = [row for row in reader if row]
      if rows:
        break
    except Exception:
      continue

  if not rows:
    st.error("❌ CSV 데이터를 읽을 수 없습니다.")
    return None, None

  expected_cols = [
      "record_type",
      "name",
      "category",
      "description",
      "system_goal",
      "default_condition",
      "recommended_inputs",
      "recommended_outputs",
      "keywords",
  ]

  data_rows = rows[1:] if rows[0][0].lower().startswith("record_type") else rows
  parsed_data = []

  for r in data_rows:
    if not r or len(r) < 2:
      continue
    if len(r) < len(expected_cols):
      r += [""] * (len(expected_cols) - len(r))
    else:
      r = r[: len(expected_cols)]
    parsed_data.append(r)

  df = pd.DataFrame(parsed_data, columns=expected_cols)
  df["record_type"] = df["record_type"].str.lower().str.strip()

  devices = df[df["record_type"] == "device"]
  systems = df[df["record_type"] == "system"]

  return devices, systems


devices_df, systems_df = load_data(CSV_PATH)

# 3. 사이드바 - Gemini API 키 설정
st.sidebar.title("⚙️ 설정")
api_key = st.secrets.get("GEMINI_API_KEY", "") or st.secrets.get(
    "GOOGLE_API_KEY", ""
)

if not api_key:
  user_key = st.sidebar.text_input(
      "Gemini API Key 입력",
      type="password",
      help="Google AI Studio에서 발급받은 API 키를 입력하세요.",
  )
  if user_key:
    api_key = user_key.strip()

st.sidebar.info(
    "💡 **안내**: CSV 파일 기반으로 장치 및 시스템 사례를 동적으로 로드합니다."
)

# -----------------------------------------------------------------------------
# [화면 1] 설계 입력 화면
# -----------------------------------------------------------------------------
if st.session_state.page == "input":
  st.title("🔌 나만의 피지컬 컴퓨팅 시스템 설계 도우미")
  st.markdown(
      "입력 장치, 처리 조건, 출력 장치를 조합하여 물리 컴퓨팅 시스템을 설계해"
      " 보세요."
  )
  st.divider()

  if devices_df is not None and systems_df is not None:
    input_devices = (
        devices_df[devices_df["category"].str.contains("입력", na=False)][
            "name"
        ].tolist()
    )
    output_devices = (
        devices_df[devices_df["category"].str.contains("출력", na=False)][
            "name"
        ].tolist()
    )

    system_options = {"직접 설계 (자유 구성)": None}
    for _, row in systems_df.iterrows():
      system_options[row["name"]] = row

    st.markdown("### 1️⃣ 시스템 사례 선택")
    selected_sys_name = st.selectbox(
        "설계할 시스템 사례를 선택하세요:", list(system_options.keys())
    )

    selected_sys = system_options[selected_sys_name]

    default_cond = ""
    default_in = input_devices[0] if input_devices else ""
    default_out = output_devices[0] if output_devices else ""
    sys_goal = ""

    if selected_sys is not None:
      default_cond = selected_sys.get("default_condition", "")
      sys_goal = selected_sys.get(
          "system_goal", selected_sys.get("description", "")
      )
      rec_in = [
          x.strip()
          for x in str(selected_sys.get("recommended_inputs", "")).split(";")
          if x.strip()
      ]
      rec_out = [
          x.strip()
          for x in str(selected_sys.get("recommended_outputs", "")).split(";")
          if x.strip()
      ]

      if rec_in and rec_in[0] in input_devices:
        default_in = rec_in[0]
      if rec_out and rec_out[0] in output_devices:
        default_out = rec_out[0]

    st.divider()

    st.markdown("### 2️⃣ 컴퓨팅 시스템 3단계 설계")
    col1, col2, col3 = st.columns(3)

    with col1:
      st.markdown("#### 📥 입력 장치")
      user_input = st.selectbox(
          "입력 장치 선택",
          input_devices,
          index=(
              input_devices.index(default_in)
              if default_in in input_devices
              else 0
          ),
      )

    with col2:
      st.markdown("#### ⚙️ 처리 조건")
      user_cond = st.text_area(
          "작동 조건 입력",
          value=default_cond,
          height=120,
          key=f"cond_{selected_sys_name}",
      )

    with col3:
      st.markdown("#### 📤 출력 장치")
      user_output = st.selectbox(
          "출력 장치 선택",
          output_devices,
          index=(
              output_devices.index(default_out)
              if default_out in output_devices
              else 0
          ),
      )

    # 설계하기 버튼 클릭 시 -> AI 진단 후 결과 저장 및 결과 화면 이동
    if st.button(
        "🚀 컴퓨팅 시스템 설계 및 AI 검증하기",
        type="primary",
        use_container_width=True,
    ):
      ai_feedback = ""
      is_valid = False
      ai_success = False

      if not api_key:
        ai_feedback = "API 키가 입력되지 않아 AI 검증을 스킵합니다."
      else:
        with st.spinner("🤖 Gemini AI가 시스템 설계를 진단 중입니다..."):
          try:
            import json
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = f"""
당신은 초·중등 정보 교육 피지컬 컴퓨팅 평가 전문가입니다.
학생이 설계한 시스템을 보고 논리성을 평가하세요.

[설계 정보]
- 시스템 명칭: {selected_sys_name}
- 목표: {sys_goal if sys_goal else "사용자 정의 목표"}
- 선택 입력 장치: {user_input}
- 작성 조건: {user_cond}
- 선택 출력 장치: {user_output}

[평가 기준]
1. 작성한 조건이 시스템 목적에 맞게 판단/비교/확인 로직을 포함하는가?
2. 선택한 입력/출력 장치가 조건과 목적에 적절히 부합하는가?

반드시 JSON 객체 형식으로만 응답하세요:
{{"is_valid": true/false, "feedback": "학생에게 전달할 친절한 한국어 피드백"}}
"""
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            res_json = json.loads(response.text)
            is_valid = res_json.get("is_valid", False)
            ai_feedback = res_json.get(
                "feedback", "피드백을 생성하지 못했습니다."
            )
            ai_success = True
          except Exception as e:
            ai_feedback = f"API 연동 중 오류 발생: {e}"

      # 결과를 세션에 저장하고 페이지를 'result'로 전환
      st.session_state.result_data = {
          "sys_name": selected_sys_name,
          "user_input": user_input,
          "user_cond": user_cond,
          "user_output": user_output,
          "ai_feedback": ai_feedback,
          "is_valid": is_valid,
          "ai_success": ai_success,
          "has_api_key": bool(api_key),
      }
      st.session_state.page = "result"
      st.rerun()

  else:
    st.error("데이터 로드 실패로 앱을 정상 동작할 수 없습니다.")

# -----------------------------------------------------------------------------
# [화면 2] 설계 결과 화면
# -----------------------------------------------------------------------------
elif st.session_state.page == "result":
  st.title("📋 시스템 설계 분석 및 진단 결과")
  st.divider()

  res = st.session_state.result_data
  if res:
    badge_status = (
        "✅ (적절함)"
        if (res["ai_success"] and res["is_valid"])
        else "⚠️ (검토 필요)"
    )

    st.markdown(
        f"""
        <div class="report-card">
            <h3>📌 [ 설계 시스템: {res['sys_name']} ]</h3>
            <ul>
                <li><b>📥 입력 장치:</b> {res['user_input']}</li>
                <li><b>⚙️ 처리 조건:</b> {res['user_cond']} {badge_status if res['has_api_key'] else ''}</li>
                <li><b>📤 출력 장치:</b> {res['user_output']}</li>
            </ul>
            <p style="font-size: 1.05em; margin-top: 15px;">💡 <b>AI 진단 피드백:</b><br>{res['ai_feedback']}</p>
            <hr style="margin: 20px 0;">
            <h4>🔄 3단계 작동 매커니즘</h4>
            <div class="step-box"><b>[1. 입력]:</b> <code>{res['user_input']}</code>(으)로 외부 물리적 신호나 데이터를 감지 및 수집합니다.</div>
            <div class="step-box"><b>[2. 처리]:</b> <i>"{res['user_cond']}"</i> 조건에 해당하는지 판단 연산을 수행합니다.</div>
            <div class="step-box"><b>[3. 출력]:</b> 판단 결과에 따라 <code>{res['user_output']}</code>(을)를 제어하여 작동시킵니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if res["ai_success"] and res["is_valid"]:
      st.balloons()
      st.success(
          "🎉 축하합니다! 논리적으로 완벽한 피지컬 컴퓨팅 시스템 설계입니다."
      )
    elif res["has_api_key"] and not res["is_valid"]:
      st.warning(
          "💡 AI 피드백을 참고하여 작성 조건을 조금 더 명확하게 수정해 보세요."
      )

  st.divider()

  # 다시 설계하기 버튼 -> 첫 화면으로 전환
  if st.button("🔄 다시 설계하기", type="primary", use_container_width=True):
    st.session_state.page = "input"
    st.session_state.result_data = None
    st.rerun()
