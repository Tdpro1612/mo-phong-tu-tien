---
id_he_thong: sys_pending_changes
cac_cot_du_lieu:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - table_name: TEXT NOT NULL                                                    # Tên bảng chính cần tác động (Ví dụ: 'data_items')
  - key_old_value: TEXT DEFAULT NULL                                            # Điểm neo: Giá trị CŨ của Cột số 2 ở bảng chính (Bắt buộc với EDIT/DELETE)
  - username: TEXT NOT NULL                                                      # Tài khoản nhân viên tạo đề xuất
  - final_data: TEXT DEFAULT NULL                                               # Chuỗi JSON dữ liệu MỚI hoàn chỉnh từ UI (Có thể NULL khi DELETE)
  - action_type: TEXT NOT NULL CHECK(action_type IN ('NEW', 'EDIT', 'DELETE'))   # Phân biệt hàm gọi dưới DB
  - review_status: TEXT NOT NULL CHECK(review_status IN ('PENDING', 'ACCEPT', 'DENY', 'DONE', 'REJECT')) # Tiến độ sảnh duyệt
  - created_at: INTEGER DEFAULT (strftime('%s', 'now'))
---