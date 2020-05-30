// Copyright (c) 2017, Bravo Logisitcs and contributors
// For license information, please see license.txt

frappe.ui.form.on('Files', {
    refresh: function (frm) {
        console.log(frm);
        frm.events.hide_show_sections(frm);
        frm.events.load_expenses(frm);
        frm.events.load_invoices(frm);
        frm.events.load_payments(frm);
        frm.events.load_purchase_invoices(frm);
        
        frm.events.close_buttons(frm);

        //Load import|export|transport reference status
        //something to add
        if ((frm.doc.requested_service == "Importation-Transit" || frm.doc.requested_service == "Importation-Local") && frm.doc.import_reference) {
            frappe.model.with_doc('Import', frm.doc.import_reference, function () {
                var reference_doc = frappe.model.get_doc('Import', frm.doc.import_reference);
                var html = '<span class="control-label">Import Status</span><br><p><b>' + reference_doc.status + '</b></p>';
                $(frm.fields_dict.import_status.wrapper).html(html);
            });
        }
        /*else if (frm.doc.requested_service == "Border Processing") {
                   frappe.model.with_doc('Border Processing', frm.doc.border_processing_reference, function () {
                       var reference_doc = frappe.model.get_doc('Border Processing', frm.doc.border_processing_reference);
                       var html = '<span class="control-label">Border Processing Status </span><br><p><b>' + reference_doc.status + '</b></p>';
                       $(frm.fields_dict.border_processing_status.wrapper).html(html);
                   });
               }*/

        //Add sales Invoice button
        frm.add_custom_button(__('Sales Invoice'),
            function () {
                frm.events.make_sales_invoice();
            }, __("Make")
        );

        //Add purchase invoice button
        frm.add_custom_button(__('Purchase Invoice'),
            function () {
                frm.events.make_purchase_invoice();
            }, __("Make")
        );
    },

    /* validate: function (frm) {
        if (frm.doc.import_transit || frm.doc.import_local) {
            if (!frm.doc.bl_number) {
                frappe.msgprint("Please enter BL Number", "Error");
                frappe.validated = false;
            }
        } else if (frm.doc.export_transit || frm.doc.export_local) {
            if (!frm.doc.booking_number) {
                frappe.msgprint("Please enter a Booking Number", "Error");
                frappe.validated = false;
            }
        } else if (frm.doc.transport_transit || frm.doc.transport_local) {
            if (!frm.doc.source_country || !frm.doc.source_city) {
                frappe.msgprint("Please enter the cargo location", "Error");
                frappe.validated = false;
            } else if (!frm.doc.destination_country || !frm.doc.destination_city) {
                frappe.msgprint("Please enter the cargo destination", "Error");
                frappe.validated = false;
            }
        } else if (frm.doc.border_clearance) {
            if (!frm.doc.number_of_borders || frm.doc.number_of_borders < 1) {
                frappe.msgprint("Please enter number of borders greater than 0", "Error");
                frappe.validated = false;
            }
        } else {
            frappe.msgprint("Please choose at least one service", "Error");
            frappe.validated = false;
        }
    },
*/


    //validation after checkbox removed
    validate: function (frm) {
        if (frm.doc.requested_service == "Importation-Transit" ||
            frm.doc.requested_service == "Importation-Local") {
            if (!frm.doc.bl_number) {
                frappe.msgprint("Please enter BL Number", "Error");
                frappe.validated = false;
            }
        } else if (frm.doc.requested_service == "Border Processing") {
            if (!frm.doc.cross_border_no) {
                frappe.msgprint("Please enter border processing number reference", "Error");
                frappe.validated = false;
            }
        } else if (frm.doc.requested_service == "Export-Transit" || frm.doc.requested_service == "Export-Local") {
            if (!frm.doc.booking_number) {
                frappe.msgprint("Please enter a Booking Number", "Error");
                frappe.validated = false;
            }
        } else if (frm.doc.requested_service == "Transport-Transit" || frm.doc.requested_service == "Transport-Local") {
            if (!frm.doc.source_country || !frm.doc.source_city) {
                frappe.msgprint("Please enter the cargo location", "Error");
                frappe.validated = false;
            } else if (!frm.doc.destination_country || !frm.doc.destination_city) {
                frappe.msgprint("Please enter the cargo destination", "Error");
                frappe.validated = false;
            }
        } else if (frm.doc.requested_service == "Border Clearance") {
            if (!frm.doc.number_of_borders || frm.doc.number_of_borders < 1) {
                frappe.msgprint("Please enter number of borders greater than 0", "Error");
                frappe.validated = false;
            }
        } else {
            frappe.msgprint("Please choose at least one service", "Error");
            frappe.validated = false;
        }
    },


    close_buttons: function (frm) {
        if (!frm.doc.__islocal) {
            if (frm.doc.status == "Open") {
                frm.add_custom_button(__("Close"), function () {
                    if (frm.events.validate_close(frm)) {
                        frm.set_value("status", "Closed");
                        frm.save();
                    }
                }, "fa fa-check", "btn-success");
            }
        }
    },

    /*    after_save: function (frm) {
            //If there is unrequested funds
            frm.events.new_fund_request(frm);


            //needs to be edited
            //If import service selected
            if (frm.doc.import_transit || frm.doc.import_local) {
                var import_typ = null;
                if (frm.doc.import_transit) {
                    import_typ = 'Transit';
                } else if (frm.doc.import_local) {
                    import_typ = 'Local';
                }
                frappe.call({
                    method: "csf_tz.clearing_and_forwarding.doctype.import.import.create_import",
                    freeze: true,
                    args: {
                        bl_number: frm.doc.bl_number,
                        documents_received_date: frm.doc.documents_received_date,
                        location: frm.doc.location,
                        customer: frm.doc.customer,
                        file_number: frm.docname,
                        import_type: import_typ
                    },
                    callback: function (data) {
                        if (!frm.doc.import_reference) {
                            frm.set_value('import_reference', data.message);
                            frm.save();
                        }
                    }
                })
            } else if (frm.doc.export_transit || frm.doc.export_local) //If export is selected
            {
                var export_typ = null;
                if (frm.doc.export_local) {
                    export_typ = 'Local';
                } else if (frm.doc.export_transit) {
                    export_typ = 'Transit';
                }
                frappe.call({
                    method: "csf_tz.clearing_and_forwarding.doctype.export.export.create_export",
                    freeze: true,
                    args: {
                        booking_number: frm.doc.booking_number,
                        documents_received_date: frm.doc.documents_received_date,
                        location: frm.doc.location,
                        customer: frm.doc.customer,
                        export_type: export_typ,
                        file_number: frm.docname
                    },
                    callback: function (data) {
                        if (!frm.doc.export_reference) {
                            frm.set_value('export_reference', data.message);
                            frm.save();
                        }
                    }
                })
            } else if (frm.doc.transport_transit || frm.doc.transport_local) //If transport is selected
            {
                var transport_typ = null;
                if (frm.doc.transport_local) {
                    transport_typ = 'Internal';
                } else if (frm.doc.transport_transit) {
                    transport_typ = 'Cross Border';
                }
                frappe.call({
                    method: "fleet_management.fleet_management.doctype.transport_request.transport_request.create_transport_request",
                    freeze: true,
                    args: {
                        request_received: frm.doc.documents_received_date,
                        customer: frm.doc.customer,
                        transport_type: transport_typ,
                        file_number: frm.docname,
                        cargo_location_country: frm.doc.source_country,
                        cargo_location_city: frm.doc.source_city,
                        cargo_destination_country: frm.doc.destination_country,
                        cargo_destination_city: frm.doc.destination_city,
                    },
                    callback: function (data) {
                        if (!frm.doc.transport_reference) {
                            setTimeout(function () {
                                frm.set_value('transport_reference', data.message);
                                frm.save();
                            }, 1000);
                        }
                    }
                })
            } else if (frm.doc.border_clearance) //If border clearance is selected
            {
                frappe.call({
                    method: "csf_tz.clearing_and_forwarding.doctype.border_clearance.border_clearance.create_border_clearance",
                    freeze: true,
                    args: {
                        number_of_borders: frm.doc.number_of_borders,
                        location: frm.doc.location,
                        documents_received_date: frm.doc.documents_received_date,
                        customer: frm.doc.customer,
                        file_number: frm.docname
                    },
                    callback: function (data) {
                        if (!frm.doc.border_clearance_ref) {
                            frm.set_value('border_clearance_ref', data.message);
                            frm.save();
                        }
                    }
                })
            }
            frm.reload_doc();
        },*/

    //after_save after checkbox removed
    after_save: function (frm) {
        //If there is unrequested funds
        frm.events.new_fund_request(frm);

        //If import service selected
        if (frm.doc.requested_service == "Importation-Transit" || frm.doc.requested_service == "Importation-Local") {
            var import_typ = null;
            if (frm.doc.requested_service == "Importation-Transit") {
                import_typ = 'Transit';
            } else if (frm.doc.requested_service == "Importation-Local") {
                import_typ = 'Local';
            }
            frappe.call({
                method: "csf_tz.clearing_and_forwarding.doctype.import.import.create_import",
                freeze: true,
                args: {
                    bl_number: frm.doc.bl_number,
                    documents_received_date: frm.doc.documents_received_date,
                    location: frm.doc.location,
                    customer: frm.doc.customer,
                    file_number: frm.docname,
                    import_type: import_typ
                },
                callback: function (data) {
                    if (!frm.doc.import_reference) {
                        frm.set_value('import_reference', data.message);
                        frm.save();
                    }
                }
            })
        } else if (frm.doc.requested_service == "Export-Transit" || frm.doc.requested_service == "Export-Local") //If export is selected
        {
            var export_typ = null;
            if (frm.doc.requested_service == "Export-Local") {
                export_typ = 'Local';
            } else if (frm.doc.requested_service == "Export-Transit") {
                export_typ = 'Transit';
            }
            frappe.call({
                method: "csf_tz.clearing_and_forwarding.doctype.export.export.create_export",
                freeze: true,
                args: {
                    booking_number: frm.doc.booking_number,
                    documents_received_date: frm.doc.documents_received_date,
                    location: frm.doc.location,
                    customer: frm.doc.customer,
                    export_type: export_typ,
                    file_number: frm.docname
                },
                callback: function (data) {
                    if (!frm.doc.export_reference) {
                        frm.set_value('export_reference', data.message);
                        frm.save();
                    }
                }
            })
        } else if (frm.doc.requested_service == "Transport-Transit" || frm.doc.requested_service == "Transport-Local") //If transport is selected
        {
            var transport_typ = null;
            if (frm.doc.requested_service == "Transport-Local") {
                transport_typ = 'Internal';
            } else if (frm.doc.requested_service == "Transport-Transit") {
                transport_typ = 'Cross Border';
            }
            frappe.call({
                method: "fleet_management.fleet_management.doctype.transport_request.transport_request.create_transport_request",
                freeze: true,
                args: {
                    request_received: frm.doc.documents_received_date,
                    customer: frm.doc.customer,
                    transport_type: transport_typ,
                    file_number: frm.docname,
                    cargo_location_country: frm.doc.source_country,
                    cargo_location_city: frm.doc.source_city,
                    cargo_destination_country: frm.doc.destination_country,
                    cargo_destination_city: frm.doc.destination_city,
                },
                callback: function (data) {
                    if (!frm.doc.transport_reference) {
                        setTimeout(function () {
                            frm.set_value('transport_reference', data.message);
                            frm.save();
                        }, 1000);
                    }
                }
            })
        } else if (frm.doc.requested_service == "Border Clearance") //If border clearance is selected
        {
            frappe.call({
                method: "csf_tz.clearing_and_forwarding.doctype.border_clearance.border_clearance.create_border_clearance",
                freeze: true,
                args: {
                    number_of_borders: frm.doc.number_of_borders,
                    location: frm.doc.location,
                    documents_received_date: frm.doc.documents_received_date,
                    customer: frm.doc.customer,
                    file_number: frm.docname
                },
                callback: function (data) {
                    if (!frm.doc.border_clearance_ref) {
                        frm.set_value('border_clearance_ref', data.message);
                        frm.save();
                    }
                }
            })
        } else if (frm.doc.requested_service == "Border Processing") //If border processing is selected
        {
            console.log("create function to create border processing doc");
            frappe.call({
                method: "csf_tz.clearing_and_forwarding.doctype.border_processing.border_processing.create_border_processing",
                freeze: true,
                args: {
                    cross_border_no: frm.doc.cross_border_no,
                    //location: frm.doc.location,
                    //documents_received_date: frm.doc.documents_received_date,
                    customer: frm.doc.customer,
                    file_number: frm.docname,
                    doctype: frm.doctype
                },
                callback: function (data) {
                    if (!frm.doc.border_processing_reference) {
                        frm.set_value('border_processing_reference', data.message);
                        frm.save();
                    }
                }
            })
        }
        frm.reload_doc();
    },


    validate_close: function (frm) {
        var excluded_fields = ['requested_funds', 'attachments', 'expenses', 'purchase_invoices_html', 'total_expenses_html', 'invoices_html', 'payments_html', 'sales_order_reference', 'quotation', 'cross_border_no', 'border_processing_reference', 'border_processing_status'];
        if (frm.doc.requested_service == "Importation-Transit" || frm.doc.requested_service == "Importation-Local") {

            frappe.call({
                method: "csf_tz.clearing_and_forwarding.doctype.import.import.check_import_status",
                freeze: true,
                args: {
                    import_reference: frm.import_reference,
                    file_number: frm.docname
                },
                callback: function (status) {
                    if (status == 'Closed') {
                        console.log(status);

                        excluded_fields.push('per_unit', 'export_reference', 'booking_number', 'source_country', 'source_city', 'destination_country', 'destination_city', 'number_of_borders', 'export_status', 'transport_reference', 'transport_status', 'border_clearance_ref', 'border_clearance_status');
                    }
                }
            })

        } else if (frm.doc.requested_service == 'Export-Transit' || frm.doc.requested_service == 'Export-Local') {

            frappe.call({
                method: "csf_tz.clearing_and_forwarding.doctype.export.export.check_export_status",
                freeze: true,
                args: {
                    //import_reference: frm.import_reference,
                    file_number: frm.docname
                },
                callback: function (status) {
                    if (status == 'Closed') {
                        console.log(status);

                        excluded_fields.push('per_unit', 'import_status', 'bl_number', 'import_reference', 'import_status', 'source_country', 'source_city', 'destination_country', 'destination_city', 'number_of_borders', 'export_status', 'transport_reference', 'transport_status', 'border_clearance_ref', 'border_clearance_status');
                    }
                }
            })

        } else if (frm.doc.requested_service == 'Transport-Transit' || frm.doc.requested_service == 'Transport-Local') {
            console.log("okk");
            frappe.call({
                method: "fleet_management.fleet_management.doctype.vehicle_trip.vehicle_trip.check_trip_status",
                freeze: true,
                args: {
                    //import_reference: frm.import_reference,
                    file_number: frm.docname
                },

                callback: function (status) {
                    console.log("okk2");

                    if (status == 'Closed') {
                        console.log(status);

                        excluded_fields.push('per_unit', 'export_reference', 'import_status', 'bl_number', 'booking_number', 'import_reference', 'import_status', 'number_of_borders', 'export_status', 'border_clearance_ref', 'border_clearance_status');

                    }
                }
            })

        } else if (frm.doc.requested_service == 'Border Clearance') {

            excluded_fields.push('per_unit', 'export_reference', 'import_status', 'bl_number', 'booking_number', 'import_reference', 'import_status', 'number_of_borders', 'export_status', 'transport_reference', 'destination_city', 'destination_country', 'source_city');
        }
        var excluded_field_type = ["Table", "Section Break", "Column Break", "HTML"];
        var error_fields = [];
        frm.meta.fields.forEach(function (field) {
            if (!(excluded_field_type.indexOf(field.fieldtype) > -1) && !(excluded_fields.indexOf(field.fieldname) > -1) && !(field.fieldname in frm.doc)) {
                error_fields.push(field.label);
                return false;
            }

            if (field.fieldtype == "Table" && !(excluded_fields.indexOf(field.fieldname) > -1) && frm.doc[field.fieldname].length == 0) {
                error_fields.push(field.label);
                return false;
            }
        })

        if (error_fields.length > 0) {
            var error_msg = "Mandatory fields required before closing <br><ul>";
            error_fields.forEach(function (error_field) {
                error_msg = error_msg + "<li>" + error_field + "</li>";
            })
            error_msg = error_msg + "</ul>";
            frappe.msgprint(error_msg, "Missing Fields");
            return false;
        } else {
            return true;
        }
    },


    /* services_selection: function (frm) {
         /Allow only one import or export to be selected and only one transport (local or transit)
         if (frm.doc.import_transit && frm.doc.import_transit == 1) {
             frm.set_value('import_local', 0);
             frm.set_value('export_local', 0);
             frm.set_value('export_transit', 0);
             frm.set_value('border_clearance', 0);
             frm.set_value('transport_local', 0);
             frm.set_value('transport_transit', 0);
         } else if (frm.doc.import_local && frm.doc.import_local == 1) {
             frm.set_value('import_transit', 0);
             frm.set_value('export_local', 0);
             frm.set_value('export_transit', 0);
             frm.set_value('border_clearance', 0);
             frm.set_value('transport_local', 0);
             frm.set_value('transport_transit', 0);
         } else if (frm.doc.export_transit && frm.doc.export_transit == 1) {
             frm.set_value('export_local', 0);
             frm.set_value('import_local', 0);
             frm.set_value('import_transit', 0);
             frm.set_value('border_clearance', 0);
             frm.set_value('transport_local', 0);
             frm.set_value('transport_transit', 0);
         } else if (frm.doc.export_local && frm.doc.export_local == 1) {
             frm.set_value('export_transit', 0);
             frm.set_value('import_local', 0);
             frm.set_value('import_transit', 0);
             frm.set_value('border_clearance', 0);
             frm.set_value('transport_local', 0);
             frm.set_value('transport_transit', 0);
         } else if (frm.doc.border_clearance && frm.doc.border_clearance == 1) {
             frm.set_value('export_local', 0);
             frm.set_value('export_transit', 0);
             frm.set_value('import_local', 0);
             frm.set_value('import_transit', 0);
             frm.set_value('transport_local', 0);
             frm.set_value('transport_transit', 0);
         } else if (frm.doc.transport_transit && frm.doc.transport_transit == 1) {
             frm.set_value('export_local', 0);
             frm.set_value('export_transit', 0);
             frm.set_value('import_local', 0);
             frm.set_value('import_transit', 0);
             frm.set_value('border_clearance', 0);
             frm.set_value('transport_local', 0);
         } else if (frm.doc.transport_local && frm.doc.transport_local == 1) {
             frm.set_value('export_local', 0);
             frm.set_value('export_transit', 0);
             frm.set_value('import_local', 0);
             frm.set_value('import_transit', 0);
             frm.set_value('border_clearance', 0);
             frm.set_value('transport_transit', 0);
         }
     },*/


    services_selection: function (frm) {
        //Allow only one import or export to be selected and only one transport (local or transit)
        if (frm.doc.requested_service == 'Importation-Transit') {
            //frm.events.hide_show_sections(frm);
            frm.set_value('import_local', 0);
            frm.set_value('export_local', 0);
            frm.set_value('export_transit', 0);
            frm.set_value('border_clearance', 0);
            frm.set_value('transport_local', 0);
            frm.set_value('transport_transit', 0);
        } else if (frm.doc.requested_service == 'Importation-Local') {
            //frm.events.hide_show_sections(frm);
            frm.set_value('import_transit', 0);
            frm.set_value('export_local', 0);
            frm.set_value('export_transit', 0);
            frm.set_value('border_clearance', 0);
            frm.set_value('transport_local', 0);
            frm.set_value('transport_transit', 0);
        } else if (frm.doc.requested_service == 'Export-Transit') {
            //frm.events.hide_show_sections(frm);
            frm.set_value('export_local', 0);
            frm.set_value('import_local', 0);
            frm.set_value('import_transit', 0);
            frm.set_value('border_clearance', 0);
            frm.set_value('transport_local', 0);
            frm.set_value('transport_transit', 0);

        } else if (frm.doc.requested_service == 'Export-Local') {
            //frm.events.hide_show_sections(frm);
            frm.set_value('export_transit', 0);
            frm.set_value('import_local', 0);
            frm.set_value('import_transit', 0);
            frm.set_value('border_clearance', 0);
            frm.set_value('transport_local', 0);
            frm.set_value('transport_transit', 0);

        } else if (frm.doc.requested_service == "Border Clearance") {
            frm.set_value('export_local', 0);
            frm.set_value('export_transit', 0);
            frm.set_value('import_local', 0);
            frm.set_value('import_transit', 0);
            frm.set_value('transport_local', 0);
            frm.set_value('transport_transit', 0);
        } else if (frm.doc.requested_service == "Transport-Transit") {
            frm.set_value('export_local', 0);
            frm.set_value('export_transit', 0);
            frm.set_value('import_local', 0);
            frm.set_value('import_transit', 0);
            frm.set_value('border_clearance', 0);
            frm.set_value('transport_local', 0);
        } else if (frm.doc.requested_service == "Transport-Local") {
            frm.set_value('export_local', 0);
            frm.set_value('export_transit', 0);
            frm.set_value('import_local', 0);
            frm.set_value('import_transit', 0);
            frm.set_value('border_clearance', 0);
            frm.set_value('transport_transit', 0);
        }
    },




    requested_service: function (frm) {
        frm.events.services_selection(frm);
        frm.events.hide_show_sections(frm);
    },

    import_transit: function (frm) {
        frm.events.services_selection(frm);
        frm.events.hide_show_sections(frm);
    },

    import_local: function (frm) {
        frm.events.services_selection(frm);
        frm.events.hide_show_sections(frm);
    },

    export_transit: function (frm) {
        frm.events.services_selection(frm);
        frm.events.hide_show_sections(frm);
    },

    export_local: function (frm) {
        frm.events.services_selection(frm);
        frm.events.hide_show_sections(frm);
    },

    transport_transit: function (frm) {
        frm.events.services_selection(frm);
        frm.events.hide_show_sections(frm);
    },

    transport_local: function (frm) {
        frm.events.services_selection(frm);
        frm.events.hide_show_sections(frm);
    },



    border_clearance: function (frm) {
        //Set number of borders to 2 and allow user to edit
        frm.set_value('number_of_borders', 1);
        frm.toggle_enable('number_of_borders', 1);
        frm.events.services_selection(frm);
        frm.events.hide_show_sections(frm);
    },

    /*hide_show_sections: function (frm) {
        frm.toggle_display('section_import_reference', (frm.doc.import_transit || frm.doc.import_local));
        frm.toggle_display('section_export_reference', (frm.doc.export_transit || frm.doc.export_local));
        frm.toggle_display('section_transport_reference', (!frm.doc.export_transit && !frm.doc.export_local && !frm.doc.import_local && !frm.doc.import_transit) &&
            (frm.doc.transport_local || frm.doc.transport_transit));
        frm.toggle_display('section_border_clearance', (frm.doc.border_clearance));
        frm.toggle_display("section_requested_funds", (frm.doc.import_reference || frm.doc.export_reference || frm.doc.transport_reference));
        frm.toggle_display("section_expenses", (frm.doc.requested_funds && frm.doc.requested_funds.length > 0));
    },*/

    hide_show_sections: function (frm) {
        frm.toggle_display('section_import_reference', (frm.doc.requested_service == "Importation-Transit" || frm.doc.requested_service == "Importation-Local"));
        frm.toggle_display('section_export_reference', (frm.doc.requested_service == "Export-Transit" || frm.doc.requested_service == "Export-Local"));
        frm.toggle_display('section_cross_border_reference', (frm.doc.requested_service == "Border Processing"));
        frm.toggle_display('section_transport_reference', (!(frm.doc.requested_service == "Export-Transit") && !(frm.doc.requested_service == "Export-Local") && !(frm.doc.requested_service == "Importation-Local") && !(frm.doc.requested_service == "Importation-Transit") &&
            (frm.doc.requested_service == "Transport-Local" || frm.doc.requested_service == "Transport-Transit")));
        frm.toggle_display('section_border_clearance', (frm.doc.requested_service == "Border Clearance"));
        frm.toggle_display("section_requested_funds", (frm.doc.import_reference || frm.doc.export_reference || frm.doc.transport_reference));
        frm.toggle_display("section_expenses", (frm.doc.requested_funds && frm.doc.requested_funds.length > 0));
    },

    new_fund_request: function (frm) {
        var new_request = false
        if (frm.doc.requested_funds && frm.doc.requested_funds.length > 0) {
            frm.doc.requested_funds.forEach(function (row) {
                if (row.request_status == "open") {
                    new_request = true
                }
            })
            if (new_request == true) {
                frappe.call({
                    method: "erpnext.accounts.doctype.requested_payments.requested_payments.request_funds",
                    args: {
                        reference_doctype: "Files",
                        reference_docname: cur_frm.doc.name,
                        company: cur_frm.doc.company
                    },
                    callback: function (data) {
                        console.log(data);
                    }
                })
            }
        }
    },

    load_expenses: function (frm) {
        if (frm.fields_dict['total_expenses_html'] && "expenses_html" in frm.doc.__onload) {
            frm.fields_dict['total_expenses_html'].wrapper.innerHTML = frm.doc.__onload.expenses_html.display;
        }
    },

    load_invoices: function (frm) {
        if (frm.fields_dict['invoices_html'] && "invoices_html" in frm.doc.__onload) {
            frm.fields_dict['invoices_html'].wrapper.innerHTML = frm.doc.__onload.invoices_html.display;
        }
    },

    load_purchase_invoices: function (frm) {
        if (frm.fields_dict['purchase_invoices_html'] && "purchase_invoices_html" in frm.doc.__onload) {
            frm.fields_dict['purchase_invoices_html'].wrapper.innerHTML = frm.doc.__onload.purchase_invoices_html.display;
        }
    },

    load_payments: function (frm) {
        if (frm.fields_dict['payments_html'] && "payments_html" in frm.doc.__onload) {
            frm.fields_dict['payments_html'].wrapper.innerHTML = frm.doc.__onload.payments_html.display;
        }
    },

    make_sales_invoice: function () {
        frappe.model.open_mapped_doc({
            //method: "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
            method: "csf_tz.clearing_and_forwarding.doctype.files.files.make_sales_invoice",
            frm: cur_frm,

        })
    },

    make_purchase_invoice: function () {
        frappe.model.open_mapped_doc({
            method: "csf_tz.clearing_and_forwarding.doctype.files.files.make_purchase_invoice",
            frm: cur_frm
        })
    },


});

frappe.ui.form.on("Requested Funds Details", {
    before_requested_funds_remove: function (frm, doctype, name) {
        var row = frappe.get_doc(doctype, name);
        if (row.request_status != 'open') {
            msgprint(__("Error: Cannot delete a processed request."));
            throw "Error: cannot delete a processed request";
        }
    },
});
