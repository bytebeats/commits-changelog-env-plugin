package me.bytebeats.jenkinsci.plugins.changelog;

import hudson.EnvVars;
import hudson.Extension;
import hudson.FilePath;
import hudson.Launcher;
import hudson.Util;
import hudson.model.AbstractBuild;
import hudson.model.AbstractProject;
import hudson.model.Run;
import hudson.model.TaskListener;
import hudson.scm.ChangeLogSet;
import hudson.tasks.BuildWrapperDescriptor;
import hudson.util.FormValidation;
import jenkins.tasks.SimpleBuildWrapper;
import org.jenkinsci.plugins.workflow.job.WorkflowRun;
import org.kohsuke.stapler.DataBoundConstructor;
import org.kohsuke.stapler.DataBoundSetter;
import org.kohsuke.stapler.QueryParameter;

import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.IllegalFormatException;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Created by bytebeats on 2022/1/6 : 10:53
 * E-mail: happychinapc@gmail.com
 * Quote: Peasant. Educated. Worker
 */
public class CommitsChangelogBuildContributor extends SimpleBuildWrapper {
    public static final String SCM_CHANGELOG = "SCM_CHANGELOG";
    public static final String SCM_CHANGELOG_COUNT = "SCM_CHANGELOG_COUNT";
    public static final String LARK_WEBHOOK = "LARK_WEBHOOK";
    public static final String LARK_KEY = "LARK_KEY";
    public static final String USE_API_TOKEN_MODE = "USE_API_TOKEN_MODE";
    public static final String AFFECTED_FILES_INCLUDED = "AFFECTED_FILES_INCLUDED";
    public static final String JENKINS_VISITOR = "JENKINS_VISITOR";
    public static final String BUILD_START_TIME = "BUILD_START_TIME";
    public static final String MAX_DISPLAYED_CHANGES = "MAX_DISPLAYED_CHANGES";
    public static final String SCM_DATE_FORMAT = "SCM_DATE_FORMAT";

    private String entryFormat;

    private String lineFormat;

    private String dateFormat;

    private boolean useApiTokenMode;

    private boolean affectedFilesIncluded;

    private String maxDisplayedChanges;

    private String jenkinsVisitor;

    private String larkBotWebhook;

    private String larkBotKey;

    @DataBoundConstructor
    public CommitsChangelogBuildContributor() {
        // need empty constructor so Stapler creates instances
    }

    @DataBoundSetter
    public void setDateFormat(String dateFormat) {
        this.dateFormat = dateFormat;
    }

    @DataBoundSetter
    public void setEntryFormat(String entryFormat) {
        this.entryFormat = entryFormat;
    }

    @DataBoundSetter
    public void setLineFormat(String lineFormat) {
        this.lineFormat = lineFormat;
    }

    @DataBoundSetter
    public void setUseApiTokenMode(boolean useApiTokenMode) {
        this.useApiTokenMode = useApiTokenMode;
    }

    @DataBoundSetter
    public void setAffectedFilesIncluded(boolean affectedFilesIncluded) {
        this.affectedFilesIncluded = affectedFilesIncluded;
    }

    @DataBoundSetter
    public void setMaxDisplayedChanges(String maxDisplayedChanges) {
        this.maxDisplayedChanges = maxDisplayedChanges;
    }

    @DataBoundSetter
    public void setJenkinsVisitor(String jenkinsVisitor) {
        this.jenkinsVisitor = jenkinsVisitor;
    }

    @DataBoundSetter
    public void setLarkBotWebhook(String larkBotWebhook) {
        this.larkBotWebhook = larkBotWebhook;
    }

    @DataBoundSetter
    public void setLarkBotKey(String larkBotKey) {
        this.larkBotKey = larkBotKey;
    }

    public String getEntryFormat() {
        return this.entryFormat;
    }

    public String getLineFormat() {
        return this.lineFormat;
    }

    public String getDateFormat() {
        return this.dateFormat;
    }

    public boolean isUseApiTokenMode() {
        return useApiTokenMode;
    }

    public boolean isAffectedFilesIncluded() {
        return affectedFilesIncluded;
    }

    public String getMaxDisplayedChanges() {
        return maxDisplayedChanges;
    }

    public String getJenkinsVisitor() {
        return jenkinsVisitor;
    }

    public String getLarkBotWebhook() {
        return larkBotWebhook;
    }

    public String getLarkBotKey() {
        return larkBotKey;
    }

    @Override
    public void setUp(Context context, Run<?, ?> build, FilePath workspace, Launcher launcher, TaskListener listener, EnvVars initialEnvironment) throws IOException, InterruptedException {
        StringBuilder sb = new StringBuilder();

        DateFormat df;
        try {
            df = new SimpleDateFormat(Util.fixNull(dateFormat));
        } catch (IllegalArgumentException ex) {
            listener.error("Failed to insert commits changelog into the environment: Illegal date format");
            return;
        }

        int maxChanges = 0;

        try {
            String nonNpe;
            if (maxDisplayedChanges == null) {
                nonNpe = "";
            } else {
                nonNpe = maxDisplayedChanges.trim();
            }
            maxChanges = Integer.parseInt(nonNpe);
        } catch (NumberFormatException nfe) {
            maxChanges = 30;
        }

        AtomicInteger counter = new AtomicInteger();

        try {
            if (build instanceof AbstractBuild<?, ?>) {
                AbstractBuild<?, ?> abstractBuild = (AbstractBuild<?, ?>) build;
                ChangeLogSet cs = abstractBuild.getChangeSet();
                processChangeLogSet(sb, cs, df, maxChanges, counter);
            }

            try {
                if (build instanceof WorkflowRun) {
                    WorkflowRun wfr = (WorkflowRun) build;
                    List<ChangeLogSet<? extends ChangeLogSet.Entry>> changeLogSets = wfr.getChangeSets();
                    for (ChangeLogSet<? extends ChangeLogSet.Entry> changeLogSet : changeLogSets) {
                        processChangeLogSet(sb, changeLogSet, df, maxChanges, counter);
                    }
                }
            } catch (NoClassDefFoundError ncdr) {
                // ignore
            }

        } catch (IllegalFormatException ex) {
            listener.error("Failed to insert commits changelog into the environment: " + ex.getMessage());
            return;
        }

        context.env(BUILD_START_TIME, String.valueOf(build.getTimeInMillis()));

        String value = sb.toString();
        if (!"".equals(value)) {
            context.env(SCM_CHANGELOG, value);
        }

        context.env(SCM_CHANGELOG_COUNT, String.valueOf(counter.get()));
        context.env(MAX_DISPLAYED_CHANGES, String.valueOf(maxChanges));
        context.env(SCM_DATE_FORMAT, Util.fixNull(dateFormat));
        context.env(USE_API_TOKEN_MODE, String.valueOf(useApiTokenMode));

        context.env(AFFECTED_FILES_INCLUDED, String.valueOf(affectedFilesIncluded));

        if (null != jenkinsVisitor && !"".equals(jenkinsVisitor)) {
            context.env(JENKINS_VISITOR, Util.fixNull(jenkinsVisitor));
        }
        if (null != larkBotWebhook && !"".equals(larkBotWebhook)) {
            context.env(LARK_WEBHOOK, Util.fixNull(larkBotWebhook));
        }
        if (null != larkBotKey && !"".equals(larkBotKey)) {
            context.env(LARK_KEY, Util.fixNull(larkBotKey));
        }
    }

    private void processChangeLogSet(StringBuilder sb, ChangeLogSet cs, DateFormat df, int maxChanges, AtomicInteger counter) {
        for (Object o : cs) {
            if (counter.get() > maxChanges) {
                counter.incrementAndGet();
                continue;
            }
            ChangeLogSet.Entry e = (ChangeLogSet.Entry) o;
            sb.append(String.format(Util.fixNull(this.entryFormat), e.getAuthor(), e.getCommitId(), e.getMsg(), df.format(new Date(e.getTimestamp()))));

            counter.incrementAndGet();

            if (!affectedFilesIncluded) {
                continue;
            }
            try {
                for (ChangeLogSet.AffectedFile file : e.getAffectedFiles()) {
                    sb.append(String.format(Util.fixNull(this.lineFormat), file.getEditType().getName(), file.getPath()));
                }
            } catch (UnsupportedOperationException ex) {
                // early versions of SCM did not support getAffectedFiles, only had getAffectedPaths
                for (String file : e.getAffectedPaths()) {
                    sb.append(String.format(Util.fixNull(this.lineFormat), "", file));
                }
            }
        }
    }

    @Extension
    public static class ChangelogEnvironmentContributorDescriptor extends BuildWrapperDescriptor {

        @Override
        public boolean isApplicable(AbstractProject<?, ?> item) {
            // only really makes sense for jobs with SCM, but cannot really not show this option otherwise
            // users would have to leave the config form between setting up SCM and this.
            return true;
        }

        @Override
        public String getDisplayName() {
            return Messages.DisplayName();
        }

        public FormValidation doCheckLineFormat(@QueryParameter String lineFormat) {
            try {
                String result = String.format(lineFormat, "add", "README.md");
                return FormValidation.ok(Messages.LineFormat_Sample(result));
            } catch (IllegalFormatException ex) {
                return FormValidation.error(Messages.LineFormat_Error());
            }
        }

        public FormValidation doCheckEntryFormat(@QueryParameter String entryFormat) {
            try {
                String result = String.format(entryFormat, "bytebeats", "879e6fa97d79fd", "Initial commit", 1448305200000L);
                return FormValidation.ok(Messages.EntryFormat_Sample(result));
            } catch (IllegalFormatException ex) {
                return FormValidation.error(Messages.EntryFormat_Error());
            }
        }

        public FormValidation doCheckDateFormat(@QueryParameter String dateFormat) {
            try {
                String result = new SimpleDateFormat(dateFormat).format(new Date());
                return FormValidation.ok(Messages.DateFormat_Sample(result));
            } catch (IllegalArgumentException ex) {
                return FormValidation.error(Messages.DateFormat_Error());
            }
        }

        public FormValidation doCheckMaxDisplayedChanges(@QueryParameter String maxDisplayedChanges) {
            try {
                int maxDisplayedCount  = Integer.parseInt(maxDisplayedChanges.trim());
                return FormValidation.ok(Messages.MaxDisplayedChanges_Sample(maxDisplayedCount));
            } catch (IllegalArgumentException ex) {
                return FormValidation.error(Messages.MaxDisplayedChanges_Error());
            }
        }

        public FormValidation doCheckJenkinsVisitor(@QueryParameter String jenkinsVisitor) {
            try {
                String[] account = jenkinsVisitor.split(":");
                if (account.length != 2) {
                    return FormValidation.error(Messages.JenkinsVisitor_Error());
                }
                return FormValidation.ok(Messages.JenkinsVisitor_Sample(account[0], account[1]));
            } catch (Exception ex) {
                return FormValidation.error(Messages.JenkinsVisitor_Error());
            }
        }
        public FormValidation doCheckUseApiTokenMode(@QueryParameter boolean useApiTokenMode) {
            try {
                String mode;
                if (useApiTokenMode) {
                    mode = "Api Token";
                } else {
                    mode = "Password";
                }
                return FormValidation.ok(Messages.UseApiTokenMode_Sample(mode));
            } catch (Exception ex) {
                return FormValidation.error(Messages.UseApiTokenMode_Error());
            }
        }

        public FormValidation doCheckAffectedFilesIncluded(@QueryParameter boolean affectedFilesIncluded) {
            try {
                String mode;
                if (affectedFilesIncluded) {
                    mode = "Included";
                } else {
                    mode = "Excluded";
                }
                return FormValidation.ok(Messages.AffectedFilesIncluded_Sample(mode));
            } catch (Exception ex) {
                return FormValidation.error(Messages.AffectedFilesIncluded_Error());
            }
        }
    }
}
