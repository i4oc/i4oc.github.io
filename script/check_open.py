# -*- coding: utf-8 -*-
# Copyright (c) 2022, IVAN HEIBI <ivanhb.ita@gmail.com>
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

# How it works:
# 1) Generate the new list of crossref members (i.e., "crossref.txt") by running the script "get_crossref_members.py"
# 2) Run this script to generate the file "open_member_no_ref.txt" listing all the members in Crossref (included in "crossref.txt") which do not have at least one deposited article with references
# 3) Move and rename open_member_no_ref.txt > ../data/remove.txt

from requests import get
from requests.exceptions import ReadTimeout
from csv import DictReader
from os import sep
from re import sub
from json import loads

api_call = "https://api.crossref.org/members/%s/works?filter=has-references:true,reference-visibility:%s"
HTTP_HEADERS = {
    "User-Agent": "check_open.py / I4OC (mailto:tech@opencitations.net)"}


def take_num(pub_id, ref_type):
    tent = 0

    while tent < 10:
        tent += 1
        try:
            ref = get(api_call % (pub_id, ref_type),
                      headers=HTTP_HEADERS, timeout=30)
            j = loads(ref.text)
            return int(j["message"]["total-results"])
        except ReadTimeout:
            pass  # retry

    raise Exception("Reading online failed.")


# members with open references with at least 1 work that has referencecs
with_refs = []
with_no_refs = []
with open(".." + sep + "data" + sep + "crossref.txt") as f:
    reader = DictReader(f)
    for row in reader:
        name_id = row["Member Name & ID"]
        if name_id in with_refs or name_id in with_no_refs:
            continue
        if row["Reference Visibility"] in ("open"):
            print("\nChecking", name_id, "...")
            pub_id = sub("^.+\\(ID ([0-9]+)\\).*$", "\\1", name_id)

            open_ref = take_num(pub_id, "open")
            if open_ref == 0:
                with_no_refs.append(name_id)
                with open("open_member_no_ref.txt", "a") as g:
                    g.write('"' + name_id + '"\n')
                print(
                    name_id, "has no references deposited!")
            else:
                with_refs.append(name_id)
            #    print(name_id, " is fine: references > 1!")
