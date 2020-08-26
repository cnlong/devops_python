import configparser
serverconfig = configparser.RawConfigParser()
# 读取配置文件
serverconfig.read('serverinfo.ini')
print(serverconfig.sections())
serverconfig.options('all')