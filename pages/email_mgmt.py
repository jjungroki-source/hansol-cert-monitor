import streamlit as st
import json
import uuid
import smtplib
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

from utils.dday import calc_dday, dday_label
from utils.email_sender import (
    send_emails, test_connection,
    fsc_d60, fsc_d30,
    iso_d60, iso_d30,
    el_d60, vegan_d60,
)

RECIPIENTS_PATH = "data/recipients.json"
FSC_PATH        = "data/fsc_schedule.json"

# ── 데이터 헬퍼 ──────────────────────────────────────────
def load_recipients():
    try:
        with open(RECIPIENTS_PATH, encoding="utf-8") as f:
            return json.load(f).get("recipients", [])
    except Exception:
        return []

def save_recipients(lst):
    Path(RECIPIENTS_PATH).write_text(
        json.dumps({"recipients": lst}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def load_fsc():
    with open(FSC_PATH, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(ttl=300)
def load_el():
    try:
        df = pd.read_excel("data/el_sample.xlsx", dtype=str)
        for c in ["최초인증일", "인증시작일", "인증종료일"]:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# ── ISO / Vegan 고정 정보 ─────────────────────────────────
ISO_DATA = {
    "ISO 9001": {
        "cert_no": "QMS-2022-00123",
        "cert_start": "2022-09-01", "cert_end": "2025-08-31",
        "next_audit": "2025-09-01",
    },
    "ISO 14001": {
        "cert_no": "EMS-2023-00456",
        "cert_start": "2023-03-15", "cert_end": "2026-03-14",
        "next_audit": "2025-03-15",
    },
}
VEGAN_DATA = {
    "한국비건인증원 (KV)": {
        "cert_end": "2025-04-30", "next_audit": "2025-04-01",
        "scope": "친환경 복사용지, 포장박스",
    },
    "The Vegan Society (영국)": {
        "cert_end": "2025-08-14", "next_audit": "2025-07-15",
        "scope": "수출용 친환경 인쇄용지",
    },
}

def _deadline(date_str: str, offset_days: int = -30) -> str:
    from datetime import datetime
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return str(d + timedelta(days=offset_days))

# ── SMTP 설정 헬퍼 ────────────────────────────────────────
def get_smtp():
    return {
        "host":        st.session_state.get("smtp_host", ""),
        "port":        st.session_state.get("smtp_port", "587"),
        "user":        st.session_state.get("smtp_user", ""),
        "password":    st.session_state.get("smtp_pass", ""),
        "sender_name": st.session_state.get("smtp_name", "한솔제지 품질환경팀"),
    }

def smtp_ready() -> bool:
    s = get_smtp()
    return bool(s["host"] and s["user"] and s["password"])

# ── 페이지 ────────────────────────────────────────────────
st.title("📧 알림 관리")
st.caption("수신자 관리 · SMTP 설정 · 메일 발송")
st.markdown("---")

tab_recv, tab_smtp, tab_send = st.tabs(["👥 수신자 관리", "⚙️ SMTP 설정", "📤 메일 발송"])

# ══════════════════════════════════════════════════════════
# TAB 1 — 수신자 관리
# ══════════════════════════════════════════════════════════
with tab_recv:
    recipients = load_recipients()

    st.subheader("📋 수신자 목록")

    if not recipients:
        st.info("등록된 수신자가 없습니다. 아래 양식에서 추가해 주세요.")
    else:
        # Header row
        h1, h2, h3, h4 = st.columns([2.5, 3.5, 2.5, 1])
        h1.html('<div style="font-size:13px;color:#6E6E73;font-weight:600;text-transform:uppercase;letter-spacing:0.4px;padding:4px 0;">이름</div>')
        h2.html('<div style="font-size:13px;color:#6E6E73;font-weight:600;text-transform:uppercase;letter-spacing:0.4px;padding:4px 0;">이메일</div>')
        h3.html('<div style="font-size:13px;color:#6E6E73;font-weight:600;text-transform:uppercase;letter-spacing:0.4px;padding:4px 0;">담당부서</div>')
        st.html('<hr style="border:none;border-top:1px solid #D2D2D7;margin:2px 0 4px;"/>')

        to_delete = None
        for r in recipients:
            c1, c2, c3, c4 = st.columns([2.5, 3.5, 2.5, 1])
            c1.html(f'<div style="font-size:13px;font-weight:600;color:#1D1D1F;padding:6px 0;">{r["name"]}</div>')
            c2.html(f'<div style="font-size:13px;color:#6E6E73;padding:6px 0;">{r["email"]}</div>')
            c3.html(f'<div style="font-size:13px;color:#3D3D3D;padding:6px 0;">{r["department"]}</div>')
            if c4.button("삭제", key=f"del_{r['id']}", type="secondary"):
                to_delete = r["id"]

        if to_delete:
            recipients = [x for x in recipients if x["id"] != to_delete]
            save_recipients(recipients)
            st.rerun()

    st.markdown("---")
    st.subheader("➕ 수신자 추가")
    with st.form("add_recipient_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        inp_name  = col1.text_input("이름 *", placeholder="홍길동")
        inp_email = col2.text_input("이메일 *", placeholder="hong@company.com")
        inp_dept  = col3.text_input("담당부서 *", placeholder="생산팀")
        submitted = st.form_submit_button("추가", use_container_width=False)

        if submitted:
            if not inp_name or not inp_email or not inp_dept:
                st.error("이름, 이메일, 담당부서를 모두 입력해 주세요.")
            elif "@" not in inp_email or "." not in inp_email.split("@")[-1]:
                st.error("올바른 이메일 형식을 입력해 주세요.")
            elif any(r["email"] == inp_email for r in recipients):
                st.warning(f"{inp_email} 은 이미 등록된 이메일입니다.")
            else:
                recipients.append({
                    "id":         str(uuid.uuid4())[:8],
                    "name":       inp_name.strip(),
                    "email":      inp_email.strip(),
                    "department": inp_dept.strip(),
                })
                save_recipients(recipients)
                st.success(f"✅ {inp_name} ({inp_email}) 이(가) 추가되었습니다.")
                st.rerun()

# ══════════════════════════════════════════════════════════
# TAB 2 — SMTP 설정
# ══════════════════════════════════════════════════════════
with tab_smtp:
    st.subheader("⚙️ SMTP 서버 설정")
    st.caption("설정은 현재 세션에만 유지됩니다. 새로고침 후 재입력이 필요합니다.")

    col_host, col_port = st.columns([4, 1])
    smtp_host = col_host.text_input("SMTP 서버 주소",
        value=st.session_state.get("smtp_host", "smtp.gmail.com"),
        placeholder="smtp.gmail.com")
    smtp_port = col_port.text_input("포트",
        value=st.session_state.get("smtp_port", "587"),
        placeholder="587")
    smtp_user = st.text_input("발신 이메일 주소",
        value=st.session_state.get("smtp_user", ""),
        placeholder="your@gmail.com")
    smtp_pass = st.text_input("비밀번호 / 앱 비밀번호",
        type="password",
        value=st.session_state.get("smtp_pass", ""),
        placeholder="16자리 앱 비밀번호 입력")
    smtp_name = st.text_input("발신자 표시 이름",
        value=st.session_state.get("smtp_name", "한솔제지 품질환경팀"),
        placeholder="한솔제지 품질환경팀")

    col_save, col_test, _ = st.columns([2, 2, 6])

    if col_save.button("💾 설정 저장", use_container_width=True, type="primary"):
        st.session_state.update({
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_user": smtp_user,
            "smtp_pass": smtp_pass,
            "smtp_name": smtp_name,
        })
        st.success("SMTP 설정이 세션에 저장되었습니다.")

    if col_test.button("🔌 연결 테스트", use_container_width=True):
        if not smtp_user or not smtp_pass:
            st.error("이메일과 비밀번호를 먼저 입력해 주세요.")
        else:
            with st.spinner("연결 중..."):
                try:
                    test_connection({
                        "host": smtp_host, "port": smtp_port,
                        "user": smtp_user, "password": smtp_pass,
                    })
                    st.success("✅ SMTP 연결 성공!")
                except Exception as e:
                    st.error(f"❌ 연결 실패: {e}")

    st.markdown("---")
    with st.expander("📌 Gmail 앱 비밀번호 설정 방법"):
        st.markdown("""
1. **Google 계정 설정** → **보안** → **2단계 인증** 활성화
2. 보안 페이지 → **앱 비밀번호** 생성 (앱: `메일`, 기기: `기타` → `Hansol`)
3. 생성된 **16자리 비밀번호**를 위 '비밀번호' 입력란에 입력
4. SMTP 서버: `smtp.gmail.com` / 포트: `587`

> 사내 Exchange 서버 사용 시 IT팀에 SMTP 주소·포트·인증 방식을 문의하세요.
""")

# ══════════════════════════════════════════════════════════
# TAB 3 — 메일 발송
# ══════════════════════════════════════════════════════════
with tab_send:
    recipients = load_recipients()

    if not smtp_ready():
        st.html(
            '<div style="background:#FFF8EF;border-left:3px solid #FF9500;border-radius:0 12px 12px 0;'
            'padding:14px 20px;font-size:13px;color:#3D3D3D;">'
            '⚠️ &nbsp;<strong>SMTP 설정</strong> 탭에서 서버 정보를 먼저 저장해 주세요.</div>'
        )

    if not recipients:
        st.html(
            '<div style="background:#F0F7FF;border-left:3px solid #007AFF;border-radius:0 12px 12px 0;'
            'padding:14px 20px;font-size:13px;color:#3D3D3D;margin-top:12px;">'
            'ℹ️ &nbsp;<strong>수신자 관리</strong> 탭에서 수신자를 먼저 등록해 주세요.</div>'
        )

    if recipients:
        # 수신자 선택
        st.subheader("1️⃣ 수신자 선택")
        all_names = [f"{r['name']} ({r['department']})" for r in recipients]
        selected_names = st.multiselect(
            "메일을 받을 수신자를 선택하세요 (복수 선택 가능)",
            options=all_names,
            default=all_names,
            key="mail_recv_select",
        )
        selected_ids = {
            r["id"] for r in recipients
            if f"{r['name']} ({r['department']})" in selected_names
        }
        selected_recipients = [r for r in recipients if r["id"] in selected_ids]

        st.html(
            f'<div style="font-size:12px;color:#6E6E73;margin-top:-8px;margin-bottom:16px;">'
            f'총 <strong>{len(selected_recipients)}명</strong> 선택됨</div>'
        )

        st.markdown("---")
        st.subheader("2️⃣ 발송할 메일 선택")

        # ── FSC ────────────────────────────────────────────
        fsc_data = load_fsc()
        fsc_cert = fsc_data["certification"]
        fsc_surv = fsc_cert["next_surveillance"]
        fsc_dday = calc_dday(fsc_surv)

        with st.expander(f"🌲 FSC CoC 인증 — 다음 사후심사: {fsc_surv} ({dday_label(fsc_dday)})", expanded=True):
            col_a, col_b = st.columns(2)

            # D-60
            with col_a:
                doc_dl_60 = _deadline(fsc_surv, -45)
                subj_60, html_60 = fsc_d60(
                    audit_date=fsc_surv,
                    cert_no=fsc_cert["cert_no"],
                    cert_period=f'{fsc_cert["cert_start"]} ~ {fsc_cert["cert_end"]}',
                    doc_deadline=doc_dl_60,
                )
                st.html(
                    f'<div style="background:#F5F5F7;border-radius:12px;padding:14px 16px;">'
                    f'<div style="font-size:12px;font-weight:700;color:#1D1D1F;margin-bottom:4px;">📢 심사 2개월 전 공지</div>'
                    f'<div style="font-size:13px;color:#6E6E73;">심사 일정 안내 + 부서별 자료 요청</div>'
                    f'</div>'
                )
                with st.expander("📧 미리보기"):
                    preview_60 = html_60.replace("[[NAME]]", "수신자").replace("[[DEPT]]", "담당부서")
                    st.components.v1.html(preview_60, height=520, scrolling=True)

                if st.button("📤 발송", key="send_fsc_60", use_container_width=True,
                             type="primary", disabled=not smtp_ready() or not selected_recipients):
                    with st.spinner(f"{len(selected_recipients)}명에게 발송 중..."):
                        try:
                            fails = send_emails(get_smtp(), selected_recipients, subj_60, html_60)
                            sent  = len(selected_recipients) - len(fails)
                            if fails:
                                st.warning(f"✅ {sent}명 성공 / ❌ {len(fails)}명 실패\n" + "\n".join(fails))
                            else:
                                st.success(f"✅ {sent}명에게 성공적으로 발송되었습니다.")
                        except RuntimeError as e:
                            st.error(str(e))

            # D-30
            with col_b:
                from datetime import datetime
                surv_date = datetime.strptime(fsc_surv, "%Y-%m-%d").date()
                internal_dt = surv_date - timedelta(days=28)
                internal_str = str(internal_dt)
                subj_30, html_30 = fsc_d30(audit_date=fsc_surv, internal_date=internal_str)

                st.html(
                    f'<div style="background:#F5F5F7;border-radius:12px;padding:14px 16px;">'
                    f'<div style="font-size:12px;font-weight:700;color:#1D1D1F;margin-bottom:4px;">📋 심사 1개월 전 내부심사 안내</div>'
                    f'<div style="font-size:13px;color:#6E6E73;">내부심사 일정 + 필수 제출 자료 요청</div>'
                    f'</div>'
                )
                with st.expander("📧 미리보기"):
                    preview_30 = html_30.replace("[[NAME]]", "수신자").replace("[[DEPT]]", "담당부서")
                    st.components.v1.html(preview_30, height=520, scrolling=True)

                if st.button("📤 발송", key="send_fsc_30", use_container_width=True,
                             type="primary", disabled=not smtp_ready() or not selected_recipients):
                    with st.spinner(f"{len(selected_recipients)}명에게 발송 중..."):
                        try:
                            fails = send_emails(get_smtp(), selected_recipients, subj_30, html_30)
                            sent  = len(selected_recipients) - len(fails)
                            if fails:
                                st.warning(f"✅ {sent}명 성공 / ❌ {len(fails)}명 실패\n" + "\n".join(fails))
                            else:
                                st.success(f"✅ {sent}명에게 성공적으로 발송되었습니다.")
                        except RuntimeError as e:
                            st.error(str(e))

        # ── ISO ────────────────────────────────────────────
        with st.expander("📋 ISO 인증", expanded=False):
            for iso_name, iso_info in ISO_DATA.items():
                st.markdown(f"**{iso_name}** — 다음 심사: `{iso_info['next_audit']}`")
                c1, c2 = st.columns(2)
                cert_period = f'{iso_info["cert_start"]} ~ {iso_info["cert_end"]}'
                doc_dl = _deadline(iso_info["next_audit"], -45)

                with c1:
                    subj, html = iso_d60(
                        iso_type=iso_name,
                        audit_date=iso_info["next_audit"],
                        cert_no=iso_info["cert_no"],
                        cert_period=cert_period,
                        doc_deadline=doc_dl,
                    )
                    st.html('<div style="background:#F5F5F7;border-radius:12px;padding:12px 14px;font-size:12px;font-weight:700;color:#1D1D1F;">📢 심사 2개월 전 공지</div>')
                    with st.expander("📧 미리보기"):
                        st.components.v1.html(html.replace("[[NAME]]","수신자").replace("[[DEPT]]","담당부서"), height=480, scrolling=True)
                    if st.button("📤 발송", key=f"send_{iso_name}_60", use_container_width=True,
                                 type="primary", disabled=not smtp_ready() or not selected_recipients):
                        with st.spinner("발송 중..."):
                            try:
                                fails = send_emails(get_smtp(), selected_recipients, subj, html)
                                sent = len(selected_recipients) - len(fails)
                                st.success(f"✅ {sent}명 발송 완료.") if not fails else st.warning(f"일부 실패: {fails}")
                            except RuntimeError as e:
                                st.error(str(e))

                with c2:
                    from datetime import datetime as _dt
                    ad = _dt.strptime(iso_info["next_audit"], "%Y-%m-%d").date()
                    int_d = str(ad - timedelta(days=28))
                    subj2, html2 = iso_d30(iso_name, iso_info["next_audit"], int_d)
                    st.html('<div style="background:#F5F5F7;border-radius:12px;padding:12px 14px;font-size:12px;font-weight:700;color:#1D1D1F;">📋 심사 1개월 전 내부심사 안내</div>')
                    with st.expander("📧 미리보기"):
                        st.components.v1.html(html2.replace("[[NAME]]","수신자").replace("[[DEPT]]","담당부서"), height=480, scrolling=True)
                    if st.button("📤 발송", key=f"send_{iso_name}_30", use_container_width=True,
                                 type="primary", disabled=not smtp_ready() or not selected_recipients):
                        with st.spinner("발송 중..."):
                            try:
                                fails = send_emails(get_smtp(), selected_recipients, subj2, html2)
                                sent = len(selected_recipients) - len(fails)
                                st.success(f"✅ {sent}명 발송 완료.") if not fails else st.warning(f"일부 실패: {fails}")
                            except RuntimeError as e:
                                st.error(str(e))

                st.html('<hr style="border:none;border-top:1px solid #E8E8ED;margin:10px 0;"/>')

        # ── EL ─────────────────────────────────────────────
        el_df = load_el()
        with st.expander("♻️ 환경표지인증 (EL)", expanded=False):
            if el_df.empty:
                st.info("EL 데이터를 불러올 수 없습니다.")
            else:
                el_df["_dday"] = el_df["인증종료일"].apply(calc_dday)
                el_df_sorted   = el_df.sort_values("_dday").reset_index(drop=True)
                for _, row in el_df_sorted.iterrows():
                    prod_name = row.get("제품명(상표명)", "")
                    cert_end  = str(row.get("인증종료일", ""))[:10]
                    apply_dl  = str(
                        (pd.to_datetime(cert_end) - pd.Timedelta(days=90)).date()
                    ) if cert_end else "-"
                    dday_val  = row.get("_dday")
                    dday_str  = dday_label(dday_val) if dday_val is not None else "-"

                    with st.container():
                        st.html(
                            f'<div style="background:#F5F5F7;border-radius:12px;padding:12px 16px;margin:4px 0;">'
                            f'<span style="font-size:13px;font-weight:600;color:#1D1D1F;">{prod_name}</span>'
                            f'<span style="font-size:13px;color:#6E6E73;margin-left:8px;">만료 {cert_end} · {dday_str}</span>'
                            f'</div>'
                        )
                        subj_el, html_el = el_d60(
                            product_name=prod_name, cert_end=cert_end, apply_deadline=apply_dl
                        )
                        c_prev, c_send = st.columns([3, 1])
                        with c_prev.expander("📧 미리보기"):
                            st.components.v1.html(
                                html_el.replace("[[NAME]]","수신자").replace("[[DEPT]]","담당부서"),
                                height=480, scrolling=True
                            )
                        key_el = f"send_el_{prod_name[:8]}"
                        if c_send.button("📤 발송", key=key_el, use_container_width=True,
                                         type="primary", disabled=not smtp_ready() or not selected_recipients):
                            with st.spinner("발송 중..."):
                                try:
                                    fails = send_emails(get_smtp(), selected_recipients, subj_el, html_el)
                                    sent = len(selected_recipients) - len(fails)
                                    st.success(f"✅ {sent}명 발송 완료.") if not fails else st.warning(f"일부 실패: {fails}")
                                except RuntimeError as e:
                                    st.error(str(e))

        # ── Vegan ──────────────────────────────────────────
        with st.expander("🌱 Vegan 인증", expanded=False):
            for vegan_name, vegan_info in VEGAN_DATA.items():
                cert_end_v  = vegan_info["cert_end"]
                apply_dl_v  = str(
                    (pd.to_datetime(cert_end_v) - pd.Timedelta(days=60)).date()
                )
                dday_v = calc_dday(cert_end_v)
                st.html(
                    f'<div style="background:#F5F5F7;border-radius:12px;padding:12px 16px;margin:4px 0;">'
                    f'<span style="font-size:13px;font-weight:600;color:#1D1D1F;">{vegan_name}</span>'
                    f'<span style="font-size:13px;color:#6E6E73;margin-left:8px;">만료 {cert_end_v} · {dday_label(dday_v)}</span>'
                    f'</div>'
                )
                subj_v, html_v = vegan_d60(
                    cert_type=vegan_name,
                    product_scope=vegan_info["scope"],
                    cert_end=cert_end_v,
                    apply_deadline=apply_dl_v,
                )
                c_prev2, c_send2 = st.columns([3, 1])
                with c_prev2.expander("📧 미리보기"):
                    st.components.v1.html(
                        html_v.replace("[[NAME]]","수신자").replace("[[DEPT]]","담당부서"),
                        height=480, scrolling=True
                    )
                key_v = f"send_vegan_{vegan_name[:6]}"
                if c_send2.button("📤 발송", key=key_v, use_container_width=True,
                                   type="primary", disabled=not smtp_ready() or not selected_recipients):
                    with st.spinner("발송 중..."):
                        try:
                            fails = send_emails(get_smtp(), selected_recipients, subj_v, html_v)
                            sent = len(selected_recipients) - len(fails)
                            st.success(f"✅ {sent}명 발송 완료.") if not fails else st.warning(f"일부 실패: {fails}")
                        except RuntimeError as e:
                            st.error(str(e))
                st.html('<hr style="border:none;border-top:1px solid #E8E8ED;margin:10px 0;"/>')
