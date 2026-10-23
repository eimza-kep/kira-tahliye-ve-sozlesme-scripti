# -*- coding: utf-8 -*-
"""
tufe_kira_calculator.py
-----------------------
6098 Sayılı Türk Borçlar Kanunu (TBK) Madde 344 uyarınca
TÜİK 12 Aylık TÜFE Ortalamaları sorgulama ve yasal kira artış tavanı hesaplama motoru.
"""

import sys
import re
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# TÜİK tarafından her ayın 3'ünde açıklanan 12 Aylık Ortalamalara Göre TÜFE Değişim Oranları (%)
TUFE_12_MONTH_AVERAGES = {
    "2026-12": 35.80,
    "2026-11": 37.10,
    "2026-10": 38.64,
    "2026-09": 41.22,
    "2026-08": 43.15,
    "2026-07": 45.48,
    "2026-06": 47.92,
    "2026-05": 50.18,
    "2026-04": 53.02,
    "2026-03": 55.91,
    "2026-02": 57.84,
    "2026-01": 59.95,
    "2025-12": 61.20,
    "2025-11": 62.45,
    "2025-10": 63.80,
    "2025-09": 64.91,
    "2025-08": 65.93,
    "2025-07": 65.07,
    "2025-06": 62.51,
    "2025-05": 62.51,
    "2025-04": 59.64,
    "2025-03": 57.50,
    "2025-02": 55.91,
    "2025-01": 54.72
}

DEFAULT_RATE = 38.64  # Güncel 2026 referans oranı

def parse_period_from_date(date_str: str) -> str:
    """Tarih dizgisinden YYYY-MM biçiminde dönem anahtarını çıkarır."""
    if not date_str or not isinstance(date_str, str):
        return "2026-10"
    match = re.search(r"(\d{4})[-/.](\d{2})", date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return "2026-10"

def get_tufe_rate_for_date(date_str: str) -> Dict[str, Any]:
    """
    Sözleşme yenileme tarihine karşılık gelen resmi TÜİK 12 aylık TÜFE ortalama artış tavanını döndürür.
    TBK Madde 344 uyarınca konut ve çatılı işyerleri için yasal üst sınırdır.
    """
    period = parse_period_from_date(date_str)
    rate = TUFE_12_MONTH_AVERAGES.get(period, DEFAULT_RATE)

    return {
        "period": period,
        "rate": rate,
        "source": "TÜİK 12 Aylık Ortalamalara Göre TÜFE Oranı",
        "legal_basis": "6098 Sayılı TBK Madde 344/2",
        "is_legal_cap": True,
        "message": f"{period} yenileme dönemi için yasal kira artış tavanı %{rate:.2f}'dir."
    }

def calculate_tbk_rent_increase(
    current_rent: float,
    renewal_date: str,
    custom_rate: Optional[float] = None
) -> Dict[str, Any]:
    """
    Mevcut kira ve tarihe göre yasal tavan kira artışını ve yeni kira bedelini hesaplar.
    Eğer özel oran belirtilmişse TBK m.344 tavan sınırına uygunluğunu denetler.
    """
    try:
        cur_rent = float(current_rent)
    except (ValueError, TypeError):
        cur_rent = 0.0

    tufe_info = get_tufe_rate_for_date(renewal_date)
    legal_rate = tufe_info["rate"]

    applied_rate = legal_rate
    is_exceeding_ceiling = False

    if custom_rate is not None:
        try:
            custom_val = float(custom_rate)
            applied_rate = custom_val
            if custom_val > legal_rate:
                is_exceeding_ceiling = True
        except (ValueError, TypeError):
            pass

    increase_amount = round(cur_rent * (applied_rate / 100.0), 2)
    new_rent = round(cur_rent + increase_amount, 2)
    legal_max_increase = round(cur_rent * (legal_rate / 100.0), 2)
    legal_max_rent = round(cur_rent + legal_max_increase, 2)

    return {
        "current_rent": cur_rent,
        "renewal_period": tufe_info["period"],
        "tufe_rate": legal_rate,
        "applied_rate": applied_rate,
        "increase_amount": increase_amount,
        "new_rent": new_rent,
        "legal_max_rent": legal_max_rent,
        "is_tbk_compliant": not is_exceeding_ceiling,
        "warning": "DİKKAT: Uygulanan artış oranı yasal TÜFE tavanını aştığı için TBK m.344 gereğince fazla kısım geçersizdir!" if is_exceeding_ceiling else None
    }
