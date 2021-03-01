// Copyright (c) 2021, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Piecework", {
  task: (frm) => setTotal(frm),
  quantity: (frm) => setTotal(frm),
  task_rate: (frm) => setTotal(frm),

  setup: (frm) => {
    frm.set_query("task", () => {
      return {
        filters: {
          disabled: 0,
        },
      };
    });
  },
});

const setTotal = (frm) => {
  const total = frm.doc.task_rate * frm.doc.quantity || 0;
  frm.set_value("total", total);
  const count = frm.doc.employees.length;
  frm.doc.employees.forEach((row) => {
    frappe.model.set_value(row.doctype, row.name, "amount", total / count);
  });
};
