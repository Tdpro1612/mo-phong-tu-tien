---
id_he_thong: sys_users
cac_cot_du_lieu:
  - id: INTEGER
  - username: TEXT UNIQUE NOT NULL
  - password_hash: TEXT NOT NULL
  - role: TEXT NOT NULL CHECK(role IN ('root', 'admin', 'manager', 'reviewer', 'staff', 'commentor', 'viewer'))
  - is_active: INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)) # 1: Đang làm việc, 0: Đã nghỉ việc (Khóa tài khoản, KHÔNG XÓA dòng)
  - created_at: INTEGER DEFAULT (strftime('%s', 'now'))
  - expired_at: INTEGER DEFAULT NULL
---
