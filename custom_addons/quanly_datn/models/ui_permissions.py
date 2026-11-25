from odoo import api, fields, models


class UiPermissions(models.AbstractModel):
    _name = 'quanly.ui.permissions'
    _description = 'Quyền thao tác trên giao diện ĐATN'

    ui_manager = fields.Boolean(compute='_compute_ui_permissions')
    ui_reviewer = fields.Boolean(compute='_compute_ui_permissions')
    ui_owner = fields.Boolean(compute='_compute_ui_permissions')

    @api.depends_context('uid')
    def _compute_ui_permissions(self):
        manager = self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem')
        for rec in self:
            rec.ui_manager = manager
            rec.ui_owner = False
            rec.ui_reviewer = manager
            if rec._name == 'quanly.detai':
                rec.ui_owner = rec.sinh_vien_id.user_id == self.env.user
                rec.ui_reviewer = manager or rec.giang_vien_huong_dan_id.user_id == self.env.user
            elif rec._name == 'quanly.baocao':
                rec.ui_owner = rec.de_tai_id.sinh_vien_id.user_id == self.env.user
                rec.ui_reviewer = manager or rec.de_tai_id.giang_vien_huong_dan_id.user_id == self.env.user
            elif rec._name == 'quanly.phieuchamdiem':
                rec.ui_reviewer = manager or rec.giang_vien_id.user_id == self.env.user
                rec.ui_reviewer = rec.ui_reviewer and rec.hoi_dong_id.trang_thai == 'dang_cham' and not rec.da_khoa_diem
            if rec._name == 'quanly.baocao' and rec.de_tai_id.trang_thai in ('cho_bao_ve', 'da_bao_ve', 'da_luu_chieu'):
                rec.ui_reviewer = False
            topic = rec if rec._name == 'quanly.detai' else rec.de_tai_id if rec._name in ('quanly.baocao', 'quanly.phieuchamdiem') else False
            if topic and (topic.dot_do_an_id.trang_thai == 'ket_thuc' or topic.trang_thai == 'da_luu_chieu'):
                rec.ui_manager = False
                rec.ui_reviewer = False
                rec.ui_owner = False
