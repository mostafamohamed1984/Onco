#!/bin/bash

# Importation Cycle Installation Script
# This script automates the installation of the importation cycle workflow

set -e  # Exit on any error

echo "🚀 Importation Cycle Installation Script"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Get installation parameters
read -p "Enter your Frappe bench path (e.g., /home/frappe/frappe-bench): " BENCH_PATH
read -p "Enter your site name (e.g., onco.local): " SITE_NAME
read -p "Enter installation method (1=Custom App, 2=Direct Copy): " INSTALL_METHOD

# Validate inputs
if [ ! -d "$BENCH_PATH" ]; then
    print_error "Bench path does not exist: $BENCH_PATH"
    exit 1
fi

if [ ! -d "$BENCH_PATH/sites/$SITE_NAME" ]; then
    print_error "Site does not exist: $SITE_NAME"
    exit 1
fi

# Get current directory (where this script is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ONCO_SOURCE="$SCRIPT_DIR"

print_status "Installation Parameters:"
print_status "  Bench Path: $BENCH_PATH"
print_status "  Site Name: $SITE_NAME"
print_status "  Source Path: $ONCO_SOURCE"
print_status "  Install Method: $INSTALL_METHOD"

echo ""
read -p "Continue with installation? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installation cancelled."
    exit 0
fi

# Change to bench directory
cd "$BENCH_PATH"

if [ "$INSTALL_METHOD" = "1" ]; then
    print_step "Installing as Custom App..."
    
    # Method 1: Custom App Installation
    print_status "Copying onco app to apps directory..."
    
    # Create apps/onco directory if it doesn't exist
    mkdir -p "$BENCH_PATH/apps/onco"
    
    # Copy all files
    cp -r "$ONCO_SOURCE/onco" "$BENCH_PATH/apps/"
    cp "$ONCO_SOURCE/pyproject.toml" "$BENCH_PATH/apps/onco/" 2>/dev/null || true
    cp "$ONCO_SOURCE/setup.py" "$BENCH_PATH/apps/onco/" 2>/dev/null || true
    
    # Create __init__.py if it doesn't exist
    touch "$BENCH_PATH/apps/onco/__init__.py"
    
    print_status "Installing onco app..."
    bench --site "$SITE_NAME" install-app onco
    
elif [ "$INSTALL_METHOD" = "2" ]; then
    print_step "Installing via Direct Copy..."
    
    # Method 2: Direct File Copy
    print_status "Copying custom item fields..."
    mkdir -p "$BENCH_PATH/apps/erpnext/erpnext/custom"
    cp "$ONCO_SOURCE/onco/onco/custom/item.json" "$BENCH_PATH/apps/erpnext/erpnext/custom/"
    
    print_status "Copying doctypes..."
    mkdir -p "$BENCH_PATH/apps/erpnext/erpnext/onco_doctypes"
    cp -r "$ONCO_SOURCE/onco/onco/doctype"/* "$BENCH_PATH/apps/erpnext/erpnext/onco_doctypes/"
    
    print_warning "You may need to manually update hooks.py to include new doctypes"
    
else
    print_error "Invalid installation method. Choose 1 or 2."
    exit 1
fi

print_step "Running database migration..."
bench --site "$SITE_NAME" migrate

print_step "Clearing cache..."
bench --site "$SITE_NAME" clear-cache

print_step "Building assets..."
bench build --app erpnext

print_step "Restarting services..."
bench restart

print_status "✅ Installation completed successfully!"

echo ""
echo "🎯 NEXT STEPS:"
echo "=============="
print_status "1. Configure Naming Series:"
print_status "   - Go to Setup > Settings > Naming Series"
print_status "   - Add the naming series from INSTALLATION_PACKAGE_README.md"
echo ""
print_status "2. Setup Email Configuration:"
print_status "   - Go to Setup > Email > Email Account"
print_status "   - Configure SMTP settings for notifications"
echo ""
print_status "3. Create Test Data:"
print_status "   - Create pharmaceutical items with required fields"
print_status "   - Create test customers and suppliers"
echo ""
print_status "4. Run Testing Workflow:"
print_status "   - Follow COMPLETE_TESTING_WORKFLOW.md"
print_status "   - Test all critical business logic"
echo ""
print_status "5. Access the system:"
print_status "   - URL: http://localhost:8000 (or your server IP)"
print_status "   - Go to: Onco > Importation Approval Request"

echo ""
print_status "📚 Documentation Files:"
print_status "  - DEPLOYMENT_GUIDE_NO_ERPNEXT.md - Complete setup guide"
print_status "  - COMPLETE_TESTING_WORKFLOW.md - Testing instructions"
print_status "  - FINAL_IMPLEMENTATION_STATUS.md - Feature summary"
print_status "  - INSTALLATION_PACKAGE_README.md - Package overview"

echo ""
print_status "🎉 Importation Cycle is ready for testing!"
print_status "All HTML requirements have been implemented and are ready for use."

# Check if services are running
print_step "Checking system status..."
if pgrep -f "bench start" > /dev/null; then
    print_status "✅ Bench services are running"
else
    print_warning "⚠️  Bench services may not be running. Run 'bench start' if needed."
fi

# Final validation
if [ -d "$BENCH_PATH/apps/onco" ] || [ -d "$BENCH_PATH/apps/erpnext/erpnext/onco_doctypes" ]; then
    print_status "✅ Installation files are in place"
else
    print_error "❌ Installation files not found. Please check the installation."
fi

echo ""
print_status "Installation log completed. Check above for any errors or warnings."