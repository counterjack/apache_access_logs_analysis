#   '64.233.172.149 - - [11/Apr/2018:11:46:22 +0530] "GET /images/image-mn.png HTTP/1.1" 200 219503 "https://www.doctorinsta.com/news.php" "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko; googleweblight) Chrome/38.0.1025.166 Mobile Safari/535.19"**RT=0/ms706755**\n',
# sample file given above. 
# Will give data of the given access log file.

Class AccessLogReprt
methods :
	overall_report(show_graph=False) # Return overall report of the given file like ip wise requests count, urls wise request count
	particular_ip_report(ip, show_graph=False)  # return report of given ip

Accessing Way :

a = AccessLogReport(file_path=path_of_the_file)
a.overall_report()
a.particular_ip_report(ip='')
