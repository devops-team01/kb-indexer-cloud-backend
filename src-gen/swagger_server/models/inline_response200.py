# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class InlineResponse200(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, message: str=None):  # noqa: E501
        """InlineResponse200 - a model defined in Swagger

        :param message: The message of this InlineResponse200.  # noqa: E501
        :type message: str
        """
        self.swagger_types = {
            'message': str
        }

        self.attribute_map = {
            'message': 'message'
        }
        self._message = message

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse200':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200 of this InlineResponse200.  # noqa: E501
        :rtype: InlineResponse200
        """
        return util.deserialize_model(dikt, cls)

    @property
    def message(self) -> str:
        """Gets the message of this InlineResponse200.

        Indicates whether the request to update the logs was accepted or denied.  # noqa: E501

        :return: The message of this InlineResponse200.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this InlineResponse200.

        Indicates whether the request to update the logs was accepted or denied.  # noqa: E501

        :param message: The message of this InlineResponse200.
        :type message: str
        """
        allowed_values = ["success", "denied"]  # noqa: E501
        if message not in allowed_values:
            raise ValueError(
                "Invalid value for `message` ({0}), must be one of {1}"
                .format(message, allowed_values)
            )

        self._message = message
