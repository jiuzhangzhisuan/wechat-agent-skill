#!/usr/bin/env python3
"""
WeChat Agent API Client
通过九章智信客户端控制微信收发消息
"""

import os
import requests
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class WeChatAgent:
    """九章智信 API 客户端"""

    def __init__(self, api_ip: str = None, api_key: str = None, creator_name: str = None):
        """
        初始化客户端

        Args:
            api_ip: 九章智信服务 IP 地址
            api_key: API 密钥，用于认证
            creator_name: 创建者名称（可选），用于标识任务创建者

        说明：如果未提供 creator_name，将自动从 IDENTITY.md 读取我的名字
        """
        # 优先使用参数，其次使用环境变量，最后从 IDENTITY.md 读取
        if creator_name is None:
            creator_name = os.getenv('JZZX_CREATOR_NAME', None)

        if creator_name is None:
            creator_name = self._load_creator_name()

        # 优先使用参数，其次使用环境变量
        api_ip = api_ip or os.getenv('JZZX_API_IP')

        if not api_ip:
            raise ValueError("缺少配置：请设置 JZZX_API_IP 环境变量或传入 api_ip 参数")

        self.base_url = f"https://{api_ip.strip()}:28658"

        self.api_key = api_key or os.getenv('JZZX_API_KEY')

        if not self.api_key:
            raise ValueError("缺少配置：请设置 JZZX_API_KEY 环境变量或传入 api_key 参数")

        self.creator_name = creator_name

        # 确保 URL 末尾没有斜杠
        self.base_url = self.base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.verify = False  # 忽略自签名证书

    @staticmethod
    def _load_creator_name() -> str:
        """从常见位置读取 Agent 名称，读取失败时使用默认值。"""
        identity_files = [
            Path.cwd() / 'IDENTITY.md',
            Path(__file__).resolve().parent.parent / 'IDENTITY.md',
            Path('/root/.openclaw/workspace/IDENTITY.md'),
        ]

        for identity_file in identity_files:
            try:
                content = identity_file.read_text(encoding='utf-8')
            except OSError:
                continue

            for line in content.splitlines():
                if '**Name:' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        return parts[1].strip().lstrip(' *').strip()

        return 'AI Agent'

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, use_json: bool = True) -> Dict[str, Any]:
        """
        发送 API 请求

        Args:
            method: HTTP 方法 (GET, POST)
            endpoint: API 路径
            data: 请求体数据
            use_json: 是否使用 JSON body

        Returns:
            API 响应数据
        """
        url = f"{self.base_url}{endpoint}"

        if method == 'GET':
            response = requests.get(url, headers=self.headers, verify=self.verify)
        elif method == 'POST':
            if use_json:
                response = requests.post(url, headers=self.headers, json=data, verify=self.verify)
            else:
                # POST without JSON body (for abort)
                response = requests.post(url, headers=self.headers, verify=self.verify)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        result = response.json()

        if not result.get('success'):
            raise Exception(f"API error: {result}")

        return result.get('data', {})

    def get_contacts(self) -> List[Dict[str, str]]:
        """
        查询所有好友列表

        Returns:
            好友列表，每个好友包含 wxid 和 name
        """
        data = self._request('GET', '/api/v1/contacts')
        contacts = data.get('contacts', [])

        result = []
        for contact in contacts:
            result.append({
                'wxid': contact.get('微信ID', ''),
                'name': contact.get('备注', ''),
                'nickname': contact.get('昵称', '')
            })

        return result

    def get_groups(self) -> List[str]:
        """
        查询所有好友分组列表

        Returns:
            分组名称列表
        """
        data = self._request('GET', '/api/v1/groups')
        groups = data.get('groups', [])

        # 如果分组是字符串列表，直接返回
        if groups and isinstance(groups[0], str):
            return groups

        # 如果是对象列表，提取名称
        result = []
        for group in groups:
            if isinstance(group, dict):
                result.append(group.get('name', ''))
            else:
                result.append(str(group))

        return result

    def send_message(self, wxids: Optional[List[str]] = None, names: Optional[List[str]] = None,
                     groups: Optional[List[str]] = None, content: str = '', creator: str = None) -> Dict[str, Any]:
        """
        发送消息给指定好友或分组

        Args:
            wxids: 好友 wxid 列表
            names: 好友名称列表
            groups: 分组名称列表
            content: 消息内容
            creator: 创建者标识（可选），如果未提供则使用 creator_name 配置的值

        Returns:
            任务信息，包含 task_id
        """
        # 如果未指定 creator，使用创建者名称
        if creator is None:
            creator = self.creator_name

        data = {
            'type': 'send',
            'content': content,
            'creator': creator
        }

        if wxids:
            data['wxids'] = wxids
        if names:
            data['names'] = names
        if groups:
            data['groups'] = groups

        result = self._request('POST', '/api/v1/tasks', data)
        return {
            'task_id': result.get('manager_task_id'),
            'task_type': result.get('task_type'),
            'queued': result.get('queued'),
            'hint': result.get('hint')
        }

    def chat(self, wxids: Optional[List[str]] = None, names: Optional[List[str]] = None,
             groups: Optional[List[str]] = None, content: str = '', creator: str = None) -> Dict[str, Any]:
        """
        发起聊天任务

        Args:
            wxids: 好友 wxid 列表
            names: 好友名称列表
            groups: 分组名称列表
            content: 初始消息内容
            creator: 创建者标识（可选），如果未提供则使用 creator_name 配置的值

        Returns:
            任务信息，包含 task_id
        """
        # 如果未指定 creator，使用创建者名称
        if creator is None:
            creator = self.creator_name

        data = {
            'type': 'chat',
            'content': content,
            'creator': creator
        }

        if wxids:
            data['wxids'] = wxids
        if names:
            data['names'] = names
        if groups:
            data['groups'] = groups

        result = self._request('POST', '/api/v1/tasks', data)
        return {
            'task_id': result.get('manager_task_id'),
            'task_type': result.get('task_type'),
            'queued': result.get('queued'),
            'hint': result.get('hint')
        }

    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务 ID

        Returns:
            任务详细信息，包括状态、报告等
        """
        return self._request('GET', f'/api/v1/tasks/{task_id}')

    def abort_task(self, task_id: int) -> Dict[str, Any]:
        """
        取消任务（仅在 queued 状态时可用）

        Args:
            task_id: 任务 ID

        Returns:
            取消结果
        """
        return self._request('POST', f'/api/v1/tasks/{task_id}/abort', use_json=False)

    def resolve_contact(self, query: str, contacts: List[Dict[str, str]]) -> List[str]:
        """
        根据名称或 wxid 解析联系人

        Args:
            query: 查询字符串（可以是名称或 wxid）
            contacts: 好友列表

        Returns:
            匹配的 wxid 列表
        """
        wxids = []

        for contact in contacts:
            if query in contact['name'] or query == contact['wxid']:
                wxids.append(contact['wxid'])

        return wxids

    def resolve_groups(self, group_names: List[str], groups: List[str]) -> List[str]:
        """
        根据分组名称获取所有成员 wxid

        Args:
            group_names: 分组名称列表
            groups: 分组名称列表 (API 返回的是简单列表)

        Returns:
            所有成员的 wxid 列表（需要先获取完整信息）
        """
        # 这里需要进一步处理，因为 API 返回的是简单的分组名称列表
        # 暂时返回空列表，实际需要时可以通过其他 API 获取
        return []


def main():
    """命令行测试"""
    import sys

    # 从参数或环境变量读取配置
    api_ip = None
    api_key = None

    if len(sys.argv) > 1:
        api_ip = sys.argv[1]
    if len(sys.argv) > 2:
        api_key = sys.argv[2]

    # 使用环境变量作为默认值
    client = WeChatAgent(api_ip=api_ip, api_key=api_key)

    if len(sys.argv) < 3:
        print("Usage: python wechat_agent.py <api_ip> <api_key> <command> [args]")
        print("Commands: contacts, groups, send, chat, status, abort")
        return

    command = sys.argv[3]

    if command == 'contacts':
        contacts = client.get_contacts()
        print(json.dumps(contacts, ensure_ascii=False, indent=2))

    elif command == 'groups':
        groups = client.get_groups()
        print(json.dumps(groups, ensure_ascii=False, indent=2))

    elif command == 'send':
        if len(sys.argv) < 6:
            print("Usage: send <wxid_or_name> <content>")
            return
        wxids = _parse_wxids_arg(sys.argv[4])
        content = sys.argv[5]
        creator = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] else None

        result = client.send_message(wxids=wxids, content=content, creator=creator)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'chat':
        if len(sys.argv) < 6:
            print("Usage: chat <wxid_or_name> <content>")
            return
        wxids = _parse_wxids_arg(sys.argv[4])
        content = sys.argv[5]
        creator = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] else None

        result = client.chat(wxids=wxids, content=content, creator=creator)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'status':
        if len(sys.argv) < 5:
            print("Usage: status <task_id>")
            return
        task_id = int(sys.argv[4])
        status = client.get_task_status(task_id)
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif command == 'abort':
        if len(sys.argv) < 5:
            print("Usage: abort <task_id>")
            return
        task_id = int(sys.argv[4])
        result = client.abort_task(task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")


def _parse_wxids_arg(value: str) -> List[str]:
    """支持单个 wxid 或 JSON 数组两种命令行入参。"""
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return [value]

    if isinstance(parsed, list):
        return [str(item) for item in parsed if item]
    if parsed:
        return [str(parsed)]
    return []


if __name__ == '__main__':
    main()
