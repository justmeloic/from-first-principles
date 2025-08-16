# Analytics Dashboard

A Streamlit dashboard for analyzing blog content, embeddings, and system metrics.

## Quick Start

1. **Install dependencies** (if not already done):

   ```bash
   pip install -e .
   ```

2. **Launch the dashboard**:

   ```bash
   analytics
   ```

3. **Open in browser**: http://localhost:8501

## Features

- **Overview**: Key metrics and system status
- **Content Analysis**: Blog post statistics and distributions
- **Embeddings**: Vector analysis and visualization with PCA
- **Raw Data**: Interactive data tables and CSV exports

## Data Structure

The dashboard analyzes data from:

```
data/
├── content/          # Markdown files with YAML frontmatter
│   ├── blog/
│   └── engineering/
└── lancedb/          # Vector embeddings
    └── blog_content.lance/
```

## Alternative Launch Methods

```bash
# Direct Python execution
python src/analytics/main.py

# Using Streamlit directly
streamlit run src/analytics/dashboard.py
```

## Requirements

- Python 3.8+
- Streamlit, pandas, plotly, numpy
- Optional: scikit-learn (for PCA analysis)
- Optional: lancedb (for embedding analysis)

---

**Ready to analyze your data!** 🚀
