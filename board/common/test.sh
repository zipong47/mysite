#!/bin/bash
echo "hello world ${1}${2}"
curl "172.16.243.140:80/mcaclb?p=product&c=QUERY_RECORD&sn=12312313&p=unit_process_check&p=start_time&p=stop_time&p=result&p=station_id&ts=ICT"
exit 0