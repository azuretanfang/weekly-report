# GitHub Pages 部署指南

## 📦 准备工作

所有文件已准备就绪！现在需要您完成以下步骤：

---

## 🚀 部署步骤

### 1️⃣ 配置Git（首次使用需要）

在终端运行：

```bash
# 设置您的GitHub用户名和邮箱
git config --global user.name "您的GitHub用户名"
git config --global user.email "您的GitHub邮箱"
```

### 2️⃣ 在GitHub创建新仓库

1. 访问：https://github.com/new
2. **Repository name**：建议填写 `telecom-weekly` 或 `weekly-report`
3. 选择 **Public**（公开仓库）
4. **不要**勾选任何初始化选项
5. 点击 **Create repository**

### 3️⃣ 推送代码到GitHub

创建完仓库后，复制仓库的URL（类似 `https://github.com/用户名/仓库名.git`），然后在终端运行：

```bash
# 进入项目目录
cd "/Users/tanfang/CodeBuddy/fangtan的工作台/运营商行业周报"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 添加运营商行业周报"

# 设置主分支名称
git branch -M main

# 添加远程仓库（替换为您的仓库地址）
git remote add origin https://github.com/您的用户名/您的仓库名.git

# 推送到GitHub
git push -u origin main
```

### 4️⃣ 启用GitHub Pages

1. 在GitHub仓库页面，点击 **Settings**（设置）
2. 左侧菜单找到 **Pages**
3. 在 **Source** 下拉菜单中选择：
   - Branch: `main`
   - Folder: `/ (root)`
4. 点击 **Save**

### 5️⃣ 等待部署完成

GitHub会自动构建和部署，通常需要 **1-3分钟**。

部署完成后，会显示访问地址：
```
https://您的用户名.github.io/仓库名称/
```

---

## 🎯 访问您的周报

- **首页**：`https://您的用户名.github.io/仓库名称/`
- **最新周报**：`https://您的用户名.github.io/仓库名称/weekly-report-0216-0222.html`

---

## 🔄 后续更新

当您有新的周报需要发布时：

```bash
cd "/Users/tanfang/CodeBuddy/fangtan的工作台/运营商行业周报"

# 添加新文件
git add .

# 提交更改
git commit -m "添加新周报"

# 推送到GitHub
git push
```

GitHub Pages会自动更新，无需额外操作！

---

## ❓ 常见问题

**Q: 推送时要求输入用户名和密码？**

A: GitHub已不支持密码认证，需要使用Personal Access Token：
1. 访问 https://github.com/settings/tokens
2. 生成新token（classic）
3. 选择 `repo` 权限
4. 复制token，推送时用token替代密码

**Q: 如何使用自定义域名？**

A: 在仓库根目录添加 `CNAME` 文件，内容为您的域名（如 `weekly.yourdomain.com`），然后在域名DNS设置中添加CNAME记录指向 `您的用户名.github.io`

---

## 📞 需要帮助？

如果在部署过程中遇到问题，请告诉我具体的错误信息，我会帮您解决！
