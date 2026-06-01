# -*- coding: utf-8 -*-
"""
GitHub 上传配置文件
请填写你的GitHub信息
"""

# GitHub配置
GITHUB_CONFIG = {
    "token": "",  # 你的GitHub Personal Access Token（必填）
    "repo": "dadabugaoxin/dadabugaoxinletter",  # 仓库名
    "branch": "main",  # 分支名
    "default_commit_message": "Update via upload tool"  # 默认提交消息
}

# 如何获取GitHub Token:
# 1. 登录GitHub
# 2. 进入 Settings -> Developer settings -> Personal access tokens
# 3. 点击 Generate new token
# 4. 勾选 repo 权限
# 5. 生成并复制token