// Copyright (c) 2025, M&M devs and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Event Registration", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Event Registration', {
    refresh(frm) {
        toggle_fields(frm);
    },

    has_presentation(frm) {
        toggle_fields(frm);
    },

    wants_booth(frm) {
        toggle_fields(frm);
    },

    has_attendees(frm) {
        toggle_fields(frm);
    }
});

function toggle_fields(frm) {
    frm.toggle_display('presentation_file', !!frm.doc.has_presentation);
    frm.toggle_display('booth_count', !!frm.doc.wants_booth);
    frm.toggle_display('attendees', !!frm.doc.has_attendees);
}