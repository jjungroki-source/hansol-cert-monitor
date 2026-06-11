from datetime import date, datetime
import pandas as pd


def calc_dday(target_date) -> int:
    """target_date까지 남은 일수 (음수면 경과)"""
    if pd.isna(target_date) or target_date is None:
        return None
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    return (target_date - date.today()).days


def get_alert_level(dday: int) -> str:
    """D-day 기반 알림 단계 반환"""
    if dday is None:
        return "unknown"
    if dday < 0:
        return "expired"     # 만료
    if dday <= 7:
        return "critical"    # D-7 이하
    if dday <= 30:
        return "warning"     # D-30 이하
    if dday <= 90:
        return "caution"     # D-90 이하
    return "normal"


ALERT_COLORS = {
    "expired":  "#FF3B30",
    "critical": "#FF3B30",
    "warning":  "#FF9500",
    "caution":  "#FF9F0A",
    "normal":   "#34C759",
    "unknown":  "#8E8E93",
}

ALERT_LABELS = {
    "expired":  "만료",
    "critical": "D-7 위험",
    "warning":  "D-30 경고",
    "caution":  "D-90 주의",
    "normal":   "정상",
    "unknown":  "정보없음",
}


def dday_label(dday: int) -> str:
    if dday is None:
        return "-"
    if dday == 0:
        return "D-Day"
    if dday > 0:
        return f"D-{dday}"
    return f"D+{abs(dday)}"
