# HỆ THỐNG QUẢN LÝ ĐỒ ÁN TỐT NGHIỆP - KHOA CÔNG NGHỆ SỐ

> **Đề tài tốt nghiệp:** Xây dựng hệ thống quản lý đồ án tốt nghiệp cho sinh viên Khoa Công nghệ số  
> **Trường:** Đại học Sư phạm Kỹ thuật - Đại học Đà Nẵng  
> **Sinh viên thực hiện:** Phan Hồ Nhật Nam  
> **Mã số sinh viên:** 22115053122323 - Lớp: 22T3  
> **Giảng viên hướng dẫn:** ThS. Nguyễn Thị Hà Quyên  
> **Công nghệ sử dụng:** Python 3.12, TypeScript/JavaScript (OWL Framework), Odoo 18.0 ERP Framework, PostgreSQL 16, QWeb PDF Reporting.

---

## 1. GIỚI THIỆU HỆ THỐNG

Hệ thống cho phép số hóa toàn diện quy trình quản lý đồ án tốt nghiệp tại Khoa Công nghệ số:
* **Ban Chủ nhiệm Khoa & Bộ môn:** Quản lý đợt đồ án theo từng học kỳ, duyệt danh sách đề tài đề xuất, tự động gợi ý và phân công giảng viên phản biện cân bằng tải, quản lý hội đồng và lịch bảo vệ trực quan trên Calendar view.
* **Giảng viên hướng dẫn:** Theo dõi tiến độ định kỳ, xem và nhận xét báo cáo của sinh viên, chấm điểm và xác nhận điều kiện bảo vệ.
* **Hội đồng chấm thi:** Nhập phiếu chấm điểm trực quan cho từng đề tài, hệ thống tự động tính điểm trung bình và xuất phiếu chấm điểm chuẩn hóa.
* **Sinh viên:** Đăng ký đề tài, nộp báo cáo định kỳ theo đợt, trao đổi với giảng viên và nộp hình ảnh sản phẩm demo lưu chiểu.

---

## 2. KIẾN TRÚC THƯ MỤC DỰ ÁN

```text
Project_Odoo/
├── .gitignore                      # Cấu hình bỏ qua file không cần thiết trên Git
├── README.md                       # Hướng dẫn chi tiết dự án
├── docker-compose.yml              # Dựng nhanh môi trường Odoo 18 + PostgreSQL 16
├── requirements.txt                # Thư viện Python phụ thuộc
├── config/
│   └── odoo.conf                   # Cấu hình kết nối Odoo & CSDL
├── database/
│   └── database_schema_postgres.sql # Script SQL đặc tả CSDL tham chiếu (chuẩn 3NF)
└── custom_addons/
    └── quanly_datn/                # Module Odoo chính của hệ thống
        ├── __init__.py
        ├── __manifest__.py         # Khai báo metadata và danh sách file XML nạp
        ├── models/                 # Định nghĩa các Model nghiệp vụ theo ERD
        │   ├── __init__.py
        │   ├── to_chuc.py          # Chuyên ngành, Lớp sinh hoạt
        │   ├── nguoi_dung.py       # Kế thừa Người dùng: Sinh viên, Giảng viên
        │   ├── dot_do_an.py        # Đợt đồ án, Đăng ký, Ngân hàng đề tài
        │   ├── de_tai.py           # Đề tài, Hình ảnh demo lưu chiểu
        │   ├── bao_cao.py          # Đợt báo cáo, Nộp báo cáo định kỳ
        │   ├── hoi_dong.py         # Hội đồng, Hội đồng giảng viên, Phiếu chấm điểm
        │   └── tuong_tac.py        # Tin nhắn trao đổi, Thông báo
        ├── security/
        │   ├── security_groups.xml # Nhóm quyền: Sinh viên, Giảng viên, BCN Khoa
        │   └── ir.model.access.csv # Bảng phân quyền CRUD chi tiết
        ├── views/                  # Giao diện XML (Form, List, Search, Calendar)
        │   ├── menu_views.xml      # Hệ thống Menu điều hướng
        │   ├── to_chuc_views.xml
        │   ├── dot_do_an_views.xml
        │   ├── de_tai_views.xml
        │   ├── bao_cao_views.xml
        │   └── hoi_dong_views.xml
        ├── reports/                # Mẫu xuất báo cáo QWeb PDF
        ├── wizard/                 # Popup chức năng (phân công phản biện, khóa điểm)
        └── static/                 # Tài nguyên tĩnh (CSS, JS, Icon)
```

---

## 3. HƯỚNG DẪN CÀI ĐẶT & CHẠY HỆ THỐNG

### Yêu cầu tiên quyết:
* Đã cài đặt **Docker** và **Docker Compose**.
* Hoặc đã cài đặt **Python 3.12**, **Odoo 18** và **PostgreSQL 16** cục bộ.

### Chạy bằng Docker (Khuyên dùng):
1. **Khởi động dịch vụ:**
   ```bash
   docker compose up -d
   ```
2. **Kiểm tra trạng thái:**
   ```bash
   docker compose ps
   ```
3. **Truy cập hệ thống:**
   * Mở trình duyệt truy cập: `http://localhost:8069`
   * Tạo database mới với thông tin:
     * Master Password: `admin_secret_datn_2026`
     * Database Name: `datn_db`
     * Email: `admin@ute.udn.vn`
     * Password: `admin`
4. **Cài đặt module:**
   * Đăng nhập với quyền Admin.
   * Kích hoạt chế độ **Developer Mode** (Settings ➔ Activate Developer Mode).
   * Vào menu **Apps** ➔ Nhấn **Update Apps List**.
   * Tìm kiếm module **Quản Lý Đồ Án Tốt Nghiệp** (`quanly_datn`) ➔ Nhấn **Activate**.

---

## 4. QUY CHUẨN COMMIT GIT

* `feat:` Tính năng mới (vd: `feat: them model BAOCAO va logic tinh nopTre`)
* `fix:` Sửa lỗi (vd: `fix: sua loi tinh diem trung binh tren phieu cham diem`)
* `docs:` Cập nhật tài liệu (vd: `docs: cap nhat README`)
* `style:` Chỉnh sửa giao diện XML/CSS
* `refactor:` Tối ưu cấu trúc mã nguồn
