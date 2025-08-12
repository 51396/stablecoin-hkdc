#!/usr/bin/env node
import { ethers } from 'ethers';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

const ERC20_MIN_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function decimals() view returns (uint8)",
];

const SELECTOR_NAME = ethers.dataSlice(ethers.id('name()'), 0, 4);
const SELECTOR_SYMBOL = ethers.dataSlice(ethers.id('symbol()'), 0, 4);

function tryDecode(types, data) {
  try {
    const [decoded] = ethers.AbiCoder.defaultAbiCoder().decode(types, data);
    return decoded;
  } catch (_) {
    return null;
  }
}

function decodeBytes32StringSafe(value) {
  try {
    return ethers.decodeBytes32String(value);
  } catch (_) {
    return null;
  }
}

async function callMetadata(provider, address, selector) {
  const raw = await provider.call({ to: address, data: ethers.concat([selector]) });
  // Try decode as string first
  let asString = tryDecode(['string'], raw);
  if (typeof asString === 'string' && asString.length > 0) return asString;
  // Try decode as bytes32 -> string
  const asBytes32 = tryDecode(['bytes32'], raw);
  const decoded = asBytes32 ? decodeBytes32StringSafe(asBytes32) : null;
  if (decoded && decoded.length > 0) return decoded;
  return null;
}

async function readMetadata(provider, tokenAddress, contract) {
  let name = null;
  let symbol = null;
  let decimals = null;

  try {
    name = await callMetadata(provider, tokenAddress, SELECTOR_NAME);
  } catch (_) {}
  try {
    symbol = await callMetadata(provider, tokenAddress, SELECTOR_SYMBOL);
  } catch (_) {}
  try {
    decimals = await contract.decimals();
  } catch (_) {
    decimals = 18; // safe default
  }

  return {
    name: name || 'Unknown',
    symbol: symbol || 'UNKNOWN',
    decimals,
  };
}

function isLikelyScaled(value) {
  // Heuristic: human-readable strings often include a decimal point or are small.
  // If value is a string with '.', assume already scaled.
  if (typeof value === 'string' && value.includes('.')) return true;
  // If value is a number (not bigint) and less than 1e12, assume scaled.
  if (typeof value === 'number') return true;
  return false;
}

function formatBalance(rawBalance, decimals, alreadyScaled = false) {
  if (alreadyScaled || isLikelyScaled(rawBalance)) {
    const asStr = typeof rawBalance === 'string' ? rawBalance : String(rawBalance);
    return asStr;
  }
  try {
    return ethers.formatUnits(rawBalance, decimals);
  } catch (_) {
    return String(rawBalance);
  }
}

async function main() {
  const argv = await yargs(hideBin(process.argv))
    .option('rpc', { type: 'string', describe: 'RPC URL', demandOption: true })
    .option('token', { type: 'string', describe: 'Token contract address', demandOption: true })
    .option('address', { type: 'string', describe: 'Holder address to query balance', demandOption: false })
    .option('scaled', { type: 'boolean', default: false, describe: 'Set true if the balance returned by your API is already human-scaled' })
    .strict()
    .help()
    .argv;

  const provider = new ethers.JsonRpcProvider(argv.rpc);
  const token = new ethers.Contract(argv.token, ERC20_MIN_ABI, provider);

  const meta = await readMetadata(provider, argv.token, token);

  let balanceFormatted = null;
  let balanceRaw = null;
  if (argv.address) {
    try {
      balanceRaw = await token.balanceOf(argv.address);
      balanceFormatted = formatBalance(balanceRaw, meta.decimals, argv.scaled);
    } catch (e) {
      balanceFormatted = null;
    }
  }

  const result = {
    address: argv.token,
    name: meta.name,
    symbol: meta.symbol,
    decimals: meta.decimals,
    balance: balanceFormatted,
    balanceRaw: balanceRaw?.toString?.() ?? null,
  };

  console.log(JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});