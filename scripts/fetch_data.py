#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Récupère 6 mois de cours, normalise base 100 et écrit data.json à la racine du repo.
Lancé par GitHub Actions (voir .github/workflows/update.yml).
Dépendance : yfinance.
"""

import json
import os
from datetime import datetime, timezone
import yfinance as yf

# (ticker Yahoo, nom, groupe, couleur, repère gras)
SERIES = [
    ("MTSI",      "MACOM",       "rf",  "#00E5C7", True),
    ("QRVO",      "Qorvo",       "rf",  "#FFB000", False),
    ("SWKS",      "Skyworks",    "rf",  "#FF5470", False),
    ("WOLF",      "Wolfspeed",   "rf",  "#9D7CFF", False),
    ("ADI",       "Analog Dev.", "rf",  "#4DA3FF", False),
    ("QCOM",      "Qualcomm",    "rf",  "#6FE26F", False),
    ("NXPI",      "NXP",         "rf",  "#FF8C42", False),
    ("IFX.DE",    "Infineon",    "rf",  "#E36BE0", False),
    ("6981.T",    "Murata",      "rf",  "#C9D14B", False),
    ("AMS.SW",    "ams-OSRAM",   "rf",  "#5BD1E6", False),
    ("MU",        "Micron",      "mem", "#FFD23F", True),
    ("005930.KS", "Samsung",     "mem", "#7AA5FF", False),
    ("000660.KS", "SK Hynix",    "mem", "#FF6FA5", False),
    ("WDC",       "Western Dig.","mem", "#5AE0A0", False),
    ("285A.T",    "Kioxia",      "mem", "#C98BFF", False),
    ("2408.TW",   "Nanya",       "mem", "#FF9E5B", False),
    ("3105.TWO",  "WIN Semi",    "gan", "#8FE388", False),
]

PERIOD = "6mo"
OUT = os.path.join(os.path.dirname(__file__), "..", "data.json")


def build():
    series = []
    for tk, name, grp, col, hero in SERIES:
        try:
            df = yf.Ticker(tk).history(period=PERIOD, auto_adjust=True)
            s = df["Close"].dropna()
            if len(s) < 2:
                raise ValueError("serie vide")
            base = float(s.iloc[0])
            x = [int(ts.timestamp() * 1000) for ts in s.index]
            y = [round(float(v) / base * 100.0, 3) for v in s.values]
            pct = round(float(s.iloc[-1]) / base * 100.0 - 100.0, 2)
            series.append(dict(tk=tk, name=name, grp=grp, col=col,
                               hero=hero, pct=pct, x=x, y=y))
            print("  ok   %-10s %-13s %+6.1f%%" % (tk, name, pct))
        except Exception as e:
            print("  FAIL %-10s %-13s (%s)" % (tk, name, e))
    return series


def main():
    print("Recuperation des cours (Yahoo Finance)...")
    series = build()
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "period": PERIOD,
        "series": series,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print("Ecrit %s (%d valeurs)" % (os.path.normpath(OUT), len(series)))


if __name__ == "__main__":
    main()
