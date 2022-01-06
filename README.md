# commits-changelog-env-plugin
A Jenkins plugin for inserting the commits changelog into the jenkins build environment.

Online office software like Lark(Feishu)/DingTalk feature notification bots.

Testers want to know what bugs were fixed, what features added, what functions modified or refactored when jenkins building started.

Jenkins build environment supports build task variables like [BUILD_NUMBER/BUILD_URL, JOB_NAME/JOB_URL, JENKINS_HOME/JENKINS_URL](https://wiki.jenkins.io/display/JENKINS/Building+a+software+project#Buildingasoftwareproject-belowJenkinsSetEnvironmentVariables)

But Jenkins do not know commits.

So Inserting commits changelog into build environment is a solution.

How?

Is there any way to generate commits changelog? A Jenkins build plugin ?!

This project is an implementation that a jenkins plugin generates commits changelog and insert it into current build environment.

## Where is the jenkins plugin?

here [it](/artifact/commits-changelog-env-inserter.hpi) is.

## Can I build my own hpi file?

Of course. Here is how: 
* install maven first, if you haven't. run `brew install maven` on Terminal, macOS.
* In root directory of this project, run `mvn verify`.
* in `/target/`, you'll see `commits-changelog-env-inserter.hpi` is generated.
* Then in Jenkins, `Manage Jenkins` -> `System Configuration` -> `Manage Plugins` -> `Advanced` Tab -> `Upload Plugin`, `choose file` and then `Upload`.
* Then in Jenkins/build tasks, `Configure` -> `Build Environment`, you'll see `Add Commits Changelog Information to the Build Environment`, check it and configure as help described.
* If you run into anything about maven configure, Google it!
* If you run into anything about Jenkins permissions, Consult your manager!