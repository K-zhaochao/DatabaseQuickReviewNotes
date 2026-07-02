"""
将 Obsidian MD 笔记转换为单页静态网页
用法: python build.py
输出: Web/index.html
"""
import os
import re
import json
import hashlib


def make_heading_id(chapter_idx, text, counter):
    """为标题生成唯一的 HTML ID（同章节内唯一）"""
    h = hashlib.md5(text.encode()).hexdigest()[:6]
    return f"c{chapter_idx}-{counter}-{h}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

# 课时文件列表（按顺序）
CHAPTERS = [
    ("课时1绪论.md", "课时1：绪论"),
    ("课时2关系数据库.md", "课时2：关系数据库"),
    ("课时3SQL.md", "课时3：SQL"),
    ("课时4数据库安全性.md", "课时4：数据库安全性"),
    ("课时5数据库完整性.md", "课时5：数据库完整性"),
    ("课时6关系数据库理论.md", "课时6：关系数据库理论"),
    ("课时7数据库设计概述.md", "课时7：数据库设计概述"),
    ("课时8数据库恢复技术.md", "课时8：数据库恢复技术"),
    ("课时9并发控制.md", "课时9：并发控制"),
]


def parse_obsidian_md(text: str, chapter_idx: int = 0) -> str:
    """将 Obsidian 风格的 Markdown 转为 HTML"""
    lines = text.split('\n')
    html_lines = []
    in_paragraph = False
    heading_counter = 0  # 确保同章节内标题 ID 唯一

    def flush_paragraph():
        nonlocal in_paragraph
        if in_paragraph:
            html_lines.append('</p>')
            in_paragraph = False

    def open_paragraph():
        nonlocal in_paragraph
        if not in_paragraph:
            html_lines.append('<p>')
            in_paragraph = True

    i = 0
    while i < len(lines):
        line = lines[i]

        # 跳过空行
        if line.strip() == '':
            flush_paragraph()
            i += 1
            continue

        # 图片: ![[filename.png]] 或 ![[filename.png|width]]
        img_match = re.match(r'^!\[\[(.+?)\]\]$', line.strip())
        if img_match:
            flush_paragraph()
            img_ref = img_match.group(1).strip()
            # 去掉可能的宽度后缀 |611
            img_name = img_ref.split('|')[0].strip()
            # URL 编码空格
            img_src = f'Images/{img_name}'
            html_lines.append(f'<div class="img-container"><img src="{img_src}" alt="{img_name}" loading="lazy" /></div>')
            i += 1
            continue

        # 标题
        h4 = re.match(r'^#### (.+)$', line.strip())
        h3 = re.match(r'^### (.+)$', line.strip())
        h2 = re.match(r'^## (.+)$', line.strip())
        h1 = re.match(r'^# (.+)$', line.strip())

        if h4:
            flush_paragraph()
            heading_counter += 1
            raw_text = h4.group(1)
            hid = make_heading_id(chapter_idx, raw_text, heading_counter)
            html_lines.append(f'<h4 id="{hid}">{process_inline(raw_text)}</h4>')
            i += 1
            continue
        if h3:
            flush_paragraph()
            heading_counter += 1
            raw_text = h3.group(1)
            hid = make_heading_id(chapter_idx, raw_text, heading_counter)
            html_lines.append(f'<h3 id="{hid}">{process_inline(raw_text)}</h3>')
            i += 1
            continue
        if h2:
            flush_paragraph()
            heading_counter += 1
            raw_text = h2.group(1)
            hid = make_heading_id(chapter_idx, raw_text, heading_counter)
            html_lines.append(f'<h2 id="{hid}">{process_inline(raw_text)}</h2>')
            i += 1
            continue
        if h1:
            flush_paragraph()
            html_lines.append(f'<h1>{process_inline(h1.group(1))}</h1>')
            i += 1
            continue

        # 普通文本行
        open_paragraph()
        html_lines.append(process_inline(line.strip()))
        i += 1

    flush_paragraph()
    return '\n'.join(html_lines)


def process_inline(text: str) -> str:
    """处理行内格式"""
    # **粗体**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # *斜体*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # `代码`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def build_html():
    """构建完整的 index.html"""
    chapters_html = []
    nav_items = []

    for idx, (filename, title) in enumerate(CHAPTERS):
        filepath = os.path.join(ROOT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"警告: 文件不存在 {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        chapter_id = f'chapter{idx + 1}'
        body_html = parse_obsidian_md(content, chapter_idx=idx + 1)

        nav_items.append(f'<li><a href="#{chapter_id}" class="nav-link" data-chapter="{chapter_id}">{title}</a></li>')

        chapters_html.append(f'''
        <section id="{chapter_id}" class="chapter">
          <h2 class="chapter-title">{title}</h2>
          {body_html}
        </section>
        ''')

    # 完整的 HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>数据库知识速查</title>
  <style>
    /* ========== Reset & Base ========== */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-size: 16px; overflow-y: auto; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
      background: #f5f6fa; color: #2d3436; line-height: 1.7;
    }}

    /* ========== Sidebar Navigation ========== */
    .sidebar {{
      position: fixed; top: 0; left: 0; width: 260px; height: 100vh;
      background: #1e272e; color: #fff; overflow-y: auto; z-index: 100;
      transition: transform 0.3s ease; padding: 20px 0;
    }}
    .sidebar-header {{
      padding: 12px 20px 20px; border-bottom: 1px solid #485460;
      margin-bottom: 8px;
    }}
    .sidebar-header h1 {{
      font-size: 1.2rem; font-weight: 700; color: #ffd32a;
      letter-spacing: 0.5px;
    }}
    .sidebar-header .subtitle {{ font-size: 0.78rem; color: #808e9b; margin-top: 4px; }}
    .sidebar nav ul {{ list-style: none; }}
    .sidebar nav ul li a {{
      display: block; padding: 10px 24px; color: #d2dae2; text-decoration: none;
      font-size: 0.92rem; border-left: 3px solid transparent;
      transition: all 0.2s ease;
    }}
    .sidebar nav ul li a:hover {{ background: #2d3a42; color: #ffd32a; border-left-color: #ffd32a; }}
    .sidebar nav ul li a.active {{ background: #2d3a42; color: #ffd32a; border-left-color: #ffd32a; font-weight: 600; }}

    /* ========== Hamburger Menu Button ========== */
    .menu-btn {{
      display: none; position: fixed; top: 12px; left: 12px; z-index: 200;
      width: 40px; height: 40px; border: none; background: #1e272e;
      color: #ffd32a; font-size: 1.5rem; border-radius: 8px; cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }}
    .menu-btn:active {{ background: #2d3a42; }}

    /* Overlay for mobile */
    .overlay {{
      display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5);
      z-index: 99;
    }}
    .overlay.show {{ display: block; }}

    /* ========== Main Content Area ========== */
    .main {{
      margin-left: 260px; margin-right: 220px; flex: 1; padding: 24px 32px 60px;
      max-width: 800px; width: 100%;
    }}
    .chapter {{ display: none; }}
    .chapter.active {{ display: block; }}
    .chapter-title {{
      font-size: 1.6rem; color: #1e272e; margin-bottom: 20px;
      padding-bottom: 10px; border-bottom: 2px solid #ffd32a;
    }}

    /* ========== Content Typography ========== */
    h2 {{ font-size: 1.25rem; color: #2d3436; margin: 28px 0 12px; }}
    h3 {{ font-size: 1.1rem; color: #636e72; margin: 22px 0 10px; }}
    h4 {{ font-size: 1rem; color: #636e72; margin: 16px 0 8px; font-weight: 600; }}
    p  {{ margin: 6px 0; }}
    strong {{ color: #e17055; font-weight: 600; }}
    code {{
      background: #dfe6e9; color: #2d3436; padding: 2px 6px;
      border-radius: 3px; font-size: 0.9em; font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    }}

    /* ========== Images ========== */
    .img-container {{
      margin: 14px 0; text-align: center;
    }}
    .img-container img {{
      max-width: 100%; height: auto; border-radius: 6px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08);
      cursor: pointer; transition: transform 0.2s;
    }}
    .img-container img:hover {{ transform: scale(1.01); }}

    /* ========== Lightbox ========== */
    .lightbox {{
      display: none; position: fixed; inset: 0; z-index: 1000;
      background: rgba(0,0,0,0.88); justify-content: center;
      align-items: center; flex-direction: column;
    }}
    .lightbox.show {{ display: flex; }}
    .lightbox img {{ max-width: 94vw; max-height: 90vh; border-radius: 4px; }}
    .lightbox-close {{
      position: absolute; top: 16px; right: 24px; font-size: 2rem;
      color: #fff; background: none; border: none; cursor: pointer;
    }}
    .lightbox-caption {{
      color: #ccc; margin-top: 10px; font-size: 0.85rem;
    }}

    /* ========== Scroll to top ========== */
    .scroll-top {{
      position: fixed; bottom: 24px; right: 28px; width: 40px; height: 40px;
      background: #1e272e; color: #ffd32a; border: none; border-radius: 50%;
      font-size: 1.2rem; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      display: none; z-index: 50;
    }}
    .scroll-top.show {{ display: flex; align-items: center; justify-content: center; }}

    /* ========== TOC Sidebar (Right) ========== */
    .toc-sidebar {{
      position: fixed; top: 0; right: 0; width: 210px; height: 100vh;
      overflow-y: auto; z-index: 90; padding: 20px 14px 20px 6px;
      background: transparent; font-size: 0.82rem; line-height: 1.5;
    }}
    .toc-sidebar h3 {{
      font-size: 0.85rem; color: #636e72; margin-bottom: 10px;
      padding-left: 8px; font-weight: 600; letter-spacing: 0.5px;
    }}
    .toc-sidebar ul {{
      list-style: none; border-left: 2px solid #dfe6e9;
    }}
    .toc-sidebar ul li a {{
      display: block; padding: 4px 12px; color: #636e72;
      text-decoration: none; border-left: 2px solid transparent;
      margin-left: -2px; transition: all 0.15s ease;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .toc-sidebar ul li a:hover {{ color: #1e272e; border-left-color: #ffd32a; }}
    .toc-sidebar ul li a.toc-active {{
      color: #1e272e; font-weight: 600; border-left-color: #ffd32a;
      background: rgba(255,211,42,0.08);
    }}
    .toc-sidebar ul li a.toc-h2 {{ padding-left: 12px; }}
    .toc-sidebar ul li a.toc-h3 {{ padding-left: 24px; font-size: 0.78rem; }}
    .toc-sidebar ul li a.toc-h4 {{ padding-left: 36px; font-size: 0.75rem; color: #999; }}

    /* ========== TOC Toggle Button (Tablet & Mobile) ========== */
    .toc-btn {{
      display: none; position: fixed; top: 12px; right: 12px; z-index: 200;
      width: 40px; height: 40px; border: none; background: #1e272e;
      color: #ffd32a; font-size: 1.15rem; border-radius: 8px; cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.25);
      align-items: center; justify-content: center;
    }}
    .toc-btn:active {{ background: #2d3a42; }}

    /* ========== Responsive: Tablet & Mobile ========== */
    @media (max-width: 1024px) {{
      .toc-btn {{ display: flex; }}
      .toc-sidebar {{
        position: fixed; top: 0; right: 0; width: 260px; height: 100vh;
        background: #fff; z-index: 150;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        padding: 20px 16px; box-shadow: -2px 0 12px rgba(0,0,0,0.12);
      }}
      .toc-sidebar.open {{ transform: translateX(0); }}
      .main {{ margin-right: 0; }}
    }}
    @media (max-width: 768px) {{
      .sidebar {{
        transform: translateX(-100%);
      }}
      .sidebar.open {{
        transform: translateX(0);
      }}
      .menu-btn {{ display: flex; align-items: center; justify-content: center; }}
      .main {{ margin-left: 0; padding: 60px 16px 40px; }}
      .chapter-title {{ font-size: 1.3rem; }}
      .toc-btn {{ top: 12px; right: 12px; }}
      .scroll-top {{ bottom: 16px; right: 14px; }}
    }}

    /* ========== Print ========== */
    @media print {{
      .sidebar, .menu-btn, .overlay, .scroll-top, .lightbox, .toc-sidebar {{ display: none !important; }}
      .main {{ margin-left: 0; }}
      .chapter {{ display: block !important; page-break-after: always; }}
      .img-container img {{ max-width: 100%; box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <!-- Mobile menu button -->
  <button class="menu-btn" id="menuBtn" aria-label="菜单">&#9776;</button>
  <!-- Mobile TOC button -->
  <button class="toc-btn" id="tocBtn" aria-label="目录">&#8801;</button>
  <!-- Mobile overlay -->
  <div class="overlay" id="overlay"></div>

  <!-- Sidebar -->
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <h1>📘 数据库知识速查</h1>
      <div class="subtitle">Database Quick Review Notes</div>
    </div>
    <nav>
      <ul>
        {''.join(nav_items)}
      </ul>
    </nav>
  </aside>

  <!-- Main Content -->
  <main class="main" id="mainContent">
    {''.join(chapters_html)}
  </main>

  <!-- TOC Sidebar (Right) -->
  <aside class="toc-sidebar" id="tocSidebar">
    <h3>📑 本节目录</h3>
    <nav><ul id="tocList"></ul></nav>
  </aside>

  <!-- Lightbox -->
  <div class="lightbox" id="lightbox">
    <button class="lightbox-close" id="lightboxClose">&times;</button>
    <img id="lightboxImg" src="" alt="" />
    <div class="lightbox-caption" id="lightboxCaption"></div>
  </div>

  <!-- Scroll to top -->
  <button class="scroll-top" id="scrollTop" title="回到顶部">&#8679;</button>

  <script>
    (function() {{
      // ========== Elements ==========
      const sidebar = document.getElementById('sidebar');
      const menuBtn = document.getElementById('menuBtn');
      const tocBtn = document.getElementById('tocBtn');
      const overlay = document.getElementById('overlay');
      const navLinks = document.querySelectorAll('.nav-link');
      const chapters = document.querySelectorAll('.chapter');
      const scrollTopBtn = document.getElementById('scrollTop');
      const lightbox = document.getElementById('lightbox');
      const lightboxImg = document.getElementById('lightboxImg');
      const lightboxCaption = document.getElementById('lightboxCaption');
      const lightboxClose = document.getElementById('lightboxClose');
      const mainContent = document.getElementById('mainContent');
      const tocList = document.getElementById('tocList');
      const tocSidebar = document.getElementById('tocSidebar');

      let currentChapterId = null;
      let headingElements = [];
      let tocLinks = [];

      // ========== Build TOC from active chapter's headings ==========
      function buildTOC(chapterEl) {{
        tocList.innerHTML = '';
        headingElements = [];
        tocLinks = [];
        if (!chapterEl) return;

        const headings = chapterEl.querySelectorAll('h2[id], h3[id], h4[id]');
        headings.forEach(h => {{
          const tag = h.tagName.toLowerCase();
          const level = 'toc-' + tag;
          const text = h.textContent.trim();
          if (!text) return;

          const li = document.createElement('li');
          const a = document.createElement('a');
          a.href = '#' + h.id;
          a.textContent = text;
          a.className = 'toc-item ' + level;
          a.setAttribute('data-target', h.id);
          a.addEventListener('click', function(e) {{
            e.preventDefault();
            const target = document.getElementById(this.getAttribute('data-target'));
            if (target) {{
              target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
              history.pushState(null, null, '#' + currentChapterId);
            }}
            // close TOC sidebar on mobile after click
            if (window.innerWidth <= 1024) closeTocSidebar();
          }});
          li.appendChild(a);
          tocList.appendChild(li);

          headingElements.push(h);
          tocLinks.push(a);
        }});
      }}

      // ========== Scroll spy: highlight active TOC item ==========
      function getScrollTop() {{
        return window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
      }}
      function updateActiveTocLink() {{
        if (headingElements.length === 0) return;
        let activeIdx = 0;
        const scrollTop = getScrollTop() + 100;

        for (let i = headingElements.length - 1; i >= 0; i--) {{
          if (headingElements[i].offsetTop <= scrollTop) {{
            activeIdx = i;
            break;
          }}
        }}

        tocLinks.forEach((link, i) => {{
          link.classList.toggle('toc-active', i === activeIdx);
        }});
      }}

      // ========== Helper: activate chapter ==========
      function activateChapter(chapterId) {{
        chapters.forEach(c => c.classList.remove('active'));
        navLinks.forEach(l => l.classList.remove('active'));
        const target = document.getElementById(chapterId);
        if (target) {{
          target.classList.add('active');
          currentChapterId = chapterId;
          buildTOC(target);
        }}
        const link = document.querySelector(`[data-chapter="${{chapterId}}"]`);
        if (link) link.classList.add('active');
        // close sidebar on mobile
        if (window.innerWidth <= 768) closeSidebar();
        // scroll to top (need to wait for DOM update)
        requestAnimationFrame(() => {{
          document.scrollingElement.scrollTo({{ top: 0, behavior: 'instant' }});
          updateActiveTocLink();
        }});
      }}

      // ========== Sidebar toggle (mobile) ==========
      function openSidebar() {{
        sidebar.classList.add('open');
        overlay.classList.add('show');
        tocSidebar.classList.remove('open');  // close TOC if open
      }}
      function closeSidebar() {{
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
      }}
      menuBtn.addEventListener('click', () => {{
        sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
      }});

      // ========== TOC toggle (mobile) ==========
      function openTocSidebar() {{
        tocSidebar.classList.add('open');
        overlay.classList.add('show');
        sidebar.classList.remove('open');  // close nav if open
      }}
      function closeTocSidebar() {{
        tocSidebar.classList.remove('open');
        overlay.classList.remove('show');
      }}
      tocBtn.addEventListener('click', () => {{
        tocSidebar.classList.contains('open') ? closeTocSidebar() : openTocSidebar();
      }});
      overlay.addEventListener('click', () => {{
        closeSidebar();
        closeTocSidebar();
      }});

      // ========== Nav click ==========
      navLinks.forEach(link => {{
        link.addEventListener('click', function(e) {{
          e.preventDefault();
          const chapterId = this.getAttribute('data-chapter');
          activateChapter(chapterId);
          history.pushState(null, null, '#' + chapterId);
        }});
      }});

      // ========== Image click → lightbox ==========
      mainContent.addEventListener('click', function(e) {{
        if (e.target.tagName === 'IMG') {{
          lightboxImg.src = e.target.src;
          lightboxCaption.textContent = e.target.alt || '';
          lightbox.classList.add('show');
          document.body.style.overflow = 'hidden';
        }}
      }});
      lightboxClose.addEventListener('click', () => {{
        lightbox.classList.remove('show');
        document.body.style.overflow = '';
      }});
      lightbox.addEventListener('click', function(e) {{
        if (e.target === lightbox) {{
          lightbox.classList.remove('show');
          document.body.style.overflow = '';
        }}
      }});
      document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape' && lightbox.classList.contains('show')) {{
          lightbox.classList.remove('show');
          document.body.style.overflow = '';
        }}
      }});

      // ========== Scroll to top ==========
      window.addEventListener('scroll', function() {{
        scrollTopBtn.classList.toggle('show', getScrollTop() > 400);
        updateActiveTocLink();
      }}, {{ passive: true }});
      scrollTopBtn.addEventListener('click', () => {{
        document.scrollingElement.scrollTo({{ top: 0, behavior: 'smooth' }});
      }});

      // ========== Init: load chapter from URL hash ==========
      function init() {{
        const hash = window.location.hash.replace('#', '');
        const validIds = Array.from(chapters).map(c => c.id);
        if (hash && validIds.includes(hash)) {{
          activateChapter(hash);
        }} else {{
          activateChapter('chapter1');
        }}
      }}

      // Handle hash change (browser back/forward)
      window.addEventListener('hashchange', function() {{
        const hash = window.location.hash.replace('#', '');
        const validIds = Array.from(chapters).map(c => c.id);
        if (hash && validIds.includes(hash)) {{
          activateChapter(hash);
        }}
      }});

      init();
    }})();
  </script>
</body>
</html>'''

    return html


def main():
    html = build_html()
    output_path = os.path.join(BASE_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 成功生成: {output_path}")
    print(f"   共 {len(CHAPTERS)} 个章节")


if __name__ == '__main__':
    main()
