#!/usr/bin/env python3
"""
WeChat API 调用脚本 - 供 AI 调用
支持发送消息、发起聊天、查询联系人和任务状态
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List


def run_wechat_agent(api_ip: str = None, api_key: str = None, command: str = '',
                     args: List[str] = None) -> dict:
    """
    运行 wechat_agent.py 脚本并返回结果
    
    Args:
        api_ip: 九章智信服务 IP 地址（可选，默认为环境变量）
        api_key: API 密钥（可选，默认为环境变量）
        command: 命令 (contacts, groups, send, chat, status)
        args: 命令参数
        
    Returns:
        解析后的 JSON 结果
    """
    script_path = Path(__file__).resolve().with_name('wechat_agent.py')
    cmd = [
        sys.executable, str(script_path),
        api_ip or '', api_key or '', command
    ]
    
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': result.stderr
            }
        
        # 检查是否有输出
        if not result.stdout.strip():
            return {
                'success': True,
                'data': {}
            }
        
        return json.loads(result.stdout)
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': '请求超时'
        }
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': f'JSON 解析失败：{result.stdout}'
        }


def get_contacts(api_ip: str, api_key: str) -> dict:
    """查询好友列表"""
    return run_wechat_agent(api_ip, api_key, 'contacts')


def get_groups(api_ip: str, api_key: str) -> dict:
    """查询分组列表"""
    return run_wechat_agent(api_ip, api_key, 'groups')


def send_message(api_ip: str = None, api_key: str = None, wxids: List[str] = None,
                 content: str = '', creator: str = None) -> dict:
    """发送消息"""
    return run_wechat_agent(
        api_ip, api_key, 'send',
        [json.dumps(wxids), content, creator or '']
    )


def chat(api_ip: str = None, api_key: str = None, wxids: List[str] = None,
         content: str = '', creator: str = None) -> dict:
    """发起聊天"""
    return run_wechat_agent(
        api_ip, api_key, 'chat',
        [json.dumps(wxids), content, creator or '']
    )


def get_task_status(api_ip: str, api_key: str, task_id: int) -> dict:
    """查询任务状态"""
    return run_wechat_agent(
        api_ip, api_key, 'status',
        [str(task_id)]
    )


def abort_task(api_ip: str, api_key: str, task_id: int) -> dict:
    """取消任务（仅在 queued 状态时可用）"""
    return run_wechat_agent(
        api_ip, api_key, 'abort',
        [str(task_id)]
    )


def check_personalization(content: str) -> dict:
    """
    检查消息是否可以使用个性化占位符，并给出建议
    
    Args:
        content: 消息内容
        
    Returns:
        包含建议的字典
    """
    suggestions = []
    
    # 检测消息中是否包含占位符
    has_placeholder = '#称呼#' in content or '#青龙#' in content or '#白虎#' in content
    
    # 检测消息是否像是群发消息（包含"所有"、"全部"、"每个"等词）
    is_massage = any(word in content for word in ['所有', '全部', '每个', 'everyone', 'all'])
    
    if is_massage and not has_placeholder:
        suggestions.append({
            'type': 'suggestion',
            'message': '检测到您可能要发送群发消息。建议添加 #称呼# 占位符实现个性化，例如："#称呼#，新年快乐！"这样每个人会收到带有自己称呼的消息。',
            'placeholder': '#称呼#'
        })
    
    # 检测消息是否涉及节日/问候
    is_greeting = any(word in content for word in ['新年', '快乐', '快乐', '祝福', '恭喜', '生日', '春节', '中秋'])
    
    if is_greeting and not has_placeholder:
        suggestions.append({
            'type': 'suggestion',
            'message': '这是一个节日/问候消息，使用 #称呼# 会让对方感觉更贴心！',
            'placeholder': '#称呼#'
        })
    
    return {
        'has_placeholder': has_placeholder,
        'suggestions': suggestions
    }


if __name__ == '__main__':
    # 简单测试（需要配置好环境变量）
    import os
    
    api_ip = os.getenv('JZZX_API_IP')
    api_key = os.getenv('JZZX_API_KEY')
    
    # 检查是否有配置
    if not api_ip or not api_key:
        print("⚠️  请先在 .env 文件中配置环境变量")
        print("示例:")
        print("  JZZX_API_IP=your-server-ip")
        print("  JZZX_API_KEY=your-api-key-here")
        sys.exit(1)
    
    # 测试查询好友
    print("查询好友列表...")
    try:
        contacts = get_contacts(api_ip, api_key)
        print(json.dumps(contacts, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"查询失败：{e}")
