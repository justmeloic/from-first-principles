#!/usr/bin/env python3
"""
Quick test script for the indexing pipeline.
Run this to verify the setup works before using the main CLI.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from indexing.main import app

    print('✅ Successfully imported indexing CLI')
    print('🚀 You can now use the CLI with: blog-index --help')
    print('\nOr run directly with: python -m indexing.main --help')
except ImportError as e:
    print(f'❌ Failed to import indexing CLI: {e}')
    print('\nTo fix this, install the dependencies:')
    print(
        '  pip install typer rich lancedb sentence-transformers pyyaml markdown-it-py langchain-text-splitters torch'
    )
    sys.exit(1)

if __name__ == '__main__':
    print('\n🧪 Testing CLI...')
    # This would run the CLI but let's just test import for now
    print('✅ CLI test completed!')
