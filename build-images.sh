#!/bin/bash

rhelbase=$(aws ec2 describe-images --filters "Name=owner-id,Values=309956199498" "Name=virtualization-type,Values=hvm" "Name=block-device-mapping.volume-type,Values=gp2" "Name=name,Values=RHEL-7.2_HVM_GA*" --query 'Images[*].{Name:Name,ImageId:ImageId}' --output=text | sort -n -k2 | awk 'END { print $1 }')
packer -machine-readable build -var "base_ami=$rhelbase" packer/template.json
[[ $? -eq 0 ]] || exit 1

base=$(aws ec2 describe-images --owners self --filters "Name=tag:image_type,Values=base" --query 'Images[*].{Name:Name,ImageId:ImageId}' --output=text | sort -n -k2 | awk 'END { print $1 }')
for class in mx relay smtp ; do
    packer -machine-readable build -var "image_type=$class" -var "base_ami=$base" packer/template.json &
done

wait
