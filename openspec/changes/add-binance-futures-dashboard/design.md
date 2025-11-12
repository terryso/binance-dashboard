## Context
基于nof1-tracker-dashboard项目的成功实践，我们需要使用Streamlit框架重新实现Binance合约dashboard。原项目使用Node.js/Express + 原生JavaScript，新项目将采用Python/Streamlit以提供更好的数据可视化能力和更简洁的开发体验。

## Goals / Non-Goals

### Goals
- 提供现代化的web界面和交互体验
- 实现实时数据监控和可视化
- 支持多账户管理和切换
- 提供灵活的配置和自定义选项
- 确保API安全和数据隐私
- 支持移动端友好界面

### Non-Goals
- 不实现交易功能（仅监控和分析）
- 不支持其他交易所（专注Binance Futures）
- 不提供历史数据存储（实时查询为主）

## Decisions

### Decision 1: 使用Streamlit作为主要框架
- **选择**: Streamlit v1.28+
- **理由**: 快速开发、内置组件丰富、适合数据科学应用、部署简单
- **替代方案**: Flask/FastAPI + React (更复杂)、Dash (学习成本高)

### Decision 2: 采用python-binance官方库
- **选择**: python-binance v1.0.19+
- **理由**: 官方维护、功能完整、文档完善、社区活跃
- **替代方案**: 自行实现API调用 (维护成本高)、其他第三方库 (风险较高)

### Decision 3: 数据可视化使用Plotly
- **选择**: Plotly + Streamlit内置图表组件
- **理由**: 交互性强、图表类型丰富、与Streamlit集成良好
- **替代方案**: Matplotlib (交互性差)、Altair (功能有限)、ECharts (集成复杂)

### Decision 4: 配置管理采用TOML格式
- **选择**: TOML配置文件 + 环境变量
- **理由**: 人类可读性好、支持注释、Python原生支持
- **替代方案**: JSON (无注释)、YAML (解析复杂)、INI (功能有限)

## Risks / Trade-offs

### Performance风险
- **风险**: 实时API调用可能导致响应延迟
- **缓解**: 实现数据缓存、异步加载、进度指示器

### Security风险
- **风险**: API密钥在前端暴露
- **缓解**: 仅在服务器端存储API密钥、使用Streamlit secrets管理

### 依赖风险
- **风险**: 外部API变更或限制
- **缓解**: 版本锁定、降级机制、错误处理

### 用户体验权衡
- **权衡**: 功能丰富性 vs 界面简洁性
- **决策**: 优先核心功能，渐进式增强

## Architecture Design

### 模块结构
```
binance-dashboard/
├── app.py                 # Streamlit主应用
├── config/
│   ├── __init__.py
│   ├── settings.py        # 配置管理
│   └── secrets.py         # 敏感信息管理
├── binance/
│   ├── __init__.py
│   ├── client.py          # API客户端
│   ├── models.py          # 数据模型
│   └── utils.py           # 工具函数
├── ui/
│   ├── __init__.py
│   ├── pages/             # 页面组件
│   ├── components/        # 可复用组件
│   └── charts/            # 图表组件
├── data/
│   ├── __init__.py
│   ├── processor.py       # 数据处理
│   └── cache.py           # 缓存管理
├── tests/                 # 测试文件
├── docs/                  # 文档
└── requirements.txt       # 依赖包
```

### 数据流
1. **用户交互** → Streamlit UI
2. **UI事件** → 处理函数
3. **数据处理** → Binance API调用
4. **API响应** → 数据处理和格式化
5. **结果展示** → UI组件更新

## Migration Plan

### 阶段1: 基础框架搭建
- 创建Streamlit应用结构
- 实现基本的API连接
- 建立配置管理系统

### 阶段2: 核心功能实现
- 账户信息展示
- 持仓数据监控
- 交易历史查询

### 阶段3: 高级功能
- 数据可视化
- 交互式图表
- 配置和设置

### 阶段4: 优化和部署
- 性能优化
- 错误处理完善
- 部署配置

## Open Questions

1. **数据存储策略**: 是否需要本地数据库存储历史数据？
2. **多账户支持**: 如何设计多账户切换的用户体验？
3. **实时性要求**: 数据刷新频率如何设定？
4. **部署方式**: 优先选择Streamlit Cloud还是自建服务器？
5. **国际化**: 是否需要多语言支持？

## Technical Requirements

### 依赖包清单
```
streamlit>=1.28.0
python-binance>=1.0.19
pandas>=2.0.0
plotly>=5.15.0
requests>=2.31.0
python-dotenv>=1.0.0
toml>=0.10.2
```

### 环境变量
```
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
USE_TESTNET=false
REFRESH_INTERVAL=60
```

### 配置文件结构
```toml
[app]
name = "Binance Futures Dashboard"
refresh_interval = 60
theme = "dark"

[binance]
use_testnet = false
timeout = 30

[display]
default_currency = "USDT"
timezone = "UTC"
date_format = "%Y-%m-%d %H:%M:%S"
```