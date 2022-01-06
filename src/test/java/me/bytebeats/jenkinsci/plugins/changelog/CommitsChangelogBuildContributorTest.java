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
                assertNull("Not expecting SCM_CHANGELOG in environment", run.getEnvironment(listener).get("SCM_CHANGELOG"));
            } else {
                assertEquals("Expecting SCM_CHANGELOG to contain string", expected, run.getEnvironment(listener).get("SCM_CHANGELOG"));
            }
        }
    }
}
