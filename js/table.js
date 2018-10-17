/*
 * The data exposed via this script are taken from
 * https://www.crossref.org/reports/members-with-open-references/.
 * It is important to clean the aforementioned CSV with the script
 * "remove_empty.py so as to include only the publishers that actually
 * comply with the release of open references."
 */

function get_csv(pub_path, rem_path, lnk_path) {
    $.ajax({
        url : pub_path,
        dataType: "text",
        success : function (pub_data) {
            $.ajax({
                url : rem_path,
                dataType: "text",
                success : function (rem_data) {
                    $.ajax({
                        url : lnk_path,
                        dataType: "text",
                        success : function (lnk_data) {
                            create_table(pub_data, rem_data, lnk_data);
                        }
                    });
                }
            });
        }
    });
}

function create_table(pub_data, rem_data, lnk_data) {
    var table = $("#partpublishers");

    var json_data = $.csv.toObjects(pub_data);
    var json_link = $.csv.toObjects(lnk_data);
    var json_remo = $.csv.toObjects(rem_data);

    /* Substituted with the link to Crossref Member Participation page
    var link_dict = {};
    json_link.forEach(function(entry) {
        link_dict[entry["Publisher"]] = entry["Address"];
    });
    */

    var remo_array = [];
    json_remo.forEach(function(entry) {
        remo_array.push(entry["Member Name & ID"]);
    });

    var done = [];
    var i = 0;
    var new_row = true;
    json_data.forEach(function(entry) {
        if (i == 0 && new_row) {
            table.append("<tr></tr>");
            new_row = false;
        }

        var cur_entry_text = entry["Member Name & ID"];

        if ($.inArray(cur_entry_text, remo_array) != 0) {
            var pub_name = cur_entry_text.substring(0, cur_entry_text.indexOf(' (ID'));
            var pub_id = cur_entry_text.substring(
                cur_entry_text.indexOf(' (ID ') + 5, cur_entry_text.length - 1);

            if ($.inArray(pub_name, done) != 0) {
                i = (i + 1) % 2;
                new_row = true;
                done.push(pub_name);

                /*
                if (pub_name in link_dict) {
                    var cur_link = link_dict[pub_name];
                    if (cur_link != "None") {
                        pub_name = "<a href='" + link_dict[pub_name] + "'>" + pub_name + "</a>";
                    }
                }
                */

                pub_name = "<a href='https://www.crossref.org/members/prep/" +
                    pub_id + "'>" + pub_name + "</a>";

                $("#partpublishers tr:last-child").append("<td>" + pub_name + "</td>");
            }
        }
    });
}

var data_dir = "data/";
var pub_file = data_dir + "crossref.txt";
var rem_file = data_dir + "remove.txt";
var lnk_file = data_dir + "links.txt";

var table = $("#partpublishers");
get_csv(pub_file, rem_file, lnk_file);