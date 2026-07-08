// Khối 1: Trạng Thái Toàn Cục (Global States)
/**
 * THIÊN CƠ LỤC - CORE APPLICATION LOGIC (CLEAN LOGIC VERSION)
 */

// Lưu trữ bản đồ Schema Metadata bốc từ các file .md (Mọi bảng game)
window.allSystemSchemas = {};

// Lưu trữ dữ liệu thực tế và cấu hình riêng của bảng đang được chọn hiển thị
window.currentSystemData = null;

// Chỉ số trang hiện tại của Wiki (0: Tổng quan + Hướng dẫn, >=1: Chi tiết từng dòng)
window.currentWikiPage = 0;

// Khối 2: Khởi Tạo Hệ Thống & Sidebar (Initialization)
// Tự động kích hoạt khi tải trang: Nạp Schemas tổng lực từ Backend và dựng Sidebar
document.addEventListener("DOMContentLoaded", () => {
    const treeMenu = document.getElementById("tree-menu");
    
    fetch(`/api/webui-schemas`)
        .then(response => {
            if (!response.ok) throw new Error("Không thể nạp bản đồ cấu trúc hệ thống (Schemas).");
            return response.json();
        })
        .then(schemas => {
            window.allSystemSchemas = schemas;
            const tableNameList = Object.keys(schemas);

            if (tableNameList.length === 0) {
                treeMenu.innerHTML = `<p class="wiki-empty-msg">💡 Chưa có hệ thống dữ liệu nào được khởi tạo hoặc thiếu file template.</p>`;
                return;
            }

            let menuHtml = `
                <div class="folder-group">
                    <div class="folder-title">
                        <i class="fa-solid fa-folder-open"></i> HỆ THỐNG DỮ LIỆU
                    </div>
                    <ul class="file-list">
            `;
            
            tableNameList.forEach(tableName => {
                const templateName = schemas[tableName]?.ten_he_thong;
                const displayName = templateName || tableName
                    .replace("he_thong_", "")
                    .split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');

                menuHtml += `
                    <li class="file-item" onclick="loadSystemData('${tableName}', this)">
                        <i class="fa-solid fa-database"></i> ${displayName}
                    </li>
                `;
            });
            
            menuHtml += `</ul></div>`;
            treeMenu.innerHTML = menuHtml;
        })
        .catch(error => {
            treeMenu.innerHTML = `
                <div class="wiki-error-box">
                    <i class="fa-solid fa-triangle-exclamation"></i> 
                    <strong>Lỗi khởi tạo hệ thống:</strong><br>${error.message}
                </div>
            `;
        });
});

// Khối 3: Nạp Dữ Liệu Bảng (Data Ingestion)
// Lazy Loading dữ liệu thô từ DB khi click Sidebar và đối chiếu Schema toàn cục
// Lazy Loading dữ liệu thô từ DB khi click Sidebar và đối chiếu Schema toàn cục
function loadSystemData(tableName, element) {
    document.querySelectorAll('.file-item').forEach(item => item.classList.remove('active'));
    if (element) element.classList.add('active');

    fetch(`/db/table/${tableName}`)
        .then(response => {
            if (!response.ok) throw new Error(`Thất bại khi lấy dữ liệu từ bảng: ${tableName}`);
            return response.json();
        })
        .then(resDb => {
            const rows = resDb.data || [];

            document.getElementById('welcome-view').style.display = 'none';
            document.getElementById('content-card').style.display = 'block';
            
            if (rows.length === 0) {
                document.getElementById('content-area').innerHTML = `
                    <p class="wiki-empty-msg">💡 Bảng [${tableName}] hiện đang rỗng dữ liệu dưới SQLite.</p>
                `;
                return;
            }

            const schema = window.allSystemSchemas[tableName] || {};
            const uiColumns = schema.cac_cot_hien_thi_ui || [];
            const mapping = schema.mapping_ngon_ngu_ui || {};
            const markdownIntro = schema.intro || '';

            let headers = [];
            if (uiColumns.length > 0) {
                headers = uiColumns.filter(col => Object.keys(rows[0]).includes(col));
            } else {
                headers = Object.keys(rows[0]).filter(h => h !== 'id');
            }

            window.currentSystemData = {
                headers: headers,
                rows: rows,
                tableName: tableName,
                mapping: mapping,
                intro: markdownIntro
            };

            window.currentWikiPage = 0; 

            let wikiHtml = `
                <div class="wiki-navigation-panel">
                    <div class="wiki-filter-wrapper">
                        <label for="wiki-page-select"><i class="fa-solid fa-compass"></i> Mục Lục Hệ Thống: </label>
                        <select id="wiki-page-select" onchange="switchWikiPage(parseInt(this.value))">
                            <option value="0">📖 Trang Giới Thiệu Tổng Quan</option>
            `;

            const nameKey = headers.find(h => h.startsWith('ten_')) || headers[1] || headers[0];

            rows.forEach((row, idx) => {
                const dynamicTitle = row[nameKey] || `Bản ghi dòng ${idx + 1}`;
                wikiHtml += `<option value="${idx + 1}">📄 Bản ghi ${idx + 1}: ${dynamicTitle}</option>`;
            });

            wikiHtml += `
                        </select>
                    </div>

                    <div id="wiki-page-content-holder">
                        <div id="wiki-markdown-guide" class="wiki-page-fade dynamic-content"></div>
                        <div id="wiki-table-summary" class="wiki-page-fade dynamic-content"></div>
                        <div id="wiki-row-detail" class="wiki-page-fade dynamic-content" style="display: none;"></div>
                    </div>

                    <div class="wiki-pagination-bar">
                        <button id="btn-wiki-back" class="wiki-nav-btn" onclick="navigateWikiPage(-1)" disabled>
                            <i class="fa-solid fa-chevron-left"></i> Trang Trước
                        </button>
                        <span id="wiki-page-indicator" class="wiki-page-indicator">Trang Giới Thiệu</span>
                        <button id="btn-wiki-next" class="wiki-nav-btn" onclick="navigateWikiPage(1)">
                            Trang Sau <i class="fa-solid fa-chevron-right"></i>
                        </button>
                    </div>
                </div>
            `;

            document.getElementById('content-area').innerHTML = wikiHtml;

            // Kích hoạt nạp dữ liệu nền lần đầu tiên cho trang 0
            initTrangTongQuan(window.currentSystemData);
            switchWikiPage(0);
        })
        .catch(error => {
            document.getElementById('content-area').innerHTML = `
                <div class="wiki-error-container">
                    <h2><i class="fa-solid fa-circle-exclamation"></i> Lỗi Nạp Dữ Liệu</h2>
                    <p>${error.message}</p>
                </div>
            `;
        });
}

// Khối 4: Điều Hướng & Render Giao Diện (Rendering & Pagination)
// Chuyển đổi trạng thái hiển thị nội dung (Trang 0 VS Trang Chi Tiết)
// Hàm bổ trợ: Chỉ vẽ nội dung Hướng dẫn tĩnh cho Trang Tổng Quan
function initTrangTongQuan(data) {
    const mdGuide = document.getElementById('wiki-markdown-guide');
    const tableSummary = document.getElementById('wiki-table-summary');
    
    if (!mdGuide || !tableSummary) return;

    // 1. Đổ tài liệu hướng dẫn .md vào phân khu riêng
    if (data.intro) {
        mdGuide.innerHTML = `<div class="markdown-body">${marked.parse(data.intro)}</div>`;
    } else {
        // Nếu bảng mới tinh chưa có file template .md, hiển thị thông báo nhẹ nhàng
        mdGuide.innerHTML = `
            <div class="wiki-empty-template-box">
                <p class="wiki-empty-msg">💡 Hệ thống [${data.tableName}] chưa được thiết lập tài liệu hướng dẫn (Thiếu file .md).</p>
            </div>
        `;
    }

    // 2. Dọn sạch phân khu tableSummary (Vì chúng ta không muốn hiện toàn bộ bảng ở đây nữa)
    tableSummary.innerHTML = '';
}

// Hàm cốt lõi: Điều phối ẩn/hiện các phân khu khi chuyển mục lục
function switchWikiPage(targetPageIndex) {
    const data = window.currentSystemData;
    if (!data) return;

    window.currentWikiPage = targetPageIndex;
    const mdGuide = document.getElementById('wiki-markdown-guide');
    const tableSummary = document.getElementById('wiki-table-summary');
    const rowDetail = document.getElementById('wiki-row-detail');
    
    const selectDropdown = document.getElementById('wiki-page-select');
    const pageIndicator = document.getElementById('wiki-page-indicator');
    
    if (selectDropdown) selectDropdown.value = targetPageIndex;

    // TRANG 0: Chỉ hiện tài liệu hướng dẫn / Ẩn sạch sành sanh các phần dữ liệu động
    if (targetPageIndex === 0) {
        if (mdGuide) mdGuide.style.display = 'block';
        if (tableSummary) tableSummary.style.display = 'none'; // Khóa hẳn vùng chứa bảng
        if (rowDetail) rowDetail.style.display = 'none';
        
        pageIndicator.innerText = "Trang Giới Thiệu";

    // TRANG CHI TIẾT (>0): Ẩn hướng dẫn / Hiện hồ sơ văn bản của dòng được chọn
    } else {
        if (mdGuide) mdGuide.style.display = 'none';
        if (tableSummary) tableSummary.style.display = 'none';
        if (rowDetail) {
            rowDetail.style.display = 'block';
            
            const rowIndex = targetPageIndex - 1;
            const rowData = data.rows[rowIndex];
            const headers = data.headers;
            
            const nameKey = headers.find(h => h.startsWith('ten_')) || headers[1] || headers[0];
            const pageTitle = rowData[nameKey] || `Hàng dữ liệu số ${targetPageIndex}`;
            
            pageIndicator.innerText = `Trang ${targetPageIndex} / ${data.rows.length}`;

            let rowHtml = `
                <div class="wiki-document-container">
                    <h1 class="wiki-doc-title">${pageTitle}</h1>
                    <hr class="wiki-doc-hr">
            `;
            
            headers.forEach((header) => {
                if (header === 'stt' || header === nameKey) return; 

                let cellValue = rowData[header];
                if (cellValue === null || cellValue === undefined || cellValue === '') {
                    cellValue = `<span class="wiki-null-value-block">NULL (Trống)</span>`;
                }

                const sectionLabel = data.mapping[header] || header.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

                rowHtml += `
                    <div class="wiki-doc-section">
                        <h4 class="wiki-section-heading"><i class="fa-solid fa-caret-right"></i> ${sectionLabel}</h4>
                        <div class="wiki-section-content">${cellValue}</div>
                    </div>
                `;
            });

            rowHtml += `</div>`;
            rowDetail.innerHTML = rowHtml;
        }
    }

    document.getElementById('btn-wiki-back').disabled = (targetPageIndex === 0);
    document.getElementById('btn-wiki-next').disabled = (targetPageIndex === data.rows.length);
}

// Bấm nút Tăng/Giảm chỉ số trang (Giữ nguyên)
function navigateWikiPage(direction) {
    const nextTarget = window.currentWikiPage + direction;
    const data = window.currentSystemData;
    if (!data) return;

    if (nextTarget >= 0 && nextTarget <= data.rows.length) {
        switchWikiPage(nextTarget);
    }
}
