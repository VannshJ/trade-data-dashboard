"""
Trade Data Intelligence Dashboard
Interactive Streamlit application for visualizing UN Comtrade data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os
from datetime import datetime

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from config import *
from database_manager import DatabaseManager

# Page configuration
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .filter-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class TradeDashboard:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.load_reference_data()
    
    def load_reference_data(self):
        """Load reference data for filters"""
        self.countries_df = self.db_manager.get_countries()
        self.hs_codes_df = self.db_manager.get_hs_codes()
        
        # Create country mapping
        if not self.countries_df.empty:
            self.country_mapping = dict(zip(self.countries_df['code'], self.countries_df['name']))
        else:
            self.country_mapping = {}
        
        # Create HS code mapping
        if not self.hs_codes_df.empty:
            self.hs_mapping = dict(zip(self.hs_codes_df['code'], self.hs_codes_df['description']))
        else:
            self.hs_mapping = HS_CATEGORIES
    
    def render_header(self):
        """Render dashboard header"""
        st.markdown(f'<div class="main-header">{DASHBOARD_TITLE}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">{DASHBOARD_SUBTITLE}</div>', unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render sidebar with filters"""
        st.sidebar.markdown("### 🔍 Filters")
        
        # Get available data for filters
        trade_data = self.db_manager.get_trade_data()
        
        if trade_data.empty:
            st.sidebar.warning("No data available. Please run data extraction first.")
            return {}
        
        # Year filter
        available_years = sorted(trade_data['year'].dropna().unique(), reverse=True)
        selected_year = st.sidebar.selectbox(
            "📅 Year",
            options=[None] + available_years,
            format_func=lambda x: "All Years" if x is None else str(int(x))
        )
        
        # Reporter country filter
        available_reporters = sorted(trade_data['reporter_code'].unique())
        reporter_options = {code: self.country_mapping.get(code, code) for code in available_reporters}
        selected_reporter = st.sidebar.selectbox(
            "🏳️ Reporter Country",
            options=[None] + available_reporters,
            format_func=lambda x: "All Countries" if x is None else reporter_options.get(x, x)
        )
        
        # Partner country filter
        available_partners = sorted(trade_data['partner_code'].unique())
        partner_options = {code: self.country_mapping.get(code, code) for code in available_partners}
        selected_partner = st.sidebar.selectbox(
            "🤝 Partner Country",
            options=[None] + available_partners,
            format_func=lambda x: "All Partners" if x is None else partner_options.get(x, x)
        )
        
        # Trade flow filter
        available_flows = trade_data['trade_flow'].unique()
        selected_flow = st.sidebar.selectbox(
            "📈 Trade Flow",
            options=[None] + list(available_flows),
            format_func=lambda x: "All Flows" if x is None else x
        )
        
        # HS Code filter
        available_hs = sorted([code for code in trade_data['hs_code'].unique() if code and len(str(code)) <= 4])
        selected_hs = st.sidebar.selectbox(
            "📦 HS Code Category",
            options=[None] + available_hs,
            format_func=lambda x: "All Categories" if x is None else f"{x} - {self.hs_mapping.get(x, 'Unknown')}"
        )
        
        return {
            'year': selected_year,
            'reporter_code': selected_reporter,
            'partner_code': selected_partner,
            'trade_flow': selected_flow,
            'hs_code': selected_hs
        }
    
    def render_summary_metrics(self, filtered_data, filters):
        """Render summary metrics"""
        st.markdown("### 📊 Summary Metrics")
        
        if filtered_data.empty:
            st.warning("No data available for selected filters.")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_records = len(filtered_data)
            st.metric("Total Records", f"{total_records:,}")
        
        with col2:
            total_value = filtered_data['trade_value'].sum()
            st.metric("Total Trade Value", f"${total_value/1e9:.2f}B")
        
        with col3:
            unique_countries = filtered_data['reporter_code'].nunique()
            st.metric("Countries", unique_countries)
        
        with col4:
            unique_products = filtered_data['hs_code'].nunique()
            st.metric("Product Categories", unique_products)
    
    def render_trade_value_chart(self, filtered_data):
        """Render trade value visualization"""
        st.markdown("### 💰 Trade Value Analysis")
        
        if filtered_data.empty:
            st.warning("No data available for visualization.")
            return
        
        # Trade value by year
        if 'year' in filtered_data.columns:
            yearly_data = filtered_data.groupby(['year', 'trade_flow'])['trade_value'].sum().reset_index()
            
            if not yearly_data.empty:
                fig = px.line(
                    yearly_data,
                    x='year',
                    y='trade_value',
                    color='trade_flow',
                    title='Trade Value Trends Over Time',
                    labels={'trade_value': 'Trade Value (USD)', 'year': 'Year'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_top_traders_chart(self, filtered_data):
        """Render top traders visualization"""
        st.markdown("### 🏆 Top Trading Partners")
        
        if filtered_data.empty:
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top reporters
            top_reporters = (filtered_data.groupby('reporter_name')['trade_value']
                           .sum().sort_values(ascending=False).head(10))
            
            if not top_reporters.empty:
                fig = px.bar(
                    x=top_reporters.values,
                    y=top_reporters.index,
                    orientation='h',
                    title='Top Reporter Countries',
                    labels={'x': 'Trade Value (USD)', 'y': 'Country'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top partners
            top_partners = (filtered_data.groupby('partner_name')['trade_value']
                          .sum().sort_values(ascending=False).head(10))
            
            if not top_partners.empty:
                fig = px.bar(
                    x=top_partners.values,
                    y=top_partners.index,
                    orientation='h',
                    title='Top Partner Countries',
                    labels={'x': 'Trade Value (USD)', 'y': 'Country'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_product_analysis(self, filtered_data):
        """Render product category analysis"""
        st.markdown("### 📦 Product Category Analysis")
        
        if filtered_data.empty:
            return
        
        # Top products by trade value
        product_data = (filtered_data.groupby(['hs_code', 'hs_description'])['trade_value']
                       .sum().sort_values(ascending=False).head(15))
        
        if not product_data.empty:
            # Create labels with HS code and description
            labels = [f"{idx[0]} - {idx[1][:30]}..." if len(idx[1]) > 30 else f"{idx[0]} - {idx[1]}" 
                     for idx in product_data.index]
            
            fig = px.pie(
                values=product_data.values,
                names=labels,
                title='Trade Value Distribution by Product Category',
                height=500
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    def render_trade_flow_comparison(self, filtered_data):
        """Render import vs export comparison"""
        st.markdown("### ⚖️ Import vs Export Analysis")
        
        if filtered_data.empty:
            return
        
        # Trade flow comparison
        flow_data = filtered_data.groupby('trade_flow')['trade_value'].sum()
        
        if not flow_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    values=flow_data.values,
                    names=flow_data.index,
                    title='Trade Value by Flow Direction'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Monthly trends if data available
                if 'month' in filtered_data.columns:
                    monthly_data = (filtered_data.groupby(['month', 'trade_flow'])['trade_value']
                                  .sum().reset_index())
                    
                    if not monthly_data.empty:
                        fig = px.bar(
                            monthly_data,
                            x='month',
                            y='trade_value',
                            color='trade_flow',
                            title='Monthly Trade Value Trends',
                            labels={'trade_value': 'Trade Value (USD)', 'month': 'Month'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    def render_data_table(self, filtered_data):
        """Render detailed data table"""
        st.markdown("### 📋 Detailed Trade Data")
        
        if filtered_data.empty:
            st.warning("No data available.")
            return
        
        # Select and format columns for display
        display_columns = [
            'year', 'reporter_name', 'partner_name', 'trade_flow',
            'hs_code', 'hs_description', 'trade_value', 'quantity', 'unit'
        ]
        
        # Filter columns that exist in the data
        available_columns = [col for col in display_columns if col in filtered_data.columns]
        display_data = filtered_data[available_columns].copy()
        
        # Format trade value
        if 'trade_value' in display_data.columns:
            display_data['trade_value'] = display_data['trade_value'].apply(
                lambda x: f"${x:,.2f}" if pd.notnull(x) else "N/A"
            )
        
        # Format quantity
        if 'quantity' in display_data.columns:
            display_data['quantity'] = display_data['quantity'].apply(
                lambda x: f"{x:,.2f}" if pd.notnull(x) else "N/A"
            )
        
        # Show data with pagination
        st.dataframe(
            display_data.head(1000),  # Limit to first 1000 rows for performance
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv_data = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv_data,
            file_name=f"trade_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def render_dashboard(self):
        """Main dashboard rendering function"""
        self.render_header()
        
        # Get filters from sidebar
        filters = self.render_sidebar()
        
        # Get filtered data
        filtered_data = self.db_manager.get_trade_data(filters)
        
        # Render main content
        self.render_summary_metrics(filtered_data, filters)
        
        # Charts and visualizations
        self.render_trade_value_chart(filtered_data)
        self.render_top_traders_chart(filtered_data)
        self.render_product_analysis(filtered_data)
        self.render_trade_flow_comparison(filtered_data)
        
        # Data table
        self.render_data_table(filtered_data)
        
        # Footer
        st.markdown("---")
        st.markdown("*Data source: UN Comtrade Database via UN Comtrade API*")
        st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

def main():
    """Main application function"""
    try:
        dashboard = TradeDashboard()
        dashboard.render_dashboard()
        
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        st.info("Please ensure the database is initialized and contains data.")
        st.info("Run the data extractor first: `python data_extractor.py`")

if __name__ == "__main__":
    main()