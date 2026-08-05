#!/usr/bin/env python3
import os
import shlex
import subprocess
import sys

REMOTE_PATH = "/workspace/Wan2GP/outputs/"
LOCAL_PATH = "/tmp/outputs/"
IDENTITY = os.path.expanduser("~/.ssh/runpod_id_ed25519")


def parse_ssh(ssh_cmd: str):
    tokens = shlex.split(ssh_cmd)

    if not tokens or tokens[0] != "ssh":
        raise ValueError("Command must start with 'ssh'")

    user = None
    host = None
    port = 22

    i = 1
    while i < len(tokens):
        t = tokens[i]

        if t in ("-p", "--port"):
            i += 1
            port = int(tokens[i])

        elif not t.startswith("-"):
            if host is None:
                if "@" in t:
                    user, host = t.split("@", 1)
                else:
                    host = t

        i += 1

    if not host:
        raise ValueError("Could not parse host")

    return user or "root", host, port


def main():
    if len(sys.argv) != 2:
        print("Usage: script.py 'ssh user@host -p PORT ...'")
        sys.exit(1)

    user, host, port = parse_ssh(sys.argv[1])

    os.makedirs(LOCAL_PATH, exist_ok=True)

    cmd = [
        "rsync",
        "-azP",
        "--ignore-existing",
        "-e",
        f"ssh -p {port} -i {IDENTITY}",
        f"{user}@{host}:{REMOTE_PATH}",
        LOCAL_PATH,
    ]

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()