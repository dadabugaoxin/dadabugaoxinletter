# -*- coding: utf-8 -*-
"""
GitHub 简易上传脚本
直接使用git命令上传，无需token
"""

import os
import subprocess
import sys

def run_git_command(cmd, cwd=None):
    """执行git命令"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True,
            encoding='utf-8'
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), -1

def upload_to_github(folder_path, commit_message="Update files"):
    """上传文件夹内容到GitHub"""
    print("=" * 40)
    print("      GitHub 简易上传工具")
    print("=" * 40)
    print("\n上传目录: " + folder_path)
    
    # 检查目录是否存在
    if not os.path.isdir(folder_path):
        print("错误：目录不存在")
        return False
    
    # 检查是否是git仓库
    git_dir = os.path.join(folder_path, ".git")
    if not os.path.isdir(git_dir):
        print("\n初始化Git仓库...")
        stdout, stderr, code = run_git_command("git init", folder_path)
        if code != 0:
            print("初始化失败: " + stderr)
            return False
        
        # 配置用户信息
        run_git_command('git config user.email "upload@local"', folder_path)
        run_git_command('git config user.name "Upload Script"', folder_path)
    
    # 添加文件（排除.git目录）
    print("\n添加文件...")
    stdout, stderr, code = run_git_command("git add --all", folder_path)
    if code != 0:
        print("添加文件失败: " + stderr)
        return False
    
    # 提交
    print("提交: " + commit_message)
    stdout, stderr, code = run_git_command('git commit -m "' + commit_message + '"', folder_path)
    if code != 0:
        if "nothing to commit" in stderr or "nothing added to commit" in stderr:
            print("没有需要提交的内容")
        else:
            print("提交失败: " + stderr)
            return False
    
    # 检查远程仓库
    print("\n检查远程仓库...")
    stdout, stderr, code = run_git_command("git remote get-url origin", folder_path)
    if code != 0:
        print("添加远程仓库...")
        repo_url = "https://github.com/dadabugaoxin/dadabugaoxinletter.git"
        stdout, stderr, code = run_git_command("git remote add origin " + repo_url, folder_path)
        if code != 0:
            print("添加远程失败: " + stderr)
            return False
    else:
        print("远程仓库: " + stdout)
    
    # 推送
    print("\n推送到GitHub...")
    stdout, stderr, code = run_git_command("git push -f origin main", folder_path)
    if code != 0:
        print("推送失败: " + stderr)
        return False
    
    print("\n✅ 上传成功！")
    return True

if __name__ == "__main__":
    # 默认上传当前目录
    folder_path = os.path.dirname(os.path.abspath(__file__))
    
    # 解析命令行参数
    if len(sys.argv) >= 2:
        folder_path = sys.argv[1]
    
    commit_msg = "Auto upload"
    if len(sys.argv) >= 3:
        commit_msg = " ".join(sys.argv[2:])
    
    # 执行上传
    success = upload_to_github(folder_path, commit_msg)
    
    if not success:
        sys.exit(1)