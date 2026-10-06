# Hướng dẫn cài đặt và chạy Dashboard xếp hạng ngân hàng

Tài liệu này dành cho người mới dùng Windows. Làm lần lượt theo các bước dưới đây; thường chỉ cần cài môi trường một lần.

## 1. Chuẩn bị

- Máy tính Windows 10/11.
- Thư mục dự án đầy đủ, ví dụ: `D:\Ngân hàng số\Ranking_top5_bank`.
- Python **3.12** và kết nối Internet khi cài thư viện.

### Kiểm tra Python

Mở **PowerShell** hoặc Terminal trong VS Code, chạy:

```powershell
py -3.12 --version
```

Nếu hiện `Python 3.12.x`, chuyển sang bước 2. Nếu báo không tìm thấy Python, hãy cài Python 3.12 từ [python.org](https://www.python.org/downloads/) và chọn **Add Python to PATH** trong trình cài đặt. Đóng rồi mở lại PowerShell, sau đó kiểm tra lại.

## 2. Cài thư viện cho dự án (làm lần đầu)

Trong PowerShell, nhập lần lượt:

```powershell
cd "D:\Ngân hàng số\Ranking_top5_bank"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirement.txt
```

Chờ đến khi lệnh cài đặt kết thúc và PowerShell hiện lại dấu nhắc nhập lệnh. Nếu thư mục `.venv` đã tồn tại, bỏ qua lệnh tạo môi trường và chạy hai lệnh cài thư viện.

## 3. Khởi động Dashboard

Mỗi lần muốn sử dụng Dashboard, mở PowerShell rồi chạy:

```powershell
cd "D:\Ngân hàng số\Ranking_top5_bank"
.\run_app.ps1
```

Giữ cửa sổ PowerShell đang chạy. Mở Chrome, Edge hoặc trình duyệt khác và truy cập:

**http://localhost:8501**

Nếu trang chưa hiện ngay, đợi vài giây rồi tải lại trang. Để tắt Dashboard, quay lại PowerShell và nhấn **Ctrl + C**.

## 4. Dùng Dashboard

- Chọn **“Xếp hạng tham khảo — đủ 5 ngân hàng”** để xem bảng so sánh đủ năm ngân hàng. Bảng này dùng điểm đề xuất và có bằng chứng ứng viên; kết quả chỉ để tham khảo.
- Chọn **“Kết quả chính thức — chỉ bằng chứng đã duyệt”** để xem điểm chỉ tính bằng chứng đã được duyệt. Ngân hàng chưa đủ điều kiện có thể hiện `N/D` hoặc chưa có hạng.
- `N/D` nghĩa là dữ liệu trong dự án chưa đủ căn cứ để chấm, không có nghĩa ngân hàng không thực hiện hoạt động đó.

## 5. Lỗi thường gặp

### Báo cổng 8501 đang được sử dụng

Dashboard có thể đã chạy. Hãy mở **http://localhost:8501** trước. Nếu có cửa sổ PowerShell khác đang chạy Dashboard, dùng cửa sổ đó; không cần khởi động thêm bản mới.

Nếu muốn chạy trên cổng khác, mở một PowerShell mới tại thư mục dự án và chạy:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```

Sau đó mở **http://localhost:8502**. Dừng phiên này bằng **Ctrl + C** trong cửa sổ vừa chạy lệnh.

### PowerShell chặn chạy `run_app.ps1`

Chạy lệnh dưới đây trong PowerShell. Thiết lập này chỉ áp dụng cho cửa sổ hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Nếu được hỏi, nhập `Y`, nhấn Enter, rồi chạy lại:

```powershell
.\run_app.ps1
```

### Không tìm thấy `.venv` hoặc báo cần Python 3.12

Đảm bảo đang ở đúng thư mục dự án. Kiểm tra phiên bản Python bằng `py -3.12 --version`; nếu chưa tạo `.venv`, làm lại bước 2.

### Cài thư viện bị lỗi hoặc Dashboard báo thiếu thư viện

Kiểm tra Internet, sau đó chạy lại lệnh cài thư viện ở bước 2. Đảm bảo dùng đúng tệp `requirement.txt` (tên tệp ở dạng số ít).

## 6. Nếu mở dự án trên máy tính khác

Sao chép **toàn bộ thư mục dự án**, không chỉ riêng `app.py`. Trên máy mới, cài Python 3.12, làm bước 2 một lần rồi khởi động theo bước 3. Không cần sao chép thư mục `.venv`; môi trường nên được tạo lại trên máy mới.

## Thông tin dự án

Dashboard đánh giá Vietcombank, VPBank, ACB, OCB và Agribank trong kỳ 2025 bằng bộ chỉ số thích nghi gồm sáu trụ cột và 19 tiêu chí. Đây là kết quả nghiên cứu của dự án, không phải điểm DBI chính thức của cơ quan quản lý. Xem [phương pháp đánh giá](METHODOLOGY.md) và [báo cáo tổng kết](FINAL_REPORT.md) để biết cách tính điểm và diễn giải kết quả.
