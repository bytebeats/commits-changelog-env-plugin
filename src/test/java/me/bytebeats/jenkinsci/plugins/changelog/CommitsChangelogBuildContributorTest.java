package me.bytebeats.jenkinsci.plugins.changelog;

import hudson.FilePath;
import hudson.Launcher;
import hudson.model.FreeStyleProject;
import hudson.model.Run;
import hudson.model.TaskListener;
import hudson.tasks.Builder;
import hudson.util.FormValidation;
import jenkins.tasks.SimpleBuildStep;
import org.junit.Rule;
import org.junit.Test;
import org.jvnet.hudson.test.FakeChangeLogSCM;
import org.jvnet.hudson.test.JenkinsRule;

import java.io.IOException;
import java.lang.Exception;

import static org.junit.Assert.*;

/**
 * @Author bytebeats
 * @Email <happychinapc@gmail.com>
 * @Github https://github.com/bytebeats
 * @Created at 2022/1/6 12:11
 * @Version 1.0
 * @Description TO-DO
 */

public class CommitsChangelogBuildContributorTest {
    @Rule
    public JenkinsRule j = new JenkinsRule();

    @Test
    public void testValidation() throws Exception {
        CommitsChangelogBuildContributor.ChangelogEnvironmentContributorDescriptor d =
                new CommitsChangelogBuildContributor.ChangelogEnvironmentContributorDescriptor();

        assertSame(d.doCheckDateFormat("").kind, FormValidation.Kind.OK);
        assertSame(d.doCheckDateFormat("lolno").kind, FormValidation.Kind.ERROR);
        assertSame(d.doCheckDateFormat("yyyy-MM-dd 'at' HH:mm:ss z").kind, FormValidation.Kind.OK);
    }

    @Test
    public void testBuildWithoutEnvironment() throws Exception {
        FreeStyleProject p = j.createFreeStyleProject();
        p.getBuildWrappersList().add(new CommitsChangelogBuildContributor());
        p.getBuildersList().add(new EnvironmentCheckBuilder(null));
        j.buildAndAssertSuccess(p);
    }

    @Test
    public void testBuildWithEnvironment() throws Exception {
        FreeStyleProject p = j.createFreeStyleProject();

        FakeChangeLogSCM scm = new FakeChangeLogSCM();
        p.setScm(scm);
        j.buildAndAssertSuccess(p);

        scm.addChange().withAuthor("bytebeats").withMsg("initial commit");

        CommitsChangelogBuildContributor c = new CommitsChangelogBuildContributor();
        c.setEntryFormat("%s | %3$s"); // format: author | message
        p.getBuildWrappersList().add(c);
        p.getBuildersList().add(new EnvironmentCheckBuilder("bytebeats | initial commit"));

        j.buildAndAssertSuccess(p);
    }

    public static class EnvironmentCheckBuilder extends Builder implements SimpleBuildStep {

        private final String expected;

        public EnvironmentCheckBuilder(String expected) {
            this.expected = expected;
        }

        @Override
        public void perform(Run<?, ?> run, FilePath workspace, Launcher launcher, TaskListener listener) throws InterruptedException, IOException {
            if (expected == null) {
                assertNull("Not expecting " + CommitsChangelogBuildContributor.SCM_CHANGELOG + " in environment", run.getEnvironment(listener).get(CommitsChangelogBuildContributor.SCM_CHANGELOG));
                assertNull("Not expecting " + CommitsChangelogBuildContributor.MAX_DISPLAYED_CHANGES + " in environment", run.getEnvironment(listener).get(CommitsChangelogBuildContributor.MAX_DISPLAYED_CHANGES));
                assertNull("Not expecting " + CommitsChangelogBuildContributor.SCM_DATE_FORMAT + " in environment", run.getEnvironment(listener).get(CommitsChangelogBuildContributor.SCM_DATE_FORMAT));
                assertNull("Not expecting " + CommitsChangelogBuildContributor.USE_API_TOKEN_MODE + " in environment", run.getEnvironment(listener).get(CommitsChangelogBuildContributor.USE_API_TOKEN_MODE));
                assertNull("Not expecting " + CommitsChangelogBuildContributor.AFFECTED_FILES_INCLUDED + " in environment", run.getEnvironment(listener).get(CommitsChangelogBuildContributor.AFFECTED_FILES_INCLUDED));
                assertNull("Not expecting " + CommitsChangelogBuildContributor.JENKINS_VISITOR + " in environment", run.getEnvironment(listener).get(CommitsChangelogBuildContributor.JENKINS_VISITOR));
                assertNull("Not expecting " + CommitsChangelogBuildContributor.LARK_WEBHOOK + " in environment", run.getEnvironment(listener).get(CommitsChangelogBuildContributor.LARK_WEBHOOK));
                assertNull("Not expecting " + CommitsChangelogBuildContributor.LARK_KEY + " in environment", run.getEnvironment(listener).get(CommitsChangelogBuildContributor.LARK_KEY));
            } else {
                assertEquals("Expecting " + CommitsChangelogBuildContributor.SCM_CHANGELOG + " to contain string", expected, run.getEnvironment(listener).get(CommitsChangelogBuildContributor.SCM_CHANGELOG));
                assertEquals("Expecting " + CommitsChangelogBuildContributor.MAX_DISPLAYED_CHANGES + " to contain string", expected, run.getEnvironment(listener).get(CommitsChangelogBuildContributor.MAX_DISPLAYED_CHANGES));
                assertEquals("Expecting " + CommitsChangelogBuildContributor.SCM_DATE_FORMAT + " to contain string", expected, run.getEnvironment(listener).get(CommitsChangelogBuildContributor.SCM_DATE_FORMAT));
                assertEquals("Expecting " + CommitsChangelogBuildContributor.USE_API_TOKEN_MODE + " to contain string", expected, run.getEnvironment(listener).get(CommitsChangelogBuildContributor.USE_API_TOKEN_MODE));
                assertEquals("Expecting " + CommitsChangelogBuildContributor.AFFECTED_FILES_INCLUDED + " to contain string", expected, run.getEnvironment(listener).get(CommitsChangelogBuildContributor.AFFECTED_FILES_INCLUDED));
                assertEquals("Expecting " + CommitsChangelogBuildContributor.JENKINS_VISITOR + " to contain string", expected, run.getEnvironment(listener).get(CommitsChangelogBuildContributor.JENKINS_VISITOR));
                assertEquals("Expecting " + CommitsChangelogBuildContributor.LARK_WEBHOOK + " to contain string", expected, run.getEnvironment(listener).get(CommitsChangelogBuildContributor.LARK_WEBHOOK));
                assertEquals("Expecting " + CommitsChangelogBuildContributor.LARK_KEY + " to contain string", expected, run.getEnvironment(listener).get(CommitsChangelogBuildContributor.LARK_KEY));
            }
        }
    }
}
