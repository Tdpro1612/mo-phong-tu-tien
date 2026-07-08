---
id_he_thong: sys_reject_archive
cac_cot_du_lieu:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - table_name: TEXT NOT NULL                  # Tên bảng chính bị từ chối
  - b_key_value: TEXT DEFAULT NULL             # Giá trị Business Key của dòng (Nếu là EDIT/DELETE)
  - username: TEXT NOT NULL                    # Tài khoản nhân viên tạo đề xuất bị từ chối
  - manager_name: TEXT NOT NULL                # Tài khoản Manager đã bấm từ chối
  - reject_reason: TEXT DEFAULT NULL           # Lý do từ chối do Manager nhập vào
  - final_data: TEXT DEFAULT NULL              # Chuỗi JSON chứa dữ liệu lỗi/bị từ chối để xem lại
  - action_type: TEXT NOT NULL                 # 'NEW', 'EDIT', 'DELETE'
  - rejected_at: INTEGER DEFAULT (strftime('%s', 'now'))
---