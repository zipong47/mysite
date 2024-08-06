from django.core.management.base import BaseCommand
from board.models import Board, TestRecord
from datetime import datetime

class Command(BaseCommand):
    help = "Manually checkin or checkout the board based on serial numbers in board_sn.txt"

    def add_arguments(self, parser):
        parser.add_argument(
            'station_type',
            choices=['checkin', 'checkout'],
            help='Specify the station type as either checkin or checkout'
        )
        parser.add_argument(
            '--file',
            default='board_sn.txt',
            help='Specify the path to the file containing board serial numbers'
        )

    def handle(self, *args, **options):
        station_type = options['station_type']
        file_path = options['file']

        try:
            with open(file_path, 'r') as file:
                # Read the entire file and split by whitespace (newlines and spaces)
                serial_numbers = file.read().split()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {file_path} not found."))
            return

        created_records = 0
        for serial_number in serial_numbers:
            try:
                board = Board.objects.get(serial_number=serial_number)
                cp_nums=board.cp_nums
                if station_type == 'checkout':
                    cp_nums = cp_nums + 100
                    board.cp_nums = cp_nums
                    board.env_finished_flag = False
                    board.save()
                else:
                    board.env_finished_flag = True
                    board.save()
                    
                TestRecord.objects.create(
                    board=board,
                    station_type=station_type,
                    start_time=datetime.now(),
                    stop_time=datetime.now(),  # You might want to adjust this
                    result='pass',  # Set default result; adjust as needed
                    cp_nums=cp_nums
                )
                created_records += 1
            except Board.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Board with serial number {serial_number} not found."))

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_records} TestRecords with station_type={station_type}."))
