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

# commit message types, if any
COMMITS_CHANGELOG_TYPES = {"ADD": "增加", "NEW": "新建", "FIX": "修复", "OPT": "优化", "MOD": "重构"}
# commit message business types, if any
COMMITS_MESSAGE_KEYWORDS = {"Quote": "行情", "Portfolio": "自选", "Trade": "交易", "IPO": "IPO", "Community": "社区",
                            "Open": "开户", "Login": "登录", "Discovery": "发现", "Asset Manage": "资管", "Mine": "我的",
                            "Setting": "设置", "Place Order": "下单", "Order": "订单", "Modify Order": "改单"}
# 获取Jenkins变量
JOB_NAME = str(os.getenv("JOB_NAME"))
# where to download apk?
ARTIFACT_URL = "https://x.y.z/android/index_{}.html".format(JOB_NAME)
JENKINS_URL = str(os.getenv("JENKINS_URL"))
if JENKINS_URL == 'None':
    # your own jenkins server url.
    JENKINS_URL = "http://x.y.z.a/"

GIT_URL = str(os.getenv("GIT_URL"))
GIT_BRANCH = str(os.getenv("GIT_BRANCH"))
JOB_URL = str(os.getenv("JOB_URL"))
BUILD_URL = str(os.getenv("BUILD_URL"))
BUILD_URL_CONSOLE = BUILD_URL + "console"
BUILD_ID = str(os.getenv("BUILD_ID"))
BUILD_NUMBER = str(os.getenv("BUILD_NUMBER"))
BUILD_CAUSE = str(os.getenv("BUILD_CAUSE"))
BUILD_ONLINE = str(os.getenv("BUILD_ONLINE"))
APP_GLOBAL_TYPE = str(os.getenv("APP_GLOBAL_TYPE"))
SCM_CHANGELOG = str(os.getenv("SCM_CHANGELOG"))
BUILD_CAUSE_MANUALTRIGGER = str(os.getenv("BUILD_CAUSE_MANUALTRIGGER"))
LARK_WEBHOOK = str(os.getenv("LARK_WEBHOOK"))

if 'None' == LARK_WEBHOOK:
    # your own Lark Bot Webhook
    LARK_WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/xxxxyyzzaaelfajsd'

LARK_KEY = str(os.getenv("LARK_KEY"))
# 默认为空, 以跳过签名验证
# if 'None' == LARK_KEY:
#     LARK_KEY = ''

JENKINS_VISITOR = str(os.getenv("JENKINS_VISITOR"))

if 'None' == JENKINS_VISITOR:
    # 默认用户, 因为3个月需要修改一次密码, 此处可能经常会遇到密码过期问题
    # your own username and password of Jenkins account.
    JENKINS_VISITOR_USERNAME = "username"
    JENKINS_VISITOR_PASSWORD = "password"
else:
    jenkins_visitor = JENKINS_VISITOR.split("&&&")
    JENKINS_VISITOR_USERNAME = jenkins_visitor[0]
    JENKINS_VISITOR_PASSWORD = jenkins_visitor[1]

print("env variables: \n{}".format("\n".join("{} == {}".format(key, value) for key, value in os.environ.items())))

# 判断日志内容
if SCM_CHANGELOG == 'None':
    SCM_CHANGELOG = EMPTY_CHANGE_LOG_MESSAGE
    print("SCM_CHANGELOG is empty")
else:
    print("SCM_CHANGELOG is not empty")
    pass


def build_notification():
    # replace your own webhook
    url = LARK_WEBHOOK
    method = 'post'
    headers = {
        'Content-Type': 'application/json'
    }
    jenkins_server = None
    try:
        # 连接jenkins
        jenkins_server = jenkins.Jenkins(url=JENKINS_URL, username=JENKINS_VISITOR_USERNAME,
                                         password=JENKINS_VISITOR_PASSWORD)
    except Exception as e:
        jenkins_error = "Jenkins服务器连接异常, 请尽快处理. \n 详细异常信息如下:\n{}".format(str(e))
        print(jenkins_error)
        json_payload = json_content_payload(jenkins_error)
        print(json_payload)
        requests.request(method=method, url=url, headers=headers, json=json_payload)
        pass

    # 什么样的 username + password 不受定期修改密码的干扰?
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
    if EMPTY_CHANGE_LOG_MESSAGE == SCM_CHANGELOG:
        formatted_change_log = EMPTY_CHANGE_LOG_MESSAGE
    else:
        change_logs = defaultdict(list)
        commits = SCM_CHANGELOG.split("--- ")
        for cmt in commits:
            if cmt != "":
                commit = cmt.strip()
                size = len(commit)
                last_left_bracket_idx = commit.rindex("(", 0, size)
                last_right_bracket_idx = commit.rindex(")", 0, size)
                message = commit[0:last_left_bracket_idx]
                author_timestamp = commit[last_left_bracket_idx + 1: last_right_bracket_idx].split(" committed at ")
                author = author_timestamp[0]
                timestamp = author_timestamp[1]
                edit_type = commit[0:3].upper()
                edit_type_zh = COMMITS_CHANGELOG_TYPES[edit_type]
                msg = "{} - {}({})".format(message, author, timestamp)
                for k, v in COMMITS_MESSAGE_KEYWORDS.items():
                    if message.find(k.lower()) >= 0 or message.find(k.upper()) >= 0 or message.find(v) >= 0:
                        msg += ' **-{}-**'.format(v)
                        change_logs[edit_type_zh].append(msg)
        #  格式化已经分类提交词典
        formatted_change_log = str("\n".join(
            ["**{}**:\n--- {}".format(type_zh, "\n> ".join(commits)) for type_zh, commits in change_logs.items()]))

    content_failed = '#### ' + JOB_NAME + ' - Build # ' + BUILD_NUMBER + ' 开始构建\n' + \
                     '**编译状态**: ' + str(build_result) + '</font> \n' + \
                     '**正在编译**: ' + str(building) + '\n' + \
                     '**编译版本**: ' + APP_GLOBAL_TYPE + '\n' + \
                     '**正式版本**: ' + BUILD_ONLINE + '\n' + \
                     '**触发类型**: ' + "{}, {}".format(BUILD_CAUSE, str(causes[0])) + '\n' + \
                     '**手动触发**: ' + BUILD_CAUSE_MANUALTRIGGER + '\n' + \
                     '**Jenkins版本**: ' + str(jenkins_version) + '\n' + \
                     '**Git地址**: ' + GIT_URL + '\n' + \
                     '**Git分支**: ' + GIT_BRANCH + '\n' + \
                     '**上次编译耗时**: ' + str(estimated_duration) + 'ms\n' + \
                     '**本次编译已耗时**: ' + str(duration) + 'ms\n' + \
                     '**编译日志**:  稍后请[查看详情](' + BUILD_URL_CONSOLE + ') \n' + \
                     '**最新提交记录**: \n\n' + \
                     str(formatted_change_log) + '\n' + \
                     '> ##### TigerTrade Android \n '

    content_finished = '#### ' + JOB_NAME + ' - Build # ' + BUILD_NUMBER + ' 开始构建\n' + \
                       '**编译状态**: ' + str(build_result) + '\n' + \
                       '**正在编译**: ' + str(building) + '\n' + \
                       '**编译版本**: ' + APP_GLOBAL_TYPE + '\n' + \
                       '**正式版本**: ' + BUILD_ONLINE + '\n' + \
                       '**触发类型**: ' + "{}, {}".format(BUILD_CAUSE, str(causes[0])) + '\n' + \
                       '**手动触发**: ' + BUILD_CAUSE_MANUALTRIGGER + '\n' + \
                       '**Jenkins版本**: ' + str(jenkins_version) + '\n' + \
                       '**Git地址**: ' + GIT_URL + '\n' + \
                       '**Git分支**: ' + GIT_BRANCH + '\n' + \
                       '**上次编译耗时**: ' + str(estimated_duration) + 'ms\n' + \
                       '**本次编译已耗时**: ' + str(duration) + 'ms\n' + \
                       '**编译日志**: 稍后请[查看详情](' + BUILD_URL_CONSOLE + ') \n' + \
                       '**最新提交记录**: \n\n' + \
                       str(formatted_change_log) + '\n' + \
                       '> ##### TigerTrade Android \n '

    if build_result == 'SUCCESS':
        lark_notification_content = content_finished
    else:
        lark_notification_content = content_failed

    print(lark_notification_content)

    json_payload = json_content_payload(lark_notification_content)
    print(json_payload)
    requests.request(method=method, url=url, headers=headers, json=json_payload)


def sign_from(timestamp):
    # webhook 签名校验密钥
    secret = LARK_KEY
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


def json_content_payload(notification_content):
    if 'None' == LARK_KEY:
        json_content = {
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
                        "content": notification_content,
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
                        },
                        {
                            # button attributes
                            "tag": "button",
                            "text": {
                                "content": "下载Apk",
                                "tag": "lark_md"
                            },
                            "url": ARTIFACT_URL,
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
    else:
        timestamp = str(round(time.time()))
        sign = sign_from(timestamp)
        json_content = {
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
                        "content": notification_content,
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
                        },
                        {
                            # button attributes
                            "tag": "button",
                            "text": {
                                "content": "下载Apk",
                                "tag": "lark_md"
                            },
                            "url": ARTIFACT_URL,
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
    return json_content


if __name__ == "__main__":
    build_notification()
