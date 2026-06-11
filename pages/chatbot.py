import streamlit as st
from openai import OpenAI

# ── 시스템 프롬프트 ────────────────────────────────────────
SYSTEM_PROMPT = """
당신은 한솔제지 천안공장 품질환경팀의 인증 전문 어시스턴트입니다.
아래에 제공된 인증 팩트 정보를 바탕으로 질문에 답변하세요.

[답변 원칙]
- 아래 팩트에 명시된 내용만 답변합니다.
- 팩트에 없는 내용은 "해당 내용은 제가 보유한 정보에 없습니다. 담당자에게 직접 문의해 주세요."라고 답변합니다.
- 추정하거나 상상해서 답변하지 않습니다.
- 답변은 한국어로 하며, 간결하고 명확하게 작성합니다.
- 인증번호, 날짜 등 구체적인 수치를 언급할 때는 팩트에 있는 내용만 인용합니다.

---

[인증 팩트 정보]

## FSC CoC 인증
- FSC: Forest Stewardship Council(산림관리협의회)의 약자
- CoC: Chain of Custody(공급망 관리)의 약자
- 목적: 지속 가능한 방식으로 관리된 산림에서 생산된 목재·종이 제품임을 보증
- CoC 인증은 인증 원료가 산림에서 최종 제품까지 공급망 전 과정에서 적절히 관리·추적됨을 증명
- 발급기관: FSC International
- 심사기관(CB): SGS Korea 등 FSC 인정 제3자 심사기관
- 인증 주기: 갱신심사 5년, 사후심사 연 1회
- 천안공장 인증번호: FSC-C012345
- 인증 범위: FSC Chain of Custody
- 현재 인증 기간: 2026-06-16 ~ 2031-06-15
- 마지막 심사: 2026-02-11 (갱신심사)
- 다음 사후심사 예정: 2027-02-11
- 공식 조회 사이트: info.fsc.org (인증 유효성 조회 및 공급사 확인 가능)
- 심사 준비 서류: FSC COC 매뉴얼, 연간실적 요약서, 인증원료 공급사 목록, 공급사 인증유효성 증명,
  펄프원료 수종 정보(학명), 재활용 종이 원료 공급사 목록, COC 교육훈련 기록, 산업안전보건 기록,
  상표사용 승인 이메일, 홍보물 샘플, 구매/생산/판매 서류, 외주업무협약서, 자기선언서,
  인증제품군별 전환계수 증빙, 크레딧 계정, 핵심노동요구사항 방침선언서, 자체평가서(GP4521B),
  HR/생산직 직원 협조 안내, 근로자 관련 서류(취업규칙·교육기록·명부·근로계약서),
  매출액 자기선언서(GP4523), 부적합 시정조치 증빙, 인증갱신 필수서류(eTLA·사업자등록증)

## 환경표지인증 (EL)
- EL: Environmental Label(환경표지)의 약자
- 발급기관: 한국환경산업기술원(KEITI), 환경부 산하 기관
- 법적 근거: 환경기술 및 환경산업 지원법
- 목적: 같은 용도 제품 중 생산·유통·사용·폐기 전 과정에서 환경 영향이 가장 적은 제품에 부여
- 인증 단위: 제품별(모델 단위)
- 인증 유효기간: 3년
- 사후관리: 연 1회 KEITI 현장심사
- 갱신 신청 권장 시기: 만료 90일 전
- 취득 효과: 공공기관 녹색제품 의무구매 대상 등재, 조달청 우선구매·입찰 가점
- 공식 신청/조회 사이트: el.keiti.re.kr
- D-90 주의: 갱신 준비 시작 (서류 점검, 시험성적서 유효기간 확인)
- D-30 경고: 갱신 신청 접수 마감 임박
- D-7 위험: 즉시 KEITI 담당자 연락 필요
- 천안공장 관리 제품 현황: 인쇄용지(그린페이퍼 A4), 화장지(에코티슈 3겹), 골판지(친환경박스 B형),
  복사용지(에코복사지 80g), 포장재(재활용포장박스) 총 5건

## ISO 9001 인증
- 정식 명칭: ISO 9001 품질경영시스템(Quality Management System)
- 발급기관: ISO(국제표준화기구) 인정 제3자 심사기관(CB)
- 국내 인정기관: KAB(한국인정지원센터)
- 목적: 제품·서비스의 일관된 품질 보증 체계 구축 및 고객 만족 향상
- 인증 유효기간: 3년
- 사후심사: 연 1회 (1차, 2차)
- 갱신심사: 3년 후 재심사
- 천안공장 인증번호: QMS-2022-00123
- 인증 기간: 2022-09-01 ~ 2025-08-31
- 마지막 심사: 2024-09-05 (사후심사 1차)
- 다음 심사: 2025-09-01 (사후심사 2차)
- 인증 범위: 인쇄용지, 복사용지, 특수지 제조 및 품질관리

## ISO 14001 인증
- 정식 명칭: ISO 14001 환경경영시스템(Environmental Management System)
- 발급기관: ISO(국제표준화기구) 인정 제3자 심사기관(CB)
- 국내 인정기관: KAB(한국인정지원센터)
- 목적: 조직의 환경 영향을 체계적으로 관리하고 환경 성과를 지속적으로 개선
- 포함 영역: 탄소 저감, 폐기물 관리, 에너지 효율화
- 인증 유효기간: 3년
- 사후심사: 연 1회 (1차, 2차)
- 갱신심사: 3년 후 재심사
- 천안공장 인증번호: EMS-2023-00456
- 인증 기간: 2023-03-15 ~ 2026-03-14
- 마지막 심사: 2024-03-20 (사후심사 1차)
- 다음 심사: 2025-03-15 (사후심사 2차)
- 인증 범위: 천안공장 제지 생산 전 공정의 환경경영 활동

## Vegan 인증 (한국비건인증원 KV)
- 발급기관: 한국비건인증원(KV)
- 목적: 제품 원료·제조 공정 전 과정에서 동물 유래 성분 미사용 및 동물 실험 미수행 검증
- 종이·포장재 분야: 주로 동물성 접착제·코팅제 미사용 여부 검증
- 인증 유효기간: 1년
- 사후심사: 해당 없음 (갱신 시 재심사, 원료 변경 여부 재검토)
- 천안공장 인증번호: KV-2024-00789
- 인증 기간: 2024-05-01 ~ 2025-04-30
- 인증 범위: 친환경 복사용지, 포장박스 (동물성 원료 미사용 검증)

## Vegan 인증 (The Vegan Society, 영국)
- 발급기관: The Vegan Society (영국, 1944년 설립, 세계 최초 비건 단체)
- 인증 명칭: Vegan Trademark
- 목적: 글로벌 비건 인증, 유럽·북미 수출 제품 대상
- 인증 유효기간: 2년
- 천안공장 인증번호: TVS-2023-EU456
- 인증 기간: 2023-08-15 ~ 2025-08-14
- 인증 범위: 수출용 친환경 인쇄용지 (유럽 바이어 요청 대응)

## 담당자 정보
- 소속: 한솔제지(주) 천안공장 품질환경팀 품질관리
- 담당자: 장정록 책임
- 이메일: jjr@hansol.com
- 전화: 041-000-0000
"""

# ── 페이지 구성 ────────────────────────────────────────────
st.title("💬 인증 챗봇")
st.caption("인증 관련 궁금한 점을 질문하세요 — GPT-4o-mini 기반, 팩트 정보만 답변합니다.")
st.markdown("---")

# ── API 키 입력 ────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 OpenAI API 키")
    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-...",
        value=st.session_state.get("openai_api_key", ""),
        help="OpenAI API 키를 입력하세요. 키는 브라우저 세션에만 저장되며 서버에 보관되지 않습니다.",
    )
    if api_key_input:
        st.session_state["openai_api_key"] = api_key_input
        st.success("API 키가 입력되었습니다.", icon="✅")
    else:
        st.info("API 키를 입력해야 챗봇을 사용할 수 있습니다.")

    st.markdown("---")
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state["chat_messages"] = []
        st.rerun()

# ── API 키 없을 때 안내 ────────────────────────────────────
api_key = st.session_state.get("openai_api_key", "")
if not api_key:
    st.html("""
        <div style="background:#FFF8E1; border-left:4px solid #F9A825; border-radius:0 8px 8px 0;
                    padding:20px 24px; margin:20px 0; text-align:center;">
            <div style="font-size:32px; margin-bottom:12px;">🔑</div>
            <div style="font-size:16px; font-weight:700; color:#E65100; margin-bottom:8px;">
                API 키를 입력해 주세요
            </div>
            <div style="font-size:13px; color:#555; line-height:1.8;">
                왼쪽 사이드바에서 OpenAI API 키를 입력하면 챗봇을 사용할 수 있습니다.<br>
                API 키는 현재 브라우저 세션에만 임시 저장되며, 서버에 저장되지 않습니다.
            </div>
        </div>
    """)
    st.stop()

# ── 채팅 히스토리 초기화 ──────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# ── 안내 문구 (첫 대화 전) ────────────────────────────────
if not st.session_state["chat_messages"]:
    st.html("""
        <div style="background:#F1F8E9; border-radius:12px; padding:20px 24px; margin-bottom:20px;">
            <div style="font-size:14px; font-weight:700; color:#2E7D32; margin-bottom:12px;">
                💡 이런 질문을 해보세요
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:13px; color:#444;">
                <div style="background:#fff; border-radius:8px; padding:10px 14px; border:1px solid #C8E6C9;">
                    FSC 인증이 뭐야?
                </div>
                <div style="background:#fff; border-radius:8px; padding:10px 14px; border:1px solid #C8E6C9;">
                    환경표지인증 갱신은 언제까지 신청해야 해?
                </div>
                <div style="background:#fff; border-radius:8px; padding:10px 14px; border:1px solid #C8E6C9;">
                    ISO 9001 사후심사가 언제야?
                </div>
                <div style="background:#fff; border-radius:8px; padding:10px 14px; border:1px solid #C8E6C9;">
                    Vegan 인증 담당자 연락처 알려줘
                </div>
            </div>
        </div>
    """)

# ── 이전 대화 표시 ─────────────────────────────────────────
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 입력창 ────────────────────────────────────────────────
if prompt := st.chat_input("인증에 대해 궁금한 점을 입력하세요..."):

    # 사용자 메시지 저장 및 표시
    st.session_state["chat_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GPT 호출
    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            try:
                client = OpenAI(api_key=api_key)

                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                # 최근 10턴만 컨텍스트로 전달 (비용 절감)
                for m in st.session_state["chat_messages"][-10:]:
                    messages.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0,          # 추정·창작 최소화
                    max_tokens=1000,
                )
                answer = response.choices[0].message.content

            except Exception as e:
                err = str(e)
                if "invalid_api_key" in err or "Incorrect API key" in err:
                    answer = "❌ API 키가 올바르지 않습니다. 사이드바에서 키를 다시 확인해 주세요."
                elif "quota" in err.lower() or "billing" in err.lower():
                    answer = "❌ API 사용 한도를 초과했거나 결제 정보가 필요합니다. OpenAI 계정을 확인해 주세요."
                else:
                    answer = f"❌ 오류가 발생했습니다: {err}"

        st.markdown(answer)

    st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
