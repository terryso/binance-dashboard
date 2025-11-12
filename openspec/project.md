# Project Context

## Purpose
本项目旨在创建一个基于Streamlit的Binance合约交易监控dashboard，提供实时的账户资产管理、持仓监控、交易历史分析和数据可视化功能。参考nof1-tracker-dashboard项目的成功实践，使用Python生态系统提供更现代化的用户体验和更强的数据分析能力。

## Tech Stack
- **Frontend Framework**: Streamlit 1.28+ (Python web framework)
- **Backend**: Python 3.9+
- **API Integration**: python-binance (official Binance API client)
- **Data Processing**: pandas, numpy
- **Visualization**: Plotly, Streamlit Charts
- **Configuration**: TOML, python-dotenv
- **Security**: Streamlit secrets management
- **Testing**: pytest
- **Deployment**: Streamlit Cloud, Docker

## Project Conventions

### Code Style
- **Python**: 遵循PEP 8标准，使用black进行代码格式化
- **命名约定**:
  - 文件名：snake_case (e.g., `account_monitor.py`)
  - 类名：PascalCase (e.g., `BinanceClient`)
  - 函数名：snake_case (e.g., `get_account_balance`)
  - 常量：UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)
- **文档字符串**: 使用Google风格docstrings
- **类型注解**: 所有函数使用type hints
- **导入顺序**: stdlib -> 第三方 -> 本地模块

### Architecture Patterns
- **分层架构**: UI层、业务逻辑层、数据访问层分离
- **模块化设计**: 按功能模块组织代码 (binance/, ui/, data/, config/)
- **依赖注入**: 使用工厂模式管理API客户端和配置
- **缓存策略**: 实现多层数据缓存减少API调用
- **错误处理**: 统一异常处理和用户友好的错误信息
- **配置驱动**: 使用TOML配置文件和环境变量管理设置

### Testing Strategy
- **单元测试**: pytest + coverage >= 80%
- **集成测试**: API客户端和数据处理模块测试
- **E2E测试**: Streamlit应用关键用户流程测试
- **Mock测试**: 使用unittest.mock模拟Binance API响应
- **测试环境**: 独立的测试数据库和配置
- **CI/CD**: GitHub Actions自动化测试和部署

### Git Workflow
- **分支策略**: GitFlow (main, develop, feature/*, release/*, hotfix/*)
- **提交格式**: Conventional Commits
  - `feat:` 新功能
  - `fix:` Bug修复
  - `docs:` 文档更新
  - `style:` 代码格式化
  - `refactor:` 重构
  - `test:` 测试相关
  - `chore:` 构建和工具相关
- **PR规范**: 必须通过所有检查，至少一个代码审查
- **发布标签**: 使用语义化版本 (v1.0.0)

## Domain Context

### Binance Futures API
- **端点**: 主要使用Futures API (fapi.binance.com)
- **认证**: HMAC-SHA256签名
- **限制**: 请求频率限制和权重管理
- **数据类型**:
  - 账户信息 (`/fapi/v2/account`)
  - 持仓信息 (`/fapi/v2/positionRisk`)
  - 交易历史 (`/fapi/v2/userTrades`)

### 交易监控概念
- **总资产**: 钱包余额 + 未实现盈亏
- **保证金**: 可用保证金、维持保证金、保证金率
- **持仓**: 多头/空头仓位、开仓价格、标记价格
- **盈亏计算**: 基于基准日期的累计收益分析
- **风险管理**: 强平价格、杠杆率、仓位分布

### 数据可视化需求
- **实时更新**: 30-300秒可配置刷新间隔
- **交互图表**: 支持缩放、筛选、钻取
- **响应式设计**: 适配桌面和移动设备
- **主题支持**: 深色/浅色模式切换

## Important Constraints

### 安全约束
- **API密钥管理**: 不得在前端暴露，使用secrets管理
- **权限最小化**: 仅请求必要的API权限
- **数据隐私**: 不存储用户敏感交易数据
- **网络安全**: HTTPS传输，CORS配置

### 性能约束
- **响应时间**: 页面加载 < 3秒，数据刷新 < 5秒
- **并发限制**: 支持多用户同时访问
- **内存使用**: 单实例内存占用 < 512MB
- **API调用**: 实现智能缓存和请求限流

### 业务约束
- **只读监控**: 不实现交易功能，仅监控和分析
- **交易所限制**: 仅支持Binance Futures，不支持现货交易
- **合规要求**: 遵守Binance API使用条款
- **数据准确性**: 确保与Binance官方数据一致

## External Dependencies

### Binance API
- **服务**: Binance Futures API v2
- **认证方式**: API Key + Secret Key
- **可用性**: 需要处理API维护和故障
- **数据格式**: JSON响应，RESTful接口

### Streamlit Cloud
- **部署平台**: Streamlit Cloud (首选)
- **资源限制**: 免费版CPU和内存限制
- **自定义域名**: 支持绑定自定义域名
- **环境变量**: 通过secrets管理配置

### 第三方库依赖
```toml
streamlit = "^1.28.0"
python-binance = "^1.0.19"
pandas = "^2.0.0"
plotly = "^5.15.0"
requests = "^2.31.0"
python-dotenv = "^1.0.0"
toml = "^0.10.2"
pytest = "^7.0.0"
black = "^23.0.0"
flake8 = "^6.0.0"
```
