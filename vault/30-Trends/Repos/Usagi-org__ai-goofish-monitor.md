---
repo: Usagi-org/ai-goofish-monitor
url: https://github.com/Usagi-org/ai-goofish-monitor
language: Python
stars: 17724
summary: "Playwright和AI驱动的闲鱼多任务实时监控与智能分析系统，配备可视化的Web管理界面帮助用户精准寻找心仪商品。"
main_category: "AI应用"
categories: ["AI应用", "自动化", "数据采集"]
first_seen: 2026-11-06
last_seen: 2026-11-06
appearances: 1
tags: [ai-trend, repo]
---
# Usagi-org/ai-goofish-monitor

> Playwright和AI驱动的闲鱼多任务实时监控与智能分析系统，配备可视化的Web管理界面帮助用户精准寻找心仪商品。

## 개요
这是一个基于网页自动化与人工智能的闲鱼商品监控系统，旨在解决海量二手商品中手动筛选效率低下的问题。用户通过Web管理界面配置监控任务、关键词与AI分析规则后，系统会自动抓取并分析商品。当发现符合条件的商品时，系统会通过多种渠道发送即时通知并将记录保存到数据库中。

## 주요 기능
- Web可视化管理: 在网页端统一管理任务、账号、运行日志和监控结果
- AI驱动分析: 使用自然语言创建任务并通过多模态模型深度分析商品
- 多任务并发: 独立配置各个任务的关键词、价格、筛选条件和分析提示词
- 高级筛选: 支持包邮、发布时间范围以及省市区三级区域精准筛选
- 即时通知: 支持通过ntfy.sh、企业微信、Bark、Telegram等渠道发送提醒
- 代理与账号轮换: 管理多个闲鱼账号并支持代理池轮换与失败自动重试

## 참고·주의
- 需要准备支持图片输入的OpenAI兼容接口API Key
- 需要配置闲鱼账号登录态才能正常抓取商品
- 过于频繁的请求可能会导致闲鱼账号被限制

## 등장 기록
| 날짜 | Today | Week | Month | ★ |
|---|---|---|---|---|
| 2026-11-06 | 4위 (+240) | – | – | 17,724 |
