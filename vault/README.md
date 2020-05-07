HashiCorp Vault management with Ansible is barely a thing, and I don't have time
to write proper modules in order to make it a thing, so our Vault config is
managed by hand.

# Secrets backends

```
vault secrets enable -path=secrets -version=1 kv
vault secrets enable -path=ssh-host-signer ssh
vault secrets enable -path=ssh-client-signer ssh
vault write ssh-host-signer/config/ca generate_signing_key=true
vault write ssh-client-signer/config/ca generate_signing_key=true
```

You probably shouldn't run the `generate_signing_key` steps.


# Auth and policy

```
vault auth enable ldap
vault write auth/ldap/config \
    url='ldaps://ldap.umich.edu' \
    userdn='ou=People,dc=umich,dc=edu' \
    userattr='cn' \
    groupdn='ou=User Groups,ou=Groups,dc=umich,dc=edu' \
    groupfilter='(member={{.UserDN}})' \
    groupattr='cn'
vault policy write blackops policy.blackops.hcl
vault write auth/ldap/groups/blackops policies=default,blackops
vault write sys/auth/ldap/tune listing_visibility='unauth'
```

```
vault auth enable aws
vault write auth/aws/role/umcollab_master @aws.master.json
vault write auth/aws/role/umcollab_standard @aws.standard.json
vault policy write ec2 policy.ec2.hcl
```

```
vault auth enable approle
vault policy write s3_datastore policy.s3_datastore.hcl
vault write auth/approle/role/dnsbl @approle.dnsbl.json
```

# SSH signing

```
vault write ssh-host-signer/roles/host @ssh.host.json
vault write ssh-client-signer/roles/ec2-user @ssh.ec2-user.json
vault write ssh-client-signer/roles/personal @ssh.personal.json
```

The `personal` role uses a hardcoded mount accessor which you probably
need to update if you're building a Vault instance from scratch.

# AWS credentials

```
vault secrets enable aws
vault write aws/roles/s3_datastore credential_type=assumed_role role_arns=arn:aws:iam::440653842962:role/umcollab_440653842962_S3_ds
```
