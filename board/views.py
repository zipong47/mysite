import os
import re
from datetime import datetime

from mysite import settings
from board.common import get_request
from .models import *
from .form import EnvReportForm,EditTestPlanForm,DisplayEditTestPlanForm
from openpyxl import load_workbook

from django.template import loader
from django.shortcuts import render,redirect
from django.db.models import Q
from django.http import HttpResponseRedirect,JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
# ban csrf
from django.views.decorators.csrf import csrf_exempt


# 定义字符串列表
STATIONS_STRINGS = ["ICT","DFU","FCT","SOC-TEST","WIFI-BT-COND-B","WIFI-BT-COND"]


class project_detail:
    def __init__(self,project_name,config_subproject_name_dict):
        self.total_subproject_nums=0
        self.project_name=project_name
        self.config_subproject_name_dict=config_subproject_name_dict
        self.subproject_num_list=[]
        for each in config_subproject_name_dict:
            temp_num=0
            for i in config_subproject_name_dict[each]:
                temp_num=temp_num+1
                self.total_subproject_nums=self.total_subproject_nums+1
            self.subproject_num_list.append(temp_num)

class build_unit:
    def __init__(self,project_name,config,build_name,checkin_nums):
        self.project_name=project_name
        self.config=config
        self.build_name=build_name
        self.checkin_nums=checkin_nums
        self.station_yield_list=[]
        
def index(request):
    project_name_set=Board.objects.values_list('project_name',flat=True).distinct()
    index_detail=[]
    for project_name in project_name_set:
        temp_dit={}
        config_set=Board.objects.filter(project_name=project_name).values_list('project_config',flat=True).distinct()
        for each in config_set:
            temp_list=[]
            build_name_set=Board.objects.filter(project_name=project_name,project_config=each).values_list('subprotject_name',flat=True).distinct()
            for build_name in build_name_set:
                temp_list.append(build_name)
            temp_dit[each]=temp_list
        b=project_detail(project_name=project_name,config_subproject_name_dict=temp_dit)
        #index_detail.append(b)
    for project_name in project_name_set:
        config_set=Board.objects.filter(project_name=project_name).values_list('project_config',flat=True).distinct()
        for config in config_set:
            build_name_set=Board.objects.filter(project_name=project_name,project_config=config).values_list('subprotject_name',flat=True).distinct()
            for build_name in build_name_set:
                checkin_set=Board.objects.filter(project_name=project_name,project_config=config,subprotject_name=build_name).filter(env_finished_flag=True)
                nums=len(checkin_set)
                bu=build_unit(project_name=project_name,config=config,build_name=build_name,checkin_nums=nums)
                station_type_list=["ICT","DFU","FCT","SOC-TEST","WIFI-BT-COND","WIFI-BT-COND-B","W3","SWDL"]
                for station_type in station_type_list:
                    station_num=0
                    for board_unit in checkin_set:
                        checkin_record=TestRecord.objects.filter(board=board_unit).filter(station_type='checkin').order_by("-start_time").first()
                        station_record=TestRecord.objects.filter(board=board_unit).filter(station_type=station_type).order_by("-start_time").first()
                        if checkin_record!=None:
                            print(checkin_record.start_time)
                        if station_record!=None:
                            print(station_record.start_time)
                        if(checkin_record != None and station_record != None and checkin_record.start_time < station_record.start_time and station_record.result == 'pass'):
                            station_num=station_num+1
                    bu.station_yield_list.append(station_num)
                    # rate=(station_num/len(checkin_set))*100
                    # rate="{:.2f}%".format(rate)
                    # bu.station_yield_list.append(rate)
                index_detail.append(bu)
                print("nums*******:"+str(nums))
                
    context = {"details": index_detail,"num":5}
    return render(request, "board/index.html", context)

def smt(request):
    latest_question_list = ['physics', 'chemistry', 1997, 2000]
    template = loader.get_template("board/smt.html")
    context = {"latest_question_list": latest_question_list}
    return render(request, "board/smt.html", context)

def upload(request):
    print("upload被调用-------------------")
    return render(request, "board/upload.html")

def check_test_plan_status(test_records, test_plan):
    plan_index = 0
    extra_tests = []
    missing_tests = []
    sequence_errors = []
    current_tests = []
    
    for record in test_records:
        if plan_index < len(test_plan) and record.station_type == test_plan[plan_index]:
            plan_index += 1
            current_tests.append(record.station_type)
        elif plan_index < len(test_plan) and record.station_type != test_plan[plan_index]:
            sequence_errors.append(record.station_type)
        else:
            extra_tests.append(record.station_type)
        
    # Check for any remaining test plans that were not executed
    if plan_index < len(test_plan):
        missing_tests.extend(test_plan[plan_index:])

    return plan_index == len(test_plan), extra_tests, missing_tests, sequence_errors, current_tests
@csrf_exempt
def show_history(request,type):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Ajax请求
        today=datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        test_records_with_schedule=[]
        test_records_today = TestRecord.objects.filter(station_type='checkin').filter(start_time__range=(start_of_day, end_of_day)).order_by('-start_time')
    # if type=='checkin':
        for record in test_records_today:
            try:
                schedule = TestSchedule.objects.get(serial_number=record.board,cp_nums=record.cp_nums)
                next_station = schedule.test_sequence.split('→')[0]
            except TestSchedule.DoesNotExist:
                schedule = None
            test_records_with_schedule.append((record, schedule, next_station))

        daily_table_context={}
        daily_table_context["test_records_with_schedule"]=test_records_with_schedule
        if type=='checkin':
            daily_table_html=render_to_string('board/checkin_daily_table.html',daily_table_context,request=request)
            return JsonResponse({"daily_table_html":daily_table_html})
        else:
            daily_table_html=render_to_string('board/checkout_daily_table.html',daily_table_context,request=request)
            return JsonResponse({"daily_table_html":daily_table_html})

    messages.error(request,"服务器错误！")
    if type=='checkin':
        return JsonResponse({'redirect_url': 'board/checkin.html/'}, status=400)
    else:
        return JsonResponse({'redirect_url': 'board/checkout.html/'}, status=400)

@csrf_exempt
def check_in(request):
    context={}
    return render(request, "board/checkin.html",context)

@csrf_exempt
def checkin_ajax(request,sn_str):
    context={}
    print("____checkin_ajax____")
    message=""
    try:
        board=Board.objects.get(pk=sn_str)
    except Board.DoesNotExist:
        messages.error(request,"未在数据库中查到关于该MLB的相关信息! 请检查sn是否正确。\n")
        return JsonResponse({'redirect_url': '/board/checkin'}, status=400)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Ajax请求
        current_cp=board.cp_nums
        try:
            test_schedule=TestSchedule.objects.filter(serial_number=board,cp_nums=current_cp).get()
        except TestSchedule.DoesNotExist:
            messages.error(request,"未在数据库中查到关于该MLB的test plan相关信息!\n")
            return JsonResponse({'redirect_url': '/board/checkin'}, status=400)

        test_plan_list=test_schedule.test_sequence.split("→")
        test_plan_list=['checkin']+test_plan_list
        
        if_checkin = TestRecord.objects.filter(board=board,cp_nums=current_cp,station_type='checkin').exists()
        if if_checkin:
            message=message+"该主板已经Check-In了，请不要重复扫描。\n"
        else:
            temp_record=TestRecord(board=board,station_type="checkin",cp_nums=board.cp_nums,start_time=datetime.now(),stop_time=datetime.now(),result='pass')
            temp_record.save()

        test_records = TestRecord.objects.filter(board=board,cp_nums=current_cp,result='pass').order_by('start_time')
        is_followed, extra_tests, missing_tests, sequence_errors, current_tests = check_test_plan_status(test_records, test_plan_list)

        test_plan_order_list=[]
        if sequence_errors:
            print("漏测或者测试顺序错误: ", sequence_errors)
            test_plan_order_list=current_tests+sequence_errors
            print(test_plan_order_list)
            message=message+"该主板测试异常，存在漏测或者测试顺序错误，请检查。\n "
        elif missing_tests:
            print("未测工站: ", missing_tests)
            test_plan_order_list=current_tests
            message=message+f"主板NO.{board.board_number}在CP{current_cp}下一个工站：{missing_tests[0]}。\n "
        elif extra_tests:
            print("多测工站: ", extra_tests)
            test_plan_order_list=current_tests
            message=message+"该主板多测了工站，请检查是否正常。\n "
        elif is_followed:
            print("所有测试通过，无错误")
            message=message+f"所有测试通过，无错误。主板在CP{current_cp}的测试都已经完成！\n "
            test_plan_order_list=current_tests+['checkout']
        
        test_plan_list=test_plan_list+['checkout']

        test_history=TestRecord.objects.filter(board=board,cp_nums=current_cp).order_by('start_time')
        if test_history.exists():
            context["test_history"]=test_history
        
        context["message"]=message
        context["test_plan"]=test_plan_list
        context["board_info"]=board

        checkin_table_html=render_to_string('board/checkin_table.html',context,request=request)

        # ------------- daily table ---------------
        today=datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        test_records_with_schedule=[]
        test_records_today = TestRecord.objects.filter(station_type='checkin').filter(start_time__range=(start_of_day, end_of_day)).order_by('-start_time')
        for record in test_records_today:
            try:
                schedule = TestSchedule.objects.get(serial_number=record.board,cp_nums=record.cp_nums)
                next_station = schedule.test_sequence.split('→')[0]
            except TestSchedule.DoesNotExist:
                schedule = None
            test_records_with_schedule.append((record, schedule, next_station))

        daily_table_context={}
        daily_table_context["test_records_with_schedule"]=test_records_with_schedule
        daily_table_html=render_to_string('board/checkin_daily_table.html',daily_table_context,request=request)
        
        print("before return~~~~~~~~~~~")
        
        return JsonResponse({"table":checkin_table_html,"test_plan_order_list":test_plan_order_list,"test_plan_list":test_plan_list,"daily_table_html":daily_table_html})

    messages.error(request,"服务器错误！")
    return JsonResponse({'redirect_url': 'board/checkin.html/'}, status=400)

@csrf_exempt
def check_out(request):
    context={}
    return render(request, "board/checkout.html",context)

@csrf_exempt
def checkout_ajax(request,sn_str):
    context={}
    print("____checkout_ajax____")
    message=""
    try:
        board=Board.objects.get(pk=sn_str)
    except Board.DoesNotExist:
        print("eception__________________")
        messages.error(request,"未在数据库中查到关于该MLB的相关信息! 请检查sn是否正确。\n")
        return JsonResponse({'redirect_url': '/board/checkout'}, status=400)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Ajax请求
        current_cp=board.cp_nums
        try:
            test_schedule=TestSchedule.objects.filter(serial_number=board,cp_nums=current_cp).get()
        except TestSchedule.DoesNotExist:
            messages.error(request,"未在数据库中查到关于该MLB的test plan相关信息!\n")
            return JsonResponse({'redirect_url': 'board/checkout.html/'}, status=400)

        test_plan_list=test_schedule.test_sequence.split("→")
        test_plan_list=['checkin']+test_plan_list

        test_records = TestRecord.objects.filter(board=board,cp_nums=current_cp,result='pass').order_by('start_time')
        is_followed, extra_tests, missing_tests, sequence_errors, current_tests= check_test_plan_status(test_records, test_plan_list)
        if_test_pass=False
        
        test_plan_order_list=[]
        if sequence_errors:
            print("漏测或者测试顺序错误: ", sequence_errors)
            test_plan_order_list=current_tests+sequence_errors
            print(test_plan_order_list)
            message=message+"该主板测试异常，存在漏测或者测试顺序错误，请检查。\n "
        elif missing_tests:
            print("未测工站: ", missing_tests)
            test_plan_order_list=current_tests
            message=message+f"该主板在CP{current_cp}还有未完成的测试，请检查。\n "
        elif extra_tests:
            print("多测工站: ", extra_tests)
            test_plan_order_list=current_tests
            message=message+"该主板多测了工站，请检查是否正常。\n "
        elif is_followed:
            print("所有测试通过，无错误")
            message=message+f"所有测试通过，无错误。主板在CP{current_cp}checkout成功！\n "
            if_test_pass=True
            test_plan_order_list=current_tests+['checkout']
            checkin_record_set=TestRecord.objects.filter(board=board).filter(station_type="checkin")
            checkout_record_set=TestRecord.objects.filter(board=board).filter(station_type="checkout")
            if_checkout = TestRecord.objects.filter(board=board,cp_nums=current_cp,station_type='checkout').exists()
            if(len(checkin_record_set)>len(checkout_record_set) and not if_checkout):
                temp_record=TestRecord(board=board,station_type="checkout",cp_nums=board.cp_nums,start_time=datetime.now(),stop_time=datetime.now(),result='pass')
                temp_record.save()
                board.cp_nums=board.cp_nums+100
                board.save()
            else:
                message=message+"该板子已经checkout了! \n"
                context["message"]=message
        
        test_plan_list=test_plan_list+['checkout']

        test_history=TestRecord.objects.filter(board=board,cp_nums=current_cp).order_by('start_time')
        if test_history.exists():
            context["test_history"]=test_history

        context["message"]=message
        context["test_plan"]=test_plan_list
        context["board_info"]=board
        
        checkin_table_html=render_to_string('board/checkin_table.html',context,request=request)

        # ------------- daily table ---------------
        today=datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        test_records_with_schedule=[]
        test_records_today = TestRecord.objects.filter(station_type='checkout').filter(start_time__range=(start_of_day, end_of_day)).order_by('-start_time')
        for record in test_records_today:
            try:
                schedule = TestSchedule.objects.get(serial_number=record.board,cp_nums=record.cp_nums)
                print(f"current cp:{record.cp_nums}")
                next_station = schedule.test_sequence.split('→')[0]
                
                
            except TestSchedule.DoesNotExist:
                schedule = None
            test_records_with_schedule.append((record, schedule, next_station))

        daily_table_context={}
        daily_table_context["test_records_with_schedule"]=test_records_with_schedule
        daily_table_html=render_to_string('board/checkout_daily_table.html',daily_table_context,request=request)
        
        print("before return~~~~~~~~~~~")
        
        return JsonResponse({"table":checkin_table_html,"test_plan_order_list":test_plan_order_list,"test_plan_list":test_plan_list,"daily_table_html":daily_table_html})

    messages.error(request,"服务器错误！")
    return JsonResponse({'redirect_url': 'board/checkout.html/'}, status=400)
  

def handle_cp_str(cp_str):
    str_list=cp_str.split(",")
    numbers = re.findall(r'\d+', str_list[-1])
    return numbers[0]

@csrf_exempt
def get_env_report(request):
    form = EnvReportForm()
    if request.method == "POST":
        form = EnvReportForm(request.POST,request.FILES)
        if form.is_valid():
            # info_dic=form.cleaned_data['project_name_select_field']
            dic=form.cleaned_data
            print(dic)
            project_name=request.POST['project_name_select_field']
            project_config=request.POST['project_config']
            subproject_name=request.POST['subproject_field']
            print("project_name:"+project_name)
            print("subproject_name:"+subproject_name)
            file_data=request.FILES['env_report_file_field']
            file_absolute_path=os.path.join(settings.BASE_DIR, 'board\\static\\download\\')
            file_absolute_path=os.path.join(file_absolute_path, datetime.now().strftime("%Y%m%d_%H%M%S_")+file_data.name)
            print(file_absolute_path)
            with open(file_absolute_path, 'wb+') as destination:
                for chunk in file_data.chunks():
                    destination.write(chunk)
            messages.success(request,"上传成功！")
            workbook=load_workbook(file_absolute_path)
            worksheet=workbook['sheet1']
            total_rows=worksheet.max_row
            for each in worksheet.iter_rows(min_row=3):
                sn=each[4].value
                configration=each[3].value
                board_num=each[2].value
                test_item=each[5].value
                cp_num=handle_cp_str(each[6].value)
                a_board=Board(project_name=project_name,project_config=project_config,subprotject_name=subproject_name,
                            serial_number=sn,configration=configration,board_number=board_num,
                            test_item_name=test_item,cp_nums=cp_num)
                a_board.save()
            # return HttpResponseRedirect("/board/get_env_report")
            return HttpResponseRedirect(request.path)
    else:
        form = EnvReportForm()
    return render(request, "board/upload_report.html", {"form": form})

@csrf_exempt
def update_summary(request):
    checkin_set=Board.objects.filter(env_finished_flag=True)
    IP="172.16.243.140:80"
    # station_type_list=["ICT","DFU","FCT","SOC-TEST","WIFI-BT-COND-B","WIFI-BT-COND"]
    station_type_list=["ICT"]
    print("*******update summary")
    for board_unit in checkin_set:
        # cp_num=board_unit.cp_nums
        # TestRecord.objects.filter(serial_number=board_unit.serial_number).filter(cp_nums=cp_num)
        for station_type in station_type_list:
            result_dict=get_request(ip=IP,sn=board_unit.serial_number,station_type=station_type)
            result_dict={}
            if board_unit.serial_number == 'sn7':
                result_dict={
                    'start_time':'2024-05-14 16:03:00',
                    'stop_time':'2024-05-14 17:03:00',
                    'result':'pass'}
            else:
                result_dict={'start_time':'','stop_time':'','result':''}
            
            lastest_record=TestRecord.objects.filter(board=board_unit).filter(station_type=station_type).order_by("-start_time").first()

            print("lastest_record:")
            print(lastest_record)
            normal_flag=True
            for key,value in result_dict.items():
                print("value:"+value)
                if value == "" or value == None:
                    normal_flag=False
                    break
            
            if normal_flag:
                starttime = datetime.strptime(result_dict["start_time"], "%Y-%m-%d %H:%M:%S")
                if (lastest_record != None and starttime <= lastest_record.start_time):
                    print("没记录")
                    continue
                # if lastest_record.result == 'fail':
                #     lastest_record.delete()
                #     print("已经删除失败的测试结果。")
                start_time = datetime.strptime(result_dict["start_time"], "%Y-%m-%d %H:%M:%S")
                stop_time = datetime.strptime(result_dict["stop_time"], "%Y-%m-%d %H:%M:%S")
                record=TestRecord(board=board_unit,station_type=station_type,start_time=start_time,stop_time=stop_time,result=result_dict["result"],cp_nums=board_unit.cp_nums)
                record.save()
    
    return redirect("index")

class test_plan_unit:
    def __init__(self,project_config_build,checkin_nums,board_no,test_plan):
        self.project_config_build=project_config_build
        self.checkin_nums=checkin_nums
        self.board_no=board_no
        self.test_plan=test_plan
        self.pk=""
    
    def __str__(self) -> str:
        return (self.project_config_build+"::"+self.checkin_nums+"::"+self.board_no+"::"+self.test_plan)
    
@csrf_exempt
def enter_test_plan(request):
    project_config_build_list=[]
    project_name_set=Board.objects.values_list('project_name',flat=True).distinct()
    for project_name in project_name_set:
        config_set=Board.objects.filter(project_name=project_name).values_list('project_config',flat=True).distinct()
        for each in config_set:
            build_name_set=Board.objects.filter(project_name=project_name,project_config=each).values_list('subprotject_name',flat=True).distinct()
            for build_name in build_name_set:
                # str=str(project_name)+str(each)+str(build_name)
                str=project_name+"-"+each+"-"+build_name
                project_config_build_list.append(str)
    
    context={'options': project_config_build_list}
    data = request.POST.getlist('data[]')
    project_config_build_str = request.POST.get('extra_data')
    checkpoint_str = request.POST.get('cp')

    if checkpoint_str!="" and checkpoint_str!=None:
        checkpoint_list=checkpoint_str.split(",")
        test_sequence="→".join(data)
        project_name,config_name,build_name=project_config_build_str.split("-")
        
        exist_test_schedule=[]
        test_plan_list=[]
        board_query_set=Board.objects.filter(project_name=project_name,project_config=config_name,subprotject_name=build_name)
        for board in board_query_set:
            for cp in checkpoint_list:
                if TestSchedule.objects.filter(serial_number=board,cp_nums=cp).exists():
                    exist_test_schedule.append(board.board_number)
                    exist_test_schedule.append(cp)
                    continue
                new_record=TestSchedule(serial_number=board,cp_nums=cp,test_sequence=test_sequence)
                new_record.save()
                plan_unit=test_plan_unit(project_config_build_str,cp,board.board_number,test_sequence)
                plan_unit.pk=new_record.pk
                test_plan_list.append(plan_unit)
        context["test_plan_list"]=test_plan_list
        if len(exist_test_schedule)==0:
            messages.success(request," 成功上传测试计划！")
        else:
            temp_list=[]
            for i in range(0, len(exist_test_schedule), 2):
                str=f"{exist_test_schedule[i]}-{exist_test_schedule[i+1]}"
                temp_list.append(str)
            str=",".join(temp_list)
            messages.error(request,"成功上传部分测试计划！以下的 板号-CP 重复上传了数据："+str+" 请保存该信息后手动编辑！")
    print(context) 
    context['enter_flag']='enter_flag'
    return render(request, "board/enter_test_plan.html",context)

@csrf_exempt
def search_test_plan(request):
    project_config_build_list=[]
    project_name_set=Board.objects.values_list('project_name',flat=True).distinct()
    for project_name in project_name_set:
        config_set=Board.objects.filter(project_name=project_name).values_list('project_config',flat=True).distinct()
        for each in config_set:
            build_name_set=Board.objects.filter(project_name=project_name,project_config=each).values_list('subprotject_name',flat=True).distinct()
            for build_name in build_name_set:
                str=project_name+"-"+each+"-"+build_name
                project_config_build_list.append(str)
    
    context={'options': project_config_build_list}
    
    data=request.POST.get("keyword")
    search_option=request.POST.get("flexRadioDefault")
    test_plan_list=[]
    if search_option=="sn":
        data_list=data.split()
        for sn in data_list:
            print("----------"+sn)
            try:
                board=Board.objects.get(serial_number=sn)
            except Board.DoesNotExist:
                messages.error(request,"不存在该SN的板子!请检查该SN是否存在:"+sn)
                return render(request, "board/enter_test_plan.html",context)
            
            str=board.project_name+"-"+board.project_config+"-"+board.subprotject_name
            test_schedule_set=TestSchedule.objects.filter(serial_number=board)
            if len(test_schedule_set)==0:
                messages.error(request,"该sn的板子没有测试计划!")
            else:
                for each in test_schedule_set:
                    plan_unit=test_plan_unit(str,each.cp_nums,board.board_number,each.test_sequence)
                    plan_unit.pk=each.pk
                    test_plan_list.append(plan_unit)
                    print(each.pk)
    elif search_option=="build_name":
        try:
            project_name,config_name,build_name=data.split("-")
        except ValueError:
            messages.error(request,"正在使用Project-Configuration-Build搜索，但输入的格式有误，请使用符号(-)进行分割每个名称。")
            return render(request, "board/enter_test_plan.html",context)
        board_set=Board.objects.filter(project_name=project_name,project_config=config_name,subprotject_name=build_name)
        if len(board_set) == 0:
            messages.error(request,"该build不存在，请确认是否已经录入或者是否输入错误!")
        else:   
            for board in board_set:
                str=board.project_name+"-"+board.project_config+"-"+board.subprotject_name
                test_schedule_set=TestSchedule.objects.filter(serial_number=board)
                for each in test_schedule_set:
                    plan_unit=test_plan_unit(str,each.cp_nums,board.board_number,each.test_sequence)
                    test_plan_list.append(plan_unit)
    context["test_plan_list"]=test_plan_list
    return render(request, "board/enter_test_plan.html",context)

@csrf_exempt
def edit_test_plan(request,item_id):
    context={}
    try:
        test_schedule=TestSchedule.objects.get(pk=item_id)
    except TestSchedule.DoesNotExist:
        messages.error(request,"未在数据库中查到test schedule相关主键信息!")
        return render(request, "board/enter_test_plan.html",context)
        
    try:
        board=test_schedule.serial_number
    except Board.DoesNotExist:
        messages.error(request,"未在数据库中查到test schedule相关board的主键信息!")
        return render(request, "board/enter_test_plan.html",context)

    print("editing test plan......")

    if request.method == 'POST':
        form = EditTestPlanForm(request.POST,instance=test_schedule)
        if form.is_valid():
            # 获取提交的字段值
            submitted_value = form.cleaned_data['test_sequence']
            valid_flag=True
            for each in submitted_value.split("→"):
                if each not in STATIONS_STRINGS:
                    valid_flag=False
            if valid_flag:
                form.save()
                messages.success(request,f"板号:{board.board_number} 已成功提交和修改 Check Point:{test_schedule.cp_nums} 的测试计划。")
            else:
                messages.error(request, '提交的测试计划格式有问题。请检查修改后重新提交！')
            
            # 补全消息框后再实现下方功能
            # context["test_plan_list"]=test_plan_list
            return render(request, "board/enter_test_plan.html",context)
    else:
        form = EditTestPlanForm(instance=test_schedule)
        board_info_form = DisplayEditTestPlanForm(instance=board)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Ajax请求
            form_html = render_to_string('board/edit_form_snippet.html', {'form': form,'board_info_form':board_info_form}, request=request)
            return JsonResponse({'form': form_html})  # 返回表单的HTML
        
    return render(request, 'board/enter_test_plan.html', {'form': form, 'item_id': item_id})

@csrf_exempt
def eception_page(request):
    project_name_set=Board.objects.values_list('project_name',flat=True).distinct()
    station_type_set = TestRecord.objects.exclude(station_type__in=['checkin', 'checkout']).values_list('station_type', flat=True).distinct()
    context={"project_name_list":list(project_name_set),"station_type_list":list(station_type_set)}
    return render(request, "board/eception_page.html",context)

@csrf_exempt
def search_eception(request):
    if request.method == 'POST':
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')
        project_name = request.POST.get('project')
        station_type = request.POST.get('station')
        
        # Initialize query filters
        test_record_filters = ~Q(result='pass')
        board_filters = ~Q(status='testing') & ~Q(status='archived')
        
        # Add filters based on user input
        if start_time and end_time:
            test_record_filters &= Q(start_time__gte=start_time, stop_time__lte=end_time)
        
        if project_name:
            board_filters &= Q(project_name=project_name)
        
        if station_type:
            test_record_filters &= Q(station_type=station_type)
        
        # Retrieve TestRecords based on filters
        test_records = TestRecord.objects.filter(test_record_filters)
        
        # Retrieve Boards based on filters
        boards = Board.objects.filter(board_filters)
        
        # Combine the results
        results = []
        for test_record in test_records:
            board = test_record.board
            if board in boards:
                # error_records = ErrorRecord.objects.filter(board=board, test_record=test_record)
                error_records = test_record.error_records.all().first()
                if error_records.exists():
                    results.append({
                        'board': {
                            'project_name': board.project_name,
                            'project_config': board.project_config,
                            'subprotject_name': board.subprotject_name,
                            'serial_number': board.serial_number,
                            'configration': board.configration,
                            'board_number': board.board_number,
                            'test_item_name': board.test_item_name,
                            'cp_nums': board.cp_nums,
                            'product_code': board.product_code,
                            'APN': board.APN,
                            'HHPN': board.HHPN,
                            'first_GS_sn': board.first_GS_sn,
                            'second_GS_sn': board.second_GS_sn,
                            'env_finished_flag': board.env_finished_flag,
                            'status': board.status,
                        },
                        'test_record': {
                            'station_type': test_record.station_type,
                            'start_time': test_record.start_time,
                            'cp_nums': test_record.cp_nums,
                            'stop_time': test_record.stop_time,
                            'result': test_record.result,
                            'site': test_record.site,
                            'operator': test_record.operator,
                            'remark': test_record.remark,
                        },
                        'error_records': list(error_records.values('fail_message', 'remark'))
                    })
        if len(results) == 0:
            print("results结果如下")
            print(results)
            customize_message_html = render_to_string('board/customize_message.html', {'message': '未找到符合条件的记录'},request=request)
            return JsonResponse({'results': results,'customize_message':customize_message_html})
        return JsonResponse({'results': results})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def search_serial_number_in_eception_page(request):
    if request.method == 'POST':
        serial_number = request.POST.get('serialNumber')
        try:
            board = Board.objects.get(serial_number=serial_number)
            test_records = TestRecord.objects.filter(board=board)
            test_records_data = list(test_records.values('station_type', 'start_time', 'stop_time', 'result'))
            return JsonResponse({'test_records': test_records_data})
        except Board.DoesNotExist:
            return JsonResponse({'error': 'Serial number not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)