# Ranking_top5_bank_v2

## Đã chốt
- 6 trụ cột theo khung QĐ 2158.
- 18 tiêu chí thích nghi cho ngân hàng.
- Không fallback / không dữ liệu giả định.
- Không median-imputation.
- Không dùng news/downloads/keyword-count làm điểm.
- Chấm định tính theo 0/30/50/70/100.
- Chỉ tiêu tỷ lệ dùng % thực tế khi có tử số + mẫu số rõ.
- DTI = trung bình 6 trụ cột.
- Maturity: <25 / <50 / <75 / <100 / 100.
- Điều kiện xếp hạng: >=12/18 tiêu chí và đủ cả 6 trụ cột.

## Bước tiếp theo
1. Tích hợp `scoring_rules.py` vào `main.py`.
2. Viết extractor tạo `evidence_data.csv` từ 5 BCTN 2025.
3. Thu thập Google Play cho C3, không fallback.
4. Kiểm tra từng evidence trước khi chấm.
5. Sinh `scoring_data.csv`.
6. Cập nhật dashboard sang 6 trụ cột + 18 tiêu chí + maturity level.
