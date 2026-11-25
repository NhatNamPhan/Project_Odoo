# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError

class HoiDong(models.Model):
    _name = 'quanly.hoidong'
    _description = 'Hội đồng chấm bảo vệ đồ án tốt nghiệp'
    _rec_name = 'ten_hoi_dong'

    dot_do_an_id = fields.Many2one('quanly.dotdoan', string='Đợt đồ án', required=True)
    chuyen_nganh_id = fields.Many2one('quanly.chuyennganh', string='Chuyên ngành', required=True)
    ma_hoi_dong = fields.Char(string='Mã hội đồng', required=True, copy=False)
    ten_hoi_dong = fields.Char(string='Tên hội đồng', required=True)

    thoi_gian_bao_ve = fields.Datetime(string='Thời gian bắt đầu bảo vệ', required=True)
    dia_diem = fields.Char(string='Phòng / Địa điểm bảo vệ (vd: Phòng A203 / Online Zoom)', required=True)

    trang_thai = fields.Selection([
        ('du_thao', 'Dự thảo lập hội đồng'),
        ('da_chot_lich', 'Đã chốt lịch bảo vệ'),
        ('dang_cham', 'Đang tiến hành chấm thi'),
        ('hoan_thanh', 'Đã hoàn thành')
    ], string='Trạng thái', default='du_thao')

    thanh_vien_ids = fields.One2many('quanly.hoidonggiangvien', 'hoi_dong_id', string='Thành viên hội đồng')
    de_tai_ids = fields.One2many('quanly.detai', 'hoi_dong_id', string='Danh sách đề tài bảo vệ')

    _sql_constraints = [
        ('ma_hoi_dong_uniq', 'unique(ma_hoi_dong)', 'Mã hội đồng đã tồn tại!')
    ]

    def _check_manager(self):
        if not self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem'):
            raise AccessError(_('Chỉ Ban chủ nhiệm khoa được điều hành hội đồng.'))

    def write(self, vals):
        self.mapped('dot_do_an_id')._check_open()
        if vals.get('dot_do_an_id'):
            self.env['quanly.dotdoan'].browse(vals['dot_do_an_id'])._check_open()
        if any(rec.trang_thai != 'du_thao' for rec in self) and set(vals) & {'thoi_gian_bao_ve', 'dia_diem', 'thanh_vien_ids', 'de_tai_ids'}:
            raise UserError(_('Hội đồng đã chốt lịch, không được thay đổi lịch hoặc phân công.'))
        if 'trang_thai' in vals:
            allowed = {'du_thao': 'da_chot_lich', 'da_chot_lich': 'dang_cham', 'dang_cham': 'hoan_thanh'}
            if any(vals['trang_thai'] != rec.trang_thai and allowed.get(rec.trang_thai) != vals['trang_thai'] for rec in self):
                raise UserError(_('Không được bỏ qua hoặc quay ngược giai đoạn hội đồng.'))
            # All entry points must validate the same preconditions as the buttons.
            if vals['trang_thai'] in ('da_chot_lich', 'dang_cham'):
                self._check_ready()
            if vals['trang_thai'] == 'dang_cham' and any(rec.dot_do_an_id.trang_thai != 'dang_bao_ve' for rec in self):
                raise UserError(_('Cần chuyển đợt đồ án sang giai đoạn bảo vệ trước khi chấm.'))
            if vals['trang_thai'] == 'hoan_thanh':
                if any(not rec.de_tai_ids or not rec.thanh_vien_ids for rec in self):
                    raise UserError(_('Hội đồng chưa có đủ đề tài và thành viên.'))
                if any(dt.trang_thai != 'da_bao_ve' or not dt.da_khoa_diem for dt in self.mapped('de_tai_ids')):
                    raise UserError(_('Cần hoàn thành và khóa điểm bằng nút nghiệp vụ.'))
        if set(vals) & {'dot_do_an_id', 'chuyen_nganh_id'} and any(rec.de_tai_ids for rec in self):
            raise UserError(_('Hội đồng đã có đề tài; không được đổi đợt hoặc chuyên ngành.'))
        result = super().write(vals)
        if vals.get('trang_thai') == 'dang_cham':
            for rec in self:
                for dt in rec.de_tai_ids:
                    for member in rec.thanh_vien_ids:
                        if not dt.phieu_cham_diem_ids.filtered(lambda p: p.hoi_dong_giang_vien_id == member):
                            self.env['quanly.phieuchamdiem'].create({'de_tai_id': dt.id, 'hoi_dong_giang_vien_id': member.id})
        return result

    def _check_ready(self):
        for rec in self:
            if not rec.thanh_vien_ids or not rec.de_tai_ids:
                raise UserError(_('Hội đồng phải có thành viên và đề tài.'))
            if any(not dt.gvhd_da_duyet or dt.trang_thai != 'cho_bao_ve' for dt in rec.de_tai_ids):
                raise UserError(_('Các đề tài phải được GVHD xác nhận đủ điều kiện bảo vệ.'))
            rec.de_tai_ids._check_bao_cao_dat()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self.env['quanly.dotdoan'].browse(vals.get('dot_do_an_id'))._check_open()
            if not self.env.su and vals.get('trang_thai', 'du_thao') != 'du_thao':
                raise UserError(_('Hội đồng mới phải bắt đầu ở dự thảo.'))
        return super().create(vals_list)

    def unlink(self):
        self.mapped('dot_do_an_id')._check_open()
        if any(rec.trang_thai != 'du_thao' or rec.de_tai_ids for rec in self):
            raise UserError(_('Không thể xóa hội đồng đã chốt hoặc đã phân đề tài.'))
        return super().unlink()

    def action_chot_lich(self):
        self._check_manager()
        for rec in self:
            if rec.trang_thai != 'du_thao' or not rec.thanh_vien_ids or not rec.de_tai_ids:
                raise UserError(_('Hội đồng phải ở dự thảo, có thành viên và đề tài trước khi chốt lịch.'))
            if any(not dt.gvhd_da_duyet or dt.trang_thai != 'cho_bao_ve' for dt in rec.de_tai_ids):
                raise UserError(_('Các đề tài phải được GVHD xác nhận đủ điều kiện bảo vệ.'))
        self.write({'trang_thai': 'da_chot_lich'})

    def action_bat_dau_cham(self):
        self._check_manager()
        if any(rec.trang_thai != 'da_chot_lich' for rec in self):
            raise UserError(_('Cần chốt lịch trước khi bắt đầu chấm.'))
        self._check_ready()
        self.write({'trang_thai': 'dang_cham'})

    def action_hoan_thanh(self):
        self._check_manager()
        for rec in self:
            if rec.trang_thai != 'dang_cham' or not rec.de_tai_ids:
                raise UserError(_('Hội đồng chưa ở giai đoạn chấm hoặc chưa có đề tài.'))
            rec.de_tai_ids._check_du_diem()
            for dt in rec.de_tai_ids:
                graded = dt.phieu_cham_diem_ids.filtered(lambda p: p.trang_thai == 'da_cham').mapped('hoi_dong_giang_vien_id')
                if not rec.thanh_vien_ids or rec.thanh_vien_ids - graded:
                    raise UserError(_('Cần đủ phiếu đã chấm của từng thành viên cho mỗi đề tài.'))
        self.mapped('de_tai_ids').write({'trang_thai': 'da_bao_ve', 'da_khoa_diem': True})
        self.write({'trang_thai': 'hoan_thanh'})


class HoiDongGiangVien(models.Model):
    _name = 'quanly.hoidonggiangvien'
    _description = 'Giảng viên trong Hội đồng'
    _rec_name = 'display_name'

    hoi_dong_id = fields.Many2one('quanly.hoidong', string='Hội đồng', required=True, ondelete='cascade')
    giang_vien_id = fields.Many2one('quanly.giangvien', string='Giảng viên', required=True)
    vai_tro = fields.Selection([
        ('chu_tich', 'Chủ tịch Hội đồng'),
        ('thu_ky', 'Thư ký Hội đồng'),
        ('uy_vien', 'Ủy viên'),
        ('phan_bien', 'Cán bộ Phản biện')
    ], string='Vai trò trong Hội đồng', default='uy_vien', required=True)

    display_name = fields.Char(string='Tên hiển thị', compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('hd_gv_uniq', 'unique(hoi_dong_id, giang_vien_id)', 'Giảng viên đã có tên trong hội đồng này rồi!')
    ]

    @api.depends('giang_vien_id.ho_ten', 'vai_tro')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.giang_vien_id.ho_ten or ''} ({dict(self._fields['vai_tro'].selection).get(rec.vai_tro, '')})"

    def _check_draft(self):
        self.mapped('hoi_dong_id.dot_do_an_id')._check_open()
        if any(rec.hoi_dong_id.trang_thai != 'du_thao' for rec in self):
            raise UserError(_('Chỉ được sửa thành viên khi hội đồng còn dự thảo.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            council = self.env['quanly.hoidong'].browse(vals.get('hoi_dong_id'))
            council.dot_do_an_id._check_open()
            if council.trang_thai != 'du_thao':
                raise UserError(_('Chỉ được thêm thành viên vào hội đồng dự thảo.'))
        return super().create(vals_list)

    def write(self, vals):
        self._check_draft()
        if vals.get('hoi_dong_id'):
            target = self.env['quanly.hoidong'].browse(vals['hoi_dong_id'])
            target.dot_do_an_id._check_open()
            if target.trang_thai != 'du_thao':
                raise UserError(_('Không thể chuyển thành viên sang hội đồng đã chốt.'))
        if set(vals) & {'hoi_dong_id', 'giang_vien_id', 'vai_tro'} and self.env['quanly.phieuchamdiem'].search_count([('hoi_dong_giang_vien_id', 'in', self.ids)]):
            raise UserError(_('Thành viên đã có phiếu chấm, không được đổi phân công.'))
        return super().write(vals)

    def unlink(self):
        self._check_draft()
        if self.env['quanly.phieuchamdiem'].search_count([('hoi_dong_giang_vien_id', 'in', self.ids)]):
            raise UserError(_('Không thể xóa thành viên đã có phiếu chấm.'))
        return super().unlink()


class PhieuChamDiem(models.Model):
    _inherit = 'quanly.ui.permissions'
    _name = 'quanly.phieuchamdiem'
    _description = 'Phiếu chấm điểm của thành viên Hội đồng'
    _rec_name = 'display_name'

    de_tai_id = fields.Many2one('quanly.detai', string='Đề tài chấm điểm', required=True, ondelete='cascade')
    hoi_dong_id = fields.Many2one(related='de_tai_id.hoi_dong_id', string='Hội đồng')
    da_khoa_diem = fields.Boolean(related='de_tai_id.da_khoa_diem')
    hoi_dong_giang_vien_id = fields.Many2one(
        'quanly.hoidonggiangvien', 
        string='Cán bộ chấm thi', 
        required=True, 
        ondelete='cascade'
    )
    giang_vien_id = fields.Many2one(
        'quanly.giangvien', 
        string='Giảng viên chấm', 
        related='hoi_dong_giang_vien_id.giang_vien_id', 
        store=True, 
        readonly=True
    )
    vai_tro = fields.Selection(
        string='Vai trò', 
        related='hoi_dong_giang_vien_id.vai_tro', 
        store=True, 
        readonly=True
    )

    diem_bao_cao = fields.Float(string='Điểm Báo cáo / Thuyết trình (thang 10)', digits=(4, 2))
    diem_do_an = fields.Float(string='Điểm Đồ án / Sản phẩm (thang 10)', digits=(4, 2))
    nhan_xet = fields.Text(string='Nhận xét chi tiết')
    trang_thai = fields.Selection([
        ('chua_cham', 'Chưa chấm'),
        ('da_cham', 'Đã chấm điểm')
    ], string='Trạng thái', default='chua_cham')
    ngay_cham = fields.Datetime(string='Thời điểm chấm', readonly=True)

    display_name = fields.Char(string='Tên hiển thị', compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('detai_cbcham_uniq', 'unique(de_tai_id, hoi_dong_giang_vien_id)', 'Cán bộ này đã có phiếu chấm cho đề tài rồi!')
    ]

    @api.depends('de_tai_id.ten_de_tai', 'giang_vien_id.ho_ten')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"Phiếu chấm: {rec.de_tai_id.ten_de_tai or ''} - {rec.giang_vien_id.ho_ten or ''}"

    @api.constrains('de_tai_id', 'hoi_dong_giang_vien_id')
    def _check_hoi_dong(self):
        for rec in self:
            if not rec.de_tai_id.hoi_dong_id or rec.de_tai_id.hoi_dong_id != rec.hoi_dong_giang_vien_id.hoi_dong_id:
                raise ValidationError(_('Giảng viên chấm phải thuộc hội đồng được phân cho đề tài.'))

    @api.constrains('diem_bao_cao', 'diem_do_an')
    def _check_diem(self):
        for rec in self:
            if not 0 <= rec.diem_bao_cao <= 10 or not 0 <= rec.diem_do_an <= 10:
                raise ValidationError(_('Điểm chấm phải nằm trong khoảng 0 đến 10.'))

    def _check_nguoi_cham(self, vals_list):
        if self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem'):
            return
        for vals in vals_list:
            member = self.env['quanly.hoidonggiangvien'].browse(vals.get('hoi_dong_giang_vien_id'))
            if not member.exists() or member.giang_vien_id.user_id != self.env.user:
                raise AccessError(_('Bạn chỉ được chấm phiếu của chính mình.'))

    def action_xac_nhan_diem(self):
        if any(rec.trang_thai != 'chua_cham' for rec in self):
            raise UserError(_('Phiếu đã được xác nhận.'))
        self.write({'trang_thai': 'da_cham'})

    @api.model_create_multi
    def create(self, vals_list):
        self._check_nguoi_cham(vals_list)
        for vals in vals_list:
            de_tai = self.env['quanly.detai'].browse(vals.get('de_tai_id'))
            de_tai.dot_do_an_id._check_open()
            if not self.env.su and (de_tai.hoi_dong_id.trang_thai != 'dang_cham' or de_tai.trang_thai != 'cho_bao_ve'):
                raise UserError(_('Chỉ được tạo phiếu khi hội đồng đang chấm đề tài đủ điều kiện.'))
            if de_tai.exists() and de_tai.da_khoa_diem:
                raise AccessError(_('Điểm đã khóa, không thể tạo phiếu chấm mới.'))
            if vals.get('trang_thai') == 'da_cham':
                vals['ngay_cham'] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        self.check_access('write')
        self.mapped('de_tai_id.dot_do_an_id')._check_open()
        if set(vals) & {'de_tai_id', 'hoi_dong_giang_vien_id'}:
            raise UserError(_('Phiếu đã tạo không được đổi đề tài hoặc người chấm.'))
        if any(rec.hoi_dong_id.trang_thai != 'dang_cham' and not rec.de_tai_id.da_khoa_diem for rec in self):
            raise UserError(_('Chỉ được sửa phiếu khi hội đồng đang tiến hành chấm.'))
        if not self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem'):
            if any(rec.giang_vien_id.user_id != self.env.user for rec in self):
                raise AccessError(_('Bạn chỉ được sửa phiếu chấm của chính mình.'))
            if not set(vals).issubset({'diem_bao_cao', 'diem_do_an', 'nhan_xet', 'trang_thai'}):
                raise AccessError(_('Giảng viên chỉ được sửa điểm, nhận xét và trạng thái chấm.'))
        if any(rec.de_tai_id.da_khoa_diem for rec in self):
            raise AccessError(_('Điểm đã khóa, không thể chỉnh sửa phiếu chấm.'))
        if vals.get('de_tai_id') and self.env['quanly.detai'].browse(vals['de_tai_id']).da_khoa_diem:
            raise AccessError(_('Không thể chuyển phiếu vào đề tài đã khóa điểm.'))
        if vals.get('de_tai_id'):
            self.env['quanly.detai'].browse(vals['de_tai_id']).dot_do_an_id._check_open()
        if vals.get('trang_thai') == 'da_cham':
            vals = dict(vals, ngay_cham=fields.Datetime.now())
        elif vals.get('trang_thai') == 'chua_cham':
            vals = dict(vals, ngay_cham=False)
        return super().write(vals)

    def unlink(self):
        self.mapped('de_tai_id.dot_do_an_id')._check_open()
        if any(rec.de_tai_id.da_khoa_diem for rec in self):
            raise AccessError(_('Điểm đã khóa, không thể xóa phiếu chấm.'))
        return super().unlink()

