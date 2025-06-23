import streamlit as st
import pandas as pd
from src.utils.larkbase_api import fetch_larkbase_data, clear_and_overwrite_table
from src.utils.data_process import extract_categories_from_mixed_data, filter_data_by_category

def allocate_quantity_by_moh(df_category, df_products):
    if 'Số lượng cần' not in df_category.columns:
        st.error("❌ Không tìm thấy cột 'Số lượng cần' trong dữ liệu danh mục! Các cột hiện có: " + ', '.join(df_category.columns))
        return pd.DataFrame(), 0
    if 'Tổng lượng hàng' not in df_products.columns or 'SL bán' not in df_products.columns:
        st.error("❌ Thiếu cột 'Tổng lượng hàng' hoặc 'SL bán' trong danh sách sản phẩm!")
        return pd.DataFrame(), 0

    total_qty = df_category['Số lượng cần'].sum()
    df_products = df_products.copy()
    df_products['SL phân bổ'] = 0
    df_products['MOH'] = df_products['Tổng lượng hàng'] / df_products['SL bán']

    remaining_qty = total_qty
    while remaining_qty > 0:
        df_products = df_products.sort_values(['MOH', 'SL bán'], ascending=[True, False]).reset_index(drop=True)
        idx = df_products[(df_products['SL bán'] > 0)].index[0]
        df_products.at[idx, 'SL phân bổ'] += 1
        df_products.at[idx, 'Tổng lượng hàng'] += 1
        df_products.at[idx, 'MOH'] = df_products.at[idx, 'Tổng lượng hàng'] / df_products.at[idx, 'SL bán']
        remaining_qty -= 1

    df_products.drop(columns=['MOH'], inplace=True)
    return df_products, total_qty

# ================== UI ==================
st.markdown("""
<style>
.stButton>button {
    width: 100%;
    background: #ef5350;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px;
    font-weight: 500;
    font-size: 16px;
    font-family: 'Arial', sans-serif;
}
.stButton>button:hover {
    background: #d32f2f;
}
.success-box {
    background: #e8f5e8;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #4caf50;
    margin: 16px 0;
    font-family: 'Arial', sans-serif;
}
.info-box {
    background: #e3f2fd;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #2196f3;
    margin: 16px 0;
    font-family: 'Arial', sans-serif;
}
.category-box {
    background: #fff3e0;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #ff9800;
    margin: 16px 0;
    font-family: 'Arial', sans-serif;
}
.allocation-box {
    background: #f1f8e9;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #8bc34a;
    margin: 16px 0;
    font-family: 'Arial', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #1976d2, #42a5f5); color: white; border-radius: 8px; margin-bottom: 2rem; font-family: 'Arial', sans-serif;">
    <h1>📊 Phân bổ danh mục</h1>
    <p>Phân bổ số lượng danh mục ra các mã sản phẩm</p>
</div>
""", unsafe_allow_html=True)

# ========== Khởi tạo session state ==========
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df_inventory_overview' not in st.session_state:
    st.session_state.df_inventory_overview = None
if 'df_product_list' not in st.session_state:
    st.session_state.df_product_list = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'df_allocated' not in st.session_state:
    st.session_state.df_allocated = None
if 'total_allocated_qty' not in st.session_state:
    st.session_state.total_allocated_qty = 0

# ========== Bước 1: Tải danh mục ==========
if st.session_state.step >= 1:
    st.markdown("### 🎯 Bước 1: Chọn danh mục cần xử lý")
    st.markdown("*Chọn danh mục để lọc dữ liệu cho toàn bộ quy trình xử lý*")
    if st.session_state.df_inventory_overview is None:
        if st.button("📂 Tải danh sách danh mục", key="load_categories"):
            with st.spinner("Đang tải danh sách danh mục..."):
                df_raw_data = fetch_larkbase_data("At3fbwyI5a1Ps1srOpxlhkfqgVf", "tblcdexU1Gk6xHOD", "danh mục cần xử lý")
                if df_raw_data is not None:
                    st.session_state.df_inventory_overview = df_raw_data
                    st.rerun()
    else:
        if 'Mã danh mục' in st.session_state.df_inventory_overview.columns:
            categories = extract_categories_from_mixed_data(st.session_state.df_inventory_overview['Mã danh mục'])
            if categories:
                selected_category = st.selectbox(
                    "🏷️ Chọn danh mục:",
                    options=["-- Chọn danh mục --"] + categories,
                    key="category_selector",
                    index=0 if st.session_state.selected_category is None else (categories.index(st.session_state.selected_category) + 1 if st.session_state.selected_category in categories else 0)
                )
                if selected_category != "-- Chọn danh mục --":
                    if st.session_state.selected_category != selected_category:
                        st.session_state.selected_category = selected_category
                        st.session_state.df_product_list = None
                        st.session_state.df_allocated = None
                    df_category = filter_data_by_category(st.session_state.df_inventory_overview, 'Mã danh mục', selected_category)
                    st.markdown(f'<div class="category-box">🎯 <strong>Danh mục đã chọn</strong>: {selected_category}</div>', unsafe_allow_html=True)
                    
                    # Sắp xếp và chỉ hiện các cột mong muốn
                    columns_order = [
                        "Tên danh mục", "Mã danh mục", "Danh mục cha", "Số lượng cần", "Tổng lượng hàng",
                        "Tồn hiện tại", "Tồn chuyển kho", "SL sản xuất tái", "SL sản xuất mới",
                        "Target SL bán tháng hiện tại", "SL bán dự kiến tháng hiện tại", "SL bán tháng hiện tại"
                    ]
                    # Chỉ lấy các cột có trong DataFrame
                    columns_show = [col for col in columns_order if col in df_category.columns]
                    df_show = df_category.reindex(columns=columns_show)
                    with st.expander("📋 Xem bảng dữ liệu danh mục đã chọn", expanded=True):
                        st.dataframe(df_show, use_container_width=True, column_order=columns_show)
                    
                    # Chỉ hiện nút "Tiếp tục" nếu đang ở step 1
                    if st.session_state.step == 1:
                        if st.button("Tiếp tục ➡️", key="to_step2"):
                            st.session_state.step = 2
                            st.rerun()
                else:
                    st.session_state.selected_category = None
                    st.markdown('<div class="info-box">ℹ️ <strong>Vui lòng chọn danh mục để tiếp tục các bước tiếp theo</strong></div>', unsafe_allow_html=True)
            else:
                st.error("❌ Không tìm thấy danh mục nào trong dữ liệu!")
        else:
            st.error("❌ Không tìm thấy cột 'Mã danh mục' trong dữ liệu!")
            st.write("<b>Các cột có sẵn:</b>")
            st.write(list(st.session_state.df_inventory_overview.columns))

# ========== Bước 2: Đọc danh sách sản phẩm ==========
if st.session_state.step >= 2:
    st.markdown("### 📋 Bước 2: Đọc danh sách sản phẩm")
    st.markdown("*Danh sách chi tiết các sản phẩm và thông tin liên quan*")
    if st.session_state.df_product_list is None:
        if st.session_state.step == 2:
            if st.button("🔄 Đọc danh sách sản phẩm", key="step2"):
                with st.spinner("Đang đọc danh sách sản phẩm..."):
                    df_products = fetch_larkbase_data("At3fbwyI5a1Ps1srOpxlhkfqgVf", "tbliknLD9NJDtSeE", "danh sách sản phẩm")
                    if df_products is not None:
                        st.session_state.df_product_list = df_products
                        st.rerun()
    else:
        st.markdown(f'<div class="success-box">✅ <strong>Đã có danh sách sản phẩm</strong>: {len(st.session_state.df_product_list):,} sản phẩm</div>', unsafe_allow_html=True)
        with st.expander("👀 Xem danh sách sản phẩm"):
            st.dataframe(st.session_state.df_product_list[['Tên sản phẩm','Màu','MOH','SL bán','Tổng lượng hàng','Tồn hiện tại','Tồn chuyển kho','SL sản xuất tái','SL sản xuất mới','SL phân bổ','SL phân bổ điều chỉnh']].head(), use_container_width=True)
        if st.session_state.step == 2:
            if st.button("Tiếp tục ➡️", key="to_step3"):
                st.session_state.step = 3
                st.rerun()

# ========== Bước 3: Phân bổ số lượng ==========
if st.session_state.step >= 3:
    st.markdown("### 🎯 Bước 3: Phân bổ số lượng")
    st.markdown("*Phân bổ từng sản phẩm cho mã có MOH thấp nhất*")
    if st.session_state.df_allocated is None:
        if st.session_state.step == 3:
            if st.button("⚡ Thực hiện phân bổ số lượng", key="step3"):
                with st.spinner("Đang phân bổ số lượng..."):
                    df_filtered_alloc = filter_data_by_category(st.session_state.df_inventory_overview, 'Mã danh mục', st.session_state.selected_category)
                    df_allocated, total_qty = allocate_quantity_by_moh(df_filtered_alloc, st.session_state.df_product_list)
                    if not df_allocated.empty:
                        st.session_state.df_allocated = df_allocated
                        st.session_state.total_allocated_qty = total_qty
                        st.rerun()
    else:
        st.markdown(f'<div class="allocation-box">🎯 <strong>Phân bổ hoàn tất!</strong><br>• Tổng số lượng: {st.session_state.total_allocated_qty:,}<br>• Số sản phẩm: {len(st.session_state.df_allocated):,}<br>• Tổng sau phân bổ: {st.session_state.df_allocated["SL phân bổ"].sum():,}</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Tổng gốc", f"{st.session_state.total_allocated_qty:,}")
        with col2:
            st.metric("📦 Tổng phân bổ", f"{st.session_state.df_allocated['SL phân bổ'].sum():,}")
        with col3:
            st.metric("📈 Trung bình", f"{st.session_state.df_allocated['SL phân bổ'].mean():.1f}")
        with col4:
            min_qty = st.session_state.df_allocated['SL phân bổ'].min()
            max_qty = st.session_state.df_allocated['SL phân bổ'].max()
            st.metric("📊 Min-Max", f"{min_qty}-{max_qty}")

        with st.expander("📋 Xem kết quả phân bổ chi tiết", expanded=True):
            st.dataframe(st.session_state.df_allocated.head(), use_container_width=True)
        
        #csv = st.session_state.df_allocated.to_csv(index=False, encoding='utf-8-sig')
        #st.download_button(label="💾 Tải xuống kết quả (CSV)", data=csv, file_name=f"phan_bo_san_pham_{st.session_state.selected_category}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

        if st.session_state.step == 3:
            if st.button("Tiếp tục ➡️", key="to_step4"):
                st.session_state.step = 4
                st.rerun()

# ========== Bước 4: Ghi kết quả ==========
if st.session_state.step >= 4:
    st.markdown("### ✍️ Bước 4: Ghi kết quả vào Larkbase")
    st.markdown("*Lưu ý: Hành động này sẽ **xóa toàn bộ dữ liệu cũ** trong bảng đích và thay thế bằng dữ liệu mới.*")
    TARGET_APP_TOKEN = "At3fbwyI5a1Ps1srOpxlhkfqgVf"
    TARGET_TABLE_ID = "tbliknLD9NJDtSeE"
    if st.button("🚀 Ghi đè kết quả vào Larkbase", key="write_to_larkbase"):
        df_to_write = st.session_state.df_allocated
        if df_to_write is not None and not df_to_write.empty:
            with st.spinner(f"Đang ghi đè dữ liệu vào bảng {TARGET_TABLE_ID}..."):
                result = clear_and_overwrite_table(
                    app_token=TARGET_APP_TOKEN,
                    table_id=TARGET_TABLE_ID,
                    new_data=df_to_write,
                    step_name=f"Kết quả phân bổ ({st.session_state.selected_category})"
                )
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                else:
                    st.error(f"❌ {result['message']}")
        else:
            st.error("❌ Không có dữ liệu phân bổ để ghi. Vui lòng thực hiện lại Bước 3.")
