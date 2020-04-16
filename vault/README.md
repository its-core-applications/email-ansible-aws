HashiCorp Vault management with Ansible is barely a thing, and I don't have time
to write proper modules in order to make it a thing, so our Vault config is
managed by hand.

Secrets backend setup:
```
vault secrets enable -path=secrets -version=1 kv
vault secrets enable -path=ssh-host-signer ssh
vault secrets enable -path=ssh-client-signer ssh
vault write ssh-host-signer/config/ca generate_signing_key=true
vault write ssh-client-signer/config/ca generate_signing_key=true
```

auth/policy setup:
```
vault auth enable ldap
vault write auth/ldap/config \
    url='ldaps://ldap.umich.edu' \
    userdn='ou=People,dc=umich,dc=edu' \
    userattr='cn' \
    groupdn='ou=User Groups,ou=Groups,dc=umich,dc=edu' \
    groupfilter='(member={{.UserDN}})' \
    groupattr='cn'
vault policy write blackops @policy.blackops.hcl
vault write auth/ldap/groups/blackops policies=default,blackops
vault write sys/auth/ldap/tune listing_visibility='unauth'
```
