#!/bin/bash

if [[ $1 ]]; then
    class=$1
else
    class=mx
fi

base=$(aws ec2 describe-images --owners self --filters "Name=tag:image_type,Values=base" --query 'Images[*].{Name:Name,ImageId:ImageId}' --output=text | sort -n -k2 | awk 'END { print $1 }')
packer -machine-readable build -var "image_type=$class" -var "base_ami=$base" packer/template.json
