import streamlit as st
import json
import pandas as pd
from datetime import date
from utils.dday import calc_dday, get_alert_level, ALERT_COLORS, ALERT_LABELS, dday_label
from utils.fsc_checklist import FSC_CHECKLIST


st.title("🌲 FSC CoC 인증 관리")
st.caption("갱신심사(5년) · 사후심사(연 1회) 일정 및 심사 준비 체크리스트")
st.markdown('---')

# ── 인증 소개 ──────────────────────────────────────────────
st.html(
    """
    <div style="background:#F5F5F7;border-left:3px solid #34C759;border-radius:0 16px 16px 0;
                padding:20px 24px;margin-bottom:24px;">
        <div style="margin-bottom:10px;">
            <span style="font-size:15px;font-weight:700;color:#1D1D1F;">FSC CoC 인증</span>
            <span style="font-size:12px;color:#6E6E73;margin-left:8px;">Forest Stewardship Council · 산림관리협의회</span>
        </div>
        <div style="font-size:13px;color:#3D3D3D;line-height:1.85;margin-bottom:14px;">
            지속 가능한 방식으로 관리된 산림에서 생산된 목재·종이 제품임을 보증하는 <strong>국제 산림 인증 제도</strong>입니다.<br>
            <strong>CoC</strong>(Chain of Custody · 공급망 관리) — 인증 원료가 산림에서 최종 제품까지
            공급망 전 과정에서 적절히 <strong>관리·추적</strong>됨을 증명합니다.
        </div>
        <div style="border-top:1px solid #E8E8ED;padding-top:12px;display:flex;flex-wrap:wrap;gap:8px;font-size:12px;">
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🚫 불법 벌채 방지</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🌱 지속가능한 원료 조달</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">📊 ESG 경영 대응</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🔄 갱신심사 <strong>5년</strong></span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🔍 사후심사 <strong>연 1회</strong></span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🏢 발급: FSC International</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🌐 info.fsc.org</span>
        </div>
    </div>
    """,
)

# ── 데이터 로드 ───────────────────────────────────────────
DATA_PATH = "data/fsc_schedule.json"

def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()
cert = data["certification"]
checklist_status = data.get("checklist_status", {})

# ── 일정 현황 ──────────────────────────────────────────────
st.subheader("📅 심사 일정")

renewal_dday = calc_dday(cert["next_renewal"])
surv_dday    = calc_dday(cert["next_surveillance"])

col1, col2 = st.columns(2)

def schedule_card(col, title, target_date, dday, audit_type):
    level = get_alert_level(dday)
    color = ALERT_COLORS[level]
    label = ALERT_LABELS[level]
    col.html(
        f'<div style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:18px;'
        f'padding:28px 20px;height:180px;display:flex;flex-direction:column;'
        f'align-items:center;justify-content:space-between;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
        f'<div style="font-size:13px;color:#6E6E73;text-transform:uppercase;'
        f'letter-spacing:0.5px;font-weight:500;">{title}</div>'
        f'<div style="font-size:44px;font-weight:700;color:{color};line-height:1;">{dday_label(dday)}</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-size:14px;color:#1D1D1F;font-weight:500;">{target_date}</div>'
        f'<div style="display:inline-block;background:{color}18;color:{color};border-radius:20px;'
        f'padding:3px 14px;font-size:12px;font-weight:600;margin-top:6px;">{label}</div>'
        f'</div>'
        f'<div style="font-size:13px;color:#8E8E93;">{audit_type}</div>'
        f'</div>',
    )

with col1:
    schedule_card(col1, "갱신심사", cert["next_renewal"], renewal_dday, "주기: 5년")
with col2:
    schedule_card(col2, "사후심사", cert["next_surveillance"], surv_dday, "주기: 연 1회")

st.markdown('---')

# ── 인증 정보 수정 ─────────────────────────────────────────
with st.expander("⚙️ 인증 정보 수정", expanded=False):
    with st.form("cert_form"):
        c1, c2, c3 = st.columns(3)
        cert_no = c1.text_input("인증번호", value=cert["cert_no"])
        company = c2.text_input("업체명", value=cert["company"])
        cb      = c3.text_input("인증기관(CB)", value=cert["cb"])
        c4, c5, c6, c7 = st.columns(4)
        last_renewal   = c4.date_input("마지막 갱신심사", value=pd.to_datetime(cert["last_renewal"]))
        next_renewal   = c5.date_input("다음 갱신심사",   value=pd.to_datetime(cert["next_renewal"]))
        last_surv      = c6.date_input("마지막 사후심사", value=pd.to_datetime(cert["last_surveillance"]))
        next_surv      = c7.date_input("다음 사후심사",   value=pd.to_datetime(cert["next_surveillance"]))
        submitted = st.form_submit_button("저장")
        if submitted:
            data["certification"].update({
                "cert_no":           cert_no,
                "company":           company,
                "cb":                cb,
                "last_renewal":      str(last_renewal),
                "next_renewal":      str(next_renewal),
                "last_surveillance": str(last_surv),
                "next_surveillance": str(next_surv),
            })
            save_data(data)
            st.success("저장되었습니다.")
            st.cache_data.clear()
            st.rerun()

# ── 체크리스트 ─────────────────────────────────────────────
st.subheader("✅ 심사 준비 체크리스트")

STATUS_OPTIONS = ["미착수", "진행중", "완료"]
STATUS_COLORS  = {"미착수": "#FF3B30", "진행중": "#FF9500", "완료": "#34C759"}

done    = sum(1 for v in checklist_status.values() if v == "완료")
ongoing = sum(1 for v in checklist_status.values() if v == "진행중")
todo    = sum(1 for v in checklist_status.values() if v == "미착수")
total   = len(checklist_status) or len(FSC_CHECKLIST)
st.progress(done / total if total else 0,
            text=f"완료 {done} | 진행중 {ongoing} | 미착수 {todo} | 전체 {total}")

filter_col1, filter_col2 = st.columns([2, 8])
status_filter = filter_col1.selectbox("상태 필터", ["전체"] + STATUS_OPTIONS, key="fsc_filter")

items = FSC_CHECKLIST
if status_filter != "전체":
    items = [i for i in items if checklist_status.get(str(i["no"]), "미착수") == status_filter]

h1, h2, h3, h4, h5 = st.columns([0.5, 3, 5, 2, 1.5])
h1.markdown("**No**"); h2.markdown("**준비항목**")
h3.markdown("**세부내용**"); h4.markdown("**담당부서**"); h5.markdown("**상태**")
st.html('<hr style="margin:4px 0;border-color:#D2D2D7;"/>')

changed = {}
for item in items:
    key   = str(item["no"])
    cur   = checklist_status.get(key, "미착수")

    c1, c2, c3, c4, c5 = st.columns([0.5, 3, 5, 2, 1.5])
    c1.markdown(f"**{item['no']}**")
    c2.markdown(item["항목"])
    c3.html(f'<span style="font-size:12px;color:#6E6E73;">{item["세부내용"]}</span>')
    c4.html(f'<span style="font-size:12px;color:#3D3D3D;">{item["담당부서"]}</span>')
    new_status = c5.selectbox(
        label="",
        options=STATUS_OPTIONS,
        index=STATUS_OPTIONS.index(cur),
        key=f"cl_{key}",
        label_visibility="collapsed",
    )
    if new_status != cur:
        changed[key] = new_status

    badge_color = STATUS_COLORS[new_status]
    c5.html(
        f'<div style="background:{badge_color}18;border:1px solid {badge_color}40;'
        f'border-radius:6px;padding:2px 6px;font-size:13px;text-align:center;'
        f'margin-top:-4px;color:{badge_color};font-weight:600;">{new_status}</div>',
    )

if changed:
    checklist_status.update(changed)
    data["checklist_status"] = checklist_status
    save_data(data)
    st.success(f"{len(changed)}건 상태가 업데이트되었습니다.")
    st.cache_data.clear()
    st.rerun()

# ── 인증서 보기 ────────────────────────────────────────────
st.markdown('---')
with st.expander("📄 인증서 보기 (샘플)", expanded=False):
    st.caption("※ 실제 인증서 파일로 교체하여 사용하세요. 현재는 샘플 이미지입니다.")
    st.image("data/certs/fsc_coc.svg", use_container_width=True)
