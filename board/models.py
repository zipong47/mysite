from django.db import models

class Board(models.Model):
    project_name=models.CharField(max_length=200)
    project_config=models.CharField(max_length=50,default='C')
    subprotject_name=models.CharField(max_length=200)
    serial_number=models.CharField(primary_key=True,max_length=200)
    configration=models.CharField(max_length=200)
    board_number=models.IntegerField()
    test_item_name=models.CharField(max_length=100)
    cp_nums = models.IntegerField(default=0)
    # input_env_finished_time = models.DateTimeField("input env finished")
    product_code=models.CharField(max_length=20,default='')
    APN=models.CharField(max_length=50,default='')
    HHPN=models.CharField(max_length=50,default='')
    first_GS_sn=models.CharField(max_length=50,default='')
    second_GS_sn=models.CharField(max_length=50,default='')
    env_finished_flag = models.BooleanField(default=False)
    STATUS_CHOICES={
        "testing":"testing",
        "pause":"pause",
        "cancel":"cancel",
        "cut":"cut",
        "archived":"archived",
    }
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='testing')
    def __str__(self):
        return f"{self.project_name}-{self.project_config}-{self.subprotject_name},no={self.board_number},cp={self.cp_nums})"    

class TestRecord(models.Model):
    STATUS_CHOICES={
        "pass":"pass",
        "fail":"fail",
        "cof":"cof",
    }
    board=models.ForeignKey(Board,on_delete=models.CASCADE)
    station_type=models.CharField(max_length=50)
    start_time=models.DateTimeField("start time.")
    cp_nums = models.IntegerField(default=0)
    stop_time=models.DateTimeField("stop time")
    result= models.CharField(max_length=4,choices=STATUS_CHOICES,default='fail')
    site=models.CharField(max_length=20,default='FXLH')
    operator=models.CharField(max_length=50,default='')
    remark=models.CharField(max_length=500,default='')
    def __str__(self): 
        return f"board_num={self.board.board_number},station_type={self.station_type},cp_num={self.cp_nums},start_time={self.start_time},TestResult(result={self.result})"
    
class TestSchedule(models.Model):
    serial_number=models.ForeignKey(Board,on_delete=models.CASCADE)
    cp_nums = models.IntegerField(default=0)
    test_sequence=models.CharField(max_length=300)
    def __str__(self):
        return f"board_num={self.serial_number.board_number},cp_num={self.cp_nums},test_sequence={self.test_sequence})"
  
class ErrorRecord(models.Model):
    # Foreign keys to Board and TestRecord
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    test_record = models.ForeignKey(TestRecord, on_delete=models.CASCADE)
    
    # String fields for failure message and remarks
    fail_message = models.CharField(max_length=255)
    remark = models.CharField(max_length=255)
    
    # File field for failure picture
    # fail_picture = models.ImageField(upload_to='failures/%Y/%m/%d/')

    def __str__(self):
        return f"ErrorRecord for {self.board.serial_number} on {self.test_record.cp_nums}"