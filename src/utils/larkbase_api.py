import requests
import pandas as pd
import streamlit as st
import json
from typing import List, Dict, Any

class LarkbaseConfig:
    def __init__(self, app_id=None, app_secret=None, api_endpoint=None):
        self.app_id = app_id or 'cli_a7fab27260385010'
        self.app_secret = app_secret or 'Zg4MVcFfiOu0g09voTcpfd4WGDpA0Ly5'
        self.api_endpoint = api_endpoint or 'https://open.larksuite.com/open-apis'
    
    def to_dict(self):
        return {
            'app_id': self.app_id,
            'app_secret': self.app_secret,
            'api_endpoint': self.api_endpoint
        }

class LarkbaseAuthenticator:
    def __init__(self, config: LarkbaseConfig):
        self.config = config
    
    def authenticate(self):
        url = f"{self.config.api_endpoint}/auth/v3/tenant_access_token/internal"
        response = requests.post(url, json={
            'app_id': self.config.app_id, 
            'app_secret': self.config.app_secret
        })
        response.raise_for_status()
        data = response.json()
        if data.get('code') == 0:
            return data.get('tenant_access_token')
        return None

class LarkbaseDataFetcher:
    def __init__(self, access_token: str, config: LarkbaseConfig):
        self.access_token = access_token
        self.config = config
    
    def fetch_data(self, app_token: str, table_id: str):
        all_records = []
        page_token = None
        has_more = True
        while has_more:
            url = f"{self.config.api_endpoint}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            headers = {'Authorization': f'Bearer {self.access_token}'}
            params = {
                'page_size': 100,
                'page_token': page_token
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get('code') != 0:
                break
            records = response_data.get('data', {}).get('items', [])
            all_records.extend(records)
            has_more = response_data.get('data', {}).get('has_more', False)
            page_token = response_data.get('data', {}).get('page_token')
        return all_records

class LarkbaseDataWriter:
    def __init__(self, access_token: str, config: LarkbaseConfig):
        self.access_token = access_token
        self.config = config
    
    def write_data(self, app_token: str, table_id: str, records: List[Dict[str, Any]], batch_size: int = 100):
        """Ghi dữ liệu vào Larkbase theo batch với xử lý lỗi chi tiết.
        
        Args:
            app_token (str): Token của ứng dụng Larkbase.
            table_id (str): ID của bảng cần ghi dữ liệu.
            records (List[Dict[str, Any]]): Danh sách các bản ghi cần ghi.
            batch_size (int, optional): Kích thước mỗi batch. Mặc định là 100.
        
        Returns:
            tuple: (success_count, error_count, errors) - Số lượng bản ghi ghi thành công, thất bại và danh sách lỗi.
        """
        success_count = 0
        error_count = 0
        errors = []  # Khởi tạo danh sách để lưu trữ lỗi
        
        if not records:
            st.warning("⚠️ Không có bản ghi nào để ghi.")
            return success_count, error_count, errors
        
        # Chia records thành các batch nhỏ
        total_batches = (len(records) + batch_size - 1) // batch_size
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_number = i // batch_size + 1
            
            try:
                result = self._write_batch(app_token, table_id, batch)
                if result:
                    success_count += len(batch)
                    st.info(f"✅ Batch {batch_number}/{total_batches} ghi thành công {len(batch)} bản ghi.")
                else:
                    error_count += len(batch)
                    error_msg = f"Batch {batch_number}/{total_batches} thất bại, không có thông tin lỗi cụ thể từ hệ thống."
                    st.error(f"❌ {error_msg}")
                    errors.append(error_msg)  # Lưu thông báo lỗi vào danh sách
            except Exception as e:
                error_count += len(batch)
                error_msg = f"Lỗi khi ghi batch {batch_number}/{total_batches}: {str(e)}"
                st.error(f"❌ {error_msg}")
                errors.append(error_msg)  # Lưu thông báo lỗi vào danh sách
                # Ghi log chi tiết lỗi nếu cần
                st.error(f"Chi tiết batch lỗi: {batch[:2]}... (hiển thị tối đa 2 bản ghi đầu tiên)")
        
        # Báo cáo tổng kết
        st.info(f"📊 Tổng kết: {success_count} bản ghi thành công, {error_count} bản ghi thất bại.")
        return success_count, error_count, errors

    
    def _write_batch(self, app_token: str, table_id: str, records: List[Dict[str, Any]]):
        """Ghi một batch records vào Larkbase"""
        url = f"{self.config.api_endpoint}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Chuẩn bị dữ liệu theo format của Larkbase
        payload = {
            "records": [{"fields": record} for record in records]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        return response_data.get('code') == 0
    
    def update_data(self, app_token: str, table_id: str, record_id: str, fields: Dict[str, Any]):
        """Cập nhật một record cụ thể"""
        url = f"{self.config.api_endpoint}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {"fields": fields}
        
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        return response_data.get('code') == 0
    
    def delete_data(self, app_token: str, table_id: str, record_ids: List[str]):
        """Xóa nhiều records"""
        url = f"{self.config.api_endpoint}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {"records": record_ids}
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        return response_data.get('code') == 0

def fetch_larkbase_data(app_token, table_id, step_name):
    """Hàm lấy dữ liệu từ Larkbase, KHÔNG thêm _record_id vào DataFrame"""
    try:
        config = LarkbaseConfig()
        authenticator = LarkbaseAuthenticator(config)
        token = authenticator.authenticate()
        
        if not token:
            st.error("❌ Không thể xác thực với Larkbase")
            return None
        
        fetcher = LarkbaseDataFetcher(token, config)
        records = fetcher.fetch_data(app_token, table_id)
        
        if not records:
            st.warning("⚠️ Không có dữ liệu")
            return None
        
        # Chỉ lấy fields, KHÔNG thêm record_id
        data = [record.get('fields', {}).copy() for record in records]
        df = pd.DataFrame(data)
        
        st.success(f"✅ Đã đọc {len(df):,} bản ghi từ {step_name}")
        return df
        
    except Exception as e:
        st.error(f"❌ Lỗi khi đọc {step_name}: {str(e)}")
        return None

def clear_and_overwrite_table(app_token, table_id, new_data, step_name):
    """
    Xóa tất cả dữ liệu trong table và ghi đè bằng dữ liệu mới
    
    Args:
        app_token (str): Token của app
        table_id (str): ID của table
        new_data (pd.DataFrame): Dữ liệu mới để ghi đè
        step_name (str): Tên bước để hiển thị log
        
    Returns:
        dict: {"success": bool, "message": str}
    """

    try:
        config = LarkbaseConfig()
        authenticator = LarkbaseAuthenticator(config)
        token = authenticator.authenticate()
        if not token:
            return {"success": False, "message": "Không thể xác thực với Larkbase"}

        # Bước 1: Lấy tất cả record_ids hiện có
        fetcher = LarkbaseDataFetcher(token, config)
        existing_records = fetcher.fetch_data(app_token, table_id)
        if existing_records:
            record_ids = [record.get('record_id') for record in existing_records if record.get('record_id')]
            if record_ids:
                # Bước 2: Xóa tất cả records theo batch
                writer = LarkbaseDataWriter(token, config)
                batch_size = 100
                for i in range(0, len(record_ids), batch_size):
                    batch_ids = record_ids[i:i + batch_size]
                    success = writer.delete_data(app_token, table_id, batch_ids)
                    if not success:
                        return {"success": False, "message": f"Lỗi khi xóa batch {i//batch_size + 1}"}
                
                st.info(f"🗑️ Đã xóa {len(record_ids)} records cũ từ {step_name}")

        # Bước 3: Ghi dữ liệu mới
        if isinstance(new_data, pd.DataFrame):
            # Loại bỏ cột _record_id nếu có
            data_to_write = new_data.copy()
            if '_record_id' in data_to_write.columns:
                data_to_write = data_to_write.drop(columns=['_record_id'])
            
            records = data_to_write.to_dict('records')
        else:
            records = new_data
        
        # Loại bỏ các giá trị NaN/None
        cleaned_records = []
        for record in records:
            cleaned_record = {k: v for k, v in record.items() if pd.notna(v) and k != '_record_id'}
            cleaned_records.append(cleaned_record)
        
        if not cleaned_records:
            return {"success": False, "message": "Không có dữ liệu hợp lệ để ghi"}

        # Ghi dữ liệu mới
        writer = LarkbaseDataWriter(token, config)
        success_count, error_count, errors = writer.write_data(app_token, table_id, cleaned_records, 100)

        if error_count == 0:
            message = f"✅ Đã ghi đè thành công {success_count:,} bản ghi vào {step_name}"
            st.success(message)
            return {"success": True, "message": message}
        else:
            message = f"⚠️ Ghi đè {step_name}: {success_count:,} thành công, {error_count:,} lỗi"
            st.warning(message)
            return {"success": success_count > 0, "message": message}
        
    except Exception as e:
        error_msg = f"❌ Lỗi khi ghi đè {step_name}: {str(e)}"
        st.error(error_msg)
        return {"success": False, "message": error_msg}
