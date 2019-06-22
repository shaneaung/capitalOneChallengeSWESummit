import os, html, string
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import nps
app = Flask(__name__, template_folder="./templates/")

#route to home page
@app.route("/")
def home():
    return render_template("home.html")

#route to park search page
@app.route("/parkSearch.html")
def search():
    return render_template("parkSearch.html")

#route to search results page
@app.route('/result',methods = ['POST', 'GET'])
def result():
    result = request.form
    #take the posted input given from the search criteria and search through API
    if request.method == 'POST':
        #change from base values if criteria was explicitly specified
        sc = None
        query = None
        des = None
        if(len(result["keyword"]) > 0): 
            query = result["keyword"]
        if(result["state"] != "unspecified"):
            sc = result["state"]
        if(result["designation"] != "unspecified"):
            des = result["designation"]
        
        #store endpoint search criteria, create endpoint, and access JSON files
        info = nps.endpointInfo(stateCode = sc, q = query, designation = des)
        listOfEndpoints = nps.npsMethods.createRequestEndpoints(info, "parks")
        listOfJSONs = nps.npsMethods.requestJSONs(listOfEndpoints)

        #declare variables
        responseMessage = ""
        resultsDict = dict()

        #check to see that request was successful
        if(type(listOfJSONs) == str):
            responseMessage = "Unfortunately, the search was unable to be completed. Either your search terms were invalid or the request timed out. Please correct or narrow down your criteria and try again."
        else:
            #store the retrieved information in the variables to use for displaying results
            data = nps.npsMethods.prepareResultInfo(listOfJSONs)
            responseMessage = "Number of Search Results: " + str(data["total"])
            for entry in data["data"]:
                resultsDict[entry["parkCode"]] = html.unescape(entry["fullName"])

        #render templage
        return render_template("result.html", 
                               responseMessage = responseMessage, 
                               resultsDict = resultsDict)

#route to basic park info page
@app.route("/parkInformation.html/<string:id>/")
def parkInfo(id):
    #access information for selected park from API
    basicParkInfo = nps.endpointInfo(parkCode = id, fields="images")
    endptList = nps.npsMethods.createRequestEndpoints(basicParkInfo, "parks")
    prepared = nps.npsMethods.prepareResultInfo(nps.npsMethods.requestJSONs(endptList))
    data = prepared["data"]

    #accessing and storing images to pass to template
    imgDict = dict()
    images = data[0]["images"]
    print(len(images))
    for n in range(min(len(images),4)):
        imgDict["image" + str(n)] = images[n]["url"]

    #storing basic park information to pass to template
    fullName = html.unescape(data[0]["fullName"])
    description = html.unescape(data[0]["description"])
    weatherInfo = html.unescape(data[0]["weatherInfo"])
    directionsInfo = html.unescape(data[0]["directionsInfo"])
    directionsUrl = html.unescape(data[0]["directionsUrl"])
    url = html.unescape(data[0]["url"])
    mappable = (fullName.lower()).replace(" ", "%%20")
    
    #empty variables for use with template (not used for this route)
    reqDict = dict()
    reqMessage = ""
    alertDict = dict()
    campDict = dict()
    visitDict = dict()
    eventDict = dict()

    #render template
    return render_template("parkInformation.html", 
                           id=id, 
                           fullName = fullName,
                           description = description,
                           weatherInfo = weatherInfo,
                           directionsInfo = directionsInfo,
                           directionsUrl = directionsUrl,
                           url = url, 
                           imgDict = imgDict, 
                           mappable = mappable,
                           reqDict= reqDict,
                           reqMessage = reqMessage,
                           alertDict = alertDict, 
                           campDict = campDict,
                           visitDict = visitDict, 
                           eventDict = eventDict)

#route to display additional info about park based on user request
@app.route("/park.<string:newRequest>.html/<string:id>/")
def parkInfoRedux(id, newRequest):
    #access information for selected park from API
    basicParkInfo = nps.endpointInfo(parkCode = id, fields="images,operatingHours")
    endptList = nps.npsMethods.createRequestEndpoints(basicParkInfo, "parks")
    prepared = nps.npsMethods.prepareResultInfo(nps.npsMethods.requestJSONs(endptList))
    data = prepared["data"]

    #accessing and storing images to pass to template
    imgDict = dict()
    images = data[0]["images"]
    for n in range(min(len(images),4)):
        imgDict["image" + str(n)] = images[n]["url"]

    #storing basic park information to pass to template
    fullName = html.unescape(data[0]["fullName"])
    description = html.unescape(data[0]["description"])
    weatherInfo = html.unescape(data[0]["weatherInfo"])
    directionsInfo = html.unescape(data[0]["directionsInfo"])
    directionsUrl = html.unescape(data[0]["directionsUrl"])
    url = html.unescape(data[0]["url"])
    mappable = (fullName.lower()).replace(" ", "%%20")

    
    #access ADDITIONAL information for selected park from API, use different path
    requestedParkInfo = nps.endpointInfo(parkCode = id)
    requestedEndptList = nps.npsMethods.createRequestEndpoints(requestedParkInfo, newRequest)
    requestedPrep = nps.npsMethods.prepareResultInfo(nps.npsMethods.requestJSONs(requestedEndptList))
    reqData = requestedPrep["data"]
    
    #set up data structures to pass to template
    reqMessage = "Number of " + newRequest + " for " + fullName + ": " + str(len(reqData))
    reqDict = dict()
    alertDict = dict()
    campDict = dict()
    visitDict = dict()
    eventDict = dict()

    #fill in the appropriate structure with necessary information; leave other structures empty
    if(newRequest == "places" or newRequest == "people" or newRequest == "articles"):
        for entry in reqData: 
            reqDict[entry["title"]] = {entry["url"]: entry["listingdescription"]}

    if(newRequest == "newsreleases"):
        reqMessage = "Number of news releases for " + fullName + ": " + str(len(reqData))
        for entry in reqData: 
            reqDict[entry["title"]] = {entry["url"]: entry["abstract"]}

    if(newRequest == "lessonplans"):
        reqMessage = "Number of lesson plans for " + fullName + ": " + str(len(reqData))
        for entry in reqData: 
            reqDict[entry["title"]] = {entry["url"]: entry["questionobjective"]}

    if(newRequest == "alerts"):
        for entry in reqData: 
            alertDict[entry["title"]] = {entry["category"]: entry["description"]}

    if(newRequest == "campgrounds"):
        for entry in reqData: 
            campDict[entry["name"]] = {"description": entry["description"]}

    if(newRequest ==  "visitorcenters"):
        for entry in reqData:
            visitDict[entry["name"]] = {"description": entry["description"],
                                        "url": entry["url"],
                                        "directionsInfo": entry["directionsInfo"]}
    if(newRequest ==  "events"):
        for entry in reqData:
            allDates = ""
            for date in entry["dates"]:
                allDates += date
                allDates += ", "
            allDates = allDates[:-2]

            desc = nps.npsMethods.stripTags(entry["description"])
            url = entry["regresurl"]
            if(len(url) == 0): url = "https://www.nps.gov/" + id + "/index.htm"
            eventDict[entry["title"]] = {"description": desc,
                                         "location": entry["location"],
                                         "url": url,
                                         "dates": allDates}
    #render template
    return render_template("parkInformation.html", 
                           id=id, 
                           fullName = fullName,
                           description = description,
                           weatherInfo = weatherInfo,
                           directionsInfo = directionsInfo,
                           directionsUrl = directionsUrl,
                           url = url, 
                           imgDict = imgDict, 
                           mappable = mappable,
                           reqDict = reqDict,
                           reqMessage = reqMessage, 
                           alertDict = alertDict,
                           campDict = campDict, 
                           visitDict = visitDict,
                           eventDict = eventDict)
                           
# THIS CODE IS USED SOLELY FOR EDITING PURPOSES TO DEAL WITH BROWSER CACHING ISSUES
# IT DOES NOT AFFECT THE FUNCTION OF THE APP AT ALL, IT IS USED ONLY FOR DEBUGGING 
# AND MAKING EDITS TO THE WEBSITE APPEARANCE
# OBTAINED FROM THIS LINK: http://flask.pocoo.org/snippets/40/
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0', port=80)
