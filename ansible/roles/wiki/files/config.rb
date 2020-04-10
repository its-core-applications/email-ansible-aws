Gollum::Wiki.default_committer_name = 'Gollum'
Gollum::Wiki.default_committer_email = 'blackops@umich.edu'

class Precious::App
    before do
        session['gollum.author'] = {
            :name       => env['HTTP_OIDC_CLAIM_NAME'],
            :email      => env['HTTP_OIDC_CLAIM_EMAIL'],
        }
    end
end
