from pyramid.response import Response
import json


class WebUtils():
    """ create basic json web response from output data """

    def createResponse(self, output, status_code):
        outputJson = json.dumps(output)
        headers = ()
        res = Response(outputJson)
        res.status_code = status_code
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res
