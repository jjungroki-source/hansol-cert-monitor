import streamlit as st
from utils.dday import calc_dday, get_alert_level, ALERT_COLORS, ALERT_LABELS, dday_label

st.title("3. ISO 인증")
st.caption("ISO 9001 · ISO 14001 인증 현황 및 심사 일정")
st.markdown('---')

# ── 인증 소개 ──────────────────────────────────────────────
st.html(
    """
    <div style="background:#F5F5F7;border-left:3px solid #FF9500;border-radius:0 16px 16px 0;
                padding:20px 24px;margin-bottom:24px;">
        <div style="margin-bottom:10px;">
            <span style="font-size:15px;font-weight:700;color:#1D1D1F;">ISO 인증</span>
            <span style="font-size:12px;color:#6E6E73;margin-left:8px;">International Organization for Standardization · 국제표준화기구</span>
        </div>
        <div style="font-size:13px;color:#3D3D3D;line-height:1.85;margin-bottom:14px;">
            기업이 해당 표준의 <strong>경영시스템을 구축·운영</strong>하고 있음을 제3자 인증기관(CB)이 공식 인정하는 제도입니다.<br>
            <strong style="color:#FF9500;">ISO 9001</strong> — <strong>품질경영시스템</strong>. 제품·서비스의 일관된 품질 보증 체계 구축 및 고객 만족 향상.<br>
            <strong style="color:#FF9500;">ISO 14001</strong> — <strong>환경경영시스템</strong>. 환경 영향 최소화, 탄소 저감·폐기물 관리·에너지 효율화 등 지속적 환경 성과 개선.
        </div>
        <div style="border-top:1px solid #E8E8ED;padding-top:12px;display:flex;flex-wrap:wrap;gap:8px;font-size:12px;">
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">📅 유효기간 <strong>3년</strong></span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🔍 사후심사 <strong>연 1회</strong> (1·2차)</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🔄 갱신심사 <strong>3년 후</strong></span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🏢 국내 인정기관: KAB</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🌍 공공조달·글로벌 바이어 사실상 필수</span>
        </div>
    </div>
    """,
)

# ── 인증별 메타 정보 ──────────────────────────────────────
ISO_INFO = {
    "ISO 9001": {
        "subtitle": "품질경영시스템",
        "icon": "🏆",
        "color": "#007AFF",
        "description": (
            "ISO 9001은 국제표준화기구(ISO)가 제정한 **품질경영시스템** 국제규격입니다. "
            "고객 만족 향상과 지속적인 품질 개선을 목적으로 하며, "
            "제품·서비스의 일관된 품질 보증 체계를 구축하는 데 활용됩니다."
        ),
        "renewal_cycle": "3년",
        "surveillance_cycle": "연 1회 (매년)",
        "issuer": "인정기관 인정 심사기관 (예: KR, SGS 등)",
        "cert_no": "QMS-2022-00123",
        "cert_start": "2022-09-01",
        "cert_end": "2025-08-31",
        "last_audit": "2024-09-05",
        "last_audit_type": "사후심사 1차",
        "next_audit": "2025-09-01",
        "next_audit_type": "사후심사 2차",
        "scope": "인쇄용지, 복사용지, 특수지 제조 및 품질관리",
    },
    "ISO 14001": {
        "subtitle": "환경경영시스템",
        "icon": "🌍",
        "color": "#34C759",
        "description": (
            "ISO 14001은 국제표준화기구(ISO)가 제정한 **환경경영시스템** 국제규격입니다. "
            "조직의 환경 영향을 체계적으로 관리하고 환경 성과를 지속적으로 개선하기 위한 "
            "프레임워크를 제공하며, 탄소 저감·폐기물 관리·에너지 효율화 등을 포함합니다."
        ),
        "renewal_cycle": "3년",
        "surveillance_cycle": "연 1회 (매년)",
        "issuer": "인정기관 인정 심사기관 (예: KR, Bureau Veritas 등)",
        "cert_no": "EMS-2023-00456",
        "cert_start": "2023-03-15",
        "cert_end": "2026-03-14",
        "last_audit": "2024-03-20",
        "last_audit_type": "사후심사 1차",
        "next_audit": "2025-03-15",
        "next_audit_type": "사후심사 2차",
        "scope": "천안공장 제지 생산 전 공정의 환경경영 활동",
    },
}

# ── 선택 카드 ─────────────────────────────────────────────
col1, col2, col3 = st.columns([3, 3, 4])
selected = st.session_state.get("iso_selected", None)

for key_name, col in [("ISO 9001", col1), ("ISO 14001", col2)]:
    info   = ISO_INFO[key_name]
    is_sel = (selected == key_name)
    border = f"2px solid {info['color']}" if is_sel else "1px solid #D2D2D7"
    shadow = "0 4px 12px rgba(0,0,0,0.10)" if is_sel else "0 1px 3px rgba(0,0,0,0.06)"
    col.html(
        f'<div style="background:#FFFFFF;border:{border};border-radius:16px;'
        f'padding:20px;height:116px;display:flex;flex-direction:column;'
        f'justify-content:space-between;box-shadow:{shadow};">'
        f'<div style="font-size:22px;">{info["icon"]}</div>'
        f'<div>'
        f'<div style="font-size:15px;font-weight:700;color:{info["color"]};letter-spacing:-0.2px;">{key_name}</div>'
        f'<div style="font-size:13px;color:#6E6E73;margin-top:2px;">{info["subtitle"]}</div>'
        f'</div>'
        f'</div>',
    )
    if col.button("선택", key=f"btn_{key_name.replace(' ','_')}", use_container_width=True):
        st.session_state["iso_selected"] = key_name
        st.rerun()

# ── 선택된 인증 상세 ──────────────────────────────────────
if selected and selected in ISO_INFO:
    st.markdown('---')
    info  = ISO_INFO[selected]
    color = info["color"]

    st.html(
        f'<div style="background:#F5F5F7;border-left:3px solid {color};'
        f'border-radius:0 14px 14px 0;padding:14px 20px;margin-bottom:20px;">'
        f'<span style="font-size:18px;">{info["icon"]}</span> '
        f'<span style="font-size:17px;font-weight:700;color:{color};margin-left:6px;">'
        f'{selected} — {info["subtitle"]}</span></div>',
    )

    st.markdown("##### 📌 인증 개요")
    st.markdown(info['description'])

    # D-day 계산
    next_audit_dday = calc_dday(info["next_audit"])
    cert_end_dday   = calc_dday(info["cert_end"])
    audit_level     = get_alert_level(next_audit_dday)
    cert_level      = get_alert_level(cert_end_dday)
    audit_color     = ALERT_COLORS[audit_level]
    cert_color_     = ALERT_COLORS[cert_level]

    # 현황 카드 4개 (균일 높이)
    st.markdown("##### 📋 인증 현황")
    k1, k2, k3, k4 = st.columns(4)

    def mini_card(col, label, value, sub, accent=None):
        bg = f"{accent}0E" if accent else "#F5F5F7"
        vc = accent if accent else "#1D1D1F"
        col.html(
            f'<div style="background:{bg};border:1px solid #D2D2D7;border-radius:16px;'
            f'padding:18px 16px;height:96px;display:flex;flex-direction:column;'
            f'justify-content:space-between;box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
            f'<div style="font-size:12px;color:#6E6E73;text-transform:uppercase;letter-spacing:0.4px;font-weight:500;">{label}</div>'
            f'<div style="font-size:16px;font-weight:700;color:{vc};line-height:1.2;overflow:hidden;'
            f'text-overflow:ellipsis;white-space:nowrap;">{value}</div>'
            f'<div style="font-size:12px;color:#8E8E93;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{sub}</div>'
            f'</div>',
        )

    mini_card(k1, "인증번호",  info["cert_no"],              info["issuer"][:16]+"…",      None)
    mini_card(k2, "인증 기간", info["cert_start"],           f"~ {info['cert_end']}",       color)
    mini_card(k3, "다음 심사", dday_label(next_audit_dday),  info["next_audit"],            audit_color)
    mini_card(k4, "인증 만료", dday_label(cert_end_dday),    info["cert_end"],              cert_color_)

    # 심사 주기 & 범위
    st.markdown("##### 🔄 심사 주기 및 범위")
    left, right = st.columns(2)

    with left:
        st.markdown(f"""
| 구분 | 내용 |
|------|------|
| 갱신심사 주기 | **{info["renewal_cycle"]}** |
| 사후심사 주기 | **{info["surveillance_cycle"]}** |
| 마지막 심사 | {info["last_audit"]} ({info["last_audit_type"]}) |
| 다음 심사 | **{info["next_audit"]}** ({info["next_audit_type"]}) |
| 심사기관 | {info["issuer"]} |
""")

    with right:
        st.html(
            f'<div style="background:#F5F5F7;border:1px solid #D2D2D7;border-radius:14px;padding:16px 18px;">'
            f'<div style="font-size:13px;color:#6E6E73;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.4px;">📍 인증 범위 (Scope)</div>'
            f'<div style="font-size:14px;color:#1D1D1F;line-height:1.7;">{info["scope"]}</div>'
            f'</div>',
        )

    # 심사 주기 타임라인
    st.markdown("##### 📅 심사 주기 흐름")
    st.html(
        f'<div style="display:flex;align-items:center;gap:0;margin:10px 0 20px 0;flex-wrap:wrap;">'
        f'<div style="background:{color};color:white;border-radius:10px;'
        f'padding:8px 16px;font-size:12px;font-weight:600;white-space:nowrap;">최초인증 / 갱신심사</div>'
        f'<div style="flex:1;min-width:30px;height:2px;background:{color}44;"></div>'
        f'<div style="background:#FFFFFF;border:1px solid {color};color:{color};border-radius:10px;'
        f'padding:8px 16px;font-size:12px;font-weight:600;white-space:nowrap;">사후심사 1차</div>'
        f'<div style="flex:1;min-width:30px;height:2px;background:{color}44;"></div>'
        f'<div style="background:#FFFFFF;border:1px solid {color};color:{color};border-radius:10px;'
        f'padding:8px 16px;font-size:12px;font-weight:600;white-space:nowrap;">사후심사 2차</div>'
        f'<div style="flex:1;min-width:30px;height:2px;background:{color}44;"></div>'
        f'<div style="background:{color};color:white;border-radius:10px;'
        f'padding:8px 16px;font-size:12px;font-weight:600;white-space:nowrap;">갱신심사 (3년)</div>'
        f'</div>',
    )

    # 인증서 보기
    st.markdown('---')
    cert_file = "data/certs/iso9001.svg" if selected == "ISO 9001" else "data/certs/iso14001.svg"
    with st.expander("📄 인증서 보기 (샘플)", expanded=False):
        st.caption("※ 실제 인증서 파일로 교체하여 사용하세요. 현재는 샘플 이미지입니다.")
        st.image(cert_file, use_container_width=True)

else:
    st.html(
        '<div style="text-align:center;color:#8E8E93;padding:48px 0;font-size:14px;">'
        '위에서 인증 항목을 선택하면 상세 정보가 표시됩니다.</div>',
    )
