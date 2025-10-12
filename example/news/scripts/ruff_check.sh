#!/bin/bash
# Ruff-only code quality check script for Finance News AgentOS
# Skips compilation tests, focuses only on code quality

echo "🔍 Finance News AgentOS - Ruff Code Quality Check"
echo "=================================================="

cd "$(dirname "$0")/.."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if ruff is available
if ! command -v ruff &> /dev/null; then
    echo -e "${RED}❌ Ruff not found!${NC}"
    echo "Install with: pip install ruff>=0.1.0"
    exit 1
fi

echo -e "${GREEN}✅ Ruff is available${NC}"
echo ""

# Function to run ruff check
run_ruff_check() {
    local target="$1"
    local name="$2"

    echo -e "${BLUE}🔍 Checking $name...${NC}"

    # Count issues
    local issues=$(ruff check "$target" --quiet 2>/dev/null | wc -l)

    if [ "$issues" -eq 0 ]; then
        echo -e "${GREEN}✅ $name: No lint issues${NC}"
    else
        echo -e "${YELLOW}⚠️  $name: $issues lint issues${NC}"
        if [ "$1" = "--show-details" ]; then
            ruff check "$target" --show-source
        fi
    fi
}

# Function to run ruff format check
run_ruff_format_check() {
    local target="$1"
    local name="$2"

    echo -e "${BLUE}🎨 Checking $name formatting...${NC}"

    if ruff format --check "$target" &>/dev/null; then
        echo -e "${GREEN}✅ $name: Formatting OK${NC}"
    else
        echo -e "${YELLOW}⚠️  $name: Formatting issues${NC}"
        if [ "$1" = "--show-details" ]; then
            ruff format --diff "$target"
        fi
    fi
}

# Parse arguments
SHOW_DETAILS=false
AUTO_FIX=false
FORMAT_ONLY=false
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --show-details|-v)
            SHOW_DETAILS=true
            shift
            ;;
        --fix|-f)
            AUTO_FIX=true
            shift
            ;;
        --format-only)
            FORMAT_ONLY=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --show-details, -v    Show detailed issue reports"
            echo "  --fix, -f            Auto-fix issues"
            echo "  --format-only        Only run formatting"
            echo "  --check-only         Only run linting (no format check)"
            echo "  --help, -h           Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Auto-fix mode
if [ "$AUTO_FIX" = true ]; then
    echo -e "${YELLOW}🔧 Auto-fixing issues...${NC}"
    echo ""

    echo "Fixing lint issues..."
    ruff check src/ tests/ --fix

    echo "Fixing format issues..."
    ruff format src/ tests/

    echo ""
    echo -e "${GREEN}✅ Auto-fix complete!${NC}"
    exit 0
fi

# Format-only mode
if [ "$FORMAT_ONLY" = true ]; then
    echo -e "${YELLOW}🎨 Format-only mode${NC}"
    echo ""

    run_ruff_format_check "src/" "Source Code"
    run_ruff_format_check "tests/" "Test Code"

    exit 0
fi

# Check-only mode
if [ "$CHECK_ONLY" = true ]; then
    echo -e "${YELLOW}🔍 Lint-only mode${NC}"
    echo ""

    run_ruff_check "src/" "Source Code"
    run_ruff_check "tests/" "Test Code"

    exit 0
fi

# Full check mode (default)
echo -e "${YELLOW}🔍 Running full Ruff analysis...${NC}"
echo ""

# Run checks
run_ruff_check "src/" "Source Code"
run_ruff_format_check "src/" "Source Code"

echo ""
run_ruff_check "tests/" "Test Code"
run_ruff_format_check "tests/" "Test Code"

# Count total issues
TOTAL_LINT_ISSUES=$(ruff check src/ tests/ --quiet 2>/dev/null | wc -l)
FORMAT_ISSUES=0

if ! ruff format --check src/ &>/dev/null; then
    FORMAT_ISSUES=$((FORMAT_ISSUES + 1))
fi

if ! ruff format --check tests/ &>/dev/null; then
    FORMAT_ISSUES=$((FORMAT_ISSUES + 1))
fi

echo ""
echo "=================================================="
echo -e "${YELLOW}📊 SUMMARY${NC}"
echo "=================================================="
echo -e "Lint Issues: ${YELLOW}$TOTAL_LINT_ISSUES${NC}"
echo -e "Format Issues: ${YELLOW}$FORMAT_ISSUES${NC}"

if [ $TOTAL_LINT_ISSUES -eq 0 ] && [ $FORMAT_ISSUES -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Perfect! No code quality issues found.${NC}"
    echo ""
    echo -e "${BLUE}💡 Next: Run type checking with MyPy${NC}"
    echo "  ./scripts/mypy_check.sh"
    exit 0
else
    echo ""
    echo -e "${YELLOW}💡 To fix issues automatically:${NC}"
    echo "  $0 --fix"
    echo ""
    echo -e "${YELLOW}💡 To see detailed reports:${NC}"
    echo "  $0 --show-details"
    echo ""
    echo -e "${YELLOW}💡 Manual fix commands:${NC}"
    echo "  ruff check src/ tests/ --fix     # Fix lint issues"
    echo "  ruff format src/ tests/          # Fix format issues"
    echo ""
    echo -e "${BLUE}💡 After fixing: Run type checking with MyPy${NC}"
    echo "  ./scripts/mypy_check.sh"
    exit 2
fi