# DTI ngân hàng – snapshot đánh giá 2025

Dự án đánh giá 5 ngân hàng bằng bộ chỉ số thích nghi gồm 6 trụ cột và 19 tiêu chí, tham chiếu khung Quyết định 2158/QĐ-BTTTT. Kết quả không phải điểm DBI chính thức của Bộ TT&TT.

## Quy tắc đã chốt

- Ngân hàng: Vietcombank, VPBank, ACB, OCB và Agribank.
- Kỳ đánh giá: 2025. Bằng chứng ngoài kỳ không được tính vào điểm snapshot 2025.
- Sáu trụ cột/19 tiêu chí: Customer (C1–C3), Strategy (S1–S3), Technology (T1–T4), Operations (O1–O3), Culture (H1–H3), Data (D1–D3).
- Định tính: 0/30/50/70/100. C2 và O1: điểm bằng tỷ lệ phần trăm khi có tử số và mẫu số/phạm vi được xác nhận. C3 là proxy Google Play: rating/5×100 và tỷ lệ đánh giá tích cực; lấy trung bình các phần có dữ liệu, chỉ khi bằng chứng được duyệt thuộc kỳ 2025.
- Chỉ bằng chứng có `Evidence_Status=Approved`, nội dung/nguồn/ngày thu thập và URL hoặc số trang mới được dùng chấm. Bằng chứng tự trích mặc định là `Candidate`.
- Không tìm thấy dữ liệu = N/D; không dùng số lượt tải, tin tức, số từ khóa, dữ liệu giả định hoặc median-imputation.
- Điểm trụ cột là trung bình các tiêu chí có dữ liệu. DTI chỉ được tính khi đủ cả 6 điểm trụ cột, theo trọng số đều 1/6. Chỉ xếp hạng khi có ít nhất 12/19 tiêu chí, đủ dữ liệu ở cả 6 trụ cột và có DTI hợp lệ.

## Chạy dự án

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirement.txt
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

Trên Windows, có thể chạy `.\run_app.ps1`. Lệnh này luôn dùng Python 3.12 trong `.venv`, tránh vô tình chạy môi trường cũ đã kích hoạt.

Pipeline tạo/cập nhật `data/evidence_data.csv`, `data/app_data.csv` và `data/scoring_data.csv`. Google Play là nguồn trực tuyến cho snapshot hiện tại; dữ liệu này được lưu kèm ngày thu thập và không tự đưa vào kỳ 2025.

## Quy trình duyệt và chấm

1. Mở `data/evidence_data.csv`; kiểm tra đoạn trích, trang và nguồn. Tự động trích xuất chỉ là bước tìm ứng viên.
2. Đổi `Evidence_Status` thành `Approved` sau khi xác minh. Với C2/O1, điền `Raw_Value` bằng tỷ lệ phần trăm và cả `Numerator`/`Denominator`. Với C3, thêm dòng `C3_RATING` (0–5) và/hoặc `C3_POSITIVE` (0–100), ghi bằng chứng, nguồn, ngày thu thập và duyệt đúng kỳ.
3. Điền điểm đã duyệt cho các tiêu chí còn lại vào `data/scoring_manual.csv`. Định tính chỉ nhận 0/30/50/70/100; C2/O1 nhận tỷ lệ 0–100. C3 được tính tự động từ các dòng bằng chứng đã duyệt.
4. Chạy lại `.\.venv\Scripts\python.exe main.py`. Chỉ `data/scoring_data.csv` là nguồn kết quả chính thức của dashboard.

Các điểm lấy từ `final_evidence_matrix.csv` đã được chép sang bảng nhập như điểm đề xuất; bằng chứng tương ứng vẫn ở trạng thái `Candidate`, một số dòng còn thiếu ngày thu thập/trang hoặc mẫu số. Hãy hoàn thiện dấu vết nguồn và duyệt từng dòng trước khi kỳ vọng điểm xuất hiện trong kết quả.

Khi chưa có điểm chính thức đã duyệt, dashboard hiển thị thêm bảng **Dự thảo** từ các điểm đề xuất và bằng chứng ứng viên kỳ 2025 có nội dung, nguồn và trang/URL tra cứu. Bảng này không đổi trạng thái bằng chứng và không thay thế `scoring_data.csv`; các tiêu chí định lượng thiếu tỷ lệ có tử số/mẫu số vẫn là N/D. Thứ hạng dự thảo chỉ dùng rà soát nội bộ.

`data/final_scoring.csv`, `data/final_evidence_matrix.csv` và `dti_banking_ranking_results.csv` là dữ liệu kết quả cũ được giữ lại để đối chiếu; dashboard không đọc các tệp này.

## Thành phần

- `main.py`: trích đoạn ứng viên từ BCTN, thu thập snapshot Google Play, xác thực điểm và tạo bảng điểm.
- `scoring_rules.py`: định nghĩa tiêu chí, tính trụ cột/DTI, mức trưởng thành và điều kiện xếp hạng.
- `app.py`: dashboard tổng hợp.
- `submetrics_section.py`: biểu đồ tiêu chí và tra cứu bằng chứng.
- `METHODOLOGY.md`: phương pháp và cách diễn giải kết quả.
