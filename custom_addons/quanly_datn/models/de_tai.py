# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

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
        ('cho_xac_nhan_bao_ve', 'Chờ GVHD xác nhận bảo vệ'),
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

    def _is_bcn(self):
        return self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem')

    def _current_sinh_vien(self):
        return self.env['quanly.sinhvien'].search([('user_id', '=', self.env.user.id)], limit=1)

    def _is_gvhd(self):
        return all(rec.giang_vien_huong_dan_id.user_id == self.env.user for rec in self)

    def write(self, vals):
        if self._is_bcn():
            return super().write(vals)

        changed_fields = set(vals)
        if self.env.user.has_group('quanly_datn.group_datn_sinh_vien'):
            sinh_vien = self._current_sinh_vien()
            if not sinh_vien or any(rec.sinh_vien_id != sinh_vien for rec in self):
                raise AccessError(_('Bạn chỉ được cập nhật đề tài của chính mình.'))
            allowed_fields = {'mo_ta', 'link_github', 'link_demo', 'trang_thai'}
            if not changed_fields.issubset(allowed_fields):
                raise AccessError(_('Sinh viên chỉ được cập nhật mô tả và các liên kết của đề tài.'))
            if 'trang_thai' in vals and any(
                rec.trang_thai != 'dang_thuc_hien' or vals['trang_thai'] != 'cho_xac_nhan_bao_ve'
                for rec in self
            ):
                raise AccessError(_('Bạn không được chuyển đề tài sang trạng thái này.'))
            return super().write(vals)

        if self.env.user.has_group('quanly_datn.group_datn_giang_vien'):
            if not self._is_gvhd():
                raise AccessError(_('Chỉ giảng viên hướng dẫn của đề tài mới được thực hiện thao tác này.'))
            allowed_fields = {'diem_gvhd', 'nhan_xet_tong_ket', 'gvhd_da_duyet', 'trang_thai'}
            if not changed_fields.issubset(allowed_fields):
                raise AccessError(_('Giảng viên chỉ được cập nhật nhận xét, điểm và xác nhận bảo vệ.'))
            if 'trang_thai' in vals and any(
                rec.trang_thai != 'cho_xac_nhan_bao_ve'
                or vals['trang_thai'] not in ('cho_bao_ve', 'khong_duoc_bao_ve')
                for rec in self
            ):
                raise AccessError(_('Đề tài không ở trạng thái chờ bạn xác nhận bảo vệ.'))
            return super().write(vals)

        raise AccessError(_('Bạn không có quyền cập nhật đề tài này.'))

    def action_gui_xac_nhan_bao_ve(self):
        self.ensure_one()
        sinh_vien = self._current_sinh_vien()
        if not sinh_vien or self.sinh_vien_id != sinh_vien:
            raise AccessError(_('Chỉ sinh viên thực hiện đề tài mới được gửi yêu cầu bảo vệ.'))
        if self.trang_thai != 'dang_thuc_hien':
            raise UserError(_('Đề tài không ở trạng thái có thể gửi yêu cầu bảo vệ.'))

        dot_bao_cao_ids = self.env['quanly.dotbaocao'].search([
            ('dot_do_an_id', '=', self.dot_do_an_id.id),
        ])
        bao_cao_dat_ids = self.bao_cao_ids.filtered(lambda report: report.trang_thai == 'dat').mapped('dot_bao_cao_id')
        if dot_bao_cao_ids - bao_cao_dat_ids:
            raise UserError(_('Bạn cần có báo cáo đạt yêu cầu ở tất cả các đợt báo cáo trước khi gửi yêu cầu bảo vệ.'))
        self.write({'trang_thai': 'cho_xac_nhan_bao_ve'})

    def action_xac_nhan_bao_ve(self):
        if not self._is_gvhd():
            raise AccessError(_('Chỉ giảng viên hướng dẫn của đề tài mới được xác nhận bảo vệ.'))
        if any(rec.trang_thai != 'cho_xac_nhan_bao_ve' for rec in self):
            raise UserError(_('Đề tài cần ở trạng thái chờ xác nhận bảo vệ.'))
        self.write({'gvhd_da_duyet': True, 'trang_thai': 'cho_bao_ve'})

    def action_tu_choi_bao_ve(self):
        if not self._is_gvhd():
            raise AccessError(_('Chỉ giảng viên hướng dẫn của đề tài mới được từ chối bảo vệ.'))
        if any(rec.trang_thai != 'cho_xac_nhan_bao_ve' for rec in self):
            raise UserError(_('Đề tài cần ở trạng thái chờ xác nhận bảo vệ.'))
        self.write({'gvhd_da_duyet': False, 'trang_thai': 'khong_duoc_bao_ve'})

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

