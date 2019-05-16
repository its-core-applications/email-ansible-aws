local google_from = 'From=/\\@[a-z\\.]+\\.google\\.com\\b/iH'
local umich_from = 'From=/\\@(umich\\.edu|.+\\.umich\\.edu)\\b/iH'
local suspicious_from = 'From=/[^=]umich\\.edu\\S*\\@/iH'
config['regexp']['UMICH_FROM_SUSPICIOUS_UMICH_EDU'] = {
    re = string.format('(%s) & !(%s) & !(%s)', suspicious_from, umich_from, google_from),
    score = 14,
    description = 'Non-UM From header contains umich.edu',
}

config['regexp']['UMICH_HAS_BITCOIN_ADDRESS'] = {
    re = '/\\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\\b/{mime}',
    score = 0.5,
    description = 'probably contains a Bitcoin address',
}

config['regexp']['UMICH_PORN_EXTORTION'] = {
    re = '/\\b(?:porn(?:ography|ographic)?|adult (?:web ?)?site)\\b/i{mime} && /\\b(?:friend|family|colleague|worker|peer|contact)s?\\b/i{mime} && /\\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\\b/{mime}',
    score = 8,
    description = 'attempt to extort money through shame',
}
