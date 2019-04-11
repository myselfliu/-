import pymysql
import json
import logging
route_list = []


def route(path):
    # 装饰器
    def decorator(fn):
        # 当执行装饰器装饰指定函数的时候，把路径和函数添加到路由表
        route_list.append((path, fn))

        def inner():
            # 执行指定函数
            return fn()
        return inner
    # 返回装饰器
    return decorator


# 获取首页数据
@route("/index.html")
def index():    # index=out(index)
    # 响应状态
    status = "200 ok"
    # 响应头
    heads = [("Server", "HjjW/9.0")]
    # 1.打开模板文件，读取数据
    with open("template/index.html", "r")as file:
        file_data = file.read()
    # 处理后的数据,从数据库查询
    coon = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="mysql",
        database="stock_db",
        charset="utf8")
    cs = coon.cursor()
    sql = "select * from info;"
    cs.execute(sql)
    result = cs.fetchall()
    print(result)

    response_body = ""
    for row in result:
        response_body += '''<tr>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td><input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="000007"></td>
                           </tr>''' % row
    # 2.替换模板文件中的模板遍历
    result = file_data.replace("{%content%}", response_body)
    # 返回请求状态信息，请求头请求体
    return status, heads, result


# 个人中心数据接口开发
@route("/center_data.html")
def center_data():
    # 响应状态
    status = "200 ok"
    # 响应头
    heads = [("Server", "HjjW/9.0"), ("Center-Type", "text/html;charset=utf-8")]
    coon = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="mysql",
        database="stock_db",
        charset="utf8")
    # 处理后的数据，从数据库查询
    cs = coon.cursor()
    sql = '''select i.code,i.short,i.chg,i.turnover,i.price,
    i.highs,f.note_info from info as i inner join focus as f on i.id=f.info_id;    
    '''
    cs.execute(sql)
    result = cs.fetchall()
    cs.close()
    coon.close()
    center_data_list = list()
    # 遍历每一行数据转成字典
    for row in result:
        # 创建空的字典
        center_dict = dict()
        center_dict["code"] = row[0]
        center_dict["short"] = row[1]
        center_dict["chg"] = row[2]
        center_dict["turnover"] = row[3]
        center_dict["price"] = row[4]
        center_dict["highs"] = row[5]
        center_dict["note_info"] = row[6]
        # 添加每个字典信息
        center_data_list.append(center_dict)

    # 把列表字典转成json字符串，并在控制台显示
    json_str = json.dumps(center_data_list, ensure_ascii=False)
    print(json_str)
    return status, heads, json_str


def not_found():
    # 响应状态
    status = "404 ont found"
    # 响应头
    heads = [("Server", "HjjW/9.0")]
    # 处理的数据
    response_body = "404  NOT FOUND!!!"

    return status, heads, response_body


# 处理动态资源请求
def handle_request(env):
    # 获取动态资源路径
    request_path = env["recv_path"]
    print("接收到动态资源请求：", request_path)
    # 遍历路由列表，选择执行的函数,不管页面有多少，用户选择了哪个路径就会遍历到相应的路径
    for path, fn in route_list:
        if request_path == path:
            result = fn()
            return result
    else:
        logging.error("没有设置相应的路由找不到页面资源", request_path)
        # 没有找到
        result = not_found()
        return result


