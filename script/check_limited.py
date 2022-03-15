# -*- coding: utf-8 -*-
# Copyright (c) 2018, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

# TODO: remember to remove "remove.txt" and "fine.txt" locally in this directory before starting a new process
# TODO: remember to download the new Crossref membership CSV document at https://www.crossref.org/reports/members-with-open-references/

from requests import get
from requests.exceptions import ReadTimeout
from csv import DictReader
from os import sep
from re import sub
from json import loads
from os.path import exists

api_call = "https://api.crossref.org/members/%s/works?filter=has-references:true,reference-visibility:%s"
HTTP_HEADERS = {"User-Agent": "check_limited.py / I4OC (mailto:essepuntato@opencitations.net)"}


def take_num(pub_id, ref_type):
    tent = 0

    while tent < 10:
        tent += 1
        try:
            ref = get(api_call % (pub_id, ref_type), headers=HTTP_HEADERS, timeout=30)
            j = loads(ref.text)
            return int(j["message"]["total-results"])
        except ReadTimeout:
            pass  # retry

    raise Exception("Reading online failed.")

not_fine = []
fine = []
if exists("remove.txt"):
    with open("remove.txt") as f:
        for line in f:
            not_fine.append(line.strip())

if exists("fine.txt"):
    with open("fine.txt") as f:
        for line in f:
            fine.append(line.strip())

with open(".." + sep + "data" + sep + "crossref.txt") as f:
    reader = DictReader(f)
    for row in reader:
        name_id = row["Member Name & ID"]
        if row["Reference Visibility"] in ("limited", "closed") and name_id not in not_fine and name_id not in fine:
            print("\nChecking", name_id, "...")
            pub_id = sub("^.+\\(ID ([0-9]+)\\).*$", "\\1", name_id)

            open_ref = take_num(pub_id, "open")
            limited_ref = take_num(pub_id, "limited")
            closed_ref = take_num(pub_id, "closed")

            total_ref = open_ref + limited_ref + closed_ref
            if open_ref / total_ref > 0.8:
                fine.append(name_id)
                with open("fine.txt", "a") as g:
                    g.write('"' + name_id + '"\n')
                print(name_id, "is fine!")
            else:
                not_fine.append(name_id)
                with open("remove.txt", "a") as g:
                    g.write('"' + name_id + '"\n')
                print(name_id, "has not < 20% of articles with references in the limited/closed datasets!")

print("\n\nPublishers that are not passing the threshold:")
for nf in sorted(not_fine):
    print(nf)
