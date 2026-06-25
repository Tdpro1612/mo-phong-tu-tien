---
id_he_thong: "he_thong_chi_so_nhan_vat"
ten_he_thong: "Hệ Thống Chỉ Số Nhân Vật"
ten_danh_muc_chinh: "Tu Tiên Lục"
# 1. Danh sách tất cả các cột để khởi tạo cấu trúc bảng trong Database SQLite3
cac_cot_du_lieu:
  - stt: "INTEGER"
  - ten_chi_so: "TEXT"
  - mo_ta_chi_so: "TEXT"
  - loai_chi_so: "TEXT"
# 2. Cấu hình giao diện: Chỉ định rõ những cột nào sẽ được lấy để hiển thị lên Web
cac_cot_hien_thi_ui:
  - ten_chi_so
  - mo_ta_chi_so
  - loai_chi_so

# 3. Mapping: Khai báo tên hiển thị Tiếng Việt có dấu cho các cột được chọn ở trên
mapping_ngon_ngu_ui:
  ten_chi_so: Tên chỉ số
  mo_ta_chi_so: Mô tả chỉ số
  loai_chi_so: Loại chỉ số
---

# Giới Thiệu Hệ Thống Chỉ Số Nhân Vật
Mỗi vị tu sĩ khi bước chân vào con đường nghịch thiên cải mệnh đều sở hữu một bộ căn cơ riêng biệt, phản ánh qua các chỉ số nhân vật. Hệ thống chỉ số phân định rạch ròi giữa năng lực sinh hoạt hàng ngày, thiên phú tu luyện ẩn tàng, vận khí cơ duyên và khả năng chiến đấu thực tế khi đối đầu với yêu ma hoặc tu sĩ khác.

---

## Cơ Chế Vận Hành & Phân Loại Chỉ Số Chi Tiết

### 1. Chỉ Số Cơ Bản Công Khai (Thể Lực)
Thể lực là chỉ số cốt lõi ảnh hưởng trực tiếp đến mọi hoạt động hàng ngày và sinh tồn của nhân vật:
* **Giới hạn & Phục hồi:** Một ngày có tối đa `100` thể lực. Nếu nhân vật nghỉ ngơi đủ 8 tiếng liên tục (không chia lẻ) sẽ hồi phục `50` thể lực.
* **Tiêu hao:** Mỗi nhiệm vụ trong game sẽ tốn một lượng thời gian và thể lực riêng biệt.
* **Cơ chế Ngất xỉu & Tử vong:** 
  * Nhân vật luôn cần tối thiểu `50` thể lực để duy trì trạng thái tỉnh táo. Dưới mốc này có nguy cơ bị ngất xỉu.
  * *Trường hợp sau khi ngất xỉu nếu thể lực trên 30:* Nghỉ ngơi đủ thời gian sẽ hồi phục đủ `50` thể lực để tỉnh lại. Trong khoảng thể lực từ 30 - 50, mỗi 1 tiếng nghỉ ngơi hồi phục `2` thể lực.
  * *Trường hợp thể lực dưới 30:* Nhân vật rơi vào trạng thái nguy kịch, tự thân không thể hồi phục trừ khi có người khác can thiệp (gặp Kỳ ngộ). Nếu không có kỳ ngộ giải cứu, nhân vật sẽ không thể tỉnh lại và dẫn đến **Tử vong**.
  * **Chấn thương:** Các vết thương gánh chịu trong quá trình chiến đấu/sinh hoạt sẽ ảnh hưởng tiêu cực đến tốc độ khôi phục thể lực và giảm mức thể lực tối đa.

### 2. Chỉ Số Cơ Bản Ẩn (Căn Cốt, Ngộ Tính, Linh Căn, Thiên Phú, Khí Vận, Phúc Duyên)
Là các chỉ số không hiển thị mặc định, quyết định tiềm năng và cơ duyên của tu sĩ:
* **Quy tắc kích hoạt đối với Tán Tu:** Nếu người chơi lựa chọn xuất thân là Tán tu, các chỉ số *Căn cốt, Linh căn, Thiên phú* ban đầu sẽ bị ẩn đi. Các chỉ số này chỉ được kích hoạt và hiển thị sau khi thực hiện kiểm tra bằng **Đá Khai Linh**.
* **Công dụng cụ thể:**
  * **Căn cốt:** Buff tăng tốc độ tu luyện kỹ năng công pháp.
  * **Ngộ tính:** Buff tăng tốc độ lĩnh hội kỹ năng công pháp.
  * **Linh căn & Thiên phú:** Buff song song, tăng mạnh cả tốc độ tu luyện lẫn tốc độ lĩnh hội kỹ năng công pháp.
  * **Khí vận:** Ảnh hưởng đến việc gặp kỳ ngộ là tốt hay xấu, đồng thời tác động trực tiếp đến xác suất thành công của các hành động lớn (đột phá, chế tạo...).
  * **Phúc duyên:** Ảnh hưởng đến tỷ lệ kích hoạt (gặp) các sự kiện kỳ ngộ trong thế giới.

### 3. Chỉ Số Chiến Đấu Công Khai (Sinh Lực, Tấn Công, Phòng Thủ)
Bộ chỉ số trực tiếp quyết định thành bại khi xảy ra tranh đấu:
* **Sinh lực:** Trạng thái sống còn của nhân vật trong trận chiến.
* **Tấn công:** Khả năng gây sát thương trực tiếp lên địch nhân.
* **Phòng thủ:** Khả năng giảm thiểu sát thương gánh chịu từ đòn đánh của kẻ địch.