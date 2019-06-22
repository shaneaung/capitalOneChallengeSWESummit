import requests, json

#structure that stores the requested criteria to search the API by
class endpointInfo(object):
    #class attributes, used for API access
    baseURL = "https://developer.nps.gov/api/v1/"
    head = {"X-Api-Key" : "9SxgL1crvEGcTEpbZoZhyzQ4flkWQahTtfAWfAy6"}
    
    #attributes that can be used to request info from API by
    def __init__(self, parkCode = None, stateCode = None, fields = None, 
                 q = None, designation = None):
        self.limit = 600
        self.parkCode = parkCode
        self.stateCode = stateCode
        self.fields = fields
        self.q = q
        self.designation = designation

    #additional standard python class methods    
    def __repr__(self):
        lim = "limit: " + str(self.limit)
        pc = "parkCode: " + str(self.parkCode)
        sc = "stateCode: " + str(self.stateCode)
        fds = "fields: " + str(self.fields)
        query = "q: " + str(self.q)
        desig = "designation: " + str(self.designation)
        return lim + "; " + pc + "; " + sc + "; " + fds + "; " + query + "; " + desig

    def __eq__(self, other):
        return (isinstance(other, npsQueryInfo) 
                and (self.limit == other.limit)
                and (self.parkCode == other.parkCode)
                and (self.stateCode == other.stateCode)
                and (self.fields == other.fields)
                and (self.q == other.q)
                and (self.designation == other.designation))

    def getHashables(self):
        return (self.lim, self.parkCode, self.stateCode, self.fields, self.q, self.designation)

    def __hash__(self):
        return hash(self.getHashables())

#methods to use to take endpointInfo object and search with
class npsMethods(object):
    
    #create list of API query links based on endpointInfo object's data
    @staticmethod
    def createRequestEndpoints(info, category):
        listOfEndpoints = list()
        endpoint = ""
        endpoint += endpointInfo.baseURL + category 
        e1 = ""
        e2 = ""
        if(info.parkCode == None and info.stateCode == None 
           and info.fields == None and info.q == None 
           and info.designation == None):
            listOfEndpoints.append(endpoint + "?limit=" + str(info.limit))
        else:
            endpoint += "?"
            if(info.parkCode != None):
                endpoint += "parkCode=" + str(info.parkCode) + "&"
            if(info.stateCode != None):
                endpoint += "stateCode=" + str(info.stateCode) + "&" 
            if(info.fields != None):
                endpoint += "fields=" + str(info.fields) + "&" 
            if(info.limit != None):
                endpoint += "limit=" + str(info.limit) + "&"
            if(info.q != None and info.designation == None):
                endpoint += "q=" + str(info.q) + "&"
            if(info.q == None and info.designation != None):
                endpoint += "q=" + str(info.designation) + "&"
            if(info.q != None and info.designation != None):
                e1 = endpoint
                e2 = endpoint
                e1 += "q=" + str(info.q) + "&"
                e2 += "q=" + str(info.designation) + "&"             

            if(e1 == "" and e2 == ""):
                listOfEndpoints.append(endpoint[:-1])
            else:
                listOfEndpoints.append(e1[:-1])
                listOfEndpoints.append(e2[:-1])
        return listOfEndpoints

    #submit request to the API with the links in a list of endpoints
    #returns a list of JSON files encoded as python dictionaries
    @staticmethod
    def requestJSONs(endpointList):
        listOfJSONs = list()
        for end in endpointList:
            r = requests.get(end, headers = endpointInfo.head)
            if (r.status_code != 200):
                return "Error: Status Code " + str(r.status_code)
            else:
                listOfJSONs.append(r.json())
        return listOfJSONs

    #used for debugging, prints out the info in a JSON
    @staticmethod
    def visualizeJSONList(jsonList):
        for j in jsonList:
            print(json.dumps(j, indent = 4, sort_keys = True))

    #merge the results from multiple JSONs into a single dictionary of 
    #results found by all JSONs in the list, returns the number of entries 
    #in common and the entries themselves
    @staticmethod
    def prepareResultInfo(jsonList):
        data = list()
        totalResults = 0;
        if(len(jsonList) == 2):
            lst1 = jsonList[0]["data"]
            lst2 = jsonList[1]["data"]
            for entry in lst1:
                if entry in lst2:
                    data.append(entry)
            totalResults = len(data)
        else: 
            
            totalResults = jsonList[0]["total"]
            data = jsonList[0]["data"]

        results = dict()
        results["total"] = totalResults
        results["data"] = data

        return results

    #removes all extra HTML tags in a string
    @staticmethod
    def stripTags(txt):
        inputStr = txt
        while("<" in inputStr and ">" in inputStr):
            front = inputStr.index("<")
            back = inputStr.index(">")
            if(back == len(inputStr)-1):
                inputStr = inputStr[:front]
            else: 
                inputStr = inputStr[:front]+inputStr[back+1:]
        return inputStr


