#!/bin/bash
# 店小秘API服务一键部署脚本

set -e

echo "========================================"
echo "店小秘API服务部署脚本"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="/home/user/dxm_gendanIW"
SERVICE_FILE="dxm-api.service"

echo -e "\n${YELLOW}步骤1: 检查依赖${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: Python3未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3已安装${NC}"

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}错误: pip3未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3已安装${NC}"

echo -e "\n${YELLOW}步骤2: 安装Python依赖${NC}"
cd "$PROJECT_DIR"
pip3 install -r requirements.txt gunicorn
echo -e "${GREEN}✓ Python依赖安装完成${NC}"

echo -e "\n${YELLOW}步骤3: 创建日志目录${NC}"
mkdir -p "$PROJECT_DIR/logs"
chmod 755 "$PROJECT_DIR/logs"
echo -e "${GREEN}✓ 日志目录创建完成${NC}"

echo -e "\n${YELLOW}步骤4: 测试Cookie管理器${NC}"
python3 "$PROJECT_DIR/cookie_manager.py"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cookie管理器测试通过${NC}"
else
    echo -e "${RED}✗ Cookie管理器测试失败${NC}"
    exit 1
fi

echo -e "\n${YELLOW}步骤5: 安装systemd服务${NC}"
sudo cp "$PROJECT_DIR/$SERVICE_FILE" /etc/systemd/system/
sudo systemctl daemon-reload
echo -e "${GREEN}✓ systemd服务已安装${NC}"

echo -e "\n${YELLOW}步骤6: 启动服务${NC}"
sudo systemctl enable dxm-api
sudo systemctl restart dxm-api
sleep 3

echo -e "\n${YELLOW}步骤7: 检查服务状态${NC}"
if sudo systemctl is-active --quiet dxm-api; then
    echo -e "${GREEN}✓ 服务运行正常${NC}"
    sudo systemctl status dxm-api --no-pager
else
    echo -e "${RED}✗ 服务启动失败，查看日志：${NC}"
    sudo journalctl -u dxm-api -n 50 --no-pager
    exit 1
fi

echo -e "\n${YELLOW}步骤8: 测试API${NC}"
sleep 2
if curl -s http://localhost:5000/ > /dev/null; then
    echo -e "${GREEN}✓ API测试通过${NC}"
    echo -e "\n${GREEN}API文档地址: http://localhost:5000/${NC}"
else
    echo -e "${RED}✗ API测试失败${NC}"
    exit 1
fi

echo -e "\n========================================"
echo -e "${GREEN}部署完成！${NC}"
echo -e "========================================"
echo -e "\n常用命令："
echo -e "  查看状态:   ${YELLOW}sudo systemctl status dxm-api${NC}"
echo -e "  查看日志:   ${YELLOW}sudo journalctl -u dxm-api -f${NC}"
echo -e "  重启服务:   ${YELLOW}sudo systemctl restart dxm-api${NC}"
echo -e "  停止服务:   ${YELLOW}sudo systemctl stop dxm-api${NC}"
echo -e "  访问日志:   ${YELLOW}tail -f $PROJECT_DIR/logs/access.log${NC}"
echo -e "  错误日志:   ${YELLOW}tail -f $PROJECT_DIR/logs/error.log${NC}"
echo ""
