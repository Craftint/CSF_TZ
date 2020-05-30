// Copyright (c) 2019, Bravo Logistics and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Inspection', {

    //function to load pre-entered checklist of inspection routine checklist
    vehicle_type: function (frm) {
        frappe.model.with_doc("Vehicle Inspection Template", frm.doc.vehicle_type, function () {
            var ref_doc = frappe.get_doc("Vehicle Inspection Template", frm.doc.vehicle_type);
            console.log(ref_doc);

            //for Lighting checklist
            if (ref_doc.lighting_checklist_details && ref_doc.lighting_checklist_details.length > 0) {

                frm.clear_table("lighting_checklist");

                ref_doc.lighting_checklist_details.forEach(function (row) {
                    var new_row = frm.add_child("lighting_checklist");
                    new_row.lighting_check_item = row.vehicle_part;
                })
            }

            //for brake system checklist
            if (ref_doc.brake_system_checklist_details && ref_doc.brake_system_checklist_details.length > 0) {

                frm.clear_table("brake_checklist");

                ref_doc.brake_system_checklist_details.forEach(function (row) {
                    var new_row = frm.add_child("brake_checklist");
                    new_row.brake_system = row.vehicle_part;
                })
            }

            //for Engine checklist
            if (ref_doc.engine_checklist_details && ref_doc.engine_checklist_details.length > 0) {

                frm.clear_table("engine_checklist");

                ref_doc.engine_checklist_details.forEach(function (row) {
                    var new_row = frm.add_child("engine_checklist");
                    new_row.engine_system = row.criteria;
                })
            }

            //for fuel system checklist
            if (ref_doc.fuel_system_checklist_details && ref_doc.fuel_system_checklist_details.length > 0) {

                frm.clear_table("fuel_system_checklist");

                ref_doc.fuel_system_checklist_details.forEach(function (row) {
                    var new_row = frm.add_child("fuel_system_checklist");
                    new_row.fuel_system = row.fuel_part;
                })
            }

            //for tire status and pressure
            if (ref_doc.tire_checklist_details && ref_doc.tire_checklist_details.length > 0) {

                frm.clear_table("tire_checklist");

                ref_doc.tire_checklist_details.forEach(function (row) {
                    var new_row = frm.add_child("tire_checklist");
                    new_row.tire_position = row.tire_part;
                })
            }
            //for power train checklist
            if (ref_doc.power_train_details && ref_doc.power_train_details.length > 0) {

                frm.clear_table("power_train_checklist");

                ref_doc.power_train_details.forEach(function (row) {
                    var new_row = frm.add_child("power_train_checklist");
                    new_row.power_train_checklist = row.power_train_part;
                })
            }

            //for electronics checklist
            if (ref_doc.electronics_details && ref_doc.electronics_details.length > 0) {

                frm.clear_table("electronics_checklist");

                ref_doc.electronics_details.forEach(function (row) {
                    var new_row = frm.add_child("electronics_checklist");
                    new_row.electronics_part = row.electronic_part;
                })
            }

            //for electrical checklist
            if (ref_doc.electrical_details && ref_doc.electrical_details.length > 0) {

                frm.clear_table("electrical_checklist");

                ref_doc.electrical_details.forEach(function (row) {
                    var new_row = frm.add_child("electrical_checklist");
                    new_row.electrical_part = row.electrical_part;
                })
            }

            //for steering checklist
            if (ref_doc.steering_details && ref_doc.steering_details.length > 0) {

                frm.clear_table("steering_checklist");

                ref_doc.steering_details.forEach(function (row) {
                    var new_row = frm.add_child("steering_checklist");
                    new_row.steering_part = row.steering_part;
                })
            }

            //for tires checklist
            if (ref_doc.tires_details && ref_doc.tires_details.length > 0) {

                frm.clear_table("tires_checklist");

                ref_doc.tires_details.forEach(function (row) {
                    var new_row = frm.add_child("tires_checklist");
                    new_row.criteria = row.criteria;
                })
            }

            //for suspension checklist
            if (ref_doc.suspension_details && ref_doc.suspension_details.length > 0) {

                frm.clear_table("suspension_checklist");

                ref_doc.suspension_details.forEach(function (row) {
                    var new_row = frm.add_child("suspension_checklist");
                    new_row.part = row.parts;
                })
            }


            //for air system/others checklist
            if (ref_doc.air_system_details && ref_doc.air_system_details.length > 0) {

                frm.clear_table("air_system_checklist");

                ref_doc.air_system_details.forEach(function (row) {
                    var new_row = frm.add_child("air_system_checklist");
                    new_row.part = row.parts;
                })
            }



        });
        frappe.after_ajax(function () {
            //list of table_names_fields from Vehicle Inspection to Update Values
            var field_lists = ["lighting_checklist", "brake_checklist", "engine_checklist", "fuel_system_checklist", "tire_checklist", "power_train_checklist", "electronics_checklist", "electrical_checklist", "steering_checklist", "tires_checklist", "suspension_checklist", "air_system_checklist"];
            field_lists.forEach(function (row) {
                frm.refresh_field(row);
            })

        })
    },
    refresh: function (frm) {


    }
});
