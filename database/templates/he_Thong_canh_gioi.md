---
id_he_thong: "he_thong_canh_gioi"
ten_he_thong: "Hệ Thống Cảnh Giới"
ten_danh_muc_chinh: "Tu Tiên Lục"

# 1. Danh sách tất cả các cột để khởi tạo cấu trúc bảng trong Database SQLite3
cac_cot_du_lieu:
  - stt: "INTEGER"
  - ten_goi: "TEXT"
  - level_min: "INTEGER"
  - level_max: "INTEGER"
  - mo_ta_canh_gioi: "TEXT"
  - so_luong_exp_can_moi_tang: "INTEGER"
  - tho_nguyen_lon_nhat: "INTEGER"
  - bac_he_so_10_mu: "INTEGER"

# 2. Cấu hình giao diện: Chỉ định rõ những cột nào sẽ được lấy để hiển thị lên Web
# (Ví dụ: Ẩn cột 'level_min', 'level_max' và 'bac_he_so_10_mu' để giao diện gọn gàng hơn)
cac_cot_hien_thi_ui:
  - ten_goi
  - level_min
  - level_max
  - mo_ta_canh_gioi
  - so_luong_exp_can_moi_tang
  - tho_nguyen_lon_nhat

# 3. Mapping: Khai báo tên hiển thị Tiếng Việt có dấu cho các cột được chọn ở trên
mapping_ngon_ngu_ui:
  ten_goi: "Tên Cảnh Giới"
  level_min: "level thấp nhất"
  level_max: "level cao nhất"
  mo_ta_canh_gioi: "Mô Tả Cảnh Giới"
  so_luong_exp_can_moi_tang: "EXP Cần Mỗi Tầng"
  tho_nguyen_lon_nhat: "Thọ Nguyên Tối Đa"
---

# Giới Thiệu Hệ Thống Cảnh Giới
Đường tu tiên phân chia thành 10 cảnh giới lớn từ Linh Hư đến Đại Thừa. Mỗi cảnh giới đại diện cho một tầng thứ sinh mệnh khác nhau, sở hữu vĩ lực và thọ nguyên hoàn toàn chênh lệch. Việc đột phá qua các đại cảnh giới yêu cầu tích lũy linh lực và ngộ tính thâm hậu.

---

## Quy Tắc Hiển Thị Cảnh Giới & Phạt Kinh Nghiệm (EXP)

> ⚠️ **Thông tin cốt lõi dành cho Đạo Hữu:**

### 1. Cơ chế hiển thị trên Giao diện (UI)
Hệ thống cấp độ được quản lý theo dạng Cảnh giới (Tương ứng với Bậc) và Tầng thực tế của cảnh giới đó:
* **Ví dụ cụ thể:** Nếu nhân vật có tổng tu vi đạt đến mốc **Trúc Cơ tầng 2** (Tương đương cấp độ thực tế trong Game):
    * **UI Cảnh giới** sẽ hiển thị chính xác là: **Bậc 1**.
    * **Cây hiển thị EXP** của nhân vật sẽ tính theo tầng hiện tại là `level 2`: Giá trị chạy từ `0.00` đến `100.00`.