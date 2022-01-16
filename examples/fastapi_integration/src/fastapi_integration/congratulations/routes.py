from congratulations_app.congratulations_services import CongratulationsServiceFactory
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from fastapi_integration.app import AppFactory
from fastapi_integration.congratulations.models import CongratulationRequest
from fastapi_integration.current_user_resolvers import CurrentUserResolverFactory
from galo_ioc import get_factory

__all__ = [
    "load",
]


def load() -> None:
    app_factory = get_factory(AppFactory)
    app = app_factory()
    congratulations_service_factory = get_factory(CongratulationsServiceFactory)
    congratulations_service = congratulations_service_factory()
    current_user_resolver_factory = get_factory(CurrentUserResolverFactory)
    current_user_resolver = current_user_resolver_factory()
    router = APIRouter(dependencies=[Depends(current_user_resolver)])

    @router.post("/happy_birthday")
    async def happy_birthday(request: CongratulationRequest) -> None:
        congratulations_service.happy_birthday(request.name)

    app.include_router(router)
