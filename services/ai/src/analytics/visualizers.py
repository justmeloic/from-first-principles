"""
Visualization components for the analytics dashboard.

Contains specialized visualizers for different types of data analysis
including content analysis, embedding visualization, and metrics display.
"""

from typing import Dict, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


class ContentVisualizer:
    """Visualizes content-related analytics."""

    @staticmethod
    def plot_category_distribution(categories: Dict[str, int]):
        """Plot distribution of content by category."""
        if not categories:
            st.warning("No category data available")
            return

        fig = px.pie(
            values=list(categories.values()),
            names=list(categories.keys()),
            title="Content Distribution by Category"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def plot_tag_cloud(tags: Dict[str, int], top_n: int = 20):
        """Plot top tags as a horizontal bar chart."""
        if not tags:
            st.warning("No tag data available")
            return

        # Get top N tags
        sorted_tags = dict(
            sorted(tags.items(), key=lambda x: x[1], reverse=True)[:top_n]
        )

        fig = px.bar(
            x=list(sorted_tags.values()),
            y=list(sorted_tags.keys()),
            orientation='h',
            title=f"Top {top_n} Tags",
            labels={'x': 'Count', 'y': 'Tags'}
        )
        fig.update_layout(height=max(400, len(sorted_tags) * 25))
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def plot_publishing_timeline(df: pd.DataFrame):
        """Plot content publishing timeline."""
        if df.empty or 'publish_date' not in df.columns:
            st.warning("No publishing date data available")
            return

        # Filter out null dates
        df_with_dates = df[df['publish_date'].notna()].copy()
        if df_with_dates.empty:
            st.warning("No valid publishing dates found")
            return

        # Create monthly aggregation
        df_with_dates['year_month'] = df_with_dates['publish_date'].dt.to_period('M')
        monthly_counts = (
            df_with_dates.groupby('year_month').size().reset_index(name='count')
        )
        monthly_counts['year_month_str'] = monthly_counts['year_month'].astype(str)

        fig = px.line(
            monthly_counts,
            x='year_month_str',
            y='count',
            title="Content Publishing Timeline",
            labels={'year_month_str': 'Month', 'count': 'Posts Published'}
        )
        fig.update_traces(mode='markers+lines')
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def plot_reading_time_distribution(df: pd.DataFrame):
        """Plot distribution of reading times."""
        if df.empty or 'reading_time' not in df.columns:
            st.warning("No reading time data available")
            return

        reading_times = df['reading_time'].dropna()
        if reading_times.empty:
            st.warning("No reading time data found")
            return

        fig = px.histogram(
            reading_times,
            nbins=20,
            title="Reading Time Distribution",
            labels={'value': 'Reading Time (minutes)', 'count': 'Number of Posts'}
        )
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def plot_word_count_vs_reading_time(df: pd.DataFrame):
        """Plot correlation between word count and reading time."""
        if (df.empty or
            'word_count' not in df.columns or
            'reading_time' not in df.columns):
            st.warning("No word count or reading time data available")
            return

        # Filter out rows with missing data
        clean_df = df[['word_count', 'reading_time', 'title']].dropna()
        if clean_df.empty:
            st.warning("No complete word count and reading time data found")
            return

        fig = px.scatter(
            clean_df,
            x='word_count',
            y='reading_time',
            hover_data=['title'],
            title="Word Count vs Reading Time",
            labels={'word_count': 'Word Count', 'reading_time': 'Reading Time (min)'}
        )

        # Add trend line
        polynomial_fit = np.polyfit(
            clean_df['word_count'], clean_df['reading_time'], 1
        )
        trend_line = np.poly1d(polynomial_fit)(clean_df['word_count'])

        fig.add_trace(
            go.Scatter(
                x=clean_df['word_count'],
                y=trend_line,
                mode='lines',
                name='Trend Line',
                line=dict(dash='dash')
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def display_content_metrics(stats):
        """Display content metrics in columns."""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Posts", stats.total_posts)

        with col2:
            st.metric("Avg Reading Time", f"{stats.avg_reading_time:.1f} min")

        with col3:
            st.metric("Avg Word Count", f"{stats.avg_word_count:.0f}")

        with col4:
            st.metric("Featured Posts", stats.featured_posts)


class EmbeddingVisualizer:
    """Visualizes embedding-related analytics."""

    @staticmethod
    def display_embedding_metrics(stats: Optional[Dict]):
        """Display embedding metrics."""
        if not stats:
            st.warning("No embedding data available")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Embeddings", stats.get('total_embeddings', 'N/A'))

        with col2:
            st.metric("Vector Dimension", stats.get('vector_dimension', 'N/A'))

        with col3:
            st.metric("Embedded Posts", stats.get('embedded_posts', 'N/A'))

    @staticmethod
    def plot_embedding_coverage(
        lancedb_df: Optional[pd.DataFrame],
        content_df: pd.DataFrame
    ):
        """Plot coverage of embeddings vs total content."""
        if lancedb_df is None or content_df.empty:
            st.warning("Cannot calculate embedding coverage - missing data")
            return

        # Calculate coverage
        if 'post_slug' in lancedb_df.columns:
            embedded_posts = set(lancedb_df['post_slug'].unique())
            total_posts = set(content_df['slug'].unique())

            covered = len(embedded_posts)
            total = len(total_posts)
            coverage_pct = (covered / total * 100) if total > 0 else 0

            # Create a simple bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=['Embedded', 'Not Embedded'],
                    y=[covered, total - covered],
                    marker_color=['green', 'lightgray']
                )
            ])

            fig.update_layout(
                title=f"Embedding Coverage ({coverage_pct:.1f}%)",
                yaxis_title="Number of Posts"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No post slug information available in embedding data")


class MetricsVisualizer:
    """Visualizes general metrics and KPIs."""

    @staticmethod
    def plot_file_system_stats(stats: Dict):
        """Plot file system statistics."""
        if not stats:
            st.warning("No file system data available")
            return

        col1, col2 = st.columns(2)

        with col1:
            # File type distribution
            if 'file_types' in stats and stats['file_types']:
                fig = px.pie(
                    values=list(stats['file_types'].values()),
                    names=list(stats['file_types'].keys()),
                    title="File Types Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Directory structure
            if 'directory_structure' in stats and stats['directory_structure']:
                # Show top directories
                dir_stats = dict(sorted(
                    stats['directory_structure'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10])

                fig = px.bar(
                    x=list(dir_stats.values()),
                    y=list(dir_stats.keys()),
                    orientation='h',
                    title="Files per Directory"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

        # Display summary metrics
        col3, col4 = st.columns(2)

        with col3:
            st.metric("Total Files", stats.get('total_files', 'N/A'))

        with col4:
            st.metric("Total Size", f"{stats.get('total_size_mb', 0):.2f} MB")

    @staticmethod
    def plot_search_trends(logs_df: Optional[pd.DataFrame]):
        """Plot search trends from logs."""
        if logs_df is None or logs_df.empty:
            st.warning("No search log data available")
            return

        # Group by date
        logs_df['date'] = logs_df['timestamp'].dt.date
        daily_searches = logs_df.groupby('date').size().reset_index(name='search_count')

        fig = px.line(
            daily_searches,
            x='date',
            y='search_count',
            title="Daily Search Activity",
            labels={'date': 'Date', 'search_count': 'Number of Searches'}
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def display_system_overview(content_stats, fs_stats, embedding_stats):
        """Display a comprehensive system overview."""
        st.subheader("System Overview")

        # Create metrics grid
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Content Health",
                "✅ Good" if content_stats.total_posts > 0 else "⚠️ No Content"
            )

        with col2:
            embedding_status = "✅ Active" if embedding_stats else "❌ No Data"
            st.metric("Embeddings", embedding_status)

        with col3:
            storage_gb = fs_stats.get('total_size_mb', 0) / 1024
            st.metric("Storage Used", f"{storage_gb:.2f} GB")

        with col4:
            categories_count = (
                len(content_stats.categories) if content_stats.categories else 0
            )
            st.metric("Categories", categories_count)
