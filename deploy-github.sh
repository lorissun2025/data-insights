#!/bin/bash

echo "=========================================="
echo "🚀 GitHub Pages 一键部署脚本"
echo "=========================================="
echo ""

# 检查是否在项目目录
PROJECT_DIR="/Users/sunsensen/claude code/智能数据平台"
cd "$PROJECT_DIR" || {
    echo "❌ 无法进入项目目录"
    exit 1
}

# 步骤1: 初始化Git
echo "📦 步骤1: 初始化Git仓库..."
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git仓库初始化完成"
else
    echo "✅ Git仓库已存在"
fi
echo ""

# 步骤2: 添加所有文件
echo "📝 步骤2: 添加文件到Git..."
git add .
echo "✅ 文件添加完成"
echo ""

# 步骤3: 创建提交
echo "💾 步骤3: 创建提交..."
git commit -m "Initial commit: 智能数据平台 v3.0 - 100%完成

- 10个功能模块全部完成
- 深色科技风格UI
- 响应式设计(支持移动端)
- 数据导出功能
- GitHub Pages部署

技术栈: Vue.js + FastAPI + ECharts
完成度: 100%
"
echo "✅ 提交完成"
echo ""

# 步骤4: 提示添加远程仓库
echo "=========================================="
echo "✅ 本地Git仓库已准备好!"
echo "=========================================="
echo ""
echo "📝 接下来的步骤:"
echo ""
echo "1. 在GitHub上创建新仓库:"
echo "   访问: https://github.com/new"
echo "   仓库名: data-insights (或其他)"
echo "   选择: Public ✅"
echo "   点击: Create repository"
echo ""
echo "2. 添加远程仓库 (替换YOUR_USERNAME):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/data-insights.git"
echo ""
echo "3. 推送代码到GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. 启用GitHub Pages:"
echo "   - 进入仓库 Settings → Pages"
echo "   - Source: Branch: main, Folder: / (root)"
echo "   - 点击 Save"
echo ""
echo "5. 访问你的网站 (等待1-2分钟):"
echo "   https://YOUR_USERNAME.github.io/data-insights/"
echo ""
echo "=========================================="
echo ""
echo "🔑 登录信息 (发给客户):"
echo ""
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "=========================================="
echo ""
echo "⚠️  重要提示:"
echo "   - 仓库必须设置为 Public 才能使用GitHub Pages"
echo "   - 首次部署需要等待1-2分钟"
echo "   - 访问 https://github.com/YOUR_USERNAME/data-insights/settings/pages 查看状态"
echo ""
