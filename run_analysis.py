#!/usr/bin/env python3
"""
CLI Runner for Dropshipping Product Analysis
Provides command-line interface for running product analysis and web server
"""
import argparse
import sys
import os
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_analysis(output_csv=None, top_n=20):
    """Run the product analysis pipeline"""
    try:
        from main_product_data_processor import ProductDataProcessor
        
        logger.info("🚀 Starting Dropshipping Product Analysis...")
        
        processor = ProductDataProcessor()
        results = processor.process_all_data()
        
        if results:
            logger.info(f"✅ Analysis completed successfully!")
            logger.info(f"📊 Analyzed {len(results)} products")
            
            # Export to custom CSV if specified
            if output_csv:
                success = processor.normalizer.export_to_csv(output_csv, top_n)
                if success:
                    logger.info(f"📁 Results exported to {output_csv}")
                else:
                    logger.error(f"❌ Failed to export to {output_csv}")
            
            # Show top results
            print("\n" + "="*60)
            print("🏆 TOP DROPSHIPPING PRODUCTS")
            print("="*60)
            
            for i, product in enumerate(results[:5], 1):
                print(f"\n{i}. {product['product_name']}")
                print(f"   Score: {product['score']}")
                print(f"   Trend: {product['trend_momentum']}")
                print(f"   Orders: {product['orders']:,}")
                print(f"   TikTok: {product['tiktok_views']}")
                print(f"   Sources: {len(product['data_sources'])}")
            
            return True
        else:
            logger.error("❌ Analysis failed - no results generated")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        logger.info("💡 Try running: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return False

def run_web_server(port=5000, debug=False):
    """Start the Flask web server"""
    try:
        from web_interface import app
        
        logger.info(f"🌐 Starting web server on port {port}...")
        logger.info(f"📱 Access dashboard at: http://localhost:{port}")
        
        app.run(debug=debug, host='0.0.0.0', port=port)
        
    except ImportError as e:
        logger.error(f"❌ Web server dependencies missing: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Web server failed: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'pandas', 'numpy', 'flask', 'requests', 'beautifulsoup4'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.warning(f"⚠️  Missing packages: {', '.join(missing)}")
        logger.info("💡 Install with: pip install " + ' '.join(missing))
        return False
    
    logger.info("✅ All dependencies satisfied")
    return True

def setup_project():
    """Set up project structure and create sample files"""
    logger.info("🔧 Setting up project structure...")
    
    # Create directories
    dirs_to_create = ['data', 'templates', 'logs']
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        logger.info(f"📁 Created directory: {dir_name}")
    
    # Create requirements.txt if it doesn't exist
    if not Path('requirements.txt').exists():
        requirements = """pandas>=1.3.0
numpy>=1.21.0
flask>=2.0.0
requests>=2.25.0
beautifulsoup4>=4.9.0
lxml>=4.6.0
selenium>=4.0.0
pytrends>=4.7.0
"""
        with open('requirements.txt', 'w') as f:
            f.write(requirements)
        logger.info("📝 Created requirements.txt")
    
    # Create .gitignore if it doesn't exist
    if not Path('.gitignore').exists():
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Data files
*.csv
*.json
data/
logs/

# Flask
instance/
.webassets-cache

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        with open('.gitignore', 'w') as f:
            f.write(gitignore)
        logger.info("📝 Created .gitignore")
    
    logger.info("✅ Project setup completed")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Dropshipping Product Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_analysis.py analyze                    # Run full analysis
  python run_analysis.py analyze --csv results.csv # Export to custom CSV
  python run_analysis.py web                        # Start web server
  python run_analysis.py web --port 8080           # Start on port 8080
  python run_analysis.py setup                     # Set up project
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run product analysis')
    analyze_parser.add_argument('--csv', '--output', help='Output CSV filename')
    analyze_parser.add_argument('--top', type=int, default=20, help='Number of top products to export')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web server')
    web_parser.add_argument('--port', type=int, default=5000, help='Web server port')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up project structure')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check dependencies')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🏪 Dropshipping Product Analyzer v1.0")
    print("="*50)
    
    if args.command == 'setup':
        setup_project()
        
    elif args.command == 'check':
        check_dependencies()
        
    elif args.command == 'analyze':
        if not check_dependencies():
            sys.exit(1)
        
        success = run_analysis(args.csv, args.top)
        if not success:
            sys.exit(1)
            
    elif args.command == 'web':
        if not check_dependencies():
            sys.exit(1)
        
        run_web_server(args.port, args.debug)
        
    else:
        parser.print_help()

if __name__ == '__main__':
    main()