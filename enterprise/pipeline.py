from openedx_filters import PipelineStep


class InviteOnlyEnrollments(PipelineStep):
    """
    Add the following to the end of edx-platform/lms/envs/devstack.py file:

        OPEN_EDX_FILTERS_CONFIG = {
            "org.openedx.learning.course.enrollment.started.v1": {
                "fail_silently": False,
                "pipeline": [
                    "enterprise.pipeline.InviteOnlyEnrollments"
                ]
            }
        }

    This will hook into the CourseEnrollmentStarted filter here: https://github.com/openedx/edx-platform/blob/592bc66b3fe5c14bafb7e44ea9e57328fe1dde06/common/djangoapps/student/models/course_enrollment.py#L658-L660
    and allow you to inspect the data that is being passed to the filter.
    """

    def run_filter(self, *args, **kwargs):
        import ipdb
        ipdb.set_trace()
        return {}
