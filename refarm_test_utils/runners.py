import unittest
from itertools import islice

from django.test.runner import DiscoverRunner

from refarm_test_utils.results import TimedResult


class RefarmTestRunner(DiscoverRunner):
    """Check every test is tagged and show slowest tests table."""

    def __init__(self, *args, top_slow=0, check_tags=True, rerun_failed=0,**kwargs):
        super().__init__(*args, **kwargs)
        self.top_slow = top_slow
        self.check_tags = check_tags

        self.rerun_failed = rerun_failed
        self.tests_to_rerun = []

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--top-slow', nargs='?', const=10, type=int,
            metavar='N', help='Shows top N of slowest tests.',
        )
        parser.add_argument(
            '--disable-tags-check', action='store_false', dest='check_tags',
            help='Disables checking that each test is tagged.'
        )
        parser.add_argument(
            '--rerun-failed', nargs='?', const=1, type=int, default=0,
            metavar='N', help='Runs failed tests while they occur. Gives N tries.',
        )

    def build_suite(self, *args, **kwargs):
        suite = super().build_suite(*args, **kwargs)
        if self.check_tags:
            check_tagged_tests(suite)
        return suite

    def get_resultclass(self):
        return TimedResult if self.top_slow else super().get_resultclass()

    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)

        if self.rerun_failed > 0 and self.suite_result(suite, result) > 0:
            self.tests_to_rerun = (
                [f[0].id() for f in result.failures]
                + [e[0].id() for e in result.errors]
            )
        else:
            self.tests_to_rerun = []

        if self.top_slow:
            assert isinstance(result, TimedResult), result

            timings = list(islice(
                sorted(
                    result.test_timings,
                    key=lambda t: t[1],  # elapsed time
                    reverse=True,
                ),
                self.top_slow
            ))

            print('\nTop slowest tests:')
            for i, (name, elapsed) in enumerate(timings, 1):
                print(f'{i}. {elapsed:.2f} {name.splitlines()[0]}')

        return result

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        suite_result = super().run_tests(test_labels, extra_tests, **kwargs)
        if self.tests_to_rerun:
            self.rerun_failed -= 1
            delimiter = '\n\t- '
            print(f'\nRerun tries left: {self.rerun_failed}')
            print(f'Rerun these failed tests:{delimiter}{delimiter.join(self.tests_to_rerun)}\n')
            suite_result = self.run_tests(self.tests_to_rerun, **kwargs)
        return suite_result


def check_tagged_tests(suite):
    # get the tags processing from:
    # django.test.runner.filter_tests_by_tags
    # https://github.com/django/django/blob/master/django/test/runner.py#L717
    suite_class = type(suite)
    for test in suite:
        if isinstance(test, suite_class):
            # check a nested suite
            check_tagged_tests(test)
        elif not isinstance(test, unittest.loader._FailedTest):
            # check a non failed test
            test_tags = set(getattr(test, 'tags', set()))
            test_fn_name = getattr(test, '_testMethodName', str(test))
            test_fn = getattr(test, test_fn_name, test)
            test_fn_tags = set(getattr(test_fn, 'tags', set()))
            if not test_tags.union(test_fn_tags):
                raise Exception(
                    f'{test_fn_name} is not tagged. You have to decorate it '
                    'with tag("slow") or tag("fast").'
                )
