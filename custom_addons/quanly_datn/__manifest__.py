# -*- coding: utf-8 -*-
{
    'name': 'Quản Lý Đồ Án Tốt Nghiệp',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Hệ thống Quản lý Đồ án tốt nghiệp cho Khoa Công nghệ số',
    'description': """
Hệ thống Quản lý Đồ án Tốt nghiệp cho sinh viên Khoa Công nghệ số
==================================================================
* Quản lý đợt làm đồ án, chuyên ngành, lớp sinh hoạt
* Quản lý giảng viên, sinh viên và tài khoản người dùng
* Quản lý ngân hàng đề tài đề xuất và đăng ký đề tài
* Quản lý tiến độ báo cáo và tệp báo cáo đính kèm
* Quản lý thư viện hình ảnh demo đề tài (lưu chiểu)
* Quản lý Hội đồng bảo vệ trên giao diện Calendar trực quan
* Tự động gợi ý & phân công giảng viên phản biện cân bằng tải
* Phiếu chấm điểm trực tuyến và tự động tính điểm trung bình
* Xuất báo cáo phiếu chấm điểm QWeb PDF
    """,
    'author': 'Phan Hồ Nhật Nam (MSSV: 22115053122323)',
    'website': 'https://ute.udn.vn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'calendar',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/to_chuc_views.xml',
        'views/dot_do_an_views.xml',
        'views/de_tai_views.xml',
        'views/bao_cao_views.xml',
        'views/hoi_dong_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

