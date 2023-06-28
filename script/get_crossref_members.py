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

from requests import get
from json import loads
from csv import DictReader
from os import remove


def normalized_crossref_list(tmp_file, header):
    dict_publishers = {}
    final_file = tmp_file[1:]

    with open(tmp_file) as f:
        reader = DictReader(f)
        for row in reader:
            dict_publishers[row["Member Name & ID"].lower()] = row

    with open(final_file, "w") as g:
        g.write('"'+'","'.join(header)+'"\n')

    with open(final_file, "a") as g:
        for i in sorted(dict_publishers.keys()):
            str_vals = ['"' + val + '"' for val in dict_publishers[i].values()]
            g.write(",".join(str_vals)+"\n")

    remove(tmp_file)


HTTP_HEADERS = {"User-Agent": "I4OC (mailto:tech@opencitations.net)"}

rows = 1000
header = [
    "Member Name & ID",
    #"Sponsored member & prefix",
    "Count Backfile DOIs",
    "Count Current DOIs",
    "Deposits Backfile References",
    "Deposits Current References",
    "Count Current Journal",
    "Count Backfile Journal",
    "Coverage Current Journal",
    "Coverage Backfile Journal"]


items = [i for i in range(0, rows)]
next_cursor = "*"
tmp_file = ".members.txt"

with open(tmp_file, "w") as g:
    g.write('"'+'","'.join(header)+'"\n')

while len(items) == rows:
    members = []
    api_call = "https://api.crossref.org/v1.0/members?rows=" + \
        str(rows)+"&cursor="+next_cursor

    print("calling: ", api_call)
    ref = get(api_call, headers=HTTP_HEADERS, timeout=30)

    if next_cursor == "*":
        print("Total number of members to elaborate with open references (mandatory in Crossref June 2022) is: ",
              str(loads(ref.text)["message"]["total-results"]))

    items = loads(ref.text)["message"]["items"]
    for item in items:
        member_meta = {
                "Member Name & ID": item["primary-name"] + " (ID "+str(item["id"])+")",
                #"Sponsored member & prefix": item["primary-name"] + pref["value"],

                "Count Backfile DOIs": str(item["counts"]["backfile-dois"]),
                "Count Current DOIs": str(item["counts"]["current-dois"]),
                "Deposits Backfile References": str(item["flags"]["deposits-references-backfile"]).lower(),
                "Deposits Current References": str(item["flags"]["deposits-references-current"]).lower()
        }

        try:
            member_meta["Count Current Journal"] = str(
                item["counts-type"]["current"]["journal-article"])
        except:
            member_meta["Count Current Journal"] = "0"

        try:
            member_meta["Count Backfile Journal"] = str(
                item["counts-type"]["backfile"]["journal-article"])
        except:
            member_meta["Count Backfile Journal"] = "0"

        try:
            member_meta["Coverage Current Journal"] = str(
                item["coverage-type"]["current"]["journal-article"]["references"])
        except:
            member_meta["Coverage Current Journal"] = "0.0"

        try:
            member_meta["Coverage Backfile Journal"] = str(
                item["coverage-type"]["backfile"]["journal-article"]["references"])
        except:
            member_meta["Coverage Backfile Journal"] = "0.0"

        members.append(member_meta)

    with open(tmp_file, "a") as g:
        for m in members:
            l_str = []
            for h in header:
                l_str.append(m[h])
            g.write('"'+'","'.join(l_str)+'"\n')

    next_cursor = loads(ref.text)["message"]["next-cursor"]

normalized_crossref_list(tmp_file, header)
