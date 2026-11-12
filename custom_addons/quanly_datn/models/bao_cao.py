# -*- coding: utf-8 -*-
from odoo import models, fields, api

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


class BaoCao(models.Model):
    _name = 'quanly.baocao'
    _description = 'Báo cáo tiến độ đề tài'
    _rec_name = 'ten_tep'
    _order = 'ngay_nop desc'

    de_tai_id = fields.Many2one('quanly.detai', string='Đề tài', required=True, ondelete='cascade')
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

    @api.depends('ngay_nop', 'dot_bao_cao_id.han_nop')
    def _compute_nop_tre(self):
        for rec in self:
            if rec.ngay_nop and rec.dot_bao_cao_id.han_nop:
                rec.nop_tre = rec.ngay_nop.date() > rec.dot_bao_cao_id.han_nop
            else:
                rec.nop_tre = False

