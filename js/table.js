/*
 * The data exposed via this script are taken from
 * https://www.crossref.org/reports/members-with-open-references/.
 * The logic for including/excluding publishers has been directly
 * embedded in this scripts.
 * Be aware: one has also to check if the 'limited' (if present) and 'closed' amount is below a given threshold
 */

 function sort_json(prop) {
    return function(a, b) {
        if (a[prop].toLowerCase() > b[prop].toLowerCase()) {
            return 1;
        } else if (a[prop].toLowerCase() < b[prop].toLowerCase()) {
            return -1;
        }
        return 0;
    }
}

function get_csv(pub_path) {
    $.ajax({
        url : pub_path,
        dataType: "text",
        success : function (pub_data) {
            create_table(pub_data);
        }
    });
}

function thousend(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function create_table(pub_data) {
    var table = $("#partpublishers");

    $("#loading_pl").css("display", "none");

    var json_data = $.csv.toObjects(pub_data);

    var remo_array = [];

    // table header
    //table.append("<tr class='table-top'><td></td><td><strong>Current journal articles with deposited references</strong></td><td><strong>Backfile journal articles with deposited references</strong></td></tr>");
    table.append("<tr class='table-top'><td></td><td></td></tr>");

    // Group the list of publishers under their corresponding alphabetic letter
    // The first group is the one having non alphabetic letter as first letter, i.e., "#"
    var new_group = false;
    var group = "#";
    var fine_items = 0;
    //add this <tr> if you want to toggle the corresponding list of each group
    //table.append("<tr id="+group.toLowerCase()+" class='group-top'><td><button onclick=on_header_click('"+group.toLowerCase()+"') class='group-top'>Group "+group+"</button></td></tr>");
    table.append("<tr id=groupheader_"+group.toLowerCase()+" class='group-top'><td><strong>"+group+"</strong></td></tr>");

    json_data.forEach(function(entry) {

        /* The name of the publisher */
        var cur_entry_text = entry["Member Name & ID"];

        /* The publisher will be considered only if it is not included in the remove list */
        if ($.inArray(cur_entry_text, remo_array) == -1) {
            /* Other constraints to check */
            /* count_current_type, count_backfile_type,deposits_references_current,deposits_references_backfile,references_current_type,references_backfile_type*/

            var count_current_journal = entry["Count Current Journal"]
            var count_backfile_journal = entry["Count Backfile Journal"]
            var coverage_current_journal = entry["Coverage Current Journal"]
            var coverage_backfile_journal = entry["Coverage Backfile Journal"]

            var back_deposit = entry["Deposits Backfile References"]
            var current_deposit = entry["Deposits Current References"]

            if (    //current_deposit == "true" &&
                    //back_deposit == "true" &&
                    (count_current_journal != 0 || count_backfile_journal != 0) &&
                    (count_current_journal == 0 || (count_current_journal > 0 && coverage_current_journal >= 0.75)) &&
                    (count_backfile_journal == 0 || (count_backfile_journal > 0 && coverage_backfile_journal >= 0.25))
                ) {

                fine_items = fine_items + 1;

                var pub_name = cur_entry_text.substring(0, cur_entry_text.indexOf(' (ID'));
                var pub_id = cur_entry_text.substring(cur_entry_text.indexOf(' (ID ') + 5, cur_entry_text.length - 1);
                const percentage_current = (coverage_current_journal * 100).toFixed(0)
                const percentage_back = (coverage_backfile_journal * 100).toFixed(0)


                /*check first letter: to group publishers together*/
                /*in case not alphabetic it goes under "#"*/
                var first_char = cur_entry_text[0]

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
                      table.append("<tr id=groupheader_"+group.toLowerCase()+" class='group-top'><td class='main-cell'><strong>"+group+"</strong></td><td></td></tr>");
                      new_group = false;
                }
                table.append("<tr id=groupmember_"+group.toLowerCase()+" class='group-tr'></tr>");

                pub_entity = "<a href='https://www.crossref.org/members/prep/"+pub_id + "'>" + pub_name + "</a>";

                curr_ref = percentage_current.toString()+"% of "+thousend(count_current_journal.toString())
                if (curr_ref == "0% of 0") {
                  curr_ref = "0"
                }

                back_ref = percentage_back.toString()+"% of "+thousend(count_backfile_journal.toString())
                if (back_ref == "0% of 0") {
                  back_ref = "0"
                }

                $("#partpublishers tr:last-child").append("<td>" + pub_entity + "</td><td>current content: "+ curr_ref + "<br>back files: "+back_ref+"</td>");
            }
            /*else {
              console.log("https://www.crossref.org/members/prep/"+cur_entry_text.substring(cur_entry_text.indexOf(' (ID ') + 5, cur_entry_text.length - 1), count_current_journal, coverage_current_journal, count_backfile_journal, coverage_backfile_journal);
            }*/
          }
    });

    console.log("Number of publishers in the list is:");
    console.log(fine_items);
}


var data_dir = "data/"; //PRODUCTION
// data_dir = "https://i4oc.org/data/" //LOCAL

var pub_file = data_dir + "crossref.txt";

var table = $("#partpublishers");
get_csv(pub_file);

//Set events
function on_header_click(group) {
  $( "tr.group-tr" ).each(function() {
    if ($( this ).attr('id') == group){
      $( this ).toggle();
    }
  });
};
