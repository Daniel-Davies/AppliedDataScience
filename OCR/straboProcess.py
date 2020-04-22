import os
from pathlib import Path
import json 
from math import radians, cos, sin, asin, sqrt,pi

city = "Burnley"
dataBasePath = "./MapData/Sample/Raw/"+city

def findAllFileIds():
  prjFiles = list(filter(lambda x: x.endswith(".prj"),os.listdir(dataBasePath)))
  return list(map(lambda x: Path(x).stem,prjFiles))
  
def getAllTextForCity():
  maps = findAllFileIds()
  for tile in maps:
      try:
        textInTile = retrieveTextWLatLonsFromImage(tile)
        with open(city+"/"+tile+'.txt','a') as f:
            for item in textInTile:
                f.write(str(item[0])+","+str(item[1])+","+item[2].replace('\n', ' ').replace('\r', '')+"\n")

      except:
          pass
    #   textTuples.extend(textInTile)
      

def retrieveTextWLatLonsFromImage(imageId):
  with open("./StraboRaw/"+imageId+".json",'rb') as f:
    parsed = (json.load(f))

  targetFile = dataBasePath+"/"+imageId
  targetFileGeo = targetFile + ".tfw"

  bboxTextLocations = (locateTextPixelsInStraboJson(parsed))
  singleXY = list(map(lambda x: mapBboxToSingleCoord(x),bboxTextLocations))
  latLonPoints = list(map(lambda x: mapImagePixelToLatLon(x,targetFileGeo),singleXY))
  latLonPoints = list(map(lambda x: (x[0],x[1],x[2],imageId), latLonPoints))
  return latLonPoints

def mapBboxToSingleCoord(textTuple):
  locations, text = textTuple 
  xs = list(map(lambda x: x[0],locations))
  ys = list(map(lambda x: x[1],locations))

  newX = (min(xs)+max(xs)) / 2
  newY = (min(ys)+max(ys)) / 2
  return ((newX,newY),text)

def locateTextPixelsInStraboJson(finalJson):
  featureList = finalJson["features"]
  bboxes = []
  for entry in featureList:
    uniqueCoords = (list(set(list(map(lambda x: (x[0],x[1]),entry['geometry']['coordinates'][0])))))
    if len(uniqueCoords) == 4:
      bboxes.append((uniqueCoords,entry["NameAfterDictionary"]))
  
  return bboxes

def mapImagePixelToLatLon(coord,targetFileGeo):
  lat,lon = getBaseLatLon()
  Xm, Ym, text = convertPixelToMetreOffset(coord,targetFileGeo)
  newLatFromBase, newLonFromBase = transformLatLonByXMetres(lat,lon,Ym,Xm)
  return (newLatFromBase, newLonFromBase, text)

def getBaseLatLon():
  return 53.9153862, -2.6224470139

def convertPixelToMetreOffset(coord,targetFileGeo):
  pixelX, pixelY = coord[0]
  with open(targetFileGeo, 'rb') as f:
    lines = f.readlines()
    lonOffsetFromBase = float(lines[-1].strip())
    latOffsetFromBase = float(lines[-2].strip())
    yPixelsToMetres = 1 / float(lines[-3].strip())
    xPixelsToMetres = 1 / float(lines[0].strip())

    metreOffsetOnY = pixelY / yPixelsToMetres
    metreOffsetOnX = pixelX / xPixelsToMetres

    return (metreOffsetOnX+latOffsetFromBase,metreOffsetOnY+lonOffsetFromBase,coord[1])
  
def transformLatLonByXMetres(lat,lon,dn,de):
    R=6377563.396 #from their files
    dLat = dn/R
    dLon = de/(R*cos(pi*lat/180))
    latO = lat + dLat * 180/pi
    lonO = lon + dLon * 180/pi

    return (latO,lonO)

print(getAllTextForCity())