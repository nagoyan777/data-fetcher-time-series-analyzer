#!/usr/bin/env python3
"""
Navigation Utility - Shared Navigation Bar
Provides navigation links between all apps in the multi-app system
"""
import panel as pn

def create_navigation_bar(current_app=None):
    """Create navigation bar with links to all apps"""

    # Define app information
    apps = {
        'data_fetcher': {
            'name': '📥 Data Fetcher',
            'port': 5006,
            'description': 'Configure and trigger data collection'
        },
        'time_series_analyzer': {
            'name': '📈 Time Series Analyzer',
            'port': 5007,
            'description': 'Visualize and analyze collected data'
        },
        'data_manager': {
            'name': '💾 Data Manager',
            'port': 5008,
            'description': 'Browse, backup, and export data'
        },
        'update_controller': {
            'name': '⚡ Update Controller',
            'port': 5009,
            'description': 'Manage manual triggers and schedules'
        }
    }

    # Create navigation links
    nav_links = []
    for app_key, app_info in apps.items():
        if app_key == current_app:
            # Current app - highlighted
            nav_links.append(f"""
                <span style="
                    background: rgba(255,255,255,0.3);
                    padding: 8px 12px;
                    border-radius: 4px;
                    color: #fff;
                    font-weight: bold;
                    border: 2px solid rgba(255,255,255,0.5);
                ">
                    {app_info['name']} (Current)
                </span>
            """)
        else:
            # Other apps - clickable links
            nav_links.append(f"""
                <a href="http://localhost:{app_info['port']}"
                   style="
                       color: #fff;
                       text-decoration: none;
                       padding: 8px 12px;
                       border-radius: 4px;
                       border: 2px solid transparent;
                       transition: all 0.3s ease;
                   "
                   onmouseover="this.style.background='rgba(255,255,255,0.2)'; this.style.borderColor='rgba(255,255,255,0.4)';"
                   onmouseout="this.style.background='transparent'; this.style.borderColor='transparent';"
                   title="{app_info['description']}">
                    {app_info['name']}
                </a>
            """)

    # Create the navigation bar HTML
    nav_html = f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
                <h3 style="margin: 0; color: #fff; font-size: 18px;">
                    🚀 Data Fetcher & Time Series Analyzer Suite
                </h3>
                <p style="margin: 5px 0 0 0; color: rgba(255,255,255,0.8); font-size: 12px;">
                    Multi-App Panel Interface for Personal Analytics
                </p>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
                {' '.join(nav_links)}
            </div>
        </div>
    </div>
    """

    return pn.pane.HTML(nav_html, sizing_mode='stretch_width')

def create_quick_actions_panel():
    """Create quick actions panel for common operations"""

    quick_actions_html = """
    <div style="
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 15px;
        color: white;
    ">
        <h4 style="margin: 0 0 8px 0; font-size: 14px;">⚡ Quick Actions</h4>
        <div style="display: flex; gap: 15px; flex-wrap: wrap; font-size: 12px;">
            <a href="http://localhost:5006" style="color: #fff; text-decoration: none;">
                📥 Fetch New Data
            </a>
            <a href="http://localhost:5007" style="color: #fff; text-decoration: none;">
                📊 View Charts
            </a>
            <a href="http://localhost:5008" style="color: #fff; text-decoration: none;">
                💾 Export Data
            </a>
            <a href="http://localhost:5009" style="color: #fff; text-decoration: none;">
                ⚡ Update All
            </a>
        </div>
    </div>
    """

    return pn.pane.HTML(quick_actions_html, sizing_mode='stretch_width')

def create_app_status_indicator():
    """Create status indicator showing which apps are running"""

    status_html = """
    <div style="
        background: #e8f5e8;
        border: 1px solid #c3e6c3;
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-size: 12px;
    ">
        <div style="display: flex; gap: 15px; align-items: center;">
            <span style="font-weight: bold; color: #2d5a2d;">System Status:</span>
            <span style="color: #28a745;">🟢 All Apps Running</span>
            <span style="color: #666;">
                Ports: 5006, 5007, 5008, 5009
            </span>
        </div>
    </div>
    """

    return pn.pane.HTML(status_html, sizing_mode='stretch_width')