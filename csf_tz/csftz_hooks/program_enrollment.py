from __future__ import unicode_literals
import frappe
from erpnext.education.doctype.program_enrollment.program_enrollment import ProgramEnrollment

def create_course_enrollments(self):
    frappe.msgprint("Hello overriding world!")
    student = frappe.get_doc("Student", self.student)
    program = frappe.get_doc("Program", self.program)
    course_list = [course.course for course in program.courses]
    for course_name in course_list:
        student.enroll_in_course(course_name=course_name, program_enrollment=self.name)

def create_course_enrollments_override(doc, method):
    ProgramEnrollment.create_course_enrollments = create_course_enrollments