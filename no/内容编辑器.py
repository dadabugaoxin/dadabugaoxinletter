import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import webbrowser
import re
import html

# 默认 HTML 模板（基于之前生成的信封动画，信纸内容部分使用占位符）
# 在实际使用中，你也可以让用户选择一个现有的 HTML 文件进行编辑。
DEFAULT_HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>爱心信封 | 可编辑信纸</title>
    <style>
        /* 完整样式代码 (与最终交付版本一致) */
        * { margin: 0; padding: 0; box-sizing: border-box; user-select: none; }
        body {
            min-height: 100vh;
            background: linear-gradient(145deg, #f9e3d0 0%, #ffccb3 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', 'Quicksand', 'Poppins', system-ui, sans-serif;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        .envelope-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            perspective: 1200px;
            z-index: 10;
        }
        .envelope-container {
            position: relative;
            width: 360px;
            height: 240px;
            perspective: 1000px;
            transform-style: preserve-3d;
            cursor: default;
            transition: opacity 0.3s ease;
        }
        .envelope {
            position: relative;
            width: 100%;
            height: 100%;
            background: #fdf8ed;
            background-image: radial-gradient(circle at 25% 40%, rgba(255,215,170,0.3) 2%, transparent 2.5%);
            background-size: 18px 18px;
            border-radius: 12px 12px 10px 10px;
            box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255,255,240,0.8);
            transform-style: preserve-3d;
        }
        .envelope::before {
            content: "";
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            height: 2px;
            background: repeating-linear-gradient(90deg, #e3c9a0, #e3c9a0 8px, transparent 8px, transparent 16px);
            border-radius: 2px;
        }
        .flap {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 48%;
            background: linear-gradient(135deg, #fef5e8 0%, #f8e3ce 100%);
            border-radius: 12px 12px 30px 30px;
            transform-origin: top center;
            transition: transform 0.65s cubic-bezier(0.23, 1, 0.32, 1);
            transform-style: preserve-3d;
            z-index: 20;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            border-bottom: 2px solid #ecd9bf;
        }
        .flap::after {
            content: "";
            position: absolute;
            bottom: -12px;
            left: 50%;
            transform: translateX(-50%);
            width: 70%;
            height: 18px;
            background: #e9d2b5;
            clip-path: polygon(0% 0%, 100% 0%, 50% 100%);
            opacity: 0.5;
        }
        .heart-btn {
            position: absolute;
            top: 55%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 44px;
            cursor: pointer;
            z-index: 30;
            transition: all 0.2s ease;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
            animation: gentleBeat 1.6s infinite ease-in-out;
            background: transparent;
            border: none;
            line-height: 1;
            pointer-events: auto;
        }
        .heart-btn.hidden-heart {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
            animation: none;
            transform: translate(-50%, -50%) scale(0.8);
            transition: opacity 0.2s, visibility 0.2s;
        }
        @keyframes gentleBeat {
            0% { transform: translate(-50%, -50%) scale(1); text-shadow: 0 0 0 rgba(255,80,120,0);}
            50% { transform: translate(-50%, -50%) scale(1.12); text-shadow: 0 0 8px rgba(255,60,100,0.6);}
            100% { transform: translate(-50%, -50%) scale(1); text-shadow: 0 0 0 rgba(255,80,120,0);}
        }
        .envelope-container.open .flap { transform: rotateX(180deg); box-shadow: 0 -2px 5px rgba(0,0,0,0.1); }
        .envelope-container.open .envelope { box-shadow: 0 25px 35px -14px rgba(0, 0, 0, 0.3); }
        .fullscreen-letter {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(8px);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            visibility: hidden;
            opacity: 0;
            transition: visibility 0.3s, opacity 0.4s cubic-bezier(0.2, 0.9, 0.4, 1.1);
            font-family: 'Georgia', '楷体', '华文楷书', cursive;
            cursor: pointer;
        }
        .fullscreen-letter.active { visibility: visible; opacity: 1; }
        .letter-card {
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            background: linear-gradient(145deg, #ffffff 0%, #fffaf0 100%);
            border-radius: 32px;
            padding: 2rem 2.2rem;
            box-shadow: 0 30px 45px -20px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 215, 170, 0.6);
            transform: scale(0.95);
            transition: transform 0.5s cubic-bezier(0.2, 0.9, 0.4, 1.2);
            position: relative;
            overflow-y: auto;
            cursor: default;
            animation: letterFloat 0.6s ease-out;
        }
        .fullscreen-letter.active .letter-card { transform: scale(1); }
        @keyframes letterFloat {
            0% { opacity: 0; transform: scale(0.9) translateY(30px); }
            100% { opacity: 1; transform: scale(1) translateY(0); }
        }
        .letter-content {
            color: #5a3e2b;
            font-size: 1.2rem;
            line-height: 1.7;
            text-align: left;
        }
        .letter-content h3 {
            text-align: center;
            margin-bottom: 1.2rem;
            color: #c53a1f;
            font-size: 2rem;
            letter-spacing: 3px;
            border-bottom: 2px solid #f3cf9a;
            display: inline-block;
            width: 100%;
        }
        .letter-content p { margin: 1rem 0; text-indent: 2em; }
        .signature {
            text-align: right;
            margin-top: 1.8rem;
            font-style: italic;
            font-size: 1rem;
            color: #b97f4b;
            border-top: 1px dotted #f0cf9e;
            padding-top: 1rem;
        }
        @media (max-width: 560px) {
            .envelope-container { width: 300px; height: 200px; }
            .heart-btn { font-size: 38px; }
            .letter-card { padding: 1.5rem; width: 85%; }
            .letter-content { font-size: 1rem; }
            .letter-content h3 { font-size: 1.6rem; }
        }
        .letter-card::-webkit-scrollbar { width: 6px; }
        .letter-card::-webkit-scrollbar-track { background: #f0dbc0; border-radius: 10px; }
        .letter-card::-webkit-scrollbar-thumb { background: #c98f5a; border-radius: 10px; }
        .helper-tip {
            font-size: 13px;
            color: #b1642c;
            background: rgba(255,235,210,0.7);
            backdrop-filter: blur(4px);
            border-radius: 30px;
            padding: 4px 12px;
            margin-top: 24px;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="envelope-wrapper">
    <div class="envelope-container" id="envelopeContainer">
        <div class="envelope">
            <div class="flap"></div>
            <button class="heart-btn" id="heartButton" aria-label="打开信封">❤️</button>
        </div>
    </div>
    <div class="helper-tip">💖 点击爱心打开信纸 · 轻触背景即可收起 ✨</div>
</div>
<div class="fullscreen-letter" id="fullscreenLetter">
    <div class="letter-card">
        <div class="letter-content" id="dynamicLetterContent">
            {{LETTER_CONTENT}}
        </div>
    </div>
</div>
<script>
    (function() {
        const envelopeContainer = document.getElementById('envelopeContainer');
        const heartBtn = document.getElementById('heartButton');
        const fullscreenLayer = document.getElementById('fullscreenLetter');
        let isOpen = false, isAnimating = false;
        function hideHeart() { heartBtn.classList.add('hidden-heart'); }
        function showHeart() { heartBtn.classList.remove('hidden-heart'); }
        function openEnvelopeAndFullscreen() {
            if (isOpen || isAnimating) return;
            isAnimating = true;
            envelopeContainer.classList.add('open');
            hideHeart();
            setTimeout(() => {
                fullscreenLayer.classList.add('active');
                document.body.style.overflow = 'hidden';
                isOpen = true;
                isAnimating = false;
            }, 200);
        }
        function closeFullscreenAndResetEnvelope() {
            if (isAnimating) return;
            if (!isOpen && !fullscreenLayer.classList.contains('active')) return;
            isAnimating = true;
            fullscreenLayer.classList.remove('active');
            document.body.style.overflow = '';
            setTimeout(() => {
                envelopeContainer.classList.remove('open');
                showHeart();
                isOpen = false;
                setTimeout(() => { isAnimating = false; }, 300);
            }, 280);
        }
        heartBtn.addEventListener('click', (e) => { e.stopPropagation(); if (!isOpen && !isAnimating && !fullscreenLayer.classList.contains('active')) openEnvelopeAndFullscreen(); });
        fullscreenLayer.addEventListener('click', (e) => { if (e.target === fullscreenLayer) closeFullscreenAndResetEnvelope(); });
        heartBtn.addEventListener('touchstart', (e) => { if (!isOpen && !isAnimating) { e.preventDefault(); openEnvelopeAndFullscreen(); } }, { passive: false });
        window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && fullscreenLayer.classList.contains('active')) closeFullscreenAndResetEnvelope(); });
        const letterCard = document.querySelector('.letter-card');
        if(letterCard) { letterCard.addEventListener('wheel', (e) => e.stopPropagation()); letterCard.addEventListener('touchstart', (e) => e.stopPropagation()); }
    })();
</script>
</body>
</html>'''

class LetterEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("✉️ 信封信纸内容编辑器")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # 设置样式
        self.root.configure(bg='#fff3e6')
        
        # 标题
        title_font = font.Font(family="微软雅黑", size=14, weight="bold")
        tk.Label(root, text="✍️ 编辑信纸内容", font=title_font, bg='#fff3e6', fg='#b45f2b').pack(pady=(15,5))
        
        # 主框架
        main_frame = tk.Frame(root, bg='#fff3e6')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 标题输入
        tk.Label(main_frame, text="📌 信纸标题：", font=("微软雅黑", 11), bg='#fff3e6', anchor='w').pack(fill=tk.X, pady=(5,0))
        self.title_entry = tk.Entry(main_frame, font=("楷体", 12), relief=tk.GROOVE, bd=2)
        self.title_entry.pack(fill=tk.X, pady=5)
        self.title_entry.insert(0, "✨ 见信如晤 ✨")
        
        # 正文（多行）
        tk.Label(main_frame, text="📝 正文内容（支持多段，使用空行分隔）：", font=("微软雅黑", 11), bg='#fff3e6', anchor='w').pack(fill=tk.X, pady=(10,0))
        self.text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("楷体", 11), height=12, relief=tk.GROOVE, bd=2)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=5)
        default_text = """亲爱的朋友：

当你打开这封铺满温暖的信笺时，世界都变得柔软起来。愿此刻的浪漫，如星子落入眼眸，点亮平凡日常。

感谢你触碰这颗爱心，让藏在信封里的絮语，化作清风，萦绕在你的身旁。每一个字句都是为你而生的心意，每一次呼吸都带着墨香。

或许我们相隔屏幕，但此刻心意相通。请收下这份独属于你的诗意时光，愿美好永驻心间。"""
        self.text_area.insert(tk.END, default_text)
        
        # 署名
        tk.Label(main_frame, text="✒️ 署名 / 落款：", font=("微软雅黑", 11), bg='#fff3e6', anchor='w').pack(fill=tk.X, pady=(5,0))
        self.signature_entry = tk.Entry(main_frame, font=("楷体", 11), relief=tk.GROOVE, bd=2)
        self.signature_entry.pack(fill=tk.X, pady=5)
        self.signature_entry.insert(0, "🌟 一封全屏信笺 · 轻触背景即归\n—— 来自数字宇宙的暖意")
        
        # 按钮区域
        btn_frame = tk.Frame(root, bg='#fff3e6')
        btn_frame.pack(pady=15)
        
        self.save_btn = tk.Button(btn_frame, text="💾 保存并生成 HTML 文件", command=self.save_html,
                                  font=("微软雅黑", 11), bg='#ffcc99', fg='#4f2f1a', padx=15, pady=5, relief=tk.RAISED, bd=2)
        self.save_btn.pack(side=tk.LEFT, padx=10)
        
        self.preview_btn = tk.Button(btn_frame, text="🌐 在浏览器中预览", command=self.preview_html,
                                     font=("微软雅黑", 11), bg='#cfe6cd', fg='#2c5e2a', padx=15, pady=5, relief=tk.RAISED, bd=2)
        self.preview_btn.pack(side=tk.LEFT, padx=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 | 点击保存生成新的信封页面")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg='#f0e0d0', fg='#884d2e')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 当前生成的文件路径
        self.last_saved_path = None
    
    def build_letter_content_html(self):
        """根据用户输入构建 letter-content 内部的 HTML"""
        title = html.escape(self.title_entry.get().strip())
        if not title:
            title = "✨ 见信如晤 ✨"
        # 处理正文：将用户输入的纯文本转换为 HTML 段落 (按空行分割)
        raw_text = self.text_area.get("1.0", tk.END).strip()
        if not raw_text:
            raw_text = "愿这封信带给你温暖。"
        # 分割段落（连续两个换行）
        paragraphs = re.split(r'\n\s*\n', raw_text)
        para_html = ""
        for para in paragraphs:
            para = para.strip()
            if para:
                # 将内部的换行替换为 <br> 保留原有换行结构，但一般段落内手动换行较少
                para_br = html.escape(para).replace('\n', '<br>')
                para_html += f"<p>{para_br}</p>\n"
        
        signature = html.escape(self.signature_entry.get().strip())
        if not signature:
            signature = "🌟 一封来自远方的信笺"
        else:
            signature = signature.replace('\n', '<br>')
        
        full_html = f"""
            <h3>{title}</h3>
            {para_html}
            <div class="signature">
                {signature}
            </div>
        """
        return full_html
    
    def generate_html_file(self, output_path="letter_output.html"):
        """生成完整的 HTML 文件，替换信纸内容"""
        # 读取模板 (这里直接使用内置模板字符串，也可以从文件读取)
        template = DEFAULT_HTML_TEMPLATE
        # 生成信纸内容
        content_html = self.build_letter_content_html()
        # 替换占位符 {{LETTER_CONTENT}}
        final_html = template.replace("{{LETTER_CONTENT}}", content_html)
        # 写入文件
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_html)
            return output_path
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存文件：{e}")
            return None
    
    def save_html(self):
        """保存 HTML 文件，让用户选择路径"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialfile="my_love_letter.html",
            title="保存信封页面"
        )
        if file_path:
            saved = self.generate_html_file(file_path)
            if saved:
                self.last_saved_path = saved
                self.status_var.set(f"已保存至：{saved}")
                messagebox.showinfo("成功", f"信封页面已生成！\n{saved}\n\n点击「预览」按钮可查看效果。")
            else:
                self.status_var.set("保存失败，请重试")
    
    def preview_html(self):
        """在默认浏览器中预览最近保存的 HTML 文件，若没有则先保存到临时文件"""
        if self.last_saved_path and self.last_saved_path.endswith('.html'):
            webbrowser.open(f"file:///{self.last_saved_path.replace(os.sep, '/')}")
            self.status_var.set(f"正在预览：{self.last_saved_path}")
        else:
            # 保存到临时文件再预览
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_path = tempfile.mktemp(suffix=".html", dir=temp_dir, prefix="envelope_")
            saved = self.generate_html_file(temp_path)
            if saved:
                self.last_saved_path = saved
                webbrowser.open(f"file:///{saved.replace(os.sep, '/')}")
                self.status_var.set(f"临时预览文件：{saved}")
            else:
                messagebox.showerror("预览失败", "无法生成临时文件，请先点击「保存」")

if __name__ == "__main__":
    import os
    root = tk.Tk()
    app = LetterEditor(root)
    root.mainloop()