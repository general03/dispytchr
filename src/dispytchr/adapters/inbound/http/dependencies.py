from typing import Annotated, cast

from fastapi import Depends, Request

from dispytchr.application.use_cases import UseCases


def get_use_cases(request: Request) -> UseCases:
    return cast(UseCases, request.app.state.use_cases)


UseCasesDep = Annotated[UseCases, Depends(get_use_cases)]
