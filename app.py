import streamlit as st
import pandas as pd
from src.utils.larkbase_api import fetch_larkbase_data, clear_and_overwrite_table
from src.utils.data_process import extract_categories_from_mixed_data, filter_data_by_category, allocate_quantity_evenly

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
.debug-box {
    background: #f3e5f5;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #9c27b0;
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

# Header
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #1976d2, #42a5f5); color: white; border-radius: 8px; margin-bottom: 2rem; font-family: 'Arial', sans-serif;">
    <h1>📊 Điều chuyển tồn kho</h1>
    <p>Điều chuyển hàng hóa của kế toán</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
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





# Bước đầu tiên: Chọn danh mục (luôn hiển thị)
st.markdown("### 🎯 Chọn danh mục cần xử lý")
st.markdown("*Chọn danh mục để lọc dữ liệu cho toàn bộ quy trình xử lý*")
if st.session_state.df_inventory_overview is None:
    if st.button("📂 Tải danh sách danh mục", key="load_categories"):
        with st.spinner("Đang tải danh sách danh mục..."):
            df_raw_data = fetch_larkbase_data("FyZCbpeEeadrkPs9HdilScCbgUh", "tbl9S5oR7lvJW119", "tồn kho tổng quan")
            if df_raw_data is not None:
                st.session_state.df_inventory_overview = df_raw_data
                st.rerun()
else:
    with st.expander("🔍 Debug - Kiểm tra cấu trúc dữ liệu", expanded=False):
        if 'tên danh mục' in st.session_state.df_inventory_overview.columns:
            first_value = st.session_state.df_inventory_overview['tên danh mục'].iloc[0]
            st.markdown(f'<div class="debug-box"><b>Giá trị đầu tiên</b>: {first_value}<br><b>Kiểu dữ liệu</b>: {type(first_value)}</div>', unsafe_allow_html=True)
            st.write("<b>5 giá trị đầu tiên:</b>")
            for i in range(min(5, len(st.session_state.df_inventory_overview))):
                value = st.session_state.df_inventory_overview['tên danh mục'].iloc[i]
                st.write(f"{i+1}. {type(value).__name__}: {value}")
    
    if 'tên danh mục' in st.session_state.df_inventory_overview.columns:
        try:
            categories = extract_categories_from_mixed_data(st.session_state.df_inventory_overview['tên danh mục'])
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
                        st.session_state.step = 2
                        st.session_state.df_product_list = None
                        st.session_state.df_allocated = None
                        st.rerun()
                    st.markdown(f'<div class="category-box">🎯 <strong>Danh mục đã chọn</strong>: {selected_category}</div>', unsafe_allow_html=True)
                    df_category = filter_data_by_category(st.session_state.df_inventory_overview, 'tên danh mục', selected_category)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Số bản ghi", len(df_category))
                    with col2:
                        total_qty = df_category['số lượng'].sum() if 'số lượng' in df_category.columns else "N/A"
                        st.metric("📦 Tổng số lượng", f"{total_qty:,}" if isinstance(total_qty, (int, float)) else total_qty)
                    with col3:
                        unique_stores = df_category.iloc[:, 0].nunique() if len(df_category) > 0 else 0
                        st.metric("🏪 Số cửa hàng", unique_stores)
                else:
                    st.session_state.selected_category = None
                    st.markdown('<div class="info-box">ℹ️ <strong>Vui lòng chọn danh mục để tiếp tục các bước tiếp theo</strong></div>', unsafe_allow_html=True)
            else:
                st.error("❌ Không tìm thấy danh mục nào trong dữ liệu!")
        except Exception as e:
            st.error(f"❌ Lỗi khi xử lý danh mục: {str(e)}")
            st.write("<b>Dữ liệu mẫu để debug:</b>")
            st.write(st.session_state.df_inventory_overview['tên danh mục'].head())
    else:
        st.error("❌ Không tìm thấy cột 'tên danh mục' trong dữ liệu!")
        st.write("<b>Các cột có sẵn:</b>")
        st.write(list(st.session_state.df_inventory_overview.columns))

st.markdown("---")

if st.session_state.selected_category is not None:
    # Step 1: Xem dữ liệu tổng quan
    st.markdown("### 📊 Bước 1: Xem dữ liệu tổng quan tồn kho")
    st.markdown("*Dữ liệu tổng quan đã được lọc theo danh mục bạn chọn*")
    df_filtered = filter_data_by_category(st.session_state.df_inventory_overview, 'tên danh mục', st.session_state.selected_category)
    st.markdown(f'<div class="success-box">✅ <strong>Dữ liệu tổng quan tồn kho</strong> (đã lọc theo danh mục "{st.session_state.selected_category}"): {len(df_filtered):,} bản ghi</div>', unsafe_allow_html=True)
    with st.expander("👀 Xem dữ liệu tổng quan (đã lọc)", expanded=True):
        if not df_filtered.empty:
            st.dataframe(df_filtered, use_container_width=True)
        else:
            st.warning("⚠️ Không có dữ liệu nào khớp với danh mục đã chọn!")

    # Step 2: Đọc danh sách sản phẩm
    if st.session_state.step >= 2:
        st.markdown("### 📋 Bước 2: Đọc danh sách sản phẩm")
        st.markdown("*Danh sách chi tiết các sản phẩm và thông tin liên quan*")
        if st.session_state.df_product_list is None:
            if st.button("🔄 Đọc danh sách sản phẩm", key="step2"):
                with st.spinner("Đang đọc danh sách sản phẩm..."):
                    df_products = fetch_larkbase_data("FyZCbpeEeadrkPs9HdilScCbgUh", "tbl7d7B1t3e6ehRS", "danh sách sản phẩm")
                    if df_products is not None:
                        st.session_state.df_product_list = df_products
                        st.session_state.step = 3
                        st.rerun()
        else:
            st.markdown(f'<div class="success-box">✅ <strong>Đã có danh sách sản phẩm</strong>: {len(st.session_state.df_product_list):,} sản phẩm</div>', unsafe_allow_html=True)
            with st.expander("👀 Xem danh sách sản phẩm"):
                st.dataframe(st.session_state.df_product_list.head(), use_container_width=True)

    # Step 3: Phân bổ số lượng
    if st.session_state.step >= 3:
        st.markdown("### 🎯 Bước 3: Phân bổ số lượng bán dự kiến 6/2025")
        st.markdown("*Chia đều tổng số lượng bán dự kiến cho tất cả sản phẩm*")
        if st.session_state.df_allocated is None:
            if st.button("⚡ Thực hiện phân bổ số lượng", key="step3"):
                with st.spinner("Đang phân bổ số lượng..."):
                    df_filtered_alloc = filter_data_by_category(st.session_state.df_inventory_overview, 'tên danh mục', st.session_state.selected_category)
                    df_allocated, total_qty = allocate_quantity_evenly(df_filtered_alloc, st.session_state.df_product_list)
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
                st.dataframe(st.session_state.df_allocated, use_container_width=True)
            
            csv = st.session_state.df_allocated.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(label="💾 Tải xuống kết quả (CSV)", data=csv, file_name=f"phan_bo_san_pham_{st.session_state.selected_category}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

    # Step 4: Ghi kết quả (CHỈ HIỂN THỊ SAU KHI BƯỚC 3 HOÀN TẤT)
    if st.session_state.step >= 3 and st.session_state.df_allocated is not None:
        st.markdown("---")
        st.markdown("### ✍️ Bước 4: Ghi kết quả vào Larkbase")
        st.markdown("*Lưu ý: Hành động này sẽ **xóa toàn bộ dữ liệu cũ** trong bảng đích và thay thế bằng dữ liệu mới.*")

        TARGET_APP_TOKEN = "FyZCbpeEeadrkPs9HdilScCbgUh"
        TARGET_TABLE_ID = "tbl3YC4Pyt3rTdaq"

        if st.button("🚀 Ghi đè kết quả vào Larkbase", key="write_to_larkbase"):
            df_to_write = st.session_state.df_allocated
            # Kiểm tra chắc chắn rằng df_to_write không phải là None trước khi ghi
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
        
        # Phần các bước tiếp theo
        st.markdown("### 🚀 Các bước tiếp theo")
        st.markdown("*Dữ liệu đã sẵn sàng cho các phân tích và xử lý nâng cao...*")
        st.markdown("- 📊 Phân tích chi tiết theo từng sản phẩm")
        st.markdown("- 🎯 Tối ưu hóa phân bổ theo tiêu chí khác")
        st.markdown("- 📈 Dự báo nhu cầu và lập kế hoạch")

else:
    st.markdown('<div class="info-box">⚠️ <strong>Vui lòng tải danh sách danh mục và chọn danh mục ở trên để bắt đầu quy trình xử lý</strong></div>', unsafe_allow_html=True)
