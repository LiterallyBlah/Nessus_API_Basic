#!/usr/bin/python
import json
import argparse
import requests
import shutil
import time
import urllib3
from os import path


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NessusRequest(object):

    parser = argparse.ArgumentParser(description='Nessus API. Functionality: Start, Check Status, Download and List.\nFollowing Options:\n\tCreate Scan: python3 nessus.py -t google.com -n Google_Scan\n\tStop Scan: python3 nessus.py -x 219\n\tStatus Scan: python3 nessus.py -s 219\n\tList Scans: python3 nessus.py -l\n\tOutput Scan: python3 nessus.py -e nessus -o /home/scutter/Reports/blah.nessus', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--targets', '-t', help='Target list. This can be a file or directory.')
    parser.add_argument('--name', '-n', help='Name of scan.')
    parser.add_argument('--status', '-s', help='Current status of scan using ID.')
    parser.add_argument('--stop', '-x', help='Stops scan using ID.')
    parser.add_argument('--export', '-e', help='Export options: Nessus, HTML, PDF, CSV, or DB.')
    parser.add_argument('--output', '-o', help='Ouput path.')
    parser.add_argument('--list', '-l', help='List Scans with their IDs', action='store_true')

    args = parser.parse_args()


    HEADERS = {} # Empty Headers json element.

    def __init__(
        self,
        username="",
        password="",
        host="https://127.0.0.1:8834",
        verify=False,
        proxies=None,
        uuid="ad629e16-03b6-8c1d-cef6-ef8c9dd3c658d24bd260ef5f9e66",
        folder_id=None,
        policy_id="219",
    ):

        self.VERIFY = verify
        self.PROXIES = proxies

        self.HOST = host
        self.login(username, password, host)

        self.folder_id = folder_id
        self.policy_id = policy_id
        self.uuid = uuid

    def req(self, verb, uri, **kwargs):
        # Changes the func variable based on the verb input.
        if verb == "get":
            func = requests.get
        elif verb == "post":
            func = requests.post
        elif verb == "put":
            func = requests.put
        else:
            func = requests.get
        # calls func with hosts, heads, etc
        return func(
            self.HOST + uri,
            headers=self.HEADERS,
            verify=self.VERIFY,
            proxies=self.PROXIES,
            **kwargs
        )

    def login(self, username, password, host):
        try:
            # We need to get both the API key and the Session token

            res = self.req("get", "/nessus6.js")

            token_location = res.text.find('getApiToken",value:function(){return')

            self.HEADERS["X-API-TOKEN"] = res.text[
                token_location : token_location + 200  # noqa: E203
            ].split('"')[2]
            self.HEADERS["Content-Type"] = "application/json"
            data = '{"username":"%s","password":"%s"}' % (username, password)
            res = self.req("post", "/session", data=data)

            self.HEADERS["X-Cookie"] = "token=" + json.loads(res.text)["token"]

        except:
            return print('Unable to login.\n', res)

    def launch_job(self, targets=args.targets, name=args.name):
        try:
            data = {
                "uuid": self.uuid,
                "settings": {
                    "emails": "",
                    "filter_type": "and",
                    "filters": [],
                    "launch_now": True,
                    "enabled": False,
                    "file_targets": "",
                    "text_targets": targets,
                    "policy_id": self.policy_id,
                    "scanner_id": "1",
                    "folder_id": self.folder_id,
                    "description": "Launched by Blah's Script.",
                    "name": name,
                    },
                }
            # grabs the above data and sends to /scans. By this point the headers (token, api, cookie, etc) have already been established.
            res = json.loads(self.req("post", "/scans", data=json.dumps(data)).text)
            # Returns scan name and scan id from the response of the request above.
            return print('Scan ID: ', res['scan']['id'])
        except:
            return print('Unable to launch job.\n', res)

    def stop_job(self, scan_id=args.stop):
        try:
            res = self.req("post", "/scans/{}/stop".format(str(scan_id)))
            return print('Scan: Stopped')
        except:
            return print('Unable to stop job.', res)

    def get_status(self, job_id=args.status): ### EDIT THIS
        try:
            # requests the /scans/jobid and returns the info and status.
            res = json.loads(self.req("get", "/scans/{}".format(str(job_id))).text)
            return print('Status: ', res["info"]["status"])
        except:
            return print('Unable to retreive status.\n', res)

    def list_scans(self):
        try:
            res = json.loads(self.req("get", "/scans").text)

            items = {}
            for item in res['scans']:
                items[item['name']] = item['id']

            for key, value in items.items():
                print('Scan:', key, ' : ', value, '\n')
        except:
            return print('Unable to retreive list.\n', res)

    def export_file(self, job_id=args.status, output_format=args.export, output_path=args.output): ### EDIT THIS
        try:
            data = json.dumps({"format": output_format}) ### MAKE THIS AN OPTION CSV OR NESSUS

            res = json.loads(
                self.req("post", "/scans/{}/export".format(job_id), data=data).text
            )
            # print('DEBUG1:',res)

            status = True
            while status:
                status = False
                if 'token' in res:
                    token = res['token']
                    print("Download ready.")
                    break
                if 'Invalid' in res['error'] or 'no found' in res['error']:
                    return print('Invalid Format and/or file.')

                status = True
                print('Download not ready.')
                time.sleep(5)

            # Download file.

            res = self.req("get", "/tokens/{}/download".format(token), stream=True)
            res.raw.decode_content = True
            with open(output_path, "wb") as f:
                shutil.copyfileobj(res.raw, f)
        except:
            return print('Unable to download file.\n', res)


nessus = NessusRequest()

if nessus.args.export and nessus.args.output and nessus.args.status:
    nessus.export_file()
elif nessus.args.targets and nessus.args.name:
    nessus.launch_job()
elif nessus.args.list:
    nessus.list_scans()
elif nessus.args.stop:
    nessus.stop_job()
elif nessus.args.status:
    nessus.get_status()
else:
    print('Unknown option or combination of options.\nTry -h or --help for options.')
