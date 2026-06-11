import streamlit as st
from utils.dday import calc_dday, get_alert_level, ALERT_COLORS, ALERT_LABELS, dday_label


st.title("4. Vegan 인증")
st.caption("비건 인증 현황 및 심사 일정")
st.markdown('---')

# ── 인증 소개 ──────────────────────────────────────────────
st.html(
    """
    <div style="background:#F5F5F7;border-left:3px solid #AF52DE;border-radius:0 16px 16px 0;
                padding:20px 24px;margin-bottom:24px;">
        <div style="margin-bottom:10px;">
            <span style="font-size:15px;font-weight:700;color:#1D1D1F;">Vegan 인증</span>
            <span style="font-size:12px;color:#6E6E73;margin-left:8px;">비건 인증 · 동물 유래 성분 및 동물 실험 미사용 검증</span>
        </div>
        <div style="font-size:13px;color:#3D3D3D;line-height:1.85;margin-bottom:14px;">
            제품의 원료·제조 공정 전 과정에서 <strong>동물 유래 성분을 사용하지 않고, 동물 실험을 수행하지 않았음</strong>을
            제3자 기관이 인증하는 제도입니다.<br>
            종이·포장재 분야에서는 주로 <strong>동물성 접착제·코팅제 미사용</strong> 여부를 검증하며,
            비건·친환경 소비 트렌드 확산에 따라 유럽·북미 바이어의 요구가 증가하는 추세입니다.
        </div>
        <div style="border-top:1px solid #E8E8ED;padding-top:12px;display:flex;flex-wrap:wrap;gap:8px;font-size:12px;">
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🚫 동물성 원료·실험 미사용</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">📅 유효기간 <strong>1~2년</strong> (기관마다 상이)</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🔄 갱신 시 원료 변경 재검토</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🇰🇷 한국비건인증원 (KV)</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🇬🇧 The Vegan Society (영국)</span>
            <span style="background:#FFFFFF;border:1px solid #D2D2D7;border-radius:20px;padding:3px 12px;color:#3D3D3D;">🌍 유럽·북미 수출 바이어 요구 대응</span>
        </div>
    </div>
    """,
)

# ── 인증 항목 정보 ─────────────────────────────────────────
VEGAN_INFO = {
    "한국비건인증원 (KV)": {
        "icon": "🇰🇷",
        "color": "#AF52DE",
        "description": "한국비건인증원(KV)은 국내 대표 비건 인증기관으로, 원료·제조공정·동물실험 여부를 종합 심사합니다. 국내 유통 및 공공조달 입찰 시 활용도가 높습니다.",
        "renewal_cycle": "1년",
        "surveillance_cycle": "해당 없음 (갱신 시 재심사)",
        "cert_no": "KV-2024-00789",
        "cert_start": "2024-05-01",
        "cert_end": "2025-04-30",
        "last_audit": "2024-05-01",
        "last_audit_type": "최초 인증심사",
        "next_audit": "2025-04-01",
        "next_audit_type": "갱신심사",
        "scope": "친환경 복사용지, 포장박스 (동물성 원료 미사용 검증)",
        "issuer": "한국비건인증원 (KV)",
    },
    "The Vegan Society (영국)": {
        "icon": "🇬🇧",
        "color": "#34C759",
        "description": "The Vegan Society는 1944년 영국에서 설립된 세계 최초의 비건 단체로, 'Vegan Trademark' 인증을 운영합니다. 글로벌 인지도가 높아 유럽·북미 수출 제품에 유효합니다.",
        "renewal_cycle": "2년",
        "surveillance_cycle": "해당 없음 (갱신 시 재심사)",
        "cert_no": "TVS-2023-EU456",
        "cert_start": "2023-08-15",
        "cert_end": "2025-08-14",
        "last_audit": "2023-08-15",
        "last_audit_type": "최초 인증심사",
        "next_audit": "2025-07-15",
        "next_audit_type": "갱신심사",
        "scope": "수출용 친환경 인쇄용지 (유럽 바이어 요청 대응)",
        "issuer": "The Vegan Society (UK)",
    },
}

# ── 선택 카드 ─────────────────────────────────────────────
selected = st.session_state.get("vegan_selected", None)
col1, col2, col3 = st.columns([3, 3, 4])

for idx, (name, info) in enumerate(VEGAN_INFO.items()):
    col    = col1 if idx == 0 else col2
    is_sel = (selected == name)
    border = f"2px solid {info['color']}" if is_sel else "1px solid #D2D2D7"
    shadow = "0 4px 12px rgba(0,0,0,0.10)" if is_sel else "0 1px 3px rgba(0,0,0,0.06)"
    col.html(
        f'<div style="background:#FFFFFF;border:{border};border-radius:16px;'
        f'padding:20px;height:116px;display:flex;flex-direction:column;'
        f'justify-content:space-between;box-shadow:{shadow};">'
        f'<div style="font-size:22px;">{info["icon"]}</div>'
        f'<div>'
        f'<div style="font-size:14px;font-weight:700;color:{info["color"]};letter-spacing:-0.2px;">{name}</div>'
        f'<div style="font-size:13px;color:#6E6E73;margin-top:2px;">유효기간 {info["renewal_cycle"]} · {info["cert_no"]}</div>'
        f'</div>'
        f'</div>',
    )
    if col.button("선택", key=f"btn_vegan_{idx}", use_container_width=True):
        st.session_state["vegan_selected"] = name
        st.rerun()

# ── 선택된 인증 상세 ──────────────────────────────────────
if selected and selected in VEGAN_INFO:
    st.markdown('---')
    info  = VEGAN_INFO[selected]
    color = info["color"]

    st.html(
        f'<div style="background:#F5F5F7;border-left:3px solid {color};'
        f'border-radius:0 14px 14px 0;padding:14px 20px;margin-bottom:20px;">'
        f'<span style="font-size:18px;">{info["icon"]}</span> '
        f'<span style="font-size:17px;font-weight:700;color:{color};margin-left:6px;">{selected}</span></div>',
    )

    st.markdown("##### 📌 인증 개요")
    st.markdown(info['description'])

    next_dday  = calc_dday(info["next_audit"])
    end_dday   = calc_dday(info["cert_end"])
    next_level = get_alert_level(next_dday)
    end_level  = get_alert_level(end_dday)
    next_color = ALERT_COLORS[next_level]
    end_color  = ALERT_COLORS[end_level]

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

    mini_card(k1, "인증번호",  info["cert_no"],       info["issuer"],            None)
    mini_card(k2, "인증 기간", info["cert_start"],    f"~ {info['cert_end']}",   color)
    mini_card(k3, "다음 심사", dday_label(next_dday), info["next_audit"],        next_color)
    mini_card(k4, "인증 만료", dday_label(end_dday),  info["cert_end"],          end_color)

    st.markdown("##### 🔄 심사 주기 및 범위")
    left, right = st.columns(2)
    with left:
        st.markdown(f"""
| 구분 | 내용 |
|------|------|
| 갱신심사 주기 | **{info["renewal_cycle"]}** |
| 사후심사 | {info["surveillance_cycle"]} |
| 마지막 심사 | {info["last_audit"]} ({info["last_audit_type"]}) |
| 다음 심사 | **{info["next_audit"]}** ({info["next_audit_type"]}) |
| 발급기관 | {info["issuer"]} |
""")
    with right:
        st.html(
            f'<div style="background:#F5F5F7;border:1px solid #D2D2D7;border-radius:14px;padding:16px 18px;">'
            f'<div style="font-size:13px;color:#6E6E73;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.4px;">📍 인증 범위 (Scope)</div>'
            f'<div style="font-size:14px;color:#1D1D1F;line-height:1.7;">{info["scope"]}</div>'
            f'</div>',
        )

    # 인증서 보기
    st.markdown('---')
    cert_file = "data/certs/vegan_kv.svg" if selected == "한국비건인증원 (KV)" else "data/certs/vegan_tvs.svg"
    with st.expander("📄 인증서 보기 (샘플)", expanded=False):
        st.caption("※ 실제 인증서 파일로 교체하여 사용하세요. 현재는 샘플 이미지입니다.")
        st.image(cert_file, use_container_width=True)

else:
    st.html(
        '<div style="text-align:center;color:#8E8E93;padding:48px 0;font-size:14px;">'
        '위에서 인증 항목을 선택하면 상세 정보가 표시됩니다.</div>',
    )
