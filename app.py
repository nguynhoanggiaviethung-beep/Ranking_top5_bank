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

# Bảng màu pastel tím
TEXT = "#4A3F6B"        # chữ tím xám dịu
SUBTEXT = "#7C6FA0"
DEEP = "#7C5CD6"        # tím đậm cho tiêu đề bảng / expander
BG = "#F7F3FF"          # nền trang
CARD = "#FFFFFF"
BORDER = "#E4D9FB"
BANK_COLORS = ["#A78BFA", "#C4B5FD", "#F0ABFC", "#93C5FD", "#D8B4FE", "#FBCFE8", "#BAE6FD", "#DDD6FE"]
PILLAR_COLORS = ["#A78BFA", "#F0ABFC", "#93C5FD", "#FBCFE8"]

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
    div[data-testid="stExpander"] summary:hover {{ background: #6B49C4; }}
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
# 4. ĐỌC DỮ LIỆU
# ==========================================
CSV_FILE = "dti_banking_ranking_results.csv"

if not os.path.exists(CSV_FILE):
    st.error(f"Không tìm thấy file dữ liệu '{CSV_FILE}'. Hãy chạy file 'main.py' trước để xuất dữ liệu!")
    st.stop()

df = pd.read_csv(CSV_FILE)

pillar_cols = ["Pillar_1_Score", "Pillar_2_Score", "Pillar_3_Score", "Pillar_4_Score"]
pillar_names = ["P1: Quy mô App", "P2: Trải nghiệm CX", "P3: Hạ tầng & BCTN", "P4: Truyền thông"]

# ==========================================
# 5. METRICS TỔNG QUAN
# ==========================================
top_1 = df.iloc[0]

top_df = df.head(6)
metric_cols = st.columns(len(top_df))
for mc, (_, r) in zip(metric_cols, top_df.iterrows()):
    mc.metric(f"TOP {int(r['Rank'])} DTI", f"{r['Bank']}", f"{r['DTI_Total_Score']:.2f} điểm", delta_color="off")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. BẢNG XẾP HẠNG
# ==========================================
section("Bảng xếp hạng tổng hợp DTI",
        f"Đánh giá {len(df)} ngân hàng. Điểm tổng DTI là trung bình cộng của 4 trụ cột (mỗi trụ cột chiếm 25%), thang điểm 100.")

df_display = df.rename(columns={
    "Rank": "Hạng",
    "Bank": "Ngân Hàng",
    "DTI_Total_Score": "Tổng Điểm DTI",
    "Pillar_1_Score": "P1: Quy Mô App (25%)",
    "Pillar_2_Score": "P2: Trải Nghiệm CX (25%)",
    "Pillar_3_Score": "P3: Hạ Tầng & BCTN (25%)",
    "Pillar_4_Score": "P4: Truyền Thông (25%)",
})

def render_table(d):
    cols = ["Hạng", "Ngân Hàng", "Tổng Điểm DTI", "P1: Quy Mô App (25%)",
            "P2: Trải Nghiệm CX (25%)", "P3: Hạ Tầng & BCTN (25%)", "P4: Truyền Thông (25%)"]

    def bar(v):
        v = float(v)
        return (f'<div class="bar-cell"><div class="bar-track"><div class="bar-fill" '
                f'style="width:{max(0, min(v, 100))}%"></div></div><span class="bar-val">{v:.2f}</span></div>')

    head = "".join(f"<th>{c}</th>" for c in cols)
    rows = ""
    for _, r in d.iterrows():
        rows += ("<tr>"
                 f'<td class="rank">{int(r["Hạng"])}</td>'
                 f'<td class="bank">{r["Ngân Hàng"]}</td>'
                 + "".join(f"<td>{bar(r[c])}</td>" for c in cols[2:])
                 + "</tr>")
    st.markdown(f'<div class="dti-wrap"><table class="dti-table"><thead><tr>{head}</tr></thead>'
                f'<tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)


render_table(df_display)
note("<b>Cách đọc bảng:</b> thanh màu càng dài nghĩa là điểm càng cao. "
     "Hạng 1 là ngân hàng có tổng điểm DTI cao nhất. So sánh các cột P1–P4 để biết ngân hàng mạnh/yếu ở trụ cột nào.")

# ==========================================
# 7. BIỂU ĐỒ 1 & 2
# ==========================================
section("Trực quan hóa kết quả đánh giá")

col_a, col_b = st.columns(2)

# ---- Biểu đồ cột
with col_a:
    fig_bar = px.bar(
        df, x="Bank", y="DTI_Total_Score", color="Bank", text_auto=".2f",
        color_discrete_sequence=BANK_COLORS,
        labels={"Bank": "Ngân hàng", "DTI_Total_Score": "Điểm DTI tổng hợp (0–100)"},
    )
    fig_bar.update_traces(textposition="outside", marker_line_color="#FFFFFF", marker_line_width=2,
                          textfont=dict(color=DEEP))
    fig_bar.update_layout(showlegend=False, yaxis_range=[0, 105])
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(gridcolor="#EDE6FB")
    style_fig(fig_bar, "Biểu đồ cột: Tổng điểm DTI của từng ngân hàng (thang 100)")
    st.plotly_chart(fig_bar, use_container_width=True)
    note("<b>Biểu đồ này cho biết:</b> vị thế tổng thể về chuyển đổi số của mỗi ngân hàng.<br>"
         "<b>Cách đọc:</b> trục ngang là ngân hàng, trục dọc là điểm DTI (0–100). Cột càng cao thì mức độ chuyển đổi số càng tốt; "
         "con số trên đầu cột là điểm chính xác.")
    gap = top_1["DTI_Total_Score"] - df.iloc[-1]["DTI_Total_Score"]
    insight(f"<b>{top_1['Bank']}</b> dẫn đầu với {top_1['DTI_Total_Score']:.2f} điểm, "
            f"cao hơn <b>{df.iloc[-1]['Bank']}</b> (hạng cuối) {gap:.2f} điểm.")

# ---- Radar
with col_b:
    categories = ["Quy mô App (P1)", "Trải nghiệm CX (P2)", "Hạ tầng BCTN (P3)", "Truyền thông (P4)"]
    fig_radar = go.Figure()
    for i, (_, row) in enumerate(df.iterrows()):
        color = BANK_COLORS[i % len(BANK_COLORS)]
        vals = [row[c] for c in pillar_cols]
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
    style_fig(fig_radar, "Biểu đồ mạng nhện: So sánh năng lực theo 4 trụ cột DTI", cartesian=False)
    st.plotly_chart(fig_radar, use_container_width=True)
    note("<b>Biểu đồ này cho biết:</b> hình dạng năng lực của từng ngân hàng, mạnh ở đâu, yếu ở đâu.<br>"
         "<b>Cách đọc:</b> mỗi đỉnh là một trụ cột, càng xa tâm điểm càng cao (tối đa 100). "
         "Vùng màu phủ rộng và đều là ngân hàng phát triển cân bằng; vùng lệch về một phía là ngân hàng chỉ mạnh một mảng. "
         "Bấm vào tên ngân hàng ở chú giải để ẩn/hiện để dễ so sánh.")
    best_pillar = top_1[pillar_cols].astype(float).idxmax()
    best_name = pillar_names[pillar_cols.index(best_pillar)]
    insight(f"Điểm mạnh nhất của <b>{top_1['Bank']}</b> là <b>{best_name}</b> ({top_1[best_pillar]:.2f} điểm).")

# ==========================================
# 8. BIỂU ĐỒ 3 & 4
# ==========================================
col_c, col_d = st.columns(2)

# ---- Cột cụm theo trụ cột
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
    note("<b>Biểu đồ này cho biết:</b> trong cùng một trụ cột, ngân hàng nào đứng đầu.<br>"
         "<b>Cách đọc:</b> mỗi nhóm cột là một trụ cột (P1–P4); mỗi màu là một ngân hàng. "
         "Nhìn cột cao nhất trong từng nhóm để biết ngân hàng dẫn đầu của trụ cột đó.")
    leaders = []
    for col, name in zip(pillar_cols, pillar_names):
        leaders.append(f"{name.split(':')[0]}: <b>{df.loc[df[col].idxmax(), 'Bank']}</b>")
    insight("Ngân hàng dẫn đầu từng trụ cột: " + " &nbsp;|&nbsp; ".join(leaders) + ".")

# ---- Cột chồng đóng góp
with col_d:
    df_stack = df.copy()
    fig_stack = go.Figure()
    for i, (col, name) in enumerate(zip(pillar_cols, pillar_names)):
        fig_stack.add_trace(go.Bar(
            y=df_stack["Bank"], x=df_stack[col] * 0.25, name=name, orientation="h",
            marker=dict(color=PILLAR_COLORS[i], line=dict(color="#FFFFFF", width=1.5)),
            text=[f"{v * 0.25:.1f}" for v in df_stack[col]], textposition="inside", textfont=dict(color=DEEP),
            hovertemplate="%{y}<br>" + name + ": %{x:.2f} điểm<extra></extra>",
        ))
    fig_stack.update_layout(barmode="stack", yaxis=dict(autorange="reversed"))
    fig_stack.update_xaxes(title="Điểm đóng góp vào tổng DTI (mỗi trụ cột × 25%)", gridcolor="#EDE6FB")
    fig_stack.update_yaxes(title="Ngân hàng", showgrid=False)
    style_fig(fig_stack, "Biểu đồ cột chồng: Cơ cấu đóng góp của 4 trụ cột vào tổng điểm DTI")
    st.plotly_chart(fig_stack, use_container_width=True)
    note("<b>Biểu đồ này cho biết:</b> tổng điểm DTI của mỗi ngân hàng được tạo nên từ những trụ cột nào.<br>"
         "<b>Cách đọc:</b> mỗi thanh ngang là một ngân hàng, được chia thành 4 đoạn màu tương ứng 4 trụ cột "
         "(đã nhân trọng số 25%). Tổng độ dài thanh chính là điểm DTI; đoạn nào dài hơn nghĩa là trụ cột đó đóng góp nhiều hơn.")
    weakest_bank = df.iloc[-1]
    weak_col = weakest_bank[pillar_cols].astype(float).idxmin()
    weak_name = pillar_names[pillar_cols.index(weak_col)]
    insight(f"<b>{weakest_bank['Bank']}</b> đang yếu nhất ở <b>{weak_name}</b> "
            f"({weakest_bank[weak_col]:.2f} điểm), đây là trụ cột cần ưu tiên cải thiện.")

# ==========================================
# 9. BỘ TIÊU CHÍ
# ==========================================
st.markdown("---")
with st.expander("Xem chi tiết cấu trúc bộ tiêu chí xếp hạng DTI"):
    st.write("""
    - **Trụ cột 1 (25%):** Mức độ phổ biến & quy mô người dùng (cào lượt tải & lượt đánh giá từ Google Play Store).
    - **Trụ cột 2 (25%):** Chất lượng trải nghiệm người dùng CX (cào điểm đánh giá sao Rating Star).
    - **Trụ cột 3 (25%):** Năng lực hạ tầng & sản phẩm số (quét từ khóa CĐS trong file Báo cáo thường niên PDF 2025).
    - **Trụ cột 4 (25%):** Truyền thông & độ phủ thương hiệu số (cào số bài viết CĐS trên báo chí qua Google News RSS).
    """)