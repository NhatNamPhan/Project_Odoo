from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    # A legacy zero cannot be distinguished from an unentered grade.
    # Leave it unconfirmed until the supervisor explicitly saves the grade.
    cr.execute('UPDATE quanly_detai SET diem_gvhd_da_nhap = TRUE WHERE diem_gvhd <> 0')
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['quanly.detai'].search([])._compute_diem_tong_ket()
