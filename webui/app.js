/**
 * THIÊN CƠ LỤC - CORE APPLICATION LOGIC (GENERIC WIKI VERSION)
 */

// SỰ KIỆN 1: Tự động chạy khi tải trang để dựng Sidebar từ API
document.addEventListener("DOMContentLoaded", () => {
    const treeMenu = document.getElementById("tree-menu");
    
    // Gọi API để lấy danh sách các bảng hiện có trong Database
    fetch(`/api/systems`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Không thể kết nối tới Backend server hoặc DB trống.");
            }
            return response.json();
        })
        .then(data => {
            let menuHtml = "";
            
            menuHtml += `
                <div class="folder-group">
                    <div class="folder-title">
                        <i class="fa-solid fa-folder-open"></i> HỆ THỐNG DỮ LIỆU
                    </div>
                    <ul class="file-list">
            `;
            
            // Duyệt qua danh sách các bảng dữ liệu trả về từ SQLite
            data.tables.forEach(tableName => {
                // Biến đổi snake_case thành dạng viết hoa chữ cái đầu để hiển thị trực quan trên Sidebar
                const displayName = tableName
                    .split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');

                menuHtml += `
                    <li class="file-item" onclick="loadSystemData('${tableName}', this)">
                        <i class="fa-solid fa-database"></i> ${displayName}
                    </li>
                `;
            });
            
            menuHtml += `
                    </ul>
                </div>
            `;
            
            treeMenu.innerHTML = menuHtml;
        })
        .catch(error => {
            // Hiển thị lỗi trực quan lên Sidebar nếu quên chưa bật FastAPI
            treeMenu.innerHTML = `
                <div style="color: #ef4444; padding: 15px; font-size: 14px; background: rgba(239, 68, 68, 0.1); border-radius: 6px;">
                    <i class="fa-solid fa-triangle-exclamation"></i> <strong>Lỗi kết nối Backend:</strong><br>${error.message}
                    <p style="font-size: 12px; color: #eab308; margin-top: 8px; margin-bottom: 0;">
                        💡 <b>Mẹo:</b> Đảm bảo đạo hữu đã khởi chạy Uvicorn server bằng lệnh <code>make run-web</code> trước khi xem trang.
                    </p>
                </div>
            `;
        });
});


// SỰ KIỆN 2: Lazy Loading dữ liệu khi bấm chọn hệ thống trên Sidebar
function loadSystemData(systemId, element) {
    // Quản lý hiệu ứng active trên thanh menu sidebar
    document.querySelectorAll('.file-item').forEach(item => item.classList.remove('active'));
    if (element) element.classList.add('active');

    // Gọi API bốc dữ liệu tổng hợp của hệ thống được chọn
    fetch(`/api/system/${systemId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Thất bại khi lấy dữ liệu hệ thống: ${systemId}`);
            }
            return response.json();
        })
        .then(data => {
            // 1. Ẩn màn hình chào mừng, mở khung nội dung chính
            document.getElementById('welcome-view').style.display = 'none';
            document.getElementById('content-card').style.display = 'block';
            
            // 2. Chuẩn bị phần nội dung hướng dẫn tĩnh (Markdown)
            let finalHtml = "";
            const markdownContent = data.huong_dan_markdown ? `<div class="markdown-body">${marked.parse(data.huong_dan_markdown)}</div>` : '';
            
            // 3. Xử lý chia trang dòng dữ liệu động tổng quát (Không hard-code)
            if (data.cac_cot_hien_thi_ui && data.cac_cot_hien_thi_ui.length > 0) {
                const rows = data.rows || [];
                const headers = data.cac_cot_hien_thi_ui; // Cột đã lọc sạch ở backend
                const mapping = data.mapping_ngon_ngu_ui || {}; // Bản đồ ngôn ngữ mới
                
                // CẬP NHẬT: Đồng bộ dữ liệu mới (gồm cả mapping) vào window để truy cập toàn cục
                window.currentSystemData = {
                    headers: headers,
                    rows: rows,
                    mapping_ngon_ngu_ui: mapping,
                    systemId: systemId
                };

                // Trả về trang 0 (Mặc định là trang Giới thiệu tổng quan)
                window.currentWikiPage = 0; 

                // Khởi tạo khung chứa tổ hợp điều hướng
                let wikiHtml = `
                    <div class="wiki-navigation-panel">
                        <div class="wiki-filter-wrapper">
                            <label for="wiki-page-select"><i class="fa-solid fa-compass"></i> Mục Lục Hệ Thống: </label>
                            <select id="wiki-page-select" onchange="switchWikiPage(parseInt(this.value))">
                                <option value="0">📖 Trang Giới Thiệu Tổng Quan</option>
                `;

                // Đổ các hàng dữ liệu vào Option - Tối ưu tìm kiếm cột Định danh tên gọi linh hoạt hơn
                rows.forEach((row, idx) => {
                    // Ưu tiên tìm các cột có chứa chữ 'ten_' để lấy tên hệ thống có dấu làm Title mục lục
                    const nameKey = headers.find(h => h.startsWith('ten_')) || headers[1] || Object.keys(row)[1];
                    const dynamicTitle = row[nameKey] || `Bản ghi số ${idx + 1}`;
                    
                    wikiHtml += `<option value="${idx + 1}">📄 Trang ${idx + 1}: ${dynamicTitle}</option>`;
                });

                wikiHtml += `
                            </select>
                        </div>

                        <div id="wiki-page-content-holder">
                            <div id="wiki-intro-section" class="wiki-page-fade">${markdownContent}</div>
                            <div id="wiki-row-detail-section" class="wiki-page-fade" style="display: none;"></div>
                        </div>

                        <div class="wiki-pagination-bar">
                            <button id="btn-wiki-back" class="wiki-nav-btn" onclick="navigateWikiPage(-1)" disabled>
                                <i class="fa-solid fa-chevron-left"></i> Trang Trước
                            </button>
                            <span id="wiki-page-indicator" class="wiki-page-indicator">Trang Giới Thiệu</span>
                            <button id="btn-wiki-next" class="wiki-nav-btn" onclick="navigateWikiPage(1)" ${rows.length === 0 ? 'disabled' : ''}>
                                Trang Sau <i class="fa-solid fa-chevron-right"></i>
                            </button>
                        </div>
                    </div>
                `;

                finalHtml = wikiHtml;
            } else {
                finalHtml = markdownContent || `<p style="color: #64748b; font-style: italic;">💡 Hệ thống này hiện chưa có tài liệu lẫn dữ liệu DB.</p>`;
            }

            // Đổ toàn bộ cấu trúc vừa build vào vùng nội dung chính
            document.getElementById('content-area').innerHTML = finalHtml;
        })
        .catch(error => {
            document.getElementById('welcome-view').style.display = 'none';
            document.getElementById('content-card').style.display = 'block';
            document.getElementById('content-area').innerHTML = `
                <div style="padding: 20px; border-left: 4px solid #ef4444; background: rgba(239,68,68,0.05);">
                    <h2 style="color: #ef4444; margin-top: 0;"><i class="fa-solid fa-circle-exclamation"></i> Lỗi Nạp Hệ Thống</h2>
                    <p style="color: #94a3b8;">${error.message}</p>
                </div>
            `;
        });
}

// HÀM TOÀN CỤC: Chuyển đổi trang tài liệu chi tiết
function switchWikiPage(targetPageIndex) {
    const data = window.currentSystemData;
    if (!data) return;

    window.currentWikiPage = targetPageIndex;
    const introSection = document.getElementById('wiki-intro-section');
    const detailSection = document.getElementById('wiki-row-detail-section');
    const selectDropdown = document.getElementById('wiki-page-select');
    const pageIndicator = document.getElementById('wiki-page-indicator');
    
    if (selectDropdown) selectDropdown.value = targetPageIndex;

    if (targetPageIndex === 0) {
        if (introSection) introSection.style.display = 'block';
        if (detailSection) detailSection.style.display = 'none';
        pageIndicator.innerText = "Trang Giới Thiệu";
    } else {
        if (introSection) introSection.style.display = 'none';
        if (detailSection) detailSection.style.display = 'block';
        
        const rowIndex = targetPageIndex - 1;
        const rowData = data.rows[rowIndex];
        const headers = data.headers;
        const mapping = data.mapping_ngon_ngu_ui || {}; // Lấy map dịch thuật toàn cục
        
        // Tối ưu hóa tìm kiếm cột làm tiêu đề trang tài liệu con
        const nameKey = headers.find(h => h.startsWith('ten_')) || headers[1] || Object.keys(rowData)[1];
        const pageTitle = rowData[nameKey] || `Hàng dữ liệu số ${targetPageIndex}`;
        
        pageIndicator.innerText = `Trang ${targetPageIndex} / ${data.rows.length}`;

        let rowHtml = `
            <div class="wiki-document-container">
                <h1 class="wiki-doc-title">${pageTitle}</h1>
                <hr class="wiki-doc-hr">
        `;
        
        // Thân bài duyệt tất cả các cột dữ liệu còn lại
        headers.forEach((header) => {
            // Bỏ qua cột STT và chính cột TÊN đã được đưa ra làm tiêu đề lớn (pageTitle) ở trên
            if (header === 'stt' || header === nameKey) {
                return; 
            }

            let cellValue = rowData[header];
            if (cellValue === null || cellValue === undefined || cellValue === '') {
                cellValue = `<span class="null-value">NULL (Trống)</span>`;
            }

            // CẬP NHẬT LOGIC TITLE TIẾNG VIỆT CÓ DẤU:
            // Ưu tiên lấy từ cấu hình mapping trong file .md, nếu không có mới dùng thuật toán fallback cũ
            const sectionLabel = mapping[header] || header.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

            rowHtml += `
                <div class="wiki-doc-section">
                    <h3 class="wiki-section-heading">${sectionLabel}</h3>
                    <div class="wiki-section-content">${cellValue}</div>
                </div>
            `;
        });

        rowHtml += `</div>`;
        if (detailSection) detailSection.innerHTML = rowHtml;
    }

    // Khóa/Mở nút điều hướng khi chạm biên dữ liệu
    document.getElementById('btn-wiki-back').disabled = (targetPageIndex === 0);
    document.getElementById('btn-wiki-next').disabled = (targetPageIndex === data.rows.length);
}

// HÀM TOÀN CỤC: Tăng/Giảm trang khi bấm Next/Back
function navigateWikiPage(direction) {
    const nextTarget = window.currentWikiPage + direction;
    const data = window.currentSystemData;
    if (!data) return;

    if (nextTarget >= 0 && nextTarget <= data.rows.length) {
        switchWikiPage(nextTarget);
    }
}