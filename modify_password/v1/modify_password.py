"""批量修改服务器密码"""
# 连接服务器的库
import paramiko
# 读取配置文件的库
import configparser
# 隐式获取用户输入的库
import getpass
import sys
import threading


def sevhandler(sec, serverfile):
    """
    读取ini配置文件中服务器的配置信息
    :param sec: ini文件的片段名
    :param serverfile: 配置文件名
    :return: 读取到的服务器列表
    """
    sevinfo_dict = dict()
    # 定义configparser对象
    serverconfig = configparser.RawConfigParser()
    # 读取配置文件
    serverconfig.read(serverfile)
    # 读取对应片段下的主机节点
    servers = serverconfig.options(sec)
    # 遍历节点，获取节点的信息，保存至字典
    for host in servers:
        sevinfo = serverconfig.get(sec, host)
        sevinfo_dict[host] = sevinfo
    return sevinfo_dict


def ssh(host, oldpwd, newpwd, port=22, username='root'):
    try:
        # 定义ssh对象
        sshclient = paramiko.SSHClient()
        # 连接服务器时，自动添加到信任策略，无需手动确认
        sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器
        sshclient.connect(hostname=host,
                          port=port,
                          username=username,
                          password=oldpwd)
        # 执行密码修改命令，并捕获输出
        stdin, stdout, stderr = sshclient.exec_command('echo %s | passwd --stdin root' % newpwd)
        result = stdout.read()
        # 根据命令执行输出判断执行结果
        if len(result) == 0 and len(stderr.read()) != 0:
            print("Host %s exec err: %s" % (host, stderr.read().decode('utf-8')))
        else:
            print("Host %s exec success" % host)
    except:
        print("Host %s connect failed" % host)


def main():
    # 注意，直接在Pycharm中运行不了，因为Pycharm不支持getpass
    newpassword = getpass.getpass("请输入新密码:")
    newpassword2 = getpass.getpass("请再次输入新密码:")
    if newpassword != newpassword2:
        print("两次密码不一样，重新运行")
        sys.exit(1)
    sev_dict = sevhandler('ceph', 'serverinfo.ini')
    for key, value in sev_dict.items():
        host = value.split(',')[0]
        oldpwd = value.split(',')[1]
        a = threading.Thread(target=ssh, args=(host, oldpwd, newpassword))
        a.start()

if __name__ == '__main__':
    main()