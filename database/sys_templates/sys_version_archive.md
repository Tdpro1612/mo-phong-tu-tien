---
id_he_thong: sys_version_archive
cac_cot_du_lieu:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - version: TEXT NOT NULL                     # Số phiên bản do Manager nhập vào lúc duyệt DONE (Ví dụ: 'v1.0.1')
  - table_name: TEXT NOT NULL                  # Tên bảng chính chịu tác động
  - b_key_value: TEXT NOT NULL                 # Khóa nghiệp vụ dùng để định vị dòng khi cần Rollback
  - action_type: TEXT NOT NULL                 # 'NEW', 'EDIT', 'DELETE'
  - delta_patch: TEXT NOT NULL                 # Chuỗi JSON lưu trữ vi sai dạng [Giá_trị_CŨ, Giá_trị_MỚI]
  - username: TEXT NOT NULL                    # Tài khoản nhân viên tạo đề xuất ban đầu
  - manager_name: TEXT NOT NULL                # Tài khoản Manager đã bấm duyệt DONE
  - approved_at: INTEGER DEFAULT (strftime('%s', 'now'))
---