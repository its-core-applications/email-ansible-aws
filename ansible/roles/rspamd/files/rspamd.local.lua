local google_from = 'From=/\\@[a-z\\.]+\\.google\\.com\\b/iH'
local umich_from = 'From=/\\@(umich\\.edu|.+\\.umich\\.edu|umdearborn\\.edu|.+\\.umdearborn\\.edu|umflint\\.edu|.+\\.umflint\\.edu)\\b/iH'
local suspicious_from = 'From=/[^=]umich\\.edu\\S*\\@/iH'
local umich_replyto = 'reply-to=/\\@(umich\\.edu|.+\\.umich\\.edu|umdearborn\\.edu|.+\\.umdearborn\\.edu|umflint\\.edu|.+\\.umflint\\.edu)\\b/iH'
local suspicious_replyto = 'reply-to=/[^=]umich\\.edu\\S*\\@/iH'
config['regexp']['UMICH_FROM_SUSPICIOUS_UMICH_EDU'] = {
    re = string.format('(%s) & !(%s) & !(%s)', suspicious_from, umich_from, google_from),
    score = 12,
    description = 'Non-UM From header contains umich.edu',
}

config['regexp']['UMICH_REPLYTO_SUSPICIOUS_UMICH_EDU'] = {
    re = string.format('(%s) & !(%s)', suspicious_replyto, umich_replyto),
    score = 0.1,
    description = 'Non-UM reply-to header contains umich.edu',
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

config['regexp']['UMICH_AKIRA_URL'] = {
    re = '/akiralkzxzq2dsrzsrvbr2xgbbu2wgsmxryd4csgfameg52n7efvr2id/{mime}',
    score = 0,
    description = 'malware URL',
}

config['regexp']['UMICH_AKIRA_TOKEN'] = {
    re = '/3246-ZF-JXAN-YQCP/{mime}',
    score = 0,
    description = 'malware token',
}
