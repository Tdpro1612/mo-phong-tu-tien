// Khởi tạo các biến global và đồng bộ dữ liệu URL cho toàn bộ các module JS khác
let currentTable = "";
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('user_id') || 0;

// Bộ nhớ đệm toàn cục dùng chung để đối chiếu dữ liệu giữa các file JS
let currentColumns = []; 
let currentMainRows = [];
let editingRowId = null;

// Hàm lưu cập nhật phân quyền nhân sự (Giữ nguyên nghiệp vụ gốc của bạn)
async function saveUserPermission(btn) {
    const targetUserId = btn.getAttribute('data-id');
    const newRole = document.getElementById(`role-select-${targetUserId}`).value;
    const checkboxes = document.querySelectorAll(`input[name="perms-${targetUserId}"]:checked`);
    const selectedSystems = Array.from(checkboxes).map(cb => cb.value);
    const currentRole = urlParams.get('role') || 'viewer';
    
    try {
        const response = await fetch(`/dashboard/api/save-permissions?role=${currentRole}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: targetUserId,
                role: newRole,
                systems: selectedSystems
            })
        });
        
        const result = await response.json();
        if (response.ok) {
            alert("🔮 Thiên Cơ Lục sắc lệnh: " + result.message);
            window.location.reload();
        } else {
            throw new Error(result.detail || "Lỗi lưu phân quyền");
        }
    } catch (err) { alert("❌ Thất bại: " + err.message); }
}

function addNewRow() { 
    alert(`Ghi nhận lệnh khởi tạo dòng tạm mới trên bảng [${currentTable}]`); 
}
