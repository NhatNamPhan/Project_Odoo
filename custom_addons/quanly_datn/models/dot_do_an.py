# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

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

    @api.constrains('trong_so_gvhd', 'trong_so_bao_cao', 'trong_so_do_an')
    def _check_trong_so(self):
        for rec in self:
            weights = (rec.trong_so_gvhd, rec.trong_so_bao_cao, rec.trong_so_do_an)
            if any(weight < 0 or weight > 100 for weight in weights) or abs(sum(weights) - 100) > 0.00001:
                raise ValidationError(_('Các trọng số phải nằm trong khoảng 0–100% và có tổng bằng 100%.'))

    @api.constrains('ngay_bat_dau_bao_ve', 'ngay_ket_thuc_bao_ve')
    def _check_lich_bao_ve(self):
        for rec in self:
            if rec.ngay_bat_dau_bao_ve and rec.ngay_ket_thuc_bao_ve and rec.ngay_ket_thuc_bao_ve < rec.ngay_bat_dau_bao_ve:
                raise ValidationError(_('Ngày kết thúc bảo vệ phải sau ngày bắt đầu bảo vệ.'))

    def action_mo_dang_ky(self):
        if not self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem'):
            raise AccessError(_('Chỉ Ban chủ nhiệm khoa được mở đăng ký đề tài.'))
        if any(rec.trang_thai != 'chuan_bi' for rec in self):
            raise UserError(_('Chỉ có thể mở đăng ký khi đợt đang ở trạng thái chuẩn bị.'))
        self.write({'trang_thai': 'dang_dang_ky'})

    def write(self, vals):
        if any(rec.trang_thai == 'ket_thuc' for rec in self):
            raise UserError(_('Đợt đã kết thúc, không thể chỉnh sửa dữ liệu.'))
        transitions = {'chuan_bi': 'dang_dang_ky', 'dang_dang_ky': 'dang_thuc_hien', 'dang_thuc_hien': 'dang_bao_ve', 'dang_bao_ve': 'ket_thuc'}
        if 'trang_thai' in vals:
            for rec in self:
                if vals['trang_thai'] == rec.trang_thai:
                    continue
                if transitions.get(rec.trang_thai) != vals['trang_thai']:
                    raise UserError(_('Không được bỏ qua hoặc quay ngược giai đoạn đồ án.'))
                if vals['trang_thai'] == 'ket_thuc':
                    if rec.hoi_dong_ids.filtered(lambda hd: hd.trang_thai != 'hoan_thanh'):
                        raise UserError(_('Cần hoàn thành các hội đồng trước khi kết thúc đợt.'))
                    if self.env['quanly.detai'].search_count([('dot_do_an_id', '=', rec.id), ('trang_thai', 'not in', ['da_luu_chieu', 'khong_duoc_bao_ve'])]):
                        raise UserError(_('Cần xử lý xong đề tài và xác nhận lưu chiểu trước khi kết thúc đợt.'))
                    topics = self.env['quanly.detai'].search([('dot_do_an_id', '=', rec.id)])
                    if rec.dang_ky_ids.filtered(lambda dk: dk.trang_thai == 'cho_duyet') or (
                        rec.dang_ky_ids.filtered(lambda dk: dk.trang_thai == 'da_duyet') - topics.mapped('dang_ky_id')
                    ):
                        raise UserError(_('Còn đăng ký chưa xử lý hoặc sinh viên đã duyệt nhưng chưa giao đề tài.'))
        if set(vals) & {'trong_so_gvhd', 'trong_so_bao_cao', 'trong_so_do_an'}:
            if self.env['quanly.detai'].search_count([('dot_do_an_id', 'in', self.ids), ('da_khoa_diem', '=', True)]):
                raise UserError(_('Không thể đổi trọng số khi đợt đã có đề tài khóa điểm.'))
        return super().write(vals)

    def _check_open(self):
        if any(rec.trang_thai == 'ket_thuc' for rec in self):
            raise UserError(_('Đợt đồ án đã kết thúc, không thể thay đổi dữ liệu nghiệp vụ.'))

    def unlink(self):
        if any(rec.trang_thai != 'chuan_bi' or rec.dang_ky_ids or rec.hoi_dong_ids or rec.dot_bao_cao_ids or rec.ngan_hang_de_tai_ids for rec in self):
            raise UserError(_('Không thể xóa đợt đã mở hoặc đã có dữ liệu liên quan.'))
        return super().unlink()

    def _chuyen_giai_doan(self, source, target):
        if not self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem'):
            raise AccessError(_('Chỉ Ban chủ nhiệm khoa được chuyển giai đoạn.'))
        if any(rec.trang_thai != source for rec in self):
            raise UserError(_('Giai đoạn hiện tại không phù hợp với thao tác này.'))
        self.write({'trang_thai': target})

    def action_bat_dau_thuc_hien(self):
        self._chuyen_giai_doan('dang_dang_ky', 'dang_thuc_hien')

    def action_bat_dau_bao_ve(self):
        self._chuyen_giai_doan('dang_thuc_hien', 'dang_bao_ve')

    def action_ket_thuc(self):
        if any(rec.hoi_dong_ids.filtered(lambda hd: hd.trang_thai != 'hoan_thanh') for rec in self):
            raise UserError(_('Cần hoàn thành các hội đồng trước khi kết thúc đợt.'))
        self._chuyen_giai_doan('dang_bao_ve', 'ket_thuc')


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

    def _is_bcn(self):
        return self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem')

    def _current_sinh_vien(self):
        return self.env['quanly.sinhvien'].search([('user_id', '=', self.env.user.id)], limit=1)

    def write(self, vals):
        self.mapped('dot_do_an_id')._check_open()
        if vals.get('dot_do_an_id'):
            self.env['quanly.dotdoan'].browse(vals['dot_do_an_id'])._check_open()
        if 'trang_thai' in vals and any(
            vals['trang_thai'] != rec.trang_thai and (rec.trang_thai != 'cho_duyet' or vals['trang_thai'] not in ('da_duyet', 'tu_choi'))
            for rec in self
        ):
            raise UserError(_('Chỉ được duyệt hoặc từ chối đăng ký đang chờ duyệt.'))
        if set(vals) & {'sinh_vien_id', 'dot_do_an_id'} and any(rec.trang_thai != 'cho_duyet' for rec in self):
            raise UserError(_('Không thể đổi người hoặc đợt của đăng ký đã xử lý.'))
        if set(vals) & {'sinh_vien_id', 'dot_do_an_id', 'trang_thai'}:
            topics = self.env['quanly.detai'].search([('dang_ky_id', 'in', self.ids)])
            if topics and (set(vals) & {'sinh_vien_id', 'dot_do_an_id'} or vals.get('trang_thai', 'da_duyet') != 'da_duyet'):
                raise UserError(_('Đăng ký đã giao đề tài, không thể đổi sinh viên, đợt hoặc hủy duyệt.'))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self.env['quanly.dotdoan'].browse(vals.get('dot_do_an_id'))._check_open()
        if not self._is_bcn():
            sinh_vien = self._current_sinh_vien()
            if not sinh_vien:
                raise AccessError(_('Tài khoản này chưa có hồ sơ sinh viên.'))
            for vals in vals_list:
                if vals.get('sinh_vien_id') != sinh_vien.id:
                    raise AccessError(_('Bạn chỉ được đăng ký đồ án cho chính mình.'))
                if sinh_vien.trang_thai != 'dang_hoc':
                    raise UserError(_('Chỉ sinh viên đang học được đăng ký đồ án.'))
                dot = self.env['quanly.dotdoan'].browse(vals.get('dot_do_an_id'))
                if not dot.exists() or dot.trang_thai != 'dang_dang_ky':
                    raise UserError(_('Đợt đồ án này hiện không mở đăng ký.'))
                vals['trang_thai'] = 'cho_duyet'
        return super().create(vals_list)

    def unlink(self):
        self.mapped('dot_do_an_id')._check_open()
        if any(rec.trang_thai != 'cho_duyet' for rec in self):
            raise UserError(_('Không thể xóa đăng ký đã được xử lý.'))
        return super().unlink()

    @api.depends('sinh_vien_id.ho_ten', 'dot_do_an_id.ten_dot')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.sinh_vien_id.ho_ten or ''} - {rec.dot_do_an_id.ten_dot or ''}"

    def action_duyet(self):
        if not self._is_bcn():
            raise AccessError(_('Chỉ Ban chủ nhiệm khoa được duyệt đăng ký.'))
        if any(rec.trang_thai != 'cho_duyet' for rec in self):
            raise UserError(_('Chỉ có thể duyệt đăng ký đang chờ duyệt.'))
        self.write({'trang_thai': 'da_duyet'})

    def action_tu_choi(self):
        if not self._is_bcn():
            raise AccessError(_('Chỉ Ban chủ nhiệm khoa được từ chối đăng ký.'))
        if any(rec.trang_thai != 'cho_duyet' for rec in self):
            raise UserError(_('Chỉ có thể từ chối đăng ký đang chờ duyệt.'))
        self.write({'trang_thai': 'tu_choi'})

class NganHangDeTai(models.Model):
    _name = 'quanly.nganhangdetai'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self.env['quanly.dotdoan'].browse(vals.get('dot_do_an_id'))._check_open()
        return super().create(vals_list)

    def write(self, vals):
        self.mapped('dot_do_an_id')._check_open()
        if vals.get('dot_do_an_id'):
            self.env['quanly.dotdoan'].browse(vals['dot_do_an_id'])._check_open()
        if set(vals) & {'dot_do_an_id', 'trang_thai'}:
            topics = self.env['quanly.detai'].search([('ngan_hang_de_tai_id', 'in', self.ids)])
            if topics and ('dot_do_an_id' in vals or vals.get('trang_thai') not in ('da_duyet', 'da_chon')):
                raise UserError(_('Đề xuất đã giao đề tài, không được đổi đợt hoặc hủy duyệt.'))
        return super().write(vals)

    def unlink(self):
        self.mapped('dot_do_an_id')._check_open()
        if self.env['quanly.detai'].search_count([('ngan_hang_de_tai_id', 'in', self.ids)]):
            raise UserError(_('Không thể xóa nguồn đề xuất đã được giao đề tài.'))
        return super().unlink()

    def _is_bcn(self):
        return self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem')

    def action_duyet(self):
        if not self._is_bcn():
            raise AccessError(_('Chỉ Ban chủ nhiệm khoa được duyệt đề tài đề xuất.'))
        if any(rec.trang_thai not in ('du_thao', 'cho_duyet') for rec in self):
            raise UserError(_('Chỉ có thể duyệt đề tài ở trạng thái dự thảo hoặc chờ duyệt.'))
        self.write({'trang_thai': 'da_duyet'})

    def action_tu_choi(self):
        if not self._is_bcn():
            raise AccessError(_('Chỉ Ban chủ nhiệm khoa được từ chối đề tài đề xuất.'))
        if any(rec.trang_thai not in ('du_thao', 'cho_duyet') for rec in self):
            raise UserError(_('Đề tài này không ở trạng thái có thể từ chối.'))
        self.write({'trang_thai': 'tu_choi'})
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

