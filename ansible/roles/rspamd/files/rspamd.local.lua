config['regexp']['UMICH_HAS_BITCOIN_ADDRESS'] = {
    re = '/\\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\\b/{mime}',
    score = 0.5,
    description = 'probably contains a Bitcoin address',
}

config['regexp']['UMICH_PORN_EXTORTION'] = {
    re = '/\\b(?:porn(?:ography|ographic)?|adult (?:web ?)?site)\\b/i{mime} && /\\b(?:friend|family|colleague|worker|peer|contact)s?\\b/i{mime} && /\\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\\b/{mime}',
    score = 0.5,
    description = 'attempt to extort money through shame',
}
