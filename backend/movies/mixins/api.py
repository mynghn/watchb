from typing import Any, Dict, List, Optional, Tuple

import requests

from ..decorators import lazy_load_property


class SingletonRequestSessionMixin:
    _session_name = "_session"

    @lazy_load_property
    def session(self) -> requests.Session:
        return requests.Session()

    @session.deleter
    def session(self):
        self._session.close()
        del self._session

    @session.setter
    def session(self, value: Any):
        if isinstance(value, requests.Session):
            del self.session
            self._session = value
        else:
            raise ValueError("Only requests.Session object is allowed.")


class RequestPaginateMixin:
    def request_page(
        self,
        method: str,
        url: str,
        former_response: Optional[requests.Response] = None,
        **kwargs,
    ) -> requests.Response:
        raise NotImplementedError

    def process_response(
        self,
        response: requests.Response,
        **kwargs,
    ) -> Tuple[List, bool]:
        """
        returns 2-element tuple: (instances, has_next)
        - instances: post-processed instances data from response
        - has_next: boolean indicating response has next page
        """
        raise NotImplementedError

    def paginate(
        self,
        method: str,
        url: str,
        *,
        max_count: Optional[int] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        response = self.request_page(method=method, url=url, **kwargs)
        response_agg, has_next = self.process_response(response, **kwargs)

        if max_count and max_count <= len(response_agg):
            return response_agg[:max_count]

        while has_next:
            response = self.request_page(
                method=method, url=url, former_response=response, **kwargs
            )
            instances, has_next = self.process_response(response, **kwargs)

            if max_count and (to_add := max_count - len(response_agg)) <= len(
                instances
            ):
                response_agg += instances[:to_add]
                break
            else:
                response_agg += instances

        return response_agg
