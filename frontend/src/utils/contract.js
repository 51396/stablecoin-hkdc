export async function getProvider() {
  if (typeof window === 'undefined' || !window.ethereum) {
    throw new Error('未检测到 MetaMask')
  }
  const { ethers } = await import('ethers')
  return new ethers.providers.Web3Provider(window.ethereum)
}

export async function getSigner() {
  const provider = await getProvider()
  return provider.getSigner()
}

export const HKDC_ABI = [
  // Read
  'function owner() view returns (address)',
  'function decimals() view returns (uint8)',
  'function balanceOf(address) view returns (uint256)',
  // Write (owner only)
  'function mint(address to, uint256 amount)',
  'function burn(address from, uint256 amount)',
  'function setWhitelistEnabled(bool enabled)',
  'function addToWhitelist(address account)',
  'function removeFromWhitelist(address account)'
]

export async function getHKDCContract(contractAddress) {
  if (!contractAddress) throw new Error('缺少合约地址')
  const { ethers } = await import('ethers')
  const signer = await getSigner()
  return new ethers.Contract(contractAddress, HKDC_ABI, signer)
}

export async function fetchOwnerAddress(contractAddress) {
  const contract = await getHKDCContract(contractAddress)
  return contract.owner()
}

export async function isOwner(contractAddress, currentAddress) {
  if (!currentAddress) return false
  const owner = await fetchOwnerAddress(contractAddress)
  return owner.toLowerCase() === currentAddress.toLowerCase()
}

export async function mintHKDC(contractAddress, toAddress, amount, decimals = 6) {
  const contract = await getHKDCContract(contractAddress)
  const { ethers } = await import('ethers')
  const value = ethers.utils.parseUnits(String(amount), decimals)
  const tx = await contract.mint(toAddress, value)
  return tx.wait()
}

export async function burnHKDC(contractAddress, fromAddress, amount, decimals = 6) {
  const contract = await getHKDCContract(contractAddress)
  const { ethers } = await import('ethers')
  const value = ethers.utils.parseUnits(String(amount), decimals)
  const tx = await contract.burn(fromAddress, value)
  return tx.wait()
}

export async function setWhitelistOnChain(contractAddress, enabled) {
  const contract = await getHKDCContract(contractAddress)
  const tx = await contract.setWhitelistEnabled(Boolean(enabled))
  return tx.wait()
}

export async function addToWhitelistOnChain(contractAddress, account) {
  const contract = await getHKDCContract(contractAddress)
  const tx = await contract.addToWhitelist(account)
  return tx.wait()
}

export async function removeFromWhitelistOnChain(contractAddress, account) {
  const contract = await getHKDCContract(contractAddress)
  const tx = await contract.removeFromWhitelist(account)
  return tx.wait()
}
