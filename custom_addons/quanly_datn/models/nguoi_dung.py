# -*- coding: utf-8 -*-
from odoo import models, fields

class SinhVien(models.Model):
    _name = 'quanly.sinhvien'
    _description = 'Thông tin sinh viên'
    _rec_name = 'ho_ten'

    user_id = fields.Many2one('res.users', string='Tài khoản người dùng', required=True, ondelete='cascade')
    ma_sv = fields.Char(string='Mã số sinh viên', required=True, copy=False)
    ho_ten = fields.Char(string='Họ và tên', related='user_id.name', store=True, readonly=False)
    email = fields.Char(string='Email', related='user_id.login', store=True, readonly=False)
    sdt = fields.Char(string='Số điện thoại')
    lop_sinh_hoat_id = fields.Many2one('quanly.lopsinhhoat', string='Lớp sinh hoạt', required=True)
    chuyen_nganh_id = fields.Many2one(
        'quanly.chuyennganh', 
        string='Chuyên ngành', 
        related='lop_sinh_hoat_id.chuyen_nganh_id', 
        store=True, 
        readonly=True
    )
    trang_thai = fields.Selection([
        ('dang_hoc', 'Đang học'),
        ('da_tot_nghiep', 'Đã tốt nghiệp'),
        ('tam_dung', 'Tạm dừng')
    ], string='Trạng thái', default='dang_hoc')

    _sql_constraints = [
        ('ma_sv_uniq', 'unique(ma_sv)', 'Mã số sinh viên đã tồn tại!'),
        ('user_id_uniq', 'unique(user_id)', 'Tài khoản người dùng này đã gắn với một sinh viên!')
    ]


class GiangVien(models.Model):
    _name = 'quanly.giangvien'
    _description = 'Thông tin giảng viên'
    _rec_name = 'ho_ten'

    user_id = fields.Many2one('res.users', string='Tài khoản người dùng', required=True, ondelete='cascade')
    ma_gv = fields.Char(string='Mã giảng viên', required=True, copy=False)
    ho_ten = fields.Char(string='Họ và tên', related='user_id.name', store=True, readonly=False)
    email = fields.Char(string='Email', related='user_id.login', store=True, readonly=False)
    sdt = fields.Char(string='Số điện thoại')
    chuyen_nganh_id = fields.Many2one('quanly.chuyennganh', string='Chuyên ngành / Bộ môn', required=True)
    hoc_ham_hoc_vi = fields.Selection([
        ('cu_nhan', 'Cử nhân / Kỹ sư'),
        ('thac_si', 'Thạc sĩ'),
        ('tien_si', 'Tiến sĩ'),
        ('pho_giao_su', 'Phó Giáo sư'),
        ('giao_su', 'Giáo sư')
    ], string='Học hàm / Học vị', default='thac_si')
    han_muc_huong_dan = fields.Integer(string='Hạn mức hướng dẫn tối đa', default=5)

    _sql_constraints = [
        ('ma_gv_uniq', 'unique(ma_gv)', 'Mã giảng viên đã tồn tại!'),
        ('user_id_uniq', 'unique(user_id)', 'Tài khoản người dùng này đã gắn với một giảng viên!')
    ]

