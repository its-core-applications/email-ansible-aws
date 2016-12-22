#!/bin/bash

rhelbase=$(aws ec2 describe-images --filters "Name=owner-id,Values=309956199498" "Name=virtualization-type,Values=hvm" "Name=block-device-mapping.volume-type,Values=gp2" "Name=name,Values=RHEL-7.2_HVM_GA*" --query 'Images[*].{Name:Name,ImageId:ImageId}' --output=text | sort -k2 | awk 'END { print $1 }')
packer build -var "base_ami=$rhelbase" packer/template.json
[[ $? -eq 0 ]] || exit 1
