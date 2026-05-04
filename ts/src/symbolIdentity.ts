import type { SymbolAliasRule } from './contracts';

export const SYMBOL_ALIAS_RULESET_VERSION = 'symbol-alias-v1';

export const SYMBOL_ALIAS_RULES = [
  {
    provider: 'massive',
    domain: 'market',
    providerSymbol: 'I:VIX',
    canonicalSymbol: '^VIX',
  },
  {
    provider: 'massive',
    domain: 'market',
    providerSymbol: 'I:VIX3M',
    canonicalSymbol: '^VIX3M',
  },
] as const satisfies readonly SymbolAliasRule[];

