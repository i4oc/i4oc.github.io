/*
 * The data exposed via this script are taken from
 * https://www.crossref.org/reports/members-with-open-references/.
 * The logic for including/excluding publishers has been directly
 * embedded in this scripts.
 * Be aware: one has also to check if the 'limited' (if present) and 'closed' amount is below a given threshold
 */

function get_csv(pub_path, rem_path) {
    $.ajax({
        url : pub_path,
        dataType: "text",
        success : function (pub_data) {
            $.ajax({
                url : rem_path,
                dataType: "text",
                success : function (rem_data) {
                    create_table(pub_data, rem_data);
                }
            });
        }
    });
}

function create_table(pub_data, rem_data) {
    var table = $("#partpublishers");

    var json_data = $.csv.toObjects(pub_data);
    var json_remo = $.csv.toObjects(rem_data);

    var remo_array = [];
    json_remo.forEach(function(entry) {
        remo_array.push(entry["Member Name & ID"]);
    });

    var done = [];
    var i = 0;
    var new_row = true;

    // Group the list of publishers under their corresponding alphabetic letter
    // The first group is the one having non alphabetic letter as first letter, i.e., "#"
    var new_group = false;
    var group = "#"
    //add this <tr> if you want to toggle the corresponding list of each group
    //table.append("<tr id="+group.toLowerCase()+" class='group-top'><td><button onclick=on_header_click('"+group.toLowerCase()+"') class='group-top'>Group "+group+"</button></td></tr>");
    table.append("<tr id=groupheader_"+group.toLowerCase()+" class='group-top'><td><strong>"+group+"</strong></td></tr>");

    json_data.forEach(function(entry) {

        /* The name of the publisher */
        var cur_entry_text = entry["Member Name & ID"];

        if (i == 0 && new_row) {
            table.append("<tr id=groupmember_"+group.toLowerCase()+" class='group-tr'></tr>");
            new_row = false;
        }

        console.log(cur_entry_text, $.inArray(cur_entry_text, remo_array));

        /* The publisher will be considered only if it is not included in the remove list */
        if ($.inArray(cur_entry_text, remo_array) == -1) {
            /* Other constraints to check */
            var ref_visibility = entry["Reference Visibility"]
            var back_doi = parseInt(entry["Total Backfile DOIs"])
            var back_deposit = entry["Deposits Backfile References"]
            var current_doi = parseInt(entry["Total Current DOIs"])
            var current_deposit = entry["Deposits Current References"]

            if (    ref_visibility == "open" &&
                    current_deposit == "true" &&
                    (current_doi > 0 || (backfile_doi > 0 && back_deposit == "true"))) {
                var pub_name = cur_entry_text.substring(0, cur_entry_text.indexOf(' (ID'));
                var pub_id = cur_entry_text.substring(
                    cur_entry_text.indexOf(' (ID ') + 5, cur_entry_text.length - 1);

                if ($.inArray(pub_name, done) == -1) {
                    i = (i + 1) % 2;
                    new_row = true;

                    /*check first letter: to group publishers together*/
                    /*in case not alphabetic it goes under "#"*/
                    var first_char = cur_entry_text.substring(0, cur_entry_text.indexOf(' (ID'))[0]
                    console.log(first_char);
                    console.log((/[a-zA-Z]/).test(first_char));
                    if ((/[a-zA-Z]/).test(first_char)) {
                      new_group = group != first_char.toUpperCase();
                      group = first_char.toUpperCase();
                    }else{
                      new_group = group != "#";
                      group = "#";
                    }

                    if (new_group) {
                      //add this <tr> if you want to toggle the corresponding list of each group
                      //table.append("<tr id="+group.toLowerCase()+" class='group-top'><td><button onclick=on_header_click('"+group.toLowerCase()+"') class='group-top'><strong>"+group+"</strong></button></td></tr>");
                      table.append("<tr id=groupheader_"+group.toLowerCase()+" class='group-top'><td><strong>"+group+"</strong></td></tr>");
                      table.append("<tr id=groupmember_"+group.toLowerCase()+" class='group-tr'></tr>");
                      new_group = false;
                      new_row = false;
                      i = 1;
                    }

                    done.push(pub_name);
                    pub_name = "<a href='https://www.crossref.org/members/prep/" +
                        pub_id + "'>" + pub_name + "</a>";

                    $("#partpublishers tr:last-child").append("<td>" + pub_name + "</td>");
                }
            }
        }
    });
}


var data_dir = "data/";
// use this instead for local tests
// data_dir = "https://i4oc.org/data/"

var pub_file = data_dir + "crossref.txt";
var rem_file = data_dir + "remove.txt";

var table = $("#partpublishers");
get_csv(pub_file, rem_file);

//Set events
function on_header_click(group) {
  $( "tr.group-tr" ).each(function() {
    if ($( this ).attr('id') == group){
      $( this ).toggle();
    }
  });
};
