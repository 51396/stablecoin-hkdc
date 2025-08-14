// Provider管理器，确保在整个应用中只使用一个Provider实例
let provider = null;

export async function getProvider() {
  // 如果已经有Provider实例且MetaMask仍然可用，直接返回
  if (provider && typeof window !== 'undefined' && window.ethereum) {
    return provider;
  }
  
  // 检查MetaMask是否已安装
  if (typeof window === 'undefined' || !window.ethereum) {
    throw new Error('未检测到 MetaMask');
  }
  
  // 动态导入ethers.js
  const { ethers } = await import('ethers');
  
  // 创建新的Provider实例
  provider = new ethers.providers.Web3Provider(window.ethereum);
  return provider;
}

export function clearProvider() {
  provider = null;
}

export async function getSigner() {
  const provider = await getProvider();
  return provider.getSigner();
}