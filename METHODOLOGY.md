# Bộ chỉ số DTI ngân hàng – phiên bản chốt

## 1. Tuyên bố phương pháp

Nhóm **không gọi đây là "điểm DBI chính thức"** của Quyết định 2158/QĐ-BTTTT.

Cách gọi chính xác trong báo cáo:

> **Bộ chỉ số đánh giá mức độ chuyển đổi số dành cho ngân hàng, tham chiếu khung 6 trụ cột của Quyết định 2158/QĐ-BTTTT và điều chỉnh tiêu chí thành phần theo đặc thù hoạt động ngân hàng và khả năng thu thập dữ liệu công khai.**

Quyết định 2158 cho phép các tổ chức khác tham khảo Bộ chỉ số và điều chỉnh hệ số theo đặc thù của mình.

## 2. Sáu trụ cột và 18 tiêu chí

| Trụ cột | Mã | Tiêu chí |
|---|---|---|
| **Khách hàng** | C1 | Mức độ bao phủ kênh/dịch vụ số |
| | C2 | Mức độ khách hàng sử dụng kênh số |
| | C3 | Chất lượng trải nghiệm số |
| **Chiến lược** | S1 | Chiến lược và lộ trình chuyển đổi số |
| | S2 | Đầu tư/ngân sách cho chuyển đổi số |
| | S3 | Hệ sinh thái và quan hệ đối tác số |
| **Công nghệ** | T1 | eKYC và sinh trắc học |
| | T2 | Cho vay số/digital lending |
| | T3 | AI/GenAI |
| | T4 | Open Banking/API |
| **Vận hành** | O1 | Tỷ trọng giao dịch trên kênh số |
| | O2 | Số hóa/tự động hóa quy trình |
| | O3 | Vận hành dịch vụ số |
| **Văn hóa** | H1 | Đào tạo và năng lực số |
| | H2 | Đổi mới sáng tạo |
| | H3 | Quản trị thay đổi và văn hóa số |
| **Dữ liệu** | D1 | Kiến trúc và tích hợp dữ liệu |
| | D2 | Quản trị và an toàn dữ liệu |
| | D3 | Phân tích dữ liệu và cá nhân hóa |

### Những thứ KHÔNG đưa vào điểm DTI
- Lượt tải Google Play dạng "5M+" / "10M+".
- Số bài báo Google News.
- Số lần regex/keyword xuất hiện trong BCTN.
- Dữ liệu fallback tự đặt.
- Median-imputation cho dữ liệu thiếu.

Các nguồn trên nếu có thể thu thập vẫn chỉ dùng làm **bằng chứng/insight**, không biến thành điểm DTI.

## 3. Nguồn dữ liệu

Ưu tiên theo thứ tự:

1. **BCTN 2025 của chính ngân hàng** – nguồn chính cho chiến lược, công nghệ, vận hành, văn hóa, dữ liệu.
2. **Website/chuyên trang chính thức của ngân hàng** – dùng để kiểm chứng và bổ sung bằng chứng.
3. **Google Play Store** – chỉ cho C3, cụ thể Rating và tỷ lệ phản hồi tích cực.
4. Không dùng báo chí làm điểm.

Mỗi quan sát phải lưu tối thiểu:

`Bank | Criterion | Raw_Value | Score | Evidence | Source | Page | URL | Collected_Date`

## 4. Chấm điểm tiêu chí

### 4.1. Tiêu chí định tính

Dùng 5 mức trưởng thành:

| Mức | Điểm đại diện | Quy tắc bằng chứng |
|---|---:|---|
| Mức 1 | 0 | Chưa có bằng chứng triển khai |
| Mức 2 | 30 | Đã có định hướng/giải pháp hoặc pilot/bước đầu |
| Mức 3 | 50 | Đã triển khai thực tế ở một phạm vi rõ ràng |
| Mức 4 | 70 | Triển khai rộng/tích hợp nhiều bộ phận hoặc quy trình |
| Mức 5 | 100 | Triển khai ở quy mô toàn ngân hàng và có kết quả/đầu ra định lượng rõ ràng |

**Quan trọng:** đây là rubric vận hành do nhóm xây dựng để chuyển bằng chứng công khai thành điểm; không được viết rằng Quyết định 2158 quy định riêng eKYC = 30/50/70/100.

### 4.2. Tiêu chí định lượng

Nếu ngân hàng công bố trực tiếp một tỷ lệ có cùng ý nghĩa với tiêu chí:

**Score = tỷ lệ % thực tế**, giới hạn 0–100.

Ví dụ: nếu BCTN công bố 82% giao dịch qua kênh số thì O1 = 82.

Nếu chỉ có số tuyệt đối nhưng không có mẫu số phù hợp thì **N/D**, không tự suy diễn.

### 4.3. C3 – trải nghiệm số

C3 là proxy công khai:

- Rating 0–5 → `Rating / 5 × 100`
- Positive Ratio 0–100% → giữ nguyên
- Nếu có cả hai → C3 = trung bình cộng hai thành phần có dữ liệu.
- Không có dữ liệu → N/D.

C3 được ghi rõ là **proxy**, không phải tiêu chí DBI gốc.

## 5. Tính điểm từ dưới lên

Quyết định 2158 yêu cầu tính từ tiêu chí → nhóm/trụ cột → tổng thể bằng **trung bình cộng**, và tiêu chí không thuộc chức năng thì không tính vào mẫu số.

Với phiên bản ngân hàng:

### Điểm trụ cột

`Pillar Score = AVERAGE(các tiêu chí có dữ liệu trong trụ cột)`

Không thay N/D bằng 0.

### Điểm DTI tổng

Sáu trụ cột được đặt trọng số bằng nhau:

`DTI = (Customer + Strategy + Technology + Operations + Culture + Data) / 6`

Đây là **quy ước thích nghi của nhóm**, được chọn vì phù hợp với nguyên tắc trung bình cộng của Quyết định 2158 và tránh áp đặt trọng số chủ quan.

## 6. Mức trưởng thành

| Điểm | Mức |
|---:|---|
| 0 – <25 | Mức 1 – Khởi động |
| 25 – <50 | Mức 2 – Bắt đầu |
| 50 – <75 | Mức 3 – Hình thành |
| 75 – <100 | Mức 4 – Nâng cao |
| 100 | Mức 5 – Dẫn dắt |

**100 phải là Mức 5**, không phải Mức 4.

## 7. Điều kiện đủ để được xếp hạng

Để tránh một ngân hàng có quá ít dữ liệu nhưng vẫn được xếp hạng:

- Có ít nhất **12/18 tiêu chí** được chấm.
- Cả **6 trụ cột đều phải có ít nhất 1 tiêu chí có dữ liệu**.
- Nếu không đạt: `Rank = N/A`, nhưng vẫn hiển thị các điểm đã có và tỷ lệ Data Coverage.

Data Coverage chỉ là **chỉ số minh bạch dữ liệu**, không cộng điểm.

## 8. Xếp hạng

- Xếp theo `DTI_Total_Score` giảm dần.
- Dùng điểm đầy đủ trước khi làm tròn.
- Nếu hai ngân hàng bằng điểm hoàn toàn → đồng hạng.
- Không dùng số bài báo, lượt tải hoặc quy mô ngân hàng làm tie-breaker.

## 9. Nguyên tắc dữ liệu thiếu

Không được:
- đặt 0 chỉ vì không tìm thấy dữ liệu;
- lấy median của ngân hàng khác;
- tự ước lượng;
- lấy số liệu OCB làm Liobank;
- dùng số liệu của công ty con để đại diện ngân hàng mẹ nếu không được xác định rõ.

Quy tắc:

`Không có bằng chứng công khai đủ mạnh → N/D → loại khỏi trung bình của tiêu chí/trụ cột.`

## 10. Năm dữ liệu

Bộ xếp hạng chính sử dụng **BCTN 2025** và các nguồn công khai tương ứng để tạo snapshot cùng thời điểm.

Nếu có dữ liệu 2026 chỉ dùng để:
- cập nhật trạng thái hiện tại;
- ghi chú biến động;
- không trộn vào điểm BCTN 2025 nếu chưa quy định lại kỳ đánh giá.

## 11. Mục tiêu của dashboard

Dashboard phải trả lời 4 câu:

1. Ngân hàng nào có DTI cao nhất?
2. Ngân hàng đang ở Mức 1–5 nào?
3. Ngân hàng mạnh/yếu ở trụ cột nào?
4. Mỗi điểm được chấm dựa trên bằng chứng nào?

Do đó dashboard sẽ có:
- Ranking tổng hợp;
- DTI + Maturity Level;
- 6 pillar scores;
- 18 criterion scores;
- Evidence/Source/URL/Page;
- Data Coverage;
- bảng so sánh và radar 6 trụ cột.
