"""Regression checks for the sample dataset; run with ``odoo shell``."""

from odoo.exceptions import AccessError, UserError, ValidationError


def rejects(error_type, action):
    try:
        with env.cr.savepoint():
            action()
    except error_type:
        return
    raise AssertionError(f'Expected {error_type.__name__}')


Topic = env['quanly.detai'].sudo()
topic = Topic.search([('ma_de_tai', '=', 'DT2026_01')], limit=1)
student = topic.sinh_vien_id.user_id
supervisor = topic.giang_vien_huong_dan_id.user_id
other_lecturer = env['quanly.giangvien'].sudo().search([('ma_gv', '=', 'GV02')], limit=1).user_id
assert topic and student and supervisor
assert topic.diem_bao_cao_tb == 9.25, topic.diem_bao_cao_tb
assert topic.diem_do_an_tb == 9.38, topic.diem_do_an_tb
assert topic.diem_tong_ket == 9.39, topic.diem_tong_ket

rejects(AccessError, lambda: topic.with_user(student).write({'trang_thai': 'cho_xac_nhan_bao_ve'}))
rejects(AccessError, lambda: topic.sinh_vien_id.with_user(student).write({'user_id': other_lecturer.id}))
rejects(AccessError, lambda: topic.with_user(other_lecturer).write({'diem_gvhd': 10}))
rejects(ValidationError, lambda: topic.write({'diem_gvhd': 11}))
rejects(ValidationError, lambda: topic.dot_do_an_id.write({'trong_so_gvhd': 0}))
rejects(UserError, lambda: topic.write({'hoi_dong_id': False}))

if topic.dot_do_an_id.trang_thai == 'dang_thuc_hien':
    topic.dot_do_an_id.action_bat_dau_bao_ve()
if topic.hoi_dong_id.trang_thai == 'da_chot_lich':
    topic.hoi_dong_id.action_bat_dau_cham()

phieu = topic.phieu_cham_diem_ids[:1]
phieu.write({'trang_thai': 'chua_cham'})
assert topic.diem_bao_cao_tb != 9.25
phieu.write({'trang_thai': 'da_cham'})
assert topic.diem_bao_cao_tb == 9.25
topic.write({'da_khoa_diem': True})
rejects(AccessError, lambda: phieu.write({'diem_bao_cao': 8}))
rejects(AccessError, lambda: topic.with_user(supervisor).write({'diem_gvhd': 8}))
topic.write({'da_khoa_diem': False})

report = topic.bao_cao_ids[:1]
rejects(AccessError, lambda: report.with_user(student).write({'trang_thai': 'dat'}))
rejects(AccessError, lambda: report.with_user(other_lecturer).write({'trang_thai': 'dat'}))

missing = Topic.search([('ma_de_tai', '=', 'DT2026_02')], limit=1)
rejects(UserError, lambda: missing.with_user(missing.sinh_vien_id.user_id).action_gui_xac_nhan_bao_ve())

recipient = env['quanly.nguoinhanthongbao'].sudo().search([
    ('thong_bao_id.dot_do_an_id', '=', topic.dot_do_an_id.id),
    ('nguoi_nhan_id', '=', student.id),
], limit=1)
assert recipient
recipient.with_user(student).action_danh_dau_da_doc()
assert recipient.da_doc and recipient.ngay_doc

message = env['quanly.tinnhan'].with_user(student).create({
    'de_tai_id': topic.id,
    'noi_dung': 'Kiểm tra quyền người gửi',
    'nguoi_gui_id': other_lecturer.id,
})
assert message.nguoi_gui_id == student
rejects(AccessError, lambda: message.with_user(other_lecturer).write({'noi_dung': 'Giả mạo'}))
rejects(AccessError, lambda: message.with_user(student).action_danh_dau_da_doc())
message.with_user(supervisor).action_danh_dau_da_doc()
assert message.da_doc

print('Workflow checks passed: grades, locks, approvals, reports, notifications and messages')
