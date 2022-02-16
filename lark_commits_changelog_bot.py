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
import datetime as dt

from jsonpath import jsonpath
from collections import defaultdict

EMPTY_CHANGE_LOG_MESSAGE = "- No changes"

DATA_TIME_PATTERN = '%Y-%m-%d %H:%M:%S'

COMMITS_CHANGELOG_TYPES = {"ADD": "增加", "NEW": "新建", "FIX": "修复", "OPT": "优化", "MOD": "重构"}
COMMITS_MESSAGE_KEYWORDS = {"Quote": "行情", "Portfolio": "自选", "Trade": "交易", "IPO": "IPO", "Community": "社区",
                            "Open": "开户", "Login": "登录", "Discovery": "发现", "Asset Manage": "资管", "Mine": "我的",
                            "Setting": "设置", "Place Order": "下单", "Order": "订单", "Modify Order": "改单"}
# 获取Jenkins变量
JOB_NAME = str(os.getenv("JOB_NAME"))
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
GIT_COMMIT = str(os.getenv("GIT_COMMIT"))
BUILD_NUMBER = str(os.getenv("BUILD_NUMBER"))
BUILD_CAUSE = str(os.getenv("BUILD_CAUSE"))
BUILD_ONLINE = str(os.getenv("BUILD_ONLINE"))

RUN_CHANGES_DISPLAY_URL = str(os.getenv("RUN_CHANGES_DISPLAY_URL"))

APP_GLOBAL_TYPE = str(os.getenv("APP_GLOBAL_TYPE"))

ARTIFACT_URL = "https://mobile.tigerbrokers.net/android/index_{}.html".format(JOB_NAME)

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

USE_API_TOKEN_MODE = str(os.getenv("USE_API_TOKEN_MODE"))

SCM_CHANGELOG_COUNT = int(str(os.getenv("SCM_CHANGELOG_COUNT")))
MAX_DISPLAYED_CHANGES = int(str(os.getenv("MAX_DISPLAYED_CHANGES")))
SCM_DATE_FORMAT = str(os.getenv("SCM_DATE_FORMAT"))

BUILD_START_TIME = str(os.getenv("BUILD_START_TIME"))
# in millisecond
BUILD_TIMESTAMP = int(BUILD_START_TIME)

JENKINS_VISITOR = str(os.getenv("JENKINS_VISITOR"))

if 'None' == JENKINS_VISITOR:
    # 默认用户, 因为3个月需要修改一次密码, 此处可能经常会遇到密码过期问题
    JENKINS_VISITOR_USERNAME = "username"
    if 'true' == USE_API_TOKEN_MODE:
        JENKINS_VISITOR_TOKEN = "your api token"
    else:
        JENKINS_VISITOR_TOKEN = "password%^"

else:
    jenkins_visitor = JENKINS_VISITOR.split(":")
    JENKINS_VISITOR_USERNAME = jenkins_visitor[0]
    JENKINS_VISITOR_TOKEN = jenkins_visitor[1]

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
    notification_summary = format_notification_summary()

    print(notification_summary)

    formatted_change_log = format_scm_changelog()

    print('formatted_change_log: \n{}'.format(formatted_change_log))

    scm_content = format_scm_content(formatted_change_log)
    print('scm_content: \n{}'.format(scm_content))
    jenkins_server = None
    try:
        # 连接jenkins
        if 'true' == USE_API_TOKEN_MODE:
            idx = JENKINS_URL.rindex("//")
            http_mode = JENKINS_URL[0:idx]
            host = JENKINS_URL[idx + 2:len(JENKINS_URL)]
            # "http://username:api-token@url-host"
            jenkins_url = "{}//{}:{}@{}".format(http_mode, JENKINS_VISITOR_USERNAME, JENKINS_VISITOR_TOKEN, host)
            print("jenkins_url: {}".format(jenkins_url))
            jenkins_server = jenkins.Jenkins(url=jenkins_url)
        else:
            jenkins_server = jenkins.Jenkins(url=JENKINS_URL, username=JENKINS_VISITOR_USERNAME,
                                             password=JENKINS_VISITOR_TOKEN)

        print('jenkins server connected')
    except Exception as e:
        jenkins_error = "Jenkins服务器连接异常, 请尽快处理. \n 详细异常信息如下:\n{}".format(str(e))
        print('jenkins_error: {}'.format(jenkins_error))
        json_payload = json_content_payload(notification_summary, jenkins_error, scm_content)
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

    duration = jsonpath(build_info_jsonobj, '$.duration')
    estimated_duration = jsonpath(build_info_jsonobj, '$.estimatedDuration')
    # 获取任务触发原因
    causes = jsonpath(build_info_jsonobj, '$.actions..shortDescription')

    notification_content = '**次要信息**: \n' + \
                           '正在构建: ' + str(building) + '\n' + \
                           '正式版本: ' + BUILD_ONLINE + '\n' + \
                           '触发类型: ' + "{}, {}".format(BUILD_CAUSE, str(causes[0])) + '\n' + \
                           '手动触发: ' + BUILD_CAUSE_MANUALTRIGGER + '\n' + \
                           'Jenkins版本: ' + str(jenkins_version) + '\n' + \
                           'Git地址: ' + GIT_URL + '\n' + \
                           '上次构建耗时: ' + str(estimated_duration) + 's\n' + \
                           '本次构建已耗时: ' + str(duration) + 's\n' + \
                           '构建日志: 稍后请[查看详情](' + BUILD_URL_CONSOLE + ') \n'

    print('notification_content: \n{}'.format(notification_content))

    json_payload = json_content_payload(notification_summary, notification_content, scm_content)
    requests.request(method=method, url=url, headers=headers, json=json_payload)
    print('request: emitted\n')


def sign_from(timestamp):
    # webhook 签名校验密钥
    secret = LARK_KEY
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


def format_time_delta(timestamp):
    second_diff = BUILD_TIMESTAMP / 1000 - timestamp
    # 1 day
    if second_diff > 60 * 60 * 24:
        time_delta = time.strftime('%Y-%m-%d', time.localtime(timestamp))
    elif second_diff > 60 * 60:
        time_delta = '{}h ago'.format(int(second_diff / 60 / 60))
    elif second_diff > 60:
        time_delta = '{}m ago'.format(int(second_diff / 60))
    else:
        time_delta = '{}s ago'.format(int(second_diff))
    return time_delta


def format_scm_changelog():
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
                # str yyyy-MM-DD HH:mm:ss
                dt_str = author_timestamp[1].strip()
                # int, in seconds
                timestamp = convert_to_timestamp(dt_str, DATA_TIME_PATTERN)
                # like:  10 s ago
                ts_delta = format_time_delta(timestamp)
                edit_type = commit[0:3].upper()
                if edit_type in COMMITS_CHANGELOG_TYPES:
                    edit_type_zh = COMMITS_CHANGELOG_TYPES[edit_type]
                    msg = ""
                    for k, v in COMMITS_MESSAGE_KEYWORDS.items():
                        if message.find(k.lower()) >= 0 or message.find(k.upper()) >= 0 or message.find(v) >= 0:
                            msg += '-**_{}_**-'.format(v)
                    msg += " {} - {}({})".format(message, author, ts_delta)
                    change_logs[edit_type_zh].append(msg)
        #  格式化已经分类提交词典
        formatted_change_log = str("\n".join(
            ["**{}**:\n\n--- {}".format(type_zh, "\n--- ".join(commits)) for type_zh, commits in
             change_logs.items()]))
    return formatted_change_log


def convert_to_timestamp(dt_str, pattern):
    date_time = dt.datetime.strptime(dt_str, pattern)
    # in seconds
    timestamp = dt.datetime.timestamp(date_time)
    return int(timestamp)


def format_notification_summary():
    formatted_build_time = time.strftime(DATA_TIME_PATTERN, time.localtime(BUILD_TIMESTAMP / 1000))
    return '**' + JOB_NAME + ' - Build # ' + BUILD_NUMBER + ' 开始构建** \n\n' + \
           '**打包类型**: ' + '{}/{}/{}'.format('AppGP', 'AppLite', 'AppGlobal') + '\n' + \
           '**Branch**: ' + GIT_BRANCH + '\n' + \
           '**Commit**: ' + GIT_COMMIT + '\n' + \
           '**Start at**: ' + formatted_build_time + '\n'


def format_scm_content(scm_change_set_content):
    if SCM_CHANGELOG_COUNT > MAX_DISPLAYED_CHANGES:
        change_content = '**最新提交({}/{} commits):** '.format(MAX_DISPLAYED_CHANGES, SCM_CHANGELOG_COUNT) + '\n\n' + \
                         str(scm_change_set_content) + '\n' + \
                         '[查看全部](' + RUN_CHANGES_DISPLAY_URL + ')\n' + \
                         '##### TigerTrade Android \n'
    else:
        change_content = '**最新提交({} commits):** '.format(SCM_CHANGELOG_COUNT) + '\n\n' + \
                         str(scm_change_set_content) + '\n' + \
                         '##### TigerTrade Android \n'
    return change_content


def json_content_payload(notification_summary, notification_secondary, scm_changelogs):
    title_content = 'Jenkins构建通知'
    if 'None' == LARK_KEY:
        json_content = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True,
                    "enable_forward": True
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": notification_summary,
                            "tag": "lark_md"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": scm_changelogs,
                            "tag": "lark_md"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": notification_secondary,
                            "tag": "lark_md"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "content": "构建详情",
                                    "tag": "lark_md"
                                },
                                "url": BUILD_URL,
                                "type": "primary",
                                "value": {}
                            },
                            {
                                # button attributes
                                "tag": "button",
                                "text": {
                                    "content": "下载地址",
                                    "tag": "lark_md"
                                },
                                "url": ARTIFACT_URL,
                                "type": "primary",
                                "value": {}
                            }
                        ],
                        "tag": "action"
                    }],
                "header": {
                    "template": "green",
                    "title": {
                        "content": title_content,
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
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": notification_summary,
                            "tag": "lark_md"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            # fill your own content
                            "content": scm_changelogs,
                            "tag": "lark_md"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": notification_secondary,
                            "tag": "lark_md"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "content": "构建详情",
                                    "tag": "lark_md"
                                },
                                "url": BUILD_URL,
                                "type": "primary",
                                "value": {}
                            },
                            {
                                # button attributes
                                "tag": "button",
                                "text": {
                                    "content": "下载地址",
                                    "tag": "lark_md"
                                },
                                "url": ARTIFACT_URL,
                                "type": "primary",
                                "value": {}
                            }
                        ],
                        "tag": "action"
                    }],
                "header": {
                    "template": "green",
                    "title": {
                        "content": title_content,
                        "tag": "plain_text"
                    }
                }
            }
        }
    return json_content


if __name__ == "__main__":
    build_notification()
