# -*- coding: utf-8 -*-
from odoo import models, fields, api

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

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.giang_vien_id.ho_ten or ''} ({dict(self._fields['vai_tro'].selection).get(rec.vai_tro, '')})"


class PhieuChamDiem(models.Model):
    _name = 'quanly.phieuchamdiem'
    _description = 'Phiếu chấm điểm của thành viên Hội đồng'
    _rec_name = 'display_name'

    de_tai_id = fields.Many2one('quanly.detai', string='Đề tài chấm điểm', required=True, ondelete='cascade')
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
    ngay_cham = fields.Datetime(string='Thời điểm chấm', default=fields.Datetime.now)

    display_name = fields.Char(string='Tên hiển thị', compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('detai_cbcham_uniq', 'unique(de_tai_id, hoi_dong_giang_vien_id)', 'Cán bộ này đã có phiếu chấm cho đề tài rồi!')
    ]

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"Phiếu chấm: {rec.de_tai_id.ten_de_tai or ''} - {rec.giang_vien_id.ho_ten or ''}"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_diem_tb_detai()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._update_diem_tb_detai()
        return res

    def _update_diem_tb_detai(self):
        for rec in self:
            if rec.de_tai_id:
                phieu_list = self.search([
                    ('de_tai_id', '=', rec.de_tai_id.id),
                    ('trang_thai', '=', 'da_cham')
                ])
                if phieu_list:
                    rec.de_tai_id.diem_bao_cao_tb = round(sum(p.diem_bao_cao for p in phieu_list) / len(phieu_list), 2)
                    rec.de_tai_id.diem_do_an_tb = round(sum(p.diem_do_an for p in phieu_list) / len(phieu_list), 2)
