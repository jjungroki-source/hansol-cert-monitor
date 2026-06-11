import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr


# ── SMTP 발송 ─────────────────────────────────────────────

def send_emails(smtp_cfg: dict, recipients: list, subject: str, html_body: str) -> list:
    """
    recipients: [{"name":..., "email":..., "department":...}, ...]
    Returns list of failure strings (empty = all succeeded).
    """
    failures = []
    from_addr = formataddr((smtp_cfg.get("sender_name", "품질환경팀"), smtp_cfg["user"]))

    try:
        with smtplib.SMTP(smtp_cfg["host"], int(smtp_cfg["port"]), timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_cfg["user"], smtp_cfg["password"])
            for r in recipients:
                try:
                    personalized = (
                        html_body
                        .replace("[[NAME]]", r["name"])
                        .replace("[[DEPT]]", r["department"])
                    )
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = subject
                    msg["From"]    = from_addr
                    msg["To"]      = formataddr((r["name"], r["email"]))
                    msg.attach(MIMEText(personalized, "html", "utf-8"))
                    server.sendmail(smtp_cfg["user"], [r["email"]], msg.as_string())
                except Exception as e:
                    failures.append(f"{r['name']} ({r['email']}): {e}")
    except Exception as e:
        raise RuntimeError(f"SMTP 연결 오류: {e}")

    return failures


def test_connection(smtp_cfg: dict) -> None:
    """Raises RuntimeError on failure."""
    with smtplib.SMTP(smtp_cfg["host"], int(smtp_cfg["port"]), timeout=8) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_cfg["user"], smtp_cfg["password"])


# ── HTML 공통 빌더 ────────────────────────────────────────

def _wrap(title: str, body: str, accent: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#F5F5F7;
             font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
  <div style="max-width:600px;margin:32px auto 48px;background:#FFFFFF;
              border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:{accent};padding:28px 32px;">
      <div style="font-size:13px;color:rgba(255,255,255,0.75);letter-spacing:0.7px;
                  text-transform:uppercase;margin-bottom:8px;">
        한솔제지(주) 천안공장 &nbsp;|&nbsp; 품질환경팀 품질관리
      </div>
      <div style="font-size:19px;font-weight:700;color:#FFFFFF;line-height:1.35;">{title}</div>
    </div>

    <!-- Body -->
    <div style="padding:32px 32px 24px;">{body}</div>

    <!-- Footer -->
    <div style="background:#F5F5F7;padding:20px 32px;border-top:1px solid #E8E8ED;">
      <div style="font-size:12px;color:#6E6E73;line-height:1.9;">
        <strong style="color:#1D1D1F;">담당</strong>&nbsp; 장정록 책임
        &nbsp;&nbsp;<strong style="color:#1D1D1F;">이메일</strong>&nbsp; jjr@hansol.com
        &nbsp;&nbsp;<strong style="color:#1D1D1F;">전화</strong>&nbsp; 041-000-0000
      </div>
      <div style="font-size:13px;color:#AEAEB2;margin-top:6px;">
        본 메일은 한솔제지(주) 천안공장 인증 모니터링 시스템에서 자동 발송되었습니다.
      </div>
    </div>

  </div>
</body>
</html>"""


def _greeting(extra: str = "") -> str:
    return (
        f'<p style="font-size:14px;color:#3D3D3D;line-height:1.85;margin:0 0 20px;">'
        f'안녕하세요, <strong>[[NAME]]</strong> 담당자님.<br>'
        f'한솔제지(주) 천안공장 품질환경팀 품질관리 <strong>장정록 책임</strong>입니다.'
        f'{(" " + extra) if extra else ""}</p>'
    )


def _info_table(rows: list) -> str:
    trs = ""
    for k, v in rows:
        trs += (
            f'<tr>'
            f'<td style="padding:10px 14px;font-size:12px;color:#6E6E73;font-weight:600;'
            f'white-space:nowrap;border-bottom:1px solid #F0F0F0;width:36%;">{k}</td>'
            f'<td style="padding:10px 14px;font-size:13px;color:#1D1D1F;'
            f'border-bottom:1px solid #F0F0F0;">{v}</td>'
            f'</tr>'
        )
    return (
        f'<table style="width:100%;border-collapse:collapse;background:#F5F5F7;'
        f'border-radius:12px;overflow:hidden;margin:0 0 20px;">{trs}</table>'
    )


def _section(heading: str, items: list) -> str:
    lis = "".join(
        f'<li style="margin:5px 0;color:#3D3D3D;font-size:13px;line-height:1.7;">{i}</li>'
        for i in items
    )
    return (
        f'<div style="margin:0 0 20px;">'
        f'<div style="font-size:13px;font-weight:700;color:#1D1D1F;'
        f'padding-bottom:7px;border-bottom:1px solid #E8E8ED;margin-bottom:10px;">{heading}</div>'
        f'<ul style="margin:0;padding-left:18px;">{lis}</ul>'
        f'</div>'
    )


def _callout(text: str, color: str, bg: str) -> str:
    return (
        f'<div style="background:{bg};border-left:3px solid {color};border-radius:0 10px 10px 0;'
        f'padding:14px 18px;margin:0 0 20px;font-size:13px;color:#3D3D3D;line-height:1.8;">'
        f'{text}</div>'
    )


def _closing() -> str:
    return (
        '<p style="font-size:13px;color:#6E6E73;line-height:1.85;margin:20px 0 0;">'
        '바쁘신 중에도 협조해 주셔서 진심으로 감사드립니다.<br>'
        '궁금하신 사항이 있으시면 언제든지 연락해 주시기 바랍니다.</p>'
    )


# ── FSC 사후심사 D-60 공지 ────────────────────────────────

def fsc_d60(audit_date: str, cert_no: str, cert_period: str, doc_deadline: str) -> tuple:
    subject = f"[FSC CoC 인증] 사후심사 일정 사전 안내 · 심사 예정일 {audit_date}"
    body = (
        _greeting("오는 FSC CoC 인증 사후심사 일정과 관련하여 사전 안내 드립니다.")
        + _info_table([
            ("심사 유형",   "FSC CoC 사후심사 (연 1회)"),
            ("심사 예정일", f"<strong>{audit_date}</strong>"),
            ("인증번호",    cert_no),
            ("인증 기간",   cert_period),
            ("심사기관",    "SGS Korea"),
        ])
        + _section("주요 준비사항 안내", [
            "FSC 인증 원료 구매·생산·판매 서류 최신 정리",
            "공급사 인증 유효성 사전 확인 (info.fsc.org 조회)",
            "COC 교육훈련 기록 업데이트",
            "근로자 관련 서류 최신화 (취업규칙·교육기록·명부·근로계약서)",
            "상표사용 승인 이메일 및 홍보물 샘플 파일 확인",
            "인증제품군별 전환계수 증빙 자료 점검",
        ])
        + _section(f"[[DEPT]] 담당자 협조 요청 사항 — 제출 기한: {doc_deadline}", [
            "담당 제품군 구매·생산·판매 실적 자료 (전년도 ~ 현재)",
            "담당자 FSC 관련 교육 이수 현황 (교육일, 교육명, 이수자 명단)",
            "인증 원료 공급사 관련 추가 서류 (해당 부서 한함)",
        ])
        + _callout(
            "⏰ &nbsp;심사 일정 변경 또는 담당자 부재가 예상되는 경우, "
            "반드시 사전에 품질환경팀으로 연락해 주시기 바랍니다.",
            "#FF9500", "#FFF8EF"
        )
        + _closing()
    )
    return subject, _wrap("FSC CoC 인증 사후심사 일정 안내 (D-60)", body, "#34C759")


# ── FSC 내부심사 D-30 안내 ────────────────────────────────

def fsc_d30(audit_date: str, internal_date: str) -> tuple:
    subject = f"[FSC CoC 인증] 내부심사 일정 안내 및 자료 요청 · 외부심사 {audit_date}"
    body = (
        _greeting(
            f"FSC CoC 인증 사후심사({audit_date})가 한 달 앞으로 다가왔습니다. "
            "내부심사 일정 및 필요 자료 요청 사항을 안내 드립니다."
        )
        + _info_table([
            ("외부 심사 예정일", f"<strong>{audit_date}</strong>"),
            ("내부심사 예정일", f"<strong>{internal_date}</strong>"),
            ("심사기관",         "SGS Korea"),
        ])
        + _section("내부심사 전 필수 제출 자료 (부서별)", [
            "연간실적 요약서 (최신 업데이트본)",
            "인증원료 공급사 목록 및 인증 유효성 증명 서류 (전량)",
            "펄프원료 수종 정보 (학명 포함) 최신 자료",
            "자체평가서 GP4521B — 작성 완료 후 제출",
            "매출액 자기선언서 GP4523",
            "부적합 사항 발생 시 시정조치 완료 증빙 서류",
        ])
        + _section("내부심사 당일 확인 사항", [
            "현장 인증 원료 보관 상태 및 표식 점검",
            "인증 마크 사용 적정성 (허가 범위 내 사용 여부) 확인",
            "직원 인터뷰 대비 — COC 절차 및 역할 숙지 당부",
            "외주 협력업체 관련 계약서·협약서 비치 확인",
        ])
        + _callout(
            "⚠️ &nbsp;내부심사에서 발견된 <strong>부적합 사항은 외부 심사 전까지 반드시 시정조치를 완료</strong>하여 "
            "증빙 서류와 함께 품질환경팀에 제출해 주시기 바랍니다.",
            "#FF3B30", "#FFF2F1"
        )
        + _closing()
    )
    return subject, _wrap("FSC CoC 인증 내부심사 안내 및 자료 요청 (D-30)", body, "#34C759")


# ── ISO 사후심사 D-60 공지 ────────────────────────────────

def iso_d60(iso_type: str, audit_date: str, cert_no: str, cert_period: str, doc_deadline: str) -> tuple:
    is_9001  = "9001" in iso_type
    accent   = "#007AFF" if is_9001 else "#34C759"
    sys_name = "품질경영시스템(QMS)" if is_9001 else "환경경영시스템(EMS)"
    specifics = (
        [
            "제품·공정 품질 기록 및 고객 불만 처리 현황 정리",
            "내부심사 지적 사항 시정조치 완료 여부 확인",
            "경영검토 회의록 및 품질 목표 달성 현황 업데이트",
            "공정별 모니터링·측정 기록 최신화",
            "납품처 요구사항 및 고객 만족도 관련 자료 정리",
        ] if is_9001 else [
            "환경 목표 및 추진계획 달성 현황 정리",
            "환경 측면·영향 평가 및 법규 준수 현황 최신화",
            "폐기물 관리 대장 및 외부 반출 기록 정리",
            "에너지·용수·원자재 사용 실적 데이터 취합",
            "환경 사고·아차사고 발생 이력 및 조치 기록 확인",
        ]
    )
    subject = f"[{iso_type}] 사후심사 일정 사전 안내 · 심사 예정일 {audit_date}"
    body = (
        _greeting(f"오는 {iso_type} {sys_name} 사후심사 일정을 안내 드립니다.")
        + _info_table([
            ("심사 유형",   f"{iso_type} {sys_name} 사후심사"),
            ("심사 예정일", f"<strong>{audit_date}</strong>"),
            ("인증번호",    cert_no),
            ("인증 기간",   cert_period),
        ])
        + _section("주요 준비사항 안내", specifics)
        + _section(f"[[DEPT]] 담당자 협조 요청 사항 — 제출 기한: {doc_deadline}", [
            "관련 기록 및 실적 데이터 취합·제출",
            "현장 점검 대비 (정리·정돈, 안전표식 등)",
            "담당자 시스템 절차 숙지 (인터뷰 대비)",
        ])
        + _callout(
            "⏰ &nbsp;심사 일정 변경 또는 담당자 부재가 예상되는 경우, "
            "반드시 사전에 품질환경팀으로 연락해 주시기 바랍니다.",
            "#FF9500", "#FFF8EF"
        )
        + _closing()
    )
    return subject, _wrap(f"{iso_type} 사후심사 일정 안내 (D-60)", body, accent)


# ── ISO 내부심사 D-30 안내 ────────────────────────────────

def iso_d30(iso_type: str, audit_date: str, internal_date: str) -> tuple:
    is_9001 = "9001" in iso_type
    accent  = "#007AFF" if is_9001 else "#34C759"
    subject = f"[{iso_type}] 내부심사 일정 안내 및 자료 요청 · 외부심사 {audit_date}"
    body = (
        _greeting(
            f"{iso_type} 사후심사({audit_date})가 한 달 앞으로 다가왔습니다. "
            "내부심사 일정 및 필요 자료 요청 사항을 안내 드립니다."
        )
        + _info_table([
            ("외부 심사 예정일", f"<strong>{audit_date}</strong>"),
            ("내부심사 예정일",  f"<strong>{internal_date}</strong>"),
        ])
        + _section("내부심사 전 공통 제출 자료", [
            "최신 절차서·작업지시서 비치 및 개정 이력 확인",
            "교육훈련 기록 (최근 1년, 담당자 전원)",
            "이전 내부심사 부적합 사항 시정조치 완료 확인서",
            "목표 및 추진계획 달성 현황 (해당 부서 분)",
        ])
        + _callout(
            f"ℹ️ &nbsp;내부심사 세부 일정 및 체크리스트는 별도 공유 드릴 예정입니다. "
            "심사 당일 담당자 부재 시 반드시 <strong>사전에 품질환경팀으로 연락</strong>해 주시기 바랍니다.",
            "#007AFF", "#F0F7FF"
        )
        + _closing()
    )
    return subject, _wrap(f"{iso_type} 내부심사 안내 및 자료 요청 (D-30)", body, accent)


# ── 환경표지인증(EL) 갱신 D-60 안내 ──────────────────────

def el_d60(product_name: str, cert_end: str, apply_deadline: str) -> tuple:
    subject = f"[환경표지인증] 갱신 일정 안내 · {product_name} · 만료 {cert_end}"
    body = (
        _greeting("관리 중인 환경표지인증 제품의 갱신 기한이 약 2개월 앞으로 다가왔습니다.")
        + _info_table([
            ("인증 제품",            f"<strong>{product_name}</strong>"),
            ("인증 만료일",          f"<strong>{cert_end}</strong>"),
            ("갱신 신청 권장 기한",  f"<strong>{apply_deadline}</strong>"),
            ("발급기관",             "한국환경산업기술원 (KEITI)"),
            ("신청 사이트",          "el.keiti.re.kr"),
        ])
        + _section("갱신 필수 준비 서류", [
            "인증 신청서 (KEITI 양식 — el.keiti.re.kr 다운로드)",
            "제품 시험성적서 — 유효기간 내, KEITI 지정 시험기관 발행본",
            "제품 설명서 및 카탈로그 (최신본)",
            "공정 흐름도 (원료 투입 → 완제품 출하 전 과정)",
            "원부자재 목록 및 함량 정보 (전 원료 포함)",
            "사업자등록증 및 공장등록증 사본",
        ])
        + _section("갱신 신청 절차 (KEITI)", [
            "KEITI 환경표지 인증시스템 접속 (el.keiti.re.kr)",
            "갱신 신청서 작성 및 서류 업로드",
            "심사 수수료 납부 후 접수 완료",
            "KEITI 서류심사 → 현장심사 → 인증서 발급 (통상 4~6주 소요)",
        ])
        + _callout(
            "⚠️ &nbsp;인증 <strong>만료 후에는 환경표지 마크 사용이 즉시 금지</strong>되며, "
            "공공기관 우선구매 혜택이 상실됩니다. "
            "만료 <strong>90일 전 갱신 신청</strong>을 적극 권장드립니다.",
            "#FF3B30", "#FFF2F1"
        )
        + _closing()
    )
    return subject, _wrap("환경표지인증 갱신 일정 안내 (D-60)", body, "#007AFF")


# ── Vegan 인증 갱신 D-60 안내 ────────────────────────────

def vegan_d60(cert_type: str, product_scope: str, cert_end: str, apply_deadline: str) -> tuple:
    is_kv  = "KV" in cert_type or "한국" in cert_type
    accent = "#AF52DE"
    issuer = "한국비건인증원 (KV)" if is_kv else "The Vegan Society (영국)"
    subject = f"[Vegan 인증] 갱신 일정 안내 · {cert_type} · 만료 {cert_end}"
    body = (
        _greeting(f"관리 중인 {cert_type} 인증의 갱신 기한이 약 2개월 앞으로 다가왔습니다.")
        + _info_table([
            ("인증 기관",           issuer),
            ("인증 범위",           product_scope),
            ("인증 만료일",         f"<strong>{cert_end}</strong>"),
            ("갱신 신청 권장 기한", f"<strong>{apply_deadline}</strong>"),
        ])
        + _section("갱신 필수 준비 서류", [
            "인증 신청서 (해당 기관 최신 양식)",
            "제품 원료 전체 목록 및 함량 명세 (동물 유래 성분 부재 증명)",
            "원료 공급사 비건 적합성 확인서 또는 성분 명세서",
            "제조 공정 흐름도 (교차 오염 방지 공정 포함)",
            "동물 실험 미수행 확인서 (자사 + 주요 원료 공급사)",
            "제품 라벨·포장재 샘플 (최신 디자인 적용본)",
        ])
        + _section("갱신 시 주요 체크사항", [
            "원료 변경 이력 확인 — 신규 원료 사용 시 사전 비건 적합성 검토 필수",
            "공급사 변경 시 해당 공급사 비건 적합성 재확인",
            "인증 마크 디자인·가이드라인 최신 버전 적용 여부 확인",
            "해외 수출용(TVS)의 경우 — 유럽 바이어 요구사항 사전 협의 권장",
        ])
        + _callout(
            "ℹ️ &nbsp;Vegan 인증은 <strong>원료 변경 시 즉시 인증기관에 신고</strong>하여야 하며, "
            "승인 없이 변경 원료를 사용하면 인증이 취소될 수 있습니다.",
            "#AF52DE", "#F9F0FF"
        )
        + _closing()
    )
    return subject, _wrap(f"{cert_type} 갱신 일정 안내 (D-60)", body, accent)
