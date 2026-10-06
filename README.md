# DTI ngân hàng – snapshot đánh giá 2025

Dự án đánh giá 5 ngân hàng bằng bộ chỉ số thích nghi gồm 6 trụ cột và 19 tiêu chí, tham chiếu khung Quyết định 2158/QĐ-BTTTT. Kết quả không phải điểm DBI chính thức của Bộ TT&TT.

## Quy tắc đã chốt

- Ngân hàng: Vietcombank, VPBank, ACB, OCB và Agribank, theo mẫu yêu cầu của đề tài.
- Kỳ đánh giá: 2025. Bằng chứng ngoài kỳ không được tính vào điểm snapshot 2025.
- Sáu trụ cột/19 tiêu chí: Customer (C1–C3), Strategy (S1–S3), Technology (T1–T4), Operations (O1–O3), Culture (H1–H3), Data (D1–D3).
- Định tính: 0/30/50/70/100. C2 và O1: điểm bằng tỷ lệ phần trăm khi có phạm vi/tử số/mẫu số được xác nhận. C3 đánh giá mức độ hỗ trợ khách hàng trên kênh số dựa trên bằng chứng kỳ 2025.
- Chỉ bằng chứng có `Evidence_Status=Approved`, nội dung/nguồn/ngày thu thập và URL hoặc số trang mới được dùng chấm. Bằng chứng tự trích mặc định là `Candidate`.
- Không tìm thấy dữ liệu = N/D; không dùng số lượt tải, tin tức, số từ khóa, dữ liệu giả định hoặc median-imputation.
- Điểm trụ cột là trung bình các tiêu chí có dữ liệu. DTI chỉ được tính khi đủ cả 6 điểm trụ cột, theo trọng số đều 1/6. Một ngân hàng chỉ đủ điều kiện xếp hạng khi có ít nhất 12/19 tiêu chí và dữ liệu ở cả 6 trụ cột; chỉ công bố thứ hạng khi có ít nhất 2 ngân hàng đủ điều kiện để so sánh.
- Dashboard có hai chế độ: **Xếp hạng tham khảo — đủ 5 ngân hàng** dùng điểm đề xuất và bằng chứng ứng viên có thể truy xuất; **Kết quả chính thức** chỉ dùng bằng chứng đã duyệt. Chế độ tham khảo không thay thế kết luận chính thức.

## Chạy dự án

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirement.txt
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

Trên Windows, có thể chạy `.\run_app.ps1`. Lệnh này luôn dùng Python 3.12 trong `.venv`, tránh vô tình chạy môi trường cũ đã kích hoạt.

Pipeline tạo/cập nhật `data/evidence_data.csv`, `data/app_data.csv`, `data/scoring_data.csv`, `data/scoring_provisional_data.csv` và ma trận rà soát `data/evidence_review_matrix.csv`. Bảng chính thức chỉ dùng bằng chứng `Approved`; bảng dự thảo dùng các điểm đề xuất và bằng chứng ứng viên có thể truy xuất. Google Play được giữ làm dữ liệu tham khảo hiện tại, không tự đưa ngược vào kỳ 2025.

## Quy trình duyệt và chấm

1. Mở `data/evidence_data.csv`; kiểm tra trích dẫn, trang, URL và kỳ dữ liệu. Trích xuất tự động chỉ tạo bằng chứng ứng viên.
2. Chuyển `Evidence_Status` thành `Approved` sau khi nhóm đối chiếu nguồn. Với C2/O1, chỉ chấm tỷ lệ được công bố trực tiếp với phạm vi/mẫu số rõ. C3 dùng rubric định tính mới về hỗ trợ khách hàng số, dựa trên báo cáo cùng kỳ.
3. Điền điểm đã duyệt cho các tiêu chí vào `data/scoring_manual.csv`. Định tính chỉ nhận 0/30/50/70/100; C2/O1 nhận tỷ lệ 0–100.
4. Chạy lại `.\.venv\Scripts\python.exe main.py`. Pipeline làm mới cả hai bảng và in nhãn riêng để tránh nhầm kết quả dự thảo với chính thức. Chỉ `data/scoring_data.csv` là nguồn kết quả chính thức của dashboard.

Các nguồn, trang, trạng thái rà soát và ghi chú chấm được lưu trong `data/evidence_data.csv`. Những đoạn trích tự động chỉ là ứng viên; ngân hàng/tiêu chí chưa có bằng chứng được duyệt sẽ hiển thị N/D cho đến khi nhóm xác minh nguồn và cập nhật trạng thái.

Khi chưa có điểm chính thức đã duyệt, dashboard hiển thị thêm bảng **Dự thảo** từ các điểm đề xuất và bằng chứng ứng viên kỳ 2025 có nội dung, nguồn và trang/URL tra cứu. Bảng này không đổi trạng thái bằng chứng và không thay thế `scoring_data.csv`; các tiêu chí định lượng thiếu tỷ lệ có tử số/mẫu số vẫn là N/D. Thứ hạng dự thảo chỉ dùng rà soát nội bộ.

`data/final_scoring.csv`, `data/final_evidence_matrix.csv` và `dti_banking_ranking_results.csv` được đồng bộ với kết quả gần nhất; dashboard đọc `data/scoring_data.csv`.

## Thành phần

- `main.py`: trích đoạn ứng viên từ BCTN, thu thập snapshot Google Play, xác thực điểm và tạo bảng điểm.
- `scoring_rules.py`: định nghĩa tiêu chí, tính trụ cột/DTI, mức trưởng thành và điều kiện xếp hạng.
- `app.py`: dashboard tổng hợp.
- `submetrics_section.py`: biểu đồ tiêu chí và tra cứu bằng chứng.
- `METHODOLOGY.md`: phương pháp và cách diễn giải kết quả.
