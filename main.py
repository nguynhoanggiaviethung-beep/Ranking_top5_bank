from __future__ import annotations
import os, re, time, datetime as dt, unicodedata, sys
from pathlib import Path
import numpy as np
import pandas as pd

try:
    from google_play_scraper import app as play_app
except Exception:
    play_app = None

try:
    import pymupdf as fitz
except Exception:
    try:
        import fitz
    except Exception:
        fitz = None

try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None
    Image = None

from scoring_rules import (
    CRITERIA, PILLARS, LEVEL_TO_SCORE,
    rank_banks, direct_percentage_score, MIN_CRITERIA_FOR_RANK,
)

# Windows consoles using legacy code pages cannot print every Vietnamese/Unicode
# character in warnings. Keep the pipeline running and preserve readable output
# where supported instead of raising UnicodeEncodeError during scoring.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "pdf_reports"
CACHE_DIR = BASE_DIR / "pdf_text_cache"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

MANUAL_PATH = DATA_DIR / "scoring_manual.csv"
MANUAL_CRITERIA = list(CRITERIA)
ASSESSMENT_YEAR = 2025
MAX_SNIPPETS_PER_CRITERION = 8

BANKS_CONFIG = {
    "Vietcombank": {"app_id": "com.VCB", "pdf_filename": "vcb_bctn_2025.pdf"},
    "VPBank": {"app_id": "com.vnpay.vpbankonline", "pdf_filename": "vpb_bctn_2025.pdf"},
    "ACB": {"app_id": "mobile.acb.com.vn", "pdf_filename": "acb_bctn_2025.pdf"},
    "OCB": {"app_id": "vn.com.ocb.awe", "pdf_filename": "ocb_bctn_2025.pdf"},
    "Agribank": {"app_id": "com.vnpay.Agribank3g", "pdf_filename": "agribank_bctn_2025.pdf"},
}

# Candidate evidence patterns. These FIND evidence; they do not themselves award points.
# C3 is assessed from documented digital customer-support capability in 2025.
PATTERNS = {
    "C1": [r"ngân hàng số", r"mobile banking", r"internet banking", r"kênh số", r"dịch vụ số", r"omni[- ]?channel", r"đa kênh"],
    "C2": [r"khách hàng số", r"khách hàng sử dụng.*kênh số", r"digital customer", r"active digital", r"người dùng.*ứng dụng"],
    "S1": [r"chiến lược chuyển đổi số", r"chiến lược.*số", r"digital transformation strategy", r"lộ trình chuyển đổi số", r"roadmap"],
    "S2": [r"đầu tư.*công nghệ", r"đầu tư.*chuyển đổi số", r"ngân sách.*công nghệ", r"technology investment", r"chi phí.*công nghệ"],
    "S3": [r"hệ sinh thái số", r"đối tác công nghệ", r"hợp tác.*công nghệ", r"digital ecosystem", r"partnership"],
    "T1": [r"ekyc", r"định danh điện tử", r"sinh trắc học", r"biometric"],
    "T2": [r"vay online", r"vay trực tuyến", r"cho vay trực tuyến", r"digital lending", r"cho vay số", r"tín dụng số"],
    "T3": [r"trí tuệ nhân tạo", r"\bai\b", r"genai", r"generative ai", r"machine learning", r"chatbot", r"trợ lý ảo"],
    "T4": [r"open banking", r"open api", r"ngân hàng mở", r"api mở", r"application programming interface"],
    "O1": [r"giao dịch.*kênh số", r"giao dịch số", r"digital transaction", r"tỷ trọng.*giao dịch.*số", r"%.*giao dịch.*số"],
    "O2": [r"tự động hóa quy trình", r"số hóa quy trình", r"robotic process automation", r"\brpa\b", r"straight[- ]?through processing", r"\bstp\b"],
    "O3": [r"paperless", r"không giấy", r"vận hành số", r"digital operation", r"quy trình số"],
    "H1": [r"đào tạo.*chuyển đổi số", r"đào tạo.*kỹ năng số", r"năng lực số", r"digital skills", r"digital training"],
    "H2": [r"đổi mới sáng tạo", r"innovation hub", r"innovation lab", r"hackathon", r"sandbox", r"trung tâm đổi mới"],
    "H3": [r"quản trị thay đổi", r"change management", r"văn hóa số", r"digital culture", r"chuyển đổi văn hóa"],
    "D1": [r"nền tảng dữ liệu", r"data platform", r"data lake", r"data warehouse", r"kho dữ liệu", r"tích hợp dữ liệu"],
    "D2": [r"quản trị dữ liệu", r"data governance", r"chất lượng dữ liệu", r"data security", r"bảo mật dữ liệu", r"quản lý dữ liệu"],
    "D3": [r"phân tích dữ liệu", r"data analytics", r"machine learning", r"cá nhân hóa", r"personalization", r"dữ liệu.*ra quyết định"],
}

EVIDENCE_COLS = [
    "Bank", "Criterion", "Pillar", "Assessment_Year", "Raw_Value", "Unit",
    "Numerator", "Denominator", "Score", "Evidence", "Source", "Page",
    "URL", "Collected_Date", "Evidence_Status", "Reviewer_Note",
]


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    return re.sub(r"\s+", " ", text).strip()


def find_pdf(filename: str) -> Path | None:
    candidates = [PDF_DIR / filename, BASE_DIR / filename, Path("pdf_reports") / filename]
    return next((p for p in candidates if p.exists()), None)


def extract_pdf_pages(pdf_path: Path):
    if fitz is None:
        return []
    pages = []
    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            text = page.get_text("text") or ""
            pages.append(text)
    except Exception:
        return []
    return pages


def ocr_pdf_pages(pdf_path: Path):
    if fitz is None or pytesseract is None or Image is None:
        return []
    pages = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pages.append(pytesseract.image_to_string(img, lang="vie+eng"))
    except Exception:
        return []
    return pages


def get_pages(filename: str):
    path = find_pdf(filename)
    if path is None:
        return [], "missing", None
    cache = CACHE_DIR / f"{path.stem}_pages.pkl"
    if cache.exists():
        try:
            return pd.read_pickle(cache), "cache", path
        except Exception:
            pass
    pages = extract_pdf_pages(path)
    usable = sum(bool(p.strip()) for p in pages)
    if usable < max(2, len(pages) * 0.2):
        ocr = ocr_pdf_pages(path)
        if ocr:
            pages = ocr
            source = "ocr"
        else:
            source = "missing"
    else:
        source = "pymupdf"
    if source != "missing":
        pd.to_pickle(pages, cache)
    return pages, source, path


def snippets_for_page(text: str, pattern: str, radius: int = 260):
    out = []
    normalized = normalize_text(text)
    for m in re.finditer(pattern, normalized, flags=re.I):
        s = max(0, m.start() - radius)
        e = min(len(normalized), m.end() + radius)
        out.append(normalized[s:e])
        if len(out) >= 3:
            break
    return out


def extract_evidence(bank: str, filename: str) -> pd.DataFrame:
    pages, source, path = get_pages(filename)
    if not pages:
        return pd.DataFrame(columns=EVIDENCE_COLS)
    today = dt.date.today().isoformat()
    rows = []
    for code in CRITERIA:
        patterns = PATTERNS.get(code, [])
        if not patterns:
            continue
        seen = set()
        count = 0
        for page_no, page_text in enumerate(pages, start=1):
            if count >= MAX_SNIPPETS_PER_CRITERION:
                break
            for pattern in patterns:
                if count >= MAX_SNIPPETS_PER_CRITERION:
                    break
                for snippet in snippets_for_page(page_text, pattern):
                    key = (code, page_no, snippet[:180])
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append({
                        "Bank": bank,
                        "Criterion": code,
                        "Pillar": CRITERIA[code]["pillar"],
                        "Assessment_Year": ASSESSMENT_YEAR,
                        "Raw_Value": np.nan,
                        "Score": np.nan,
                        "Evidence": snippet,
                        "Source": f"{path.name} ({source})" if path else f"BCTN 2025 ({source})",
                        "Page": page_no,
                        "URL": "",
                        "Collected_Date": today,
                        "Evidence_Status": "Candidate",
                        "Reviewer_Note": "Đoạn trích tự động tìm thấy; cần kiểm tra trước khi dùng chấm điểm.",
                    })
                    count += 1
                    if count >= MAX_SNIPPETS_PER_CRITERION:
                        break
    return pd.DataFrame(rows, columns=EVIDENCE_COLS)


def scrape_google_play(bank: str, app_id: str) -> dict:
    base = {"Bank": bank, "Rating_Star": np.nan, "Ratings_Count": np.nan, "Positive_Ratio": np.nan,
            "App_Source": "missing", "App_URL": f"https://play.google.com/store/apps/details?id={app_id}",
            "Assessment_Year": dt.date.today().year, "Collected_Date": dt.date.today().isoformat(),
            "Scoring_Use": "Context only; not used in the 2025 DTI snapshot"}
    if play_app is None:
        base["App_Source"] = "package_missing"
        return base
    try:
        result = play_app(app_id, lang="vi", country="vn")
        base["Rating_Star"] = float(result.get("score")) if result.get("score") is not None else np.nan
        base["Ratings_Count"] = float(result.get("ratings")) if result.get("ratings") is not None else np.nan
        hist = result.get("histogram") or []
        if len(hist) == 5 and sum(hist) > 0:
            # Positive = tỷ lệ đánh giá 4–5 sao (proxy công khai)
            base["Positive_Ratio"] = (hist[3] + hist[4]) / sum(hist) * 100
        base["App_Source"] = "Google Play live"
    except Exception as exc:
        base["App_Source"] = f"error: {type(exc).__name__}"
    return base


# ---------------------------------------------------------------------------
# CHẤM ĐIỂM
# ---------------------------------------------------------------------------
def create_manual_template() -> None:
    """Tạo file mẫu để nhóm điền điểm sau khi duyệt evidence_data.csv.
    Ô TRỐNG = N/D (chưa đủ bằng chứng). Không điền 0 thay cho thiếu dữ liệu."""
    tpl = pd.DataFrame({"Bank": list(BANKS_CONFIG)})
    for c in MANUAL_CRITERIA:
        tpl[f"{c}_Score"] = np.nan
    tpl["Scoring_Note"] = ""
    tpl.to_csv(MANUAL_PATH, index=False, encoding="utf-8-sig")


def load_manual_scoring() -> pd.DataFrame:
    if not MANUAL_PATH.exists():
        create_manual_template()
        print(f"[!] Chưa có {MANUAL_PATH.name} -> đã tạo file mẫu trống tại: {MANUAL_PATH}")
    return pd.read_csv(MANUAL_PATH, encoding="utf-8-sig")


def _approved_evidence(ev: pd.DataFrame, bank: str, code: str) -> pd.DataFrame:
    if ev.empty or "Bank" not in ev.columns or "Criterion" not in ev.columns:
        return pd.DataFrame()
    subset = ev[(ev["Bank"] == bank) & (ev["Criterion"] == code)].copy()
    if "Evidence_Status" not in subset.columns:
        return pd.DataFrame()
    subset = subset[subset["Evidence_Status"].astype(str).str.casefold().eq("approved")]
    if "Assessment_Year" in subset.columns:
        subset = subset[pd.to_numeric(subset["Assessment_Year"], errors="coerce") == ASSESSMENT_YEAR]
    required = ["Evidence", "Source", "Collected_Date"]
    if any(c not in subset.columns for c in required) or not {"URL", "Page"}.issubset(subset.columns):
        return pd.DataFrame()
    for col in required:
        subset = subset[subset[col].fillna("").astype(str).str.strip().ne("")]
    has_locator = (
        subset["URL"].fillna("").astype(str).str.strip().ne("")
        | subset["Page"].fillna("").astype(str).str.strip().ne("")
    )
    subset = subset[has_locator]
    return subset


def build_scoring_table() -> pd.DataFrame:
    evidence_path = DATA_DIR / "evidence_data.csv"
    ev = pd.read_csv(evidence_path, encoding="utf-8-sig") if evidence_path.exists() else pd.DataFrame()
    manual = load_manual_scoring()

    valid_levels = set(LEVEL_TO_SCORE.values())
    warnings = []
    rows = []
    for bank in BANKS_CONFIG:
        row = {"Bank": bank}  # khóa là "C1", "T1"... (không có hậu tố "_Score")

        # All criteria, including C3, require approved evidence in the 2025 period.
        m = manual[manual["Bank"] == bank]
        for code in MANUAL_CRITERIA:
            col = f"{code}_Score" if f"{code}_Score" in manual.columns else code
            if m.empty or col not in manual.columns:
                row[code] = None
                continue
            val = pd.to_numeric(m.iloc[0][col], errors="coerce")
            if pd.isna(val):
                row[code] = None  # N/D
                continue
            approved = _approved_evidence(ev, bank, code)
            if approved.empty:
                warnings.append(f"{bank}-{code}: chưa có bằng chứng được duyệt cho kỳ {ASSESSMENT_YEAR} -> bỏ (N/D)")
                row[code] = None
                continue
            try:
                if CRITERIA[code]["type"] == "quantitative":  # C2, O1
                    if not {"Numerator", "Denominator"}.issubset(approved.columns):
                        warnings.append(f"{bank}-{code}: thiếu tử số/mẫu số -> bỏ (N/D)")
                        row[code] = None
                        continue
                    ratio_rows = approved[
                        approved["Numerator"].fillna("").astype(str).str.strip().ne("")
                        & approved["Denominator"].fillna("").astype(str).str.strip().ne("")
                    ]
                    if ratio_rows.empty:
                        warnings.append(f"{bank}-{code}: bằng chứng chưa xác nhận tử số/mẫu số -> bỏ (N/D)")
                        row[code] = None
                        continue
                    raw_percentages = pd.to_numeric(ratio_rows["Raw_Value"], errors="coerce").dropna()
                    if raw_percentages.empty or not (raw_percentages.sub(float(val)).abs() < 1e-6).any():
                        warnings.append(f"{bank}-{code}: điểm không khớp tỷ lệ Raw_Value đã duyệt -> bỏ (N/D)")
                        row[code] = None
                        continue
                    row[code] = direct_percentage_score(val)
                elif CRITERIA[code]["type"] == "quantitative_proxy":
                    row[code] = direct_percentage_score(val)
                elif float(val) in valid_levels:  # định tính: 0/30/50/70/100
                    row[code] = float(val)
                else:
                    warnings.append(f"{bank}-{code}: điểm {val} không thuộc {sorted(valid_levels)} -> bỏ (N/D)")
                    row[code] = None
            except ValueError as e:
                warnings.append(f"{bank}-{code}: {e} -> bỏ (N/D)")
                row[code] = None
        rows.append(row)

    scored = rank_banks(pd.DataFrame(rows))
    scored.to_csv(DATA_DIR / "scoring_data.csv", index=False, encoding="utf-8-sig")
    for w in warnings:
        print("[!]", w)
    return scored


def build_provisional_scoring_table() -> pd.DataFrame:
    """Build a clearly labelled draft from staged scores and Candidate evidence.

    This does not approve evidence or alter the official scoring table. It lets
    reviewers inspect the existing proposed results while preserving N/D for
    unsupported, quantitative, or otherwise untraceable criteria.
    """
    evidence_path = DATA_DIR / "evidence_data.csv"
    ev = pd.read_csv(evidence_path, encoding="utf-8-sig", keep_default_na=False) if evidence_path.exists() else pd.DataFrame()
    manual = load_manual_scoring()
    if not ev.empty:
        ev["Assessment_Year"] = pd.to_numeric(ev.get("Assessment_Year"), errors="coerce")

    rows = []
    for bank in BANKS_CONFIG:
        row = {"Bank": bank, "Result_Status": "Dự thảo — chưa duyệt bằng chứng"}
        m = manual[manual["Bank"].astype(str) == bank]
        for code, meta in CRITERIA.items():
            row[code] = None
            if ev.empty:
                continue
            candidates = ev[
                ev["Bank"].astype(str).eq(bank)
                & ev["Criterion"].astype(str).eq(code)
                & pd.to_numeric(ev["Assessment_Year"], errors="coerce").eq(ASSESSMENT_YEAR)
                & ev["Evidence_Status"].astype(str).str.casefold().isin(["candidate", "approved"])
            ].copy()
            if candidates.empty:
                continue
            has_trace = (
                candidates["Evidence"].astype(str).str.strip().ne("")
                & candidates["Source"].astype(str).str.strip().ne("")
                & (
                    candidates["URL"].astype(str).str.strip().ne("")
                    | candidates["Page"].astype(str).str.strip().ne("")
                )
            )
            candidates = candidates[has_trace]
            if candidates.empty:
                continue

            score_col = f"{code}_Score" if f"{code}_Score" in manual.columns else code
            if m.empty or score_col not in manual.columns:
                continue
            value = pd.to_numeric(m.iloc[0][score_col], errors="coerce")
            if pd.isna(value):
                continue

            if meta["type"] == "quantitative":
                valid_ratio = candidates[
                    candidates["Numerator"].astype(str).str.strip().ne("")
                    & candidates["Denominator"].astype(str).str.strip().ne("")
                ]
                raw = pd.to_numeric(valid_ratio["Raw_Value"], errors="coerce").dropna()
                if raw.empty or not (raw.sub(float(value)).abs() < 1e-6).any():
                    continue
                try:
                    row[code] = direct_percentage_score(float(value))
                except ValueError:
                    continue
            elif float(value) in set(LEVEL_TO_SCORE.values()):
                row[code] = float(value)

        rows.append(row)

    draft = rank_banks(pd.DataFrame(rows))
    draft.to_csv(DATA_DIR / "scoring_provisional_data.csv", index=False, encoding="utf-8-sig")
    return draft


def build_evidence_review_matrix() -> pd.DataFrame:
    """Create a reviewer queue for all bank/criterion pairs; this is not a score source."""
    evidence_path = DATA_DIR / "evidence_data.csv"
    ev = pd.read_csv(evidence_path, encoding="utf-8-sig", keep_default_na=False) if evidence_path.exists() else pd.DataFrame(columns=EVIDENCE_COLS)
    manual = load_manual_scoring().fillna("")
    rows = []

    for bank in BANKS_CONFIG:
        bank_manual = manual[manual["Bank"].astype(str).eq(bank)]
        for code in CRITERIA:
            group = ev[(ev["Bank"].astype(str) == bank) & (ev["Criterion"].astype(str) == code)] if not ev.empty else ev
            score_col = f"{code}_Score"
            proposed = str(bank_manual.iloc[0].get(score_col, "")).strip() if not bank_manual.empty else ""
            approved_rows = group[
                group["Evidence_Status"].astype(str).str.casefold().eq("approved")
                & pd.to_numeric(group["Assessment_Year"], errors="coerce").eq(ASSESSMENT_YEAR)
            ] if not group.empty else group
            if not approved_rows.empty:
                status = "ĐÃ DUYỆT"
                note = "Có bằng chứng đã duyệt cho kỳ đánh giá 2025."
            elif proposed:
                status = "CẦN ĐỐI CHIẾU"
                note = "Điểm hiện tại là đề xuất; kiểm tra nội dung, mức rubric, nguồn và vị trí trước khi duyệt."
            elif group.empty:
                status = "N/D - CẦN TÌM NGUỒN"
                note = "Chưa có dòng bằng chứng ứng viên cho tiêu chí này."
            else:
                status = "N/D - CẦN RÀ SOÁT"
                note = "Chưa có điểm đề xuất; rà bằng chứng trước khi quyết định chấm hay giữ N/D."

            traceable = group[
                group["Evidence"].astype(str).str.strip().ne("")
                & group["Source"].astype(str).str.strip().ne("")
                & group["Collected_Date"].astype(str).str.strip().ne("")
                & (
                    group["URL"].astype(str).str.strip().ne("")
                    | group["Page"].astype(str).str.strip().ne("")
                )
            ] if not group.empty else group
            ratio_count = 0
            if code in {"C2", "O1"} and not group.empty:
                ratio_count = int(
                    group["Numerator"].astype(str).str.strip().ne("")
                    .mul(group["Denominator"].astype(str).str.strip().ne(""))
                    .sum()
                )
                note += f" Dòng ứng viên có cả tử số và mẫu số: {ratio_count}; cần xác minh cùng phạm vi."

            rows.append({
                "Bank": bank,
                "Criterion": code,
                "Proposed_Score": proposed,
                "Candidate_Rows": len(group),
                "Traceable_Candidate_Rows": len(traceable),
                "Approved_Rows": int(group["Evidence_Status"].astype(str).str.casefold().eq("approved").sum()) if not group.empty else 0,
                "Review_Status": status,
                "Review_Note": note,
            })

    matrix = pd.DataFrame(rows)
    matrix.to_csv(DATA_DIR / "evidence_review_matrix.csv", index=False, encoding="utf-8-sig")
    return matrix


def run_pipeline():
    evidence_frames = []
    app_rows = []
    for bank, cfg in BANKS_CONFIG.items():
        print(f"[PDF] {bank}")
        evidence_frames.append(extract_evidence(bank, cfg["pdf_filename"]))
        print(f"[Google Play] {bank}")
        app_rows.append(scrape_google_play(bank, cfg["app_id"]))
    evidence = pd.concat(evidence_frames, ignore_index=True) if evidence_frames else pd.DataFrame(columns=EVIDENCE_COLS)
    # Preserve reviewer decisions when the same extracted excerpt is regenerated.
    old_path = DATA_DIR / "evidence_data.csv"
    if old_path.exists() and not evidence.empty:
        try:
            old = pd.read_csv(old_path, encoding="utf-8-sig").fillna("")
            key_cols = ["Bank", "Criterion", "Page", "Evidence"]
            keep_cols = key_cols + [c for c in ("Evidence_Status", "Reviewer_Note", "Raw_Value", "Unit", "Numerator", "Denominator", "Score", "URL") if c in old.columns]
            if all(c in old.columns for c in key_cols):
                prior = old[keep_cols].copy()
                # If duplicated excerpts exist, an explicit reviewer approval
                # must take precedence over a Candidate copy of the same row.
                prior["_approved_priority"] = prior.get(
                    "Evidence_Status", pd.Series(index=prior.index, dtype=object)
                ).astype(str).str.casefold().eq("approved").astype(int)
                prior = (
                    prior.sort_values("_approved_priority")
                    .drop_duplicates(key_cols, keep="last")
                    .drop(columns="_approved_priority")
                )
                evidence = evidence.drop(columns=[c for c in keep_cols if c not in key_cols and c in evidence.columns]).merge(prior, on=key_cols, how="left", suffixes=("", "_old"))
                for col in keep_cols:
                    if col not in key_cols and f"{col}_old" in evidence.columns:
                        evidence[col] = evidence[f"{col}_old"].where(evidence[f"{col}_old"].fillna("").astype(str).str.strip().ne(""), evidence[col])
                        evidence.drop(columns=[f"{col}_old"], inplace=True)
                evidence["Evidence_Status"] = evidence["Evidence_Status"].fillna("Candidate").replace("", "Candidate")
                generated_keys = set(map(tuple, evidence[key_cols].fillna("").astype(str).to_numpy()))
                old_keys = old[key_cols].fillna("").astype(str)
                unmatched = old.loc[~old_keys.apply(tuple, axis=1).isin(generated_keys)].copy()
                if not unmatched.empty:
                    for col in EVIDENCE_COLS:
                        if col not in unmatched.columns:
                            unmatched[col] = ""
                    evidence = pd.concat([evidence, unmatched[EVIDENCE_COLS]], ignore_index=True)
        except Exception as exc:
            print(f"[!] Không giữ được trạng thái duyệt evidence cũ: {type(exc).__name__}")
    evidence.to_csv(DATA_DIR / "evidence_data.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(app_rows).to_csv(DATA_DIR / "app_data.csv", index=False, encoding="utf-8-sig")
    scoring = build_scoring_table()
    # Keep the clearly labelled draft in sync with the just-refreshed evidence
    # and manual-score inputs. The official table remains gated by Approved.
    build_provisional_scoring_table()
    build_evidence_review_matrix()
    return evidence, pd.DataFrame(app_rows), scoring


if __name__ == "__main__":
    evidence, apps, scoring = run_pipeline()
    print("\n=== KẾT QUẢ ===")
    print(f"Evidence rows: {len(evidence)}")
    print(f"App rows: {len(apps)}")
    cols = ["Rank", "Bank", "DTI_Total_Score", "DTI_Level",
            "Criteria_Available", "Pillars_Available", "Data_Coverage", "Rank_Eligible"]
    print(scoring[cols].to_string(index=False))
    if not scoring["Rank_Eligible"].any():
        print(f"\nChưa ngân hàng nào đủ điều kiện xếp hạng (cần >={MIN_CRITERIA_FOR_RANK}/{len(CRITERIA)} tiêu chí và đủ 6 trụ cột).")
        print(f"Hãy duyệt data/evidence_data.csv rồi điền điểm vào {MANUAL_PATH.name}.")
    draft_path = DATA_DIR / "scoring_provisional_data.csv"
    if draft_path.exists():
        draft = pd.read_csv(draft_path, encoding="utf-8-sig")
        print("\n=== KẾT QUẢ DỰ THẢO (chưa thay thế kết quả chính thức) ===")
        print(draft[cols].to_string(index=False))
        print("\nBảng dự thảo dùng để rà soát; chỉ bằng chứng đã xác minh và đổi thành Approved mới được tính vào bảng chính thức.")
