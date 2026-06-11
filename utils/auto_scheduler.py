"""
자동 발송 스케줄러
- APScheduler BackgroundScheduler로 매일 오전 8시에 D-day 체크
- 각 인증별 D-90 / D-60 / D-30 / D-3 도달 시 해당 수신자에게 자동 발송
- data/send_log.json 으로 중복 발송 방지
- data/auto_send_config.json 에 SMTP 설정 및 활성화 여부 저장
"""

import json
import logging
from datetime import date, timedelta, datetime
from pathlib import Path

AUTO_CFG_PATH   = "data/auto_send_config.json"
SEND_LOG_PATH   = "data/send_log.json"
RECIPIENTS_PATH = "data/recipients.json"
FSC_PATH        = "data/fsc_schedule.json"
EL_PATH         = "data/el_sample.xlsx"

THRESHOLDS = [90, 60, 30, 3]

logger = logging.getLogger("auto_scheduler")


# ── config I/O ────────────────────────────────────────────

def load_auto_cfg() -> dict:
    try:
        with open(AUTO_CFG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"enabled": False, "hour": 8, "smtp": {}}


def save_auto_cfg(cfg: dict):
    Path(AUTO_CFG_PATH).write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ── send log I/O ──────────────────────────────────────────

def _load_log() -> dict:
    try:
        with open(SEND_LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"sent": [], "errors": []}


def _save_log(log: dict):
    Path(SEND_LOG_PATH).write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _already_sent(log: dict, key: str) -> bool:
    today = str(date.today())
    for e in log.get("sent", []):
        if e.get("key") == key and e.get("date") >= str(date.today() - timedelta(days=2)):
            return True
    return False


def _mark_sent(log: dict, key: str, subject: str):
    log.setdefault("sent", [])
    log["sent"] = [e for e in log["sent"] if e.get("key") != key]
    log["sent"].append({
        "key":     key,
        "date":    str(date.today()),
        "subject": subject,
        "time":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    log["sent"] = log["sent"][-300:]
    _save_log(log)


def _log_error(log: dict, key: str, error: str):
    log.setdefault("errors", [])
    log["errors"].append({
        "key":   key,
        "error": error,
        "time":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    log["errors"] = log["errors"][-100:]
    _save_log(log)


# ── D-day helper ─────────────────────────────────────────

def _dday(date_str: str):
    try:
        return (datetime.strptime(date_str, "%Y-%m-%d").date() - date.today()).days
    except Exception:
        return None


# ── 핵심 체크 함수 ────────────────────────────────────────

def run_daily_check():
    """매일 실행: 모든 인증의 D-day를 체크하고 해당되는 메일을 자동 발송."""
    cfg = load_auto_cfg()
    if not cfg.get("enabled"):
        return

    smtp_cfg = cfg.get("smtp", {})
    if not all([smtp_cfg.get("host"), smtp_cfg.get("user"), smtp_cfg.get("password")]):
        logger.warning("SMTP 설정이 불완전합니다. 자동 발송을 건너뜁니다.")
        return

    try:
        with open(RECIPIENTS_PATH, encoding="utf-8") as f:
            recipients = json.load(f).get("recipients", [])
    except Exception:
        logger.error("수신자 목록을 불러올 수 없습니다.")
        return

    if not recipients:
        return

    log = _load_log()

    from utils.email_sender import send_emails
    from utils.email_sender import (
        fsc_d90, fsc_d60, fsc_d30, fsc_d3,
        iso_d90, iso_d60, iso_d30, iso_d3,
        el_d90,  el_d60,  el_d3,
        vegan_d90, vegan_d60, vegan_d3,
    )

    def _send(log_key, subj, html):
        if _already_sent(log, log_key):
            return
        try:
            send_emails(smtp_cfg, recipients, subj, html)
            _mark_sent(log, log_key, subj)
            logger.info(f"발송 완료: {log_key}")
        except Exception as e:
            _log_error(log, log_key, str(e))
            logger.error(f"발송 실패 {log_key}: {e}")

    # ── FSC ───────────────────────────────────────────────
    try:
        with open(FSC_PATH, encoding="utf-8") as f:
            fsc_data = json.load(f)
        fsc_cert  = fsc_data["certification"]
        surv_date = fsc_cert["next_surveillance"]
        dday      = _dday(surv_date)
        cert_period = f'{fsc_cert["cert_start"]} ~ {fsc_cert["cert_end"]}'
        surv_dt = datetime.strptime(surv_date, "%Y-%m-%d").date()

        if dday == 90:
            s, h = fsc_d90(surv_date, fsc_cert["cert_no"], cert_period)
            _send(f"fsc_surv_d90_{surv_date}", s, h)
        elif dday == 60:
            doc_dl = str(surv_dt - timedelta(days=45))
            s, h = fsc_d60(surv_date, fsc_cert["cert_no"], cert_period, doc_dl)
            _send(f"fsc_surv_d60_{surv_date}", s, h)
        elif dday == 30:
            internal = str(surv_dt - timedelta(days=28))
            s, h = fsc_d30(surv_date, internal)
            _send(f"fsc_surv_d30_{surv_date}", s, h)
        elif dday == 3:
            s, h = fsc_d3(surv_date)
            _send(f"fsc_surv_d3_{surv_date}", s, h)
    except Exception as e:
        _log_error(log, "fsc", str(e))

    # ── ISO ───────────────────────────────────────────────
    ISO_DATA = {
        "ISO 9001":  {"cert_no": "QMS-2022-00123", "cert_start": "2022-09-01", "cert_end": "2025-08-31", "next_audit": "2025-09-01"},
        "ISO 14001": {"cert_no": "EMS-2023-00456", "cert_start": "2023-03-15", "cert_end": "2026-03-14", "next_audit": "2025-03-15"},
    }
    for iso_name, iso_info in ISO_DATA.items():
        try:
            audit_date  = iso_info["next_audit"]
            dday        = _dday(audit_date)
            cert_period = f'{iso_info["cert_start"]} ~ {iso_info["cert_end"]}'
            audit_dt    = datetime.strptime(audit_date, "%Y-%m-%d").date()
            tag         = iso_name.replace(" ", "_")

            if dday == 90:
                s, h = iso_d90(iso_name, audit_date, iso_info["cert_no"], cert_period)
                _send(f"{tag}_d90_{audit_date}", s, h)
            elif dday == 60:
                doc_dl = str(audit_dt - timedelta(days=45))
                s, h = iso_d60(iso_name, audit_date, iso_info["cert_no"], cert_period, doc_dl)
                _send(f"{tag}_d60_{audit_date}", s, h)
            elif dday == 30:
                internal = str(audit_dt - timedelta(days=28))
                s, h = iso_d30(iso_name, audit_date, internal)
                _send(f"{tag}_d30_{audit_date}", s, h)
            elif dday == 3:
                s, h = iso_d3(iso_name, audit_date)
                _send(f"{tag}_d3_{audit_date}", s, h)
        except Exception as e:
            _log_error(log, iso_name, str(e))

    # ── EL ────────────────────────────────────────────────
    try:
        import pandas as pd
        el_df = pd.read_excel(EL_PATH, dtype=str)
        for col in ["인증종료일"]:
            if col in el_df.columns:
                el_df[col] = pd.to_datetime(el_df[col], errors="coerce")

        for _, row in el_df.iterrows():
            prod_name = str(row.get("제품명(상표명)", "")).strip()
            cert_end_dt = row.get("인증종료일")
            if pd.isna(cert_end_dt) or not prod_name:
                continue
            cert_end = str(cert_end_dt.date())
            dday = _dday(cert_end)
            tag  = f"el_{prod_name[:12]}"

            if dday == 90:
                s, h = el_d90(prod_name, cert_end)
                _send(f"{tag}_d90_{cert_end}", s, h)
            elif dday == 60:
                apply_dl = str(cert_end_dt.date() - timedelta(days=90))
                s, h = el_d60(prod_name, cert_end, apply_dl)
                _send(f"{tag}_d60_{cert_end}", s, h)
            elif dday == 3:
                s, h = el_d3(prod_name, cert_end)
                _send(f"{tag}_d3_{cert_end}", s, h)
    except Exception as e:
        _log_error(log, "el", str(e))

    # ── Vegan ─────────────────────────────────────────────
    VEGAN_DATA = {
        "한국비건인증원 (KV)":    {"cert_end": "2025-04-30", "scope": "친환경 복사용지, 포장박스"},
        "The Vegan Society (영국)": {"cert_end": "2025-08-14", "scope": "수출용 친환경 인쇄용지"},
    }
    for vname, vinfo in VEGAN_DATA.items():
        try:
            cert_end = vinfo["cert_end"]
            dday     = _dday(cert_end)
            tag      = f"vegan_{vname[:8]}"
            apply_dl = str(
                datetime.strptime(cert_end, "%Y-%m-%d").date() - timedelta(days=60)
            )

            if dday == 90:
                s, h = vegan_d90(vname, vinfo["scope"], cert_end)
                _send(f"{tag}_d90_{cert_end}", s, h)
            elif dday == 60:
                s, h = vegan_d60(vname, vinfo["scope"], cert_end, apply_dl)
                _send(f"{tag}_d60_{cert_end}", s, h)
            elif dday == 3:
                s, h = vegan_d3(vname, cert_end)
                _send(f"{tag}_d3_{cert_end}", s, h)
        except Exception as e:
            _log_error(log, vname, str(e))


# ── Streamlit 앱에서 스케줄러 시작 ───────────────────────

_scheduler_started = False


def start_scheduler():
    """st.cache_resource 로 감싸서 앱 시작 시 1회만 실행."""
    global _scheduler_started
    if _scheduler_started:
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        cfg  = load_auto_cfg()
        hour = int(cfg.get("hour", 8))

        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(
            run_daily_check,
            trigger="cron",
            hour=hour,
            minute=0,
            id="daily_cert_check",
            replace_existing=True,
        )
        scheduler.start()
        _scheduler_started = True
        logger.info(f"스케줄러 시작 완료 — 매일 {hour:02d}:00 자동 발송 체크")
    except Exception as e:
        logger.error(f"스케줄러 시작 실패: {e}")
