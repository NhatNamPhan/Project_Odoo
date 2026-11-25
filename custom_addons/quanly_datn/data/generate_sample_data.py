# -*- coding: utf-8 -*-
import base64
from datetime import datetime, date, timedelta

print("Bắt đầu cập nhật lại dữ liệu mẫu với bảng mã UTF-8 chuẩn...")

dummy_file = base64.b64encode(b"Tai lieu bao cao tien do do an tot nghiep Odoo 18").decode('utf-8')

# 1. Nhóm quyền
group_sv = env.ref('quanly_datn.group_datn_sinh_vien')
group_gv = env.ref('quanly_datn.group_datn_giang_vien')
group_bcn = env.ref('quanly_datn.group_datn_ban_chu_nhiem')
group_internal = env.ref('base.group_user')

# 2. Cập nhật Chuyên ngành
ChuyenNganh = env['quanly.chuyennganh'].sudo()
cns = [
    ('KTPM', 'Kỹ thuật phần mềm', 'Đào tạo kỹ sư phần mềm, phát triển ứng dụng web/mobile và hệ thống thông tin.'),
    ('KHMT', 'Khoa học máy tính & Trí tuệ nhân tạo', 'Nghiên cứu về giải thuật, mô hình học máy (Machine Learning) và thị giác máy tính.'),
    ('MMT', 'Mạng máy tính & An toàn thông tin', 'Quản trị hạ tầng mạng doanh nghiệp, điện toán đám mây và phòng chống tấn công mạng.'),
]
cn_map = {}
for ma, ten, mo_ta in cns:
    rec = ChuyenNganh.search([('ma_chuyen_nganh', '=', ma)], limit=1)
    vals = {'ma_chuyen_nganh': ma, 'ten_chuyen_nganh': ten, 'mo_ta': mo_ta}
    if rec:
        rec.write(vals)
    else:
        rec = ChuyenNganh.create(vals)
    cn_map[ma] = rec
print(f"- Đã chuẩn hóa {len(cn_map)} chuyên ngành.")

# 3. Cập nhật Lớp sinh hoạt
Lop = env['quanly.lopsinhhoat'].sudo()
lops = [
    ('22T1', 'Lớp 22T1 - KTPM', cn_map['KTPM'].id, '2022 - 2026'),
    ('22T2', 'Lớp 22T2 - KTPM', cn_map['KTPM'].id, '2022 - 2026'),
    ('22T3', 'Lớp 22T3 - KTPM', cn_map['KTPM'].id, '2022 - 2026'),
    ('22AI', 'Lớp 22AI - Trí tuệ nhân tạo', cn_map['KHMT'].id, '2022 - 2026'),
    ('22ANM', 'Lớp 22ANM - An ninh mạng', cn_map['MMT'].id, '2022 - 2026'),
]
lop_map = {}
for ma, ten, cn_id, nien_khoa in lops:
    rec = Lop.search([('ma_lop', '=', ma)], limit=1)
    vals = {'ma_lop': ma, 'ten_lop': ten, 'chuyen_nganh_id': cn_id, 'nien_khoa': nien_khoa}
    if rec:
        rec.write(vals)
    else:
        rec = Lop.create(vals)
    lop_map[ma] = rec
print(f"- Đã chuẩn hóa {len(lop_map)} lớp sinh hoạt.")

# Helper cập nhật hoặc tạo user
User = env['res.users'].sudo()
def upsert_user(name, login, password, groups):
    u = User.search([('login', '=', login)], limit=1)
    if u:
        u.write({
            'name': name,
            'groups_id': [(4, g.id) for g in groups]
        })
    else:
        u = User.create({
            'name': name,
            'login': login,
            'password': password,
            'groups_id': [(6, 0, [g.id for g in groups])],
        })
    return u

# 4. Cập nhật Giảng viên
GiangVien = env['quanly.giangvien'].sudo()
gvs = [
    ('haquyen@ute.udn.vn', 'ThS. Nguyễn Thị Hà Quyên', 'GV01', '0905111222', cn_map['KTPM'].id, 'thac_si', 8),
    ('tranvana@ute.udn.vn', 'TS. Trần Văn An', 'GV02', '0905222333', cn_map['KTPM'].id, 'tien_si', 6),
    ('levanb@ute.udn.vn', 'PGS.TS. Lê Văn Bình', 'GV03', '0905333444', cn_map['KHMT'].id, 'pho_giao_su', 10),
    ('phamthic@ute.udn.vn', 'ThS. Phạm Thị Cúc', 'GV04', '0905444555', cn_map['MMT'].id, 'thac_si', 5),
    ('hoangd@ute.udn.vn', 'TS. Hoàng Minh Dũng', 'GV05', '0905555666', cn_map['KTPM'].id, 'tien_si', 6),
]
gv_map = {}
for email, name, ma, sdt, cn_id, hoc_vi, han_muc in gvs:
    u = upsert_user(name, email, '123456', [group_gv, group_internal])
    rec = GiangVien.search([('ma_gv', '=', ma)], limit=1)
    vals = {
        'user_id': u.id,
        'ma_gv': ma,
        'ho_ten': name,
        'email': email,
        'sdt': sdt,
        'chuyen_nganh_id': cn_id,
        'hoc_ham_hoc_vi': hoc_vi,
        'han_muc_huong_dan': han_muc,
    }
    if rec:
        rec.write(vals)
    else:
        rec = GiangVien.create(vals)
    gv_map[ma] = rec
print(f"- Đã chuẩn hóa {len(gv_map)} giảng viên.")

# 5. Cập nhật Sinh viên
SinhVien = env['quanly.sinhvien'].sudo()
svs = [
    ('nhatnam@sv.ute.udn.vn', 'Phan Hồ Nhật Nam', '22115053122323', '0905123456', '22T3'),
    ('quanghuy@sv.ute.udn.vn', 'Nguyễn Quang Huy', '22115053122301', '0905234567', '22T1'),
    ('thuha@sv.ute.udn.vn', 'Trần Thị Thu Hà', '22115053122302', '0905345678', '22T2'),
    ('minhtuan@sv.ute.udn.vn', 'Lê Minh Tuấn', '22115053122303', '0905456789', '22AI'),
    ('hoangviet@sv.ute.udn.vn', 'Đặng Hoàng Việt', '22115053122304', '0905567890', '22ANM'),
]
sv_map = {}
for email, name, mssv, sdt, ma_lop in svs:
    u = upsert_user(name, email, '123456', [group_sv, group_internal])
    rec = SinhVien.search([('ma_sv', '=', mssv)], limit=1)
    vals = {
        'user_id': u.id,
        'ma_sv': mssv,
        'ho_ten': name,
        'email': email,
        'sdt': sdt,
        'lop_sinh_hoat_id': lop_map[ma_lop].id,
        'trang_thai': 'dang_hoc',
    }
    if rec:
        rec.write(vals)
    else:
        rec = SinhVien.create(vals)
    sv_map[mssv] = rec
print(f"- Đã chuẩn hóa {len(sv_map)} sinh viên.")

# 6. Cập nhật Đợt làm đồ án
DotDoAn = env['quanly.dotdoan'].sudo()
dot = DotDoAn.search([('ma_dot', '=', 'DATN_2026_HK2')], limit=1)
dot_vals = {
    'ma_dot': 'DATN_2026_HK2',
    'ten_dot': 'Đợt bảo vệ ĐATN Học kỳ 2 (2025 - 2026)',
    'nien_khoa': '2025 - 2026',
    'hoc_ky': '2',
    'ma_hoc_phan': '1022133',
    'ten_hoc_phan': 'Đồ án tốt nghiệp Công nghệ thông tin',
    'ngay_bat_dau': date(2026, 2, 15),
    'ngay_bat_dau_bao_ve': date(2026, 6, 20),
    'ngay_ket_thuc_bao_ve': date(2026, 6, 25),
    'trong_so_gvhd': 30.0,
    'trong_so_bao_cao': 20.0,
    'trong_so_do_an': 50.0,
    'trang_thai': 'dang_thuc_hien',
}
if dot:
    dot.write(dot_vals)
else:
    dot = DotDoAn.create(dot_vals)
print(f"- Đã chuẩn hóa Đợt đồ án: {dot.ten_dot}")

# 7. Cập nhật Đăng ký tham gia đợt
DangKy = env['quanly.dangky'].sudo()
dangky_map = {}
for mssv, sv in sv_map.items():
    dk = DangKy.search([('sinh_vien_id', '=', sv.id), ('dot_do_an_id', '=', dot.id)], limit=1)
    dk_vals = {
        'sinh_vien_id': sv.id,
        'dot_do_an_id': dot.id,
        'trang_thai': 'da_duyet',
        'ngay_dang_ky': date(2026, 2, 16),
    }
    if dk:
        dk.write(dk_vals)
    else:
        dk = DangKy.create(dk_vals)
    dk._compute_display_name()
    dangky_map[mssv] = dk
print(f"- Đã chuẩn hóa {len(dangky_map)} đăng ký đợt.")

# 8. Cập nhật Ngân hàng đề tài
NganHang = env['quanly.nganhangdetai'].sudo()
de_xuat_list = [
    (
        'Xây dựng hệ thống quản lý đồ án tốt nghiệp cho sinh viên Khoa Công nghệ số',
        dot.id, cn_map['KTPM'].id, 'gv_de_xuat', gv_map['GV01'].id, None,
        'Ứng dụng Odoo ERP 18, kiến trúc OWL Framework, quản lý toàn diện quy trình giao đề tài, nộp báo cáo, chấm điểm hội đồng.',
        'da_chon'
    ),
    (
        'Xây dựng ứng dụng đặt lịch khám bệnh trực tuyến đa nền tảng',
        dot.id, cn_map['KTPM'].id, 'gv_de_xuat', gv_map['GV02'].id, None,
        'Hệ thống Tele-health hỗ trợ người bệnh đặt lịch hẹn khám bệnh viện theo thời gian thực và quản lý bệnh án điện tử.',
        'da_chon'
    ),
    (
        'Sàn thương mại điện tử tích hợp trợ lý ảo tư vấn tự động (LLM)',
        dot.id, cn_map['KTPM'].id, 'gv_de_xuat', gv_map['GV05'].id, None,
        'Nền tảng mua sắm trực tuyến tối ưu trải nghiệm khách hàng với Chatbot AI sử dụng mô hình ngôn ngữ lớn.',
        'da_chon'
    ),
    (
        'Nghiên cứu mô hình nhận diện khuôn mặt điểm danh sinh viên trong lớp học',
        dot.id, cn_map['KHMT'].id, 'gv_de_xuat', gv_map['GV03'].id, None,
        'Sử dụng thuật toán RetinaFace và ArcFace để điểm danh tự động từ camera lớp học.',
        'da_duyet'
    ),
    (
        'Hệ thống phát hiện xâm nhập mạng sử dụng thuật toán Deep Learning',
        dot.id, cn_map['MMT'].id, 'gv_de_xuat', gv_map['GV04'].id, None,
        'Phân tích lưu lượng mạng và phát hiện tấn công DDoS, quét cổng theo thời gian thực.',
        'da_duyet'
    ),
]
for ten, dot_id, cn_id, loai, gv_id, sv_id, mo_ta, tt in de_xuat_list:
    rec = NganHang.search([('dot_do_an_id', '=', dot_id), ('chuyen_nganh_id', '=', cn_id), ('giang_vien_de_xuat_id', '=', gv_id)], limit=1)
    vals = {
        'ten_de_tai': ten,
        'dot_do_an_id': dot_id,
        'chuyen_nganh_id': cn_id,
        'loai_de_tai': loai,
        'giang_vien_de_xuat_id': gv_id,
        'sinh_vien_de_xuat_id': sv_id,
        'mo_ta': mo_ta,
        'trang_thai': tt,
    }
    if rec:
        rec.write(vals)
    else:
        rec = NganHang.create(vals)
print(f"- Đã chuẩn hóa {len(de_xuat_list)} đề tài đề xuất.")

# 9. Cập nhật Đợt báo cáo tiến độ
DotBaoCao = env['quanly.dotbaocao'].sudo()
dot_bc_list = [
    (1, 'Đợt 1: Khảo sát hiện trạng, phân tích yêu cầu & thiết kế CSDL', dot.id, date(2026, 3, 20), False),
    (2, 'Đợt 2: Xây dựng Module chức năng cốt lõi & API giao tiếp', dot.id, date(2026, 4, 25), False),
    (3, 'Đợt 3: Hoàn thiện sản phẩm, đóng gói & kiểm thử', dot.id, date(2026, 5, 30), True),
]
dot_bc_map = {}
for thu_tu, ten, dot_id, han, la_cuoi in dot_bc_list:
    rec = DotBaoCao.search([('dot_do_an_id', '=', dot_id), ('thu_tu', '=', thu_tu)], limit=1)
    vals = {
        'thu_tu': thu_tu,
        'ten_dot_bao_cao': ten,
        'dot_do_an_id': dot_id,
        'han_nop': han,
        'la_ban_cuoi': la_cuoi,
        'noi_dung_yeu_cau': f'Yêu cầu sinh viên nộp tài liệu báo cáo kèm mã nguồn tiến độ đợt {thu_tu}.',
    }
    if rec:
        rec.write(vals)
    else:
        rec = DotBaoCao.create(vals)
    dot_bc_map[thu_tu] = rec
print(f"- Đã chuẩn hóa {len(dot_bc_map)} đợt báo cáo.")

# 10. Cập nhật Đề tài chính thức
DeTai = env['quanly.detai'].sudo()
dt_list = [
    (
        'DT2026_01',
        'Xây dựng hệ thống quản lý đồ án tốt nghiệp cho sinh viên Khoa Công nghệ số',
        dangky_map['22115053122323'].id,
        gv_map['GV01'].id,
        'https://github.com/NhatNamPhan/Project_Odoo',
        'http://localhost:8069',
        'Hệ thống số hóa toàn diện quy trình quản lý đồ án: từ phân công đề tài, nộp báo cáo tiến độ, chấm điểm hội đồng và lưu chiểu sản phẩm.',
        9.5,
        True,
        'Sinh viên nắm vững kiến thức framework Odoo, hoàn thành vượt mức các yêu cầu đề tài.',
        'cho_bao_ve'
    ),
    (
        'DT2026_02',
        'Xây dựng ứng dụng đặt lịch khám bệnh trực tuyến đa nền tảng',
        dangky_map['22115053122301'].id,
        gv_map['GV02'].id,
        'https://github.com/example/hospital-booking',
        'http://localhost:3000',
        'Ứng dụng React Native và Node.js hỗ trợ bệnh nhân đặt hẹn và nhận thông báo nhắc lịch.',
        8.5,
        False,
        'Tiến độ đáp ứng yêu cầu cơ bản.',
        'dang_thuc_hien'
    ),
    (
        'DT2026_03',
        'Sàn thương mại điện tử tích hợp trợ lý ảo tư vấn tự động (LLM)',
        dangky_map['22115053122302'].id,
        gv_map['GV05'].id,
        'https://github.com/example/ecommerce-ai',
        'http://localhost:8080',
        'Website bán lẻ với hệ thống đề xuất sản phẩm thông minh và chatbot tư vấn tự động.',
        9.0,
        True,
        'Hoàn thiện đầy đủ tính năng và tích hợp mô hình AI tốt.',
        'cho_bao_ve'
    ),
]
dt_map = {}
for ma, ten, dk_id, gv_id, gh, demo, mo_ta, d_gv, gv_duyet, nx, tt in dt_list:
    rec = DeTai.search([('ma_de_tai', '=', ma)], limit=1)
    vals = {
        'ma_de_tai': ma,
        'ten_de_tai': ten,
        'dang_ky_id': dk_id,
        'giang_vien_huong_dan_id': gv_id,
        'link_github': gh,
        'link_demo': demo,
        'mo_ta': mo_ta,
        'diem_gvhd': d_gv,
        'gvhd_da_duyet': gv_duyet,
        'nhan_xet_tong_ket': nx,
        'trang_thai': tt,
    }
    if rec:
        rec.write(vals)
    else:
        rec = DeTai.create(vals)
    dt_map[ma] = rec
print(f"- Đã chuẩn hóa {len(dt_map)} đề tài chính thức.")

# 11. Cập nhật Báo cáo tiến độ
BaoCao = env['quanly.baocao'].sudo()
baocao_data = [
    (dt_map['DT2026_01'].id, dot_bc_map[1].id, 1, 'baocao_tiendo_dot1_PhanHoNhatNam.pdf', 'dat', 'Đã nộp đúng hạn, thiết kế ERD chuẩn hóa 3NF tốt.'),
    (dt_map['DT2026_01'].id, dot_bc_map[2].id, 1, 'baocao_tiendo_dot2_PhanHoNhatNam.pdf', 'dat', 'Module quanly_datn cài đặt ổn định trên Odoo 18.'),
    (dt_map['DT2026_01'].id, dot_bc_map[3].id, 1, 'baocao_tiendo_dot3_PhanHoNhatNam.pdf', 'dat', 'Đã hoàn thành toàn bộ chức năng theo đề cương. Đủ điều kiện bảo vệ.'),
    (dt_map['DT2026_03'].id, dot_bc_map[1].id, 1, 'baocao_tiendo_dot1_TranThiThuHa.pdf', 'dat', 'Thiết kế hệ thống rõ ràng.'),
    (dt_map['DT2026_03'].id, dot_bc_map[2].id, 1, 'baocao_tiendo_dot2_TranThiThuHa.pdf', 'dat', 'Tích hợp mô hình AI hoạt động tốt.'),
    (dt_map['DT2026_03'].id, dot_bc_map[3].id, 1, 'baocao_tiendo_dot3_TranThiThuHa.pdf', 'dat', 'Báo cáo đầy đủ, đủ điều kiện bảo vệ.'),
]
for dt_id, dot_id, pb, ten_tep, tt, ph in baocao_data:
    rec = BaoCao.search([('de_tai_id', '=', dt_id), ('dot_bao_cao_id', '=', dot_id)], limit=1)
    vals = {
        'de_tai_id': dt_id,
        'dot_bao_cao_id': dot_id,
        'phien_ban': pb,
        'ten_tep': ten_tep,
        'file_bao_cao': dummy_file,
        'trang_thai': tt,
        'phan_hoi_gvhd': ph,
    }
    if rec:
        rec.write(vals)
    else:
        BaoCao.create(vals)
print(f"- Đã chuẩn hóa {len(baocao_data)} bài báo cáo tiến độ.")

# 12. Cập nhật Hội đồng bảo vệ
HoiDong = env['quanly.hoidong'].sudo()
hd1 = HoiDong.search([('ma_hoi_dong', '=', 'HD_KTPM_01')], limit=1)
hd_vals = {
    'dot_do_an_id': dot.id,
    'chuyen_nganh_id': cn_map['KTPM'].id,
    'ma_hoi_dong': 'HD_KTPM_01',
    'ten_hoi_dong': 'Hội đồng bảo vệ ĐATN Ngành Kỹ thuật phần mềm - Hội đồng 1',
    'thoi_gian_bao_ve': datetime(2026, 6, 22, 8, 0, 0),
    'dia_diem': 'Phòng Hội đồng B102 - Tòa nhà Trung tâm UTE',
    'trang_thai': 'du_thao',
}
if hd1:
    hd1.write(hd_vals)
else:
    hd1 = HoiDong.create(hd_vals)

HDGV = env['quanly.hoidonggiangvien'].sudo()
thanh_vien_list = [
    (hd1.id, gv_map['GV03'].id, 'chu_tich'),
    (hd1.id, gv_map['GV04'].id, 'thu_ky'),
    (hd1.id, gv_map['GV05'].id, 'phan_bien'),
    (hd1.id, gv_map['GV02'].id, 'uy_vien'),
]
hdgv_map = {}
for hd_id, gv_id, vt in thanh_vien_list:
    rec = HDGV.search([('hoi_dong_id', '=', hd_id), ('giang_vien_id', '=', gv_id)], limit=1)
    vals = {
        'hoi_dong_id': hd_id,
        'giang_vien_id': gv_id,
        'vai_tro': vt,
    }
    if rec:
        rec.write(vals)
    else:
        rec = HDGV.create(vals)
    rec._compute_display_name()
    hdgv_map[gv_id] = rec

dt_map['DT2026_01'].write({'hoi_dong_id': hd1.id})
dt_map['DT2026_03'].write({'hoi_dong_id': hd1.id})
hd1.action_chot_lich()
print(f"- Đã chuẩn hóa Hội đồng bảo vệ: {hd1.ten_hoi_dong}")

# 13. Cập nhật Phiếu chấm điểm
PhieuCham = env['quanly.phieuchamdiem'].sudo()
phieu_data = [
    (dt_map['DT2026_01'].id, hdgv_map[gv_map['GV03'].id].id, 9.5, 9.5, 'Sản phẩm hoàn thiện xuất sắc, có tính ứng dụng thực tế cao.', 'da_cham'),
    (dt_map['DT2026_01'].id, hdgv_map[gv_map['GV04'].id].id, 9.0, 9.5, 'Sinh viên tự tin, trả lời tốt câu hỏi của Hội đồng.', 'da_cham'),
    (dt_map['DT2026_01'].id, hdgv_map[gv_map['GV05'].id].id, 9.5, 9.0, 'Mã nguồn tổ chức bài bản theo chuẩn Odoo 18.', 'da_cham'),
    (dt_map['DT2026_01'].id, hdgv_map[gv_map['GV02'].id].id, 9.0, 9.5, 'Kiến trúc CSDL và phân quyền chặt chẽ.', 'da_cham'),
]
for dt_id, cb_id, d_bc, d_da, nx, tt in phieu_data:
    rec = PhieuCham.search([('de_tai_id', '=', dt_id), ('hoi_dong_giang_vien_id', '=', cb_id)], limit=1)
    vals = {
        'de_tai_id': dt_id,
        'hoi_dong_giang_vien_id': cb_id,
        'diem_bao_cao': d_bc,
        'diem_do_an': d_da,
        'nhan_xet': nx,
        'trang_thai': tt,
    }
    if rec:
        rec.write(vals)
    else:
        rec = PhieuCham.create(vals)
    rec._compute_display_name()
print(f"- Đã chuẩn hóa {len(phieu_data)} phiếu chấm điểm.")

# 14. Cập nhật Thông báo
ThongBao = env['quanly.thongbao'].sudo()
tb1 = ThongBao.search([('dot_do_an_id', '=', dot.id)], limit=1)
tb_title = 'Thông báo số 01/TB-KCN: Kế hoạch thực hiện và hướng dẫn nộp ĐATN Học kỳ 2'
tb_content = '<p>Ban Chủ nhiệm Khoa Công nghệ số thông báo đến toàn thể sinh viên làm ĐATN:</p><ul><li>Các mốc nộp báo cáo tiến độ Đợt 1, 2, 3 bắt buộc tuân thủ theo lịch.</li><li>Sinh viên thường xuyên liên hệ với GVHD để cập nhật tình hình thực hiện.</li></ul>'
if tb1:
    tb1.write({
        'tieu_de': tb_title,
        'noi_dung': tb_content,
    })
else:
    tb1 = ThongBao.create({
        'tieu_de': tb_title,
        'dot_do_an_id': dot.id,
        'noi_dung': tb_content,
    })
print(f"- Đã chuẩn hóa Thông báo chính thức: {tb1.tieu_de}")

# Recompute display_names
env['quanly.dangky'].sudo().search([])._compute_display_name()
env['quanly.hoidonggiangvien'].sudo().search([])._compute_display_name()
env['quanly.phieuchamdiem'].sudo().search([])._compute_display_name()

env.cr.commit()
print("🎉 ĐÃ HOÀN TẤT CẬP NHẬT DỮ LIỆU MẪU CHUẨN TIẾNG VIỆT UTF-8!")
