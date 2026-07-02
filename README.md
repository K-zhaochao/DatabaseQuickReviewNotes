# DatabaseQuickReviewNotes

数据库课程的速通笔记，涵盖 9 个课时的核心知识点，可部署为静态网站，方便电脑端和手机端考前速查。

## 📁 项目结构

```
DatabaseQuickReviewNotes/
├── 课时1绪论.md              # 原始 Obsidian 笔记（不动）
├── 课时2关系数据库.md
├── 课时3SQL.md
├── 课时4数据库安全性.md
├── 课时5数据库完整性.md
├── 课时6关系数据库理论.md
├── 课时7数据库设计概述.md
├── 课时8数据库恢复技术.md
├── 课时9并发控制.md
├── Images/                   # 笔记中引用的图片
├── Web/
│   ├── index.html            # 生成的单页静态网站
│   └── build.py              # 从 MD 生成 index.html 的脚本
└── README.md
```

## 🚀 快速开始

直接双击打开 `Web/index.html` 即可在浏览器中查看，无需任何服务器。

## 🔧 重新生成

如果修改了原始 `.md` 笔记，在 `Web/` 目录下重新运行生成脚本：

```powershell
cd Web
python build.py
```

## 🌐 部署方案

### 方案一：GitHub Pages（免费，推荐）

1. 将整个项目推送到 GitHub 仓库
2. 在仓库 `Settings → Pages` 中：
   - **Source**：选择 `Deploy from a branch`
   - **Branch**：选择 `main`（或 `master`），文件夹选 `/ (root)`
   - 点击 **Save**
3. 等待几分钟后，访问 `https://<你的用户名>.github.io/DatabaseQuickReviewNotes/Web/`

> 💡 如果需要根域名访问，可以将 `Web/` 下的文件移到仓库根目录。

### 方案二：Vercel / Netlify（免费，自动部署）

**Vercel：**

1. 注册 [vercel.com](https://vercel.com)，绑定 GitHub
2. 导入仓库，**Root Directory** 设置为 `Web`
3. 部署即可，每次 push 自动更新

**Netlify：**

1. 注册 [netlify.com](https://netlify.com)，绑定 GitHub
2. 导入仓库，**Base directory** 设置为 `Web`
3. 部署即可，支持自定义域名

### 方案三：Nginx / Apache 服务器

将 `Web/` 目录下的所有文件上传到服务器的网站根目录：

```bash
# Nginx 示例配置
server {
    listen       80;
    server_name  your-domain.com;
    root         /var/www/database-notes;
    index        index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

然后上传文件：

```bash
scp -r Web/* user@your-server:/var/www/database-notes/
```

### 方案四：本地 / 局域网访问

使用任意静态文件服务器：

```bash
# Python 3
cd Web
python -m http.server 8080

# Node.js (需安装 http-server)
npx http-server Web -p 8080

# PowerShell
cd Web
Start-Process "http://localhost:8080"
```

然后用手机连接同一 Wi-Fi，访问 `http://<电脑IP>:8080` 即可在手机上查看。

### 方案五：Docker

创建 `Dockerfile`：

```dockerfile
FROM nginx:alpine
COPY Web/ /usr/share/nginx/html/
EXPOSE 80
```

构建并运行：

```bash
docker build -t database-notes .
docker run -d -p 8080:80 database-notes
```

访问 `http://localhost:8080`。

---

## 📝 许可

MIT License
