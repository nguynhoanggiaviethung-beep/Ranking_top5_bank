# Xếp hạng mức độ chuyển đổi số của 5 ngân hàng

**Kỳ đánh giá:** 2025  
**Mẫu nghiên cứu:** Vietcombank, VPBank, ACB, OCB và Agribank (giữ nguyên theo yêu cầu đề tài)

## Xếp hạng tham khảo đủ năm ngân hàng

Để có bảng so sánh cho đủ mẫu nghiên cứu, dashboard có chế độ **Xếp hạng tham khảo**. Chế độ này dùng điểm đề xuất gắn với bằng chứng `Candidate` có nguồn và vị trí tra cứu; các tỷ lệ định lượng chưa xác nhận vẫn để N/D. Tất cả năm ngân hàng đang đạt ngưỡng kỹ thuật 12/19 tiêu chí và có dữ liệu ở sáu trụ cột trong bảng tham khảo:

| Hạng tham khảo | Ngân hàng | DTI tham khảo | Tiêu chí có dữ liệu |
|---:|---|---:|---:|
| 1 | Vietcombank | 71,74 | 18/19 |
| 2 | ACB | 68,61 | 17/19 |
| 3 | OCB | 68,39 | 18/19 |
| 4 | Agribank | 68,28 | 19/19 |
| 5 | VPBank | 65,83 | 16/19 |

Đây là thứ hạng tham khảo để hoàn tất so sánh đủ năm ngân hàng; chưa phải kết luận chính thức vì các ứng viên chưa được đối chiếu độc lập hết.

## Kết quả chính thức

Bảng dưới đây chỉ tính tiêu chí có bằng chứng trạng thái `Approved`. Ngân hàng cần có ít nhất 12/19 tiêu chí và dữ liệu ở cả sáu trụ cột mới đủ điều kiện xếp hạng.

| Hạng | Ngân hàng | DTI | Mức trưởng thành | Tiêu chí có dữ liệu | Bao phủ |
|---:|---|---:|---|---:|---:|
| 1 | Vietcombank | 72,62 | Mức 3 – Hình thành | 13/19 | 68,4% |
| 2 | Agribank | 72,25 | Mức 3 – Hình thành | 13/19 | 68,4% |
| 3 | OCB | 67,67 | Mức 3 – Hình thành | 13/19 | 68,4% |
| — | ACB | N/D | N/D | 3/19 | 15,8% |
| — | VPBank | N/D | N/D | 1/19 | 5,3% |

ACB và VPBank chưa có hạng chính thức vì bằng chứng đã duyệt chưa đạt ngưỡng. Chọn **Kết quả chính thức** trên dashboard để xem bảng này; chọn **Xếp hạng tham khảo — đủ 5 ngân hàng** để xem thứ hạng so sánh của cả mẫu.

## Điều chỉnh tiêu chí C3

C3 được đổi từ proxy rating ứng dụng Google Play sang **Hỗ trợ khách hàng trên kênh số**. Rating hiện tại không đại diện cho kỳ 2025 và không so sánh ổn định giữa các ngân hàng. Tiêu chí mới dùng bằng chứng cùng kỳ về chatbot/voicebot, kênh phục vụ, mức độ triển khai và kết quả được công bố; áp dụng chung rubric 0/30/50/70/100. C3 không còn tự tính từ snapshot Google Play.

C2 và O1 vẫn là tỷ lệ định lượng. Chỉ chấm khi nguồn cho biết rõ phạm vi và tử số/mẫu số; không đổi sang tiêu chí định tính chỉ để lấp chỗ thiếu dữ liệu. Các tiêu chí chưa đủ bằng chứng được giữ N/D, không quy thành 0.

## Phương pháp và giới hạn

1. Giữ nguyên năm ngân hàng theo đề tài và dùng dữ liệu kỳ 2025.
2. Lưu nguồn, vị trí trang, đoạn trích và trạng thái rà soát trong `data/evidence_data.csv`.
3. Chỉ dòng `Approved` được dùng trong bảng điểm chính thức. Trích đoạn tự động và dòng chưa đối chiếu là `Candidate`.
4. DTI là bộ chỉ số thích nghi do nhóm xây dựng, tham chiếu khung sáu trụ cột; đây không phải điểm DBI chính thức của cơ quan quản lý.
5. N/D nghĩa là dự án chưa có bằng chứng đạt yêu cầu trong dữ liệu đang lưu, không khẳng định ngân hàng không triển khai hoạt động đó.

## Tệp kết quả

- `data/scoring_data.csv`: kết quả chính thức.
- `data/scoring_provisional_data.csv`: bảng dự thảo có tính cả điểm ứng viên.
- `data/evidence_data.csv`: bằng chứng, nguồn và trạng thái duyệt.
- `data/evidence_review_matrix.csv`: ma trận rà soát theo ngân hàng và tiêu chí.
