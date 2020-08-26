"""批量修改服务器密码"""
import paramiko
import configparser
import getpass
import sys
import threading
import argparse
import logging


class ModifyPassword(object):
    """修改密码的类对象"""
    def __init__(self, oldpwd, newpwd, port, username, sec, serverfile):
        self.oldpwd = oldpwd
        self.newpwd = newpwd
        self.sec = sec
        self.serverfile = serverfile
        self.username = username
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
        self.handler = logging.FileHandler('modifypassword.log')
        self.handler.setFormatter(self.log_formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def sevhandler(self):
        """
        读取ini配置文件中服务器的配置信息
        :param sec: ini文件的片段名
        :param serverfile: 配置文件名
        :return: 读取到的服务器列表
        """
        sevinfo_dict = dict()
        serverconfig = configparser.RawConfigParser()
        serverconfig.read(self.serverfile)
        if self.sec == 'all':
            # 获取所有的sections下的所有信息
            secs = serverconfig.sections()
            for sec in secs:
                servers = serverconfig.options(sec)
                for host in servers:
                    sevinfo = serverconfig.get(sec, host)
                    sevinfo_dict[host] = sevinfo
        else:
            servers = serverconfig.options(self.sec)
            for host in servers:
                sevinfo = serverconfig.get(self.sec, host)
                sevinfo_dict[host] = sevinfo
        return sevinfo_dict

    def ssh(self, host):
        try:
            sshclient = paramiko.SSHClient()
            sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshclient.connect(hostname=host,
                              port=self.port,
                              username=self.username,
                              password=self.oldpwd)
            stdin, stdout, stderr = sshclient.exec_command('echo %s | passwd --stdin root' % self.newpwd)
            result = stdout.read()
            if len(result) == 0 and len(stderr.read()) != 0:
                self.logger.error("Host %s exec err: %s" % (host, stderr.read().decode('utf-8')))
                # print("Host %s exec err: %s" % (host, stderr.read().decode('utf-8')))
            else:
                self.logger.info("Host %s exec success" % host)
                # print("Host %s exec success" % host)
        except:
            self.logger.error("Host %s connect failed" % host)
            # print("Host %s connect failed" % host)

    def run(self):
        """启动"""
        sev_dict = self.sevhandler()
        for key, value in sev_dict.items():
            host = value
            a = threading.Thread(target=self.ssh, args=(host, ))
            a.start()


def get_argparse():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="A modify server password client in terminal")
    parser.add_argument('-s', action='store', dest='section', default='all',
                        help='specify a section, default value is all ')
    parser.add_argument('-f', action='store', dest='serverfile', default='serverinfo.ini',
                        help='specify a serverfile, default value is serverinfo.ini')
    parser.add_argument('-p', action='store', dest='port', default=22,
                        help='port connect to server, default value is 22')
    parser.add_argument('-u', action='store', dest='user', default='root',
                        help='user connect to server, default value is root')
    parser.add_argument('-v', action='version', version='%(prog)s 0.1')
    return parser.parse_args()


def main():
    parser = get_argparse()
    sec = parser.section
    serverfile = parser.serverfile
    port = parser.port
    user = parser.user
    oldpwd = getpass.getpass("请输入旧密码：")
    newpassword = getpass.getpass("请输入新密码:")
    newpassword2 = getpass.getpass("请再次输入新密码:")
    if newpassword != newpassword2:
        print("两次密码不一样，重新运行")
        sys.exit(1)
    md_pass = ModifyPassword(oldpwd=oldpwd, newpwd=newpassword2, port=port, username=user,
                             sec=sec, serverfile=serverfile)
    md_pass.run()


if __name__ == '__main__':
    main()