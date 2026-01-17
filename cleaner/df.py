import pandas as pd
import re

def df_manager(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuẩn hóa DataFrame trước khi xử lý sâu hơn hoặc upload (Standardization Layer).
    
    Chức năng:
    1. Chuẩn hóa tên cột (Snake_case, xóa ký tự lạ).
    2. Ép kiểu dữ liệu (tránh lỗi mixed types khi lưu Parquet).
    3. Xóa dữ liệu rác (trùng lặp hoàn toàn).
    """

    # --- 1. Defensive Coding (Phòng thủ ngay từ đầu) ---
    if df is None:
        raise ValueError("Lỗi: Input DataFrame là None.")
    
    if df.empty:
        print("⚠️ Cảnh báo: DataFrame rỗng. Bỏ qua các bước xử lý.")
        return df

    # Tạo bản sao để tránh "SettingWithCopyWarning" và không làm hỏng biến gốc bên ngoài
    processed_df = df.copy()

    # --- 2. Chuẩn hóa tên cột (Column Name Normalization) ---
    # Nguyên tắc: Chuyển hết về lowercase để mapping với Postgres (jobId -> jobid)
    new_columns = []
    for col in processed_df.columns:
        # 1. Chuyển về chữ thường
        clean_col = str(col).strip().lower()
        # 2. Thay khoảng trắng bằng _ (nếu có), giữ lại a-z, 0-9, _
        clean_col = clean_col.replace(' ', '_')
        clean_col = re.sub(r'[^a-z0-9_]', '', clean_col)
        
        new_columns.append(clean_col)
    
    processed_df.columns = new_columns

    # --- 3. Ổn định kiểu dữ liệu (Type Enforcement) ---
    # Đây là bước QUAN TRỌNG NHẤT nếu bạn lưu file Parquet.
    # Parquet rất ghét cột 'object' chứa lẫn lộn số và chữ (mixed types).
    
    # Lấy danh sách các cột object (thường là string hoặc mixed)
    object_cols = processed_df.select_dtypes(include=['object']).columns
    
    for col in object_cols:
        # Ép về string hết để an toàn. 
        # Lưu ý: 'nan' (float) sẽ thành chuỗi 'nan', cần xử lý nếu muốn.
        # processed_df[col] = processed_df[col].astype(str)
        # SỬA LỖI: Chỉ ép kiểu string nhẹ nhàng, và quan trọng nhất:
        # Biến chuỗi 'None', 'nan' quay về None thực sự để Postgres hiểu là NULL
        
        processed_df[col] = processed_df[col].astype(str).replace({'None': None, 'nan': None, 'NaN': None})

    # --- 4. Loại bỏ trùng lặp (Deduplication) ---
    # Chỉ xóa nếu TRÙNG KHỚP HOÀN TOÀN tất cả các cột.
    before_count = len(processed_df)
    processed_df = processed_df.drop_duplicates()
    after_count = len(processed_df)

    if before_count != after_count:
        print(f"🧹 Đã dọn dẹp {before_count - after_count} dòng trùng lặp.")

    # --- 5. Kiểm tra cuối (Final Sanity Check) ---
    print(f"✅ df_manager completed. Shape: {processed_df.shape}")
    print(f"   Columns: {list(processed_df.columns[:5])} ...") # Print 5 cột đầu check chơi

    return processed_df