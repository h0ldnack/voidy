#! /usr/bin/env nix-shell
#! nix-shell -i python -p python310 python310Packages.rich python310Packages.httpx python310Packages.prompt_toolkit
import httpx
import sys
import typing as T
from rich import print
from rich.pretty import pprint
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from urllib.parse import quote
import json
import platform
import subprocess
from rich.console import Console
from rich.text import Text
import random
import shutil

def ppprint(msgz: list):
    colors = ["green", "yellow", "blue", "magenta", "cyan", "white", "bright_black", "bright_red", "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan", "bright_white"]
    def p1(t: tuple, count: int):
        c = random.choice(colors)
        console = Console()
        name = Text(str(count) + ". " + t[0] + ":")
        name.stylize(c)
        console.print(name)
        desc = Text(t[1])
        console.print(desc)

    count = 1
    for m in msgz:
        p1(m, count)
        count = count + 1

def get_platform():
    void_archs = ["x86_64", "aarch64", "armv6l", "armv7l", "x86_64-musl", "aarch64-musl", "armv6l-musl", "armv7l-musl", "i686"]
    arch = platform.processor()
    if arch in void_archs:
        return arch
    else:
        return "x86_64"

def main(query_string: str, architecture: str):
    q = quote(query_string.encode('utf8'))
    params = {"q": q}
    base_url = "https://xq-api.voidlinux.org/v1/query/"
    url = base_url + architecture
    with httpx.Client() as client:
        try:
            res = client.get(url, params=params)
            j = res.json()["data"]
        except Exception as e:
            raise Exception("Remote data not returned")
            
        if len(j) == 0:
            return False
        else:
            data = list(map(lambda x: (x["name"], x["short_desc"]), j))
            names = list(map(lambda x: x[0], data))
            names_comp = WordCompleter(names)
            if len(names) >= 15:
                ppprint(data[0:15])
                print("[red]Programs rounded at 15: All options are still selectable[/red]")
            else:
                ppprint(data)
            name = prompt("Choose which program you want, or anything else if you dont want to install the app: ", completer=names_comp)
            # Check if user-supplied name is valid
            if name in names:
                cmd = ["sudo xbps-install --yes " + name]
                res = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)  # type: ignore
                if res.returncode == 0:  # type: ignore
                    print("Installed", name)
                else:
                    print(res.returncode, "code returned, when attempting to install", name)  # type: ignore
                
            else:
                print("No app was installed")
                return False

        
if __name__ == "__main__":
    try:
        main(sys.argv[1], get_platform())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(e, "Error occured")
