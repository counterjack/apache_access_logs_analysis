# python program to get detailed datewise information from the apache log file
# output :  no. of reauest, source ip and no. of request made
# clients wise figures
import operator
import datetime
import threading
import matplotlib.pyplot as plt
import os
from config import lines_to_parse, date_format, files_to_skip, BASE_DIR
from thread import start_new_thread
from multiprocessing.pool import Pool
# import celery
# app=celery.Celery('access_logs.tasks',broker='redis://localhost:6379/0')
file_name = '/home/ankur/Downloads/access_log_20April'    

if not file_name:
    raise Exception('Give absolute path of the file')
try:
    fp =  open(file_name, 'r')
    lines = fp.readlines()
except Exception as e:
    raise Exception(e)

def time_range_decorator(func):
    def wrapper(*args, **kwargs):
        initial_time = None
        end_time = None
        day_wise_requests = {}
        try:
            ip = args[1]
        except IndexError:
            ip = None

        if ip is not None:
            log_data = [i for i in lines if ip in i]
        else:
            log_data = lines[:lines_to_parse]

        for item in log_data:
            separated_by_space = item.split(' ')
            current_datetime = separated_by_space[3][1:]
            current_datetime = datetime.datetime.strptime(current_datetime, date_format)
            current_date = current_datetime.date()
            
            # getting daywise requests 
            if str(current_date) in day_wise_requests.keys():
                day_wise_requests[str(current_date)] += 1
            else:
                day_wise_requests[str(current_date)] = 1

            if initial_time is None and end_time is None:
                initial_time = end_time = current_datetime
            if current_datetime < initial_time:
                initial_time = current_datetime
            if current_datetime > end_time:
                end_time = current_datetime  
        
        func.day_wise_requests = day_wise_requests
        print ('time range from {} to {}').format(str(initial_time), str(end_time))        
        return func(*args, **kwargs)        
    return wrapper

@time_range_decorator    
def overall_report(show_graph=False):
    """
        output : return urls hit and origin ip adddresses in descending order for the given log file 
    """
    ip_address = {}
    urls_hit = {}
    for item in lines[:lines_to_parse]:
        # exclude zabbix agent from the request 
        if 'Zabbix' in item:
            continue
        # with Pool(8) as p:
            # p.map(self.overall_helper, (item, ip_address, urls_hit))
        start_new_thread(overall_helper, (item, ip_address, urls_hit))        
        # thread = threading.Thread(target=self.overall_helper, args=(item, ip_address, urls_hit))
        # thread.start()
    
    urls_hit = sorted(urls_hit.items(),key=operator.itemgetter(1), reverse=True )
    ip_address= sorted(ip_address.items(), key=operator.itemgetter(1), reverse=True)
    print "Unique Visitors {}".format(len(ip_address))
    return urls_hit, ip_address, len(ip_address), len(ip_address)

# @app.task(name='particular_report')
@time_range_decorator
def particular_ip_report(ip, show_graph=False):
    """
        i/p: 
        args: ip address in string format
        args: show_graph : boolean 
        o/p: logs corresponding to the given ip address and devices used by the client
    """ 
    devices_used = set()
    urls_hit = {}
    log_list = [i for i in lines if ip in i]
    for item in log_list:
        overall_helper(item, urls_hit=urls_hit)
        try:
            devices_used.add(item.split(' ')[11])
        except Exception as e:
            print e

    total_logs = len(log_list)
    urls_hit = sorted(urls_hit.items(),key=operator.itemgetter(1), reverse=True )
    # generate urls access graph
    if show_graph:
        plot_graph(urls_hit, graph_type=1)
    return log_list, total_logs, devices_used

def overall_helper(item, ip_address=None, urls_hit=None):
    separated_by_space = item.split(' ')
    ip = separated_by_space[0]
    url = separated_by_space[6]

    # counting ip wise requests
    if ip_address is not None:
        if ip in ip_address.keys():
            ip_address[ip] += 1        
        else:
            ip_address[ip] = 1

    # counting urls wise requests 
    if urls_hit is not None:
        if url.endswith(files_to_skip):
            return  
        if url in urls_hit.keys():
            urls_hit[url] += 1
        else:
            urls_hit[url] = 1

def plot_graph(data, graph_type=0):

    """
    i/p: data : [(ip, request_count, ('1.1.1.1', 10)], list of tuple
    args: graph_type = 0 // ip wise graph
          graph_type = 1 // url wise graph 
    """
    if graph_type == 0 :
        label = 'IP Wise Graph'
        xlabel = 'Ip addresses'
        ylabel = 'Requests made'
    else:
        label = 'URL Wise Graph'
        xlabel = 'Urls'
        ylabel = 'Requests made'

    # instantiate plt
    x_data = [i[0] for i in data] 
    y_data = [i[1] for i in data] 
    plt.plot(x_data, y_data, color='green', linewidth=2.5, label=label, frame=False)
    plt.ylim(min(y_data), max(y_data))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc='upper left', frameon=False)
    plt.show(block=False)
