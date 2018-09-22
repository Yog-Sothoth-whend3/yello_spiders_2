import re
import requests
from pyquery import PyQuery as pq 
from selenium import webdriver
import pymysql
from multiprocessing import Pool





def child_page(root_url):
    url_2 = root_url.replace('.html','_2.html')
    num = 3 
    error_count = 0
    page_list = [root_url,url_2]
    while(True):
        string = '_'+str(num)
        p = re.compile('_\d*')
        new_url = re.sub(p,string,url_2)
        req = requests.get(new_url)
        if(req.status_code == 200):
            print(req.url)
            page_list.append(new_url)
            num = num +1   
        else:
            print('error')
            error_count = error_count + 1
            if (error_count == 3):
                break
            else:
                continue    

    return page_list



def contentpage(page_list):
    content_list = []
    for i in page_list:
        req = requests.get(i)
        doc = pq(req.text)
        content = doc('.box.movie_list li a').items()
        for e in content:
            print(e.attr('href'))
            content_list.append(e.attr('href'))
    return content_list

def getcontent(content_list):
    for i in content_list:
        try:
            url = 'http://www.3c6e.com'+i
            req = requests.get(url ,timeout = 5)
            req.encoding = 'gbk'
            doc = pq(req.text)
            title =  doc('dt img').attr('alt')
    
            player = doc('.film_bar.clearfix a').attr('href')
            player = 'http://www.3c6e.com'+player
            req_content = requests.get(player,timeout = 5)

            doc_content = pq(req_content.text)
            address = doc_content('#content_jr script').attr('src')
            address = 'http://www.3c6e.com'+address
            req_adress = requests.get(address,timeout = 5)
            p = re.compile('http\S*.m3u8')
            m3u8 = re.search(p,req_adress.text).group(0).replace('$m3u8','')
            req_m3u8 = requests.get(m3u8,timeout= 5)

            if(req_m3u8.status_code== 200):
                print(m3u8)
                status_result = 100
                db = pymysql.connect(host = '122.152.234.185',user = 'admin',password = 'XXXXXXXXX',port = 3306,db = 'adark',charset = 'utf8')
                cursor = db.cursor()
                sql = 'INSERT INTO myapp_movie(name,adrees,ST) values(%s,%s,%s) ON DUPLICATE KEY UPDATE name = %s ,adrees = %s ,ST = %s  '
                try:
                    cursor.execute(sql,(title,m3u8,status_result)*2)
                    db.commit()
                    print ('successful!')
                except:
                    print('FALL')
                    db.rollback()
            else:
                continue
        except:
            continue


def main(section):
    page_list =child_page(section)
    content_list = contentpage(page_list)
    getcontent(content_list)





if __name__=='__main__':

    section_list = ['http://www.3c6e.com/list/index1.html','http://www.3c6e.com/list/index2.html','http://www.3c6e.com/list/index3.html','http://www.3c6e.com/list/index4.html','http://www.3c6e.com/list/index5.html','http://www.3c6e.com/list/index6.html','http://www.3c6e.com/list/index7.html','http://www.3c6e.com/list/index8.html']
            
    p = Pool(4)
    for i in section_list:
        p.apply_async(main,args=(i,))
    p.close()
    p.join()
 



    
    