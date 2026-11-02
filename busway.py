# 生成地铁svg文件
import json
from pathlib import Path
import requests
import re
'''
    # 获取百度地图-城市地铁索引
    https://ditu.baidu.com/?qt=subwayscity
    # 获取百度地图-城市地铁数据
    https://map.baidu.com/?qt=subways&c=340&format=json
    # 页面-百度地图-城市地铁路线图页面：含svg-提取svg
    https://map.baidu.com/subway/%E4%B8%8A%E6%B5%B7%E5%B8%82/@12647363,4121218,15z/ccode%3D340%26cname%3D%25E6%25B7%25B1%25E5%259C%25B3%25E5%25B8%2582
'''
current_dir=Path(__file__).parent
# 字符串模版
svg_template=f'''
<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%d %d %d %d" >
    <defs> 
        <g id="change">
        <circle cx="5" cy="5" r="5" fill="#fff" stroke="#393" stroke-width="1.2"></circle>
        <path fill='#393' d='M 3.46,3.28 C 2.39,4.48 2.21,5.9 3.46,7.37 L 2.83,7.86 L 5.14,8.51 L 4.86,6.28 L 4.19,6.82 C 3.1,5.6 3.27,4.96 4.32,3.61 L 3.46,3.28 M 6.53,6.76 C 7.6,5.56 7.79,4.14 6.53,2.67 L 7.17,2.18 L 4.85,1.52 L 5.13,3.76 L 5.8,3.21 C 6.89,4.44 6.72,5.08 5.67,6.43 L 6.53,6.76'/>
        </g>
    </defs> 
<g id="lines">%s</g>
<g id="stations">%s%s%s</g>
</svg>
'''


## 获取地铁城市索引
def get_subway_index():
    url='https://ditu.baidu.com/?qt=subwayscity'
    response=requests.get(url)
    response.encoding='utf-8'
    res_data=json.loads(response.text)
    with open(current_dir/'subwayscity.json','w',encoding='utf-8') as f:
        json.dump(res_data,f,ensure_ascii=False,indent=2)
    data=res_data['subways_city']['cities']
    result={}
    for city in data:
        result[city['cename']]=str(city['code'])
    outfile=current_dir/'subway_index.json'
    with open(outfile,'w',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)

## 获取城市地铁数据json
def get_city_subway_data(city_name):
    ccode=subway_index[city_name]
    url=f'https://map.baidu.com/?qt=subways&c={ccode}&format=json'
    response=requests.get(url)
    response.encoding='utf-8'
    res_data=json.loads(response.text)
    # 保存源数据
    with open(current_dir/f'subways-{city_name}.json','w',encoding='utf-8') as f:
        json.dump(res_data,f,ensure_ascii=False,indent=2)
    print(f'已获取{city_name}地铁数据')
    return res_data

## 换乘站点添加多个线路class
def add_class(add_str):
    def replacer(match):
        prefix = match.group(1) 
        old_class = match.group(2) 
        suffix = match.group(3) 
        new_class_content = f"{old_class} {add_str}".strip()
        return f"{prefix}{new_class_content}{suffix}"
    return replacer


## 生成城市地铁svg文件
def create_city_subway_svg(city_name):
    # 读取城市地铁数据json
    city_subway_json=current_dir/f'subways-{city_name}.json'
    if not city_subway_json.exists():
        get_city_subway_data(city_name)
    json_data=json.load(open(city_subway_json,'r',encoding='utf-8'))
    # 地铁线路
    ## 当前城市地铁svg文件宽度高度视口
    max_x=0
    max_y=0
    min_x=0
    min_y=0
    # 地铁线路-svg路径字符串
    lines_str=''
    # 地铁站点标记
    stations_str=''
    # 地铁站点文本
    stations_text=''
    # 地铁站点换乘图标
    stations_ex=''
    # 记录站点名称，判断换乘站点，不重复添加文本和换乘图标
    stations_name_list=[]
    for line in json_data['subways']['l']:
        line_str='M'
        line_name=line['l_xmlattr']['lb']
        line_isLoop=line['l_xmlattr']['loop']
        line_color=line['l_xmlattr']['lc'].replace('0x','#')
        lbx=line['l_xmlattr']['lbx']
        lby=line['l_xmlattr']['lby']
        # 线路名称：修正，去除含括号的内容（作为class时会报错，因为class名不能包含括号）
        line_name=line_name.split('(')[0]
        line_id=line['l_xmlattr']['lid']
        line_id=re.sub(r'^地铁|^轨道交通|\([^)]*\)', '', line_id)
        stations_text+=f'<rect class="line line-{line_name}" x="{lbx-7}" y="{lby}" width="{len(line_id)*14+7}" height="20" fill="{line_color}" font-size="14"/>'
        stations_text+=f'<text class="line line-{line_name}" x="{lbx}" y="{lby+16}" fill="#fff" font-size="14">{line_id}</text>'

        # 路线站点
        is_arc=False  #线路拐点
        for station in line['p']:
            station_name=station["p_xmlattr"]['lb'].split('·')[0]
            x=station['p_xmlattr']['x']
            y=station['p_xmlattr']['y']
            max_x=max(max_x,x)
            max_y=max(max_y,y)
            min_x=min(min_x,x)
            min_y=min(min_y,y)
            rx=station['p_xmlattr'].get('rx',0)
            ry=station['p_xmlattr'].get('ry',0)
            ex=station['p_xmlattr']['ex']
            # 生成路径字符串
            rc=station['p_xmlattr']['rc']
            if rc:
                is_arc=True
                line_str+=f'Q{x} {y}'
                continue
            if is_arc:
                line_str+=f' {x} {y}'
                is_arc=False
            else:
                if line_str!='M':
                    line_str+='L'
                line_str+=f'{x} {y}'
            # 生成站点名称字符串
            if station_name:
                # 不重复添加文本和站点图标
                if station_name not in stations_name_list:
                    stations_text+=f'<text id="station-{station_name}" class="line line-{line_name}" x="{x+rx}" y="{y+ry+12}" fill="#000" font-size="14">{station_name}</text>'
                    stations_str+=f'<circle class="line line-{line_name}" cx="{x}" cy="{y}" r="4" fill="#fff" stroke="{line_color}" stroke-width="1"/>'
                # 换乘站点图标
                if ex:
                    if station_name not in stations_name_list:
                        # 第一次添加换乘图标
                        stations_ex+=f'<use id="station-{station_name}" class="line line-{line_name}" href="#change" x="{x-5}" y="{y-5}"/>'
                    else:
                        # 其他换乘路线增加class名
                        add_str=f'line-{line_name}'
                        pattern = rf'(id="station-{station_name}"[^>]*?class=")([^"]*)(")'
                        callback_func = add_class(add_str)
                        stations_ex = re.sub(pattern, callback_func, stations_ex)
                        stations_text=re.sub(pattern, callback_func, stations_text)
                stations_name_list.append(station_name)
        # 判断是否环线
        if line_isLoop:
            line_str+='Z'
        path_d=f'<path id="line-{line_name}" class="line line-{line_name}" fill="none" stroke="{line_color}" stroke-width="6" d="{line_str}"/>'
        lines_str+=path_d
    width=max_x-min_x
    height=max_y-min_y
    _height=height*1000//width
    svg=svg_template%(1000,_height,min_x-100,min_y-100,width+200,height+200,lines_str,stations_text,stations_str,stations_ex)
    city_file=current_dir/f'subways-{city_name}.svg'
    with open(city_file,'w',encoding='utf-8') as f:
        f.write(svg)    
        print(f'已生成{city_file}')

if __name__=='__main__':
    subway_index=json.load(open(current_dir/'subway_index.json','r',encoding='utf-8'))
    city_name='shanghai'
    # create_city_subway_svg(city_name)
    index_data=cityList = [['北京市', 'beijing'], ['上海市', 'shanghai'], ['广州市', 'guangzhou'], ['深圳市', 'shenzhen'], ['重庆市', 'chongqing'], ['天津市', 'tianjin'], ['石家庄市', 'shijiazhuang'], ['南京市', 'nanjing'], ['南通市', 'nantong'], ['成都市', 'chengdu'], ['资阳市', 'ziyang'], ['沈阳市', 'shenyang'], ['杭州市', 'hangzhou'], ['武汉市', 'wuhan'], ['鄂州市', 'ezhou'], ['长沙市', 'changsha'], ['湘潭市', 'xiangtan'], ['苏州市', 'suzhou'], ['大连市', 'dalian'], ['长春市', 'changchun'], ['西安市', 'xian'], ['咸阳市', 'xianyang'], ['昆明 市', 'kunming'], ['佛山市', 'foshan'], ['哈尔滨市', 'haerbin'], ['郑州市', 'zhengzhou'], ['许昌市', 'xuchang'], ['宁波市', 'ningbo'], ['无锡市', 'wuxi'], ['温州市', 'wenzhou'], ['常州市', 'changzhou'], ['青岛市', 'qingdao'], ['清远市', 'qingyuan'], ['济南市', 'jinan'], ['南昌市', 'nanchang'], ['福州市', 'fuzhou'], ['东莞市', 'dongguan'], ['南宁市', 'nanning'], ['合肥市', 'hefei'], ['厦门市', 'xiamen'], ['乌鲁木齐市', 'wulumuqi'], ['贵阳市', 'guiyang'], ['兰州市', 'lanzhou'], ['徐州市', 'xuzhou'], ['呼和浩特市', 'huhehaote'], ['太原市', 'taiyuan'], ['金华市', 'jinhua'], ['洛阳市', 'luoyang'], ['绍兴市', 'shaoxing'], ['芜湖市', 'wuhu'], ['台州市', 'taizhou'], ['滁州市', 'chuzhou']]
    for city in index_data:
        cename=city[1]
        # 仅更新指定城市的地铁图
        # 注释后即可更新所有城市的地铁图
        if cename==city_name:
            create_city_subway_svg(cename)


