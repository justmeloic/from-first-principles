"""
Main Streamlit dashboard for analytics.

Simple dashboard that properly launches with Streamlit.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import numpy as np
try:
    import lancedb
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    st.warning("LanceDB not available - install with: pip install lancedb")

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Blog Analytics Dashboard")
st.markdown("Comprehensive analytics for blog content, embeddings, and performance")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")

    # Data directory selector
    data_dir = st.text_input(
        "Data Directory",
        value="data",
        help="Path to the data directory"
    )

    # Refresh data button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # Navigation
    st.header("Navigation")
    selected_page = st.selectbox(
        "Select View",
        ["Overview", "Content Analysis", "Embeddings", "Raw Data"]
    )

# Basic data loading function
def load_basic_stats(data_dir):
    """Load basic file statistics."""
    try:
        data_path = Path(data_dir)
        if not data_path.exists():
            return {"error": f"Directory {data_dir} not found"}

        content_dir = data_path / "content"
        lancedb_dir = data_path / "lancedb"
        logs_dir = Path("logs")

        stats = {
            "data_dir_exists": data_path.exists(),
            "content_dir_exists": content_dir.exists(),
            "lancedb_dir_exists": lancedb_dir.exists(),
            "logs_dir_exists": logs_dir.exists(),
            "content_files": 0,
            "total_size_mb": 0
        }

        # Count files
        if content_dir.exists():
            md_files = list(content_dir.glob("**/*.md"))
            stats["content_files"] = len(md_files)

        # Calculate directory size
        if data_path.exists():
            total_size = sum(f.stat().st_size for f in data_path.rglob('*') if f.is_file())
            stats["total_size_mb"] = total_size / (1024 * 1024)

        return stats
    except Exception as e:
        return {"error": str(e)}

@st.cache_data
def load_lancedb_data(data_dir):
    """Load embeddings data from LanceDB."""
    if not LANCEDB_AVAILABLE:
        return None, "LanceDB not installed"

    try:
        lancedb_path = Path(data_dir) / "lancedb"
        if not lancedb_path.exists():
            return None, f"LanceDB directory not found: {lancedb_path}"

        db = lancedb.connect(str(lancedb_path))
        tables = db.table_names()

        if not tables:
            return None, "No tables found in LanceDB"

        # Try to load blog_content table first
        tables_list = list(tables)
        table_name = "blog_content" if "blog_content" in tables else tables_list[0]
        table = db.open_table(table_name)
        df = table.to_pandas()

        return df, f"Loaded table: {table_name}"

    except Exception as e:
        return None, f"Error loading LanceDB: {str(e)}"

def analyze_embeddings(df):
    """Analyze embedding vectors in the dataframe."""
    # Look for vector column (common names)
    vector_cols = [col for col in df.columns if 'vector' in col.lower() or 'embedding' in col.lower()]

    if not vector_cols:
        # Try to find columns with array-like data
        for col in df.columns:
            if df[col].dtype == object:
                try:
                    # Check if first non-null value is array-like
                    first_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                    if isinstance(first_val, (list, np.ndarray)) or (isinstance(first_val, str) and first_val.startswith('[')):
                        vector_cols.append(col)
                        break
                except:
                    continue

    if not vector_cols:
        return None, "No vector columns found"

    vector_col = vector_cols[0]

    try:
        # Convert vectors to numpy arrays if they're strings
        vectors = []
        for idx, val in df[vector_col].items():
            if isinstance(val, str):
                # Try to parse string representation of list/array
                import ast
                try:
                    parsed = ast.literal_eval(val)
                    vectors.append(np.array(parsed))
                except:
                    vectors.append(np.array([]))
            elif isinstance(val, (list, np.ndarray)):
                vectors.append(np.array(val))
            else:
                vectors.append(np.array([]))

        # Filter out empty vectors
        valid_vectors = [v for v in vectors if len(v) > 0]

        if not valid_vectors:
            return None, "No valid vectors found"

        # Stack vectors
        vector_matrix = np.vstack(valid_vectors)

        analysis = {
            "total_vectors": len(valid_vectors),
            "dimensions": vector_matrix.shape[1],
            "vector_col": vector_col,
            "vector_matrix": vector_matrix,
            "mean_norm": np.mean(np.linalg.norm(vector_matrix, axis=1)),
            "std_norm": np.std(np.linalg.norm(vector_matrix, axis=1))
        }

        return analysis, "Analysis complete"

    except Exception as e:
        return None, f"Error analyzing vectors: {str(e)}"

# Load stats
stats = load_basic_stats(data_dir)

# Display selected page
if selected_page == "Overview":
    st.header("📊 Overview")

    if "error" in stats:
        st.error(f"Error: {stats['error']}")
    else:
        # Key metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Content Files", stats["content_files"])

        with col2:
            st.metric("Data Directory Size", f"{stats['total_size_mb']:.2f} MB")

        with col3:
            dirs_found = (
                int(stats["content_dir_exists"]) +
                int(stats["lancedb_dir_exists"]) +
                int(stats["logs_dir_exists"])
            )
            st.metric("Directories Found", dirs_found)

        # Directory status
        st.subheader("Directory Status")
        status_data = {
            "Directory": ["Content", "LanceDB", "Logs"],
            "Status": [
                "✅ Found" if stats["content_dir_exists"] else "❌ Missing",
                "✅ Found" if stats["lancedb_dir_exists"] else "❌ Missing",
                "✅ Found" if stats["logs_dir_exists"] else "❌ Missing"
            ]
        }
        st.table(pd.DataFrame(status_data))

elif selected_page == "Content Analysis":
    st.header("📄 Content Analysis")

    content_path = Path(data_dir) / "content"
    if content_path.exists():
        # Find all markdown files
        md_files = list(content_path.glob("**/*.md"))

        if md_files:
            st.metric("Total Markdown Files", len(md_files))

            # File distribution by subdirectory
            subdirs = {}
            for file in md_files:
                # Get relative path from content directory
                rel_path = file.relative_to(content_path)
                if len(rel_path.parts) > 1:
                    subdir = rel_path.parts[0]
                    subdirs[subdir] = subdirs.get(subdir, 0) + 1
                else:
                    subdirs["root"] = subdirs.get("root", 0) + 1

            if subdirs:
                st.subheader("Files by Directory")
                fig = px.pie(
                    values=list(subdirs.values()),
                    names=list(subdirs.keys()),
                    title="Content Files by Directory"
                )
                st.plotly_chart(fig, use_container_width=True)

                # File list
                st.subheader("Content Files")
                files_data = []
                for file in md_files[:20]:  # Limit to first 20 files
                    rel_path = file.relative_to(content_path)
                    size_kb = file.stat().st_size / 1024
                    files_data.append({
                        "File": str(rel_path),
                        "Size (KB)": f"{size_kb:.1f}"
                    })

                if files_data:
                    df = pd.DataFrame(files_data)
                    st.dataframe(df, use_container_width=True)

                    if len(md_files) > 20:
                        st.info(f"Showing first 20 of {len(md_files)} files")
        else:
            st.info("No markdown files found in content directory")
    else:
        st.warning(f"Content directory not found: {content_path}")

elif selected_page == "Embeddings":
    st.header("🧬 Embeddings Analysis")

    # Load embeddings data
    embeddings_df, message = load_lancedb_data(data_dir)
    st.info(f"Status: {message}")

    if embeddings_df is not None:
        st.subheader("Embeddings Data Overview")

        # Basic info about the dataframe
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(embeddings_df))
        with col2:
            st.metric("Columns", len(embeddings_df.columns))
        with col3:
            st.metric("Memory Usage", f"{embeddings_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        # Show column information
        st.subheader("Column Information")
        col_info = []
        for col in embeddings_df.columns:
            dtype = str(embeddings_df[col].dtype)
            null_count = embeddings_df[col].isnull().sum()
            col_info.append({
                "Column": col,
                "Data Type": dtype,
                "Null Count": null_count,
                "Sample Value": str(embeddings_df[col].iloc[0])[:100] + "..." if len(str(embeddings_df[col].iloc[0])) > 100 else str(embeddings_df[col].iloc[0])
            })

        col_df = pd.DataFrame(col_info)
        st.dataframe(col_df, use_container_width=True)

        # Analyze embeddings
        st.subheader("Vector Analysis")
        analysis, analysis_msg = analyze_embeddings(embeddings_df)

        if analysis:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Vector Count", analysis["total_vectors"])
            with col2:
                st.metric("Dimensions", analysis["dimensions"])
            with col3:
                st.metric("Avg Vector Norm", f"{analysis['mean_norm']:.4f}")

            # Vector statistics
            st.subheader("Vector Statistics")
            vector_matrix = analysis["vector_matrix"]

            # Plot vector norms distribution
            norms = np.linalg.norm(vector_matrix, axis=1)
            fig_norms = px.histogram(
                x=norms,
                title="Distribution of Vector Norms",
                labels={"x": "Vector Norm", "y": "Count"}
            )
            st.plotly_chart(fig_norms, use_container_width=True)

            # Dimensionality visualization - show first few dimensions
            if analysis["dimensions"] > 1:
                st.subheader("Dimension Analysis")

                # Show statistics for first 10 dimensions
                dim_stats = []
                for i in range(min(10, analysis["dimensions"])):
                    dim_values = vector_matrix[:, i]
                    dim_stats.append({
                        "Dimension": f"dim_{i}",
                        "Mean": f"{np.mean(dim_values):.4f}",
                        "Std": f"{np.std(dim_values):.4f}",
                        "Min": f"{np.min(dim_values):.4f}",
                        "Max": f"{np.max(dim_values):.4f}"
                    })

                dim_df = pd.DataFrame(dim_stats)
                st.dataframe(dim_df, use_container_width=True)

                # 2D visualization using first 2 dimensions
                if analysis["dimensions"] >= 2:
                    st.subheader("2D Visualization (First 2 Dimensions)")
                    fig_2d = px.scatter(
                        x=vector_matrix[:, 0],
                        y=vector_matrix[:, 1],
                        title="Embeddings in 2D Space (Dimensions 0 vs 1)",
                        labels={"x": "Dimension 0", "y": "Dimension 1"}
                    )
                    st.plotly_chart(fig_2d, use_container_width=True)

                # PCA visualization if we have enough data
                if len(vector_matrix) > 3 and analysis["dimensions"] > 2:
                    try:
                        from sklearn.decomposition import PCA
                        pca = PCA(n_components=2)
                        pca_result = pca.fit_transform(vector_matrix)

                        st.subheader("PCA Visualization")
                        fig_pca = px.scatter(
                            x=pca_result[:, 0],
                            y=pca_result[:, 1],
                            title=f"PCA Visualization (Explained Variance: {pca.explained_variance_ratio_[0]:.2%}, {pca.explained_variance_ratio_[1]:.2%})",
                            labels={"x": "First Principal Component", "y": "Second Principal Component"}
                        )
                        st.plotly_chart(fig_pca, use_container_width=True)

                    except ImportError:
                        st.info("Install scikit-learn for PCA visualization: pip install scikit-learn")

            # Show raw embedding data (limited)
            st.subheader("Sample Embeddings Data")
            display_df = embeddings_df.head(10)
            st.dataframe(display_df, use_container_width=True)

        else:
            st.warning(f"Could not analyze embeddings: {analysis_msg}")

    else:
        st.warning("No embeddings data available. Check your LanceDB directory and tables.")

elif selected_page == "Raw Data":
    st.header("🔍 Raw Data Explorer")

    # Show directory structure
    data_path = Path(data_dir)
    if data_path.exists():
        st.subheader("Directory Structure")

        # Get directory tree (first 2 levels)
        tree_data = []
        for item in data_path.iterdir():
            if item.is_dir():
                tree_data.append({"Path": item.name + "/", "Type": "Directory"})
                # Add subdirectories
                for subitem in item.iterdir():
                    if subitem.is_dir():
                        tree_data.append({"Path": f"  {item.name}/{subitem.name}/", "Type": "Subdirectory"})
            else:
                tree_data.append({"Path": item.name, "Type": "File"})

        if tree_data:
            df = pd.DataFrame(tree_data)
            st.dataframe(df, use_container_width=True)

        # File counts by type
        st.subheader("File Statistics")
        file_types = {}
        for file in data_path.rglob('*'):
            if file.is_file():
                ext = file.suffix.lower()
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1
                else:
                    file_types["no extension"] = file_types.get("no extension", 0) + 1

        if file_types:
            fig = px.bar(
                x=list(file_types.keys()),
                y=list(file_types.values()),
                title="File Types Distribution"
            )
            fig.update_layout(xaxis_title="File Extension", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Data directory not found: {data_path}")

# Footer
st.divider()
st.markdown("**Analytics Dashboard** - Analyzing your AI service data")
