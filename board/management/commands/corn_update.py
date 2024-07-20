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

def get_test_schedule_station(board):
    current_cp_schedule = TestSchedule.objects.filter(serial_number=board,cp_nums=board.cp_nums)
    test_sequence = current_cp_schedule.test_sequence
    test_plan_list = test_sequence.split("→")
    distinct_test_plan = set(test_plan_list)
    return distinct_test_plan
 
class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        IP="172.16.243.140:80"
        #station_type_list=["ICT","DFU","FCT","SOC-TEST","WIFI-BT-COND-B","WIFI-BT-COND"]
        with open("","a") as log:
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
                for key, value in result_dict.items():
                    if value == "" or value is None:
                        print("没记录")
                        continue
                start_time = datetime.strptime(result_dict["start_time"], "%Y-%m-%d %H:%M:%S")
                lastest_record=TestRecord.objects.filter(board=board_unit,cp_nums=board_unit.cp_nums,station_type=next_station).order_by("-start_time").first()
                if (lastest_record != None and start_time <= lastest_record.start_time):
                    print("没记录")
                    continue
                stop_time = datetime.strptime(result_dict["stop_time"], "%Y-%m-%d %H:%M:%S")
                record=TestRecord(board=board_unit,station_type=next_station,start_time=start_time,stop_time=stop_time,result=result_dict["result"],cp_nums=board_unit.cp_nums)
                record.save()
                
                if(board_unit.status=="pause"):
                    if result_dict["result"]=="pass":
                        board_unit.status="testing"
                        board_unit.save()
                        ErrorRecord.objects.filter(board=board_unit,cp_nums=board_unit.cp_nums)
                    else:
                        
        
        self.stdout.write(
            self.style.SUCCESS('成功更新数据')
        )