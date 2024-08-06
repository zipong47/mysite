import http.client

def get_request(ip, sn, station_type):
    conn = http.client.HTTPConnection(ip)   
    # 使用str.format拼接URL路径和查询参数
    path = "/macmlb?p=product&c=QUERY_RECORD&sn={}&p=start_time&p=stop_time&p=result&p=station_id&ts={}&p=failure_message&p=list_of_failing_tests".format(sn, station_type)

    conn.request("GET", path)
    
    response = conn.getresponse()
    if(response.status==200):
        print(response.status, response.reason)
        # 读取响应数据
        data = response.read().decode()
        # 将数据解析成字典对象
        result_dict = parse_response_data(data)
        print(result_dict)
        conn.close()
        return result_dict
    
    return "连接失败"


def parse_response_data(data):
    # 创建一个空字典
    result_dict = {}
    
    # 按行拆分数据  
    lines = data.splitlines()
    
    # 解析每行数据，并将键值对添加到字典中
    for line in lines[1:]:
        if "::" in line:
            temp=line.split("::")[-1]
            key, value = temp.split("=", 1)
            result_dict[key.strip()] = value.strip()
    
    return result_dict
