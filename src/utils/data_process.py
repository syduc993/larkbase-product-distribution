# Hàm phân bổ số lượng đều cho các sản phẩm
def allocate_quantity_evenly(df_filtered, df_products, qty_column='SL bán dự kiến 6/2025'):
    """
    Phân bổ đều số lượng từ df_filtered cho các sản phẩm trong df_products
    Đảm bảo: nguyên dương, tổng chính xác, phân bổ công bằng
    """
    # Lấy tổng số lượng
    if qty_column in df_filtered.columns:
        total_qty = int(df_filtered[qty_column].sum())
    else:
        total_qty = 0
    
    num_products = len(df_products)
    
    if num_products > 0 and total_qty > 0:
        base = total_qty // num_products
        remainder = total_qty % num_products
        
        qty_list = [base] * num_products
        
        for i in range(remainder):
            qty_list[i] += 1
        
        for i in range(num_products):
            if qty_list[i] < 1:
                qty_list[i] = 1
        
        diff = sum(qty_list) - total_qty
        while diff > 0:
            for i in range(num_products-1, -1, -1):
                if qty_list[i] > 1 and diff > 0:
                    qty_list[i] -= 1
                    diff -= 1
                if diff == 0:
                    break
        
        df_result = df_products.copy()
        df_result['SL phân bổ'] = qty_list
        
        return df_result, total_qty
    else:
        df_result = df_products.copy()
        df_result['SL phân bổ'] = 0
        return df_result, 0


# Hàm xử lý danh mục từ list hoặc string
def extract_categories_from_mixed_data(series):
    categories = set()
    for item in series.dropna():
        if isinstance(item, list):
            for sub_item in item:
                if sub_item and str(sub_item).strip():
                    categories.add(str(sub_item).strip())
        elif isinstance(item, str) and item.strip():
            categories.add(item.strip())
        elif item and str(item).strip():
            categories.add(str(item).strip())
    return sorted(list(categories))


def filter_data_by_category(df, category_column, selected_category):
    def category_matches(row_value, target_category):
        if isinstance(row_value, list):
            return target_category in [str(x).strip() for x in row_value]
        elif isinstance(row_value, str):
            return row_value.strip() == target_category
        else:
            return str(row_value).strip() == target_category
    mask = df[category_column].apply(lambda x: category_matches(x, selected_category))
    return df[mask].copy()