# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DeTai(models.Model):
    _name = 'quanly.detai'
    _description = 'Đề tài tốt nghiệp chính thức'
    _rec_name = 'ten_de_tai'

    ma_de_tai = fields.Char(string='Mã đề tài', required=True, copy=False)
    ten_de_tai = fields.Char(string='Tên đề tài tốt nghiệp', required=True)
    mo_ta = fields.Text(string='Mô tả chi tiết nội dung')

    dang_ky_id = fields.Many2one('quanly.dangky', string='Sinh viên thực hiện', required=True, ondelete='restrict')
    sinh_vien_id = fields.Many2one(
        'quanly.sinhvien', 
        string='Sinh viên', 
        related='dang_ky_id.sinh_vien_id', 
        store=True, 
        readonly=True
    )
    dot_do_an_id = fields.Many2one(
        'quanly.dotdoan', 
        string='Đợt làm đồ án', 
        related='dang_ky_id.dot_do_an_id', 
        store=True, 
        readonly=True
    )

    ngan_hang_de_tai_id = fields.Many2one('quanly.nganhangdetai', string='Nguồn từ Ngân hàng đề tài')
    giang_vien_huong_dan_id = fields.Many2one('quanly.giangvien', string='Giảng viên hướng dẫn', required=True)
    hoi_dong_id = fields.Many2one('quanly.hoidong', string='Hội đồng bảo vệ', ondelete='set null')

    link_github = fields.Char(string='Link Github / Source Code')
    link_demo = fields.Char(string='Link Demo sản phẩm')

    gvhd_da_duyet = fields.Boolean(string='GVHD đồng ý cho bảo vệ', default=False)
    nhan_xet_tong_ket = fields.Text(string='Nhận xét tổng kết của GVHD')

    diem_gvhd = fields.Float(string='Điểm GVHD (thang 10)', digits=(4, 2))
    diem_bao_cao_tb = fields.Float(string='Điểm Báo cáo TB', digits=(4, 2), readonly=True)
    diem_do_an_tb = fields.Float(string='Điểm Đồ án TB Hội đồng', digits=(4, 2), readonly=True)
    diem_tong_ket = fields.Float(string='Điểm tổng kết cuối cùng', digits=(4, 2), compute='_compute_diem_tong_ket', store=True)
    xep_loai = fields.Selection([
        ('xuat_sac', 'Xuất sắc'),
        ('gioi', 'Giỏi'),
        ('kha', 'Khá'),
        ('trung_binh', 'Trung bình'),
        ('khong_dat', 'Không đạt')
    ], string='Xếp loại', compute='_compute_diem_tong_ket', store=True)

    da_khoa_diem = fields.Boolean(string='Đã khóa điểm', default=False)
    trang_thai = fields.Selection([
        ('dang_thuc_hien', 'Đang thực hiện'),
        ('cho_bao_ve', 'Đủ điều kiện chờ bảo vệ'),
        ('khong_duoc_bao_ve', 'Không được bảo vệ'),
        ('da_bao_ve', 'Đã bảo vệ xong'),
        ('da_luu_chieu', 'Đã nộp lưu chiểu')
    ], string='Trạng thái đề tài', default='dang_thuc_hien')

    bao_cao_ids = fields.One2many('quanly.baocao', 'de_tai_id', string='Danh sách nộp báo cáo')
    hinh_anh_ids = fields.One2many('quanly.hinhanhdetai', 'de_tai_id', string='Thư viện ảnh sản phẩm (Showcase)')
    phieu_cham_diem_ids = fields.One2many('quanly.phieuchamdiem', 'de_tai_id', string='Phiếu chấm điểm hội đồng')

    _sql_constraints = [
        ('ma_de_tai_uniq', 'unique(ma_de_tai)', 'Mã đề tài đã tồn tại!'),
        ('dang_ky_uniq', 'unique(dang_ky_id)', 'Mỗi lượt đăng ký của sinh viên chỉ được gán đúng 1 đề tài!')
    ]

    @api.depends('diem_gvhd', 'diem_bao_cao_tb', 'diem_do_an_tb', 'dot_do_an_id')
    def _compute_diem_tong_ket(self):
        for rec in self:
            w_gvhd = (rec.dot_do_an_id.trong_so_gvhd or 30.0) / 100.0
            w_bc = (rec.dot_do_an_id.trong_so_bao_cao or 20.0) / 100.0
            w_da = (rec.dot_do_an_id.trong_so_do_an or 50.0) / 100.0

            total = (rec.diem_gvhd * w_gvhd) + (rec.diem_bao_cao_tb * w_bc) + (rec.diem_do_an_tb * w_da)
            rec.diem_tong_ket = round(total, 2)

            if rec.diem_tong_ket >= 9.0:
                rec.xep_loai = 'xuat_sac'
            elif rec.diem_tong_ket >= 8.0:
                rec.xep_loai = 'gioi'
            elif rec.diem_tong_ket >= 6.5:
                rec.xep_loai = 'kha'
            elif rec.diem_tong_ket >= 5.0:
                rec.xep_loai = 'trung_binh'
            else:
                rec.xep_loai = 'khong_dat'


class HinhAnhDeTai(models.Model):
    _name = 'quanly.hinhanhdetai'
    _description = 'Hình ảnh demo / Showcase sản phẩm đề tài'
    _rec_name = 'ten_hinh'

    de_tai_id = fields.Many2one('quanly.detai', string='Đề tài', required=True, ondelete='cascade')
    ten_hinh = fields.Char(string='Tiêu đề hình ảnh', required=True)
    hinh_anh = fields.Image(string='File hình ảnh', max_width=1920, max_height=1080)
    url = fields.Char(string='URL đường dẫn ảnh')
    mo_ta = fields.Text(string='Mô tả ảnh')

