# 城市地铁路线图SVG
> 数据来源：百度地图
```
    # 获取百度地图-城市地铁索引
    https://ditu.baidu.com/?qt=subwayscity
    # 获取百度地图-城市地铁数据
    https://map.baidu.com/?qt=subways&c=340&format=json
    # 页面-百度地图-城市地铁路线图页面：含svg-可手工提取svg
    https://map.baidu.com/subway/%E4%B8%8A%E6%B5%B7%E5%B8%82/@12647363,4121218,15z/ccode%3D340%26cname%3D%25E6%25B7%25B1%25E5%259C%25B3%25E5%25B8%2582
```

- 文件：subways.py
> 获取城市地图索引，源数据保存为：subwayscity.json
>
> 根据城市代码获取地铁数据，源数据保存为json [subways-CITY.json]
>
> 生成每个城市的地铁路线图SVG [subways-CITY.svg]


- 文件：subways.html
> 预览城市地铁图: 选择城市，选择线路，高亮选中线路并置中
> 
> 使用svg-pan-zoom.js 支持缩放平移
>
> 使用 hammer.min.js 支持移动端触摸缩放平移

- 文件：subwayscity.json
- 文件：subways-*.json
- 文件：subways-*.svg
