# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SinhVien(models.Model):
    _name = 'quanly.sinhvien'
    _description = 'Thông tin sinh viên'
    _rec_name = 'ho_ten'

    user_id = fields.Many2one('res.users', string='Tài khoản liên kết', required=False, ondelete='set null')
    ma_sv = fields.Char(string='Mã số sinh viên', required=True, copy=False)
    ho_ten = fields.Char(string='Họ và tên', required=True)
    email = fields.Char(string='Email', required=True)
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

    @api.constrains('ma_sv')
    def _check_ma_sv_uniq(self):
        for rec in self:
            duplicate = self.search([('ma_sv', '=', rec.ma_sv), ('id', '!=', rec.id)], limit=1)
            if duplicate:
                raise ValidationError(
                    _(f"Mã số sinh viên '{rec.ma_sv}' đã được cấp cho sinh viên '{duplicate.ho_ten}'. "
                      f"Vui lòng kiểm tra lại MSSV.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        group_sv = self.env.ref('quanly_datn.group_datn_sinh_vien', raise_if_not_found=False)
        group_internal = self.env.ref('base.group_user')
        groups = [group_internal.id]
        if group_sv:
            groups.append(group_sv.id)

        for vals in vals_list:
            email = vals.get('email')
            name = vals.get('ho_ten') or vals.get('ma_sv')
            if not email and vals.get('ma_sv'):
                email = f"sv_{vals.get('ma_sv').lower()}@sv.ute.udn.vn"
                vals['email'] = email

            if not vals.get('user_id') and email:
                user = self.env['res.users'].sudo().search([('login', '=', email)], limit=1)
                if not user:
                    user = self.env['res.users'].sudo().create({
                        'name': name,
                        'login': email,
                        'email': email,
                        'password': '123456',
                        'groups_id': [(6, 0, groups)],
                    })
                else:
                    existing_sv = self.search([('user_id', '=', user.id)], limit=1)
                    if existing_sv:
                        raise ValidationError(
                            _(f"Email '{email}' đã được liên kết với sinh viên '{existing_sv.ho_ten}' (MSSV: {existing_sv.ma_sv}). "
                              f"Vui lòng sử dụng email khác.")
                        )
                vals['user_id'] = user.id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.user_id:
                user_vals = {}
                if 'ho_ten' in vals:
                    user_vals['name'] = vals['ho_ten']
                if 'email' in vals:
                    user_vals['login'] = vals['email']
                    user_vals['email'] = vals['email']
                if user_vals:
                    rec.user_id.sudo().write(user_vals)
        return res


class GiangVien(models.Model):
    _name = 'quanly.giangvien'
    _description = 'Thông tin giảng viên'
    _rec_name = 'ho_ten'

    user_id = fields.Many2one('res.users', string='Tài khoản liên kết', required=False, ondelete='set null')
    ma_gv = fields.Char(string='Mã giảng viên', required=True, copy=False)
    ho_ten = fields.Char(string='Họ và tên', required=True)
    email = fields.Char(string='Email', required=True)
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

    @api.constrains('ma_gv')
    def _check_ma_gv_uniq(self):
        for rec in self:
            duplicate = self.search([('ma_gv', '=', rec.ma_gv), ('id', '!=', rec.id)], limit=1)
            if duplicate:
                raise ValidationError(
                    _(f"Mã giảng viên '{rec.ma_gv}' đã được cấp cho giảng viên '{duplicate.ho_ten}'. "
                      f"Vui lòng nhập mã mới (ví dụ: GV06, GV07...) hoặc vào menu 'Hồ sơ Giảng viên' để chuyển chuyên ngành.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        group_gv = self.env.ref('quanly_datn.group_datn_giang_vien', raise_if_not_found=False)
        group_internal = self.env.ref('base.group_user')
        groups = [group_internal.id]
        if group_gv:
            groups.append(group_gv.id)

        for vals in vals_list:
            email = vals.get('email')
            name = vals.get('ho_ten') or vals.get('ma_gv')
            if not email and vals.get('ma_gv'):
                email = f"gv_{vals.get('ma_gv').lower()}@ute.udn.vn"
                vals['email'] = email

            if not vals.get('user_id') and email:
                user = self.env['res.users'].sudo().search([('login', '=', email)], limit=1)
                if not user:
                    user = self.env['res.users'].sudo().create({
                        'name': name,
                        'login': email,
                        'email': email,
                        'password': '123456',
                        'groups_id': [(6, 0, groups)],
                    })
                else:
                    existing_gv = self.search([('user_id', '=', user.id)], limit=1)
                    if existing_gv:
                        raise ValidationError(
                            _(f"Email '{email}' đã được liên kết với giảng viên '{existing_gv.ho_ten}' (Mã GV: {existing_gv.ma_gv}). "
                              f"Vui lòng sử dụng email khác.")
                        )
                vals['user_id'] = user.id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.user_id:
                user_vals = {}
                if 'ho_ten' in vals:
                    user_vals['name'] = vals['ho_ten']
                if 'email' in vals:
                    user_vals['login'] = vals['email']
                    user_vals['email'] = vals['email']
                if user_vals:
                    rec.user_id.sudo().write(user_vals)
        return res
