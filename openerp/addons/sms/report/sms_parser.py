# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime

from openerp.report import report_sxw

class crossovered_analytic(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crossovered_analytic, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'get_exam_type': self.get_exam_type,
            'get_class': self.get_class,
            'get_section': self.get_section,
            'get_subject': self.get_subject,
            'get_teacher': self.get_teacher,
            'get_today_formatted':self.get_today_formatted,
            'get_today_month':self.get_today_month,
            
            'get_class_timetable': self.get_class_timetable,
            'get_teacher_timetable': self.get_teacher_timetable,
            'get_class_timetable_heading': self.get_class_timetable_heading,
            
            'get_student_signature_list': self.get_student_signature_list,
            'get_student_award_list': self.get_student_award_list,
            'get_result_list': self.get_result_list,
            'get_result_sheet': self.get_result_sheet,
            'get_students_dmc':self.get_students_dmc,
            'get_students_dmc_multiple':self.get_students_dmc_multiple,
            'get_company':self.get_company,
            'get_student_date_sheet':self.get_student_date_sheet,
        })
        self.base_amount = 0.00
    
    def get_company(self, objects):
        sql = """SELECT name from res_company where id in (SELECT cid from res_company_users_rel) order by id"""
        self.cr.execute(sql)
        company_name = self.cr.fetchone()[0]
        return company_name
    
    def get_exam_type(self,form):
        return self.pool.get('sms.exam.datesheet').browse(self.cr, self.uid,self.datas['form']['exam_type'][0]).name
        
    def get_class(self,form):
        return self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,self.datas['form']['academiccalendar_id'][0]).name
    
    def get_section(self,form):
        return self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,self.datas['form']['academiccalendar_id'][0]).section_id.name        
    
    def get_subject(self,form):
        return self.pool.get('sms.academiccalendar.subjects').browse(self.cr, self.uid,self.datas['form']['subject_id'][0]).subject_id.name
    
    def get_teacher(self,form):
        return self.pool.get('sms.academiccalendar.subjects').browse(self.cr, self.uid,self.datas['form']['subject_id'][0]).teacher_id.name
            
    def get_today_formatted(self,form):
        
        today = time.strftime('%B %d, %Y')
        return today 
    
    def get_today_month(self,form):
        today = time.strftime('%B %d, %Y')
        today = today.split(" ")[0] + ", " + today.split(" ")[2] 
        return today
     
    def get_class_timetable_heading(self, form):
        result = []
         
        if self.ids:
            print "Self.id: ", self.ids[0]
        else:
            return result
        
        day_query="""SELECT day_id, (SELECT name from sms_day where id = day_id)  
            from sms_timetable_lines where timetable_id = """ + str(self.ids[0]) + """
            group by day_id order by day_id""" 
        
        self.cr.execute(day_query)
        day_record = self.cr.fetchone()
        
        dict = {'day':'','period_1':'','period_2':'','period_3':'','period_4':'','period_5':'','period_6':'','period_7':'','period_8':'','period_9':'','period_10':''}
        dict['day'] = 'DAY/ PERIOD'
    
        query="""SELECT sms_timetable.name, (SELECT name_related from hr_employee where id = teacher_id) as name, 
            (SELECT name from sms_subject where id = (SELECT subject_id from sms_academiccalendar_subjects where id = sms_timetable_lines.subject_id)), 
            (SELECT name from sms_day where id = day_id) , type, period_break_no,
            (SELECT name from sms_timetable_slot where id = sms_timetable_lines.timetable_slot_id) as slot_name,
            (SELECT name_24 from sms_timetable_slot where id = sms_timetable_lines.timetable_slot_id) as slot_name_24
            FROM sms_timetable
            inner join sms_timetable_lines 
            on 
            sms_timetable.id = sms_timetable_lines.timetable_id
            WHERE day_id = """ + str(day_record[0]) + """ 
            AND timetable_id = """ + str(self.ids[0]) + """ order by slot_name_24"""
        
        self.cr.execute(query)
        records = self.cr.fetchall()
        
        i = 1
        for record in records:
            if record[4]  == 'Break':
                dict['period_' + str(i)] = 'Break ' + str(record[5])  + "\n" + str(record[6]).split("--")[0].split(" ")[0]
            else:        
                dict['period_' + str(i)] = 'Period ' + str(record[5]) + "\n" + str(record[6]).split("--")[0].split(" ")[0] 
            i = i + 1
                
        result.append(dict)
        return result
    
    def get_class_timetable(self, form):
        result = []
        dict = {'period_1':'','period_2':'','period_3':'','period_4':'','period_5':'','period_6':'','period_7':'','period_8':'','period_9':'','period_10':''}
        
        if self.ids:
            print "Self.id: ", self.ids[0]
        else:
            return result
        
        day_query="""SELECT day_id, (SELECT name from sms_day where id = day_id)  
            from sms_timetable_lines where timetable_id = """ + str(self.ids[0]) + """
            group by day_id order by day_id"""  
        
        self.cr.execute(day_query)
        day_records = self.cr.fetchall()
        
        for day_record in day_records:
            dict = {'day':'','period_1':'','period_2':'','period_3':'','period_4':'','period_5':'','period_6':'','period_7':'','period_8':'','period_9':'','period_10':''}
            dict['day'] = day_record[1][:3].upper()
        
            query="""SELECT sms_timetable.name, (SELECT name_related from hr_employee where id = teacher_id) as name, 
                (SELECT name from sms_subject where id = (SELECT subject_id from sms_academiccalendar_subjects where id = sms_timetable_lines.subject_id)), 
                (SELECT name from sms_day where id = day_id) , type, period_break_no,
                (SELECT name from sms_timetable_slot where id = sms_timetable_lines.timetable_slot_id) as slot_name,
                (SELECT name_24 from sms_timetable_slot where id = sms_timetable_lines.timetable_slot_id) as slot_name_24
                FROM sms_timetable
                inner join sms_timetable_lines 
                on 
                sms_timetable.id = sms_timetable_lines.timetable_id
                WHERE day_id = """ + str(day_record[0]) + """ 
                AND timetable_id = """ + str(self.ids[0]) + """ order by slot_name_24"""
            
            self.cr.execute(query)
            records = self.cr.fetchall()
            
            i = 1
            for record in records:
                if record[4]  == 'Break':
                    dict['period_' + str(i)] = str(record[4]) + " " + str(record[5])
                else:        
                    dict['period_' + str(i)] = str(record[2]) + "\n(" + str(record[1]) + ")"
                i = i + 1
                
            result.append(dict)
        return result
    
    def get_teacher_timetable(self, form):
        result1 = []
        
        if self.ids:
            print "Self.id: ", self.ids[0]
        else:
            return result1
        
        teacher_query="""SELECT teacher_id, (SELECT name_related from hr_employee where id = teacher_id) as name
            FROM sms_timetable_lines 
            where type = 'Period' group by teacher_id""" 
        
        self.cr.execute(teacher_query)
        teacher_records = self.cr.fetchall()
        
        for teacher_record in teacher_records:
        
            dict1 = {'day':'','period_1':'','period_2':'','period_3':'','period_4':'','period_5':'','period_6':'','period_7':'','period_8':'','period_9':'','period_10':'', 'teacher_name':'','record':''}
            result2 = [] 
            
            #########################
            day_query="""SELECT day_id, (SELECT name from sms_day where id = day_id)  
            from sms_timetable_lines where timetable_id = """ + str(self.ids[0]) + """
            group by day_id order by day_id""" 
        
            self.cr.execute(day_query)
            day_record = self.cr.fetchone()
            
            dict1 = {'day':'','period_1':'','period_2':'','period_3':'','period_4':'','period_5':'','period_6':'','period_7':'','period_8':'','period_9':'','period_10':''}
            dict1['day'] = 'DAY/ PERIOD'
        
            query="""SELECT sms_timetable.name, (SELECT name_related from hr_employee where id = teacher_id) as name, 
                (SELECT name from sms_subject where id = (SELECT subject_id from sms_academiccalendar_subjects where id = sms_timetable_lines.subject_id)), 
                (SELECT name from sms_day where id = day_id) , type, period_break_no,
                (SELECT name from sms_timetable_slot where id = sms_timetable_lines.timetable_slot_id) as slot_name,
                (SELECT name_24 from sms_timetable_slot where id = sms_timetable_lines.timetable_slot_id) as slot_name_24
                FROM sms_timetable
                inner join sms_timetable_lines 
                on 
                sms_timetable.id = sms_timetable_lines.timetable_id
                WHERE day_id = """ + str(day_record[0]) + """ 
                AND timetable_id = """ + str(self.ids[0]) + """ order by slot_name_24"""
            
            self.cr.execute(query)
            records = self.cr.fetchall()
            
            i = 1
            for record in records:
                dict1['period_' + str(i)] = 'Period ' + str(record[5]) + "\n" + str(record[6]).split("--")[0].split(" ")[0] 
                i = i + 1
                
            ######################################
            
            day_query="""SELECT day_id, (SELECT name from sms_day where id = day_id)
                from sms_timetable_lines group by day_id order by day_id""" 
            
            self.cr.execute(day_query)
            day_records = self.cr.fetchall()
            
            for day_record in day_records:
                dict2 = {'day':'',
                         'period_1':'---','period_2':'---','period_3':'---','period_4':'---','period_5':'---','period_6':'---','period_7':'---','period_8':'---','period_9':'---','period_10':'---',
                         'alias_1':'','alias_2':'','alias_3':'','alias_4':'','alias_5':'','alias_6':'','alias_7':'','alias_8':'','alias_9':'','alias_10':'',
                         'script_1':'','script_2':'','script_3':'','script_4':'','script_5':'','script_6':'','script_7':'','script_8':'','script_9':'','script_10':'',}
                
                dict2['day'] = day_record[1][:3].upper()
            
                query="""SELECT sms_timetable.name, (SELECT name_related from hr_employee where id = teacher_id) as name, 
                    (SELECT name from sms_subject where id = (SELECT subject_id from sms_academiccalendar_subjects where id = sms_timetable_lines.subject_id)), 
                    (SELECT name from sms_day where id = day_id) , type, period_break_no, alias, script
                    FROM sms_timetable
                    inner join sms_timetable_lines 
                    on 
                    sms_timetable.id = sms_timetable_lines.timetable_id
                    inner join sms_academiccalendar 
                    on 
                    sms_academiccalendar.id = sms_timetable.academic_id
                    inner join sms_classes 
                    on 
                    sms_classes.id = sms_academiccalendar.class_id
                    WHERE teacher_id = """ + str(teacher_record[0]) + """  
                    AND day_id = """ + str(day_record[0]) + """ order by day_id"""
                
                self.cr.execute(query)
                records = self.cr.fetchall()
                
                i = 1
                for record in records:
                    dict2['period_' + str(record[5])] = str(record[2])
                    dict2['alias_' + str(record[5])] = " (" + str(record[6]) + ")"
                    if record[7] != None:
                        dict2['alias_' + str(record[5])] = " (" + str(record[6]) 
                        dict2['script_' + str(record[5])] = str(record[7]) + ")" 
                    i = i + 1
                
                result2.append(dict2)
            dict1['teacher_name'] = teacher_record[1]
            dict1['record'] = result2
            
            result1.append(dict1)
        return result1
    
    def get_student_signature_list(self,form):
        result = []
        
        list_type = str(form['list_type'])
        academiccalendar_id = str(form['academiccalendar_id'][0])
        subject_id = str(form['subject_id'][0])
        exam_type = str(form['exam_type'][0])
        
        
        students_sql = """SELECT sms_student.name, sms_student.father_name, sms_student.registration_no, 
            sms_student_subject.id, sms_student_subject.subject_status, sms_academiccalendar_student.id
            from sms_student 
            inner join sms_academiccalendar_student
            on sms_student.id = sms_academiccalendar_student.std_id
            inner join sms_student_subject
            on
            sms_academiccalendar_student.id = sms_student_subject.student 
            where sms_student_subject.subject = """ + str(subject_id) + """ 
            and sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
            and sms_student.state = 'Admitted'
            and sms_academiccalendar_student.state = 'Current'
            ORDER BY sms_student.name, sms_student.father_name"""
        
        self.cr.execute(students_sql)
        students_rows = self.cr.fetchall()
        
        k = 1
        for students_row in students_rows:
            my_dict = {'SNO':'','reg_no':'','name':'', 'father_name':'', 'signature':'', 'remarks':''}
        
            reg_no = students_row[2] 
            student_names = students_row[0] 
            father_name =  students_row[1]
            
            my_dict["reg_no"] = reg_no
            my_dict["name"] = student_names
            my_dict["father_name"] = father_name
            my_dict["SNO"] = k
            my_dict["remarks"] = ''
            
            k = k + 1
            result.append(my_dict)
        
        return result
    
    def get_student_award_list(self,form):
        result = []
        
        list_type = str(form['list_type'])
        academiccalendar_id = str(form['academiccalendar_id'][0])
        subject_id = str(form['subject_id'][0])
        exam_type = str(form['exam_type'][0])
        
        
        students_sql = """SELECT sms_student.name, sms_student.father_name, sms_student.registration_no, 
            sms_student_subject.id, sms_student_subject.subject_status, sms_academiccalendar_student.id
            from sms_student 
            inner join sms_academiccalendar_student
            on sms_student.id = sms_academiccalendar_student.std_id
            inner join sms_student_subject
            on
            sms_academiccalendar_student.id = sms_student_subject.student 
            where sms_student_subject.subject = """ + str(subject_id) + """ 
            and sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
            and sms_student.state = 'Admitted'
            and sms_academiccalendar_student.state = 'Current'
            ORDER BY subject_status, sms_student.name, sms_student.father_name"""
        
        self.cr.execute(students_sql)
        students_rows = self.cr.fetchall()
        
        k = 1
        for students_row in students_rows:
            my_dict = {'SNO':'','reg_no':'','name':'', 'father_name':'', 'marks':'', 'remarks':''}
        
            reg_no = students_row[2] 
            student_names = students_row[0] 
            father_name =  students_row[1]
         
            my_dict["reg_no"] = reg_no
            my_dict["name"] = student_names
            my_dict["father_name"] = father_name
            my_dict["SNO"] = k
            my_dict["remarks"] = ''
            
            k = k + 1
            result.append(my_dict)
        
        return result
    
    
    def get_result_list(self,form):
    
        result = []
        
        list_type = str(form['list_type'])
        academiccalendar_id = str(form['academiccalendar_id'][0])
        #subject_id = str(form['subject_id'][0])
        exam_type = str(form['exam_type'][0])
        
        order_by = str(form['order_by'])
          
        if academiccalendar_id:
            students_in_acad_cal_sql = """SELECT sms_student.name, sms_student.father_name, sms_student.registration_no, sms_student.id, 
                sum(obtained_marks) as marks,sum(total_marks),(sum(obtained_marks)/sum(total_marks))*100 AS percentage
                from sms_student 
                inner join sms_academiccalendar_student
                on sms_student.id = sms_academiccalendar_student.std_id
                inner join sms_student_subject
                on sms_academiccalendar_student.id = sms_student_subject.student
                inner join sms_exam_lines
                on sms_student_subject.id = sms_exam_lines.student_subject
                where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                and sms_student.state = 'Admitted'
                and sms_exam_lines.name =  """ + str(exam_type) + """
                group by sms_student.name, sms_student.father_name, sms_student.registration_no, sms_student.id
                order by """ + order_by + """, sms_student.name, sms_student.father_name"""    

            self.cr.execute(students_in_acad_cal_sql)
            students_acad_cal_rows = self.cr.fetchall()
            
            k = 1
            for rec1 in students_acad_cal_rows:
                
                my_dict1 = {'SNO':'', 'reg_no':'','name':'', 'marks':'','total_marks':'', 'percentage':'', 'remarks':''}
                my_dict1["SNO"] = k
                my_dict1["name"] = rec1[0]
                my_dict1["reg_no"] = rec1[2]
                
                if rec1[4]:
                    my_dict1["marks"] = '%.2f' % round(rec1[4],2)
                else:
                    my_dict1["marks"] = 0
                    
                if rec1[5]:
                    my_dict1["total_marks"] = '%.2f' % round(rec1[5],2)
                else:
                    my_dict1["total_marks"] = 0
                
                if rec1[6]:
                    my_dict1["percentage"] = '%.2f' % round(rec1[6],2)
                else:
                    my_dict1["percentage"] = 0
                my_dict1["remarks"] = ''
                
                k = k + 1
                result.append(my_dict1)
                
        return result

    def get_result_sheet(self,form):
    
        result = []
        
        list_type = str(form['list_type'])
        academiccalendar_id = str(form['academiccalendar_id'][0])
        #subject_id = str(form['subject_id'][0])
        exam_type = str(form['exam_type'][0])
        
        order_by = str(form['order_by'])
          
        if academiccalendar_id:
            students_in_acad_cal_sql = """SELECT sms_student.name, sms_student.father_name, sms_student.registration_no, sms_student.id, 
                sum(obtained_marks) as marks,sum(total_marks),(sum(obtained_marks)/sum(total_marks))*100 as percentage, sms_academiccalendar_student.id
                from sms_student 
                inner join sms_academiccalendar_student
                on sms_student.id = sms_academiccalendar_student.std_id
                inner join sms_student_subject
                on sms_academiccalendar_student.id = sms_student_subject.student
                inner join sms_exam_lines
                on sms_student_subject.id = sms_exam_lines.student_subject
                where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                and sms_student.state = 'Admitted'
                and sms_exam_lines.name =  """ + str(exam_type) + """
                group by sms_student.name, sms_student.father_name, sms_student.registration_no, sms_student.id, sms_academiccalendar_student.id
                order by """ + order_by + """, sms_student.name, sms_student.father_name"""    

            self.cr.execute(students_in_acad_cal_sql)
            students_acad_cal_rows = self.cr.fetchall()
            
            k = 1
            subject_sql = """SELECT sms_academiccalendar_subjects.id, sms_subject.name
                from sms_academiccalendar_subjects
                inner join sms_subject on
                sms_subject.id = sms_academiccalendar_subjects.subject_id
                where sms_academiccalendar_subjects.academic_calendar = """ + str(academiccalendar_id) + """ 
                and sms_academiccalendar_subjects.offered_as != 'practical'
                order by sms_subject.name"""
                
            self.cr.execute(subject_sql)
            subject_rows = self.cr.fetchall()
            my_dict1 = {'SNO':'S.No', 'reg_no':'Admission No','name':'Name','subject_1':'','subject_2':'','subject_3':'','subject_4':'','subject_5':'','subject_6':'',
                        'subject_7':'','subject_8':'','subject_9':'','subject_10':'', 'marks':'Marks Obtained','total_marks':'Total Marks', 'percentage':'%age', 'position':'Position'}
            
            count = 1
            for subject_row in subject_rows:
                my_dict1['subject_' + str(count)] = subject_row[1] 
                count = count + 1
            
            result.append(my_dict1)
            
            
            for rec1 in students_acad_cal_rows:
                
                my_dict1 = {'SNO':'S.No', 'reg_no':'Admission No','name':'Name','subject_1':'','subject_2':'','subject_3':'','subject_4':'','subject_5':'','subject_6':'',
                            'subject_7':'','subject_8':'','subject_9':'','subject_10':'', 'marks':'Marks Obtained','total_marks':'Total Marks', 'percentage':'%age', 'position':''}
                
                if rec1[4] == None:
                    continue
                pos_sql = """SELECT count(marks) from (SELECT 
                    (SELECT sum(obtained_marks) from sms_exam_lines where student_subject in 
                    (SELECT id from sms_student_subject where  student in 
                    (SELECT id from sms_academiccalendar_student where std_id = sms_student.id))
                    and sms_exam_lines.name = """ + str(exam_type) + """) as marks
                    from sms_student 
                    inner join sms_academiccalendar_student
                    on sms_student.id = sms_academiccalendar_student.std_id
                    where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted')a
                    where marks > """ + str(rec1[4])
                    
                self.cr.execute(pos_sql)
                my_dict1["position"] = self.cr.fetchone()[0] + 1
                
                count = 1
                for subject_row in subject_rows:
                    marks_sql = """SELECT obtained_marks, sms_student_subject.id, exam_status from sms_exam_lines 
                        inner join sms_student_subject
                        on sms_student_subject.id = sms_exam_lines.student_subject
                        where sms_student_subject.student = """ + str(rec1[7]) + """
                        and sms_exam_lines.name = """ + str(exam_type) + """
                        and sms_student_subject.subject = """ + str(subject_row[0])
                    
                    self.cr.execute(marks_sql)
                    marks_rows = self.cr.fetchone()
                    
                    if marks_rows:
                        marks_pract_sql = """SELECT obtained_marks from sms_exam_lines 
                            inner join sms_student_subject
                            on sms_student_subject.id = sms_exam_lines.student_subject
                            where reference_practical_of = """ + str(marks_rows[1])
                            
                        self.cr.execute(marks_pract_sql)
                        marks_prac_rows = self.cr.fetchone()
                        
                        if marks_rows[2] != 'Present':
                            my_dict1['subject_' + str(count)] = marks_rows[2]
                        elif marks_prac_rows:
                            my_dict1['subject_' + str(count)] = str(marks_rows[0] + marks_prac_rows[0])
                        else:
                            my_dict1['subject_' + str(count)] = str(marks_rows[0])
                    else:
                        my_dict1['subject_' + str(count)] = 0 
                                                  
                    count = count + 1
                        
                my_dict1["SNO"] = k
                my_dict1["name"] = rec1[0]
                my_dict1["reg_no"] = rec1[2]
                my_dict1["marks"] = '%.2f' % round(rec1[4],2)
                my_dict1["total_marks"] = '%.2f' % round(rec1[5],2)
                my_dict1["percentage"] = '%.2f' % round(rec1[6],2)
                
                k = k + 1
                result.append(my_dict1)
                
        return result

    def get_students_dmc(self,form):
        
        final_result = []
        subjects = []

        dmc_type = str(form['dmc_type'])
        academiccalendar_id = str(form['academiccalendar_id'][0])
        exam_type = str(form['exam_type'][0])
        
        student_query = ""
        if dmc_type == 'Single_DMC':
            student = str(form['student_id'][0])
            student_query = "AND sms_student.id = " + str(student)
           
        student_sql = """SELECT distinct sms_student.id, sms_student.name, sms_student.father_name, sms_student.current_class from sms_student
                    inner join sms_academiccalendar_student on
                    sms_student.id = sms_academiccalendar_student.std_id 
                    inner join sms_student_subject
                    on sms_academiccalendar_student.id = sms_student_subject.student
                    inner join sms_exam_lines
                    on sms_student_subject.id = sms_exam_lines.student_subject
                    WHERE sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted'
                    """ + str(student_query) + """
                    ORDER BY  sms_student.name, sms_student.father_name"""
        
        self.cr.execute(student_sql)
        student_rows = self.cr.fetchall()
        
        for row in student_rows:
            student_id = row[0]
            result = []
            current_class = row[3]
            class_id = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,current_class).class_id.id
            sql = """SELECT min(upper_limit) from sms_grading_scheme_line
                inner join sms_grading_scheme on 
                sms_grading_scheme.id = sms_grading_scheme_line.grading_scheme
                where class_id = """ + str(class_id)
            self.cr.execute(sql)
            lower_grade = self.cr.fetchone()[0]
            
            std_subs_sql = """SELECT sms_subject.name, sms_exam_lines.obtained_marks, sms_exam_lines.total_marks, 
                sms_academiccalendar_subjects.offered_as, sms_student_subject.id, sms_exam_lines.exam_status 
                from sms_exam_lines 
                inner join sms_student_subject 
                on 
                sms_student_subject.id = sms_exam_lines.student_subject 
                inner join sms_academiccalendar_student 
                on 
                sms_academiccalendar_student.id = sms_student_subject.student
                inner join sms_academiccalendar_subjects 
                on 
                sms_academiccalendar_subjects.id = sms_student_subject.subject
                inner join sms_subject 
                on 
                sms_subject.id = sms_academiccalendar_subjects.subject_id
                where sms_academiccalendar_student.std_id = """ + str(student_id) + """
                and sms_exam_lines.name =  """ + str(exam_type) + """
                and sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                and sms_academiccalendar_subjects.reference_practical_of is null"""
            
            self.cr.execute(std_subs_sql)
            std_subs_rows = self.cr.fetchall()
            
            s_no = 1
            total_obatined_marks = 0.0;
            class_total_marks = 0.0
            count_fail = 0
            
            empty_lines = "..\n.\n.\n.\n.\n."
            
            for std_subs_row in std_subs_rows:
                empty_lines = empty_lines.replace("..\n", ".")
                my_dict = {'s_no':'','title':'', 'theory':'', 'practical':'', 'obtained_marks':0,'total_marks':'','percentage':''}
                practical_marks = 0.0
                practical_total = 0.0
                practical_rows = None
                
                if std_subs_row[3] == 'theory_practical':
                    practical_sql = """SELECT sms_subject.name, sms_exam_lines.obtained_marks, sms_exam_lines.total_marks, 
                        sms_academiccalendar_subjects.offered_as, sms_student_subject.id,sms_exam_lines.exam_status 
                        from sms_exam_lines 
                        inner join sms_student_subject 
                        on 
                        sms_student_subject.id = sms_exam_lines.student_subject 
                        inner join sms_academiccalendar_student 
                        on 
                        sms_academiccalendar_student.id = sms_student_subject.student
                        inner join sms_academiccalendar_subjects 
                        on 
                        sms_academiccalendar_subjects.id = sms_student_subject.subject
                        inner join sms_subject 
                        on 
                        sms_subject.id = sms_academiccalendar_subjects.subject_id
                        where sms_academiccalendar_student.std_id = """ + str(student_id) + """
                        and sms_exam_lines.name =  """ + str(exam_type) + """
                        and sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                        and sms_academiccalendar_subjects.reference_practical_of is not null
                        and sms_student_subject.reference_practical_of = """ + str(std_subs_row[4])
            
                    self.cr.execute(practical_sql)
                    practical_rows = self.cr.fetchone()
                    if practical_rows:
                        practical_marks = practical_rows[1]
                        practical_total = practical_rows[2]
                
                my_dict["s_no"] = s_no
                my_dict["title"] = std_subs_row[0]
                
                if std_subs_row[5] != 'Present':
                    my_dict['theory'] = std_subs_row[5]
                else:
                    my_dict["theory"] = str(round(std_subs_row[1],2))
                
                if std_subs_row[3] == 'theory_practical':
                    if practical_rows:
                        if practical_rows[5] != 'Present':
                            my_dict['practical'] = practical_rows[5]
                        else:
                            my_dict["practical"] = str(round(practical_marks,2))
                else:
                    my_dict["practical"] = practical_marks
                
                my_dict["obtained_marks"] = str(round(std_subs_row[1] + practical_marks, 2))
                my_dict["total_marks"] = round(std_subs_row[2] + practical_total, 2)
                
                if (std_subs_row[2]+practical_total) == 0:
                    obt_percentage = 0
                else:
                    obt_percentage = round(( (std_subs_row[1]+practical_marks) / (std_subs_row[2]+practical_total) ) * 100,2)
                my_dict["percentage"] = str(obt_percentage)
                
                if obt_percentage <= lower_grade:
                    count_fail = count_fail + 1  
                result.append(my_dict)
                
                total_obatined_marks = total_obatined_marks + std_subs_row[1] + practical_marks
                class_total_marks = class_total_marks + std_subs_row[2] + practical_total
                
                s_no = s_no + 1
            
            final_dict = {'empty_lines':'','result':'','total_students':'','position':'','grade':'','remarks':'','student_class_status':'','cadidate_no':'','student_name':'','father_name':'','gender':'','total_obtained_marks':'','total_obtained_percentage':''}
            
            sql = """SELECT sms_student.registration_no, sms_student.name, 
                sms_student.father_name, sms_student.gender from sms_student
                inner join sms_academiccalendar_student on
                sms_student.id = sms_academiccalendar_student.std_id 
                WHERE sms_student.id = """ + str(student_id) + """
                AND sms_academiccalendar_student.name = """ + str(academiccalendar_id)
                    
            self.cr.execute(sql)
            row= self.cr.fetchone()
            if row:
                final_dict['empty_lines'] = empty_lines
                final_dict['result'] = result
                final_dict['cadidate_no'] = row[0]
                final_dict['student_name'] = row[1]
                final_dict['father_name'] = row[2]
                final_dict['total_obtained_marks'] =  round(total_obatined_marks,2)
                final_dict['class_total_marks'] =  round(class_total_marks,2)
                if class_total_marks == 0:
                    percentage = 0
                else:
                    percentage = round((total_obatined_marks/class_total_marks) * 100,2)
                    
                final_dict['total_obtained_percentage'] = percentage
                
                if count_fail < 3:
                    final_dict['student_class_status'] = 'Pass'
                else:
                    final_dict['student_class_status'] = 'Fail'
                
                sql = """SELECT sms_grading_scheme_line.name, sms_grading_scheme_line.subject_remarks
                    FROM sms_grading_scheme_line 
                    inner join sms_grading_scheme on 
                    sms_grading_scheme.id = sms_grading_scheme_line.grading_scheme
                    WHERE FLOOR(""" + str(percentage) + """) between sms_grading_scheme_line.lower_limit AND sms_grading_scheme_line.upper_limit
                    AND class_id  = (SELECT class_id from sms_academiccalendar where id = """ + str(academiccalendar_id) + """)"""
                
                self.cr.execute(sql)
                grading_row = self.cr.fetchone()
        
                final_dict['grade'] = grading_row[0]
                final_dict['remarks'] = grading_row[1]
                
                sql = """SELECT count(marks) from (SELECT 
                    (SELECT sum(obtained_marks) from sms_exam_lines where student_subject in 
                    (SELECT id from sms_student_subject where  student in 
                    (SELECT id from sms_academiccalendar_student where std_id = sms_student.id))
                    and sms_exam_lines.name = """ + str(exam_type) + """) as marks
                    from sms_student 
                    inner join sms_academiccalendar_student
                    on sms_student.id = sms_academiccalendar_student.std_id
                    where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted')a
                    where marks > """ + str(total_obatined_marks)
                
                self.cr.execute(sql)
                final_dict['position'] = self.cr.fetchone()[0] + 1

                sql = """SELECT count(marks) from (SELECT 
                    (SELECT sum(obtained_marks) from sms_exam_lines where student_subject in 
                    (SELECT id from sms_student_subject where  student in 
                    (SELECT id from sms_academiccalendar_student where std_id = sms_student.id))
                    and sms_exam_lines.name = """ + str(exam_type) + """) as marks
                    from sms_student 
                    inner join sms_academiccalendar_student
                    on sms_student.id = sms_academiccalendar_student.std_id
                    where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted')a"""
                
                self.cr.execute(sql)
                final_dict['total_students'] = self.cr.fetchone()[0]
                
                my_dict = {'s_no':'','title':'', 'theory':'', 'practical':'', 'obtained_marks':0,'total_marks':'','percentage':''}
               
                my_dict = {'s_no':'Total','title':'', 'theory':'', 'practical':'', 'obtained_marks':round(total_obatined_marks,2),
                           'total_marks':round(class_total_marks,2),'percentage':percentage}
                result.append(my_dict)
            

                if row[3]=='Male':
                    final_dict['gender'] = 'S/o'
                else:
                    final_dict['gender'] = 'D/o'
                
            final_result.append(final_dict)
            
        return final_result

    def get_students_dmc_multiple(self,form):
        
        final_result = []
        report_type = str(form['report_type'])
        academiccalendar_id = form['academiccalendar_id'][0]
        #exam_type = str(form['exam_type'][0])
        
        student_query = ""
        if report_type == 'Single_Report':
            student = str(form['student_id'][0])
            student_query = "AND sms_student.id = " + str(student)
           
        student_sql = """SELECT distinct sms_student.id, sms_student.name, sms_student.father_name, sms_student.current_class from sms_student
                    inner join sms_academiccalendar_student on
                    sms_student.id = sms_academiccalendar_student.std_id 
                    inner join sms_student_subject
                    on sms_academiccalendar_student.id = sms_student_subject.student
                    inner join sms_exam_lines
                    on sms_student_subject.id = sms_exam_lines.student_subject
                    WHERE sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted'
                    """ + str(student_query) + """
                    ORDER BY  sms_student.name, sms_student.father_name"""
        
        self.cr.execute(student_sql)
        student_rows = self.cr.fetchall()
        
        for row in student_rows:
            exam_result = []
            
            student_id = row[0]
            current_class = row[3]
            class_id = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,current_class).class_id.id
            sql = """SELECT min(upper_limit) from sms_grading_scheme_line
                inner join sms_grading_scheme on 
                sms_grading_scheme.id = sms_grading_scheme_line.grading_scheme
                where class_id = """ + str(class_id)
            self.cr.execute(sql)
            lower_grade = self.cr.fetchone()[0]
            
            exam_ids = self.pool.get('sms.exam.datesheet').search(self.cr, self.uid,[('academiccalendar','=',academiccalendar_id)], order='start_date asc')
            exam_objs = self.pool.get('sms.exam.datesheet').browse(self.cr, self.uid,exam_ids)
          
            for exam_obj in exam_objs:
                subject_result = []
                    
                std_subs_sql = """SELECT sms_subject.name, sms_exam_lines.obtained_marks, sms_exam_lines.total_marks, 
                    sms_academiccalendar_subjects.offered_as, sms_student_subject.id, sms_exam_lines.exam_status 
                    from sms_exam_lines 
                    inner join sms_student_subject 
                    on 
                    sms_student_subject.id = sms_exam_lines.student_subject 
                    inner join sms_academiccalendar_student 
                    on 
                    sms_academiccalendar_student.id = sms_student_subject.student
                    inner join sms_academiccalendar_subjects 
                    on 
                    sms_academiccalendar_subjects.id = sms_student_subject.subject
                    inner join sms_subject 
                    on 
                    sms_subject.id = sms_academiccalendar_subjects.subject_id
                    where sms_academiccalendar_student.std_id = """ + str(student_id) + """
                    and sms_exam_lines.name =  """ + str(exam_obj.id) + """
                    and sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_academiccalendar_subjects.reference_practical_of is null"""
                
                self.cr.execute(std_subs_sql)
                std_subs_rows = self.cr.fetchall()
                
                s_no = 1
                total_obatined_marks = 0.0;
                class_total_marks = 0.0
                count_fail = 0
                
                for std_subs_row in std_subs_rows:
                    sub_dict = {'s_no':'','title':'', 'theory':'', 'practical':'', 'obtained_marks':0,'total_marks':'','percentage':''}
                    practical_marks = 0.0
                    practical_total = 0.0
                    practical_rows = None
                    
                    if std_subs_row[3] == 'theory_practical':
                        practical_sql = """SELECT sms_subject.name, sms_exam_lines.obtained_marks, sms_exam_lines.total_marks, 
                            sms_academiccalendar_subjects.offered_as, sms_student_subject.id,sms_exam_lines.exam_status 
                            from sms_exam_lines 
                            inner join sms_student_subject 
                            on 
                            sms_student_subject.id = sms_exam_lines.student_subject 
                            inner join sms_academiccalendar_student 
                            on 
                            sms_academiccalendar_student.id = sms_student_subject.student
                            inner join sms_academiccalendar_subjects 
                            on 
                            sms_academiccalendar_subjects.id = sms_student_subject.subject
                            inner join sms_subject 
                            on 
                            sms_subject.id = sms_academiccalendar_subjects.subject_id
                            where sms_academiccalendar_student.std_id = """ + str(student_id) + """
                            and sms_exam_lines.name =  """ + str(exam_obj.id) + """
                            and sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                            and sms_academiccalendar_subjects.reference_practical_of is not null
                            and sms_student_subject.reference_practical_of = """ + str(std_subs_row[4])
                
                        self.cr.execute(practical_sql)
                        practical_rows = self.cr.fetchone()
                        if practical_rows:
                            practical_marks = practical_rows[1]
                            practical_total = practical_rows[2]
                    
                    sub_dict["s_no"] = s_no
                    sub_dict["title"] = std_subs_row[0]
                    
                    if std_subs_row[5] != 'Present':
                        sub_dict['theory'] = std_subs_row[5]
                    else:
                        sub_dict["theory"] = str(round(std_subs_row[1],2))
                    
                    if std_subs_row[3] == 'theory_practical':
                        if practical_rows:
                            if practical_rows[5] != 'Present':
                                sub_dict['practical'] = practical_rows[5]
                            else:
                                sub_dict["practical"] = str(round(practical_marks,2))
                    else:
                        sub_dict["practical"] = practical_marks
                    
                    sub_dict["obtained_marks"] = str(round(std_subs_row[1] + practical_marks, 2))
                    sub_dict["total_marks"] = round(std_subs_row[2] + practical_total, 2)
                    
                    if (std_subs_row[2]+practical_total) == 0:
                        obt_percentage = 0
                    else:
                        obt_percentage = round(( (std_subs_row[1]+practical_marks) / (std_subs_row[2]+practical_total) ) * 100,2)
                    sub_dict["percentage"] = str(obt_percentage)
                    
                    if obt_percentage <= lower_grade:
                        count_fail = count_fail + 1  
                    subject_result.append(sub_dict)
                    
                    total_obatined_marks = total_obatined_marks + std_subs_row[1] + practical_marks
                    class_total_marks = class_total_marks + std_subs_row[2] + practical_total
                    
                    s_no = s_no + 1
                
                exam_dict = {'subject_result':'','total_students':'','position':'','grade':'','remarks':'','student_class_status':'','total_obtained_marks':'','total_obtained_percentage':'','class_total_marks':'','exam_name':''}
                exam_dict['subject_result'] = subject_result
                exam_dict['total_obtained_marks'] =  round(total_obatined_marks,2)
                exam_dict['class_total_marks'] =  round(class_total_marks,2)
                if class_total_marks == 0:
                    percentage = 0
                else:
                    percentage = round((total_obatined_marks/class_total_marks) * 100,2)
                    
                exam_dict['total_obtained_percentage'] = percentage
                
                paper_date = datetime.strptime(exam_obj.exam_offered.start_date, '%Y-%m-%d')
                monthyear = paper_date.strftime('%B, %Y')
            
                exam_dict['exam_name'] = str(exam_obj.exam_offered.exam_type.name) + ": " + str(monthyear)
                
                if count_fail < 3:
                    exam_dict['student_class_status'] = 'Pass'
                else:
                    exam_dict['student_class_status'] = 'Fail'
                
                sql = """SELECT sms_grading_scheme_line.name, sms_grading_scheme_line.subject_remarks
                    FROM sms_grading_scheme_line 
                    inner join sms_grading_scheme on 
                    sms_grading_scheme.id = sms_grading_scheme_line.grading_scheme
                    WHERE FLOOR(""" + str(percentage) + """) between sms_grading_scheme_line.lower_limit AND sms_grading_scheme_line.upper_limit
                    AND class_id  = (SELECT class_id from sms_academiccalendar where id = """ + str(academiccalendar_id) + """)"""
                
                self.cr.execute(sql)
                grading_row = self.cr.fetchone()
        
                exam_dict['grade'] = grading_row[0]
                exam_dict['remarks'] = grading_row[1]
                
                sql = """SELECT count(marks) from (SELECT 
                    (SELECT sum(obtained_marks) from sms_exam_lines where student_subject in 
                    (SELECT id from sms_student_subject where  student in 
                    (SELECT id from sms_academiccalendar_student where std_id = sms_student.id))
                    and sms_exam_lines.name = """ + str(exam_obj.id) + """) as marks
                    from sms_student 
                    inner join sms_academiccalendar_student
                    on sms_student.id = sms_academiccalendar_student.std_id
                    where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted')a
                    where marks > """ + str(total_obatined_marks)
                
                self.cr.execute(sql)
                exam_dict['position'] = self.cr.fetchone()[0] + 1

                sql = """SELECT count(marks) from (SELECT 
                    (SELECT sum(obtained_marks) from sms_exam_lines where student_subject in 
                    (SELECT id from sms_student_subject where  student in 
                    (SELECT id from sms_academiccalendar_student where std_id = sms_student.id))
                    and sms_exam_lines.name = """ + str(exam_obj.id) + """) as marks
                    from sms_student 
                    inner join sms_academiccalendar_student
                    on sms_student.id = sms_academiccalendar_student.std_id
                    where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted')a"""
                
                self.cr.execute(sql)
                exam_dict['total_students'] = self.cr.fetchone()[0]
                exam_result.append(exam_dict)
            
            final_dict = {'exam_result':'','cadidate_no':'','student_name':'','father_name':'','gender':''}
            sql = """SELECT sms_student.registration_no, sms_student.name, 
                sms_student.father_name, sms_student.gender from sms_student
                inner join sms_academiccalendar_student on
                sms_student.id = sms_academiccalendar_student.std_id 
                WHERE sms_student.id = """ + str(student_id) + """
                AND sms_academiccalendar_student.name = """ + str(academiccalendar_id)
                    
            self.cr.execute(sql)
            row= self.cr.fetchone()
   
            final_dict['exam_result'] = exam_result
            final_dict['cadidate_no'] = str(row[0]).upper()
            final_dict['student_name'] = str(row[1]).upper()
            final_dict['father_name'] = str(row[2]).upper()
            if row[3]=='Male':
                final_dict['gender'] = 'S/o'
            else:
                final_dict['gender'] = 'D/o'
            final_result.append(final_dict)

        return final_result
    
    def get_student_date_sheet(self,form):
        result = []
        exam_offered = self.datas['form']['exam_offered'][0]
        if self.datas['form']['exam_datesheet']:
            datesheet_ids = [self.datas['form']['exam_datesheet'][0]]
        else:
            datesheet_ids = self.pool.get('sms.exam.datesheet').search(self.cr, self.uid,[('exam_offered','=',exam_offered)])
        
        datesheet_objs = self.pool.get('sms.exam.datesheet').browse(self.cr, self.uid,datesheet_ids)
        
        for datesheet_obj in datesheet_objs:
            dict = {'class':'','sub_list':''}
            
            sub_result = []
            my_dict = {'SNO':'S.No','paper_date':'Paper Date', 'subject':'Subject', 'invigilator':'Invigilator', 'total_marks':'Total Marks'}
            sub_result.append(my_dict)
            
            datesheet_lines = self.pool.get('sms.exam.datesheet.lines').search(self.cr,self.uid,[('name','=',datesheet_obj.id)], order="paper_date asc")
            datesheet_objs = self.pool.get('sms.exam.datesheet.lines').browse(self.cr, self.uid,datesheet_lines)
        
            k = 1
            for obj in datesheet_objs:
                my_dict = {'SNO':'','paper_date':'', 'subject':'', 'invigilator':'', 'total_marks':''}
                paper_date = datetime.strptime(obj.paper_date, '%Y-%m-%d')
                date_string = paper_date.strftime('%d-%m-%Y')
                day_week = paper_date.strftime("%A")
                my_dict["SNO"] = k
                my_dict["paper_date"] = date_string + " (" + str(day_week) + ")"
                my_dict["subject"] = obj.subject.subject_id.name
                my_dict["invigilator"] = obj.invigilator.name
                my_dict["total_marks"] = obj.total_marks
                k = k + 1
                sub_result.append(my_dict)
            dict["class"] = datesheet_obj.academiccalendar.name
            dict["sub_list"] = sub_result
            result.append(dict)
        return result
    
report_sxw.report_sxw('report.sms.class.timetable.report', 'sms.timetable', 'addons/sms/class_timetable_report.rml',parser = crossovered_analytic, header='external')
report_sxw.report_sxw('report.sms.teacher.timetable.report', 'sms.timetable', 'addons/sms/teacher_timetable_report.rml',parser = crossovered_analytic, header='external')
report_sxw.report_sxw('report.sms.student.signature.list.name', 'sms.student', 'addons/sms/student_signature_list_report.rml',parser = crossovered_analytic, header='external')
report_sxw.report_sxw('report.sms.student.award.list.name', 'sms.student', 'addons/sms/student_award_list_report.rml',parser = crossovered_analytic, header='external')
report_sxw.report_sxw('report.sms.student.result.list.name', 'sms.student', 'addons/sms/student_result_list_report.rml',parser = crossovered_analytic, header='internal')
report_sxw.report_sxw('report.sms.student.result.sheet.name', 'sms.student', 'addons/sms/student_result_sheet_report.rml',parser = crossovered_analytic, header=False)
report_sxw.report_sxw('report.sms.student.dmc.name', 'sms.student', 'addons/sms/student_dmc_report.rml',parser = crossovered_analytic, header='external')
report_sxw.report_sxw('report.sms.student.dmc.multiple.name', 'sms.student', 'addons/sms/student_dmc_multiple_report.rml',parser = crossovered_analytic, header=False)
report_sxw.report_sxw('report.sms.student.date.sheet.name', 'sms.student', 'addons/sms/student_date_sheet_report.rml',parser = crossovered_analytic, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

