# -*- coding: utf-8 -*-
from odoo import models, fields

class ChuyenNganh(models.Model):
    _name = 'quanly.chuyennganh'
    _description = 'Chuyên ngành đào tạo'
    _rec_name = 'ten_chuyen_nganh'

    ma_chuyen_nganh = fields.Char(string='Mã chuyên ngành', required=True, copy=False)
    ten_chuyen_nganh = fields.Char(string='Tên chuyên ngành', required=True)
    mo_ta = fields.Text(string='Mô tả')

    lop_ids = fields.One2many('quanly.lopsinhhoat', 'chuyen_nganh_id', string='Danh sách lớp')
    giang_vien_ids = fields.One2many('quanly.giangvien', 'chuyen_nganh_id', string='Danh sách giảng viên')

    _sql_constraints = [
        ('ma_chuyen_nganh_uniq', 'unique(ma_chuyen_nganh)', 'Mã chuyên ngành đã tồn tại!')
    ]


class LopSinhHoat(models.Model):
    _name = 'quanly.lopsinhhoat'
    _description = 'Lớp sinh hoạt'
    _rec_name = 'ten_lop'

    ma_lop = fields.Char(string='Mã lớp', required=True, copy=False)
    ten_lop = fields.Char(string='Tên lớp sinh hoạt', required=True)
    nien_khoa = fields.Char(string='Niên khóa', required=True)
    chuyen_nganh_id = fields.Many2one('quanly.chuyennganh', string='Chuyên ngành', required=True, ondelete='restrict')

    sinh_vien_ids = fields.One2many('quanly.sinhvien', 'lop_sinh_hoat_id', string='Danh sách sinh viên')

    _sql_constraints = [
        ('ma_lop_uniq', 'unique(ma_lop)', 'Mã lớp sinh hoạt đã tồn tại!')
    ]

