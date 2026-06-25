---
id_he_thong: "he_thong_linh_can"
ten_he_thong: "Hệ Thống Linh Căn"
ten_danh_muc_chinh: "Tu Tiên Lục"
cac_cot_du_lieu:
  - stt: "INTEGER"
  - ten_linh_can: "TEXT"
  - level_bich_chuong: "TEXT"
  - tdtl_doi_voi_cp_cung_linh_can: "TEXT"
  - tdtl_doi_voi_cp_khac_linh_can: "TEXT"

# 2. Cấu hình giao diện: Chỉ định rõ những cột nào sẽ được lấy để hiển thị lên Web
cac_cot_hien_thi_ui:
  - ten_linh_can
  - level_bich_chuong
  - tdtl_doi_voi_cp_cung_linh_can
  - tdtl_doi_voi_cp_khac_linh_can
# 3. Mapping: Khai báo tên hiển thị Tiếng Việt có dấu cho các cột được chọn ở trên
mapping_ngon_ngu_ui:
  ten_linh_can : Tên linh căn
  level_bich_chuong : Level bắt đầu gặp phải bích chướng
  tdtl_doi_voi_cp_cung_linh_can : Tốc độ tu luyện đối với công pháp cùng hệ linh căn
  tdtl_doi_voi_cp_khac_linh_can : Tốc độ tu luyện đối với công pháp khác hệ linh căn
---

# Giới Thiệu Hệ Thống Linh Căn
Linh Căn là căn cơ, quyết định phẩm chất và tốc độ cảm ứng linh khí đất trời của mỗi tu sĩ. Trong thế giới tu chân, Linh Căn không chỉ phân định theo độ thuần khiết (Phẩm cấp) mà còn dựa vào thuộc tính ngũ hành cấu thành. Linh căn càng thuần túy hoặc mang thuộc tính dị biến dị bảo thì tốc độ lĩnh hội công pháp và tích lũy tu vi càng kinh người.

---

## Quy Tắc Hiển Thị Linh Căn & Phân Loại Cơ Bản

### 1. Phân cấp theo Phẩm Chất (Độ thuần khiết)
Phẩm cấp Linh căn quy định giới hạn bách chướng (Mốc kẹt cấp độ) của tu sĩ. Linh căn phẩm càng thấp, mốc bách chướng đến càng sớm:
* **Thiên linh căn:** Điểm linh căn $\ge 90$ (Phá vỡ bách chướng ở `lv 101`).
* **Địa linh căn:** Điểm linh căn $\ge 70$ (Kẹt bách chướng ở `lv 81`).
* **Huyền linh căn:** Điểm linh căn $\ge 50$ (Kẹt bách chướng ở `lv 61`).
* **Hoàng linh căn:** Điểm linh căn $\ge 30$ (Kẹt bách chướng ở `lv 41`).
* **Phế linh căn:** Điểm linh căn $< 30$ (Kẹt bách chướng ngay từ `lv 11`).

### 2. Phân loại theo Số Lượng Thuộc Tính Ngũ Hành
Số lượng thuộc tính nghịch lý với tốc độ tu luyện đơn hệ, nhưng mang lại sự đa dụng khi phối hợp chiêu thức:
* **Đơn / Hai / Ba / Tứ / Ngũ linh căn:** Tương ứng lượng thuộc tính ngũ hành sở hữu. Càng nhiều hệ, tốc độ tu luyện công pháp chuyên biệt càng giảm mạnh (Từ `x10` giảm sâu xuống chỉ còn `x1`).
* **Dị linh căn (Băng, Phong, Lôi):** Biến dị hệ đặc biệt. Sở hữu thiên phú chiến đấu vượt trội và có tỷ lệ đột phá bách chướng ngang ngửa với **Thiên linh căn**.

### 3. Quy tắc tác động Tốc Độ Tu Luyện (TDTL) đối với Công Pháp (CP)
* **CP Cùng Linh Căn:** Khi tu luyện công pháp trùng khớp hoàn toàn với hệ linh căn của bản thân, tốc độ hấp thụ sẽ được nhân theo hệ số cực đại (Lên tới `x10` đối với Thiên/Đơn/Dị linh căn).
* **CP Khác Linh Căn:** Khi tu luyện các công pháp trái hệ hoặc không tối ưu, tốc độ tu luyện sẽ bị suy giảm đáng kể (Ví dụ: Phế linh căn hay Ngũ linh căn chỉ đạt hiệu suất `x0.5`).