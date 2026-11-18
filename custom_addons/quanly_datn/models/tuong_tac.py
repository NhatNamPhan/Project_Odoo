# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class ThongBao(models.Model):
    _name = 'quanly.thongbao'
    _description = 'Thông báo đợt đồ án'
    _rec_name = 'tieu_de'
    _order = 'ngay_tao desc'

    tieu_de = fields.Char(string='Tiêu đề thông báo', required=True)
    noi_dung = fields.Html(string='Nội dung thông báo', required=True)
    nguoi_gui_id = fields.Many2one('res.users', string='Người gửi', default=lambda self: self.env.user, required=True)
    dot_do_an_id = fields.Many2one('quanly.dotdoan', string='Đợt đồ án liên quan')
    ngay_tao = fields.Datetime(string='Thời gian gửi', default=fields.Datetime.now, readonly=True)

    tep_ids = fields.One2many('quanly.tepthongbao', 'thong_bao_id', string='Tệp đính kèm thông báo')
    nguoi_nhan_ids = fields.One2many(
        'quanly.nguoinhanthongbao',
        'thong_bao_id',
        string='Danh sách người nhận'
    )

    def _is_bcn(self):
        return self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem')

    @api.model_create_multi
    def create(self, vals_list):
        if not self._is_bcn():
            raise AccessError(_('Chỉ người phụ trách đợt đồ án được đăng thông báo chính thức.'))
        for vals in vals_list:
            vals['nguoi_gui_id'] = self.env.user.id
        records = super().create(vals_list)
        records._tao_nguoi_nhan_tu_dot_do_an()
        return records

    def _tao_nguoi_nhan_tu_dot_do_an(self):
        recipient_model = self.env['quanly.nguoinhanthongbao']
        for record in self:
            if not record.dot_do_an_id:
                continue
            users = record.dot_do_an_id.dang_ky_ids.filtered(
                lambda dang_ky: dang_ky.trang_thai == 'da_duyet'
            ).mapped('sinh_vien_id.user_id')
            existing_users = record.nguoi_nhan_ids.mapped('nguoi_nhan_id')
            missing_users = users - existing_users
            if missing_users:
                recipient_model.create([
                    {
                        'thong_bao_id': record.id,
                        'nguoi_nhan_id': user.id,
                    }
                    for user in missing_users
                ])

    def write(self, vals):
        if 'dot_do_an_id' in vals and any(record.nguoi_nhan_ids for record in self):
            raise UserError(_('Không thể đổi đợt đồ án sau khi thông báo đã có người nhận.'))
        return super().write(vals)

    def action_dong_bo_nguoi_nhan(self):
        if not self._is_bcn():
            raise AccessError(_('Chỉ người phụ trách đợt đồ án được đồng bộ người nhận.'))
        if any(not record.dot_do_an_id for record in self):
            raise UserError(_('Cần chọn đợt đồ án trước khi đồng bộ người nhận.'))
        self._tao_nguoi_nhan_tu_dot_do_an()

    def action_danh_dau_da_doc(self):
        recipients = self.env['quanly.nguoinhanthongbao'].search([
            ('thong_bao_id', 'in', self.ids),
            ('nguoi_nhan_id', '=', self.env.user.id),
            ('da_doc', '=', False),
        ])
        recipients.action_danh_dau_da_doc()


class TepThongBao(models.Model):
    _name = 'quanly.tepthongbao'
    _description = 'Tệp đính kèm thông báo'
    _rec_name = 'ten_tep'

    thong_bao_id = fields.Many2one('quanly.thongbao', string='Thông báo', required=True, ondelete='cascade')
    ten_tep = fields.Char(string='Tên tệp', required=True)
    file_dinh_kem = fields.Binary(string='File đính kèm')
    url_tep = fields.Char(string='URL tệp')


class NguoiNhanThongBao(models.Model):
    _name = 'quanly.nguoinhanthongbao'
    _description = 'Người nhận thông báo'
    _rec_name = 'nguoi_nhan_id'

    thong_bao_id = fields.Many2one(
        'quanly.thongbao',
        string='Thông báo',
        required=True,
        ondelete='cascade'
    )
    nguoi_nhan_id = fields.Many2one(
        'res.users',
        string='Người nhận',
        required=True,
        ondelete='cascade'
    )
    da_doc = fields.Boolean(string='Đã đọc', default=False)
    ngay_doc = fields.Datetime(string='Thời gian đọc', readonly=True)

    def _is_bcn(self):
        return self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem')

    def write(self, vals):
        if not self._is_bcn():
            if any(record.nguoi_nhan_id != self.env.user for record in self):
                raise AccessError(_('Bạn chỉ được cập nhật trạng thái đọc của chính mình.'))
            if not set(vals).issubset({'da_doc', 'ngay_doc'}):
                raise AccessError(_('Bạn chỉ được cập nhật trạng thái đã đọc.'))
        return super().write(vals)

    def action_danh_dau_da_doc(self):
        unread_records = self.filtered(
            lambda record: record.nguoi_nhan_id == self.env.user and not record.da_doc
        )
        if unread_records:
            unread_records.write({
                'da_doc': True,
                'ngay_doc': fields.Datetime.now(),
            })


class TinNhan(models.Model):
    _name = 'quanly.tinnhan'
    _description = 'Tin nhắn trao đổi tiến độ đề tài'
    _rec_name = 'noi_dung'
    _order = 'ngay_gui asc'

    de_tai_id = fields.Many2one('quanly.detai', string='Đề tài', required=True, ondelete='cascade')
    nguoi_gui_id = fields.Many2one('res.users', string='Người gửi', default=lambda self: self.env.user, required=True)
    noi_dung = fields.Text(string='Nội dung tin nhắn', required=True)
    da_doc = fields.Boolean(string='Đã đọc', default=False)
    ngay_gui = fields.Datetime(string='Thời gian gửi', default=fields.Datetime.now, readonly=True)

