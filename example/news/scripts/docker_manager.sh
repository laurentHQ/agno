#!/bin/bash
# Docker Compose Management Script for Finance News AgentOS
# Usage: ./scripts/docker_manager.sh [command] [options]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Docker Compose file path
COMPOSE_FILE="docker/docker-compose.yml"
PROJECT_NAME="finance-agentos"

# Helper functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if docker compose file exists
check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found"
        if [ -f config/.env.example ]; then
            print_info "Creating .env from template..."
            cp config/.env.example .env
            print_warning "Please edit .env with your API keys"
            exit 1
        else
            print_error "No .env.example template found"
            exit 1
        fi
    fi
}

# Command implementations
cmd_start() {
    print_header "🚀 Starting Services"
    check_compose_file
    check_env_file

    docker compose -f "$COMPOSE_FILE" up -d "$@"

    print_success "Services started successfully"
    print_info "Run './scripts/docker_manager.sh logs' to view logs"
    print_info "Run './scripts/docker_manager.sh status' to check service status"
}

cmd_stop() {
    print_header "⏹️  Stopping Services"
    check_compose_file

    docker compose -f "$COMPOSE_FILE" stop "$@"
    print_success "Services stopped"
}

cmd_restart() {
    print_header "🔄 Restarting Services"
    check_compose_file

    if [ -z "$1" ]; then
        docker compose -f "$COMPOSE_FILE" restart
        print_success "All services restarted"
    else
        docker compose -f "$COMPOSE_FILE" restart "$@"
        print_success "Service(s) restarted: $*"
    fi
}

cmd_down() {
    print_header "🛑 Stopping and Removing Containers"
    check_compose_file

    read -p "This will stop and remove all containers. Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose -f "$COMPOSE_FILE" down
        print_success "Containers stopped and removed"
    else
        print_info "Operation cancelled"
    fi
}

cmd_logs() {
    print_header "📋 Service Logs"
    check_compose_file

    if [ -z "$1" ]; then
        docker compose -f "$COMPOSE_FILE" logs -f --tail=100
    else
        docker compose -f "$COMPOSE_FILE" logs -f --tail=100 "$@"
    fi
}

cmd_status() {
    print_header "📊 Service Status"
    check_compose_file

    docker compose -f "$COMPOSE_FILE" ps
    echo ""

    # Show health status
    print_info "Health Status:"
    docker ps --filter "name=finance-" --format "table {{.Names}}\t{{.Status}}"
}

cmd_build() {
    print_header "🔨 Building Images"
    check_compose_file
    check_env_file

    if [ "$1" = "--no-cache" ]; then
        shift
        docker compose -f "$COMPOSE_FILE" build --no-cache "$@"
    else
        docker compose -f "$COMPOSE_FILE" build "$@"
    fi

    print_success "Build completed"
}

cmd_clean() {
    print_header "🧹 Cleaning Up"
    check_compose_file

    echo "This will:"
    echo "  - Stop and remove all containers"
    echo "  - Remove all volumes (DATABASE WILL BE DELETED)"
    echo "  - Remove networks"
    echo ""
    read -p "Are you sure? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose -f "$COMPOSE_FILE" down -v
        print_success "Cleanup completed"
        print_warning "All data has been removed"
    else
        print_info "Operation cancelled"
    fi
}

cmd_exec() {
    print_header "💻 Execute Command"
    check_compose_file

    if [ -z "$1" ]; then
        print_error "Please specify a service name"
        echo "Available services: finance-agentos, postgres, redis"
        exit 1
    fi

    service="$1"
    shift

    if [ -z "$1" ]; then
        # Default to bash shell
        docker compose -f "$COMPOSE_FILE" exec "$service" /bin/bash
    else
        # Execute specified command
        docker compose -f "$COMPOSE_FILE" exec "$service" "$@"
    fi
}

cmd_shell() {
    print_header "🐚 Opening Shell"

    service="${1:-finance-agentos}"

    print_info "Opening shell in: $service"
    docker compose -f "$COMPOSE_FILE" exec "$service" /bin/bash
}

cmd_db_shell() {
    print_header "🗄️  Opening Database Shell"
    check_compose_file

    print_info "Connecting to PostgreSQL..."
    docker compose -f "$COMPOSE_FILE" exec postgres psql -U agentos -d finance_agent
}

cmd_redis_shell() {
    print_header "🔴 Opening Redis Shell"
    check_compose_file

    print_info "Connecting to Redis..."
    docker compose -f "$COMPOSE_FILE" exec redis redis-cli
}

cmd_pull() {
    print_header "📥 Pulling Latest Images"
    check_compose_file

    docker compose -f "$COMPOSE_FILE" pull
    print_success "Images pulled successfully"
}

cmd_prune() {
    print_header "🗑️  Pruning Docker Resources"

    echo "This will remove:"
    echo "  - All stopped containers"
    echo "  - All unused networks"
    echo "  - All dangling images"
    echo "  - All build cache"
    echo ""
    read -p "Continue? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -af
        print_success "Pruning completed"
    else
        print_info "Operation cancelled"
    fi
}

cmd_backup() {
    print_header "💾 Database Backup"
    check_compose_file

    backup_dir="data/backups"
    mkdir -p "$backup_dir"

    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="$backup_dir/finance_agent_${timestamp}.sql"

    print_info "Creating backup: $backup_file"
    docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U agentos finance_agent > "$backup_file"

    if [ $? -eq 0 ]; then
        print_success "Backup created: $backup_file"

        # Compress backup
        gzip "$backup_file"
        print_success "Backup compressed: ${backup_file}.gz"
    else
        print_error "Backup failed"
        exit 1
    fi
}

cmd_restore() {
    print_header "📤 Database Restore"
    check_compose_file

    if [ -z "$1" ]; then
        print_error "Please specify backup file"
        echo "Available backups:"
        ls -lh data/backups/*.sql.gz 2>/dev/null || echo "No backups found"
        exit 1
    fi

    backup_file="$1"

    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi

    print_warning "This will overwrite the current database"
    read -p "Continue? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Restoring from: $backup_file"

        # Check if file is compressed
        if [[ "$backup_file" == *.gz ]]; then
            gunzip -c "$backup_file" | docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U agentos finance_agent
        else
            docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U agentos finance_agent < "$backup_file"
        fi

        if [ $? -eq 0 ]; then
            print_success "Restore completed"
        else
            print_error "Restore failed"
            exit 1
        fi
    else
        print_info "Operation cancelled"
    fi
}

cmd_help() {
    cat << EOF
🐳 Docker Compose Manager for Finance News AgentOS

USAGE:
    ./scripts/docker_manager.sh [command] [options]

COMMANDS:
    Service Management:
        start [service]        Start all services or specific service
        stop [service]         Stop all services or specific service
        restart [service]      Restart all services or specific service
        down                   Stop and remove containers
        status                 Show service status and health

    Logs & Monitoring:
        logs [service]         Follow logs (default: all services)
        status                 Show service status

    Build & Images:
        build [--no-cache]     Build or rebuild images
        pull                   Pull latest images

    Shell Access:
        shell [service]        Open bash shell (default: finance-agentos)
        exec <service> [cmd]   Execute command in service
        db                     Open PostgreSQL shell
        redis                  Open Redis CLI

    Database Operations:
        backup                 Create database backup
        restore <file>         Restore database from backup

    Cleanup:
        clean                  Remove all containers, volumes, networks
        prune                  Prune unused Docker resources

    Information:
        help                   Show this help message

EXAMPLES:
    ./scripts/docker_manager.sh start
    ./scripts/docker_manager.sh logs finance-agentos
    ./scripts/docker_manager.sh restart postgres
    ./scripts/docker_manager.sh build --no-cache
    ./scripts/docker_manager.sh shell finance-agentos
    ./scripts/docker_manager.sh backup
    ./scripts/docker_manager.sh restore data/backups/finance_agent_20250114.sql.gz

SERVICES:
    finance-agentos        Main application (port 8080)
    postgres               PostgreSQL database (port 5432)
    redis                  Redis cache (port 6379)

EOF
}

# Main command dispatcher
main() {
    if [ $# -eq 0 ]; then
        cmd_help
        exit 0
    fi

    command="$1"
    shift

    case "$command" in
        start|up)
            cmd_start "$@"
            ;;
        stop)
            cmd_stop "$@"
            ;;
        restart)
            cmd_restart "$@"
            ;;
        down)
            cmd_down
            ;;
        logs|log)
            cmd_logs "$@"
            ;;
        status|ps)
            cmd_status
            ;;
        build)
            cmd_build "$@"
            ;;
        clean)
            cmd_clean
            ;;
        exec)
            cmd_exec "$@"
            ;;
        shell|sh|bash)
            cmd_shell "$@"
            ;;
        db|database|psql)
            cmd_db_shell
            ;;
        redis|redis-cli)
            cmd_redis_shell
            ;;
        pull)
            cmd_pull
            ;;
        prune)
            cmd_prune
            ;;
        backup)
            cmd_backup
            ;;
        restore)
            cmd_restore "$@"
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
