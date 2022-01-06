# coding=utf-8

'''
 * Created by bytebeats on 2022/1/6 : 20:14
 * E-mail: happychinapc@gmail.com
 * Quote: Peasant. Educated. Worker
'''
import os, jenkins, configparser, requests, json, time
import hashlib
import base64
import hmac
from jsonpath import jsonpath

# 获取Jenkins变量
JOB_NAME = str(os.getenv("JOB_NAME"))
BUILD_URL = str(os.getenv("BUILD_URL")) + "console"
BUILD_VERSION = str(os.getenv("BUILD_VERSION"))
JENKINS_HOME = os.getenv("JENKINS_HOME")
BUILD_NUMBER = str(os.getenv("BUILD_NUMBER"))
SCM_CHANGELOG = str(os.getenv("SCM_CHANGELOG"))
WORKSPACE = os.getenv("WORKSPACE")

versionPath = JENKINS_HOME + "\workspace\Version.ini"

# 读取版本号
config = configparser.ConfigParser()
config.read(versionPath)
for key in config.items:
    print(key+":"+config[key])
xxx_Major = config.get("xxx", "xxx_Major", fallback="xxx_Major")
xxx_Minor = config.get("xxx", "xxx_Minor", fallback="xxx_Minor")
xxx_Build = config.get("xxx", "xxx_Build", fallback="xxx_Build")
xxx_Revision = config.get("xxx", "xxx_Revision", fallback="xxx_Revision")
JENKINS_VERSION = xxx_Major + "." + xxx_Minor + "." + xxx_Build+ "." + xxx_Revision

# 判断日志内容
if SCM_CHANGELOG == 'None':
    SCM_CHANGELOG = '- No changes'
    print("empty")
else:
    print("not empty")
    pass

def buildNotification():
    # 连接jenkins
    # your url, username, password of jenkins server
    jenkinsServer = jenkins.Jenkins(url="http://xxx.yyy.zzz:8080", username='xxx', password="yyy")
    build_info = jenkinsServer.get_build_info(JOB_NAME, int(BUILD_NUMBER))
    # dict字典转json数据
    build_info_json = json.dumps(build_info)
    # 把json字符串转json对象
    build_info_jsonobj = json.loads(build_info_json)
    # 获取任务触发原因
    causes = jsonpath(build_info_jsonobj, '$.actions..shortDescription')
    print(causes[0])

    contentFailed = '#### ' + JOB_NAME + ' - Build # ' + BUILD_NUMBER + ' \n' + \
               '##### <font color=#FF0000 size=6 face="黑体">编译状态: ' + BUILD_STATUS + '</font> \n' + \
               '##### **版本类型**: ' + 'Debug' + '\n' + \
               '##### **当前版本**: ' + JENKINS_VERSION + '\n' + \
               '##### **触发类型**: ' + str(causes[0]) + '\n' + \
               '##### **编译日志**:  [查看详情](' + BUILD_URL + ') \n' + \
               '##### **更新记录**: \n' + \
               SCM_CHANGELOG + '\n' + \
               '> ###### TigerTrade Android研发 \n '

    # '##### **关注人**: @186xxxx2487 \n' + \

    contentFinished = '#### ' + JOB_NAME + ' - Build # ' + BUILD_NUMBER + ' \n' + \
                  '##### **编译状态**: ' + BUILD_STATUS + '\n' + \
                  '##### **版本类型**: ' + 'Debug' + '\n' + \
                  '##### **当前版本**: ' + JENKINS_VERSION + '\n' + \
                  '##### **触发类型**: ' + str(causes[0]) + '\n' + \
                  '##### **编译日志**: [查看详情](' + BUILD_URL + ') \n' + \
                  '##### **更新记录**: \n' + \
                  SCM_CHANGELOG + '\n' + \
                  '> ###### TigerTrade Android研发 \n '

    if BUILD_STATUS == 'SUCCESS':
        larkNotificationContent = contentFinished
    else:
        larkNotificationContent = contentFailed

    sendToLarkBot(larkNotificationContent)

def sendToLarkBot(content):
    timestamp = str(round(time.time()))
    secret = "你的密钥"
    # replace your own webhook
    url = 'https://open.feishu.cn/open-apis/bot/v2/hook/f8ce052a-5773-4d91-aab0-fe3e4a263f70'
    method = 'post'
    headers = {
        'Content-Type': 'application/json'
    }
    json = {
        "timestamp": timestamp,
        "sign": gen_sign(timestamp, secret),
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True
            },
            "elements": [{
                "tag": "div",
                "text": {
                # fill your own content
                    "content": content,
                    "tag": "lark_md"
                }
            }, {
                "actions": [
                {
                # button attributes
                    "tag": "button",
                    "text": {
                        "content": "构建报告",
                        "tag": "lark_md"
                    },
                    "url": JOB_URL,
                    "type": "default",
                    "value": {}
                },
                {
                # button attributes
                    "tag": "button",
                    "text": {
                        "content": "下载地址",
                        "tag": "lark_md"
                    },
                    "url": "https://mobile.tigerbrokers.net/android/index_"+JOB_NAME+".html",
                    "type": "default",
                    "value": {}
                }
                ],
                "tag": "action"
            }],
            "header": {
                "title": {
                # lark notification card title
                    "content": "dev分支编译通知",
                    "tag": "plain_text"
                }
            }
        }
    }
    requests.request(method=method, url=url, headers=headers, json=json)

def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')

    return sign

if __name__ == "__main__":
    buildNotification()