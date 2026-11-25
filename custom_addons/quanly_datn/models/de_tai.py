# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class DeTai(models.Model):
    _inherit = 'quanly.ui.permissions'
    _name = 'quanly.detai'
    _description = 'Đề tài tốt nghiệp chính thức'
    _rec_name = 'ten_de_tai'

    ma_de_tai = fields.Char(string='Mã đề tài', required=True, copy=False)
    ten_de_tai = fields.Char(string='Tên đề tài tốt nghiệp', required=True)
    mo_ta = fields.Text(string='Mô tả chi tiết nội dung')

    dang_ky_id = fields.Many2one('quanly.dangky', string='Sinh viên thực hiện', required=True, ondelete='restrict')
    sinh_vien_id = fields.Many2one(
        'quanly.sinhvien', 
        string='Sinh viên', 
        related='dang_ky_id.sinh_vien_id', 
        store=True, 
        readonly=True
    )
    dot_do_an_id = fields.Many2one(
        'quanly.dotdoan', 
        string='Đợt làm đồ án', 
        related='dang_ky_id.dot_do_an_id', 
        store=True, 
        readonly=True
    )

    ngan_hang_de_tai_id = fields.Many2one('quanly.nganhangdetai', string='Nguồn từ Ngân hàng đề tài')
    giang_vien_huong_dan_id = fields.Many2one('quanly.giangvien', string='Giảng viên hướng dẫn', required=True)
    hoi_dong_id = fields.Many2one('quanly.hoidong', string='Hội đồng bảo vệ', ondelete='set null')

    link_github = fields.Char(string='Link Github / Source Code')
    link_demo = fields.Char(string='Link Demo sản phẩm')

    gvhd_da_duyet = fields.Boolean(string='GVHD đồng ý cho bảo vệ', default=False)
    nhan_xet_tong_ket = fields.Text(string='Nhận xét tổng kết của GVHD')

    diem_gvhd = fields.Float(string='Điểm GVHD (thang 10)', digits=(4, 2))
    diem_gvhd_da_nhap = fields.Boolean(string='Đã nhập điểm GVHD', default=False, readonly=True, copy=False)
    diem_bao_cao_tb = fields.Float(string='Điểm Báo cáo TB', digits=(4, 2), compute='_compute_diem_hoi_dong', store=True)
    diem_do_an_tb = fields.Float(string='Điểm Đồ án TB Hội đồng', digits=(4, 2), compute='_compute_diem_hoi_dong', store=True)
    diem_tong_ket = fields.Float(string='Điểm tổng kết cuối cùng', digits=(4, 2), compute='_compute_diem_tong_ket', store=True)
    xep_loai = fields.Selection([
        ('chua_du_diem', 'Chưa đủ điểm'),
        ('xuat_sac', 'Xuất sắc'),
        ('gioi', 'Giỏi'),
        ('kha', 'Khá'),
        ('trung_binh', 'Trung bình'),
        ('khong_dat', 'Không đạt')
    ], string='Xếp loại', compute='_compute_diem_tong_ket', store=True)

    da_khoa_diem = fields.Boolean(string='Đã khóa điểm', default=False)
    trang_thai = fields.Selection([
        ('dang_thuc_hien', 'Đang thực hiện'),
        ('cho_xac_nhan_bao_ve', 'Chờ GVHD xác nhận bảo vệ'),
        ('cho_bao_ve', 'Đủ điều kiện chờ bảo vệ'),
        ('khong_duoc_bao_ve', 'Không được bảo vệ'),
        ('da_bao_ve', 'Đã bảo vệ xong'),
        ('da_luu_chieu', 'Đã nộp lưu chiểu')
    ], string='Trạng thái đề tài', default='dang_thuc_hien')

    bao_cao_ids = fields.One2many('quanly.baocao', 'de_tai_id', string='Danh sách nộp báo cáo')
    hinh_anh_ids = fields.One2many('quanly.hinhanhdetai', 'de_tai_id', string='Thư viện ảnh sản phẩm (Showcase)')
    phieu_cham_diem_ids = fields.One2many('quanly.phieuchamdiem', 'de_tai_id', string='Phiếu chấm điểm hội đồng')

    _sql_constraints = [
        ('ma_de_tai_uniq', 'unique(ma_de_tai)', 'Mã đề tài đã tồn tại!'),
        ('dang_ky_uniq', 'unique(dang_ky_id)', 'Mỗi lượt đăng ký của sinh viên chỉ được gán đúng 1 đề tài!')
    ]

    @api.constrains('dang_ky_id', 'ngan_hang_de_tai_id', 'hoi_dong_id')
    def _check_phan_cong(self):
        for rec in self:
            if rec.dang_ky_id.trang_thai != 'da_duyet':
                raise ValidationError(_('Chỉ được giao đề tài cho đăng ký đã duyệt.'))
            if rec.ngan_hang_de_tai_id and (
                rec.ngan_hang_de_tai_id.dot_do_an_id != rec.dot_do_an_id
                or rec.ngan_hang_de_tai_id.trang_thai not in ('da_duyet', 'da_chon')
            ):
                raise ValidationError(_('Đề tài đề xuất phải được duyệt và thuộc cùng đợt đồ án.'))
            if rec.hoi_dong_id and (
                rec.hoi_dong_id.dot_do_an_id != rec.dot_do_an_id
                or rec.hoi_dong_id.chuyen_nganh_id != rec.sinh_vien_id.chuyen_nganh_id
            ):
                raise ValidationError(_('Hội đồng phải thuộc cùng đợt đồ án và chuyên ngành của sinh viên.'))
            if rec.phieu_cham_diem_ids and any(
                phieu.hoi_dong_giang_vien_id.hoi_dong_id != rec.hoi_dong_id
                for phieu in rec.phieu_cham_diem_ids
            ):
                raise ValidationError(_('Không thể đổi hội đồng khi đã có phiếu chấm của hội đồng khác.'))

    @api.constrains('diem_gvhd')
    def _check_diem_gvhd(self):
        for rec in self:
            if not 0 <= rec.diem_gvhd <= 10:
                raise ValidationError(_('Điểm GVHD phải nằm trong khoảng 0 đến 10.'))

    @api.depends('phieu_cham_diem_ids.trang_thai', 'phieu_cham_diem_ids.diem_bao_cao', 'phieu_cham_diem_ids.diem_do_an')
    def _compute_diem_hoi_dong(self):
        for rec in self:
            phieu = rec.phieu_cham_diem_ids.filtered(lambda p: p.trang_thai == 'da_cham')
            rec.diem_bao_cao_tb = round(sum(phieu.mapped('diem_bao_cao')) / len(phieu), 2) if phieu else 0.0
            rec.diem_do_an_tb = round(sum(phieu.mapped('diem_do_an')) / len(phieu), 2) if phieu else 0.0

    def _is_bcn(self):
        return self.env.user.has_group('quanly_datn.group_datn_ban_chu_nhiem')

    def _current_sinh_vien(self):
        return self.env['quanly.sinhvien'].search([('user_id', '=', self.env.user.id)], limit=1)

    def _is_gvhd(self):
        return all(rec.giang_vien_huong_dan_id.user_id == self.env.user for rec in self)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            registration = self.env['quanly.dangky'].browse(vals.get('dang_ky_id'))
            registration.dot_do_an_id._check_open()
            if not self.env.su and vals.get('hoi_dong_id'):
                council = self.env['quanly.hoidong'].browse(vals['hoi_dong_id'])
                if council.trang_thai != 'du_thao':
                    raise UserError(_('Chỉ được giao đề tài mới vào hội đồng dự thảo.'))
            if not self.env.su and vals.get('trang_thai', 'dang_thuc_hien') != 'dang_thuc_hien':
                raise UserError(_('Đề tài mới phải bắt đầu ở trạng thái đang thực hiện.'))
            vals['diem_gvhd_da_nhap'] = bool(vals.get('diem_gvhd'))
        return super().create(vals_list)

    def _check_bao_cao_dat(self):
        for rec in self:
            periods = self.env['quanly.dotbaocao'].sudo().search([('dot_do_an_id', '=', rec.dot_do_an_id.id)])
            if not periods:
                raise UserError(_('Cần cấu hình và duyệt đủ báo cáo trước khi bảo vệ.'))
            for period in periods:
                latest = self.env['quanly.baocao'].sudo().search([
                    ('de_tai_id', '=', rec.id), ('dot_bao_cao_id', '=', period.id)
                ], order='ngay_nop desc, id desc', limit=1)
                if not latest or latest.trang_thai != 'dat':
                    raise UserError(_('Bản báo cáo mới nhất của tất cả các đợt phải đạt yêu cầu.'))

    def _check_du_diem(self):
        for rec in self:
            members = rec.hoi_dong_id.thanh_vien_ids
            graded = rec.sudo().phieu_cham_diem_ids.filtered(lambda p: p.trang_thai == 'da_cham').mapped('hoi_dong_giang_vien_id')
            if not rec.diem_gvhd_da_nhap or not members or members - graded:
                raise UserError(_('Cần nhập điểm GVHD và đủ phiếu đã chấm của mọi thành viên.'))

    def _validate_transition(self, target):
        self.mapped('dot_do_an_id')._check_open()
        allowed = {
            'dang_thuc_hien': ('cho_xac_nhan_bao_ve',),
            'cho_xac_nhan_bao_ve': ('cho_bao_ve', 'khong_duoc_bao_ve'),
            'khong_duoc_bao_ve': ('dang_thuc_hien',),
            'cho_bao_ve': ('da_bao_ve',),
            'da_bao_ve': ('da_luu_chieu',),
        }
        for rec in self:
            if target == rec.trang_thai:
                continue
            if target not in allowed.get(rec.trang_thai, ()):
                raise UserError(_('Không được bỏ qua hoặc quay ngược trạng thái đề tài.'))
            if target in ('cho_xac_nhan_bao_ve', 'cho_bao_ve', 'da_bao_ve'):
                rec._check_bao_cao_dat()
            if target == 'da_bao_ve':
                if not rec.hoi_dong_id or rec.hoi_dong_id.trang_thai != 'dang_cham' or not rec.gvhd_da_duyet:
                    raise UserError(_('Chỉ hoàn tất bảo vệ khi hội đồng đang chấm và GVHD đã đồng ý.'))
                rec._check_du_diem()
            if target == 'da_luu_chieu' and (not rec.hinh_anh_ids or not rec.link_github):
                raise UserError(_('Cần nộp ảnh sản phẩm và liên kết mã nguồn trước khi lưu chiểu.'))

    def write(self, vals):
        self.check_access('write')
        if 'trang_thai' in vals and not self._is_bcn():
            raise AccessError(_('Cần sử dụng nút nghiệp vụ để chuyển trạng thái đề tài.'))
        self.mapped('dot_do_an_id')._check_open()
        if vals.get('da_khoa_diem'):
            self._check_du_diem()
        if vals.get('da_khoa_diem') is False and any(rec.hoi_dong_id.trang_thai == 'hoan_thanh' for rec in self):
            raise UserError(_('Hội đồng đã hoàn thành, không thể mở khóa điểm trực tiếp.'))
        if 'diem_gvhd_da_nhap' in vals:
            raise AccessError(_('Trạng thái nhập điểm do hệ thống quản lý.'))
        if set(vals) & {'dang_ky_id', 'giang_vien_huong_dan_id'}:
            if any(rec.trang_thai != 'dang_thuc_hien' or rec.hoi_dong_id or rec.bao_cao_ids for rec in self):
                raise UserError(_('Không thể đổi đăng ký/GVHD sau khi đã có báo cáo hoặc chuyển sang bảo vệ.'))
            if vals.get('dang_ky_id'):
                self.env['quanly.dangky'].browse(vals['dang_ky_id']).dot_do_an_id._check_open()
        if any(rec.trang_thai == 'da_luu_chieu' for rec in self):
            raise UserError(_('Đề tài đã lưu chiểu, không được thay đổi nội dung đã nộp.'))
        if 'hoi_dong_id' in vals:
            new_council = self.env['quanly.hoidong'].browse(vals['hoi_dong_id'])
            if any(rec.hoi_dong_id and rec.hoi_dong_id.trang_thai != 'du_thao' for rec in self) or (new_council and new_council.trang_thai != 'du_thao'):
                raise UserError(_('Chỉ được phân công đề tài vào hội đồng còn dự thảo.'))
        if 'trang_thai' in vals:
            self._validate_transition(vals['trang_thai'])
        if 'gvhd_da_duyet' in vals and 'trang_thai' not in vals:
            raise AccessError(_('Cần xác nhận bảo vệ bằng thao tác chuyển trạng thái.'))
        if set(vals) & {'diem_gvhd', 'diem_bao_cao_tb', 'diem_do_an_tb', 'hoi_dong_id', 'dang_ky_id'} and any(
            rec.da_khoa_diem for rec in self
        ):
            raise AccessError(_('Điểm đã khóa, cần mở khóa trước khi thay đổi dữ liệu chấm.'))
        if self._is_bcn():
            values = dict(vals)
            if 'diem_gvhd' in vals:
                values['diem_gvhd_da_nhap'] = True
            if 'trang_thai' in vals:
                values['gvhd_da_duyet'] = vals['trang_thai'] in ('cho_bao_ve', 'da_bao_ve', 'da_luu_chieu')
            return super().write(values)

        changed_fields = set(vals)
        if self.env.user.has_group('quanly_datn.group_datn_sinh_vien'):
            sinh_vien = self._current_sinh_vien()
            if not sinh_vien or any(rec.sinh_vien_id != sinh_vien for rec in self):
                raise AccessError(_('Bạn chỉ được cập nhật đề tài của chính mình.'))
            allowed_fields = {'mo_ta', 'link_github', 'link_demo'}
            if not changed_fields.issubset(allowed_fields):
                raise AccessError(_('Sinh viên chỉ được cập nhật mô tả và các liên kết của đề tài.'))
            return super().write(vals)

        if self.env.user.has_group('quanly_datn.group_datn_giang_vien'):
            if not self._is_gvhd():
                raise AccessError(_('Chỉ giảng viên hướng dẫn của đề tài mới được thực hiện thao tác này.'))
            allowed_fields = {'diem_gvhd', 'nhan_xet_tong_ket'}
            if not changed_fields.issubset(allowed_fields):
                raise AccessError(_('Giảng viên chỉ được cập nhật nhận xét, điểm và xác nhận bảo vệ.'))
            if 'diem_gvhd' in vals and any(rec.da_khoa_diem for rec in self):
                raise AccessError(_('Điểm đã khóa, không thể chỉnh sửa.'))
            values = dict(vals)
            if 'diem_gvhd' in vals:
                values['diem_gvhd_da_nhap'] = True
            return super().write(values)

        raise AccessError(_('Bạn không có quyền cập nhật đề tài này.'))

    def unlink(self):
        self.mapped('dot_do_an_id')._check_open()
        if any(rec.trang_thai != 'dang_thuc_hien' or rec.bao_cao_ids or rec.phieu_cham_diem_ids or rec.hoi_dong_id for rec in self):
            raise UserError(_('Không thể xóa đề tài đã phát sinh báo cáo hoặc phân công bảo vệ.'))
        return super().unlink()

    def action_gui_xac_nhan_bao_ve(self):
        self.ensure_one()
        sinh_vien = self._current_sinh_vien()
        if not sinh_vien or self.sinh_vien_id != sinh_vien:
            raise AccessError(_('Chỉ sinh viên thực hiện đề tài mới được gửi yêu cầu bảo vệ.'))
        if self.trang_thai != 'dang_thuc_hien':
            raise UserError(_('Đề tài không ở trạng thái có thể gửi yêu cầu bảo vệ.'))

        self._validate_transition('cho_xac_nhan_bao_ve')
        super().write({'trang_thai': 'cho_xac_nhan_bao_ve'})

    def action_xac_nhan_bao_ve(self):
        if not self._is_gvhd():
            raise AccessError(_('Chỉ giảng viên hướng dẫn của đề tài mới được xác nhận bảo vệ.'))
        if any(rec.trang_thai != 'cho_xac_nhan_bao_ve' for rec in self):
            raise UserError(_('Đề tài cần ở trạng thái chờ xác nhận bảo vệ.'))
        self._validate_transition('cho_bao_ve')
        super().write({'gvhd_da_duyet': True, 'trang_thai': 'cho_bao_ve'})

    def action_tu_choi_bao_ve(self):
        if not self._is_gvhd():
            raise AccessError(_('Chỉ giảng viên hướng dẫn của đề tài mới được từ chối bảo vệ.'))
        if any(rec.trang_thai != 'cho_xac_nhan_bao_ve' for rec in self):
            raise UserError(_('Đề tài cần ở trạng thái chờ xác nhận bảo vệ.'))
        self._validate_transition('khong_duoc_bao_ve')
        super().write({'gvhd_da_duyet': False, 'trang_thai': 'khong_duoc_bao_ve'})

    def action_cho_lam_lai(self):
        if not self._is_gvhd() and not self._is_bcn():
            raise AccessError(_('Chỉ GVHD hoặc BCN được cho phép bổ sung báo cáo.'))
        if any(rec.trang_thai != 'khong_duoc_bao_ve' for rec in self):
            raise UserError(_('Chỉ mở lại đề tài bị từ chối bảo vệ.'))
        self._validate_transition('dang_thuc_hien')
        super().write({'trang_thai': 'dang_thuc_hien', 'gvhd_da_duyet': False})

    def action_xac_nhan_diem_gvhd(self):
        if not self._is_gvhd() and not self._is_bcn():
            raise AccessError(_('Chỉ GVHD của đề tài hoặc BCN được xác nhận điểm hướng dẫn.'))
        for rec in self:
            # Explicit confirmation makes a legitimate zero distinguishable
            # from the default zero on a newly assigned thesis.
            rec.write({'diem_gvhd': rec.diem_gvhd})

    def action_luu_chieu(self):
        if not self._is_bcn():
            raise AccessError(_('Chỉ BCN xác nhận lưu chiểu.'))
        if any(rec.trang_thai != 'da_bao_ve' or not rec.hinh_anh_ids or not rec.link_github for rec in self):
            raise UserError(_('Cần bảo vệ xong, nộp liên kết mã nguồn và ảnh sản phẩm trước khi lưu chiểu.'))
        self.write({'trang_thai': 'da_luu_chieu'})

    @api.depends('diem_gvhd', 'diem_gvhd_da_nhap', 'diem_bao_cao_tb', 'diem_do_an_tb', 'dot_do_an_id.trong_so_gvhd', 'dot_do_an_id.trong_so_bao_cao', 'dot_do_an_id.trong_so_do_an', 'phieu_cham_diem_ids.trang_thai', 'phieu_cham_diem_ids.hoi_dong_giang_vien_id', 'hoi_dong_id.thanh_vien_ids')
    def _compute_diem_tong_ket(self):
        for rec in self:
            w_gvhd = rec.dot_do_an_id.trong_so_gvhd / 100.0
            w_bc = rec.dot_do_an_id.trong_so_bao_cao / 100.0
            w_da = rec.dot_do_an_id.trong_so_do_an / 100.0

            total = (rec.diem_gvhd * w_gvhd) + (rec.diem_bao_cao_tb * w_bc) + (rec.diem_do_an_tb * w_da)
            rec.diem_tong_ket = round(total, 2)

            members = rec.hoi_dong_id.thanh_vien_ids
            graded = rec.phieu_cham_diem_ids.filtered(lambda p: p.trang_thai == 'da_cham').mapped('hoi_dong_giang_vien_id')
            if not rec.diem_gvhd_da_nhap or not members or members - graded:
                rec.xep_loai = 'chua_du_diem'
            elif rec.diem_tong_ket >= 9.0:
                rec.xep_loai = 'xuat_sac'
            elif rec.diem_tong_ket >= 8.0:
                rec.xep_loai = 'gioi'
            elif rec.diem_tong_ket >= 6.5:
                rec.xep_loai = 'kha'
            elif rec.diem_tong_ket >= 5.0:
                rec.xep_loai = 'trung_binh'
            else:
                rec.xep_loai = 'khong_dat'


class HinhAnhDeTai(models.Model):
    _name = 'quanly.hinhanhdetai'
    _description = 'Hình ảnh demo / Showcase sản phẩm đề tài'
    _rec_name = 'ten_hinh'

    de_tai_id = fields.Many2one('quanly.detai', string='Đề tài', required=True, ondelete='cascade')
    ten_hinh = fields.Char(string='Tiêu đề hình ảnh', required=True)
    hinh_anh = fields.Image(string='File hình ảnh', max_width=1920, max_height=1080)
    url = fields.Char(string='URL đường dẫn ảnh')
    mo_ta = fields.Text(string='Mô tả ảnh')

    def _check_editable(self):
        self.mapped('de_tai_id.dot_do_an_id')._check_open()
        if any(rec.de_tai_id.trang_thai == 'da_luu_chieu' for rec in self):
            raise UserError(_('Sản phẩm đã lưu chiểu, không thể thay đổi hình ảnh.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            topic = self.env['quanly.detai'].browse(vals.get('de_tai_id'))
            topic.dot_do_an_id._check_open()
            if topic.trang_thai == 'da_luu_chieu':
                raise UserError(_('Không thể thêm ảnh vào đề tài đã lưu chiểu.'))
        return super().create(vals_list)

    def write(self, vals):
        self._check_editable()
        if vals.get('de_tai_id'):
            target = self.env['quanly.detai'].browse(vals['de_tai_id'])
            target.dot_do_an_id._check_open()
            if target.trang_thai == 'da_luu_chieu':
                raise UserError(_('Không thể chuyển ảnh vào đề tài đã lưu chiểu.'))
        return super().write(vals)

    def unlink(self):
        self._check_editable()
        return super().unlink()

