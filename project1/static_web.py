import socket
import threading
import sys
import logging
import framework


class HttpSrever(object):
    # 初始化函数
    def __init__(self, port):
        # tcp通信工具套接字的创建
        ser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 使得端口可以复用
        ser_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # 绑定服务器端口
        ser_socket.bind(("", port))
        # 设置监听最大监听数为128
        ser_socket.listen(128)
        # 初始化对象ser_socket
        self.ser_socket = ser_socket

    # 设置启动函数，创建线程
    def start(self):
        # 等待客户端的连接请求
        new_socket, client_addr = self.ser_socket.accept()
        print("有新的客户连接进来了")
        # 创建线程实现服务器一对多连接客户
        t1 = threading.Thread()
        # 给主线程设置守护
        t1.setDaemon(True)
        # 启动线程
        t1.start()

    @staticmethod
    # 处理客户端发来的数据
    def handle_client(new_socket):
        # 新定义的套接字所能接受的数据大小
        recv_info = new_socket.recv(4096)
        print(recv_info.decode('utf-8'))
        # 对这个接受信息进行判断客户在线否
        if not recv_info:
            print("客户关闭了浏览器")
            return
        # 将收到的信息进行以空格分割，第二个就是客户需要的页面路径
        recv_list = recv_info.split(" ", maxsplit=2)
        # 将接受数据第二个数据传给变量recv_path
        recv_path = recv_list[1]
        # 对用户输入进行判断，若输入为空，则返回给客户首页页面
        if recv_path == "":
            recv_path = "/index.html"
        '''判断是动态资源请求还是静态'''
        if recv_path.endswith(".html"):
            '''这里是动态资源请求，交给框架处理'''
            # 通过日志记录客户端请求的页面路径
            logging.info("客户请求的动态页面路径是：", recv_path)
            # 将客户端请求的页面路径用字典的方式装起来，进行包间传参
            env = {
                "recv_path":recv_path
            }
            # 从框架的路由中获取处理函数获取响应状态、响应头、响应体传参使用
            status, heads, response_body = framework.handle_request(env)
            # 响应行拼接响应状态
            response_line = "HTTP/1.1 %s\r\n" % status
            # 响应头
            response_head = ""
            # 因为页面的响应头不止一个数据，
            for head in heads:
                response_head += "%s: %s\r\n" % head
            # 将响应数据进行整合并且编码
            response_data = (response_line + response_head + "\r\n" + response_body).encode("utf-8")
            # 通过新的套接字向客户端发送给响应报文
            new_socket.send(response_data)
            # 发送完了需将新创建的套接字关闭
            new_socket.close()
        else:
            '''这里是静态资源请求'''
            logging.info("客户端请求的静态页面路径是：", recv_path)
            try:
                # 静态请求判断，防止用户输入的路径不存在
                with open("static"+recv_path, "rb")as file:
                    file_content = file.read()
            # 对用户输入错误进行解决办法
            except Exception as e:
                # 错误的响应行
                response_line = "HTTP/1.1 404 not found\r\n"
                # 错误的响应头
                response_head = "Server: HjjW/9.0\r\n"
                # 错误的响应体，需要通过打开错误页面数据返回
                with open("static/error.html", "rb")as er_file:
                    er_file_content = er_file.read()
                # 进行赋值给response_body美观一点
                response_body = er_file_content
                # 将错误响应数据整合并且编码
                response_data = (response_line + response_head + "\r\n").encode("utf-8") + response_body
                # 新的套接字发送给客户端
                new_socket.send(response_data)
                # 关闭新的套接字
                new_socket.close()
            else:
                # 正确响应行
                response_line = "HTTP/1.1 200 ok\r\n"
                # 正确的响应头数据
                response_head = "Server: HjjW/9.0\r\n"
                # 直接打开了正确的数据赋值给response_body
                response_body = file_content
                # 正确页面的响应报文整合并且编码
                response_data = (response_line + response_head + "\r\n").encode("utf-8") + response_body
                # 新的套接字向客户端发送数据
                new_socket.send(response_data)
                # 关闭新的套接字
                new_socket.close()


def judge_port():
    if len(sys.argv) != 2:
        logging.warning("用户输入命令的参数不是两个")
        print("The command usage:python3 xxx.py port_id")
        return
    elif not sys.argv[1].isdigit():
        logging.warning("用户输入的第二个参数不是数字")
        print("The command usage:python3 xxx.py port_id")
        return
    port = int(sys.argv[1])
    user1 = HttpSrever(port)
    user1.start()


if __name__ == '__main__':
    judge_port()





