from __future__ import annotations
import os, re, time, datetime as dt, unicodedata
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
    rank_banks, app_cx_score, direct_percentage_score, MIN_CRITERIA_FOR_RANK,
)

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "pdf_reports"
CACHE_DIR = BASE_DIR / "pdf_text_cache"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

MANUAL_PATH = DATA_DIR / "scoring_manual.csv"
AUTO_CRITERIA = {"C3"}  # C3 tự tính từ Google Play, không nhập tay
MANUAL_CRITERIA = [c for c in CRITERIA if c not in AUTO_CRITERIA]
MAX_SNIPPETS_PER_CRITERION = 8

BANKS_CONFIG = {
    "Vietcombank": {"app_id": "com.VCB", "pdf_filename": "vcb_bctn_2025.pdf"},
    "VPBank": {"app_id": "com.vnpay.vpbankonline", "pdf_filename": "vpb_bctn_2025.pdf"},
    "ACB": {"app_id": "mobile.acb.com.vn", "pdf_filename": "acb_bctn_2025.pdf"},
    "OCB": {"app_id": "vn.com.ocb.awe", "pdf_filename": "ocb_bctn_2025.pdf"},
    "Agribank": {"app_id": "com.vnpay.Agribank3g", "pdf_filename": "agribank_bctn_2025.pdf"},
}

# Candidate evidence patterns. These FIND evidence; they do not themselves award points.
# C3 không có pattern: điểm lấy tự động từ Google Play.
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

EVIDENCE_COLS = ["Bank", "Criterion", "Raw_Value", "Score", "Evidence", "Source", "Page", "URL", "Collected_Date"]


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
                        "Raw_Value": np.nan,
                        "Score": np.nan,
                        "Evidence": snippet,
                        "Source": f"BCTN 2025 ({source})",
                        "Page": page_no,
                        "URL": "",
                        "Collected_Date": today,
                    })
                    count += 1
                    if count >= MAX_SNIPPETS_PER_CRITERION:
                        break
    return pd.DataFrame(rows, columns=EVIDENCE_COLS)


def scrape_google_play(bank: str, app_id: str) -> dict:
    base = {"Bank": bank, "Rating_Star": np.nan, "Ratings_Count": np.nan, "Positive_Ratio": np.nan,
            "App_Source": "missing", "App_URL": f"https://play.google.com/store/apps/details?id={app_id}"}
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
    tpl.to_csv(MANUAL_PATH, index=False, encoding="utf-8-sig")


def load_manual_scoring() -> pd.DataFrame:
    if not MANUAL_PATH.exists():
        create_manual_template()
        print(f"[!] Chưa có {MANUAL_PATH.name} -> đã tạo file mẫu trống tại: {MANUAL_PATH}")
    return pd.read_csv(MANUAL_PATH, encoding="utf-8-sig")


def _has_evidence(ev: pd.DataFrame, bank: str, code: str) -> bool:
    if ev.empty or "Bank" not in ev.columns or "Criterion" not in ev.columns:
        return False
    return not ev[(ev["Bank"] == bank) & (ev["Criterion"] == code)].empty


def build_scoring_table() -> pd.DataFrame:
    evidence_path = DATA_DIR / "evidence_data.csv"
    app_path = DATA_DIR / "app_data.csv"
    ev = pd.read_csv(evidence_path, encoding="utf-8-sig") if evidence_path.exists() else pd.DataFrame()
    apps = pd.read_csv(app_path, encoding="utf-8-sig") if app_path.exists() else pd.DataFrame()
    manual = load_manual_scoring()

    valid_levels = set(LEVEL_TO_SCORE.values())
    warnings = []
    rows = []
    for bank in BANKS_CONFIG:
        row = {"Bank": bank}  # khóa là "C1", "T1"... (không có hậu tố "_Score")

        # C3: tự động từ Google Play (proxy, không phải tiêu chí DBI gốc)
        a = apps[apps["Bank"] == bank] if not apps.empty else pd.DataFrame()
        if not a.empty:
            row["C3"] = app_cx_score(a.iloc[0].get("Rating_Star"), a.iloc[0].get("Positive_Ratio"))
        else:
            row["C3"] = None

        # Các tiêu chí còn lại: điểm nhập tay đã duyệt evidence
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
            if not _has_evidence(ev, bank, code):
                warnings.append(f"{bank}-{code}: có điểm nhưng không có dòng evidence -> bỏ (N/D)")
                row[code] = None
                continue
            try:
                if CRITERIA[code]["type"] == "quantitative":  # C2, O1
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


def run_pipeline():
    evidence_frames = []
    app_rows = []
    for bank, cfg in BANKS_CONFIG.items():
        print(f"[PDF] {bank}")
        evidence_frames.append(extract_evidence(bank, cfg["pdf_filename"]))
        print(f"[Google Play] {bank}")
        app_rows.append(scrape_google_play(bank, cfg["app_id"]))
    evidence = pd.concat(evidence_frames, ignore_index=True) if evidence_frames else pd.DataFrame(columns=EVIDENCE_COLS)
    evidence.to_csv(DATA_DIR / "evidence_data.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(app_rows).to_csv(DATA_DIR / "app_data.csv", index=False, encoding="utf-8-sig")
    scoring = build_scoring_table()
    return evidence, pd.DataFrame(app_rows), scoring


if __name__ == "__main__":
    evidence, apps, scoring = run_pipeline()
    print("\n=== KẾT QUẢ ===")
    print(f"Evidence rows: {len(evidence)}")
    print(f"App rows: {len(apps)}")
    cols = ["Rank", "Bank", "DBI_Total_Score", "DBI_Level",
            "Criteria_Available", "Pillars_Available", "Data_Coverage", "Rank_Eligible"]
    print(scoring[cols].to_string(index=False))
    if not scoring["Rank_Eligible"].any():
        print(f"\nChưa ngân hàng nào đủ điều kiện xếp hạng (cần >={MIN_CRITERIA_FOR_RANK}/{len(CRITERIA)} tiêu chí và đủ 6 trụ cột).")
        print(f"Hãy duyệt data/evidence_data.csv rồi điền điểm vào {MANUAL_PATH.name}.")