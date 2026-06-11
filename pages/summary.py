import streamlit as st
import json
import pandas as pd
from datetime import date
from utils.dday import calc_dday, get_alert_level, ALERT_COLORS, ALERT_LABELS, dday_label

st.title("한솔제지 천안공장 인증 모니터링")
st.caption("FSC CoC 인증 · 환경표지인증(EL) 통합 관리")
st.markdown('---')

# ── 데이터 로드 ───────────────────────────────────────────
@st.cache_data(ttl=300)
def load_fsc():
    with open("data/fsc_schedule.json", encoding="utf-8") as f:
        return json.load(f)

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

fsc    = load_fsc()
el_df  = load_el()
cert   = fsc["certification"]

fsc_next_surv_dday = calc_dday(cert["next_surveillance"])

if not el_df.empty:
    el_df["_dday"]    = el_df["인증종료일"].apply(calc_dday)
    el_df["알림단계"] = el_df["_dday"].apply(get_alert_level)
    el_total  = len(el_df)
    el_due    = int(el_df["알림단계"].isin(["expired", "critical", "warning", "caution"]).sum())
    el_normal = el_total - el_due
else:
    el_total = el_due = el_normal = 0

# ── Apple 균일 내부 카드 ──────────────────────────────────
def _inner(label, value, sub, accent=None):
    bg = f"{accent}0E" if accent else "#F5F5F7"
    vc = accent if accent else "#1D1D1F"
    return (
        f'<div style="background:{bg};border-radius:14px;padding:14px 16px;height:84px;'
        f'display:flex;flex-direction:column;justify-content:space-between;">'
        f'<div style="font-size:12px;color:#6E6E73;text-transform:uppercase;'
        f'letter-spacing:0.4px;font-weight:500;">{label}</div>'
        f'<div style="font-size:16px;font-weight:700;color:{vc};line-height:1.2;">{value}</div>'
        f'<div style="font-size:12px;color:#8E8E93;">{sub}</div>'
        f'</div>'
    )

# ── 전체 현황 요약 ─────────────────────────────────────────
st.subheader("📊 전체 현황 요약")

left, right = st.columns(2)

with left:
    cert_start   = cert.get("cert_start", "")
    cert_end     = cert.get("cert_end", "")
    last_renewal = cert.get("last_renewal", "")
    last_surv    = cert.get("last_surveillance", "")
    dates_valid  = [(d, t) for d, t in [(last_renewal, "갱신심사"), (last_surv, "사후심사")] if d]
    last_audit_date, last_audit_type = max(dates_valid, key=lambda x: x[0]) if dates_valid else ("-", "-")
    surv_level = get_alert_level(fsc_next_surv_dday)
    surv_color = ALERT_COLORS[surv_level]

    c1 = _inner("인증 기간", cert_start, f"~ {cert_end}")
    c2 = _inner("마지막 심사", last_audit_date, last_audit_type)
    c3 = _inner("다음 사후심사", dday_label(fsc_next_surv_dday), cert["next_surveillance"], surv_color)

    st.html(
        f'<div style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;'
        f'padding:22px;box-shadow:0 1px 6px rgba(0,0,0,0.06);">'
        f'<div style="font-size:14px;font-weight:700;color:#1D1D1F;margin-bottom:14px;">'
        f'🌲 FSC CoC 인증</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">'
        f'{c1}{c2}{c3}'
        f'</div></div>'
    )

with right:
    due_color = ALERT_COLORS["critical"] if el_due > 0 else "#34C759"

    c1 = _inner("천안공장 제품", str(el_total), "건")
    c2 = _inner("심사 도래", str(el_due), "D-90 이내", due_color if el_due > 0 else None)
    c3 = _inner("이상 없음", str(el_normal), "건")

    st.html(
        f'<div style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;'
        f'padding:22px;box-shadow:0 1px 6px rgba(0,0,0,0.06);">'
        f'<div style="font-size:14px;font-weight:700;color:#1D1D1F;margin-bottom:14px;">'
        f'♻️ 환경표지인증 (EL)</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">'
        f'{c1}{c2}{c3}'
        f'</div></div>'
    )

st.markdown('---')

# ── 알림 배너 ─────────────────────────────────────────────
alerts = []
surv_level = get_alert_level(fsc_next_surv_dday)
if surv_level in ("expired", "critical", "warning", "caution"):
    alerts.append((surv_level, f"[FSC] 사후심사 {dday_label(fsc_next_surv_dday)} — {cert['next_surveillance']} 예정"))

if not el_df.empty:
    urgent = el_df[el_df["알림단계"].isin(["expired", "critical", "warning", "caution"])].sort_values("_dday")
    for _, row in urgent.iterrows():
        alerts.append((row["알림단계"],
            f"[EL] {row.get('제품명(상표명)', '')} — {dday_label(row['_dday'])} "
            f"(만료 {str(row['인증종료일'])[:10]})"))

BANNER = {
    "expired":  ("#FF3B30", "#FFF2F1"),
    "critical": ("#FF3B30", "#FFF2F1"),
    "warning":  ("#FF9500", "#FFF8EF"),
    "caution":  ("#FF9F0A", "#FFFDF0"),
}

if alerts:
    st.subheader("🔔 알림")
    for lvl, msg in alerts:
        fg, bg = BANNER.get(lvl, ("#007AFF", "#F0F7FF"))
        st.html(
            f'<div style="background:{bg};border-left:3px solid {fg};border-radius:0 12px 12px 0;'
            f'padding:11px 18px;margin:4px 0;color:{fg};font-size:13px;font-weight:500;">{msg}</div>'
        )
    st.markdown('---')

# ── EL 현황 테이블 ────────────────────────────────────────
st.subheader("📋 환경표지인증 (EL) 현황")

if el_df.empty:
    st.info("data/el_sample.xlsx 파일을 확인해 주세요.")
else:
    view = el_df.copy()
    view["인증종료일_표시"] = view["인증종료일"].dt.strftime("%Y-%m-%d")
    view["D-day표시"]      = view["_dday"].apply(dday_label)
    view["상태"]           = view["알림단계"].map(ALERT_LABELS)
    show_cols = [c for c in ["대상제품군", "제품명(상표명)", "인증종료일_표시", "D-day표시", "상태"] if c in view.columns]
    show = view[show_cols].rename(columns={"인증종료일_표시": "인증종료일", "D-day표시": "D-day"})
    st.dataframe(show, use_container_width=True, hide_index=True)

# ── FSC 체크리스트 진행률 ──────────────────────────────────
st.markdown('---')
st.subheader("🌲 FSC 심사 준비 체크리스트")
checklist_data = fsc.get("checklist_status", {})
done        = sum(1 for v in checklist_data.values() if v == "완료")
ongoing     = sum(1 for v in checklist_data.values() if v == "진행중")
todo        = sum(1 for v in checklist_data.values() if v == "미착수")
total_items = len(checklist_data)
st.progress(done / total_items if total_items else 0,
            text=f"완료 {done} | 진행중 {ongoing} | 미착수 {todo} | 전체 {total_items}건")
st.caption("👈 1. FSC 인증 페이지에서 항목별 상태를 관리할 수 있습니다.")
