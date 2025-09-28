"""
Time Series Analyzer App - Panel Implementation
Interactive visualization with Linear/Log Y-axis toggle feature
"""
import panel as pn
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_store import shared_store
from utils.navigation import create_navigation_bar, create_quick_actions_panel, create_app_status_indicator

class DataAnalyzerApp:
    """Time series analysis and visualization with interactive controls"""

    def __init__(self):
        # Y-axis scale toggle
        self.y_scale_toggle = pn.widgets.RadioButtonGroup(
            name='Y-Axis Scale',
            options=['Linear', 'Log'],
            value='Linear',
            button_type='light'
        )

        # === INDIVIDUAL AXIS CONTROLS (NEW FEATURE) ===
        # Primary series scale (text input + slider)
        self.primary_scale_text = pn.widgets.FloatInput(
            name="Primary Scale Factor",
            value=1.0,
            step=0.1,
            start=0.1,
            end=10.0,
            width=150
        )
        self.primary_scale_slider = pn.widgets.FloatSlider(
            name="Primary Scale Slider",
            start=0.1,
            end=10.0,
            value=1.0,
            step=0.1,
            width=200
        )

        # Primary series offset (text input + slider)
        self.primary_offset_text = pn.widgets.FloatInput(
            name="Primary Offset",
            value=0.0,
            step=1.0,
            start=-100.0,
            end=100.0,
            width=150
        )
        self.primary_offset_slider = pn.widgets.FloatSlider(
            name="Primary Offset Slider",
            start=-100.0,
            end=100.0,
            value=0.0,
            step=1.0,
            width=200
        )

        # Secondary series scale (text input + slider)
        self.secondary_scale_text = pn.widgets.FloatInput(
            name="Secondary Scale Factor",
            value=0.1,
            step=0.01,
            start=0.001,
            end=1.0,
            width=150
        )
        self.secondary_scale_slider = pn.widgets.FloatSlider(
            name="Secondary Scale Slider",
            start=0.001,
            end=1.0,
            value=0.1,
            step=0.01,
            width=200
        )

        # Secondary series offset (text input + slider)
        self.secondary_offset_text = pn.widgets.FloatInput(
            name="Secondary Offset",
            value=0.0,
            step=1.0,
            start=-50.0,
            end=50.0,
            width=150
        )
        self.secondary_offset_slider = pn.widgets.FloatSlider(
            name="Secondary Offset Slider",
            start=-50.0,
            end=50.0,
            value=0.0,
            step=1.0,
            width=200
        )

        # Multi-series display mode
        self.display_mode = pn.widgets.RadioButtonGroup(
            name='Display Mode',
            options=['Individual Subplots', 'Aligned Overlay'],
            value='Individual Subplots',
            button_type='primary'
        )

        # Standard controls
        self.refresh_button = pn.widgets.Button(
            name="🔄 Refresh Data",
            button_type="primary",
            width=150
        )

        self.plot_height = pn.widgets.IntSlider(
            name="Plot Height",
            start=300,
            end=800,
            value=400,
            step=50
        )

        self.show_grid = pn.widgets.Checkbox(
            name="Show Grid",
            value=True
        )

        # Setup bidirectional synchronization for axis controls
        self._setup_axis_control_sync()

        self.data_info = pn.pane.HTML(
            """<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
            No data loaded yet. Use Data Fetcher to collect time series data.
            </div>""",
            width=400
        )

        # Main time series plot
        self.time_series_plot = pn.pane.Plotly(
            object=self.create_empty_plot(),
            height=400,
            sizing_mode='stretch_width'
        )

        # Statistics panel
        self.stats_panel = pn.pane.HTML(
            self.create_empty_stats(),
            width=400
        )

        # Setup callbacks
        self.refresh_button.on_click(self.refresh_data)
        self.y_scale_toggle.param.watch(self.update_plot_scale, 'value')
        self.plot_height.param.watch(self.update_plot_height, 'value')
        self.show_grid.param.watch(self.update_plot_grid, 'value')

        # Setup callbacks for axis controls
        for control in [self.primary_scale_text, self.primary_scale_slider,
                       self.primary_offset_text, self.primary_offset_slider,
                       self.secondary_scale_text, self.secondary_scale_slider,
                       self.secondary_offset_text, self.secondary_offset_slider,
                       self.display_mode]:
            control.param.watch(self.update_visualization, 'value')

        # Initial data load
        self.current_data = None
        self.load_data_on_startup()

    def _setup_axis_control_sync(self):
        """Setup bidirectional synchronization between text inputs and sliders"""

        # Primary scale synchronization
        def sync_primary_scale_to_slider(event):
            self.primary_scale_slider.value = self.primary_scale_text.value
        def sync_primary_scale_to_text(event):
            self.primary_scale_text.value = self.primary_scale_slider.value

        # Primary offset synchronization
        def sync_primary_offset_to_slider(event):
            self.primary_offset_slider.value = self.primary_offset_text.value
        def sync_primary_offset_to_text(event):
            self.primary_offset_text.value = self.primary_offset_slider.value

        # Secondary scale synchronization
        def sync_secondary_scale_to_slider(event):
            self.secondary_scale_slider.value = self.secondary_scale_text.value
        def sync_secondary_scale_to_text(event):
            self.secondary_scale_text.value = self.secondary_scale_slider.value

        # Secondary offset synchronization
        def sync_secondary_offset_to_slider(event):
            self.secondary_offset_slider.value = self.secondary_offset_text.value
        def sync_secondary_offset_to_text(event):
            self.secondary_offset_text.value = self.secondary_offset_slider.value

        # Wire up synchronization
        self.primary_scale_text.param.watch(sync_primary_scale_to_slider, 'value')
        self.primary_scale_slider.param.watch(sync_primary_scale_to_text, 'value')
        self.primary_offset_text.param.watch(sync_primary_offset_to_slider, 'value')
        self.primary_offset_slider.param.watch(sync_primary_offset_to_text, 'value')

        self.secondary_scale_text.param.watch(sync_secondary_scale_to_slider, 'value')
        self.secondary_scale_slider.param.watch(sync_secondary_scale_to_text, 'value')
        self.secondary_offset_text.param.watch(sync_secondary_offset_to_slider, 'value')
        self.secondary_offset_slider.param.watch(sync_secondary_offset_to_text, 'value')

    def create_app(self):
        """Create the time series analyzer interface"""

        # Navigation bar
        navigation = create_navigation_bar(current_app='time_series_analyzer')

        # Status indicator
        status = create_app_status_indicator()

        # Header
        header = pn.pane.HTML("""
        <div style="background: linear-gradient(90deg, #007bff, #0056b3); padding: 20px; color: white; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">📈 Time Series Analyzer - Enhanced Individual Axis Control</h2>
            <p style="margin: 5px 0 0 0;">Advanced data alignment with synchronized sliders + text inputs</p>
        </div>
        """, sizing_mode='stretch_width')

        # Individual Axis Controls Panel
        axis_controls = pn.Column(
            "## 🎛️ Individual Axis Controls",
            self.display_mode,
            "### Primary Series",
            pn.Row(self.primary_scale_text, self.primary_scale_slider),
            pn.Row(self.primary_offset_text, self.primary_offset_slider),
            "### Secondary Series",
            pn.Row(self.secondary_scale_text, self.secondary_scale_slider),
            pn.Row(self.secondary_offset_text, self.secondary_offset_slider),
            width=500
        )

        # Standard control panel
        control_panel = pn.Column(
            "## 📊 Plot Settings",
            self.y_scale_toggle,
            self.plot_height,
            self.show_grid,
            self.refresh_button,
            "## 📊 Data Information",
            self.data_info,
            "## 📈 Statistics",
            self.stats_panel,
            width=400
        )

        # Main visualization panel
        viz_panel = pn.Column(
            "## 📊 Time Series Visualization",
            self.time_series_plot,
            sizing_mode='stretch_width'
        )

        # Main layout
        return pn.Column(
            navigation,
            status,
            header,
            pn.Row(
                pn.Column(axis_controls, control_panel),
                viz_panel,
                sizing_mode='stretch_width'
            ),
            sizing_mode='stretch_width'
        )

    def load_data_on_startup(self):
        """Load existing data when app starts"""
        try:
            time_series_data = shared_store.load_time_series_data()
            if time_series_data:
                self.current_data = time_series_data
                self.update_visualization()
                self.update_data_info()
        except Exception as e:
            print(f"Error loading data on startup: {e}")

    def refresh_data(self, event):
        """Refresh data from shared store"""
        try:
            time_series_data = shared_store.load_time_series_data()
            if time_series_data:
                self.current_data = time_series_data
                self.update_visualization()
                self.update_data_info()
                self.update_status("✅ Data refreshed successfully")
            else:
                self.update_status("⚠️ No data available. Use Data Fetcher first.")
        except Exception as e:
            self.update_status(f"❌ Error refreshing data: {str(e)}")

    def update_plot_scale(self, event):
        """Update Y-axis scale (Linear/Log toggle)"""
        if self.current_data:
            self.update_visualization()

    def update_plot_height(self, event):
        """Update plot height"""
        self.time_series_plot.height = self.plot_height.value
        if self.current_data:
            self.update_visualization()

    def update_plot_grid(self, event):
        """Update grid visibility"""
        if self.current_data:
            self.update_visualization()

    def update_visualization(self):
        """Update the main time series visualization with individual axis controls"""
        if not self.current_data or not self.current_data.get('data'):
            self.time_series_plot.object = self.create_empty_plot()
            return

        try:
            # Extract data
            data_points = self.current_data['data']
            df = pd.DataFrame(data_points)

            if df.empty:
                self.time_series_plot.object = self.create_empty_plot()
                return

            # Convert timestamp to datetime if needed
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:
                # Create timestamps if missing
                df['timestamp'] = pd.date_range(
                    start=datetime.now() - timedelta(hours=len(df)),
                    periods=len(df),
                    freq='H'
                )

            # Generate secondary data for demonstration (in real app, this would come from shared store)
            secondary_data = df['value'].values * 0.5 + np.random.randn(len(df)) * 2

            # Apply individual axis transformations
            primary_transformed = df['value'] * self.primary_scale_text.value + self.primary_offset_text.value
            secondary_transformed = secondary_data * self.secondary_scale_text.value + self.secondary_offset_text.value

            # Apply Y-axis scale (Linear/Log toggle feature)
            y_axis_type = 'log' if self.y_scale_toggle.value == 'Log' else 'linear'

            if self.display_mode.value == "Individual Subplots":
                # Create subplots with individual axis controls
                from plotly.subplots import make_subplots
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=[
                        f"Primary Series (×{self.primary_scale_text.value:.1f} +{self.primary_offset_text.value:.0f})",
                        f"Secondary Series (×{self.secondary_scale_text.value:.3f} +{self.secondary_offset_text.value:.0f})"
                    ],
                    vertical_spacing=0.15
                )

                # Add primary series
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=primary_transformed,
                    mode='lines+markers',
                    name='Primary Series',
                    line=dict(width=2, color='#007bff'),
                    marker=dict(size=4, color='#007bff')
                ), row=1, col=1)

                # Add secondary series
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=secondary_transformed,
                    mode='lines+markers',
                    name='Secondary Series',
                    line=dict(width=2, color='#e74c3c'),
                    marker=dict(size=4, color='#e74c3c')
                ), row=2, col=1)

                # Update layout for subplots
                fig.update_layout(
                    title=f"Individual Axis Control - {self.current_data.get('source_name', 'Time Series')} ({self.y_scale_toggle.value} Scale)",
                    height=self.plot_height.value + 200,
                    showlegend=True,
                    template='plotly_white'
                )

                # Update individual Y-axes
                fig.update_yaxes(title_text="Primary Values", type=y_axis_type, showgrid=self.show_grid.value, row=1, col=1)
                fig.update_yaxes(title_text="Secondary Values", type=y_axis_type, showgrid=self.show_grid.value, row=2, col=1)
                fig.update_xaxes(showgrid=self.show_grid.value)

            else:  # Aligned Overlay
                # Create overlay plot with aligned axes
                fig = go.Figure()

                # Add primary series
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=primary_transformed,
                    mode='lines+markers',
                    name=f'Primary (×{self.primary_scale_text.value:.1f} +{self.primary_offset_text.value:.0f})',
                    line=dict(width=3, color='#007bff'),
                    marker=dict(size=6, color='#007bff')
                ))

                # Add secondary series
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=secondary_transformed,
                    mode='lines+markers',
                    name=f'Secondary (×{self.secondary_scale_text.value:.3f} +{self.secondary_offset_text.value:.0f})',
                    line=dict(width=2, color='#e74c3c', dash='dash'),
                    marker=dict(size=4, color='#e74c3c')
                ))

                # Update layout for overlay
                fig.update_layout(
                    title=f"Aligned Multi-Series - {self.current_data.get('source_name', 'Time Series')} ({self.y_scale_toggle.value} Scale)",
                    xaxis_title="Time",
                    yaxis_title="Aligned Values",
                    yaxis_type=y_axis_type,
                    height=self.plot_height.value,
                    showlegend=True,
                    hovermode='x unified',
                    template='plotly_white',
                    xaxis=dict(showgrid=self.show_grid.value),
                    yaxis=dict(showgrid=self.show_grid.value)
                )

            self.time_series_plot.object = fig
            self.update_statistics(df)

        except Exception as e:
            print(f"Error updating visualization: {e}")
            self.time_series_plot.object = self.create_error_plot(str(e))

    def create_empty_plot(self):
        """Create empty plot placeholder"""
        fig = go.Figure()
        fig.add_annotation(
            text="No data available<br>Use Data Fetcher to collect time series data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Time Series Visualization",
            xaxis_title="Time",
            yaxis_title="Value",
            height=self.plot_height.value,
            template='plotly_white'
        )
        return fig

    def create_error_plot(self, error_message):
        """Create error plot"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error loading data:<br>{error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(
            title="Time Series Visualization - Error",
            xaxis_title="Time",
            yaxis_title="Value",
            height=self.plot_height.value,
            template='plotly_white'
        )
        return fig

    def update_statistics(self, df):
        """Update statistics panel"""
        try:
            values = df['value'].dropna()
            if len(values) == 0:
                self.stats_panel.object = self.create_empty_stats()
                return

            stats = {
                'count': len(values),
                'mean': values.mean(),
                'median': values.median(),
                'std': values.std(),
                'min': values.min(),
                'max': values.max(),
                'range': values.max() - values.min()
            }

            stats_html = f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace;">
                <h4 style="margin-top: 0;">Basic Statistics</h4>
                <table style="width: 100%;">
                    <tr><td><strong>Count:</strong></td><td>{stats['count']}</td></tr>
                    <tr><td><strong>Mean:</strong></td><td>{stats['mean']:.4f}</td></tr>
                    <tr><td><strong>Median:</strong></td><td>{stats['median']:.4f}</td></tr>
                    <tr><td><strong>Std Dev:</strong></td><td>{stats['std']:.4f}</td></tr>
                    <tr><td><strong>Min:</strong></td><td>{stats['min']:.4f}</td></tr>
                    <tr><td><strong>Max:</strong></td><td>{stats['max']:.4f}</td></tr>
                    <tr><td><strong>Range:</strong></td><td>{stats['range']:.4f}</td></tr>
                </table>
                <p style="margin-bottom: 0; font-size: 12px; color: #666;">
                    Y-axis: {self.y_scale_toggle.value} Scale
                </p>
            </div>
            """
            self.stats_panel.object = stats_html

        except Exception as e:
            self.stats_panel.object = f"""
            <div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                Error calculating statistics: {str(e)}
            </div>
            """

    def create_empty_stats(self):
        """Create empty statistics panel"""
        return """
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h4 style="margin-top: 0;">Statistics</h4>
            <p style="color: #666; margin: 0;">No data available for analysis</p>
        </div>
        """

    def update_data_info(self):
        """Update data information panel"""
        if not self.current_data:
            self.data_info.object = """
            <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                No data loaded yet. Use Data Fetcher to collect time series data.
            </div>
            """
            return

        try:
            metadata = self.current_data.get('metadata', {})
            data_points = len(self.current_data.get('data', []))
            timestamp = self.current_data.get('timestamp', 'Unknown')

            info_html = f"""
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; border: 1px solid #c3e6cb;">
                <h4 style="margin-top: 0; color: #155724;">📊 Data Information</h4>
                <table style="width: 100%;">
                    <tr><td><strong>Source:</strong></td><td>{self.current_data.get('source_name', 'Unknown')}</td></tr>
                    <tr><td><strong>Data Points:</strong></td><td>{data_points}</td></tr>
                    <tr><td><strong>Last Updated:</strong></td><td>{timestamp[:19] if timestamp else 'Unknown'}</td></tr>
                    <tr><td><strong>API URL:</strong></td><td>{metadata.get('api_url', 'N/A')[:50]}...</td></tr>
                    <tr><td><strong>Data Path:</strong></td><td>{metadata.get('data_path', 'N/A')}</td></tr>
                </table>
            </div>
            """
            self.data_info.object = info_html

        except Exception as e:
            self.data_info.object = f"""
            <div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                Error loading data info: {str(e)}
            </div>
            """

    def update_status(self, message):
        """Update status (placeholder for now)"""
        print(f"Time Series Analyzer: {message}")