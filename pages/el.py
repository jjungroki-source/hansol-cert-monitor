import streamlit as st
import pandas as pd
from datetime import date
from utils.dday import calc_dday, get_alert_level, ALERT_COLORS, ALERT_LABELS, dday_label


st.title("♻️ 환경표지인증(EL) 관리")
st.caption("제품별 인증 유효기간(3년) · 사후관리(연 1회) 모니터링 — 발급기관: KEITI")
st.markdown('---')

# ── 인증 소개 ──────────────────────────────────────────────
st.html(
    """
    <div style="background:#F5F5F7;border-left:3px solid #007AFF;border-radius:0 16px 16px 0;
                padding:20px 24px;margin-bottom:24px;">
        <div style="margin-bottom:10px;">
            <span style="font-size:15px;font-weight:700;color:#1D1D1F;">환경표지인증 (EL)</span>
            <span style="font-size:12px;color:#6E6E73;margin-left:8px;">Environmental Label · 환경부 산하 KEITI 발급</span>
        </div>
        <div style="font-size:13px;color:#3D3D3D;line-height:1.85;margin-bottom:14px;">
            같은 용도의 제품 중 생산·유통·사용·폐기 전 과정에서 <strong>환경 영향이 가장 적은 제품</strong>에 부여하는
            <strong>국가 공인 친환경 인증 제도</strong>입니다.<br>
            인증 단위는 <strong>제품별(모델 단위)</strong>이며, 인증 취득 시 공공기관 녹색제품 의무구매 대상 품목으로 등재됩니다.
        </div>
        <div style="border-top:1px solid #E8E8ED;padding-top:12px;display:flex;flex-wrap:wrap;gap:8px;font-size:12px;">
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🏛 공공조달 우선구매 대상</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">📦 인증 단위: 제품(모델)별</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">📅 유효기간 <strong>3년</strong></span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🔍 사후관리 <strong>연 1회</strong></span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">⏰ 갱신 권장: 만료 <strong>90일 전</strong></span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🌐 el.keiti.re.kr</span>
        </div>
    </div>
    """,
)

# ── 데이터 로드 ───────────────────────────────────────────
@st.cache_data(ttl=300)
def load_el():
    try:
        df = pd.read_excel("data/el_sample.xlsx", dtype=str)
        for col in ["최초인증일", "인증시작일", "인증종료일"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df = load_el()

if df.empty:
    st.warning("data/el_sample.xlsx 파일을 확인해 주세요.")
    st.stop()

# ── D-day 계산 ────────────────────────────────────────────
df["D-day_num"] = df["인증종료일"].apply(calc_dday)
df["D-day"]     = df["D-day_num"].apply(dday_label)
df["알림단계"]  = df["D-day_num"].apply(get_alert_level)
df["상태"]      = df["알림단계"].map(ALERT_LABELS)

# ── KPI 요약 ──────────────────────────────────────────────
total    = len(df)
expired  = int((df["알림단계"] == "expired").sum())
critical = int((df["알림단계"] == "critical").sum())
warning  = int((df["알림단계"] == "warning").sum())
caution  = int((df["알림단계"] == "caution").sum())
normal   = int((df["알림단계"] == "normal").sum())

kpi_data = [
    ("전체",      total,    "#1D1D1F"),
    ("만료",      expired,  ALERT_COLORS["expired"]),
    ("D-7 위험",  critical, ALERT_COLORS["critical"]),
    ("D-30 경고", warning,  ALERT_COLORS["warning"]),
    ("D-90 주의", caution,  ALERT_COLORS["caution"]),
]

cols = st.columns(5)
for col, (label, val, color) in zip(cols, kpi_data):
    col.html(
        f'<div style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:16px;'
        f'padding:18px 14px;height:96px;display:flex;flex-direction:column;'
        f'justify-content:space-between;box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
        f'<div style="font-size:12px;color:#6E6E73;text-transform:uppercase;letter-spacing:0.4px;font-weight:500;">{label}</div>'
        f'<div style="font-size:28px;font-weight:700;color:{color};line-height:1;">{val}</div>'
        f'<div style="font-size:12px;color:#8E8E93;">건</div>'
        f'</div>',
    )

st.markdown('---')

# ── 필터 ──────────────────────────────────────────────────
f1, f2, f3 = st.columns([2, 2, 6])
status_filter = f1.selectbox("상태 필터", ["전체", "만료", "D-7 위험", "D-30 경고", "D-90 주의", "정상"])
group_filter  = f2.selectbox("제품군 필터", ["전체"] + sorted(df["대상제품군"].dropna().unique().tolist()))

LABEL_TO_KEY = {"전체": None, "만료": "expired", "D-7 위험": "critical",
                "D-30 경고": "warning", "D-90 주의": "caution", "정상": "normal"}

filtered = df.copy()
if LABEL_TO_KEY[status_filter]:
    filtered = filtered[filtered["알림단계"] == LABEL_TO_KEY[status_filter]]
if group_filter != "전체":
    filtered = filtered[filtered["대상제품군"] == group_filter]

filtered = filtered.sort_values("D-day_num", na_position="last")

# ── 상세 테이블 ───────────────────────────────────────────
st.subheader(f"📋 인증 목록 ({len(filtered)}건)")

DISPLAY_COLS = ["대상제품군", "업체명", "제품명(상표명)", "인증시작일", "인증종료일", "D-day", "상태", "공장구분"]
show_cols = [c for c in DISPLAY_COLS if c in filtered.columns]
view = filtered[show_cols].copy()

for col in ["인증시작일", "인증종료일"]:
    if col in view.columns:
        view[col] = pd.to_datetime(view[col]).dt.strftime("%Y-%m-%d")

def highlight_status(row):
    level = filtered.loc[row.name, "알림단계"] if row.name in filtered.index else "normal"
    color = ALERT_COLORS.get(level, "#8E8E93")
    return [f"background-color:{color}14"] * len(row)

styled = view.style.apply(highlight_status, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)

# ── 카드 뷰 (긴급 항목) ───────────────────────────────────
urgent = filtered[filtered["알림단계"].isin(["expired", "critical", "warning"])]
if not urgent.empty:
    st.markdown('---')
    st.subheader("🚨 즉시 조치 필요 항목")
    for _, row in urgent.iterrows():
        level = row["알림단계"]
        color = ALERT_COLORS[level]
        label = ALERT_LABELS[level]
        name  = row.get("제품명(상표명)", "")
        group = row.get("대상제품군", "")
        end   = str(row.get("인증종료일", ""))[:10]
        dd    = row.get("D-day", "-")
        st.html(
            f'<div style="background:#FFFFFF;border:1px solid #D2D2D7;border-left:3px solid {color};'
            f'border-radius:0 14px 14px 0;padding:14px 20px;margin:6px 0;'
            f'display:flex;justify-content:space-between;align-items:center;'
            f'box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
            f'<div>'
            f'<div style="font-size:14px;font-weight:600;color:#1D1D1F;">{name}</div>'
            f'<div style="font-size:12px;color:#6E6E73;margin-top:2px;">{group} · 인증종료일 {end}</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:24px;font-weight:700;color:{color};line-height:1;">{dd}</div>'
            f'<div style="background:{color}18;color:{color};border-radius:12px;padding:2px 10px;'
            f'font-size:13px;font-weight:600;margin-top:4px;">{label}</div>'
            f'</div></div>',
        )

# ── 인증서 보기 ────────────────────────────────────────────
with st.expander("📄 인증서 보기 (샘플)", expanded=False):
    st.caption("※ 실제 인증서 파일로 교체하여 사용하세요. 현재는 샘플 이미지입니다.")
    st.image("data/certs/el_cert.svg", use_container_width=True)

# ── 안내 ──────────────────────────────────────────────────
st.markdown('---')
with st.expander("ℹ️ 환경표지인증 갱신 안내"):
    st.markdown("""
| 구분 | 내용 |
|------|------|
| 유효기간 | 3년 (인증시작일 기준) |
| 사후관리 | 연 1회 (KEITI 현장심사) |
| 갱신신청 | 만료 **90일 전** 권장 |
| 발급기관 | 한국환경산업기술원 (KEITI) |
| 신청방법 | 환경표지 인증시스템 (el.keiti.re.kr) |

- **D-90 주의**: 갱신 준비 시작 (서류 점검, 시험성적서 유효기간 확인)
- **D-30 경고**: 갱신 신청 접수 마감 임박
- **D-7 위험**: 즉시 KEITI 담당자 연락 필요
""")
