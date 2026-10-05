"""
Phần dashboard: Phân tích tiêu chí thành phần theo từng trụ cột DBI (6 trụ cột – các tiêu chí theo bộ chỉ số).

Cách dùng trong app.py (đặt trước phần "9. BỘ TIÊU CHÍ"):

    from submetrics_section import render_submetrics
    render_submetrics(df, section, note, insight, style_fig, BANK_COLORS, hex_to_rgba)

df là kết quả của scoring_rules.rank_banks(...) (hoặc bảng có cột Bank + C1..D3).
- Điểm của mỗi tiêu chí là điểm 0–100 theo rubric QĐ 2158 (KHÔNG dùng Min-Max).
- Ô trống/NaN = N/D (không có bằng chứng đủ mạnh), không phải 0 và không bị điền giá trị.
- Không dùng Downloads, số bài báo, từ khóa, News để chấm.
"""
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from scoring_rules import PILLARS, CRITERIA, MIN_CRITERIA_FOR_RANK


def _build_structure():
    """{tên tab: [(mã tiêu chí, nhãn hiển thị), ...]} lấy trực tiếp từ scoring_rules."""
    out = {}
    for key, p in PILLARS.items():
        tab = f"{key}: {p['name']}"
        out[tab] = [(c, f"{c} · {CRITERIA[c]['name']}") for c in p["criteria"]]
    return out


SUBMETRICS = _build_structure()


def _prepare(df):
    d = df.copy()
    for c in CRITERIA:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")   # N/D giữ nguyên là NaN
    return d


def _available(df, items):
    return [(c, l) for c, l in items if c in df.columns]


def _leaders(df, avail):
    parts = []
    for c, l in avail:
        s = df[c].dropna()
        if s.empty:
            parts.append(f"{l}: <b>N/D</b>")
            continue
        top = df.loc[df[c] == s.max(), "Bank"].tolist()      # đồng điểm -> liệt kê tất cả
        parts.append(f"{l}: <b>{' = '.join(top)}</b> ({s.max():.0f})")
    return parts


def render_submetrics(df, section, note, insight, style_fig, bank_colors, hex_to_rgba):
    section("Phân tích chi tiết từng tiêu chí thành phần",
            f"6 trụ cột được tách thành {len(CRITERIA)} tiêu chí (điểm 0–100 theo rubric). "
            "Ô N/D nghĩa là chưa có bằng chứng đủ mạnh để chấm – không đồng nghĩa với 0 điểm.")

    df = _prepare(df)
    all_cols = [c for items in SUBMETRICS.values() for c, _ in items]
    present = [c for c in all_cols if c in df.columns]
    if not present:
        st.warning(
            "Bảng điểm chưa có cột điểm tiêu chí nên chưa vẽ được biểu đồ. "
            "Cần các cột: " + ", ".join(f"`{c}`" for c in all_cols)
        )
        return

    # ---------- Heatmap tổng quan (N/D hiển thị rõ) ----------
    label_map = {c: f"{c} · {CRITERIA[c]['name']}" for c in all_cols}
    z = [[None if pd.isna(v) else float(v) for v in row] for row in df[present].values]
    txt = [["N/D" if v is None else f"{v:.0f}" for v in row] for row in z]
    fig_heat = go.Figure(go.Heatmap(
        z=z,
        x=[label_map[c] for c in present],
        y=df["Bank"],
        colorscale=[[0, "#F3EDFF"], [0.5, "#C4B5FD"], [1, "#7C5CD6"]],
        zmin=0, zmax=100,
        text=txt, texttemplate="%{text}",
        hoverongaps=False,
        hovertemplate="%{y}<br>%{x}: %{z:.1f}<extra></extra>",
        colorbar=dict(title="Điểm"),
    ))
    fig_heat.update_yaxes(autorange="reversed")
    fig_heat.update_xaxes(tickangle=-35)
    style_fig(fig_heat, f"Bản đồ nhiệt: điểm từng ngân hàng ở {len(CRITERIA)} tiêu chí (N/D = chưa đủ bằng chứng)",
              height=160 + 60 * len(df))
    st.plotly_chart(fig_heat, use_container_width=True)
    note("<b>Biểu đồ này cho biết:</b> toàn cảnh điểm mạnh/yếu của mỗi ngân hàng ở từng tiêu chí.<br>"
         "<b>Cách đọc:</b> mỗi hàng là một ngân hàng, mỗi cột là một tiêu chí; ô càng tím đậm thì điểm càng cao. "
         "Ô trống ghi <b>N/D</b> là không có dữ liệu/bằng chứng đủ mạnh và <b>không</b> được tính vào trung bình.")

    # ---------- Độ phủ dữ liệu (chỉ để minh bạch, không cộng điểm) ----------
    cov_cols = [c for c in ("Criteria_Available", "Data_Coverage", "Rank_Eligible") if c in df.columns]
    if cov_cols:
        cov = df[["Bank"] + cov_cols].rename(columns={
            "Bank": "Ngân hàng",
            "Criteria_Available": f"Số tiêu chí có dữ liệu (/{len(CRITERIA)})",
            "Data_Coverage": "Data Coverage (%)",
            "Rank_Eligible": "Đủ điều kiện xếp hạng",
        })
        with st.expander("Độ phủ dữ liệu (không cộng điểm)"):
            st.dataframe(cov.round(1), use_container_width=True, hide_index=True)
            st.caption(f"Điều kiện xếp hạng: ≥ {MIN_CRITERIA_FOR_RANK}/{len(CRITERIA)} tiêu chí và cả 6 trụ cột đều có ít nhất 1 tiêu chí.")

    # ---------- Tab theo từng trụ cột ----------
    tabs = st.tabs(list(SUBMETRICS.keys()))
    for tab, (pillar, items) in zip(tabs, SUBMETRICS.items()):
        with tab:
            avail = _available(df, items)
            if not avail:
                st.info("Chưa có dữ liệu thành phần cho trụ cột này. Cột cần có: "
                        + ", ".join(f"`{c}`" for c, _ in items))
                continue

            names = {c: l for c, l in avail}
            long = df.melt(id_vars="Bank", value_vars=[c for c, _ in avail],
                           var_name="Metric", value_name="Score")
            long["Metric"] = long["Metric"].map(names)
            long_valid = long.dropna(subset=["Score"])          # N/D không vẽ thành cột 0

            if long_valid.empty:
                st.info("Tất cả tiêu chí của trụ cột này đang là N/D.")
                continue

            col1, col2 = st.columns(2)

            with col1:
                fig_g = px.bar(
                    long_valid, x="Metric", y="Score", color="Bank", barmode="group",
                    color_discrete_sequence=bank_colors, text_auto=".0f",
                    labels={"Metric": "Tiêu chí", "Score": "Điểm (0–100)", "Bank": "Ngân hàng"},
                )
                fig_g.update_traces(textposition="outside", textfont=dict(color="#7C5CD6", size=10))
                fig_g.update_xaxes(showgrid=False)
                fig_g.update_yaxes(gridcolor="#EDE6FB", range=[0, 110])
                style_fig(fig_g, f"Cột nhóm: {pillar} – điểm theo từng tiêu chí")
                st.plotly_chart(fig_g, use_container_width=True)

            with col2:
                if len(avail) >= 3:
                    cats = [c for c, _ in avail]
                    fig_r = go.Figure()
                    for i, (_, row) in enumerate(df.iterrows()):
                        color = bank_colors[i % len(bank_colors)]
                        vals = [None if pd.isna(row[c]) else float(row[c]) for c in cats]
                        fig_r.add_trace(go.Scatterpolar(
                            r=vals + [vals[0]], theta=cats + [cats[0]], fill="toself",
                            connectgaps=False,
                            name=row["Bank"], line=dict(color=color, width=2),
                            fillcolor=hex_to_rgba(color, 0.2)))
                    fig_r.update_layout(polar=dict(
                        bgcolor="#FBF9FF",
                        radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E4D9FB",
                                        tickfont=dict(color="#7C5CD6")),
                        angularaxis=dict(gridcolor="#E4D9FB", tickfont=dict(color="#7C5CD6"))))
                    style_fig(fig_r, f"Mạng nhện: hình dạng năng lực trong {pillar}", cartesian=False)
                    st.plotly_chart(fig_r, use_container_width=True)
                else:
                    fig_h = px.bar(
                        long_valid, y="Bank", x="Score", color="Metric", barmode="group", orientation="h",
                        color_discrete_sequence=["#A78BFA", "#F0ABFC", "#93C5FD"], text_auto=".1f",
                        labels={"Bank": "Ngân hàng", "Score": "Điểm (0–100)", "Metric": "Tiêu chí"},
                    )
                    fig_h.update_xaxes(range=[0, 110], gridcolor="#EDE6FB")
                    fig_h.update_yaxes(autorange="reversed")
                    style_fig(fig_h, f"Cột ngang: ngân hàng theo {pillar}")
                    st.plotly_chart(fig_h, use_container_width=True)

            n_nd = int(long["Score"].isna().sum())
            note(f"<b>Cách đọc ({pillar}):</b> biểu đồ cột cho thấy ngân hàng nào dẫn đầu ở từng tiêu chí; "
                 "mạng nhện cho thấy hình dạng năng lực – vùng phủ rộng, đều nghĩa là phát triển cân bằng."
                 + (f"<br><b>Lưu ý:</b> có {n_nd} ô N/D trong trụ cột này; các ô đó không được vẽ và "
                    "không tính vào điểm trụ cột." if n_nd else ""))

            insight("Ngân hàng dẫn đầu từng tiêu chí – " + " &nbsp;|&nbsp; ".join(_leaders(df, avail)) + ".")

            with st.expander(f"Xem bảng điểm chi tiết {pillar}"):
                tbl = df[["Bank"] + [c for c, _ in avail]].rename(columns={"Bank": "Ngân hàng", **names})
                tbl = tbl.round(2).astype(object).where(tbl.notna(), "N/D")
                st.dataframe(tbl, use_container_width=True, hide_index=True)