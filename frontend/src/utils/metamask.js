// MetaMask 连接和钱包信息获取工具

// 检查是否安装了 MetaMask
export function isMetaMaskInstalled() {
  return typeof window.ethereum !== 'undefined' && window.ethereum.isMetaMask
}

// 连接 MetaMask
export async function connectMetaMask() {
  if (!isMetaMaskInstalled()) {
    throw new Error('请先安装 MetaMask 钱包')
  }

  try {
    // 请求连接账户
    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts'
    })
    
    if (accounts.length === 0) {
      throw new Error('用户拒绝了连接请求')
    }
    
    return accounts[0] // 返回第一个账户地址
  } catch (error) {
    throw new Error(`连接失败: ${error.message}`)
  }
}

// 获取当前连接的账户
export async function getCurrentAccount() {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    const accounts = await window.ethereum.request({
      method: 'eth_accounts'
    })
    return accounts.length > 0 ? accounts[0] : null
  } catch (error) {
    console.error('获取账户失败:', error)
    return null
  }
}

// 获取账户余额
export async function getAccountBalance(address) {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    const balance = await window.ethereum.request({
      method: 'eth_getBalance',
      params: [address, 'latest']
    })
    
    // 将 wei 转换为 ETH
    return parseInt(balance, 16) / Math.pow(10, 18)
  } catch (error) {
    console.error('获取余额失败:', error)
    return null
  }
}

// 获取当前网络信息
export async function getNetworkInfo() {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    const chainId = await window.ethereum.request({
      method: 'eth_chainId'
    })
    
    const networkMap = {
      // Ethereum 网络
      '0x1': { name: 'Ethereum Mainnet', symbol: 'ETH', explorer: 'https://etherscan.io', decimals: 18 },
      '0x5': { name: 'Goerli Testnet', symbol: 'ETH', explorer: 'https://goerli.etherscan.io', decimals: 18 },
      '0xaa36a7': { name: 'Sepolia Testnet', symbol: 'ETH', explorer: 'https://sepolia.etherscan.io', decimals: 18 },
      
      // Polygon 网络
      '0x89': { name: 'Polygon Mainnet', symbol: 'MATIC', explorer: 'https://polygonscan.com', decimals: 18 },
      '0x13881': { name: 'Mumbai Testnet', symbol: 'MATIC', explorer: 'https://mumbai.polygonscan.com', decimals: 18 },
      
      // BSC 网络
      '0x38': { name: 'BSC Mainnet', symbol: 'BNB', explorer: 'https://bscscan.com', decimals: 18 },
      '0x61': { name: 'BSC Testnet', symbol: 'tBNB', explorer: 'https://testnet.bscscan.com', decimals: 18 },
      
      // Avalanche 网络
      '0xa86a': { name: 'Avalanche C-Chain', symbol: 'AVAX', explorer: 'https://snowtrace.io', decimals: 18 },
      '0xa869': { name: 'Avalanche Fuji Testnet', symbol: 'AVAX', explorer: 'https://testnet.snowtrace.io', decimals: 18 },
      
      // Arbitrum 网络
      '0xa4b1': { name: 'Arbitrum One', symbol: 'ETH', explorer: 'https://arbiscan.io', decimals: 18 },
      '0x66eed': { name: 'Arbitrum Goerli', symbol: 'ETH', explorer: 'https://goerli.arbiscan.io', decimals: 18 },
      
      // Optimism 网络
      '0xa': { name: 'Optimism', symbol: 'ETH', explorer: 'https://optimistic.etherscan.io', decimals: 18 },
      '0x1a4': { name: 'Optimism Goerli', symbol: 'ETH', explorer: 'https://goerli-optimism.etherscan.io', decimals: 18 },
      
      // Fantom 网络
      '0xfa': { name: 'Fantom Opera', symbol: 'FTM', explorer: 'https://ftmscan.com', decimals: 18 },
      '0xfa2': { name: 'Fantom Testnet', symbol: 'FTM', explorer: 'https://testnet.ftmscan.com', decimals: 18 }
    }
    
    const network = networkMap[chainId]
    if (network) {
      return {
        chainId,
        ...network
      }
    } else {
      // 对于未知网络，尝试获取网络名称
      try {
        const networkName = await window.ethereum.request({
          method: 'net_version'
        })
        return {
          chainId,
          name: `Network ${parseInt(chainId, 16)}`,
          symbol: 'Unknown',
          explorer: '',
          decimals: 18
        }
      } catch {
        return {
          chainId,
          name: `Unknown Network (${chainId})`,
          symbol: 'Unknown',
          explorer: '',
          decimals: 18
        }
      }
    }
  } catch (error) {
    console.error('获取网络信息失败:', error)
    return null
  }
}

// 获取 Gas 费用估算
export async function getGasPrice() {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    const gasPrice = await window.ethereum.request({
      method: 'eth_gasPrice'
    })
    
    // 将 wei 转换为 Gwei
    return parseInt(gasPrice, 16) / Math.pow(10, 9)
  } catch (error) {
    console.error('获取 Gas 价格失败:', error)
    return null
  }
}

// 获取当前区块号
export async function getBlockNumber() {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    const blockNumber = await window.ethereum.request({
      method: 'eth_blockNumber'
    })
    
    return parseInt(blockNumber, 16)
  } catch (error) {
    console.error('获取区块号失败:', error)
    return null
  }
}

// 获取区块信息
export async function getBlockInfo(blockNumber = 'latest') {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    const block = await window.ethereum.request({
      method: 'eth_getBlockByNumber',
      params: [blockNumber, false]
    })
    
    if (block) {
      return {
        number: parseInt(block.number, 16),
        hash: block.hash,
        timestamp: parseInt(block.timestamp, 16),
        gasLimit: parseInt(block.gasLimit, 16),
        gasUsed: parseInt(block.gasUsed, 16),
        miner: block.miner,
        transactions: block.transactions.length
      }
    }
    return null
  } catch (error) {
    console.error('获取区块信息失败:', error)
    return null
  }
}

// 获取交易收据
export async function getTransactionReceipt(txHash) {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    const receipt = await window.ethereum.request({
      method: 'eth_getTransactionReceipt',
      params: [txHash]
    })
    
    if (receipt) {
      return {
        status: receipt.status === '0x1',
        blockNumber: parseInt(receipt.blockNumber, 16),
        gasUsed: parseInt(receipt.gasUsed, 16),
        cumulativeGasUsed: parseInt(receipt.cumulativeGasUsed, 16),
        effectiveGasPrice: parseInt(receipt.effectiveGasPrice, 16),
        contractAddress: receipt.contractAddress,
        logs: receipt.logs
      }
    }
    return null
  } catch (error) {
    console.error('获取交易收据失败:', error)
    return null
  }
}

// 监听交易状态变化
export function onTransactionStatusChange(callback) {
  if (!isMetaMaskInstalled()) {
    return
  }

  // 监听交易状态变化事件
  window.ethereum.on('transactionStatusChanged', callback)
}

// 移除交易状态变化监听器
export function removeTransactionStatusListener() {
  if (!isMetaMaskInstalled()) {
    return
  }

  window.ethereum.removeAllListeners('transactionStatusChanged')
}

// 获取交易历史（最近的交易）
export async function getTransactionHistory(address, limit = 10) {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    // 注意：这个方法需要 RPC 节点支持，不是所有节点都支持
    const transactions = await window.ethereum.request({
      method: 'eth_getTransactionHistory',
      params: [address, limit]
    })
    
    return transactions || []
  } catch (error) {
    console.error('获取交易历史失败:', error)
    // 如果 RPC 不支持，返回空数组
    return []
  }
}

// 获取代币余额（ERC-20）
export async function getTokenBalance(tokenAddress, userAddress) {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    // ERC-20 代币的 balanceOf 方法
    const data = '0x70a08231' + '000000000000000000000000' + userAddress.slice(2)
    
    const result = await window.ethereum.request({
      method: 'eth_call',
      params: [{
        to: tokenAddress,
        data: data
      }, 'latest']
    })
    
    // 获取代币精度
    const decimalsData = '0x313ce567'
    const decimalsResult = await window.ethereum.request({
      method: 'eth_call',
      params: [{
        to: tokenAddress,
        data: decimalsData
      }, 'latest']
    })
    
    const decimals = parseInt(decimalsResult, 16)
    const balance = parseInt(result, 16) / Math.pow(10, decimals)
    
    return balance
  } catch (error) {
    console.error('获取代币余额失败:', error)
    return null
  }
}

// 获取代币信息（ERC-20）
export async function getTokenInfo(tokenAddress) {
  if (!isMetaMaskInstalled()) {
    return null
  }

  try {
    // 获取代币名称
    const nameData = '0x06fdde03' // name() 方法
    const nameResult = await window.ethereum.request({
      method: 'eth_call',
      params: [{
        to: tokenAddress,
        data: nameData
      }, 'latest']
    })
    
    // 获取代币符号
    const symbolData = '0x95d89b41' // symbol() 方法
    const symbolResult = await window.ethereum.request({
      method: 'eth_call',
      params: [{
        to: tokenAddress,
        data: symbolData
      }, 'latest']
    })
    
    // 获取代币精度
    const decimalsData = '0x313ce567' // decimals() 方法
    const decimalsResult = await window.ethereum.request({
      method: 'eth_call',
      params: [{
        to: tokenAddress,
        data: decimalsData
      }, 'latest']
    })
    
    // 解码字符串（简化处理）
    const name = decodeAbiString(nameResult)
    const symbol = decodeAbiString(symbolResult)
    const decimals = parseInt(decimalsResult, 16)
    
    return {
      name: name || 'Unknown Token',
      symbol: symbol || 'UNKNOWN',
      decimals: decimals || 18,
      address: tokenAddress
    }
  } catch (error) {
    console.error('获取代币信息失败:', error)
    return null
  }
}

// 解码十六进制字符串（兼容 ABI 动态 string 与 bytes32）
function decodeAbiString(hex) {
  if (!hex || hex === '0x') return ''
  try {
    const cleanHex = hex.startsWith('0x') ? hex.slice(2) : hex
    // bytes32（定长 32 字节 => 64 hex）
    if (cleanHex.length === 64) {
      const trimmed = trimRightZeros(cleanHex)
      return hexToUtf8(trimmed)
    }
    // 兼容 ABI 动态字符串编码: [offset][length][data...]
    // 单返回值时 offset 通常为 0x20（32 字节 => 64 hex）
    const offsetHex = cleanHex.slice(0, 64)
    let offset = parseInt(offsetHex, 16)
    if (!Number.isFinite(offset) || offset === 0) {
      // 退化处理：大多数实现为 0x20
      offset = 32
    }
    const offsetIndex = offset * 2
    const lengthHex = cleanHex.slice(offsetIndex, offsetIndex + 64)
    const strLength = parseInt(lengthHex, 16)
    const dataStart = offsetIndex + 64
    const dataHex = cleanHex.slice(dataStart, dataStart + strLength * 2)
    if (dataHex.length > 0) {
      return hexToUtf8(dataHex)
    }
    // 回退到 bytes32 尝试
    const fallback = trimRightZeros(cleanHex.slice(0, 64))
    return hexToUtf8(fallback)
  } catch (e) {
    return ''
  }
}

function trimRightZeros(hex) {
  return hex.replace(/(00)+$/g, '')
}

function hexToUtf8(hex) {
  if (!hex) return ''
  // hex => Uint8Array
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(hex.substr(i * 2, 2), 16)
  }
  try {
    const decoder = new TextDecoder('utf-8')
    return decoder.decode(bytes).replace(/\0/g, '')
  } catch (e) {
    // 最后回退使用基本 ASCII 解码
    return Array.from(bytes)
      .map((b) => (b >= 32 && b <= 126 ? String.fromCharCode(b) : ''))
      .join('')
      .replace(/\0/g, '')
  }
}

// 切换网络
export async function switchNetwork(chainId) {
  if (!isMetaMaskInstalled()) {
    throw new Error('请先安装 MetaMask 钱包')
  }

  try {
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId }]
    })
  } catch (error) {
    // 如果网络不存在，尝试添加网络
    if (error.code === 4902) {
      throw new Error('请先在 MetaMask 中添加该网络')
    }
    throw error
  }
}

// 添加网络到 MetaMask
export async function addNetwork(networkConfig) {
  if (!isMetaMaskInstalled()) {
    throw new Error('请先安装 MetaMask 钱包')
  }

  try {
    await window.ethereum.request({
      method: 'wallet_addEthereumChain',
      params: [networkConfig]
    })
  } catch (error) {
    throw new Error(`添加网络失败: ${error.message}`)
  }
}

// 监听账户变化
export function onAccountsChanged(callback) {
  if (!isMetaMaskInstalled()) {
    return
  }

  window.ethereum.on('accountsChanged', callback)
}

// 监听网络变化
export function onChainChanged(callback) {
  if (!isMetaMaskInstalled()) {
    return
  }

  window.ethereum.on('chainChanged', callback)
}

// 移除监听器
export function removeListeners() {
  if (!isMetaMaskInstalled()) {
    return
  }

  window.ethereum.removeAllListeners()
  // 特别移除交易状态变化监听器
  removeTransactionStatusListener()
}
