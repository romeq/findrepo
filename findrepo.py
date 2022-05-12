#!/usr/bin/env python3
import requests
import getopt
import sys


def usage():
    print(f"usage: {sys.argv[0]} <search term> [-n count] [-v] [-d] [-t 0|1]")
    print("  -n int: number of results")
    print("  -t int: search type (0: repositories | 1: users)")
    print("  -v: show additional data")
    print("  -d: disable colors")
    print("  -c: show only clone url")
    print("    -s: show only ssh clone link")


def print_err(error):
    print(f"error: {error}", file=sys.stderr)


def print_data(items, find_type, flag_verbose, colors):
    if find_type == "repositories":
        for repo in items:
            reponame = repo["full_name"]
            if not flag_verbose: 
                if colors:
                    print(f"\033[33m{reponame}\033[0m")
                else:
                    print(reponame)
            else: 
                repourl = repo["html_url"]
                repo_desc = repo["description"]
                if colors:
                    print(f"\033[33m{reponame}\033[0m - \033[35m{repo_desc}\033[0m ({repourl})")
                else:
                    print(f"{reponame}: {repourl} - {repo_desc}")

    elif find_type == "users":
        for user in items:
            username = user["login"]
            if not flag_verbose: 
                if colors:
                    print(f"\033[33m{username}\033[0m")
                else:
                    print(username)
            else: 
                repourl = user["html_url"]
                if colors:
                    print(f"\033[33m{username}\033[0m - {repourl}")
                else:
                    print(f"{username} - {repourl}")


def main() -> int:
    count = 1
    search = None
    flag_verbose = False
    flag_disable_colors = False
    flag_clone_url = False
    flag_ssh_clone_link = False
    find_type = "repositories"
    args_len = len(sys.argv)

    # parse arguments
    if args_len > 1:
        search = sys.argv[1]
        if search[0] == "-":
            usage()
            return 2

        if args_len > 2:
            try:
                opts, _ = getopt.getopt(sys.argv[2:], "csvdn:t:")
            except getopt.GetoptError as e:
                print_err(e)
                usage()
                return 2
            for arg, arg_val in opts:
                if arg == "-n":
                    try:
                        count = int(arg_val)
                    except ValueError:
                        print("error (args [-n]): value is not a number")
                        return 1
                elif arg == "-t":
                    try:
                        intarg = int(arg_val)
                    except ValueError:
                        print("error (args [-t]): value is not a number")
                        return 1

                    if intarg not in [0,1]:
                        print("error (args [-t]): allowed values are: 0,1")
                        return 1
                    find_type = "users" if intarg == 1 else "repositories"
                elif arg == "-c":
                    flag_clone_url = True
                elif arg == "-s":
                    flag_ssh_clone_link = True
                elif arg == "-v":
                    flag_verbose = True
                elif arg == "-d":
                    flag_disable_colors = True
    else:
        print_err("Not enough arguments")
        usage()
        return 2

    colors = not flag_disable_colors

    if flag_clone_url and flag_ssh_clone_link:
        print_err("-c and -s flags cannot be used at the same time.")
        return 1
    elif (flag_clone_url or flag_ssh_clone_link) and find_type != "repositories":
        print_err("-c and -s flags require that search type is set to \"repositories\".")
        return 1

    # declare variables
    base_url = f"https://api.github.com/search/{find_type}"
    request_url = f"{base_url}?q={search}&per_page={count}"

    # make request to github
    req = requests.get(request_url)
    if req.status_code != 200:
        msg = req.json()["message"]
        status = req.status_code
        print(f"Request failed: {msg} ({status}).")
        return 1

    request_json = req.json()
    if request_json["total_count"] == 0:
        print("No results found")
        return 1

    items = request_json["items"]
    if flag_clone_url or flag_ssh_clone_link:
        for repo in items:
            print(repo["clone_url"] if flag_clone_url else repo["ssh_url"])
    else:
        print_data(items, find_type, flag_verbose, colors)

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

