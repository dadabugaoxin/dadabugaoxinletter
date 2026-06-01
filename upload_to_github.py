#!/usr/bin/env python3
"""
GitHub 文件上传工具 - GUI 版本
使用 tkinter 构建界面，支持上传文件或整个文件夹到 GitHub 仓库
"""

import os
import base64
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Optional

import requests

# 默认配置
DEFAULT_CONFIG = {
    "repo": "dadabugaoxin/dadabugaoxinletter",
    "branch": "main",
    "commit_message": "Update via GUI tool"
}

# ==================== GitHub 上传核心逻辑 ====================
class GitHubUploader:
    """GitHub 文件上传器（与命令行版本相同）"""
    
    API_URL = "https://api.github.com"
    
    def __init__(self, token: str, repo: str, branch: str = "main"):
        self.token = token
        self.owner, self.repo_name = repo.split('/')
        self.branch = branch
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })
    
    def _get_file_sha(self, remote_path: str) -> Optional[str]:
        url = f"{self.API_URL}/repos/{self.owner}/{self.repo_name}/contents/{remote_path}"
        params = {"ref": self.branch}
        resp = self.session.get(url, params=params)
        if resp.status_code == 200:
            return resp.json().get("sha")
        elif resp.status_code == 404:
            return None
        else:
            resp.raise_for_status()
            return None
    
    def upload_file(self, local_path: Path, remote_path: str, commit_message: str, callback=None):
        """
        上传单个文件
        :param callback: 可选回调函数，接收 (success, message) 参数
        """
        try:
            if not local_path.is_file():
                raise FileNotFoundError(f"本地文件不存在: {local_path}")
            
            with open(local_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")
            
            sha = self._get_file_sha(remote_path)
            url = f"{self.API_URL}/repos/{self.owner}/{self.repo_name}/contents/{remote_path}"
            payload = {
                "message": commit_message,
                "content": content,
                "branch": self.branch,
            }
            if sha:
                payload["sha"] = sha
            
            resp = self.session.put(url, json=payload)
            if resp.status_code in (200, 201):
                msg = f"✅ 上传成功: {local_path.name} -> {remote_path}"
                if callback:
                    callback(True, msg)
                return True
            else:
                msg = f"❌ 上传失败: {local_path.name} -> {remote_path}\n   错误: {resp.status_code} - {resp.text}"
                if callback:
                    callback(False, msg)
                return False
        except Exception as e:
            msg = f"❌ 异常: {local_path.name} -> {remote_path}\n   {str(e)}"
            if callback:
                callback(False, msg)
            return False
    
    def upload_directory(self, local_dir: Path, remote_base: str, commit_message: str,
                         ignore_hidden: bool = True, callback=None):
        """递归上传目录，每次上传一个文件时调用 callback"""
        local_dir = Path(local_dir).resolve()
        if not local_dir.is_dir():
            raise NotADirectoryError(f"本地目录不存在: {local_dir}")
        
        results = []
        total = 0
        for root, dirs, files in os.walk(local_dir):
            if ignore_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if ignore_hidden and file.startswith('.'):
                    continue
                total += 1
        
        processed = 0
        for root, dirs, files in os.walk(local_dir):
            if ignore_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if ignore_hidden and file.startswith('.'):
                    continue
                local_file = Path(root) / file
                rel_path = local_file.relative_to(local_dir)
                remote_path = f"{remote_base}/{rel_path}".replace("\\", "/")
                
                ok = self.upload_file(local_file, remote_path, commit_message, callback=None)
                results.append(ok)
                processed += 1
                if callback:
                    callback(ok, f"进度: {processed}/{total} - {rel_path}", is_progress=True)
        
        return results


# ==================== GUI 界面 ====================
class GitHubUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub 文件上传工具")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        
        # 停止标志
        self.stop_upload = False
        
        # 创建界面组件
        self.create_widgets()
    
    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 说明标签
        info_label = tk.Label(main_frame, text="📦 上传本地文件或文件夹到 GitHub 仓库",
                              font=("微软雅黑", 12, "bold"), bg='#f0f0f0', fg='#2c3e50')
        info_label.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0,10))
        
        # Token
        tk.Label(main_frame, text="GitHub Token:", font=("微软雅黑", 10), bg='#f0f0f0', anchor='w')\
            .grid(row=1, column=0, sticky='w', pady=5)
        self.token_entry = tk.Entry(main_frame, width=50, show='*', font=("Consolas", 10))
        self.token_entry.grid(row=1, column=1, columnspan=2, sticky='ew', pady=5, padx=(5,0))
        self.show_token_var = tk.BooleanVar()
        tk.Checkbutton(main_frame, text="显示", variable=self.show_token_var, command=self.toggle_token_show,
                       bg='#f0f0f0').grid(row=1, column=3, padx=(5,0))
        
        # 仓库
        tk.Label(main_frame, text="仓库 (owner/repo):", font=("微软雅黑", 10), bg='#f0f0f0', anchor='w')\
            .grid(row=2, column=0, sticky='w', pady=5)
        self.repo_entry = tk.Entry(main_frame, width=40, font=("Consolas", 10))
        self.repo_entry.grid(row=2, column=1, columnspan=3, sticky='ew', pady=5, padx=(5,0))
        self.repo_entry.insert(0, DEFAULT_CONFIG["repo"])
        
        # 分支输入
        tk.Label(main_frame, text="分支 (branch):", font=("微软雅黑", 10), bg='#f0f0f0', anchor='w')\
            .grid(row=3, column=0, sticky='w', padx=10)
        self.branch_entry = tk.Entry(main_frame, width=20, font=("Consolas", 10))
        self.branch_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(5,0))
        self.branch_entry.insert(0, DEFAULT_CONFIG["branch"])
        
        # 本地路径选择
        tk.Label(main_frame, text="本地路径:", font=("微软雅黑", 10), bg='#f0f0f0', anchor='w')\
            .grid(row=4, column=0, sticky='w', pady=5)
        self.local_path_var = tk.StringVar()
        self.local_entry = tk.Entry(main_frame, textvariable=self.local_path_var, width=40, font=("Consolas", 10))
        self.local_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=(5,0))
        self.browse_file_btn = tk.Button(main_frame, text="选择文件", command=self.browse_file, width=10)
        self.browse_file_btn.grid(row=4, column=2, padx=(5,5))
        self.browse_dir_btn = tk.Button(main_frame, text="选择文件夹", command=self.browse_directory, width=12)
        self.browse_dir_btn.grid(row=4, column=3, padx=(5,0))
        
        # 远程目标路径
        tk.Label(main_frame, text="远程路径 (可留空):", font=("微软雅黑", 10), bg='#f0f0f0', anchor='w')\
            .grid(row=5, column=0, sticky='w', pady=5)
        self.remote_entry = tk.Entry(main_frame, width=50, font=("Consolas", 10))
        self.remote_entry.grid(row=5, column=1, columnspan=2, sticky='ew', pady=5, padx=(5,0))
        self.remote_entry.insert(0, "")
        
        # Commit 信息
        tk.Label(main_frame, text="Commit 信息:", font=("微软雅黑", 10), bg='#f0f0f0', anchor='w')\
            .grid(row=6, column=0, sticky='w', pady=5)
        self.commit_entry = tk.Entry(main_frame, width=50, font=("Consolas", 10))
        self.commit_entry.grid(row=6, column=1, columnspan=2, sticky='ew', pady=5, padx=(5,0))
        self.commit_entry.insert(0, DEFAULT_CONFIG["commit_message"])
        
        # 忽略隐藏文件选项
        self.ignore_hidden_var = tk.BooleanVar(value=True)
        tk.Checkbutton(main_frame, text="忽略隐藏文件/文件夹 (.开头)", variable=self.ignore_hidden_var,
                       bg='#f0f0f0').grid(row=7, column=0, columnspan=2, sticky='w', pady=5)
        
        # 按钮区域
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.grid(row=8, column=0, columnspan=4, pady=10)
        self.upload_btn = tk.Button(btn_frame, text="🚀 开始上传", command=self.start_upload,
                                    bg='#4CAF50', fg='white', font=("微软雅黑", 11), padx=20, pady=5)
        self.upload_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = tk.Button(btn_frame, text="⏹️ 停止", command=self.stop_upload_cmd,
                                  bg='#f44336', fg='white', font=("微软雅黑", 11), padx=20, pady=5, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # 日志区域
        tk.Label(main_frame, text="📋 上传日志:", font=("微软雅黑", 10), bg='#f0f0f0', anchor='w')\
            .grid(row=9, column=0, sticky='w', pady=(10,0))
        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=18,
                                                   font=("Consolas", 9), bg='#ffffff', fg='#333')
        self.log_area.grid(row=10, column=0, columnspan=4, sticky='nsew', pady=5)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(10, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def toggle_token_show(self):
        if self.show_token_var.get():
            self.token_entry.config(show='')
        else:
            self.token_entry.config(show='*')
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(title="选择要上传的文件")
        if file_path:
            self.local_path_var.set(file_path)
    
    def browse_directory(self):
        dir_path = filedialog.askdirectory(title="选择要上传的文件夹")
        if dir_path:
            self.local_path_var.set(dir_path)
    
    def log(self, message, is_error=False):
        """在日志区域添加一行"""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()
    
    def start_upload(self):
        """启动上传线程"""
        # 验证输入
        token = self.token_entry.get().strip()
        repo = self.repo_entry.get().strip()
        local_path = self.local_path_var.get().strip()
        remote_path = self.remote_entry.get().strip()
        branch = self.branch_entry.get().strip()
        commit_msg = self.commit_entry.get().strip()
        
        if not repo or '/' not in repo:
            messagebox.showerror("错误", "仓库格式错误，应为 owner/repo")
            return
        if not local_path:
            messagebox.showerror("错误", "请选择本地文件或文件夹")
            return
        if not commit_msg:
            commit_msg = "Upload via GUI tool"
        
        path_obj = Path(local_path)
        if not path_obj.exists():
            messagebox.showerror("错误", "本地路径不存在")
            return
        
        # 清空日志
        self.log_area.delete(1.0, tk.END)
        self.log("===== 开始上传任务 =====")
        self.log(f"仓库: {repo}")
        self.log(f"分支: {branch}")
        self.log(f"本地: {local_path}")
        self.log(f"远程: {remote_path if remote_path else '(根目录)'}")
        self.log("")
        
        # 禁用开始按钮，启用停止按钮
        self.upload_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.stop_upload = False
        
        # 启动后台线程
        thread = threading.Thread(target=self.upload_worker,
                                  args=(token, repo, branch, path_obj, remote_path, commit_msg),
                                  daemon=True)
        thread.start()
    
    def upload_worker(self, token, repo, branch, local_path, remote_path, commit_msg):
        """后台上传工作函数"""
        try:
            uploader = GitHubUploader(token, repo, branch)
            
            # 定义回调函数，用于更新日志
            def callback(success, message, is_progress=False):
                if self.stop_upload:
                    return
                if is_progress:
                    self.log(message)
                else:
                    if success:
                        self.log(message)
                    else:
                        self.log(message, is_error=True)
            
            if local_path.is_file():
                # 单个文件
                dest = remote_path if remote_path else local_path.name
                uploader.upload_file(local_path, dest, commit_msg, callback=callback)
            else:
                # 文件夹
                base = remote_path if remote_path else local_path.name
                uploader.upload_directory(local_path, base, commit_msg,
                                          ignore_hidden=self.ignore_hidden_var.get(),
                                          callback=callback)
            
            if not self.stop_upload:
                self.log("\n🎉 所有上传任务完成！")
            else:
                self.log("\n⚠️ 上传已由用户停止")
        except Exception as e:
            self.log(f"❌ 发生错误: {str(e)}", is_error=True)
        finally:
            # 恢复按钮状态
            self.root.after(0, self.upload_finished)
    
    def upload_finished(self):
        self.upload_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.stop_upload = False
    
    def stop_upload_cmd(self):
        self.stop_upload = True
        self.log("正在停止上传... (等待当前文件完成)")
        self.stop_btn.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = GitHubUploaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()