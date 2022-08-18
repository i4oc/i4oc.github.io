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


HTTP_HEADERS = {"User-Agent": "I4OC (mailto:tech@opencitations.net)"}

rows = 1000
for visibility in ["closed", "limited", "open"]:
    members = set()
    items_with_no_mem = set()
    items = [i for i in range(0, rows)]
    next_cursor = "*"

    with open("members_"+visibility+".txt", "w") as g:
        g.write('"Member Name & ID","Sponsored member & prefix","Reference Visibility","Total Backfile DOIs","Total Current DOIs","Deposits Backfile References","Deposits Current References"\n')

    while len(items) == rows:
        api_call = "https://api.crossref.org/v1.0/members?filter=reference-visibility:" + \
            str(visibility)+"&rows="+str(rows)+"&cursor="+next_cursor

        print("calling: ", api_call)
        ref = get(api_call, headers=HTTP_HEADERS, timeout=30)

        if next_cursor == "*":
            print("Total number of members to elaborate with reference-visibility= ",
                  visibility, " is: ", str(loads(ref.text)["message"]["total-results"]))

        items = loads(ref.text)["message"]["items"]
        for item in items:
            for pref in item["prefix"]:
                # e.g. "American Physical Society (APS) (ID 16)","American Physical Society10.1103","open","661523","50657","true","true"
                members.append({
                    "Member Name & ID": item["primary-name"] + " (ID "+str(item["id"])+")",
                    "Sponsored member & prefix": item["primary-name"] + pref["value"],
                    "Reference Visibility": pref["reference-visibility"],
                    "Total Backfile DOIs": str(item["counts"]["backfile-dois"]),
                    "Total Current DOIs": str(item["counts"]["current-dois"]),
                    "Deposits Backfile References": str(item["flags"]["deposits-references-backfile"]).lower(),
                    "Deposits Current References": str(item["flags"]["deposits-references-current"]).lower()
                })

            with open("members_"+visibility+".txt", "a") as g:
                #sort and remove duplicates
                dict_members = dict()
                for m in members:
                    dict_members[m["Member Name & ID"].lower()] = m

                for i in sorted(dict_members.keys()):
                    str_vals = ['"' + val
                                + '"' for val in dict_members[i].values()]
                    g.write(",".join(str_vals)+"\n")

        next_cursor = loads(ref.text)["message"]["next-cursor"]
