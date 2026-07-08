// ---- HÀM BẤM NÚT SỬA ĐỂ DỰNG FORM ĐỘNG ----
function editRow(id) {
    editingRowId = id;
    const primaryKey = currentColumns[0];
    
    // Tìm dòng dữ liệu gốc tương ứng trong mảng lưu tạm global đã được table.js nạp sẵn
    const targetRow = currentMainRows.find(r => String(r[primaryKey]) === String(id));
    if (!targetRow) { alert("❌ Không tìm thấy dữ liệu gốc của bản ghi này!"); return; }

    const container = document.getElementById('modal-inputs-container');
    container.innerHTML = ""; // Làm sạch form cũ

    // Sinh tự động các ô Input dựa theo cấu trúc cột của bảng thực tế
    currentColumns.forEach((col, index) => {
        const value = targetRow[col] !== null ? targetRow[col] : "";
        
        const fieldDiv = document.createElement('div');
        fieldDiv.style.display = 'flex';
        fieldDiv.style.flexDirection = 'column';
        fieldDiv.style.gap = '0.3rem';

        const isKey = index === 0; // Cột khóa chính đầu tiên -> Khóa lại không cho sửa

        fieldDiv.innerHTML = `
            <label style="font-size: 0.9rem; color: var(--text-muted); font-weight: bold;">${col.toUpperCase()} ${isKey ? '(Khóa chính - Không thể sửa)' : ''}</label>
            <input type="text" name="${col}" value="${value}" ${isKey ? 'readonly style="background: var(--border); color: var(--text-muted); cursor: not-allowed;"' : ''} style="padding: 0.5rem; background: var(--bg-main); color: var(--text-main); border: 1px solid var(--border); border-radius: 4px;">
        `;
        container.appendChild(fieldDiv);
    });

    // Bật mở hiển thị Modal
    document.getElementById('edit-modal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

// ---- SUBMIT GỬI ĐỀ XUẤT SỬA LÊN BACKEND ----
async function submitEditForm(event) {
    event.preventDefault();
    
    const formData = new FormData(document.getElementById('edit-form'));
    const finalData = {};
    
    // Đóng gói dữ liệu từ Form thành một object key-value chuẩn
    formData.forEach((value, key) => {
        if (value === "") finalData[key] = null;
        else if (!isNaN(value) && value.trim() !== "") finalData[key] = Number(value);
        else finalData[key] = value;
    });

    try {
        const response = await fetch(`/dashboard/api/propose-change`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: Number(userId),
                system_id: currentTable,
                action: "EDIT", 
                primary_key_val: String(editingRowId),
                final_data: JSON.stringify(finalData)
            })
        });

        const result = await response.json();
        if (response.ok) {
            alert("🔮 Đề xuất chỉnh sửa (EDIT) đã nạp vào Thiên Cơ Lục bản tạm!");
            closeEditModal();
            loadTableData(currentTable); // Tải lại bảng để cập nhật dòng viền xanh lá ngay lập tức
        } else {
            throw new Error(result.detail || "Gặp lỗi khi nạp đề xuất");
        }
    } catch (err) { alert("❌ Thất bại: " + err.message); }
}

// ---- HÀM ĐỀ XUẤT XÓA ----
async function deleteRow(id) {
    if (!confirm(`Bạn có chắc chắn muốn đề xuất XÓA bản ghi ID = ${id} này không?`)) return;

    try {
        const response = await fetch(`/dashboard/api/propose-change`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: Number(userId),
                system_id: currentTable,
                action: "DELETE",
                primary_key_val: String(id),
                final_data: "{}" 
            })
        });

        const result = await response.json();
        if (response.ok) {
            alert("🔮 Đề xuất XÓA đã nạp thành công vào bản tạm chờ duyệt!");
            loadTableData(currentTable);
        } else {
            throw new Error(result.detail || "Gặp lỗi khi nạp đề xuất xóa");
        }
    } catch (err) { alert("❌ Thất bại: " + err.message); }
}
