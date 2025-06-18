import streamlit as st

def load_material_ui_css():
    """Load Material UI inspired CSS styles"""
    st.markdown("""
    <style>
    /* Import Material Design Icons and Roboto Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    
    /* Global Styles */
    .main {
        padding: 1rem 2rem;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Material Card Style */
    .material-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 24px;
        margin: 16px 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Material Button Styles */
    .material-button {
        background: #1976d2;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 12px 24px;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .material-button:hover {
        background: #1565c0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .material-button-outlined {
        background: transparent;
        color: #1976d2;
        border: 1px solid #1976d2;
    }
    
    .material-button-outlined:hover {
        background: rgba(25, 118, 210, 0.04);
    }
    
    /* Step Indicator */
    .step-container {
        display: flex;
        align-items: center;
        margin: 20px 0;
        padding: 16px;
        background: #f5f5f5;
        border-radius: 8px;
        border-left: 4px solid #1976d2;
    }
    
    .step-number {
        background: #1976d2;
        color: white;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 500;
        margin-right: 16px;
        font-size: 14px;
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-title {
        font-weight: 500;
        font-size: 16px;
        color: #212121;
        margin: 0 0 4px 0;
    }
    
    .step-description {
        color: #757575;
        font-size: 14px;
        margin: 0;
    }
    
    /* Progress Bar */
    .progress-container {
        background: #e0e0e0;
        border-radius: 4px;
        height: 8px;
        margin: 16px 0;
        overflow: hidden;
    }
    
    .progress-bar {
        background: #4caf50;
        height: 100%;
        transition: width 0.3s ease;
        border-radius: 4px;
    }
    
    /* Alert Styles */
    .alert {
        padding: 16px;
        border-radius: 4px;
        margin: 16px 0;
        display: flex;
        align-items: center;
    }
    
    .alert-success {
        background: #e8f5e8;
        color: #2e7d32;
        border-left: 4px solid #4caf50;
    }
    
    .alert-warning {
        background: #fff3e0;
        color: #f57c00;
        border-left: 4px solid #ff9800;
    }
    
    .alert-error {
        background: #ffebee;
        color: #c62828;
        border-left: 4px solid #f44336;
    }
    
    .alert-info {
        background: #e3f2fd;
        color: #1565c0;
        border-left: 4px solid #2196f3;
    }
    
    /* Data Table Styles */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .dataframe thead th {
        background: #f5f5f5 !important;
        color: #424242 !important;
        font-weight: 500 !important;
        border: none !important;
        padding: 12px !important;
    }
    
    .dataframe tbody td {
        border: none !important;
        padding: 12px !important;
        border-bottom: 1px solid #e0e0e0 !important;
    }
    
    /* File Upload Area */
    .uploadedFile {
        border: 2px dashed #1976d2;
        border-radius: 8px;
        padding: 24px;
        text-align: center;
        background: #f8f9fa;
        margin: 16px 0;
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Metric Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #1976d2;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1976d2;
        margin: 8px 0;
    }
    
    .metric-label {
        color: #757575;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

def create_step_indicator(step_number, title, description, is_active=False, is_completed=False):
    """Create a material design step indicator"""
    if is_completed:
        icon = "✓"
        bg_color = "#4caf50"
    elif is_active:
        icon = str(step_number)
        bg_color = "#1976d2"
    else:
        icon = str(step_number)
        bg_color = "#bdbdbd"
    
    return f"""
    <div class="step-container" style="{'border-left-color: #4caf50' if is_completed else 'border-left-color: #1976d2' if is_active else 'border-left-color: #bdbdbd'}">
        <div class="step-number" style="background: {bg_color}">
            {icon}
        </div>
        <div class="step-content">
            <div class="step-title">{title}</div>
            <div class="step-description">{description}</div>
        </div>
    </div>
    """

def create_alert(message, alert_type="info"):
    """Create material design alert"""
    return f"""
    <div class="alert alert-{alert_type}">
        <span class="material-icons" style="margin-right: 12px;">
            {'check_circle' if alert_type == 'success' else 'warning' if alert_type == 'warning' else 'error' if alert_type == 'error' else 'info'}
        </span>
        {message}
    </div>
    """

def create_metric_card(value, label, color="#1976d2"):
    """Create material design metric card"""
    return f"""
    <div class="metric-card" style="border-left-color: {color}">
        <div class="metric-value" style="color: {color}">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def get_material_ui_styles():
    """Trả về CSS styles cho Material UI"""
    return """
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
    """
