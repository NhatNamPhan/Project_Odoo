"""Run in odoo shell against a test database. All changes roll back on exit."""
import base64
from odoo.exceptions import AccessError, UserError, ValidationError

checks = 0


def denied(error, fn):
    global checks
    try:
        with env.cr.savepoint():
            fn()
    except error:
        checks += 1
        return
    raise AssertionError('Expected rejection: ' + error.__name__)


sv = env['quanly.sinhvien'].search([('ma_sv', '=', '22115053122323')], limit=1)
gv = env['quanly.giangvien'].search([('ma_gv', '=', 'GV01')], limit=1)
member = env['quanly.giangvien'].search([('ma_gv', '=', 'GV03')], limit=1)
assert sv and gv and member
student, lecturer = sv.user_id, gv.user_id
manager = env.ref('base.user_admin')
batch = env['quanly.dotdoan'].create({'ma_dot': 'AUDIT_FULL_CYCLE', 'ten_dot': 'Audit', 'nien_khoa': '2026', 'hoc_ky': '1'})
batch = batch.with_user(manager)
denied(UserError, lambda: batch.write({'trang_thai': 'dang_bao_ve'}))
denied(AccessError, lambda: batch.with_user(student).action_mo_dang_ky())
batch.action_mo_dang_ky()
denied(UserError, lambda: batch.action_mo_dang_ky())
registration = env['quanly.dangky'].with_user(student).create({'sinh_vien_id': sv.id, 'dot_do_an_id': batch.id})
registration.with_user(manager).action_duyet()
denied(UserError, lambda: registration.with_user(manager).write({'trang_thai': 'cho_duyet'}))
topic = env['quanly.detai'].create({'ma_de_tai': 'AUDIT_FULL_CYCLE', 'ten_de_tai': 'Audit', 'dang_ky_id': registration.id, 'giang_vien_huong_dan_id': gv.id})
topic = topic.with_user(manager)
assert topic.xep_loai == 'chua_du_diem'
denied(UserError, lambda: topic.write({'da_khoa_diem': True}))
denied(UserError, lambda: topic.write({'trang_thai': 'da_bao_ve'}))
denied(AccessError, lambda: topic.with_user(student).write({'trang_thai': 'cho_xac_nhan_bao_ve'}))
batch.action_bat_dau_thuc_hien()
period = env['quanly.dotbaocao'].create({'dot_do_an_id': batch.id, 'ten_dot_bao_cao': 'Audit', 'thu_tu': 1, 'han_nop': '2026-12-01'})
report = env['quanly.baocao'].with_user(student).create({'de_tai_id': topic.id, 'dot_bao_cao_id': period.id, 'ten_tep': 'audit.txt', 'file_bao_cao': base64.b64encode(b'audit')})
denied(AccessError, lambda: report.with_user(student).action_dat())
report.with_user(lecturer).action_can_sua()
report.with_user(lecturer).action_dat()
revision = env['quanly.baocao'].with_user(student).create({
    'de_tai_id': topic.id, 'dot_bao_cao_id': period.id,
    'ten_tep': 'revision.txt', 'file_bao_cao': base64.b64encode(b'revision'), 'phien_ban': 99,
})
assert revision.phien_ban == 2
denied(UserError, lambda: topic.with_user(student).action_gui_xac_nhan_bao_ve())
revision.with_user(lecturer).action_dat()
report = revision
topic.with_user(student).action_gui_xac_nhan_bao_ve()
report.with_user(lecturer).action_can_sua()
denied(UserError, lambda: topic.with_user(lecturer).action_xac_nhan_bao_ve())
report.with_user(lecturer).action_dat()
topic.with_user(lecturer).action_tu_choi_bao_ve()
topic.with_user(lecturer).action_cho_lam_lai()
topic.with_user(student).action_gui_xac_nhan_bao_ve()
topic.with_user(lecturer).action_xac_nhan_bao_ve()
denied(UserError, lambda: report.with_user(lecturer).action_can_sua())
denied(UserError, lambda: report.with_user(manager).write({'file_bao_cao': base64.b64encode(b'overwrite')}))
denied(UserError, lambda: env['quanly.dotbaocao'].with_user(manager).create({'dot_do_an_id': batch.id, 'ten_dot_bao_cao': 'Late', 'thu_tu': 2, 'han_nop': '2026-12-10'}))
council = env['quanly.hoidong'].create({'ma_hoi_dong': 'AUDIT_FULL_CYCLE', 'ten_hoi_dong': 'Audit', 'dot_do_an_id': batch.id, 'chuyen_nganh_id': sv.chuyen_nganh_id.id, 'thoi_gian_bao_ve': '2026-12-02 01:00:00', 'dia_diem': 'Audit'})
council = council.with_user(manager)
env['quanly.hoidonggiangvien'].create({'hoi_dong_id': council.id, 'giang_vien_id': member.id, 'vai_tro': 'chu_tich'})
topic.write({'hoi_dong_id': council.id})
council.action_chot_lich()
denied(UserError, lambda: council.write({'dia_diem': 'Changed'}))
denied(UserError, lambda: env['quanly.hoidonggiangvien'].create({'hoi_dong_id': council.id, 'giang_vien_id': gv.id}))
denied(UserError, lambda: council.thanh_vien_ids.with_user(manager).unlink())
denied(UserError, lambda: council.thanh_vien_ids.with_user(manager).write({'vai_tro': 'thu_ky'}))
denied(UserError, lambda: topic.write({'hoi_dong_id': False}))
denied(UserError, lambda: council.action_bat_dau_cham())
batch.action_bat_dau_bao_ve()
council.action_bat_dau_cham()
denied(UserError, lambda: council.write({'trang_thai': 'du_thao'}))
denied(UserError, lambda: council.action_hoan_thanh())
score = topic.phieu_cham_diem_ids.with_user(member.user_id)
assert len(score) == 1
denied(ValidationError, lambda: score.write({'diem_bao_cao': 11}))
denied(AccessError, lambda: score.with_user(lecturer).write({'diem_do_an': 10}))
score.write({'diem_bao_cao': 9, 'diem_do_an': 10})
score.action_xac_nhan_diem()
assert topic.xep_loai == 'chua_du_diem'
denied(UserError, lambda: council.action_hoan_thanh())
# Explicit zero is valid and distinct from a missing grade.
topic.with_user(lecturer).action_xac_nhan_diem_gvhd()
assert topic.diem_gvhd_da_nhap
topic.with_user(lecturer).write({'diem_gvhd': 8})
assert topic.diem_tong_ket == 9.2
assert topic.xep_loai == 'xuat_sac'
council.action_hoan_thanh()
assert topic.da_khoa_diem and topic.trang_thai == 'da_bao_ve'
denied(UserError, lambda: topic.write({'da_khoa_diem': False}))
denied(AccessError, lambda: score.write({'diem_do_an': 8}))
denied(AccessError, lambda: topic.with_user(lecturer).write({'diem_gvhd': 9}))
denied(UserError, lambda: batch.write({'trong_so_gvhd': 20, 'trong_so_bao_cao': 30}))
denied(UserError, lambda: batch.action_ket_thuc())
topic.with_user(student).write({'link_github': 'https://example.com/source'})
env['quanly.hinhanhdetai'].with_user(student).create({'de_tai_id': topic.id, 'ten_hinh': 'Audit', 'url': 'https://example.com/demo.png'})
topic.action_luu_chieu()
assert topic.trang_thai == 'da_luu_chieu'
denied(UserError, lambda: topic.hinh_anh_ids.with_user(student).unlink())
batch.action_ket_thuc()
denied(UserError, lambda: topic.write({'link_demo': 'https://example.com/changed'}))
denied(UserError, lambda: env['quanly.dotbaocao'].create({'dot_do_an_id': batch.id, 'ten_dot_bao_cao': 'Closed', 'thu_tu': 2, 'han_nop': '2026-12-10'}))
denied(UserError, lambda: score.write({'diem_do_an': 8}))
denied(UserError, lambda: registration.with_user(manager).write({'trang_thai': 'tu_choi'}))
denied(UserError, lambda: council.write({'dia_diem': 'Closed'}))
denied(UserError, lambda: env['quanly.dangky'].with_user(student).create({'sinh_vien_id': sv.id, 'dot_do_an_id': batch.id}))
denied(UserError, lambda: batch.write({'trang_thai': 'chuan_bi'}))
denied(UserError, lambda: batch.unlink())

for user in (env.user, student, lecturer, member.user_id):
    views = env['ir.ui.view'].search([('model', '=like', 'quanly.%'), ('type', 'in', ['list', 'form', 'calendar'])])
    for view in views:
        env[view.model].with_user(user).get_view(view.id, view.type)
print(f'PASS: full lifecycle, {checks} rejected invalid operations, grades, archival, and all registered views for four roles')
