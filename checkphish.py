#!/usr/bin/env python3
# 7/20/22 GitStoph
# Script to quickly grab and print results from CheckPhish.ai
#############################################################\

from rich.console import Console
from rich.table import Table
import keyring
import json
import requests
from time import sleep
import argparse
from PIL import Image

console = Console()
cpapikey = keyring.get_password("checkphish", "apikey")

def get_args(): # creating our args to parse later.
    parser = argparse.ArgumentParser(
        description='Arguments for submitting URLs to Checkphish.ai. Note that if you choose to download/view an image, it is on you to delete it later!')
    parser.add_argument('-u', '--url',required=True,type=str,default='None',action='store',
        help="What URL should be investigated.")
    parser.add_argument('-v', '--verbose',required=False,type=bool, default=argparse.SUPPRESS,nargs='?', help="Pass this arg to see verbose output while running.")
    parser.add_argument('-i', '--image',required=False,type=bool, default=argparse.SUPPRESS,nargs='?', help="Pass this arg to download and view a screenshot of the URL that was submitted.")
    args = parser.parse_args()
    return args


def makesafe(url): # makes dangerous URLs unclickable.
    url = url.replace('http', 'hxxp', 1)
    return url.replace('.', '[.]')


def download_screenshot(threaturl, screenshoturl): # downloads the screenshot from the passed URL, and opens it.
    filename = threaturl[:30].replace('/', '').replace(':', '')
    with open(f'{filename}.png', 'wb') as handler:
        handler.write(requests.get(screenshoturl).content)
    Image.open(f'{filename}.png').show()


def __isjson(myjson): #checks that myjson is json loadable. If not, returns false.
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True


def __returnhandler(statuscode, returntext, objtype, suppressprint):
    """Checks if returntext is json. If it is, it json.loads it into a dict. If 'errors' is in the
    dict's keys, it returns the error, otherwise flips noerr to True. Depending on the statuscode
    that's returned from requests/dnsfilter api, a different print message/return is done per situation.
    """
    validreturn = __isjson(returntext)
    noerr = False
    errmesg = ''
    if validreturn:
        returntext = json.loads(returntext)
        try:
            errmesg = returntext['errors']
        except KeyError:
            noerr = True
        except TypeError:
            noerr = True
    if str(statuscode) == '200' and validreturn:
        if suppressprint is False:
            console.log('[green]{0} Operation Successful - See returned data for results.'.format(str(objtype)))
        return returntext
    elif str(statuscode) == '200':
        if suppressprint is False:
            console.log('[green]{0} Operation Successful.'.format(str(objtype)))
        return None
    elif str(statuscode) == '201' and validreturn:
        if suppressprint is False:
            console.log('[green]{0} Added Successfully - See returned data for results.'.format(str(objtype)))
        return returntext
    elif str(statuscode) == '201':
        if suppressprint is False:
            console.log('[green]{0} Added Successfully.'.format(str(objtype)))
        return None
    elif str(statuscode) == '204' and validreturn:
        if suppressprint is False:
            console.log('[green]{0} Deleted Successfully - See returned data for results.'.format(str(objtype)))
        return returntext
    elif str(statuscode) == '204':
        console.log('[green]{0} Deleted Successfully.'.format(str(objtype)))
        return None
    elif str(statuscode) == '400' and validreturn and noerr is False:
        if suppressprint is False:
            console.log('[red]Bad Request - See returned data for error details.')
        return errmesg
    elif str(statuscode) == '400' and validreturn and noerr:
        if suppressprint is False:
            console.log('[red]Bad Request - See returned data for details.')
        return returntext
    elif str(statuscode) == '400':
        if suppressprint is False:
            console.log('[red]Bad Request - No additional error data available.')
    elif str(statuscode) == '401' and validreturn and noerr is False:
        if suppressprint is False:
            console.log('[red]Unauthorized Access - See returned data for error details.')
        return errmesg
    elif str(statuscode) == '401' and validreturn:
        if suppressprint is False:
            console.log('[red]Unauthorized Access.')
        return returntext
    elif str(statuscode) == '404' and validreturn and noerr is False:
        if suppressprint is False:
            console.log('[red]Resource Not Found - See returned data for error details.')
        return errmesg
    elif str(statuscode) == '404' and validreturn:
        if suppressprint is False:
            console.log('[red]Resource Not Found.')
        return returntext
    elif str(statuscode) == '500':
        if suppressprint is False:
            console.log('[red]HTTP 500 - Server Error.')
        return returntext
    elif validreturn and noerr is False:
        if suppressprint is False:
            console.log('[red]HTTP Status Code: {0} - See returned data for error details.'.format(str(statuscode)))
        return errmesg
    else:
        console.log('[red]HTTP Status Code: {0} - No returned data.'.format(str(statuscode)))


def submit_url(url, suppressprint=False): # Actually submits the job to CheckPhish
    if suppressprint == False:
        console.log("[yellow]Submitting URL to the CheckPhish API..")
    calltype = 'URL Submission'
    geturl = 'https://developers.checkphish.ai/api/neo/scan'
    headers = {'Content-Type': 'application/json'}
    params = {'apiKey': cpapikey, 'urlInfo': {'url': url}}
    dashboard = requests.post(geturl, headers=headers, data=json.dumps(params))
    result = __returnhandler(dashboard.status_code, dashboard.text, calltype, suppressprint)
    return result


def get_our_results(jobid, suppressprint=False): # checks back every 3s to see if our results are ready and returns them.
    if suppressprint == False:
        console.log("[yellow]Checking status of the CheckPhish job we submitted..")
    calltype = 'Job retrieval'
    geturl = 'https://developers.checkphish.ai/api/neo/scan/status'
    headers = {'Content-Type': 'application/json'}
    params = {'apiKey': cpapikey, 'jobID': jobid, 'insights': True}
    dashboard = requests.post(geturl, headers=headers, data=json.dumps(params))
    result = __returnhandler(dashboard.status_code, dashboard.text, calltype, suppressprint)
    waittime = 0
    while result['status'] != 'DONE':
        waittime += 3
        sleep(3)
        if suppressprint == False:
            console.log(f"[yellow][I] Waiting [white]{str(waittime)}[yellow] seconds for our results..")
        dashboard = requests.post(geturl, headers=headers, data=json.dumps(params))
        result = __returnhandler(dashboard.status_code, dashboard.text, calltype, suppressprint)
    return result


def get_checkphish_result(url, suppressprint=False): # combining functions to one callable.
    urlsubmit = submit_url(url, suppressprint)
    checkphish = get_our_results(urlsubmit['jobID'], suppressprint)
    return checkphish


def create_result_table(cpresults): # Creates the pretty table to print results with.
    table = Table(title="[bold green]CheckPhish Results:", show_header=True, header_style="bold green")
    table.add_column("Key", justify="center")
    table.add_column("Result", justify="center")
    if cpresults['disposition'] == 'clean':
        table.add_row("disposition: ", f"[bold green]{cpresults['disposition']}")
    else:
        table.add_row("disposition: ", f"[bold red]{cpresults['disposition']}")
    table.add_row("url: ", makesafe(cpresults['url']))
    table.add_row("brand: ", cpresults['brand'])
    table.add_row("insights: ", cpresults['insights'])
    table.add_row("error: ", str(cpresults['error']))
    table.add_row("image_objects: ", str(cpresults['image_objects']))
    table.add_row("categories: ", str(cpresults['categories']))
    return table


def main():
    try:
        args = get_args()
        if 'verbose' in args:
            suppressprint = False
        else:
            suppressprint = True
        checkphish = get_checkphish_result(args.url, suppressprint)
        console.print(create_result_table(checkphish), style='green')
        if 'image' in args:
            console.log("[green]Downloading and opening screenshot from CheckPhish results..")
            download_screenshot(args.url, checkphish['screenshot_path'])
    except KeyboardInterrupt:
        console.log("[red][!!!] Ctrl + C Detected!")
        console.log("[red][XXX] Exiting script now..")
        exit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.log("\n[!!!] Ctrl + C Detected!")
        console.log("[XXX] Exiting script now..")
        exit()