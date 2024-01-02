import sys
import colorama
import time
import argparse
import json
import httpx
import hmac
import hashlib
import urllib
import requests
from httpx import get
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style, init

colorama.init(autoreset=True)


def banner():
    print("                _ _   _                ")
    print("  _  _ ___ ___ (_) |_( )___  _ __  ___ ")
    print(" | || / -_|_-< | |  _|/(_-< | '  \/ -_)")
    print("  \_, \___/__/ |_|\__| /__/ |_|_|_\___|")
    print("  |__/                                 ")
    print("\n\tTwitter: " + Fore.MAGENTA + "@blackeko5")


def getUserId(username, sessionsId):
    cookies = {'sessionid': sessionsId}
    headers = {'User-Agent': 'Instagram 64.0.0.14.96', }
    r = get('https://www.instagram.com/{}/?__a=1'.format(username),
            headers=headers, cookies=cookies)
    try:
        info = json.loads(r.text)
        id = info["logging_page_id"].strip("profilePage_")
        return({"id": id, "error": None})
    except:
        return({"id": None, "error": "User not found or rate limit"})


def getInfo(username, sessionId):
    userId = getUserId(username, sessionId)
    if userId["error"] is not None:
        return({"user": None, "error": "User not found or rate limit"})
    else:
        cookies = {'sessionid': sessionId}
        headers = {'User-Agent': 'Instagram 64.0.0.14.96', }
        response = get('https://i.instagram.com/api/v1/users/' +
                       userId["id"]+'/info/', headers=headers, cookies=cookies)
        info = json.loads(response.text)
        infoUser = info["user"]
        infoUser["userID"] = userId["id"]
        return({"user": infoUser, "error": None})


def get_user_posts(username, session_id):
    user_id = getUserId(username, session_id)

    if user_id["error"] is not None:
        return {"posts": None, "error": user_id["error"]}
    else:
        cookies = {'sessionid': session_id}
        headers = {'User-Agent': 'Instagram 64.0.0.14.96'}
        response = get(f'https://i.instagram.com/api/v1/users/{user_id["id"]}/media/recent/', headers=headers, cookies=cookies)
        
        try:
            posts_info = json.loads(response.text)
            return {"posts": posts_info.get("items", []), "error": None}
        except Exception as e:
            return {"posts": None, "error": str(e)}


def dumpor(name):
    url = "https://dumpor.com/search?query="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    req = url + name.replace(" ", "+")

    try:
        account_list = []
        response = requests.get(req, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        accounts = soup.findAll('a', {"class": "profile-name-link"})
        for account in accounts:
            account_list.append(account.text)
        return {"user": account_list, "error": None}
    except:
        return {"user": None, "error": "rate limit"}


def print_user_info(infos):
    if infos["user"] is not None:
        print("\nInformation about      : " + infos["user"]["username"])
        print("Full Name              : " + infos["user"]["full_name"])
        print("User ID                : " + infos["user"]["userID"])
        print("Verified               : " + str(infos['user']['is_verified']))
        print("Is business Account    : " + str(infos["user"]["is_business"]))
        print("Is private Account     : " + str(infos["user"]["is_private"]))
        print("Followers              : " + str(infos["user"]["follower_count"]))
        print("Following              : " + str(infos["user"]["following_count"]))
        print("Number of posts        : " + str(infos["user"]["media_count"]))
        print("External URL           : " + infos["user"]["external_url"])
        print("Biography              : " + infos["user"]["biography"])
        print("Profile Picture        : " + infos["user"]["hd_profile_pic_url_info"]["url"])
        print("-" * 30)
    else:
        print(infos["error"])


def print_user_posts(posts_result):
    if posts_result["error"] is not None:
        print(posts_result["error"])
    else:
        posts = posts_result["posts"]
        if posts:
            print("\nRecent Posts:")
            for post in posts:
                print(f"- Post ID: {post.get('id')}, Caption: {post.get('caption', {}).get('text', 'N/A')}")
        else:
            print("No posts found.")


def main():
    banner()
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('required arguments')
    parser.add_argument('-s', '--sessionid',
                        help="Instagram session ID", required=True)
    parser.add_argument(
        '-n', '--name', help="Target name & surname", required=True)
    parser.add_argument('-e', '--email', help="Target email", required=True)
    parser.add_argument(
        '-p', '--phone', help="Target phone number", required=True)
    parser.add_argument('-t', '--timeout',
                        help="Timeout between requests", required=False)

    args = parser.parse_args()

    sessionsId = args.sessionid
    name = args.name
    email = args.email
    phone = args.phone
    timeout = args.timeout

    accounts = dumpor(name)

    if accounts["user"] is None:
        print(accounts["error"])
    else:
        for account in accounts["user"]:
            name_f, email_f, phone_f = 0, 0, 0
            infos = getInfo(account[1:], sessionsId)
            print_user_info(infos)

            posts_result = get_user_posts(account[1:], sessionsId)
            print_user_posts(posts_result)

            if(name_f + email_f + phone_f == 3):
                print(Fore.CYAN + "[*] " + Fore.GREEN + "Profile ID " +
                      infos["user"]["userID"] + " match level: HIGH\n")
                usr_choice = input("Stop searching? Y/n ")
                if(usr_choice.lower() == 'y'):
                    sys.exit(0)
                else:
                    pass
            elif(name_f + email_f + phone_f == 2):
                print(Fore.CYAN + "[*] " + Fore.YELLOW + "Profile ID " +
                      infos["user"]["userID"] + " match level: MEDIUM\n")
            elif(name_f + email_f + phone_f == 1):
                print(Fore.CYAN + "[*] " + Fore.RED + "Profile with ID " +
                      infos["user"]["userID"] + " match level: LOW\n")

            print("-" * 30)

            if(timeout):
                time.sleep(int(timeout))


if __name__ == "__main__":
    main()
