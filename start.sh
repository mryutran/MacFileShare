#!/bin/bash

# 🍎 Mac File Share - Script khởi động nhanh
# ==========================================

# Màu sắc cho terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║                                                          ║"
echo "  ║        🍎 MAC FILE SHARE                                 ║"
echo "  ║        Chia sẻ file từ Mac sang iPhone                   ║"
echo "  ║                                                          ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Thư mục mặc định
DEFAULT_DIR="$HOME/Downloads"
SHARE_DIR="${1:-$DEFAULT_DIR}"
PORT="${2:-8888}"

# Kiểm tra thư mục
if [ ! -d "$SHARE_DIR" ]; then
    echo -e "${RED}❌ Thư mục không tồn tại: $SHARE_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}📁 Thư mục chia sẻ: ${YELLOW}$SHARE_DIR${NC}"
echo -e "${GREEN}🔌 Port: ${YELLOW}$PORT${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Chạy server
cd "$(dirname "$0")"
python3 server.py "$SHARE_DIR" "$PORT"

