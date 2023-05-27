import logging
import traceback as tb
from datetime import datetime

from jivago.event.async_event_bus import AsyncEventBus
from jivago.event.config.annotations import EventHandler, EventHandlerClass
from jivago.inject.annotation import Component
from jivago.lang.annotations import Inject
from ohdieux.caching.programme_cache import ProgrammeCache
from ohdieux.service.programme_fetching_service import ProgrammeFetchingService


@Component
@EventHandlerClass
class InProcessProgrammeRefresher(object):

    @Inject
    def __init__(self, fetcher: ProgrammeFetchingService,
                 cache: ProgrammeCache, event_bus: AsyncEventBus):
        self._fetcher = fetcher
        self._cache = cache
        self._bus = event_bus
        self._logger = logging.getLogger(self.__class__.__name__)

    @EventHandler("refresh_programme")
    def do_refresh(self, programme_id: int):
        try:
            self._logger.info(f"Refreshing programme {programme_id}.")
            start = datetime.now()
            programme = self._fetcher.fetch_programme(programme_id)
            self._cache.set(programme_id, programme)
            self._logger.info(
                f"Done refreshing programme {programme_id} in {datetime.now() - start}."
            )
        except KeyboardInterrupt as e:
            raise e
        except Exception:
            self._logger.error(
                f"Uncaught exception while refreshing programme {tb.format_exc()}."
            )
        finally:
            self._bus.emit("refresh_complete", programme_id)
