#!/usr/bin/env python

# This file is distributed under the terms of the MIT license.
# Copyright (c) 2015-2018 Daniel Roesler
# Copyright (c) 2018 Regents of The University of Michigan

import argparse
import base64
import binascii
import copy
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import textwrap
import time

try:
    from urllib.request import urlopen, Request # Python 3
except ImportError:
    from urllib2 import urlopen, Request # Python 2

import boto3

#DEFAULT_DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"
DEFAULT_DIRECTORY_URL = "https://acme-staging-v02.api.letsencrypt.org/directory"

def get_crt(account_key, csr, log, directory_url):
    directory = None
    acct_headers = None
    alg = None
    jwk = None

    # helper functions - base64 encode for jose spec
    def _b64(b):
        return base64.urlsafe_b64encode(b).decode('utf8').replace("=", "")

    # helper function - run external commands
    def _cmd(cmd_list, stdin=None, cmd_input=None, err_msg="Command Line Error"):
        proc = subprocess.Popen(cmd_list, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate(cmd_input)
        if proc.returncode != 0:
            raise IOError("{0}\n{1}".format(err_msg, err))
        return out

    # helper function - make request and automatically parse json response
    def _do_request(url, data=None, err_msg="Error", depth=0):
        try:
            resp = urlopen(Request(url, data=data, headers={"Content-Type": "application/jose+json", "User-Agent": "acme-tiny"}))
            resp_data, code, headers = resp.read().decode("utf8"), resp.getcode(), resp.headers
            resp_data = json.loads(resp_data) # try to parse json results
        except ValueError:
            pass # ignore json parsing errors
        except IOError as e:
            resp_data = e.read().decode("utf8") if hasattr(e, "read") else str(e)
            code, headers = getattr(e, "code", None), {}
        if depth < 100 and code == 400 and json.loads(resp_data)['type'] == "urn:ietf:params:acme:error:badNonce":
            raise IndexError(resp_data) # allow 100 retrys for bad nonces
        if code not in [200, 201, 204]:
            raise ValueError("{0}:\nUrl: {1}\nData: {2}\nResponse Code: {3}\nResponse: {4}".format(err_msg, url, data, code, resp_data))
        return resp_data, code, headers

    # helper function - make signed requests
    def _send_signed_request(url, payload, err_msg, depth=0):
        payload64 = _b64(json.dumps(payload).encode('utf8'))
        new_nonce = _do_request(directory['newNonce'])[2]['Replay-Nonce']
        protected = {"url": url, "alg": alg, "nonce": new_nonce}
        protected.update({"jwk": jwk} if acct_headers is None else {"kid": acct_headers['Location']})
        protected64 = _b64(json.dumps(protected).encode('utf8'))
        protected_input = "{0}.{1}".format(protected64, payload64).encode('utf8')
        out = _cmd(["openssl", "dgst", "-sha256", "-sign", account_key], stdin=subprocess.PIPE, cmd_input=protected_input, err_msg="OpenSSL Error")
        data = json.dumps({"protected": protected64, "payload": payload64, "signature": _b64(out)})
        try:
            return _do_request(url, data=data.encode('utf8'), err_msg=err_msg, depth=depth)
        except IndexError: # retry bad nonces (they raise IndexError)
            return _send_signed_request(url, payload, err_msg, depth=(depth + 1))

    # helper function - poll until complete
    def _poll_until_not(url, pending_statuses, err_msg):
        while True:
            result, code, headers = _do_request(url, err_msg=err_msg)
            if result['status'] in pending_statuses:
                time.sleep(2)
                continue
            return result

    # parse account key to get public key
    log.info("Parsing account key...")
    out = _cmd(["openssl", "rsa", "-in", account_key, "-noout", "-text"], err_msg="OpenSSL Error")
    pub_pattern = r"modulus:\n\s+00:([a-f0-9\:\s]+?)\npublicExponent: ([0-9]+)"
    pub_hex, pub_exp = re.search(pub_pattern, out.decode('utf8'), re.MULTILINE|re.DOTALL).groups()
    pub_exp = "{0:x}".format(int(pub_exp))
    pub_exp = "0{0}".format(pub_exp) if len(pub_exp) % 2 else pub_exp
    alg = "RS256"
    jwk = {
        "e": _b64(binascii.unhexlify(pub_exp.encode("utf-8"))),
        "kty": "RSA",
        "n": _b64(binascii.unhexlify(re.sub(r"(\s|:)", "", pub_hex).encode("utf-8"))),
    }
    accountkey_json = json.dumps(jwk, sort_keys=True, separators=(',', ':'))
    thumbprint = _b64(hashlib.sha256(accountkey_json.encode('utf8')).digest())

    # find domains
    log.info("Parsing CSR...")
    out = _cmd(["openssl", "req", "-in", csr, "-noout", "-text"], err_msg="Error loading {0}".format(csr))
    domains = set([])
    common_name = re.search(r"Subject:.*? CN\s?=\s?([^\s,;/]+)", out.decode('utf8'))
    if common_name is not None:
        domains.add(common_name.group(1))
    subject_alt_names = re.search(r"X509v3 Subject Alternative Name: \n +([^\n]+)\n", out.decode('utf8'), re.MULTILINE|re.DOTALL)
    if subject_alt_names is not None:
        for san in subject_alt_names.group(1).split(", "):
            if san.startswith("DNS:"):
                domains.add(san[4:])
    log.info("Found domains: {0}".format(", ".join(domains)))

    # get the ACME directory of urls
    log.info("Getting directory...")
    directory, code, headers = _do_request(directory_url, err_msg="Error getting directory")
    log.info("Directory found!")

    log.info("Registering account...")
    reg_payload = {"termsOfServiceAgreed": True}
    account, code, acct_headers = _send_signed_request(directory['newAccount'], reg_payload, "Error registering")
    log.info("Registered!" if code == 201 else "Already registered!")

    # create a new order
    log.info("Creating new order...")
    order_payload = {"identifiers": [{"type": "dns", "value": d} for d in domains]}
    order, code, order_headers = _send_signed_request(directory['newOrder'], order_payload, "Error creating new order")
    log.info("Order created!")

    # get the authorizations that need to be completed
    challenges = []
    for auth_url in order['authorizations']:
        authorization, code, headers = _do_request(auth_url, err_msg="Error getting challenges")
        domain = authorization['identifier']['value']
        log.info("Verifying {0}...".format(domain))

        if [c for c in authorization['challenges'] if c['status'] == 'valid']:
            continue

        challenge = [c for c in authorization['challenges'] if c['type'] == 'dns-01'][0]

        boto3.setup_default_session(profile_name='acme')
        client = boto3.client('route53')
        zones = client.list_hosted_zones_by_name()
        zoneid = None
        for zone in zones['HostedZones']:
            if (domain.endswith(zone['Name'][:-1])):
                zoneid = zone['Id']

        if zoneid == None:
            raise ValueError("Unable to find a matching zone for {0}".format(domain))
        token = re.sub(r"[^A-Za-z0-9_\-]", '_', challenge['token'])
        keyauthorization = "{0}.{1}".format(token, thumbprint)
        token = '"{0}"'.format(_b64(hashlib.sha256(keyauthorization.encode('utf8')).digest()))

        change = client.change_resource_record_sets(
            HostedZoneId = zoneid,
            ChangeBatch = {
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': '_acme-challenge.{0}'.format(domain),
                        'Type': 'TXT',
                        'TTL': 300,
                        'ResourceRecords': [{ 'Value': token }],
                    }
                }]
            }
        )

        challenges.append({
            'url': challenge['url'],
            'change': change['ChangeInfo']['Id'],
            'domain': domain,
        })

    for challenge in challenges:
        log.info('Waiting for Route53 for {0}...'.format(challenge['domain']))
        while (client.get_change(Id=challenge['change']))['ChangeInfo']['Status'] == 'PENDING':
            time.sleep(1)
        _send_signed_request(challenge['url'], {}, "Error submitting challenges: {0}".format(domain))

    for challenge in challenges:
        authorization = _poll_until_not(auth_url, ["pending"], "Error checking challenge status for {0}".format(challenge['domain']))
        if authorization['status'] != "valid":
            raise ValueError("Challenge did not pass for {0}: {1}".format(challenge['domain'], authorization))
        log.info("{0} verified!".format(challenge['domain']))

    # finalize the order with the csr
    log.info("Signing certificate...")
    csr_der = _cmd(["openssl", "req", "-in", csr, "-outform", "DER"], err_msg="DER Export Error")
    _send_signed_request(order['finalize'], {"csr": _b64(csr_der)}, "Error finalizing order")

    # poll the order to monitor when it's done
    order = _poll_until_not(order_headers['Location'], ["pending", "processing"], "Error checking order status")
    if order['status'] != "valid":
        raise ValueError("Order failed: {0}".format(order))

    # download the certificate
    certificate_pem, code, headers = _do_request(order['certificate'], err_msg="Certificate download failed")
    log.info("Certificate signed!")
    return certificate_pem

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--account-key", required=True, help="path to your Let's Encrypt account private key")
    parser.add_argument("--csr", required=True, help="path to your certificate signing request")
    parser.add_argument("--quiet", action="store_const", const=logging.ERROR, help="suppress output except for errors")
    parser.add_argument("--directory-url", default=DEFAULT_DIRECTORY_URL, help="ACME directory URL")

    args = parser.parse_args(argv)

    log = logging.getLogger(__name__)
    log.addHandler(logging.StreamHandler())
    log.setLevel(args.quiet or logging.INFO)

    signed_crt = get_crt(args.account_key, args.csr, log, args.directory_url)
    sys.stdout.write(signed_crt)

if __name__ == "__main__": # pragma: no cover
    main(sys.argv[1:])
