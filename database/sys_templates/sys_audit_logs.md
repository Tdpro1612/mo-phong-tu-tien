---
id_he_thong: sys_audit_logs
cac_cot_du_lieu:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - version: TEXT DEFAULT NULL                 # Số phiên bản (Chỉ có khi review_status = 'DONE', còn lại NULL)
  - username: TEXT NOT NULL                    # Tài khoản người thực hiện hành vi hoặc người duyệt
  - table_name: TEXT NOT NULL                  # Bảng mục tiêu chịu tác động (Ví dụ: 'data_items')
  - business_key_value: TEXT NOT NULL                 # Giá trị Business Key tại Cột 2 làm điểm neo truy vết (Kể cả NEW vẫn lưu tên mới vào đây để lọc)
  - action_type: TEXT NOT NULL                 # 'NEW', 'EDIT', 'DELETE'
  - review_status: TEXT NOT NULL               # 'PENDING', 'ACCEPT', 'DENY', 'DONE', 'REJECT'
  - history_data: TEXT                         # Chuỗi JSON lưu Full Snapshot dữ liệu cũ và mới: {"old": {...}, "new": {...}}
  - timestamp: INTEGER DEFAULT (strftime('%s', 'now'))
---