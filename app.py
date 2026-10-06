import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    page_title="Dashboard Ranking CĐS Ngân Hàng",
    layout="wide"
)

# Bảng màu pastel tím — GIỮ NGUYÊN GIAO DIỆN
TEXT = "#4A3F6B"
SUBTEXT = "#7C6FA0"
DEEP = "#7C5CD6"
BG = "#F7F3FF"
CARD = "#FFFFFF"
BORDER = "#E4D9FB"
BANK_COLORS = ["#A78BFA", "#C4B5FD", "#F0ABFC", "#93C5FD", "#D8B4FE", "#FBCFE8", "#BAE6FD", "#DDD6FE"]
PILLAR_COLORS = ["#A78BFA", "#F0ABFC", "#93C5FD", "#FBCFE8", "#C4B5FD", "#BAE6FD"]

# ==========================================
# 2. CSS GIAO DIỆN SÁNG TÍM PASTEL
# ==========================================
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, {BG} 0%, #FDFBFF 100%);
        color: {TEXT};
    }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    h1, h2, h3, h4, p, span, label, li, div {{ color: {TEXT}; }}

    .hero {{
        background: linear-gradient(120deg, #E9DDFD 0%, #F8E8FF 55%, #E3ECFF 100%);
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 28px 34px;
        margin-bottom: 18px;
        box-shadow: 0 6px 20px rgba(167,139,250,0.15);
    }}
    .hero h1 {{ margin: 0; font-size: 2rem; color: {TEXT}; }}
    .hero p {{ margin: 6px 0 0 0; color: {SUBTEXT}; font-size: 1rem; }}

    div[data-testid="stMetric"] {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 4px 14px rgba(167,139,250,0.12);
    }}
    div[data-testid="stMetricLabel"] p {{ color: {SUBTEXT}; font-weight: 600; }}
    div[data-testid="stMetricValue"] {{ color: {TEXT}; }}

    .section-title {{
        font-size: 1.25rem; font-weight: 700; color: {TEXT};
        border-left: 6px solid #C4B5FD; padding-left: 12px; margin: 10px 0 4px 0;
    }}
    .section-desc {{ color: {SUBTEXT}; font-size: 0.93rem; margin-bottom: 10px; }}

    .chart-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 14px 16px 6px 16px;
        box-shadow: 0 4px 14px rgba(167,139,250,0.10);
    }}
    .note {{
        background: #F3EDFF;
        border: 1px dashed #C4B5FD;
        border-radius: 14px;
        padding: 12px 16px;
        margin: 8px 0 18px 0;
        font-size: 0.92rem;
        line-height: 1.55;
        color: {TEXT};
    }}
    .note b {{ color: #7C5CD6; }}
    .insight {{
        background: #FFF0FA;
        border: 1px solid #F5D0FE;
        border-radius: 14px;
        padding: 12px 16px;
        margin: 8px 0 18px 0;
        font-size: 0.92rem;
        line-height: 1.55;
    }}

    div[data-testid="stExpander"] {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; overflow: hidden;
    }}
    div[data-testid="stExpander"] summary {{
        background: {DEEP}; padding: 12px 16px;
    }}
    div[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] summary svg {{
        color: #FFFFFF !important; fill: #FFFFFF !important; font-weight: 600;
    }}

    .dti-wrap {{
        border: 1px solid {BORDER}; border-radius: 16px; overflow: hidden;
        background: {CARD}; box-shadow: 0 4px 14px rgba(167,139,250,0.12);
    }}
    .dti-table {{ width: 100%; border-collapse: collapse; }}
    .dti-table th {{
        background: {DEEP}; color: #FFFFFF !important; padding: 13px 14px;
        text-align: left; font-weight: 600; font-size: 0.86rem;
        border-right: 1px solid rgba(255,255,255,0.35);
    }}
    .dti-table td {{
        padding: 12px 14px; border-bottom: 1px solid #D9CCF5; border-right: 1px solid #E4D9FB;
        color: {TEXT}; font-size: 0.92rem; vertical-align: middle;
    }}
    .dti-table th:last-child, .dti-table td:last-child {{ border-right: none; }}
    .dti-table tr:nth-child(even) td {{ background: #FAF7FF; }}
    .dti-table tr:last-child td {{ border-bottom: none; }}
    .dti-table td.rank {{ font-weight: 700; color: {DEEP}; width: 60px; }}
    .dti-table td.bank {{ font-weight: 600; }}
    .bar-cell {{ display: flex; align-items: center; gap: 10px; min-width: 130px; }}
    .bar-track {{ flex: 1; height: 10px; background: #EFE7FF; border-radius: 999px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: linear-gradient(90deg, #B79CFA, {DEEP}); border-radius: 999px; }}
    .bar-val {{ min-width: 48px; text-align: right; font-weight: 600; font-size: 0.85rem; }}

    .coverage-good {{ color: #5B3FB5; font-weight: 700; }}
    .coverage-warn {{ color: #9B6B00; font-weight: 700; }}
    .nd {{ color: #9A8FB5; font-style: italic; }}

    div[data-testid="stMetricDelta"] {{
        background: #EFE7FF !important; border-radius: 999px; padding: 2px 10px;
    }}
    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] * {{
        color: {DEEP} !important; fill: {DEEP} !important; font-weight: 600;
    }}
    hr {{ border-color: {BORDER}; }}
</style>
""", unsafe_allow_html=True)


def section(title, desc=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if desc:
        st.markdown(f'<div class="section-desc">{desc}</div>', unsafe_allow_html=True)


def note(html):
    st.markdown(f'<div class="note">{html}</div>', unsafe_allow_html=True)


def insight(html):
    st.markdown(f'<div class="insight"><b>Nhận xét:</b> {html}</div>', unsafe_allow_html=True)


def hex_to_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def style_fig(fig, title, height=430, cartesian=True):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=15, color=DEEP), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FBF9FF",
        font=dict(color=DEEP, size=12),
        height=height,
        margin=dict(l=20, r=20, t=70, b=30),
        legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor=BORDER, borderwidth=1,
                    font=dict(color=DEEP), title=dict(font=dict(color=DEEP))),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=BORDER, font=dict(color=DEEP)),
        modebar=dict(color=DEEP, activecolor="#5B3FB5", bgcolor="rgba(0,0,0,0)"),
    )
    if cartesian:
        fig.update_xaxes(tickfont=dict(color=DEEP), title_font=dict(color=DEEP), linecolor=BORDER)
        fig.update_yaxes(tickfont=dict(color=DEEP), title_font=dict(color=DEEP), linecolor=BORDER)
    return fig


def maturity_level(score):
    if pd.isna(score):
        return "N/D"
    score = float(score)
    if score < 25:
        return "Mức 1 – Khởi động"
    elif score < 50:
        return "Mức 2 – Bắt đầu"
    elif score < 75:
        return "Mức 3 – Hình thành"
    elif score < 100:
        return "Mức 4 – Nâng cao"
    return "Mức 5 – Dẫn dắt"


# ==========================================
# 3. HEADER
# ==========================================
st.markdown("""
<div class="hero">
    <h1>Dashboard Xếp Hạng Chuyển Đổi Số Ngân Hàng (DTI)</h1>
    <p><b>Môn học:</b> Ngân hàng số &nbsp;|&nbsp; <b>Đối tượng đánh giá:</b> Vietcombank, VPBank, ACB, OCB, Agribank</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. ĐỌC DỮ LIỆU ĐÃ CHỐT
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_FILE = os.path.join(DATA_DIR, "scoring_data.csv")

if not os.path.exists(CSV_FILE):
    st.error("Chưa có data/scoring_data.csv. Hãy chạy main.py để tạo bảng điểm từ các bằng chứng đã duyệt.")
    st.stop()

df = pd.read_csv(CSV_FILE)
view_mode = st.radio(
    "Chế độ kết quả",
    ["Xếp hạng tham khảo — đủ 5 ngân hàng", "Kết quả chính thức — chỉ bằng chứng đã duyệt"],
    horizontal=True,
    key="ranking_view_mode",
)
is_provisional = view_mode.startswith("Xếp hạng tham khảo")
if is_provisional:
    from main import build_provisional_scoring_table

    df = build_provisional_scoring_table()
    st.warning(
        "Đây là bảng xếp hạng tham khảo để so sánh đủ 5 ngân hàng. Điểm đề xuất được ghép với bằng chứng ứng viên có nguồn và vị trí tra cứu; "
        "bằng chứng chưa được duyệt độc lập nên thứ hạng chưa phải kết quả chính thức. Tiêu chí định lượng thiếu tỷ lệ đã xác nhận vẫn để N/D.",
        icon="⚠️",
    )
else:
    st.info("Đang xem kết quả chính thức; chỉ tính bằng chứng đã duyệt. Ngân hàng chưa đủ ngưỡng sẽ hiện N/D và không có hạng.")

# Chuẩn hóa tên cột từ bộ dữ liệu mới
pillar_cols = ["Customer", "Strategy", "Technology", "Operations", "Culture", "Data"]
pillar_names = [
    "P1: Khách hàng",
    "P2: Chiến lược",
    "P3: Công nghệ",
    "P4: Vận hành",
    "P5: Văn hóa",
    "P6: Dữ liệu",
]

score_column_map = {p: f"{p}_Score" for p in pillar_cols}
for pillar, source_col in score_column_map.items():
    if source_col in df.columns:
        df[pillar] = df[source_col]
if "DTI_Total_Score" in df.columns:
    df["DTI"] = df["DTI_Total_Score"]
if "Data_Coverage" in df.columns:
    df["Coverage"] = df["Data_Coverage"] / 100
for c in pillar_cols + ["DTI", "Criteria_Available", "Coverage"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.sort_values(["Rank_Eligible", "DTI"], ascending=[False, False], na_position="last").reset_index(drop=True)
if "Rank" not in df.columns:
    df["Rank"] = pd.NA
df["Maturity"] = df["DTI"].apply(maturity_level)

# ==========================================
# 5. METRICS TỔNG QUAN
# ==========================================
top_df = df.head(5)
metric_cols = st.columns(len(top_df))
for mc, (_, r) in zip(metric_cols, top_df.iterrows()):
    mc.metric(
        f"{'TOP ' + str(int(r['Rank'])) if pd.notna(r['Rank']) else 'Chưa đủ điều kiện'}",
        f"{r['Bank']}",
        f"{r['DTI']:.2f} điểm" if pd.notna(r['DTI']) else "N/D",
        delta_color="off"
    )
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. BẢNG XẾP HẠNG
# ==========================================
section(
    "Bảng xếp hạng tổng hợp DTI" + (" — THAM KHẢO" if is_provisional else " — CHÍNH THỨC"),
    f"Đánh giá {len(df)} ngân hàng theo 6 trụ cột. Điều kiện xếp hạng là ít nhất 12/19 tiêu chí và có dữ liệu ở cả 6 trụ cột."
)

# Bảng HTML giữ nguyên phong cách cũ, chỉ đổi sang 6 trụ cột mới.
def render_table(d):
    cols = ["Hạng", "Ngân Hàng", "Tổng Điểm DTI", "Mức trưởng thành", "Coverage"] + pillar_names

    def bar(v):
        if pd.isna(v):
            return '<span class="nd">N/D</span>'
        v = float(v)
        return (
            f'<div class="bar-cell"><div class="bar-track"><div class="bar-fill" '
            f'style="width:{max(0, min(v, 100))}%"></div></div>'
            f'<span class="bar-val">{v:.2f}</span></div>'
        )

    head = "".join(f"<th>{c}</th>" for c in cols)
    rows = ""
    for _, r in d.iterrows():
        coverage = float(r["Coverage"]) * 100 if float(r["Coverage"]) <= 1 else float(r["Coverage"])
        coverage_class = "coverage-good" if coverage >= 75 else "coverage-warn"
        rows += (
            "<tr>"
            f'<td class="rank">{int(r["Rank"]) if pd.notna(r["Rank"]) else "N/A"}</td>'
            f'<td class="bank">{r["Bank"]}</td>'
            f'<td>{bar(r["DTI"])}</td>'
            f'<td>{r["Maturity"]}</td>'
            f'<td class="{coverage_class}">{coverage:.1f}% ({int(r["Criteria_Available"])}/19)</td>'
            + "".join(f"<td>{bar(r[c])}</td>" for c in pillar_cols)
            + "</tr>"
        )

    st.markdown(
        f'<div class="dti-wrap"><table class="dti-table"><thead><tr>{head}</tr></thead>'
        f'<tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True
    )


render_table(df)
note(
    "<b>Cách đọc:</b> DTI là điểm tổng hợp trên thang 100. "
    "Coverage chỉ phản ánh tỷ lệ tiêu chí có dữ liệu, không cộng điểm vào DTI. "
    "N/D được giữ là thiếu dữ liệu và không bị quy về 0."
)

# ==========================================
# 7. BIỂU ĐỒ 1 & 2
# ==========================================
section("Trực quan hóa kết quả đánh giá")
col_a, col_b = st.columns(2)

with col_a:
    fig_bar = px.bar(
        df, x="Bank", y="DTI", color="Bank", text_auto=".2f",
        color_discrete_sequence=BANK_COLORS,
        labels={"Bank": "Ngân hàng", "DTI": "Điểm DTI tổng hợp (0–100)"},
    )
    fig_bar.update_traces(textposition="outside", marker_line_color="#FFFFFF", marker_line_width=2,
                          textfont=dict(color=DEEP))
    fig_bar.update_layout(showlegend=False, yaxis_range=[0, 105])
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(gridcolor="#EDE6FB")
    style_fig(fig_bar, "Biểu đồ cột: Tổng điểm DTI của từng ngân hàng (thang 100)")
    st.plotly_chart(fig_bar, use_container_width=True)
    note(
        "<b>Biểu đồ này cho biết:</b> vị thế tổng thể về chuyển đổi số của mỗi ngân hàng.<br>"
        "<b>Cách đọc:</b> cột càng cao thì điểm DTI càng cao."
    )
    eligible_df = df[df["Rank_Eligible"].astype(bool) & df["DTI"].notna()]
    if not eligible_df.empty:
        leader = eligible_df.iloc[0]
        insight(f"<b>{leader['Bank']}</b> đang đứng đầu nhóm đủ điều kiện với {leader['DTI']:.2f} điểm.")
    else:
        insight("Chưa có ngân hàng đủ điều kiện xếp hạng. Các điểm trụ cột và độ phủ vẫn được hiển thị để rà soát dữ liệu.")

with col_b:
    categories = pillar_names
    fig_radar = go.Figure()
    for i, (_, row) in enumerate(df.iterrows()):
        color = BANK_COLORS[i % len(BANK_COLORS)]
        vals = [row[c] if not pd.isna(row[c]) else None for c in pillar_cols]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=row["Bank"],
            line=dict(color=color, width=2),
            fillcolor=hex_to_rgba(color, 0.22),
        ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#FBF9FF",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E4D9FB", linecolor="#E4D9FB",
                            tickfont=dict(color=DEEP)),
            angularaxis=dict(gridcolor="#E4D9FB", linecolor="#E4D9FB", tickfont=dict(color=DEEP)),
        ),
        showlegend=True,
    )
    style_fig(fig_radar, "Biểu đồ mạng nhện: So sánh năng lực theo 6 trụ cột DTI", cartesian=False)
    st.plotly_chart(fig_radar, use_container_width=True)
    note(
        "<b>Biểu đồ này cho biết:</b> hình dạng năng lực của từng ngân hàng theo 6 trụ cột. "
        "Mỗi đỉnh càng xa tâm thì điểm càng cao."
    )
    available_pillars = df.iloc[0][pillar_cols].dropna()
    if not available_pillars.empty:
        best_pillar = available_pillars.astype(float).idxmax()
        best_name = pillar_names[pillar_cols.index(best_pillar)]
        insight(f"Điểm trụ cột cao nhất của <b>{df.iloc[0]['Bank']}</b> là <b>{best_name}</b> ({df.iloc[0][best_pillar]:.2f} điểm).")

# ==========================================
# 8. BIỂU ĐỒ 3 & 4
# ==========================================
col_c, col_d = st.columns(2)

with col_c:
    df_long = df.melt(id_vars="Bank", value_vars=pillar_cols, var_name="Pillar", value_name="Score")
    df_long["Pillar"] = df_long["Pillar"].map(dict(zip(pillar_cols, pillar_names)))
    fig_group = px.bar(
        df_long, x="Pillar", y="Score", color="Bank", barmode="group",
        color_discrete_sequence=BANK_COLORS,
        labels={"Pillar": "Trụ cột đánh giá", "Score": "Điểm trụ cột (0–100)", "Bank": "Ngân hàng"},
    )
    fig_group.update_xaxes(showgrid=False)
    fig_group.update_yaxes(gridcolor="#EDE6FB", range=[0, 105])
    style_fig(fig_group, "Biểu đồ cột nhóm: Điểm từng trụ cột của các ngân hàng")
    st.plotly_chart(fig_group, use_container_width=True)
    note(
        "<b>Biểu đồ này cho biết:</b> trong cùng một trụ cột, ngân hàng nào có điểm cao hơn. "
        "Mỗi màu tương ứng một ngân hàng."
    )
    leaders = []
    for col, name in zip(pillar_cols, pillar_names):
        valid = df[col].dropna()
        if len(valid):
            bank = df.loc[valid.idxmax(), "Bank"]
            leaders.append(f"{name.split(':')[0]}: <b>{bank}</b>")
    insight("Ngân hàng dẫn đầu từng trụ cột: " + " &nbsp;|&nbsp; ".join(leaders) + ".")

with col_d:
    df_stack = df.copy()
    fig_stack = go.Figure()
    weight = 1 / 6
    for i, (col, name) in enumerate(zip(pillar_cols, pillar_names)):
        vals = df_stack[col]
        fig_stack.add_trace(go.Bar(
            y=df_stack["Bank"], x=vals * weight, name=name, orientation="h",
            marker=dict(color=PILLAR_COLORS[i], line=dict(color="#FFFFFF", width=1.5)),
            text=[f"{v * weight:.1f}" if pd.notna(v) else "" for v in vals], textposition="inside", textfont=dict(color=DEEP),
            hovertemplate="%{y}<br>" + name + ": %{x:.2f} điểm đóng góp<extra></extra>",
        ))
    fig_stack.update_layout(barmode="stack", yaxis=dict(autorange="reversed"))
    fig_stack.update_xaxes(title="Điểm đóng góp vào tổng DTI (mỗi trụ cột × 1/6)", gridcolor="#EDE6FB")
    fig_stack.update_yaxes(title="Ngân hàng", showgrid=False)
    style_fig(fig_stack, "Biểu đồ cột chồng: Cơ cấu đóng góp của 6 trụ cột vào tổng điểm DTI")
    st.plotly_chart(fig_stack, use_container_width=True)
    note(
        "<b>Biểu đồ này cho biết:</b> tổng điểm DTI được tạo nên từ 6 trụ cột. "
        "Mỗi đoạn đã nhân trọng số 1/6; tổng độ dài thanh chính là điểm DTI."
    )
    weakest_bank = df.iloc[-1]
    valid_weak = weakest_bank[pillar_cols].dropna()
    if len(valid_weak):
        weak_col = valid_weak.astype(float).idxmin()
        weak_name = pillar_names[pillar_cols.index(weak_col)]
        insight(
            f"<b>{weakest_bank['Bank']}</b> đang yếu nhất ở <b>{weak_name}</b> "
            f"({weakest_bank[weak_col]:.2f} điểm)."
        )

# ==========================================
# 9. BỘ TIÊU CHÍ & PHÂN TÍCH
# ==========================================
from submetrics_section import render_submetrics
render_submetrics(
    df,
    section,
    note,
    insight,
    style_fig,
    BANK_COLORS,
    hex_to_rgba,
)

st.markdown("---")
with st.expander("Xem phương pháp tính điểm và cấu trúc bộ tiêu chí"):
    st.markdown("""
    **Khung tham chiếu:** 6 trụ cột của Quyết định 2158/QĐ-BTTTT, được nhóm điều chỉnh theo đặc thù ngân hàng và khả năng thu thập dữ liệu công khai.

    **19 tiêu chí:**
    - **P1 – Khách hàng:** C1 Bao phủ kênh/dịch vụ số; C2 Mức độ khách hàng sử dụng kênh số; C3 Hỗ trợ khách hàng trên kênh số.
    - **P2 – Chiến lược:** S1 Chiến lược & lộ trình CĐS; S2 Đầu tư/ngân sách CĐS; S3 Hệ sinh thái & đối tác số.
    - **P3 – Công nghệ:** T1 eKYC & sinh trắc học; T2 Cho vay số; T3 AI/GenAI; T4 Open Banking/API.
    - **P4 – Vận hành:** O1 Giao dịch trên kênh số; O2 Số hóa/tự động hóa quy trình; O3 Vận hành dịch vụ số.
    - **P5 – Văn hóa:** H1 Đào tạo & năng lực số; H2 Đổi mới sáng tạo; H3 Quản trị thay đổi & văn hóa số.
    - **P6 – Dữ liệu:** D1 Kiến trúc & tích hợp dữ liệu; D2 Quản trị & an toàn dữ liệu; D3 Phân tích dữ liệu & cá nhân hóa.

    **Tính điểm:**
    - Tiêu chí định lượng có số liệu phù hợp: dùng giá trị thực tế khi có thể quy đổi trực tiếp về thang 0–100.
    - Tiêu chí định tính: rubric nội bộ 5 mức **0 / 30 / 50 / 70 / 100**.
    - Điểm trụ cột = trung bình cộng các tiêu chí **có dữ liệu**, không biến N/D thành 0.
    - DTI = trung bình cộng của 6 trụ cột, mỗi trụ cột **1/6 = 16,67%**.
    - Coverage chỉ dùng để minh bạch mức độ đầy đủ dữ liệu, **không cộng vào điểm**.

    **Mức trưởng thành:**
    - 0–<25: Mức 1 – Khởi động
    - 25–<50: Mức 2 – Bắt đầu
    - 50–<75: Mức 3 – Hình thành
    - 75–<100: Mức 4 – Nâng cao
    - 100: Mức 5 – Dẫn dắt

    **Nguyên tắc dữ liệu:** không dùng dữ liệu giả định, không median imputation, không tính điểm từ số lượt tải Google Play, số bài báo hoặc số lần xuất hiện từ khóa.
    """)
