"""Install (or remove) the dsh-Weyland CRT ident as a DeepSeek Harness plugin.

  python plugin/install.py              install, or update an existing install
  python plugin/install.py --uninstall  remove it again
  python plugin/install.py --profile <dir>   non-default profile directory

What it does, in order:

  1. finds the dsh profile (default ~/.dsh/profiles/desktop)
  2. notes whether a rival intro plugin (dsh-boot-intro) is already there,
     and builds the ident to take turns with it if so -- or to always play
     if not, so a machine with only this plugin never sits through a launch
     with no intro at all
  3. copies package.json and lib/ into <profile>/node_modules/dsh-weyland-intro
  4. registers the plugin in <profile>/cordis.patch.yml, backing that file up
     first and touching only its own entry

Nothing outside the profile directory is modified, and --uninstall reverses
all of it.
"""

import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, os.pardir, "config.json")
PLUGIN_NAME = "dsh-weyland-intro"
RIVAL_NAME = "dsh-boot-intro"
DEFAULT_PROFILE = os.path.join(os.path.expanduser("~"), ".dsh", "profiles", "desktop")

# YAML row list that loads this plugin, and the file it lives in
PATCH_NAME = "cordis.patch.yml"
INSERT_KEY = "- insert:"
INSERT_ROW = ("    - id: weyland-intro",
              "      name: dsh-weyland-intro")
PATCH_HEADER = (
    "# Your patch layer for this dsh profile, applied after every bundle layer.\n"
    "# Created by dsh-Weyland's installer.\n")


def fail(message):
    print("error: " + message)
    sys.exit(1)


def read_lines(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
    trailing = bool(lines) and lines[-1] == ""
    if trailing:
        lines.pop()
    return lines, trailing, newline


def write_lines(path, lines, trailing, newline):
    data = newline.join(line.encode("utf-8") for line in lines)
    if trailing or lines:
        data += newline
    with open(path, "wb") as fh:
        fh.write(data)


def find_row(lines):
    """Index of the `name:` line that loads us, or -1."""
    for i, line in enumerate(lines):
        if line.strip() == "name: " + PLUGIN_NAME:
            return i
    return -1


def add_row(lines):
    """Append our row to the first `- insert:` list, or start one."""
    for i, line in enumerate(lines):
        if line.strip() != INSERT_KEY:
            continue
        # walk past that list's existing items so a re-install lands in the
        # same place as the install that came before it
        at = i + 1
        while at < len(lines) and lines[at].startswith("    ") and lines[at].strip():
            at += 1
        lines.insert(at, INSERT_ROW[0])
        lines.insert(at + 1, INSERT_ROW[1])
        return lines
    if lines and lines[-1].strip():
        lines.append("")
    lines.extend([INSERT_KEY, INSERT_ROW[0], INSERT_ROW[1]])
    return lines


def drop_row(lines, name_at):
    """Undo add_row: drop our id/name pair, then the key if it emptied."""
    id_at = name_at - 1
    key_at = name_at - 2
    if id_at < 0 or lines[id_at].strip() != INSERT_ROW[0].strip():
        return lines                     # not shaped as we expect -- leave it
    del lines[name_at]
    del lines[id_at]
    if key_at >= 0 and lines[key_at].strip() == INSERT_KEY:
        following = lines[key_at + 1] if key_at + 1 < len(lines) else ""
        if not following.strip() or not following.startswith("    "):
            del lines[key_at]
    return lines


def emblem_choice(argv):
    """Which emblem to build: --emblem wins, then config.json, then rotate."""
    if "--emblem" in argv:
        index = argv.index("--emblem")
        if index + 1 < len(argv):
            return argv[index + 1]
    try:
        with open(CONFIG, "r", encoding="utf-8") as fh:
            value = (json.load(fh) or {}).get("emblem")
        if value in ("rotate", "circle", "corp"):
            return value
    except Exception:
        pass
    return "rotate"


def install(profile, emblem):
    node_modules = os.path.join(profile, "node_modules")
    target = os.path.join(node_modules, PLUGIN_NAME)
    patch = os.path.join(profile, PATCH_NAME)

    if not os.path.isdir(profile):
        fail("no dsh profile at %s -- pass --profile if yours lives elsewhere"
             % profile)

    rival = os.path.isdir(os.path.join(node_modules, RIVAL_NAME))
    if rival:
        print("rival    : %s found -- the two intros will take turns" % RIVAL_NAME)
    else:
        print("rival    : none -- this ident will play on every launch")

    args = [sys.executable, os.path.join(HERE, "build.py"), "--emblem", emblem]
    if rival:
        args.append("--alternate")
    print("emblem   : %s" % emblem)
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        fail("build failed:\n" + result.stdout + result.stderr)

    os.makedirs(node_modules, exist_ok=True)
    os.makedirs(os.path.join(target, "lib"), exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "package.json"),
                    os.path.join(target, "package.json"))
    for name in ("index.js", "client.js"):
        shutil.copyfile(os.path.join(HERE, "lib", name),
                        os.path.join(target, "lib", name))
    print("plugin   : %s" % target)

    if os.path.isfile(patch):
        lines, trailing, newline = read_lines(patch)
        if find_row(lines) >= 0:
            print("register : already listed in %s" % PATCH_NAME)
            return
        backup = patch + ".bak-dsh-weyland"
        if not os.path.exists(backup):
            shutil.copyfile(patch, backup)
            print("backup   : %s" % backup)
        write_lines(patch, add_row(lines), trailing, newline)
    else:
        os.makedirs(os.path.dirname(patch), exist_ok=True)
        lines = PATCH_HEADER.rstrip("\n").split("\n") + [INSERT_KEY,
                                                         INSERT_ROW[0],
                                                         INSERT_ROW[1]]
        write_lines(patch, lines, True, b"\n")
        print("created  : %s" % patch)
    print("register : added to %s" % PATCH_NAME)
    print()
    print("Done. Restart DeepSeek Harness to see it.")


def uninstall(profile):
    node_modules = os.path.join(profile, "node_modules")
    target = os.path.join(node_modules, PLUGIN_NAME)
    patch = os.path.join(profile, PATCH_NAME)

    if os.path.isdir(target):
        shutil.rmtree(target)
        print("removed  : %s" % target)
    else:
        print("absent   : %s" % target)

    if os.path.isfile(patch):
        lines, trailing, newline = read_lines(patch)
        at = find_row(lines)
        if at >= 0:
            write_lines(patch, drop_row(lines, at), trailing, newline)
            print("register : removed from %s" % PATCH_NAME)
        else:
            print("register : not listed in %s" % PATCH_NAME)
    print()
    print("Done. Restart DeepSeek Harness.")


def main():
    argv = sys.argv[1:]
    profile = DEFAULT_PROFILE
    if "--profile" in argv:
        index = argv.index("--profile")
        if index + 1 >= len(argv):
            fail("--profile needs a directory")
        profile = os.path.abspath(argv[index + 1])

    print("profile  : %s" % profile)
    if "--uninstall" in argv:
        uninstall(profile)
    else:
        install(profile, emblem_choice(argv))


if __name__ == "__main__":
    main()
