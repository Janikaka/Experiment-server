from pyramid.httpexceptions import HTTPBadRequest
import json


class WebUtils():
    """ create basic json web response from output data """

    def createResponse(self, output, status_code):
        res = HTTPBadRequest()
        res.text = json.dumps(output)
        res.content_type = 'application/json'
        return res
