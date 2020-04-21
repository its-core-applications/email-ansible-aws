path "ssh-host-signer/*" {
  capabilities = ["list"]
}

path "ssh-host-signer/sign/host" {
  capabilities = ["read", "update", "list"]
}
