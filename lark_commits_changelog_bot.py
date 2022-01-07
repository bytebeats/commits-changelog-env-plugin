#!/usr/bin/env python
# -*- encoding:utf-8 -*-
# coding=utf-8

"""
 * Created by bytebeats on 2022/1/6 : 20:14
 * E-mail: happychinapc@gmail.com
 * Quote: Peasant. Educated. Worker
"""
import base64
import hashlib
import hmac
import jenkins
import json
import os
import requests
import time

from jsonpath import jsonpath
from collections import defaultdict

EMPTY_CHANGE_LOG_MESSAGE = "- No changes"

# 获取Jenkins变量
JOB_NAME = str(os.getenv("JOB_NAME"))
JENKINS_URL = str(os.getenv("JENKINS_URL"))
if JENKINS_URL == 'None':
# default jenkins url
    JENKINS_URL = "http://xxx.xx.xx.xx/"
JOB_URL = str(os.getenv("JOB_URL"))
BUILD_URL = str(os.getenv("BUILD_URL"))
BUILD_URL_CONSOLE = BUILD_URL + "console"
BUILD_ID = str(os.getenv("BUILD_ID"))
BUILD_NUMBER = str(os.getenv("BUILD_NUMBER"))
BUILD_CAUSE = str(os.getenv("BUILD_CAUSE"))
BUILD_ONLINE = str(os.getenv("BUILD_ONLINE"))
SCM_CHANGELOG = str(os.getenv("SCM_CHANGELOG"))
BUILD_CAUSE_MANUALTRIGGER = str(os.getenv("BUILD_CAUSE_MANUALTRIGGER"))

print("env variables: \n{}".format("\n".join("{} == {}".format(key, value) for key, value in os.environ.items())))

# 判断日志内容
if SCM_CHANGELOG == 'None':
    SCM_CHANGELOG = EMPTY_CHANGE_LOG_MESSAGE
    print("SCM_CHANGELOG is empty")
else:
    print("SCM_CHANGELOG is not empty")
    pass


def build_notification():
    timestamp = str(round(time.time()))
    # webhook 签名校验密钥
    secret = "your own public key"
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    # replace your own webhook
    url = 'https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxxx'
    method = 'post'
    headers = {
        'Content-Type': 'application/json'
    }
    jenkins_server = None
    try:
        # 连接jenkins
        jenkins_server = jenkins.Jenkins(url=JENKINS_URL, username="xxx", password="yyyxxxzzz")
    except Exception as e:
        jenkins_error = "Jenkins服务器连接异常, 请尽快处理. \n 详细异常信息如下:\n{}".format(str(e))
        json_payload = {
            "timestamp": timestamp,
            "sign": sign,
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
                        "content": jenkins_error,
                        "tag": "lark_md"
                    }
                }, {
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "构建历史",
                                "tag": "lark_md"
                            },
                            "url": JOB_URL,
                            "type": "default",
                            "value": {}
                        },
                        {
                            "tag": "button",
                            "text": {
                                "content": "本次构建",
                                "tag": "lark_md"
                            },
                            "url": BUILD_URL,
                            "type": "default",
                            "value": {}
                        }
                    ],
                    "tag": "action"
                }],
                "header": {
                    "title": {
                        "content": "xxx编译通知",
                        "tag": "plain_text"
                    }
                }
            }
        }
        print(json_payload)
        requests.request(method=method, url=url, headers=headers, json=json_payload)
        pass

    build_info = jenkins_server.get_build_info(JOB_NAME, int(BUILD_NUMBER))
    jenkins_version = jenkins_server.get_version()
    # dict字典转json数据
    build_info_json = json.dumps(build_info)
    # 把json字符串转json对象
    build_info_jsonobj = json.loads(build_info_json)
    # 获取任务触发原因
    building = jsonpath(build_info_jsonobj, '$.building')
    build_result = jsonpath(build_info_jsonobj, '$.result')
    if build_result == 'None':
        build_result = '开始构建'
    duration = jsonpath(build_info_jsonobj, '$.duration')
    estimated_duration = jsonpath(build_info_jsonobj, '$.estimatedDuration')
    # 获取任务触发原因
    causes = jsonpath(build_info_jsonobj, '$.actions..shortDescription')

#     if EMPTY_CHANGE_LOG_MESSAGE == SCM_CHANGELOG:
#         formatted_change_log = EMPTY_CHANGE_LOG_MESSAGE
#     else:
#         change_logs = defaultdict(list)
#         commits = SCM_CHANGELOG.split("--- ")
#         for cmt in commits:
#             if cmt != "":
#                 commit = cmt.strip()
#                 size = len(commit)
#                 last_left_bracket_idx = commit.rindex("(", 0, size)
#                 last_right_bracket_idx = commit.rindex(")", 0, size)
#                 message = commit[0:last_left_bracket_idx]
#                 author_timestamp = commit[last_left_bracket_idx + 1: last_right_bracket_idx].split(" committed at ")
#                 author = author_timestamp[0]
#                 timestamp = author_timestamp[1]
#                 edit_type = commit[0:3].upper()
#                 edit_type_zh = COMMITS_CHANGELOG_TYPES[edit_type]
#                 msg = "{} - {}({})".format(message, author, timestamp)
#                 for k, v in COMMITS_MESSAGE_KEYWORDS.items():
#                     print("{}:{}".format(k, v))
#                     if message.find(str(k).lower()) >= 0 or message.find(str(k).upper()) >= 0 or message.find(
#                             str(v)) >= 0:
#                         print("contains")
#                         msg += v
#                     change_logs[edit_type_zh].append(msg)
#
#         #  格式化已经分类提交词典
#         formatted_change_log = "\n".join(
#             "**{}**:\n--- {}".format(type_zh, "\n> ".join(commits)) for type_zh, commits in
#             change_logs.items())
#         print(formatted_change_log)

    content_failed = '#### ' + JOB_NAME + ' - Build # ' + BUILD_NUMBER + ' 开始构建\n' + \
                     '**编译状态**: ' + build_result + '</font> \n' + \
                     '**正在编译**: ' + building + '\n' + \
                     '**正式版本**: ' + BUILD_ONLINE + '\n' + \
                     '**手动触发**: ' + BUILD_CAUSE_MANUALTRIGGER + '\n' + \
                     '**触发类型**: ' + "{}, {}".format(BUILD_CAUSE, str(causes[0])) + '\n' + \
                     'Jenkins版本: ' + jenkins_version + '\n' + \
                     '**预估耗时**: ' + estimated_duration + '\n' + \
                     '**已编译耗时**: ' + duration + '\n' + \
                     '**编译日志**:  稍后请[查看详情](' + BUILD_URL_CONSOLE + ') \n' + \
                     '**最新提交记录**: \n' + \
                     str(SCM_CHANGELOG) + '\n' + \
                     '> ##### TigerTrade Android \n '
#                      str(formatted_change_log) + '\n' + \

    content_finished = '#### ' + JOB_NAME + ' - Build # ' + BUILD_NUMBER + ' 开始构建\n' + \
                       '**编译状态**: ' + build_result + '\n' + \
                       '**正在编译**: ' + building + '\n' + \
                       '**正式版本**: ' + BUILD_ONLINE + '\n' + \
                       '**手动触发**: ' + BUILD_CAUSE_MANUALTRIGGER + '\n' + \
                       '**触发类型**: ' + "{}, {}".format(BUILD_CAUSE, str(causes[0])) + '\n' + \
                       '**Jenkins版本**: ' + jenkins_version + '\n' + \
                       '**预估耗时**: ' + estimated_duration + '\n' + \
                       '**已编译耗时**: ' + duration + '\n' + \
                       '**编译日志**: 稍后请[查看详情](' + BUILD_URL_CONSOLE + ') \n' + \
                       '**最新提交记录**: \n' + \
                       str(SCM_CHANGELOG) + '\n' + \
                       '> ##### TigerTrade Android \n '
#                        str(formatted_change_log) + '\n' + \

    if build_result == 'SUCCESS':
        lark_notification_content = content_finished
    else:
        lark_notification_content = content_failed

    print(lark_notification_content)

    json_payload = {
        "timestamp": timestamp,
        "sign": sign,
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
                    "content": lark_notification_content,
                    "tag": "lark_md"
                }
            }, {
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "content": "构建历史",
                            "tag": "lark_md"
                        },
                        "url": JOB_URL,
                        "type": "default",
                        "value": {}
                    },
                    {
                        "tag": "button",
                        "text": {
                            "content": "本次构建",
                            "tag": "lark_md"
                        },
                        "url": BUILD_URL,
                        "type": "default",
                        "value": {}
                    }
                ],
                "tag": "action"
            }],
            "header": {
                "title": {
                    "content": "dev分支编译通知",
                    "tag": "plain_text"
                }
            }
        }
    }
    print(json_payload)
    requests.request(method=method, url=url, headers=headers, json=json_payload)


if __name__ == "__main__":
    build_notification()
