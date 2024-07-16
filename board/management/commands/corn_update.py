from django.core.management.base import BaseCommand, CommandError
from board.models import Board,TestRecord
from board.common import get_request 
from datetime import datetime

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        with open("","a") as log:
            log.write(f"update summary at {datetime.now()}\n")
        checkin_set=Board.objects.filter(env_finished_flag=True)
        IP="172.16.243.140:80"
        station_type_list=["ICT","DFU","FCT","SOC-TEST","WIFI-BT-COND-B","WIFI-BT-COND"]
        for board_unit in checkin_set:
            # cp_num=board_unit.cp_nums
            # TestRecord.objects.filter(serial_number=board_unit.serial_number).filter(cp_nums=cp_num)
            for station_type in station_type_list:
                result_dict=get_request(ip=IP,sn=board_unit.serial_number,station_type=station_type)
                lastest_record=TestRecord.objects.filter(board=board_unit).filter(station_type=station_type).order_by("-start_time").first()
                
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
        
        self.stdout.write(
            self.style.SUCCESS('成功更新数据')
        )