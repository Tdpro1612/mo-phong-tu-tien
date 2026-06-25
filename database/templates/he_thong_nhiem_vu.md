---
id_he_thong: "he_thong_nhiem_vu"
ten_he_thong: "Hệ Thống Nhiệm Vụ"
ten_danh_muc_chinh: "Tu Tiên Lục"
cac_cot_du_lieu:
  - stt: "INTEGER"
  - ten_nhiem_vu: "TEXT"
  - ma_nhiem_vu: "TEXT"
  - mo_ta_nhiem_vu: "TEXT"
  - bac: "INTEGER"
  - level: "INTEGER"
  - loai_nhiem_vu: "TEXT"
  - yeu_cau: "TEXT"

# 2. Cấu hình giao diện: Chỉ định rõ những cột nào sẽ được lấy để hiển thị lên Web
cac_cot_hien_thi_ui:
  - ten_nhiem_vu
  - mo_ta_nhiem_vu
  - bac
  - level
  - loai_nhiem_vu
  - yeu_cau
# 3. Mapping: Khai báo tên hiển thị Tiếng Việt có dấu cho các cột được chọn ở trên
mapping_ngon_ngu_ui:
  ten_nhiem_vu: Tên nhiệm vụ
  mo_ta_nhiem_vu: Mô tả nhiệm vụ
  bac: Bậc
  level: Level nhận nhiệm vụ
  loai_nhiem_vu: Loại nhiệm vụ
  yeu_cau: Yêu cầu tiền để để nhận nhiệm vụ
---

# Giới Thiệu Hệ Thống Nhiệm Vụ
Trong thế giới tu chân, nhân vật không chỉ bế quan tu luyện mà còn phải thực hiện các nhiệm vụ tông môn, rèn luyện nghề phụ, thi đấu tỷ thí để tích lũy tài nguyên và danh vọng. Hệ thống nhiệm vụ phân định rõ ràng các tầng thứ yêu cầu (Bậc, Level) và mối quan hệ ràng buộc giữa các chuỗi nhiệm vụ với nhau.

---

## Quy Tắc Định Danh Vấn Đề & Phân Loại Nhiệm Vụ

### 1. Quy tắc đặt Mã Nhiệm Vụ (Naming Convention)
Mọi nhiệm vụ trong game bắt buộc phải tuân theo cấu trúc mã hóa nghiêm ngặt để hệ thống tự động nhận diện logic mà không cần hard-code:
* **Cú pháp:** `Q_[Bậc]_[Level]_[LoạiNhiệmVụ]_[MãSố]`
* **Giải thích các ký tự viết tắt của Loại Nhiệm Vụ:**
  * `R`: Tuần hoàn (Nhiệm vụ cơ bản, lặp lại hàng ngày/tháng).
  * `S`: Ẩn (Nhiệm vụ ẩn phúc lợi, chỉ xuất hiện khi đủ duyên số hoặc điều kiện).
  * `C`: Khiếu chiến (Nhiệm vụ thử thách, tỷ thí nâng cao danh vọng, chức vụ).

### 2. Phân Loại Chi Tiết Các Loại Nhiệm Vụ
* **Nhiệm vụ Tuần hoàn (`R`):**
  * *Nhiệm vụ mầm tiên:* (Ví dụ: Đọc sách, Trồng trọt linh thực, Chăn nuôi linh thú) Giúp nhân vật tiếp xúc với chữ viết, kinh mạch, kiếm thu nhập ban đầu. Yêu cầu cơ bản ở `Bậc 0, Level 0`.
  * *Nhiệm vụ nghề phụ / cao cấp:* (Ví dụ: Làm học đồ, Đóng giữ, Nhân viên sảnh/chiến đấu/hậu cần) Yêu cầu cấp độ cao hơn (`Level 2 -> 5`), giúp tích lũy nhiều tài lộc hơn.
* **Nhiệm vụ Ẩn (`S`):**
  * (Ví dụ: Cổ tông môn truyền thừa, Đan vương truyền thừa, Khí vương chọn đồ...) Đây là các nhiệm vụ ẩn phúc lợi đầu tiên. Khi hoàn thành sẽ giúp tu tiên giả gia tăng đột biến tốc độ tu luyện.
  * *Cơ chế ràng buộc (Yêu cầu):* Các nhiệm vụ ẩn này đòi hỏi nhân vật phải hoàn thành một nhiệm vụ điều kiện trước đó. Ví dụ: Để mở khóa nhiệm vụ ẩn `Q_B0_4_S_9` thì bắt buộc cột Yêu cầu phải ghi nhận đã hoàn thành nhiệm vụ nghề phụ `Q_B0_2_R_4`.
* **Nhiệm vụ Khiếu chiến (`C`):**
  * (Ví dụ: Thi đấu hạng nhất, hạng nhì, hạng ba) Thường xuất hiện ở các mốc mấu chốt (`Bậc 0, Level 8`). Giúp tu tiên giả gia tăng mạnh mẽ danh vọng, chức vụ và mở rộng tầm ảnh hưởng của bản thân trong tông môn.