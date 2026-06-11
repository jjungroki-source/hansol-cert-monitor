import streamlit as st
from datetime import date
from openai import OpenAI

st.set_page_config(
    page_title="한솔제지 천안공장 인증 모니터링",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global Apple-style CSS ────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif !important;
}
.stApp { background-color: #F5F5F7 !important; }
[data-testid="stSidebar"] > div:first-child {
    background-color: #FFFFFF !important;
    border-right: 1px solid #D2D2D7 !important;
}
h1 {
    color: #1D1D1F !important; font-weight: 700 !important;
    letter-spacing: -0.4px !important; font-size: 26px !important;
}
h2, h3 { color: #1D1D1F !important; font-weight: 600 !important; }
h4, h5 { color: #1D1D1F !important; }
hr { border-color: #D2D2D7 !important; opacity: 0.8; }
[data-testid="stExpander"] {
    border: 1px solid #D2D2D7 !important;
    border-radius: 14px !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
.stProgress > div > div { border-radius: 6px !important; height: 8px !important; }
div[data-testid="stAlert"] { border-radius: 12px !important; }
.stCaption { color: #6E6E73 !important; }
</style>
""", unsafe_allow_html=True)

# ── 챗봇 시스템 프롬프트 ──────────────────────────────────────
SYSTEM_PROMPT = """
당신은 한솔제지 천안공장 품질환경팀의 인증 전문 AI 어시스턴트 ROKI입니다.
ROKI는 "Recognition & Certification Knowledge Intelligence"의 약자입니다.
아래에 제공된 인증 팩트 정보를 바탕으로 질문에 답변하세요.

[답변 원칙]
- 아래 팩트에 명시된 내용만 답변합니다.
- 팩트에 없는 내용은 "해당 내용은 제가 보유한 정보에 없습니다. 담당자에게 직접 문의해 주세요."라고 답변합니다.
- 추정하거나 상상해서 답변하지 않습니다.
- 답변은 한국어로 하며, 간결하고 명확하게 작성합니다.
- 자기소개 시 "안녕하세요, 저는 ROKI입니다. 한솔제지 천안공장의 인증 전문 AI 어시스턴트입니다."라고 답변합니다.

[인증 팩트 정보]

## FSC CoC 인증
- FSC: Forest Stewardship Council(산림관리협의회)
- CoC: Chain of Custody(공급망 관리)
- 목적: 지속 가능한 방식으로 관리된 산림에서 생산된 목재·종이 제품임을 보증
- 발급기관: FSC International / 심사기관: SGS Korea 등 FSC 인정 CB
- 갱신심사: 5년 주기 / 사후심사: 연 1회
- 천안공장 인증번호: FSC-C012345
- 인증 기간: 2026-06-16 ~ 2031-06-15
- 마지막 심사: 2026-02-11 (갱신심사)
- 다음 사후심사: 2027-02-11
- 조회: info.fsc.org
- 심사 준비 서류 22종: FSC COC 매뉴얼, 연간실적 요약서, 인증원료 공급사 목록, 공급사 인증유효성 증명,
  펄프원료 수종 정보(학명), 재활용 종이 원료 공급사 목록, COC 교육훈련 기록, 산업안전보건 기록,
  상표사용 승인 이메일, 홍보물 샘플, 구매/생산/판매 서류, 외주업무협약서, 자기선언서,
  인증제품군별 전환계수 증빙, 크레딧 계정, 핵심노동요구사항 방침선언서, 자체평가서(GP4521B),
  HR/생산직 직원 협조 안내, 근로자 관련 서류(취업규칙·교육기록·명부·근로계약서),
  매출액 자기선언서(GP4523), 부적합 시정조치 증빙, 인증갱신 필수서류(eTLA·사업자등록증)

## 환경표지인증 (EL)
- EL: Environmental Label / 발급기관: 한국환경산업기술원(KEITI), 환경부 산하
- 목적: 생산·유통·사용·폐기 전 과정에서 환경 영향이 가장 적은 제품에 부여
- 인증 단위: 제품별(모델 단위) / 유효기간: 3년 / 사후관리: 연 1회
- 갱신 신청 권장: 만료 90일 전
- 효과: 공공기관 녹색제품 의무구매 등재, 조달청 우선구매·입찰 가점
- 조회/신청: el.keiti.re.kr
- 천안공장 관리 제품(5건): 인쇄용지(그린페이퍼 A4), 화장지(에코티슈 3겹),
  골판지(친환경박스 B형), 복사용지(에코복사지 80g), 포장재(재활용포장박스)

## ISO 9001
- 품질경영시스템(QMS) / 발급: ISO 인정 CB / 국내 인정기관: KAB
- 목적: 제품·서비스의 일관된 품질 보증 및 고객 만족
- 유효기간: 3년 / 사후심사: 연 1회(1·2차) / 갱신: 3년 후
- 인증번호: QMS-2022-00123 / 기간: 2022-09-01 ~ 2025-08-31
- 마지막 심사: 2024-09-05(사후1차) / 다음 심사: 2025-09-01(사후2차)
- 범위: 인쇄용지, 복사용지, 특수지 제조 및 품질관리

## ISO 14001
- 환경경영시스템(EMS) / 발급: ISO 인정 CB / 국내 인정기관: KAB
- 목적: 환경 영향 최소화, 탄소 저감·폐기물 관리·에너지 효율화
- 유효기간: 3년 / 사후심사: 연 1회(1·2차) / 갱신: 3년 후
- 인증번호: EMS-2023-00456 / 기간: 2023-03-15 ~ 2026-03-14
- 마지막 심사: 2024-03-20(사후1차) / 다음 심사: 2025-03-15(사후2차)
- 범위: 천안공장 제지 생산 전 공정의 환경경영 활동

## Vegan 인증 - 한국비건인증원(KV)
- 목적: 동물 유래 성분 미사용·동물 실험 미수행 검증 / 유효기간: 1년
- 인증번호: KV-2024-00789 / 기간: 2024-05-01 ~ 2025-04-30
- 범위: 친환경 복사용지, 포장박스

## Vegan 인증 - The Vegan Society(영국)
- 1944년 설립 세계 최초 비건 단체, Vegan Trademark 운영
- 유효기간: 2년 / 인증번호: TVS-2023-EU456 / 기간: 2023-08-15 ~ 2025-08-14
- 범위: 수출용 친환경 인쇄용지(유럽 바이어 대응)

## 담당자
- 소속: 한솔제지(주) 천안공장 품질환경팀 품질관리
- 담당자: 장정록 책임 / 이메일: jjr@hansol.com / 전화: 041-000-0000
"""

# ── 팝업 다이얼로그 ───────────────────────────────────────────
@st.dialog("💬 무엇이든 물어보세요", width="large")
def contact_dialog():
    tab_contact, tab_chat = st.tabs(["📋 담당자 연락처", "✦ ROKI"])

    # ── 탭1: 연락처 ────────────────────────────────────────
    with tab_contact:
        st.html("""
            <div style="padding:8px 0;">
                <div style="font-size:13px;color:#8E8E93;text-transform:uppercase;
                            letter-spacing:0.5px;margin-bottom:14px;">품질환경팀 품질관리</div>
                <div style="background:#F5F5F7;border-radius:14px;padding:16px 20px;margin-bottom:8px;">
                    <div style="font-size:12px;color:#8E8E93;text-transform:uppercase;
                                letter-spacing:0.4px;margin-bottom:4px;">담당자</div>
                    <div style="font-size:16px;font-weight:700;color:#1D1D1F;">장정록 책임</div>
                </div>
                <div style="background:#F5F5F7;border-radius:14px;padding:16px 20px;margin-bottom:8px;">
                    <div style="font-size:12px;color:#8E8E93;text-transform:uppercase;
                                letter-spacing:0.4px;margin-bottom:4px;">이메일</div>
                    <div style="font-size:15px;font-weight:600;color:#007AFF;">jjr@hansol.com</div>
                </div>
                <div style="background:#F5F5F7;border-radius:14px;padding:16px 20px;">
                    <div style="font-size:12px;color:#8E8E93;text-transform:uppercase;
                                letter-spacing:0.4px;margin-bottom:4px;">전화번호</div>
                    <div style="font-size:15px;font-weight:600;color:#34C759;">041-000-0000</div>
                </div>
            </div>
        """)

    # ── 탭2: ROKI 챗봇 ─────────────────────────────────────
    with tab_chat:
        # API 키 미입력 시
        api_key = st.session_state.get("openai_api_key", "")
        if not api_key:
            st.html("""
                <div style="text-align:center;padding:28px 0 16px;">
                    <div style="font-size:44px;font-weight:800;
                                background:linear-gradient(135deg,#007AFF,#AF52DE,#34C759);
                                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                                background-clip:text;letter-spacing:-2px;margin-bottom:6px;">ROKI</div>
                    <div style="font-size:12px;color:#8E8E93;letter-spacing:0.3px;">
                        Recognition &amp; Certification Knowledge Intelligence
                    </div>
                </div>
            """)
            new_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                help="키는 세션에만 임시 저장되며 서버에 보관되지 않습니다.",
            )
            if new_key:
                st.session_state["openai_api_key"] = new_key
                st.rerun()
            st.caption("API 키를 입력하면 ROKI를 바로 사용할 수 있습니다.")
            st.stop()

        # 대화 히스토리 초기화
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = []

        # 대화 영역
        chat_area = st.container(height=330)
        with chat_area:
            if not st.session_state["chat_messages"]:
                st.html("""
                    <div style="text-align:center;padding:32px 0 24px;">
                        <div style="font-size:40px;font-weight:800;
                                    background:linear-gradient(135deg,#007AFF,#AF52DE,#34C759);
                                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                                    background-clip:text;letter-spacing:-2px;margin-bottom:8px;">ROKI</div>
                        <div style="font-size:13px;font-weight:600;color:#1D1D1F;margin-bottom:4px;">
                            인증 전문 AI 어시스턴트
                        </div>
                        <div style="font-size:12px;color:#8E8E93;line-height:1.7;">
                            FSC · 환경표지인증 · ISO · Vegan<br>인증에 대해 무엇이든 물어보세요
                        </div>
                        <div style="display:flex;justify-content:center;gap:8px;
                                    flex-wrap:wrap;margin-top:16px;">
                            <span style="background:#F5F5F7;border:1px solid #D2D2D7;border-radius:20px;
                                         padding:5px 13px;font-size:13px;color:#3D3D3D;">FSC 심사일은?</span>
                            <span style="background:#F5F5F7;border:1px solid #D2D2D7;border-radius:20px;
                                         padding:5px 13px;font-size:13px;color:#3D3D3D;">EL 갱신 서류?</span>
                            <span style="background:#F5F5F7;border:1px solid #D2D2D7;border-radius:20px;
                                         padding:5px 13px;font-size:13px;color:#3D3D3D;">ISO 14001이란?</span>
                        </div>
                    </div>
                """)
            for msg in st.session_state["chat_messages"][-12:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # 입력 폼
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_btn = st.columns([8, 1])
            user_input = col_input.text_input(
                "질문 입력",
                placeholder="ROKI에게 인증 관련 질문을 입력하세요...",
                label_visibility="collapsed",
            )
            submitted = col_btn.form_submit_button("↑", use_container_width=True)

        col_clear, _ = st.columns([2, 8])
        if col_clear.button("대화 초기화", key="clear_chat"):
            st.session_state["chat_messages"] = []
            st.rerun()

        # GPT 호출
        if submitted and user_input.strip():
            st.session_state["chat_messages"].append(
                {"role": "user", "content": user_input.strip()}
            )

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state["chat_messages"][-10:]:
                messages.append({"role": m["role"], "content": m["content"]})

            try:
                client = OpenAI(api_key=st.session_state["openai_api_key"])
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0,
                    max_tokens=800,
                )
                answer = response.choices[0].message.content
            except Exception as e:
                err = str(e)
                if "invalid_api_key" in err or "Incorrect API key" in err:
                    answer = "❌ API 키가 올바르지 않습니다. 키를 다시 확인해 주세요."
                elif "quota" in err.lower() or "billing" in err.lower():
                    answer = "❌ API 사용 한도 초과 또는 결제 정보 필요. OpenAI 계정을 확인해 주세요."
                else:
                    answer = f"❌ 오류: {err}"

            st.session_state["chat_messages"].append(
                {"role": "assistant", "content": answer}
            )
            st.rerun()

# ── 사이드바 헤더 ─────────────────────────────────────────────
with st.sidebar:
    st.html(
        """
        <div style="padding:12px 0 16px 0;">
            <div style="font-size:13px;color:#8E8E93;letter-spacing:0.6px;text-transform:uppercase;margin-bottom:8px;">
                품질환경팀 품질관리
            </div>
            <div style="font-size:17px;font-weight:700;color:#1D1D1F;line-height:1.3;letter-spacing:-0.3px;">
                한솔제지(주) 천안공장
            </div>
            <div style="font-size:13px;color:#6E6E73;margin-top:4px;">
                담당자 · 장정록 책임
            </div>
            <div style="font-size:13px;color:#8E8E93;margin-top:10px;padding-top:10px;border-top:1px solid #E8E8ED;">
                기준일 · {today}
            </div>
        </div>
        """.format(today=date.today().strftime("%Y년 %m월 %d일")),
    )

    st.html(
        """
        <style>
        div[data-testid="stButton"] button[kind="secondary"] {
            background: #F2F2F7;
            border: 1px solid #D2D2D7;
            color: #1D1D1F;
            font-size: 13px;
            font-weight: 500;
            border-radius: 10px;
            padding: 8px 12px;
            width: 100%;
            text-align: center;
            letter-spacing: 0.1px;
        }
        div[data-testid="stButton"] button[kind="secondary"]:hover {
            background: #E5E5EA;
            border-color: #C5C5CA;
        }
        </style>
        """,
    )
    if st.button("💬 무엇이든 물어보세요", use_container_width=True):
        contact_dialog()

    st.html('<hr style="border:none;border-top:1px solid #D2D2D7;margin:10px 0;"/>')

# ── 페이지 네비게이션 ─────────────────────────────────────────
pg = st.navigation(
    [
        st.Page("pages/summary.py",    title="Summary",        icon="📊"),
        st.Page("pages/fsc.py",        title="1. FSC 인증",    icon="🌲"),
        st.Page("pages/el.py",         title="2. 환경표지인증", icon="♻️"),
        st.Page("pages/iso.py",        title="3. ISO",          icon="📋"),
        st.Page("pages/vegan.py",      title="4. Vegan 인증",   icon="🌱"),
        st.Page("pages/etc.py",        title="5. 기타",         icon="📁"),
        st.Page("pages/email_mgmt.py", title="6. 알림 관리",    icon="📧"),
    ]
)
pg.run()
