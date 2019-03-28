#!/bin/bash

admin_account=admin-mgoogle
purge_date=$(date --iso-8601 --date="10 days ago")
pass_folder_id=$(gam user $admin_account show filelist query "title='Shared Account Passwords'" id | awk -F, 'NR > 1 { print $2 }')

if [[ -n "$pass_folder_id" ]]; then
    gam user $admin_account show filelist id query "modifiedDate < '$purge_date' and '$pass_folder_id' in parents" | awk -F, 'NR > 1 { print $2 }' | xargs -I % gam user $admin_account delete drivefile % purge
fi
