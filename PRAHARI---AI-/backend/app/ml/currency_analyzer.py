"""Counterfeit Currency Identification Agent.

A deployable image-analysis pipeline (Pillow + NumPy, no GPU required) that a
field officer or bank teller can run on a phone/PoS capture. It extracts
physical/print features from the note image and evaluates them against
per-denomination reference profiles for the current Mahatma Gandhi (New) Series,
returning an explainable, per-check authenticity breakdown.

Checks modelled:
  - Aspect ratio vs. RBI dimensions
  - Dominant colour vs. denomination's characteristic base colour
  - Micro-print / intaglio proxy via high-frequency edge energy
  - Security-thread band detection (vertical high-contrast stripe)
  - Print-sharpness / focus (Laplacian variance)
  - Serial-number pattern validation (RBI format)
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from PIL import Image, ImageFilter

# RBI Mahatma Gandhi (New) Series reference profiles.
# size_ratio = width / height (RBI published note dimensions).
# base_rgb = characteristic dominant colour of the note.
DENOM_PROFILES = {
    10:   {"size_ratio": 123 / 63, "base_rgb": (176, 137, 92),  "name": "Chocolate Brown"},
    20:   {"size_ratio": 129 / 63, "base_rgb": (173, 190, 110), "name": "Greenish Yellow"},
    50:   {"size_ratio": 135 / 66, "base_rgb": (110, 170, 170), "name": "Fluorescent Blue"},
    100:  {"size_ratio": 142 / 66, "base_rgb": (150, 140, 180), "name": "Lavender"},
    200:  {"size_ratio": 146 / 66, "base_rgb": (210, 160, 90),  "name": "Bright Yellow-Orange"},
    500:  {"size_ratio": 150 / 66, "base_rgb": (140, 130, 120), "name": "Stone Grey"},
    2000: {"size_ratio": 166 / 66, "base_rgb": (190, 150, 190), "name": "Magenta"},
}

# RBI serial-number format: prefix = digit + two letters, then 6 digits.
SERIAL_RE = re.compile(r"^\d[A-Z]{2}\s?\d{6}$")


def _py(v):
    """Coerce NumPy scalars to native Python types for JSON/DB serialization."""
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


@dataclass
class Check:
    name: str
    passed: bool
    score: float          # 0..1 confidence this feature is authentic
    detail: str

    def as_dict(self):
        return {"name": self.name, "passed": bool(self.passed),
                "score": float(self.score), "detail": self.detail}


@dataclass
class CurrencyResult:
    denomination: int
    verdict: str          # genuine | suspect | counterfeit
    authenticity_score: float
    checks: list = field(default_factory=list)
    serial: Optional[str] = None
    serial_valid: Optional[bool] = None
    dominant_color: tuple = (0, 0, 0)
    recommendation: str = ""


def _laplacian_variance(gray: np.ndarray) -> float:
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    h, w = gray.shape
    # simple valid convolution
    out = (
        gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2] + gray[1:-1, 2:]
        - 4 * gray[1:-1, 1:-1]
    )
    return float(out.var())


def _high_freq_energy(gray: np.ndarray) -> float:
    gx = np.abs(np.diff(gray, axis=1)).mean()
    gy = np.abs(np.diff(gray, axis=0)).mean()
    return float((gx + gy) / 2.0)


def _detect_vertical_thread(gray: np.ndarray) -> float:
    """Security thread ~ a vertical band with locally high column contrast."""
    col_std = gray.std(axis=0)  # per-column vertical variation
    if col_std.size == 0:
        return 0.0
    # look in the central band where the thread usually sits
    w = col_std.size
    band = col_std[int(w * 0.30):int(w * 0.70)]
    peak = band.max() if band.size else 0.0
    baseline = np.median(col_std) + 1e-6
    return float(min(1.0, (peak / baseline) / 3.0))


class CurrencyAnalyzer:
    def analyze(self, image_bytes: bytes, denomination: int, serial: Optional[str] = None) -> CurrencyResult:
        profile = DENOM_PROFILES.get(denomination)
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size
        arr = np.asarray(img, dtype=np.float32)
        gray = arr.mean(axis=2)

        checks: list[Check] = []

        # 1) Aspect ratio
        ratio = (w / h) if h else 0
        expected = profile["size_ratio"] if profile else ratio
        ratio_err = abs(ratio - expected) / expected if expected else 1.0
        ar_score = max(0.0, 1.0 - ratio_err * 2.2)
        checks.append(Check(
            "Dimensional aspect ratio", ratio_err < 0.12, round(ar_score, 3),
            f"measured {ratio:.2f} vs RBI {expected:.2f} (Δ {ratio_err:.0%})"
        ))

        # 2) Dominant colour vs denomination base colour
        dom = tuple(int(x) for x in arr.reshape(-1, 3).mean(axis=0))
        if profile:
            dist = np.linalg.norm(np.array(dom) - np.array(profile["base_rgb"]))
            col_score = max(0.0, 1.0 - dist / 180.0)
            checks.append(Check(
                f"Base colour ({profile['name']})", col_score > 0.55, round(col_score, 3),
                f"dominant RGB {dom} vs expected {profile['base_rgb']}"
            ))
        else:
            col_score = 0.5

        # 3) Micro-print / intaglio proxy (high-frequency energy)
        hf = _high_freq_energy(gray)
        hf_score = min(1.0, hf / 18.0)   # genuine notes: dense fine print
        checks.append(Check(
            "Micro-print & intaglio texture", hf_score > 0.5, round(hf_score, 3),
            f"high-frequency edge energy {hf:.1f} (higher = finer print)"
        ))

        # 4) Security thread band
        thread = _detect_vertical_thread(gray)
        checks.append(Check(
            "Security thread band", thread > 0.5, round(thread, 3),
            f"central vertical-contrast peak ratio {thread:.2f}"
        ))

        # 5) Print sharpness / focus
        lap = _laplacian_variance(gray)
        sharp_score = min(1.0, lap / 900.0)
        checks.append(Check(
            "Print sharpness (Laplacian)", sharp_score > 0.4, round(sharp_score, 3),
            f"focus variance {lap:.0f}"
        ))

        # 6) Serial validation
        serial_valid = None
        if serial:
            serial = serial.strip().upper()
            serial_valid = bool(SERIAL_RE.match(serial))
            checks.append(Check(
                "Serial number format (RBI)", serial_valid, 1.0 if serial_valid else 0.0,
                f"'{serial}' {'matches' if serial_valid else 'violates'} RBI 1L2N-6D pattern"
            ))

        # Weighted authenticity score
        weights = {
            "Dimensional aspect ratio": 0.12,
            f"Base colour ({profile['name']})" if profile else "Base colour": 0.16,
            "Micro-print & intaglio texture": 0.26,
            "Security thread band": 0.22,
            "Print sharpness (Laplacian)": 0.12,
            "Serial number format (RBI)": 0.12,
        }
        total_w = sum(weights.get(c.name, 0.1) for c in checks)
        score = sum(c.score * weights.get(c.name, 0.1) for c in checks) / (total_w or 1)
        score = round(float(score), 3)

        if score >= 0.72:
            verdict = "genuine"
            rec = "PASS — features consistent with a genuine note. Clear for transaction."
        elif score >= 0.5:
            verdict = "suspect"
            rec = "HOLD — inconclusive. Re-scan under UV, verify security thread & watermark manually."
        else:
            verdict = "counterfeit"
            rec = "REJECT — multiple security features failed. Seize note, log serial, file under FICN protocol."

        return CurrencyResult(
            denomination=denomination,
            verdict=verdict,
            authenticity_score=score,
            checks=[c.as_dict() for c in checks],
            serial=serial,
            serial_valid=bool(serial_valid) if serial_valid is not None else None,
            dominant_color=tuple(int(x) for x in dom),
            recommendation=rec,
        )


analyzer = CurrencyAnalyzer()
