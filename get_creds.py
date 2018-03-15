import httplib, urllib, base64, json, sys

class AuthError(Exception):
    def __init__(self):
        self.msg = "auth error"
# read the oauth secrets and account ID from a configuration file
def loadSecret():
# read the s3 creds from json file
    try:
        credsFile=open('brightcove_oauth.txt')
        creds = json.load(credsFile)
        return creds
    except Exception, e:
        print "Error loading oauth secret from local file called 'brightcove_oauth.txt'"
        print "\tThere should be a local file in this directory called brightcove_oauth.txt "
        print "\tWhich has contents like this:"
        print """
		{
            "account_id": "1752604059001",
            "client_id": "c5d0a622-5479-46d8-8d8a-5f034b943fab",
            "client_secret": "w7NQYu0vUloM4GYYy2SXAxrvyFpt8fwI35qAFZcS13-VIgs0itwKNsAwHOS80sOWKJ1BUwHIvSFG2IbgcxEGKg"
		}

		"""
    sys.exit("System error: " + str(e) )
    # get the oauth 2.0 token
def getAuthToken(creds):
    conn = httplib.HTTPSConnection("oauth.brightcove.com")
    url =  "/v4/access_token"
    params = {
"grant_type": "client_credentials"
    }
    client = creds["client_id"];
    client_secret = creds["client_secret"];
    authString = base64.encodestring('%s:%s' % (client, client_secret)).replace('\n', '')
    requestUrl = url + "?" + urllib.urlencode(params)
    headersMap = {
"Content-Type": "application/x-www-form-urlencoded",
"Authorization": "Basic " + authString
    };
    conn.request("POST", requestUrl, headers=headersMap)
    response = conn.getresponse()
    if response.status == 200:
        data = response.read()
        result = json.loads( data )
        return result["access_token"]
# call analytics api for video views in the last 30 days
def getVideoViews( token , account ):
    conn = httplib.HTTPSConnection("data.brightcove.com")
    url =  "/analytics-api/videocloud/account/" + account + "/report/"
    params = {
"dimensions": "video",
"limit": "10",
"sort": "video_view",
"fields": "video,video_name,video_view",
"format": "json"
    }
    requestUrl = url + "?" + urllib.urlencode(params)
    headersMap = {
"Authorization": "Bearer " + token
    };
    conn.request("POST", requestUrl, headers=headersMap)
    response = conn.getresponse()
    if response.status == 200:
        data = response.read()
        result = json.loads( data )
        return result
    elif response.status == 401:
    # if we get a 401 it is most likely because the token is expired.
        raise AuthError
    else:
        raise Exception('API_CALL_ERROR' + " error " + str(response.status) )
# call CMS API to return the number of videos in the catalog
def getVideos( token , account ):
    conn = httplib.HTTPSConnection("cms.api.brightcove.com")
    url =  "/v1/accounts/" + account + "/counts/videos/"
    requestUrl = url
    print "GET " + requestUrl
    headersMap = {
"Authorization": "Bearer " + token
    };
    conn.request("GET", requestUrl, headers=headersMap)
    response = conn.getresponse()
    if response.status == 200:
        data = response.read()
        result = json.loads( data )
        return result
    elif response.status == 401:
    # if we get a 401 it is most likely because the token is expired.
        raise AuthError
    else:
        raise Exception('API_CALL_ERROR' + " error " + str(response.status) )
def demo():
    creds = loadSecret()
    token = getAuthToken(creds)

    account = creds["account_id"];
    try:
        results = getVideos( token , account )
    except AuthError, e:
    # handle an auth error by re-fetching a auth token again
        token = getAuthToken(creds)
        results = getVideoViews( token , account )
# print the videos
    print results
if __name__ == "__main__":
  demo();
