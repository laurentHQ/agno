#!/bin/bash
# MyPy Type Checking Script for Finance News AgentOS
# Provides comprehensive type checking with detailed reporting and options

echo "🔍 Finance News AgentOS - MyPy Type Checking"
echo "============================================"

cd "$(dirname "$0")/.."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
SHOW_DETAILED=false
CHECK_ONLY_ERRORS=false
STRICT_MODE=false

# Check if MyPy is available
if ! command -v mypy &> /dev/null; then
    echo -e "${RED}❌ MyPy not found!${NC}"
    echo "Install with: pip install mypy>=1.0.0"
    exit 1
fi

echo -e "${GREEN}✅ MyPy is available${NC}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --detailed|-d)
            SHOW_DETAILED=true
            shift
            ;;
        --errors-only|-e)
            CHECK_ONLY_ERRORS=true
            shift
            ;;
        --strict|-s)
            STRICT_MODE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --detailed, -d     Show detailed type checking output"
            echo "  --errors-only, -e  Show only errors (no success messages)"
            echo "  --strict, -s       Use strict mode (override config)"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Basic type checking"
            echo "  $0 --detailed         # Detailed output with all information"
            echo "  $0 --errors-only      # Only show errors and warnings"
            echo "  $0 --strict           # Use strict type checking"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to run MyPy with options
run_mypy_check() {
    local target="$1"
    local description="$2"

    echo ""
    echo -e "${BLUE}🔍 Checking: $description${NC}"
    echo "Target: $target"
    echo "----------------------------------------"

    # Build MyPy command
    local mypy_cmd="mypy $target"

    if [ "$STRICT_MODE" = true ]; then
        mypy_cmd="$mypy_cmd --strict"
    fi

    if [ "$SHOW_DETAILED" = true ]; then
        mypy_cmd="$mypy_cmd --show-error-codes --show-error-context"
    fi

    # Run MyPy and capture output
    local output
    local exit_code
    output=$(eval "$mypy_cmd" 2>&1)
    exit_code=$?

    # Count errors and warnings
    local error_count=$(echo "$output" | grep -c "error:" || true)
    local warning_count=$(echo "$output" | grep -c "warning:" || true)
    local note_count=$(echo "$output" | grep -c "note:" || true)

    # Check for "no files" message which should not be considered an error
    local no_files_msg=$(echo "$output" | grep -c "There are no .py\[i\] files in directory" || true)

    # Display results
    if [ $exit_code -eq 0 ] || [ $no_files_msg -gt 0 ]; then
        if [ "$CHECK_ONLY_ERRORS" = false ]; then
            if [ $no_files_msg -gt 0 ]; then
                echo -e "${YELLOW}⚠️  No Python files found in target${NC}"
            else
                echo -e "${GREEN}✅ Type checking passed!${NC}"
            fi
            if [ $note_count -gt 0 ] && [ "$SHOW_DETAILED" = true ]; then
                echo -e "${BLUE}ℹ️  Notes: $note_count${NC}"
            fi
        fi
        exit_code=0  # Override exit code for no files case
    else
        echo -e "${RED}❌ Type checking failed${NC}"
        echo -e "${RED}Errors: $error_count${NC}"
        if [ $warning_count -gt 0 ]; then
            echo -e "${YELLOW}Warnings: $warning_count${NC}"
        fi
        if [ $note_count -gt 0 ]; then
            echo -e "${BLUE}Notes: $note_count${NC}"
        fi
    fi

    # Show output if there are issues or detailed mode is enabled
    if [ $exit_code -ne 0 ] || [ "$SHOW_DETAILED" = true ]; then
        if [ -n "$output" ]; then
            echo ""
            echo "MyPy Output:"
            echo "$output"
        fi
    fi

    return $exit_code
}

# Track overall results
TOTAL_ERRORS=0
TOTAL_WARNINGS=0

echo -e "${YELLOW}🎯 Starting MyPy Type Checking...${NC}"

# Check source code
if run_mypy_check "src/" "Source Code (src/)"; then
    if [ "$CHECK_ONLY_ERRORS" = false ]; then
        echo -e "${GREEN}✅ Source code type checking passed${NC}"
    fi
else
    echo -e "${RED}❌ Source code has type issues${NC}"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi

# Check tests if they exist
if [ -d "tests" ] && [ "$(find tests -name "*.py" | wc -l)" -gt 0 ]; then
    if run_mypy_check "tests/" "Test Code (tests/)"; then
        if [ "$CHECK_ONLY_ERRORS" = false ]; then
            echo -e "${GREEN}✅ Test code type checking passed${NC}"
        fi
    else
        echo -e "${RED}❌ Test code has type issues${NC}"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    fi
fi

# Final summary
echo ""
echo "============================================"
echo -e "${YELLOW}📊 MyPy Type Checking Summary${NC}"
echo "============================================"

if [ $TOTAL_ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 All type checking passed!${NC}"
    echo -e "${GREEN}Code is type-safe and well-annotated.${NC}"

    if [ "$SHOW_DETAILED" = false ]; then
        echo ""
        echo -e "${BLUE}💡 Tip: Use --detailed flag to see more information${NC}"
    fi

    exit 0
else
    echo -e "${RED}⚠️  Type checking issues found in $TOTAL_ERRORS target(s)${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "1. Review the type errors shown above"
    echo "2. Add type annotations where missing"
    echo "3. Fix type mismatches and inconsistencies"
    echo "4. Run 'mypy src/ --show-error-codes' for detailed error information"
    echo ""
    echo -e "${BLUE}💡 Configuration:${NC}"
    echo "MyPy settings are configured in pyproject.toml [tool.mypy] section"

    exit 1
fi