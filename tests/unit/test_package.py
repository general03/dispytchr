import dispytchr
from dispytchr.application.use_cases import UseCases
from dispytchr.bootstrap import bootstrap
from dispytchr.domain.errors import DomainError


def test_version_is_exposed() -> None:
    assert isinstance(dispytchr.__version__, str)
    assert dispytchr.__version__


def test_bootstrap_builds_use_cases() -> None:
    assert isinstance(bootstrap(), UseCases)


def test_domain_error_is_an_exception() -> None:
    assert issubclass(DomainError, Exception)
