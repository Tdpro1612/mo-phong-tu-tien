import sqlite3


def khoi_tao_database():
    # Chỉ kết nối để SQLite tự đẻ ra file vật lý trống trên ổ cứng
    conn = sqlite3.connect("database/game_tu_tien.db")
    conn.commit()
    conn.close()
    print("🎉 Tạo file 'game_tu_tien.db' trống thành công!")


if __name__ == "__main__":
    khoi_tao_database()
