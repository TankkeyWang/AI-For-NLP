import requests
from bs4 import BeautifulSoup
import re

def process_data_to_graph(graph,soup,line_num):
   locate_ths=soup.find_all("th",text=re.compile('起始/终到车站'))
   if locate_ths:
      for th in locate_ths:
         pass_ways=th.parent.find_next_siblings("tr")
         for way in pass_ways:
            if way.contents[0].string:
               source,destination=str(way.contents[0].string).split("——")
               construct_graph(graph,source,destination,line_num)
               source, destination=destination,source
               construct_graph(graph, source, destination, line_num)
   # else:
   #    print(soup.head.title)

def construct_graph(graph,source,destination,line_num):
   if source not in graph:
      graph[source] = [(destination, line_num)]
   else:
      graph[source] += [(destination, line_num)]


def search(graph, start, is_goal, search_strategy):
   pathes_and_lines = [[[start],[]]]#[[start]]
   seen = set()

   while pathes_and_lines:
      path_and_line = pathes_and_lines.pop(0)
      path=path_and_line[0]
      line=path_and_line[1]

      froniter = path[-1]

      if froniter in seen: continue

      successors = graph[froniter]

      for station,l in successors:
         if station in path: continue

         new_path = path + [station]
         new_line = line + [l]

         pathes_and_lines.append([new_path,new_line])

         if is_goal(new_path): return new_path
      seen.add(froniter)
      pathes_and_lines = search_strategy(pathes_and_lines)


def is_goal(desitination,pass_by):
   if '' in pass_by:
      pass_by.remove('')
   def _wrap(current_path):
      return current_path[-1] == desitination and len([p for p in pass_by if p not in current_path])==0

   return _wrap


def sort_path(cmp_func, beam=-1):
   def _sorted(pathes):
      return sorted(pathes, key=cmp_func)
   return _sorted


def get_total_station(path_and_linenum):
   return len(path_and_linenum[0])

def get_change_count(path_and_linenum):
   if len(path_and_linenum[1]) <=1:return 0
   ans=0
   for i in range(1,len(path_and_linenum[1])-1):
      if path_and_linenum[1][i] != path_and_linenum[1][i-1]:
         ans+=1
   return ans

def get_comprehensive_path(path):
   return get_total_station(path) + get_change_count(path)*2

headers = {
   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
}
r=requests.get('https://baike.baidu.com/item/%E5%8C%97%E4%BA%AC%E5%9C%B0%E9%93%81/408485',headers=headers)

soup = BeautifulSoup(r.content)

line_dict=dict()
for item in soup.find_all(href=re.compile('/item/')):
   if re.match('^北京地铁\w*线',str(item.string)):
      if item.string not in line_dict.keys():
         line_dict[item.string]=set()
         line_dict[item.string].add(item['href'])
      else:
         line_dict[item.string].add(item['href'])


line_num=0
graph=dict()
for k in line_dict.keys():
   r=requests.get('https://baike.baidu.com'+list(line_dict[k])[0],headers=headers)
   soup = BeautifulSoup(r.content)
   process_data_to_graph(graph,soup,line_num)
   line_num += 1



while True:
   start=input("起点：")
   end=input("终点：")
   pass_by=input("路过：（多个请用空格隔开）")
   pass_by=pass_by.split(" ")
   if start not in graph or end not in graph:
      print('站点错误，请重新输入')
      continue
   print("路程最短优先：")
   print(search(graph,start,is_goal(end,pass_by),search_strategy=sort_path(get_total_station)))
   print("最少换乘优先：" )
   print(search(graph, start, is_goal(end, pass_by), search_strategy=sort_path(get_change_count)))
   print("综合优先：")
   print(search(graph, start, is_goal(end, pass_by), search_strategy=sort_path(get_comprehensive_path)))