# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
import pytz

class DotBaoCao(models.Model):
    _name = 'quanly.dotbaocao'
    _description = 'Đợt nộp báo cáo tiến độ'
    _rec_name = 'ten_dot_bao_cao'
    _order = 'thu_tu asc, han_nop asc'

    dot_do_an_id = fields.Many2one('quanly.dotdoan', string='Đợt đồ án', required=True, ondelete='cascade')
    ten_dot_bao_cao = fields.Char(string='Tên đợt báo cáo', required=True)
    noi_dung_yeu_cau = fields.Text(string='Nội dung yêu cầu nộp')
    thu_tu = fields.Integer(string='Thứ tự đợt', default=1, required=True)
    han_nop = fields.Date(string='Hạn nộp cuối cùng', required=True)
    la_ban_cuoi = fields.Boolean(string='Là bản nộp hoàn thiện (Bản cuối)', default=False)

    bao_cao_ids = fields.One2many('quanly.baocao', 'dot_bao_cao_id', string='Danh sách bài nộp')

    _sql_constraints = [
        ('dot_thu_tu_uniq', 'unique(dot_do_an_id, thu_tu)', 'Thứ tự đợt báo cáo đã tồn tại trong đợt đồ án!'),
    ]

    @api.constrains('thu_tu')
    def _check_thu_tu(self):
        for rec in self:
            if rec.thu_tu < 1:
                raise ValidationError(_('Thứ tự đợt báo cáo phải lớn hơn 0.'))

    def _check_edit_periods(self, batches):
        batches._check_open()
        if self.env['quanly.detai'].sudo().search_count([
            ('dot_do_an_id', 'in', batches.ids), ('trang_thai', 'not in', ['dang_thuc_hien', 'khong_duoc_bao_ve'])
        ]):
            raise UserError(_('Không thể đổi các đợt báo cáo khi đã có đề tài gửi yêu cầu bảo vệ.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_edit_periods(self.env['quanly.dotdoan'].browse(vals.get('dot_do_an_id')))
        return super().create(vals_list)

    def write(self, vals):
        self.mapped('dot_do_an_id')._check_open()
        if 'dot_do_an_id' in vals and self.mapped('bao_cao_ids'):
            raise UserError(_('Không thể chuyển đợt báo cáo đã có bài nộp sang đợt đồ án khác.'))
        if set(vals) & {'dot_do_an_id', 'thu_tu', 'la_ban_cuoi'}:
            self._check_edit_periods(self.mapped('dot_do_an_id'))
            if vals.get('dot_do_an_id'):
                self._check_edit_periods(self.env['quanly.dotdoan'].browse(vals['dot_do_an_id']))
        return super().write(vals)

    def unlink(self):
        self._check_edit_periods(self.mapped('dot_do_an_id'))
        if self.mapped('bao_cao_ids'):
            raise UserError(_('Không thể xóa đợt báo cáo đã có bài nộp.'))
        return super().unlink()


class BaoCao(models.Model):
    _inherit = 'quanly.ui.permissions'
    _name = 'quanly.baocao'
    _description = 'Báo cáo tiến độ đề tài'
    _rec_name = 'ten_tep'
    _order = 'ngay_nop desc'

    de_tai_id = fields.Many2one('quanly.detai', string='Đề tài', required=True, ondelete='cascade')
    dot_do_an_id = fields.Many2one(related='de_tai_id.dot_do_an_id', string='Đợt đồ án')
    dot_bao_cao_id = fields.Many2one('quanly.dotbaocao', string='Đợt báo cáo', required=True, ondelete='restrict')
    phien_ban = fields.Integer(string='Phiên bản nộp', default=1)
    ten_tep = fields.Char(string='Tên tệp báo cáo', required=True)
    file_bao_cao = fields.Binary(string='Tệp đính kèm (PDF/Word)', required=True)
    url_tep = fields.Char(string='URL tệp lưu trữ')
    ngay_nop = fields.Datetime(string='Ngày nộp', default=fields.Datetime.now, readonly=True)
    nop_tre = fields.Boolean(string='Nộp trễ hạn', compute='_compute_nop_tre', store=True)
    phan_hoi_gvhd = fields.Text(string='Nhận xét / Phản hồi của GVHD')
    trang_thai = fields.Selection([
        ('dang_cho', 'Đang chờ duyệt'),
        ('dat', 'Đạt yêu cầu'),
        ('can_sua', 'Cần sửa đổi nộp lại'),
        ('khong_dat', 'Không đạt')
    ], string='Trạng thái duyệt', default='dang_cho')

    _sql_constraints = [
        ('de_tai_dot_phien_ban_uniq', 'unique(de_tai_id, dot_bao_cao_id, phien_ban)', 'Phiên bản báo cáo đã tồn tại trong đợt này.'),
    ]

    @api.constrains('phien_ban')
    def _check_phien_ban(self):
        for rec in self:
            if rec.phien_ban < 1:
                raise ValidationError(_('Phiên bản báo cáo phải lớn hơn 0.'))

    def _is_bcn(self):
        return self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem')

    def action_dat(self):
        self.write({'trang_thai': 'dat'})

    def action_can_sua(self):
        self.write({'trang_thai': 'can_sua'})

    def action_khong_dat(self):
        self.write({'trang_thai': 'khong_dat'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            de_tai = self.env['quanly.detai'].browse(vals.get('de_tai_id'))
            dot_bao_cao = self.env['quanly.dotbaocao'].browse(vals.get('dot_bao_cao_id'))
            if not de_tai.exists() or not dot_bao_cao.exists() or dot_bao_cao.dot_do_an_id != de_tai.dot_do_an_id:
                raise ValidationError(_('Đợt báo cáo phải thuộc cùng đợt đồ án với đề tài.'))
            de_tai.dot_do_an_id._check_open()
            if not self.env.su and de_tai.trang_thai != 'dang_thuc_hien':
                raise UserError(_('Chỉ được nộp báo cáo khi đề tài đang thực hiện.'))
        if not self._is_bcn():
            sinh_vien = self.env['quanly.sinhvien'].search([('user_id', '=', self.env.user.id)], limit=1)
            if not sinh_vien:
                raise AccessError(_('Tài khoản này chưa có hồ sơ sinh viên.'))
            next_versions = {}
            for vals in vals_list:
                de_tai = self.env['quanly.detai'].browse(vals.get('de_tai_id'))
                if not de_tai.exists() or de_tai.sinh_vien_id != sinh_vien:
                    raise AccessError(_('Bạn chỉ được nộp báo cáo cho đề tài của chính mình.'))
                if de_tai.trang_thai != 'dang_thuc_hien':
                    raise ValidationError(_('Chỉ được nộp báo cáo khi đề tài đang thực hiện.'))
                key = (de_tai.id, vals['dot_bao_cao_id'])
                # Serialize submissions for this thesis to allocate versions safely.
                self.env.cr.execute('SELECT id FROM quanly_detai WHERE id = %s FOR UPDATE', [de_tai.id])
                if key not in next_versions:
                    previous = self.search([
                        ('de_tai_id', '=', key[0]), ('dot_bao_cao_id', '=', key[1])
                    ], order='phien_ban desc', limit=1)
                    next_versions[key] = (previous.phien_ban or 0) + 1
                vals['phien_ban'] = next_versions[key]
                next_versions[key] += 1
                vals['trang_thai'] = 'dang_cho'
                vals['ngay_nop'] = fields.Datetime.now()
                vals.pop('phan_hoi_gvhd', None)
        return super().create(vals_list)

    @api.constrains('de_tai_id', 'dot_bao_cao_id')
    def _check_dot_bao_cao(self):
        for rec in self:
            if rec.dot_bao_cao_id.dot_do_an_id != rec.de_tai_id.dot_do_an_id:
                raise ValidationError(_('Đợt báo cáo phải thuộc cùng đợt đồ án với đề tài.'))

    def write(self, vals):
        self.check_access('write')
        self.mapped('de_tai_id.dot_do_an_id')._check_open()
        if any(rec.de_tai_id.trang_thai in ('cho_bao_ve', 'da_bao_ve', 'da_luu_chieu') for rec in self):
            raise UserError(_('Báo cáo đã dùng để xác nhận bảo vệ, không thể sửa đánh giá hoặc bài nộp.'))
        if set(vals) & {'de_tai_id', 'dot_bao_cao_id', 'phien_ban', 'ngay_nop', 'file_bao_cao', 'ten_tep'}:
            raise UserError(_('Bài đã nộp không được ghi đè. Cần nộp phiên bản mới.'))
        if self._is_bcn():
            return super().write(vals)
        if not self.env.user.has_group('quanly_datn.group_datn_giang_vien') or any(
            rec.de_tai_id.giang_vien_huong_dan_id.user_id != self.env.user for rec in self
        ):
            raise AccessError(_('Chỉ giảng viên hướng dẫn được phản hồi báo cáo.'))
        allowed_fields = {'phan_hoi_gvhd', 'trang_thai'}
        if not set(vals).issubset(allowed_fields):
            raise AccessError(_('Giảng viên chỉ được cập nhật phản hồi và trạng thái duyệt báo cáo.'))
        return super().write(vals)

    def unlink(self):
        self.mapped('de_tai_id.dot_do_an_id')._check_open()
        if any(rec.trang_thai != 'dang_cho' or rec.de_tai_id.trang_thai != 'dang_thuc_hien' for rec in self):
            raise UserError(_('Không thể xóa báo cáo đã đánh giá hoặc đã gửi yêu cầu bảo vệ.'))
        return super().unlink()

    @api.depends('ngay_nop', 'dot_bao_cao_id.han_nop')
    def _compute_nop_tre(self):
        for rec in self:
            if rec.ngay_nop and rec.dot_bao_cao_id.han_nop:
                rec.nop_tre = pytz.UTC.localize(rec.ngay_nop).astimezone(pytz.timezone('Asia/Ho_Chi_Minh')).date() > rec.dot_bao_cao_id.han_nop
            else:
                rec.nop_tre = False

