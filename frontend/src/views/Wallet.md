# 钱包页面功能说明

## 功能概述

钱包页面实现了完整的 MetaMask 钱包连接和管理功能，包括：

### 1. MetaMask 连接
- 检测是否安装 MetaMask
- 连接/断开钱包
- 自动检测已连接的钱包
- 监听账户和网络变化

### 2. 钱包信息显示
- 钱包地址（可复制）
- 原生代币余额（ETH、MATIC、BNB 等）
- 当前网络信息
- 网络切换功能

### 3. 网络管理
- 支持主流网络：Ethereum、Polygon、BSC 等
- 主网和测试网区分
- 一键切换网络
- 网络状态标签

### 4. 资产管理
- 显示原生代币余额
- 充值/提币功能
- 资产明细表格
- 24小时价格变化

### 5. 🆕 新增查询功能
- **Gas 费用查询**：实时获取当前网络的 Gas 价格
- **区块信息查询**：显示最新区块的详细信息
- **网络状态监控**：实时监控连接状态和网络状态
- **ERC-20 代币查询**：查询任意代币的余额和信息
- **常用代币列表**：预设常用代币，一键查询

## 技术实现

### 核心文件
- `utils/metamask.js` - MetaMask 连接工具
- `store/modules/wallet.js` - 钱包状态管理
- `api/wallet.js` - 钱包 API 服务
- `views/Wallet.vue` - 钱包页面组件
- `components/TokenQuery.vue` - 代币查询组件

### 主要功能模块

#### MetaMask 工具 (`utils/metamask.js`)
```javascript
// 连接钱包
const address = await connectMetaMask()

// 获取余额
const balance = await getAccountBalance(address)

// 获取网络信息
const network = await getNetworkInfo()

// 获取 Gas 价格
const gasPrice = await getGasPrice()

// 获取区块信息
const blockInfo = await getBlockInfo('latest')

// 获取代币余额
const tokenBalance = await getTokenBalance(tokenAddress, userAddress)

// 获取代币信息
const tokenInfo = await getTokenInfo(tokenAddress)
```

#### 状态管理 (`store/modules/wallet.js`)
```javascript
// 连接钱包
await this.$store.dispatch('wallet/connectWallet')

// 获取钱包状态
const connected = this.$store.getters['wallet/isConnected']
const address = this.$store.getters['wallet/walletAddress']
const balance = this.$store.getters['wallet/walletBalance']
const gasPrice = this.$store.getters['wallet/gasPrice']
const blockInfo = this.$store.getters['wallet/blockInfo']

// 更新信息
await this.$store.dispatch('wallet/updateAllInfo')
```

#### 代币查询组件 (`components/TokenQuery.vue`)
```javascript
// 查询代币信息
const tokenInfo = await this.getTokenInfo(tokenAddress)

// 查询代币余额
const balance = await this.getTokenBalance(tokenAddress)

// 选择常用代币
this.selectCommonToken(token)
```

## 使用方法

### 1. 连接钱包
1. 确保已安装 MetaMask 浏览器插件
2. 点击"连接 MetaMask"按钮
3. 在 MetaMask 弹窗中确认连接
4. 连接成功后显示钱包信息

### 2. 查看钱包信息
- **钱包地址**：显示当前连接的地址，点击复制按钮可复制
- **余额**：显示当前网络的原生代币余额
- **网络**：显示当前网络名称和切换按钮

### 3. 查询网络状态
- **Gas 价格**：显示当前网络的 Gas 费用，点击刷新按钮更新
- **当前区块**：显示最新区块号，点击刷新按钮更新
- **连接状态**：实时显示钱包连接状态

### 4. 查看区块信息
- **区块号**：最新区块的编号
- **时间戳**：区块生成的时间
- **Gas 使用情况**：区块的 Gas 限制和使用量
- **交易数量**：区块中包含的交易数量
- **矿工地址**：打包该区块的矿工地址

### 5. 查询代币信息
- **输入代币地址**：在输入框中输入 ERC-20 代币合约地址
- **点击查询**：获取代币的名称、符号、精度等信息
- **查看余额**：显示当前钱包中该代币的余额
- **常用代币**：点击预设的常用代币快速查询

### 6. 刷新信息
- **单独刷新**：每个信息卡片都有独立的刷新按钮
- **批量刷新**：点击"刷新所有信息"按钮一次性更新所有数据

## 支持的网络

### 主网
- **Ethereum Mainnet** (0x1) - ETH
- **Polygon Mainnet** (0x89) - MATIC
- **BSC Mainnet** (0x38) - BNB
- **Avalanche C-Chain** (0xa86a) - AVAX

### 测试网
- **Goerli Testnet** (0x5) - ETH
- **Mumbai Testnet** (0x13881) - MATIC
- **BSC Testnet** (0x61) - BNB

## 常用代币

### Ethereum 主网
- **USDT** (Tether USD) - 0xdAC17F958D2ee523a2206206994597C13D831ec7
- **USDC** (USD Coin) - 0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8
- **DAI** (Dai) - 0x6B175474E89094C44Da98b954EedeAC495271d0F
- **WETH** (Wrapped Ether) - 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2

## 注意事项

1. **MetaMask 安装**：必须安装 MetaMask 浏览器插件
2. **网络切换**：切换网络时需要在 MetaMask 中确认
3. **余额更新**：网络切换后会自动更新余额信息
4. **错误处理**：连接失败或网络错误会显示相应提示
5. **事件监听**：页面会自动监听账户和网络变化
6. **代币查询**：代币查询需要 RPC 节点支持，某些功能可能受限
7. **Gas 费用**：Gas 价格会实时变化，建议在交易前刷新

## 扩展功能

### 添加新网络
在 `utils/metamask.js` 的 `networkMap` 中添加新网络配置：

```javascript
const networkMap = {
  '0x1': { name: 'Ethereum Mainnet', symbol: 'ETH', explorer: 'https://etherscan.io', decimals: 18 },
  // 添加新网络
  '0x123': { name: 'New Network', symbol: 'NEW', explorer: 'https://explorer.new.network', decimals: 18 }
}
```

### 添加新代币
在 `components/TokenQuery.vue` 的 `commonTokens` 数组中添加新代币：

```javascript
commonTokens: [
  {
    name: 'New Token',
    symbol: 'NEW',
    address: '0x...',
    chainId: '0x1'
  }
]
```

### 自定义查询功能
可以扩展 `utils/metamask.js` 添加更多查询方法：

```javascript
// 获取交易历史
export async function getTransactionHistory(address, limit = 10)

// 获取 NFT 余额
export async function getNFTBalance(contractAddress, userAddress)

// 获取合约代码
export async function getContractCode(address)
```

## 性能优化

1. **防重复更新**：使用 `isUpdating` 标志防止重复调用
2. **延迟更新**：网络切换后延迟更新，避免冲突
3. **批量更新**：支持一次性更新所有信息
4. **错误处理**：完善的错误处理和用户提示
5. **响应式设计**：适配不同屏幕尺寸

现在钱包页面已经具备了完整的查询功能，可以满足大部分区块链钱包的使用需求！
