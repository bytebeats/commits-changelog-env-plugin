# commits-changelog-env-plugin

[![GitHub latest commit](https://badgen.net/github/last-commit/bytebeats/commits-changelog-env-plugin)](https://github.com/bytebeats/commits-changelog-env-plugin/commit/)
[![GitHub contributors](https://img.shields.io/github/contributors/bytebeats/commits-changelog-env-plugin.svg)](https://github.com/bytebeats/commits-changelog-env-plugin/graphs/contributors/)
[![GitHub issues](https://img.shields.io/github/issues/bytebeats/commits-changelog-env-plugin.svg)](https://github.com/bytebeats/commits-changelog-env-plugin/issues/)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/bytebeats/commits-changelog-env-plugin/)
[![GitHub forks](https://img.shields.io/github/forks/bytebeats/commits-changelog-env-plugin.svg?style=social&label=Fork&maxAge=2592000)](https://github.com/bytebeats/commits-changelog-env-plugin/network/)
[![GitHub stars](https://img.shields.io/github/stars/bytebeats/commits-changelog-env-plugin.svg?style=social&label=Star&maxAge=2592000)](https://github.com/bytebeats/commits-changelog-env-plugin/stargazers/)
[![GitHub watchers](https://img.shields.io/github/watchers/bytebeats/commits-changelog-env-plugin.svg?style=social&label=Watch&maxAge=2592000)](https://github.com/bytebeats/commits-changelog-env-plugin/watchers/)

A Jenkins plugin for inserting the commits changelog into the jenkins build environment.

Jenkins插件, 在构建时通过将提交的更新列表插入 Jenkins 构建环境, 从而实现将提交信息通知给飞书/钉钉机器人.

Online office software like Lark(Feishu)/DingTalk feature notification bots.

Testers want to know what bugs were fixed, what features added, what functions modified or refactored when jenkins building started.

Jenkins build environment supports build task variables like [BUILD_NUMBER/BUILD_URL, JOB_NAME/JOB_URL, JENKINS_HOME/JENKINS_URL](https://wiki.jenkins.io/display/JENKINS/Building+a+software+project#Buildingasoftwareproject-belowJenkinsSetEnvironmentVariables)

But Jenkins do not know commits.

So Inserting commits changelog into build environment is a solution.

## How?

Is there any way to generate commits changelog? A Jenkins build plugin ?!

This project is an implementation that a jenkins plugin generates commits changelog and insert it into current build environment.

## Where is the jenkins plugin?

here [commits-changelog-env-inserter.hpi](/artifact/commits-changelog-env-inserter.hpi) is. 

## Can I build my own hpi file?

Of course. Here is how: 
* install maven first, if you haven't. run `brew install maven` on Terminal, macOS.
* In root directory of this project, run `mvn verify`.
* in `/target/`, you'll see `commits-changelog-env-inserter.hpi` is generated.
* Then in Jenkins, `Manage Jenkins` -> `System Configuration` -> `Manage Plugins` -> `Advanced` Tab -> `Upload Plugin`, `choose file` and then `Upload`.
* Then in Jenkins/build tasks, `Configure` -> `Build Environment`, you'll see `Add Commits Changelog Information to the Build Environment`, check it and configure as help described.
* If you run into anything about maven configure, Google it!
* If you run into anything about Jenkins permissions, Consult your manager!

## How to send the commit changelog to Lark bot? 如何将提交记录发送给飞书机器人?

Check [lark_commits_changelog_bot.py](/lark_commits_changelog_bot.py)

## Stargazers over time
[![Stargazers over time](https://starchart.cc/bytebeats/commits-changelog-env-plugin.svg)](https://starchart.cc/bytebeats/commits-changelog-env-plugin)

## Github Stars Sparklines
[![Sparkline](https://stars.medv.io/bytebeats/commits-changelog-env-plugin.svg)](https://stars.medv.io/bytebeats/commits-changelog-env-plugin)

## Contributors
[![Contributors over time](https://contributor-graph-api.apiseven.com/contributors-svg?chart=contributorOverTime&repo=bytebeats/commits-changelog-env-plugin)](https://www.apiseven.com/en/contributor-graph?chart=contributorOverTime&repo=bytebeats/commits-changelog-env-plugin)

## MIT License

    Copyright (c) 2022 Chen Pan

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
