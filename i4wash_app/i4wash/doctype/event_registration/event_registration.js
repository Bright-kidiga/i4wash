// Copyright (c) 2025, M&M devs and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Event Registration", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Event Registration', {
  has_presentation: function(frm) {
    frm.toggle_display('presentation_file', frm.doc.has_presentation === 'Yes');
  },
  wants_booth: function(frm) {
    frm.toggle_display('booth_count', frm.doc.wants_booth === 'Yes');
  },
  has_attendees: function(frm) {
    frm.toggle_display('attendees', frm.doc.has_attendees === 'Yes');
  },
  onload: function(frm) {
    frm.trigger('has_presentation');
    frm.trigger('wants_booth');
    frm.trigger('has_attendees');
  }
});
