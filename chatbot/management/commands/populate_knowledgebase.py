import os
import django
from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase

class Command(BaseCommand):
    help = 'Populate the KnowledgeBase with initial data'

    def handle(self, *args, **options):
        # Sample knowledge base entries
        knowledge_data = [
            {
                'question_type': 'course',
                'question_pattern': 'course information',
                'answer': 'You can find detailed course information including descriptions, prerequisites, and schedules in the official university course catalog or by contacting the academic department directly.',
                'keywords': 'course, class, information, details, description, catalog'
            },
            {
                'question_type': 'deadline',
                'question_pattern': 'registration deadline',
                'answer': 'Fall registration ends August 25th. Spring registration ends January 15th. Summer registration deadlines vary by session. Always check the official academic calendar for the most current dates.',
                'keywords': 'registration, deadline, enroll, sign up, add/drop, deadline'
            },
            {
                'question_type': 'deadline',
                'question_pattern': 'tuition payment deadline',
                'answer': 'Tuition payment is typically due two weeks before the semester starts. For Fall 2024, the deadline is August 15th. Late payments may incur fees.',
                'keywords': 'tuition, payment, fee, deadline, pay, billing'
            },
            {
                'question_type': 'resource',
                'question_pattern': 'library hours',
                'answer': 'Main Library Hours:\n- Monday-Thursday: 8:00 AM - 10:00 PM\n- Friday: 8:00 AM - 8:00 PM\n- Saturday: 10:00 AM - 6:00 PM\n- Sunday: 12:00 PM - 8:00 PM\n\n24/7 study rooms are available in the Student Center with student ID.',
                'keywords': 'library, hours, open, close, study, research'
            },
            {
                'question_type': 'resource',
                'question_pattern': 'tutoring center',
                'answer': 'The Academic Success Center offers free tutoring for most subjects:\n- Location: Student Services Building, Room 201\n- Hours: Mon-Fri 9AM-7PM, Sat 10AM-2PM\n- Schedule appointments online or walk-in\n- Subjects: Math, Science, Writing, Languages, and more',
                'keywords': 'tutoring, tutor, help, academic, success, center, study'
            },
            {
                'question_type': 'resource',
                'question_pattern': 'IT support',
                'answer': 'IT Help Desk Services:\n- Phone: (555) 123-HELP\n- Email: helpdesk@university.edu\n- Location: Tech Building, Room 100\n- Hours: 24/7 phone support, in-person 8AM-6PM Mon-Fri\n- Services: Password reset, software installation, network issues',
                'keywords': 'IT, tech, computer, wifi, password, email, support, helpdesk'
            },
            {
                'question_type': 'course',
                'question_pattern': 'prerequisites',
                'answer': 'Course prerequisites are listed in the course catalog. Generally, you need to complete introductory courses before advanced ones. Some departments require minimum grades in prerequisite courses. Check with your academic advisor for specific requirements.',
                'keywords': 'prerequisites, requirements, needed, before, preparation'
            },
            {
                'question_type': 'general',
                'question_pattern': 'academic calendar',
                'answer': 'Key Academic Dates 2024-2025:\n- Fall Semester: Aug 26 - Dec 13\n- Spring Semester: Jan 13 - May 9\n- Summer Sessions: May 27 - Aug 2\n- Thanksgiving Break: Nov 27 - Dec 1\n- Spring Break: Mar 16 - Mar 23\n\nFull calendar available on the university website.',
                'keywords': 'calendar, academic, dates, schedule, break, holiday'
            },
            {
                'question_type': 'resource',
                'question_pattern': 'career services',
                'answer': 'Career Development Center Services:\n- Resume and cover letter reviews\n- Mock interviews\n- Job and internship postings\n- Career counseling\n- Career fairs (Fall: Oct 15, Spring: Feb 20)\n- Location: Career Center Building, Room 150',
                'keywords': 'career, job, internship, resume, interview, employment'
            },
            {
                'question_type': 'general',
                'question_pattern': 'financial aid',
                'answer': 'Financial Aid Office Information:\n- FAFSA Deadline: March 1st for priority consideration\n- Office Hours: Mon-Fri 8:30AM-5:00PM\n- Contact: finaid@university.edu or (555) 123-AID\n- Services: Scholarships, grants, loans, work-study programs',
                'keywords': 'financial aid, fafsa, scholarship, grant, loan, tuition, aid'
            }
        ]

        created_count = 0
        updated_count = 0

        for data in knowledge_data:
            obj, created = KnowledgeBase.objects.update_or_create(
                question_pattern=data['question_pattern'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {data["question_pattern"]}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {data["question_pattern"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated knowledge base! Created: {created_count}, Updated: {updated_count}'
            )
        )