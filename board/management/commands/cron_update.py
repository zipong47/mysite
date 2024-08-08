import json
from django.core.management.base import BaseCommand, CommandError
from board.models import *
from board.common import get_request 
from datetime import datetime


def find_first_error_station(test_plan, test_record):
    """
    Find the first mismatching test station in the test plan and test record.

    Args:
    test_plan (list): The planned sequence of test stations for the board.
    test_record (list): The actual sequence of test stations the board went through, sorted by time.

    Returns:
    tuple: The first mismatching test station from the test plan and its index.
    """
    plan_idx = 0
    record_idx = 0

    while plan_idx < len(test_plan) and record_idx < len(test_record):
        if test_plan[plan_idx] == test_record[record_idx]:
            plan_idx += 1
        record_idx += 1

    # If we went through the whole plan, check for unfinished tests
    if plan_idx < len(test_plan):
        return test_plan[plan_idx], plan_idx
    
    # If all plan stations matched and there are extra records, we handle over-tests here
    if record_idx < len(test_record):
        return None, None
    
    return None, None

class Command(BaseCommand):
    help = "auto record the test record by crontab"

    def handle(self, *args, **options):
        IP="172.16.243.140:80"
        #station_type_list=["ICT","DFU","FCT","SOC-TEST","WIFI-BT-COND-B","WIFI-BT-COND"]
        with open("/Users/tony_wei/Desktop/HuangZP/mysite0807/logfile.txt","a") as log:
            log.write(f"update summary at {datetime.now()}\n")
            
        checkin_set=Board.objects.filter(env_finished_flag=True).filter(status__in=["testing","pause"])
        for board_unit in checkin_set:
            testrecord_in_order = TestRecord.objects.filter(board=board_unit,cp_nums=board_unit.cp_nums).exclude(result="fail").order_by("start_time")
            try:
                test_plan = TestSchedule.objects.filter(serial_number=board_unit,cp_nums=board_unit.cp_nums).first().test_sequence.split("→")
            except AttributeError:
                continue
            test_record = [record.station_type for record in testrecord_in_order]
            next_station, index = find_first_error_station(test_plan, test_record)
            if next_station:
                result_dict=get_request(ip=IP,sn=board_unit.serial_number,station_type=next_station)
                if result_dict['start_time'] == "":
                    print("没记录")
                    continue
                # Compare result_dict["start_time"] with the board_unit the newest TestRecord of checkin start_time
                # If result_dict["start_time"] <= the newest TestRecord of checkin start_time, then continue
                start_time = datetime.strptime(result_dict["start_time"], "%Y-%m-%d %H:%M:%S")
                checkin_time = TestRecord.objects.filter(board=board_unit,cp_nums=board_unit.cp_nums,station_type="checkin").order_by("-start_time").first().start_time
                if start_time <= checkin_time:
                    print("不是本轮的记录")
                    continue
                
                result_dict["result"] = result_dict["result"].lower()
                # Pretty print the dictionary
                print("Result Dictionary:")
                print(json.dumps(result_dict, indent=4, ensure_ascii=False))
                with open("/Users/tony_wei/Desktop/HuangZP/mysite0807/logfile.txt","a") as log:
                    log.write("Result Dictionary:")
                    # log.write(json.dumps(result_dict, indent=4, ensure_ascii=False))
                    log.write("\n")
                start_time = datetime.strptime(result_dict["start_time"], "%Y-%m-%d %H:%M:%S")
                stop_time = datetime.strptime(result_dict["stop_time"], "%Y-%m-%d %H:%M:%S")
                lastest_record=TestRecord.objects.filter(board=board_unit,cp_nums=board_unit.cp_nums,station_type=next_station).order_by("-start_time").first()
                if (lastest_record != None and start_time <= lastest_record.start_time):
                    print("没记录")
                    continue
                elif (lastest_record == None):
                    current_record=TestRecord(board=board_unit,station_type=next_station,start_time=start_time,stop_time=stop_time,result=result_dict["result"],cp_nums=board_unit.cp_nums)
                    current_record.save()
                    if result_dict["result"]=="fail":
                        board_unit.status="pause"
                        board_unit.save()
                        error_record=ErrorRecord(board=board_unit,cp_nums=board_unit.cp_nums,STATUS_CHOICES='ongoing')
                        error_record.add(current_record)
                        error_record.save()
                    elif result_dict["result"]=="pass":
                        print("pass")
                        continue
                else:
                    current_record=TestRecord(board=board_unit,station_type=next_station,start_time=start_time,stop_time=stop_time,result=result_dict["result"],cp_nums=board_unit.cp_nums)
                    if(board_unit.status=="pause"):
                        if lastest_record.result=="fail":
                            error_record = lastest_record.error_records.all().first()
                            if result_dict["result"]=="fail":
                                error_record.add(current_record)
                            elif result_dict["result"]=="pass":
                                board_unit.status="testing"
                                board_unit.save()
                                error_record.delete()    
                                current_record.save()
                        elif lastest_record.result=="cof":
                            if result_dict["result"]=="fail":
                                board_unit.status="testing"
                                board_unit.save()
                                current_record.result='cof'
                                current_record.save()
                                error_record.add(current_record)
                                error_record.status='finish'
                                error_record.save()
                            elif result_dict["result"]=="pass":
                                board_unit.status="testing"
                                board_unit.save()
                                current_record.save()
                                error_record.status='finish'
                                error_record.save()
                        elif lastest_record.result=='pass':
                            current_record.save()
                            print("error,this situation should not exist!!")
                    elif(board_unit.status=="testing"):
                        if result_dict["result"]=="fail":
                            board_unit.status="pause"
                            board_unit.save()
                            current_record.save()
                            error_record=ErrorRecord(board=board_unit,cp_nums=board_unit.cp_nums,STATUS_CHOICES='ongoing')
                            error_record.add(current_record)
                            error_record.save()
                        else:
                            current_record.save()
                            print("pass")
                            
        # Check Board if overdue
        checkin_board_set = Board.objects.filter(env_finished_flag=True)
        for board_unit in checkin_board_set:
            checkin_record = TestRecord.objects.filter(board=board_unit,cp_nums=board_unit.cp_nums,station_type="checkin").get()
            time_difference = datetime.now() - checkin_record.start_time
            if time_difference.total_seconds() > 72 * 3600:
                board_unit.if_overdue = True
                board_unit.save()