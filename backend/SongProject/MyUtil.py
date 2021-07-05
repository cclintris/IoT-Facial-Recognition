import requests, json, sys, re, time, os, warnings
from requests_toolbelt.multipart.encoder import MultipartEncoder
from datetime import datetime

warnings.filterwarnings("ignore")

EDGEX_IP = None

def bindEdgeXHost(host):
    global EDGEX_IP
    EDGEX_IP = host

def regis(deviceName, key, profilePath, deviceHost, port) :
    def createAddressables() :
        url = 'http://%s:48081/api/v1/addressable' % EDGEX_IP

        payload = {
            "name" : "%s_dev_addr" % deviceName,
            "protocol" : "HTTP",
            "address" : deviceHost,
            "port" : int(port),
            "path" : "/api/v1/device/register"  # REST endpoint on the test app
        }
        headers = {'content-type' : 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        print("Result for createAddressables: %s - Message: %s" % (response, response.text))

    def createValueDescriptors() :
        url = 'http://%s:48080/api/v1/valuedescriptor' % EDGEX_IP

        payload = {
            "name" : key,
            "description" : "",
            "type" : "Int64",
            "min" : "0",
            "max" : "100",
            "uomLabel" : key,
            "defaultValue" : "0",
            "formatting" : "%s",
            "labels" : [deviceName, "app"]
        }
        headers = {'content-type' : 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        print("Result for createValueDescriptors #1: %s - Message: %s" % (response, response.text))

    def uploadDeviceProfile() :
        multipart_data = MultipartEncoder(
            fields={
                'file' : (profilePath, open(profilePath, 'rb'), 'text/plain')
            }
        )

        url = 'http://%s:48081/api/v1/deviceprofile/uploadfile' % EDGEX_IP
        response = requests.post(url, data=multipart_data, headers={'Content-Type' : multipart_data.content_type})

        print("Result of uploading device profile: %s with message %s" % (response, response.text))

    def addNewDevice() :
        url = 'http://%s:48081/api/v1/device' % EDGEX_IP

        payload = {
            "name" : "%s_device" % deviceName,
            "description" : "",
            "adminState" : "unlocked",
            "operatingState" : "enabled",
            "protocols" : {
                "example" : {
                    "host" : "dummy",
                    "port" : "1234",
                    "unitID" : "1"
                }
            },
            "labels" : [
                deviceName,
                "app"
            ],
            "location" : "tokyo",
            "service" : {
                "name" : "edgex-device-rest"
                # "name" : "%s_rest_service" % name
            },
            "profile" : {
                "name" : "%s_profile" % deviceName
            }
        }
        headers = {'content-type' : 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        print("Result for addNewDevice: %s - Message: %s" % (response, response.text))

    createAddressables()
    createValueDescriptors()
    uploadDeviceProfile()
    addNewDevice()


def createStream() :
    url = "http://%s:48075/streams" % EDGEX_IP
    payload = {
        "sql" : "create stream temp_threshold() WITH (FORMAT=\"JSON\", TYPE=\"edgex\")"
    }
    headers = {'content-type' : 'application/json'}
    try :
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        print("Result for createStream: %s - Message: %s" % (response, response.text))
    except :
        pass


ON = 1
NOR = 0
OFF = -1


def createRule(key, case, targetUrl) :
    # key 从流中提取的字段名
    sql = ""
    method = ""
    if case == ON :
        sql = "SELECT %s FROM temp_threshold where %s = 1" % (key, key)
        method = "GET"
    elif case == 0 :
        sql = "SELECT %s FROM temp_threshold where %s = 0" % (key, key)
        method = "POST"
    else :
        sql = "SELECT %s FROM temp_threshold where %s = -1" % (key, key)
        method = "DELETE"

    url = "http://%s:48075/rules" % EDGEX_IP
    payload = {
        "id" : "rule_%s_%s" % (key, case),
        "sql" : sql,
        "actions" : [
            {
                "rest" : {
                    "url" : targetUrl,
                    "method" : method,
                    "retryInterval" : -1,
                    "dataTemplate" : "{\"sign\":\"1\"}",
                    "sendSingle" : True
                }
            },
            {
                "log" : {}
            }
        ]
    }
    headers = {'content-type' : 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    print("Result for createRule: %s - Message: %s" % (response, response.text))


def Touch(device,resource,value) :
    # data 1代表使用，0代表成功返回，-1代表不成功返回
    url = "http://%s:49986/api/v1/resource/%s_device/%s" % (EDGEX_IP,device,resource)
    sendData(url, value)


def sendData(url, data) :
    requests.post(url, data=json.dumps(data), verify=False)
