async function loadTableData(tableName) {
    if (!tableName) { document.getElementById('data-workspace').style.display = 'none'; return; }
    currentTable = tableName;
    document.getElementById('current-table-title').innerText = `📋 Bảng: ${tableName.replace(/_/g, ' ').toUpperCase()}`;
    
    const tbodyMain = document.getElementById('table-tbody-main');
    const tbodyTemp = document.getElementById('table-tbody-temp');
    const thead = document.getElementById('table-thead');
    
    thead.innerHTML = "";
    tbodyMain.innerHTML = "";
    if (tbodyTemp) tbodyTemp.innerHTML = "";
    document.getElementById('proposal-counter').innerText = "Số dòng đã đề xuất: 0";

    try {
        // ---- BƯỚC 1: Rút trích dữ liệu gốc chính thức ----
        const responseMain = await fetch(`/dashboard/api/table-data/main?table=${tableName}`);
        const resultMain = await responseMain.json();
        if (!responseMain.ok) throw new Error(resultMain.detail || "Lỗi đọc dữ liệu gốc");

        // 🔥 VÁ LỖI CHÍ MẠNG: Nạp thẳng dữ liệu vừa fetch vào bộ nhớ đệm global để actions.js bốc ID chuẩn
        currentColumns = resultMain.columns;
        currentMainRows = resultMain.rows;

        // Tạo Header tiêu đề bảng chính xác
        let headerRow = "<tr>";
        currentColumns.forEach(col => { headerRow += `<th>${col}</th>`; });
        headerRow += "<th style='text-align: center;'>HÀNH ĐỘNG</th></tr>";
        thead.innerHTML = headerRow;

        // Đổ các dòng dữ liệu gốc chính thức
        if (currentMainRows.length === 0) {
            tbodyMain.innerHTML = `<tr><td colspan="${currentColumns.length + 1}" style="text-align: center; color: var(--text-muted);">Bảng này chưa có dữ liệu tu tiên chính thức.</td></tr>`;
        } else {
            const primaryKeyColumn = currentColumns[0]; // Lấy cột khóa chính đầu tiên làm mốc (stt/id)

            currentMainRows.forEach(row => {
                let rowHtml = "<tr>";
                currentColumns.forEach(col => { 
                    rowHtml += `<td>${row[col] !== null ? row[col] : 'NULL'}</td>`; 
                });
                
                // Trích xuất ID chuẩn xác từ cột khóa chính của dòng
                const actualId = row[primaryKeyColumn];

                rowHtml += `
                    <td style="text-align: center; width: 150px;">
                        <button class="btn-sm btn-edit" onclick="editRow('${actualId}')">✏️ Sửa</button>
                        <button class="btn-sm btn-delete" onclick="deleteRow('${actualId}')">❌ Xóa</button>
                    </td></tr>`;
                tbodyMain.innerHTML += rowHtml;
            });
        }

        // ---- BƯỚC 2: Rút trích dữ liệu bản tạm cá nhân (Trừ vai trò viewer) ----
        if (userRole !== 'viewer' && tbodyTemp) {
            const responseTemp = await fetch(`/dashboard/api/table-data/temp?table=${tableName}&user_id=${userId}`);
            const resultTemp = await responseTemp.json();
            
            if (responseTemp.ok && resultTemp.rows.length > 0) {
                document.getElementById('proposal-counter').innerText = `Số dòng đã đề xuất: ${resultTemp.rows.length}`;
                
                resultTemp.rows.forEach(row => {
                    let rowHtml = `<tr class="khung-xanh-la">`;
                    currentColumns.forEach(col => { rowHtml += `<td>${row[col] !== null ? row[col] : 'NULL'}</td>`; });
                    rowHtml += `
                        <td style="text-align: center; width: 150px;">
                            <span style="font-size: 0.85rem; font-style: italic;">⏳ Chờ duyệt...</span>
                        </td></tr>`;
                    tbodyTemp.innerHTML += rowHtml;
                });
            }
        }

        document.getElementById('data-workspace').style.display = 'block';
    } catch (err) { alert("❌ Thất bại: " + err.message); }
}
