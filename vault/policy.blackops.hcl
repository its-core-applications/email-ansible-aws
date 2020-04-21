path "identity/*" {
  capabilities = ["read", "list"]
}

path "identity" {
  capabilities = ["list"]
}

path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret" {
  capabilities = ["list"]
}

path "ssh-client-signer/*" {
  capabilities = ["list"]
}

path "ssh-client-signer/sign/ec2-user" {
  capabilities = ["read", "update", "list"]
}

path "ssh-client-signer/sign/personal" {
  capabilities = ["read", "update", "list"]
}

path "ssh-client-signer" {
  capabilities = ["list"]
}

path "sys/*" {
  capabilities = ["read", "list"]
}

path "sys/capabilities-self" {
  capabilities = ["read", "list", "update"]
}

path "sys" {
  capabilities = ["list"]
}
