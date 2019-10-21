frappe.ui.form.on("Sales Invoice", {
    onload: function(frm) {
        if (frm.doc.is_return == "0") {
            frm.set_value("naming_series","ACC-SINV-.YYYY.-");
        }
        else if (frm.doc.is_return == "1") {
            frm.set_value("naming_series","ACC-CN-.YYYY.-");
        }
    },
});
