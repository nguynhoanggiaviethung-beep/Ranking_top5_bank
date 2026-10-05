"""
scoring_rules.py
Bộ quy tắc chấm DBI ngân hàng - tham chiếu Quyết định 2158/QĐ-BTTTT.

LƯU Ý:
- Đây là bộ chỉ số ADAPTED cho ngân hàng, không phải "điểm DBI chính thức" của Bộ TT&TT.
- Tính từ dưới lên: tiêu chí -> trụ cột -> DBI, dùng trung bình cộng.
- Không dùng dữ liệu giả định, không fallback, không median-imputation.
- N/D = không có bằng chứng/dữ liệu công khai đủ để chấm -> không đưa vào mẫu số.
  (Không tìm thấy dữ liệu != ngân hàng không thực hiện.)
- Không đưa Downloads, số bài báo, số lần keyword, News vào điểm.
- Điểm định tính dùng 5 mức 0/30/50/70/100 theo logic mức độ của QĐ 2158
  (đây là rubric vận hành của nhóm, KHÔNG phải quy định của QĐ 2158).
- Điểm nào không truy được nguồn -> không chấm.
"""

from __future__ import annotations
import pandas as pd

# ---------------------------------------------------------------------------
# 1. CẤU TRÚC 6 TRỤ CỘT - 19 TIÊU CHÍ (đúng theo bảng bộ chỉ số: 3+3+4+3+3+3)
# ---------------------------------------------------------------------------
PILLARS = {
    "Customer":   {"name": "Khách hàng", "weight": 1/6, "criteria": ["C1", "C2", "C3"]},
    "Strategy":   {"name": "Chiến lược", "weight": 1/6, "criteria": ["S1", "S2", "S3"]},
    "Technology": {"name": "Công nghệ",  "weight": 1/6, "criteria": ["T1", "T2", "T3", "T4"]},
    "Operations": {"name": "Vận hành",   "weight": 1/6, "criteria": ["O1", "O2", "O3"]},
    "Culture":    {"name": "Văn hóa",    "weight": 1/6, "criteria": ["H1", "H2", "H3"]},
    "Data":       {"name": "Dữ liệu",    "weight": 1/6, "criteria": ["D1", "D2", "D3"]},
}

CRITERIA = {
    "C1": {"pillar": "Customer", "name": "Mức độ bao phủ kênh/dịch vụ số", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ ngân hàng chuyển các điểm chạm/sản phẩm dịch vụ sang môi trường số và tích hợp đa kênh."},
    "C2": {"pillar": "Customer", "name": "Mức độ khách hàng sử dụng kênh số", "type": "quantitative",
           "source": "BCTN 2025 / tài liệu chính thức",
           "description": "Tỷ lệ khách hàng số/khách hàng hoạt động hoặc chỉ tiêu tương đương; chỉ chấm khi có tử số và mẫu số rõ ràng."},
    "C3": {"pillar": "Customer", "name": "Chất lượng trải nghiệm số", "type": "quantitative_proxy",
           "source": "Google Play",
           "description": "Proxy công khai (không phải tiêu chí DBI gốc): Rating/5*100 và Positive Ratio; có cả hai thì lấy trung bình."},

    "S1": {"pillar": "Strategy", "name": "Chiến lược và lộ trình chuyển đổi số", "type": "qualitative",
           "source": "BCTN 2025 + tài liệu chính thức",
           "description": "Mức độ hiện diện của định hướng, mục tiêu, roadmap và việc tích hợp CĐS vào chiến lược ngân hàng."},
    "S2": {"pillar": "Strategy", "name": "Đầu tư/ngân sách cho chuyển đổi số", "type": "qualitative",
           "source": "BCTN 2025 + công bố chính thức",
           "description": "Mức độ thể hiện nguồn lực tài chính dành cho công nghệ/CĐS và mức độ gắn đầu tư với kết quả."},
    "S3": {"pillar": "Strategy", "name": "Hệ sinh thái và quan hệ đối tác số", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ thiết kế hệ sinh thái, hợp tác công nghệ và tạo giá trị mới thông qua đối tác."},

    "T1": {"pillar": "Technology", "name": "eKYC và sinh trắc học", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ triển khai định danh điện tử/sinh trắc học trong onboarding và xác thực."},
    "T2": {"pillar": "Technology", "name": "Cho vay số/digital lending", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ số hóa quy trình cấp tín dụng/giải ngân/đánh giá tín dụng."},
    "T3": {"pillar": "Technology", "name": "AI/GenAI", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ triển khai AI/ML/GenAI trong sản phẩm, vận hành, chăm sóc khách hàng hoặc quản trị."},
    "T4": {"pillar": "Technology", "name": "Open Banking/API", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ triển khai API/Open Banking và kết nối hệ sinh thái số."},

    "O1": {"pillar": "Operations", "name": "Tỷ trọng giao dịch trên kênh số", "type": "quantitative",
           "source": "BCTN 2025",
           "description": "Tỷ lệ giao dịch qua kênh số khi ngân hàng công bố rõ mẫu số và phạm vi."},
    "O2": {"pillar": "Operations", "name": "Số hóa/tự động hóa quy trình", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ số hóa, tự động hóa, STP/RPA/workflow trong các quy trình vận hành."},
    "O3": {"pillar": "Operations", "name": "Vận hành dịch vụ số", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ vận hành liên tục, paperless, straight-through và đo lường hiệu quả của dịch vụ số."},

    "H1": {"pillar": "Culture", "name": "Đào tạo và năng lực số", "type": "qualitative",
           "source": "BCTN 2025",
           "description": "Mức độ đào tạo, nâng cao kỹ năng số và khả năng thích ứng của nhân sự."},
    "H2": {"pillar": "Culture", "name": "Đổi mới sáng tạo", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ có chương trình, ngân sách, sandbox, innovation hub/hackathon hoặc cơ chế thử nghiệm."},
    "H3": {"pillar": "Culture", "name": "Quản trị thay đổi và văn hóa số", "type": "qualitative",
           "source": "BCTN 2025",
           "description": "Mức độ tổ chức thúc đẩy thay đổi, phối hợp liên đơn vị và gắn CĐS với văn hóa quản trị."},

    "D1": {"pillar": "Data", "name": "Kiến trúc và tích hợp dữ liệu", "type": "qualitative",
           "source": "BCTN 2025",
           "description": "Mức độ xây dựng nền tảng dữ liệu, kho dữ liệu, tích hợp dữ liệu và khai thác xuyên hệ thống."},
    "D2": {"pillar": "Data", "name": "Quản trị và an toàn dữ liệu", "type": "qualitative",
           "source": "BCTN 2025",
           "description": "Mức độ có chính sách/quy trình quản trị dữ liệu, chất lượng, bảo mật và kiểm soát truy cập."},
    "D3": {"pillar": "Data", "name": "Phân tích dữ liệu và cá nhân hóa", "type": "qualitative",
           "source": "BCTN 2025 + website chính thức",
           "description": "Mức độ sử dụng analytics/ML để hỗ trợ quyết định, quản trị rủi ro, gợi ý và cá nhân hóa dịch vụ."},
}

CRITERIA_CODES = list(CRITERIA.keys())

# Điều kiện xếp hạng chính thức
MIN_CRITERIA_FOR_RANK = 12      # ít nhất 12 tiêu chí có dữ liệu (trên tổng len(CRITERIA))
MIN_CRITERIA_PER_PILLAR = 1     # mỗi trụ cột ít nhất 1 tiêu chí

# Rubric 5 mức (logic mức độ của QĐ 2158): Mức 1 = 0, Mức 2-5 = 30/50/70/100
LEVEL_TO_SCORE = {1: 0.0, 2: 30.0, 3: 50.0, 4: 70.0, 5: 100.0}

# Cấu trúc bảng bằng chứng - mỗi điểm số phải truy được nguồn
EVIDENCE_COLUMNS = [
    "Bank", "Criterion", "Raw_Value", "Score",
    "Evidence", "Source", "Page", "URL", "Collected_Date",
]
# Các trường bắt buộc để một bằng chứng được phép chấm điểm
EVIDENCE_REQUIRED = ["Bank", "Criterion", "Raw_Value", "Source", "URL", "Collected_Date"]


# ---------------------------------------------------------------------------
# 2. HÀM CHẤM TỪNG TIÊU CHÍ
# ---------------------------------------------------------------------------
def _is_missing(x) -> bool:
    return x is None or pd.isna(x)


def maturity_level(score: float | None) -> str:
    """Thang mức trưởng thành của QĐ 2158. Đúng 100 mới là Mức 5."""
    if _is_missing(score):
        return "N/D"
    score = float(score)
    if score < 25:
        return "Mức 1 – Khởi động"
    if score < 50:
        return "Mức 2 – Bắt đầu"
    if score < 75:
        return "Mức 3 – Hình thành"
    if score < 100:
        return "Mức 4 – Nâng cao"
    return "Mức 5 – Dẫn dắt"


def score_from_level(level: int | None) -> float | None:
    """Tiêu chí định tính: mức 1..5 -> 0/30/50/70/100. None -> N/D."""
    if _is_missing(level):
        return None
    level = int(level)
    if level not in LEVEL_TO_SCORE:
        raise ValueError("level phải nằm trong 1..5")
    return LEVEL_TO_SCORE[level]


def direct_percentage_score(value: float | None) -> float | None:
    """Tiêu chí định lượng (C2, O1): điểm = tỷ lệ thực tế (%). Không có mẫu số rõ ràng -> N/D."""
    if _is_missing(value):
        return None
    value = float(value)
    if value < 0 or value > 100:
        raise ValueError("Tỷ lệ % phải nằm trong [0,100].")
    return value


def app_cx_score(rating_star=None, positive_ratio=None) -> float | None:
    """
    C3: proxy trải nghiệm số (không phải tiêu chí DBI gốc).
    Rating Google Play: Rating/5*100; Positive Ratio: giữ nguyên %.
    Có cả hai -> trung bình; chỉ có một -> dùng cái đó; không có -> N/D.
    """
    scores = []
    if not _is_missing(rating_star):
        rating_star = float(rating_star)
        if not 0 <= rating_star <= 5:
            raise ValueError("Rating phải nằm trong [0,5].")
        scores.append(rating_star / 5 * 100)
    if not _is_missing(positive_ratio):
        positive_ratio = float(positive_ratio)
        if not 0 <= positive_ratio <= 100:
            raise ValueError("Positive ratio phải nằm trong [0,100].")
        scores.append(positive_ratio)
    return sum(scores) / len(scores) if scores else None


# ---------------------------------------------------------------------------
# 3. TỪ BẰNG CHỨNG -> BẢNG ĐIỂM CÁC TIÊU CHÍ
# ---------------------------------------------------------------------------
def build_scores_from_evidence(evidence: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Pipeline: Evidence -> Raw_Value -> Score.

    Quy ước Raw_Value trong bảng evidence:
      - tiêu chí định tính : mức 1..5
      - C2, O1             : tỷ lệ % (0..100), chỉ nhập khi có mẫu số rõ ràng
      - C3                 : dùng 2 dòng riêng, Criterion = "C3_RATING" (0..5)
                             và "C3_POSITIVE" (0..100)

    Dòng thiếu Bank/Criterion/Raw_Value/Source/URL/Collected_Date -> KHÔNG chấm (N/D).
    Trả về (scores_wide, audit):
      scores_wide: mỗi ngân hàng một dòng, cột Bank + C1..D3 (NaN = N/D)
      audit: các dòng bằng chứng kèm trạng thái Used / lý do loại
    """
    ev = evidence.copy()
    for col in EVIDENCE_COLUMNS:
        if col not in ev.columns:
            ev[col] = pd.NA

    def blank(v):
        return pd.isna(v) or str(v).strip() == ""

    status, scores = [], []
    c3_parts: dict[str, dict[str, float]] = {}
    for idx, r in ev.iterrows():
        missing = [c for c in EVIDENCE_REQUIRED if blank(r[c])]
        if missing:
            status.append("Loại: thiếu " + ", ".join(missing))
            scores.append(None)
            continue
        crit = str(r["Criterion"]).strip().upper()
        try:
            raw = float(r["Raw_Value"])
            if crit == "C3_RATING":
                c3_parts.setdefault(r["Bank"], {})["rating"] = raw
                app_cx_score(rating_star=raw)          # chỉ để validate
                s = None
            elif crit == "C3_POSITIVE":
                c3_parts.setdefault(r["Bank"], {})["positive"] = raw
                app_cx_score(positive_ratio=raw)
                s = None
            elif crit not in CRITERIA:
                status.append(f"Loại: tiêu chí '{crit}' không tồn tại")
                scores.append(None)
                continue
            elif CRITERIA[crit]["type"] == "quantitative":
                s = direct_percentage_score(raw)
            elif crit == "C3":
                status.append("Loại: C3 phải nhập qua C3_RATING / C3_POSITIVE")
                scores.append(None)
                continue
            else:
                s = score_from_level(int(raw))
            status.append("Used")
            scores.append(s)
        except (ValueError, TypeError) as e:
            status.append(f"Loại: giá trị không hợp lệ ({e})")
            scores.append(None)

    ev["Criterion"] = ev["Criterion"].astype(str).str.strip().str.upper()
    ev["Score"] = scores
    ev["Status"] = status

    banks = list(dict.fromkeys(ev["Bank"].dropna()))
    wide = pd.DataFrame({"Bank": banks})
    for code in CRITERIA_CODES:
        wide[code] = float("nan")
    used = ev[(ev["Status"] == "Used") & ev["Score"].notna()]
    for _, r in used.iterrows():
        wide.loc[wide["Bank"] == r["Bank"], r["Criterion"]] = r["Score"]
    for bank, parts in c3_parts.items():
        c3 = app_cx_score(parts.get("rating"), parts.get("positive"))
        if c3 is not None:
            wide.loc[wide["Bank"] == bank, "C3"] = c3
    return wide, ev


# ---------------------------------------------------------------------------
# 4. TRỤ CỘT, DBI, XẾP HẠNG
# ---------------------------------------------------------------------------
def pillar_score(scores: list[float | None]) -> float | None:
    """Trung bình cộng các tiêu chí có dữ liệu; N/D không bị thay bằng 0."""
    valid = [float(x) for x in scores if not _is_missing(x)]
    return sum(valid) / len(valid) if valid else None


def overall_score(pillar_scores: dict[str, float | None]) -> float | None:
    """
    DBI = trung bình cộng các trụ cột có dữ liệu (đủ 6 thì mỗi trụ cột 1/6).
    Trụ cột N/D không đưa vào mẫu số. Điều kiện đủ 6 trụ cột chỉ áp dụng cho
    việc XẾP HẠNG (Rank_Eligible), không chặn việc hiển thị DBI phần đã tính.
    """
    valid = [float(v) for v in pillar_scores.values() if not _is_missing(v)]
    return sum(valid) / len(valid) if valid else None


def evaluate_bank(row: dict) -> dict:
    """row chứa Score của các tiêu chí (NaN/None = N/D). Tính 6 trụ cột + DBI + coverage."""
    out = dict(row)
    p_scores = {}
    for key, pillar in PILLARS.items():
        p_scores[key] = pillar_score([row.get(c) for c in pillar["criteria"]])

    total = overall_score(p_scores)
    for key, score in p_scores.items():
        out[f"{key}_Score"] = score
        out[f"{key}_Level"] = maturity_level(score)
        out[f"{key}_Coverage"] = sum(
            1 for c in PILLARS[key]["criteria"] if not _is_missing(row.get(c))
        )
    out["DBI_Total_Score"] = total
    out["DBI_Level"] = maturity_level(total)
    out["Pillars_Available"] = sum(1 for v in p_scores.values() if v is not None)
    out["Criteria_Available"] = sum(1 for c in CRITERIA if not _is_missing(row.get(c)))
    out["Criteria_Total"] = len(CRITERIA)
    # Data Coverage chỉ để hiển thị, không cộng điểm
    out["Data_Coverage"] = out["Criteria_Available"] / out["Criteria_Total"] * 100
    out["Rank_Eligible"] = bool(
        out["Criteria_Available"] >= MIN_CRITERIA_FOR_RANK
        and all(
            out[f"{k}_Coverage"] >= MIN_CRITERIA_PER_PILLAR for k in PILLARS
        )
    )
    return out


def rank_banks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Xếp hạng theo DBI (điểm đầy đủ, chưa làm tròn) giảm dần.
    Không đủ điều kiện -> Rank = <NA> (hiển thị N/A), nhưng vẫn giữ DBI phần đã tính.
    Bằng điểm hoàn toàn -> đồng hạng (method='min'); không dùng lượt tải/số bài báo làm tie-breaker.
    """
    out = pd.DataFrame([evaluate_bank(r.to_dict()) for _, r in df.iterrows()])
    out["Rank"] = pd.array([pd.NA] * len(out), dtype="Int64")
    eligible = out["Rank_Eligible"] & out["DBI_Total_Score"].notna()
    if eligible.any():
        out.loc[eligible, "Rank"] = (
            out.loc[eligible, "DBI_Total_Score"]
            .rank(method="min", ascending=False)
            .astype("Int64")
        )
    return out.sort_values(
        ["Rank_Eligible", "DBI_Total_Score"],
        ascending=[False, False],
        na_position="last",
    ).reset_index(drop=True)