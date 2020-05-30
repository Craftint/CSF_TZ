// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors // License: GNU General Public License v3. See license.txt


frappe.ui.form.on('Container Entry', {
     onload:function(frm){
        frm.fields_dict['export_reference'].get_query = function(doc) {
            return{
                filters:[
                    ['shipping_line', '=', frm.doc.shipping_line]
                ]
            }
        }
     }

    
})

   /*on_submit:function(frm){
        console.log(frm);
        frappe.model.with_doc('Container', frm.doc.container_reference, function(){
				var reference_doc = frappe.model.get_doc('Container', frm.doc.container_reference);
            });
       //console.log(referene_doc);
       frappe.call({
				method: "csf_tz.clearing_and_forwarding.doctype.container_entry.container_entry.create_container",
				freeze: true,
				args: {
					booking_number: frm.doc.booking_number,
					collection_date: frm.doc.collection_date,
                    container_number: frm.docname,
                    container_type:frm.doctype


					
				},
				callback: function(data){
					if(!frm.doc.container_reference)
					{
						frm.set_value('container_reference', data.message);
						frm.save();
					}
				}
			})
       
    }*/
   
   
    
    
    
//} )  