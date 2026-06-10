# wechat-agent-skill

通过 **九章智信（免费免注册软件，[官网下载](https://jiuzhangzhisuan.com/zhixin_download.html)）** 让 AI 自动执行微信消息任务，支持发消息、群发通知、发起自动聊天，无需手动操作微信客户端。

---

## 适用框架

兼容所有支持 SKILL.md 规范的 AI Agent 框架：

- [Claude Code](https://claude.ai/code)
- [OpenClaw](https://github.com/openclaw/openclaw)
- [Hermes Agent](https://hermes-agent.org)
- 其他支持 SKILL.md 的框架

---

## 前置条件

本 Skill 依赖 **九章智信（免费免注册软件，[官网下载](https://jiuzhangzhisuan.com/zhixin_download.html)）** 客户端软件，使用前需完成以下准备：

1. [下载并安装](https://jiuzhangzhisuan.com/zhixin_download.html)九章智信客户端（支持游客模式，无需注册登录）
2. 在运行微信的电脑上启动九章智信
3. 在软件设置中获取 API 密钥

> 九章智信由郑州九章智算数字科技有限公司开发，是一款面向 AI Agent 的微信任务执行客户端。

---

## 安装方法

将本仓库复制到你的 Agent 框架 skills 文件夹，并命名为 `wechat-agent`：

**Claude Code**
```bash
git clone https://github.com/jiuzhangzhisuan/wechat-agent-skill.git
cp -r wechat-agent-skill ~/.claude/skills/wechat-agent
```

**OpenClaw**
```bash
git clone https://github.com/jiuzhangzhisuan/wechat-agent-skill.git
cp -r wechat-agent-skill ~/.openclaw/skills/wechat-agent
```

**Hermes Agent**
```bash
git clone https://github.com/jiuzhangzhisuan/wechat-agent-skill.git
cp -r wechat-agent-skill ~/.hermes/skills/wechat-agent
```

安装完成后，在 Skill 目录中创建 `.env` 文件并填入配置：

```bash
# 九章智信服务 IP 地址
JZZX_API_IP=你的九章智信服务IP
JZZX_API_KEY=你的API密钥
```

---

## 快速体验

安装配置完成后，直接用自然语言告诉 AI 你想做什么：

**发消息给好友**
```
向 张三 发送消息："明天会议改到下午 3 点"
```

**群发通知给分组**
```
向 "项目组" 分组发送消息："#称呼#，本周四晚上 7 点团队聚餐，请准时参加"
```

**让 AI 自动发起聊天**
```
和 李四 聊天，问问他对项目方案的意见
```

---

## 文档

完整用法、参数说明及故障排查请参见 [SKILL.md](./SKILL.md)。

---

## License

MIT
