# -*- coding: utf-8 -*-
from odoo import models, fields

class DotDoAn(models.Model):
    _name = 'quanly.dotdoan'
    _description = 'Đợt làm đồ án tốt nghiệp'
    _rec_name = 'ten_dot'

    ma_dot = fields.Char(string='Mã đợt', required=True, copy=False)
    ten_dot = fields.Char(string='Tên đợt làm đồ án', required=True)
    nien_khoa = fields.Char(string='Niên khóa', required=True)
    hoc_ky = fields.Selection([
        ('1', 'Học kỳ 1'),
        ('2', 'Học kỳ 2'),
        ('he', 'Học kỳ Hè')
    ], string='Học kỳ', default='1', required=True)
    ma_hoc_phan = fields.Char(string='Mã học phần')
    ten_hoc_phan = fields.Char(string='Tên học phần', default='Đồ án tốt nghiệp')
    ngay_bat_dau = fields.Date(string='Ngày bắt đầu')
    ngay_bat_dau_bao_ve = fields.Date(string='Ngày bắt đầu bảo vệ')
    ngay_ket_thuc_bao_ve = fields.Date(string='Ngày kết thúc bảo vệ')

    trong_so_gvhd = fields.Float(string='Trọng số điểm GVHD (%)', default=30.0)
    trong_so_bao_cao = fields.Float(string='Trọng số điểm Báo cáo (%)', default=20.0)
    trong_so_do_an = fields.Float(string='Trọng số điểm Đồ án Hội đồng (%)', default=50.0)

    trang_thai = fields.Selection([
        ('chuan_bi', 'Chuẩn bị mở đợt'),
        ('dang_dang_ky', 'Đang cho đăng ký đề tài'),
        ('dang_thuc_hien', 'Đang thực hiện đồ án'),
        ('dang_bao_ve', 'Giai đoạn bảo vệ'),
        ('ket_thuc', 'Đã kết thúc đợt')
    ], string='Trạng thái đợt', default='chuan_bi')

    dang_ky_ids = fields.One2many('quanly.dangky', 'dot_do_an_id', string='Danh sách đăng ký')
    ngan_hang_de_tai_ids = fields.One2many('quanly.nganhangdetai', 'dot_do_an_id', string='Ngân hàng đề tài')
    dot_bao_cao_ids = fields.One2many('quanly.dotbaocao', 'dot_do_an_id', string='Các đợt báo cáo')
    hoi_dong_ids = fields.One2many('quanly.hoidong', 'dot_do_an_id', string='Hội đồng bảo vệ')

    _sql_constraints = [
        ('ma_dot_uniq', 'unique(ma_dot)', 'Mã đợt làm đồ án đã tồn tại!')
    ]


class DangKy(models.Model):
    _name = 'quanly.dangky'
    _description = 'Đăng ký tham gia đợt đồ án'
    _rec_name = 'display_name'

    sinh_vien_id = fields.Many2one('quanly.sinhvien', string='Sinh viên', required=True, ondelete='cascade')
    dot_do_an_id = fields.Many2one('quanly.dotdoan', string='Đợt đồ án', required=True, ondelete='cascade')
    ngay_dang_ky = fields.Date(string='Ngày đăng ký', default=fields.Date.context_today)
    trang_thai = fields.Selection([
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt điều kiện'),
        ('tu_choi', 'Từ chối')
    ], string='Trạng thái', default='cho_duyet')

    display_name = fields.Char(string='Tên hiển thị', compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('sinhvien_dot_uniq', 'unique(sinh_vien_id, dot_do_an_id)', 'Sinh viên đã đăng ký tham gia đợt này rồi!')
    ]

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.sinh_vien_id.ho_ten or ''} - {rec.dot_do_an_id.ten_dot or ''}"


class NganHangDeTai(models.Model):
    _name = 'quanly.nganhangdetai'
    _description = 'Ngân hàng đề tài đề xuất'
    _rec_name = 'ten_de_tai'

    dot_do_an_id = fields.Many2one('quanly.dotdoan', string='Đợt đồ án', required=True)
    chuyen_nganh_id = fields.Many2one('quanly.chuyennganh', string='Chuyên ngành', required=True)
    loai_de_tai = fields.Selection([
        ('gv_de_xuat', 'Giảng viên đề xuất'),
        ('sv_de_xuat', 'Sinh viên đề xuất'),
        ('khoa_de_xuat', 'Khoa/Doanh nghiệp đề xuất')
    ], string='Nguồn đề xuất', default='gv_de_xuat', required=True)

    giang_vien_de_xuat_id = fields.Many2one('quanly.giangvien', string='Giảng viên đề xuất')
    sinh_vien_de_xuat_id = fields.Many2one('quanly.sinhvien', string='Sinh viên đề xuất')

    ten_de_tai = fields.Char(string='Tên đề tài', required=True)
    mo_ta = fields.Text(string='Mô tả mục tiêu & yêu cầu đề tài')
    trang_thai = fields.Selection([
        ('du_thao', 'Dự thảo'),
        ('cho_duyet', 'Chờ BCN Khoa duyệt'),
        ('da_duyet', 'Đã duyệt (Có thể đăng ký)'),
        ('da_chon', 'Đã có sinh viên nhận'),
        ('tu_choi', 'Không duyệt')
    ], string='Trạng thái', default='cho_duyet')

