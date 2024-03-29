import re
from typing import Any, Optional

import requests


class SingletonRequestSessionMixin:
    @property
    def session(self) -> requests.Session:
        if not getattr(self, "_session", False):
            self.__class__._session = requests.Session()
            self._prepare_session()
        return self._session

    @session.deleter
    def session(self):
        self._session.close()
        del self.__class__._session

    @session.setter
    def session(self, value: Any):
        if isinstance(value, requests.Session):
            if getattr(self, "_session", False):
                del self.session
            self.__class__._session = value
        else:
            raise ValueError("Only requests.Session object is allowed.")

    def _prepare_session(self):
        """
        configure session level settings with predefined instance attributes.
        ex) self.session.headers.update({"Authorization": f"Bearer {self._access_token}"})
        """
        raise NotImplementedError

    def refresh_session(self):
        self.session = requests.Session()
        self._prepare_session()

    def request(self, *args, **kwargs) -> requests.Response:
        response = self.session.request(*args, **kwargs)
        response.raise_for_status()
        return response

    def json_response(self, response: requests.Response) -> dict[str, Any]:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            if m := re.match(
                r"^Invalid control character at: line \d+ column \d+ \(char (\d+)\)$",
                e.args[0],
            ):
                response._content = (
                    str(
                        response.content,
                        encoding := response.encoding or response.apparent_encoding,
                        errors="replace",
                    )
                    .replace(response.text[int(m.groups()[0])], "")
                    .encode(encoding)
                )
                response._content_consumed = False
            else:
                raise e

            return self.json_response(response)


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
    ) -> tuple[list[dict[str, Any]], bool]:
        """
        returns 2-element tuple: (instances, has_next)
        - instances: post-processed instances data from response
        - has_next: boolean indicating response has next page
        """
        raise NotImplementedError

    def paginate_request(
        self,
        method: str,
        url: str,
        *,
        max_count: Optional[int] = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
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
