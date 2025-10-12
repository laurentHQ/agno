#!/bin/bash
# Comprehensive compilation and code quality test script for Finance News AgentOS
# Tests all Python files for compilation, imports, and code quality with Ruff

echo "🔍 Finance News AgentOS - Compilation & Code Quality Test Suite"
echo "======================================================================"

cd "$(dirname "$0")/.."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_FILES=0
PASSED_FILES=0
FAILED_FILES=0
RUFF_ISSUES=0
MYPY_ISSUES=0

# Check if ruff is available
RUFF_AVAILABLE=false
if command -v ruff &> /dev/null; then
    RUFF_AVAILABLE=true
    echo -e "${GREEN}✅ Ruff is available for code quality checks${NC}"
else
    echo -e "${YELLOW}⚠️  Ruff not found - skipping code quality checks${NC}"
    echo "   Install with: pip install ruff>=0.1.0"
fi

# Check if mypy is available
MYPY_AVAILABLE=false
if command -v mypy &> /dev/null; then
    MYPY_AVAILABLE=true
    echo -e "${GREEN}✅ MyPy is available for type checking${NC}"
else
    echo -e "${YELLOW}⚠️  MyPy not found - skipping type checking${NC}"
    echo "   Install with: pip install mypy>=1.0.0"
fi

# Function to test compilation
test_compile() {
    local file="$1"
    local description="$2"

    TOTAL_FILES=$((TOTAL_FILES + 1))

    if python -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $description - OK"
        PASSED_FILES=$((PASSED_FILES + 1))
    else
        echo -e "${RED}❌${NC} $description - COMPILATION ERROR"
        python -m py_compile "$file"
        FAILED_FILES=$((FAILED_FILES + 1))
    fi
}

# Function to test imports
test_import() {
    local module="$1"
    local description="$2"

    TOTAL_FILES=$((TOTAL_FILES + 1))

    if python -c "import sys; sys.path.insert(0, '.'); import $module" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $description - OK"
        PASSED_FILES=$((PASSED_FILES + 1))
    else
        echo -e "${RED}❌${NC} $description - IMPORT ERROR"
        python -c "import sys; sys.path.insert(0, '.'); import $module"
        FAILED_FILES=$((FAILED_FILES + 1))
    fi
}

# Function to test with Ruff
test_ruff() {
    local file_or_dir="$1"
    local description="$2"
    local check_type="$3"  # "check" or "format"

    if [ "$RUFF_AVAILABLE" = false ]; then
        return 0
    fi

    if [ "$check_type" = "format" ]; then
        # Test formatting
        if ruff format --check "$file_or_dir" &>/dev/null; then
            echo -e "${GREEN}✅${NC} $description - Format OK"
        else
            echo -e "${YELLOW}⚠️${NC} $description - Format issues (fixable with: ruff format $file_or_dir)"
            RUFF_ISSUES=$((RUFF_ISSUES + 1))
        fi
    else
        # Test linting
        local issues=$(ruff check "$file_or_dir" --quiet 2>/dev/null | wc -l)
        if [ "$issues" -eq 0 ]; then
            echo -e "${GREEN}✅${NC} $description - Lint OK"
        else
            echo -e "${YELLOW}⚠️${NC} $description - $issues lint issues (run: ruff check $file_or_dir)"
            RUFF_ISSUES=$((RUFF_ISSUES + issues))
        fi
    fi
}

# Function to test with MyPy
test_mypy() {
    local file_or_dir="$1"
    local description="$2"

    if [ "$MYPY_AVAILABLE" = false ]; then
        return 0
    fi

    local errors=$(mypy "$file_or_dir" 2>/dev/null | grep -c "error:" || true)
    if [ "$errors" -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $description - Type Check OK"
    else
        echo -e "${YELLOW}⚠️${NC} $description - $errors type errors (run: mypy $file_or_dir)"
        MYPY_ISSUES=$((MYPY_ISSUES + errors))
    fi
}

# Function to run comprehensive ruff checks
run_ruff_suite() {
    if [ "$RUFF_AVAILABLE" = false ]; then
        echo -e "${YELLOW}⚠️  Skipping Ruff checks - not available${NC}"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}🔍 Ruff Code Quality Checks${NC}"
    echo "--------------------------------------------"

    echo "Running Ruff linter on src/ directory..."
    test_ruff "src/" "Source Code Linting" "check"

    echo "Running Ruff formatter check on src/ directory..."
    test_ruff "src/" "Source Code Formatting" "format"

    echo "Running Ruff on tests/ directory..."
    test_ruff "tests/" "Test Code Quality" "check"

    # Show detailed output if there are issues
    if [ "$RUFF_ISSUES" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}📋 Detailed Ruff Report:${NC}"
        echo "Run the following commands to see detailed issues:"
        echo "  ruff check src/ tests/ --show-source"
        echo "  ruff format --diff src/ tests/"
        echo ""
        echo "To auto-fix issues:"
        echo "  ruff check src/ tests/ --fix"
        echo "  ruff format src/ tests/"
    fi
}

# Function to run comprehensive mypy checks
run_mypy_suite() {
    if [ "$MYPY_AVAILABLE" = false ]; then
        echo -e "${YELLOW}⚠️  Skipping MyPy checks - not available${NC}"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}🔍 MyPy Type Checking${NC}"
    echo "--------------------------------------------"

    echo "Running MyPy on src/ directory..."
    test_mypy "src/" "Source Code Type Checking"

    echo "Running MyPy on tests/ directory..."
    test_mypy "tests/" "Test Code Type Checking"

    # Show detailed output if there are issues
    if [ "$MYPY_ISSUES" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}📋 Detailed MyPy Report:${NC}"
        echo "Run the following commands to see detailed type errors:"
        echo "  mypy src/ --show-error-codes"
        echo "  mypy tests/ --show-error-codes"
        echo ""
        echo "MyPy configuration is in pyproject.toml [tool.mypy] section"
    fi
}

echo -e "${YELLOW}📁 Testing Core Modules${NC}"
echo "------------------------------"
test_compile "src/core/cache_manager.py" "Cache Manager"
test_compile "src/core/scheduler.py" "Task Scheduler"
test_import "src.core.cache_manager" "Cache Manager Import"
test_import "src.core.scheduler" "Task Scheduler Import"

echo ""
echo -e "${YELLOW}🤖 Testing Agent Modules${NC}"
echo "------------------------------"
test_compile "src/agents/finance_news_agent.py" "Finance News Agent"
test_compile "src/agents/tech_news_hub.py" "Tech News Hub"
test_compile "src/agents/github_trending_agent.py" "GitHub Trending Agent"
test_compile "src/agents/multisource_news_agent.py" "Multisource News Agent"
test_import "src.agents.finance_news_agent" "Finance Agent Import"
test_import "src.agents.tech_news_hub" "Tech News Import"
test_import "src.agents.github_trending_agent" "GitHub Agent Import"
test_import "src.agents.multisource_news_agent" "Multisource Agent Import"

echo ""
echo -e "${YELLOW}🌐 Testing API Modules${NC}"
echo "-" * 30
test_compile "src/api/finance_agentos.py" "Finance AgentOS Full"
test_compile "src/api/finance_agentos_lite.py" "Finance AgentOS Lite"
test_compile "src/api/launcher.py" "Agent Launcher"

echo ""
echo -e "${YELLOW}🛠️ Testing Utility Modules${NC}"
echo "-" * 30
test_compile "src/utils/config_loader.py" "Configuration Loader"
test_compile "src/utils/model_selector.py" "Model Selector"
test_compile "src/utils/report_utils.py" "Report Utilities"
test_compile "src/utils/news_reporter.py" "News Reporter"
test_compile "src/utils/github_trending_reporter.py" "GitHub Trending Reporter"
test_compile "src/utils/configure_model.py" "Model Configuration"
test_import "src.utils.config_loader" "Config Loader Import"
test_import "src.utils.model_selector" "Model Selector Import"
test_import "src.utils.report_utils" "Report Utils Import"
test_import "src.utils.news_reporter" "News Reporter Import"
test_import "src.utils.github_trending_reporter" "GitHub Reporter Import"

echo ""
echo -e "${YELLOW}🧪 Testing Example/Test Files${NC}"
echo "-" * 30
for test_file in tests/*.py; do
    if [ -f "$test_file" ]; then
        filename=$(basename "$test_file")
        test_compile "$test_file" "Test: $filename"
    fi
done

echo ""
echo -e "${YELLOW}📊 Comprehensive Test - All Source Files${NC}"
echo "-" * 30

# Test all Python files in src directory
echo "Testing all .py files in src/ directory..."
find src/ -name "*.py" -print0 | while IFS= read -r -d '' file; do
    if python -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $(basename "$file")"
    else
        echo -e "${RED}❌${NC} $(basename "$file") - ERROR"
    fi
done

# Run Ruff code quality checks
run_ruff_suite

# Run MyPy type checking
run_mypy_suite

echo ""
echo "======================================================================"
echo -e "${YELLOW}📈 FINAL RESULTS${NC}"
echo "======================================================================"
echo "Compilation Tests: $TOTAL_FILES"
echo -e "Passed: ${GREEN}$PASSED_FILES${NC}"
echo -e "Failed: ${RED}$FAILED_FILES${NC}"

if [ "$RUFF_AVAILABLE" = true ]; then
    echo -e "Ruff Issues: ${YELLOW}$RUFF_ISSUES${NC}"
fi

if [ "$MYPY_AVAILABLE" = true ]; then
    echo -e "MyPy Issues: ${YELLOW}$MYPY_ISSUES${NC}"
fi

echo ""
if [ $FAILED_FILES -eq 0 ]; then
    total_quality_issues=$((RUFF_ISSUES + MYPY_ISSUES))
    if [ $total_quality_issues -gt 0 ]; then
        echo -e "${YELLOW}✅ Compilation passed, but code quality/type issues found!${NC}"
        if [ "$RUFF_AVAILABLE" = true ] && [ $RUFF_ISSUES -gt 0 ]; then
            echo -e "${YELLOW}   Run 'ruff check src/ tests/ --fix' to auto-fix Ruff issues${NC}"
        fi
        if [ "$MYPY_AVAILABLE" = true ] && [ $MYPY_ISSUES -gt 0 ]; then
            echo -e "${YELLOW}   Run 'mypy src/ tests/' to see detailed type errors${NC}"
        fi
        exit 2  # Different exit code for quality issues
    else
        echo -e "${GREEN}🎉 ALL TESTS PASSED! Code is clean, well-structured, and type-safe.${NC}"
        exit 0
    fi
else
    echo -e "${RED}⚠️  Compilation errors found. Please fix the errors above.${NC}"
    exit 1
fi