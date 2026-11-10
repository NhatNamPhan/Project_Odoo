# -*- coding: utf-8 -*-
from odoo import models, fields

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


class TepThongBao(models.Model):
    _name = 'quanly.tepthongbao'
    _description = 'Tệp đính kèm thông báo'
    _rec_name = 'ten_tep'

    thong_bao_id = fields.Many2one('quanly.thongbao', string='Thông báo', required=True, ondelete='cascade')
    ten_tep = fields.Char(string='Tên tệp', required=True)
    file_dinh_kem = fields.Binary(string='File đính kèm')
    url_tep = fields.Char(string='URL tệp')


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
