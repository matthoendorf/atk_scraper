#!/usr/bin/env python
import requests
import re
import json
from os.path import exists

def authentication(mail, password, mealie_url):
  headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
  }
  data = {
    'grant_type': '',
    'username': mail,
    'password': password,
    'scope': '',
    'client_id': '',
    'client_secret': ''
  }
  auth = requests.post(mealie_url + "/api/auth/token", headers=headers, data=data)
  token = re.sub(r'.*token":"(.*)",.*', r'\1', auth.text)
  return token

def import_from_filelist(filelist, token, mealie_url):
  # generate file list
  fnames = []
  with open(filelist) as f:
      for fname in f:
          fnames = [fname.rstrip() for fname in f]
  
  # find all tags and make a unique list
  tags = []
  print("Generating all tags...", end='')
  for fname in fnames:
      with open(fname) as j_fp:
        j = json.load(j_fp)
        tags += [x for x in j["tags"]]
  tags = set(tags)
  print("Done\n")

  headers = {
      'Authorization': "Bearer " + token,
      'accept': 'application/json',
      'Content-Type': 'application/json'
  }
  # CREATE all tags found in all recipes, storing the auto-generated tag ids
  alltags = []
  for tag in tags:
      response = requests.post(mealie_url + "/api/organizers/tags", headers=headers, json={"name":tag})
      alltags.append(json.loads(response.text))
  
  # load up the recipes
  print("Creating recipes...")
  for fname in fnames:
    with open(fname, 'r') as f:
      data = json.load(f)
    newtags = []
    for oldtag in data["tags"]:
      newtag = {}
      for reftag in alltags:
        if oldtag == reftag["name"]:
          newtag = reftag
          newtags.append(newtag)
          break
    data["tags"] = newtags

    print(data["name"])
    # CREATE empty recipe
    response = requests.post(mealie_url + "/api/recipes", headers=headers, json={"name":data["name"]})
    slug = json.loads(response.text)
    #print(slug)

    # REPLACE empty recipe with recipe from json
    response = requests.get(mealie_url + "/api/recipes/"+slug, headers=headers)
    temp = json.loads(response.text)
    data["userId"] = temp["userId"]
    data["groupId"] = temp["groupId"]

    response = requests.patch(mealie_url + "/api/recipes/"+slug, headers=headers, json=data)

    # ADD image if one exists
    headers = {
      'Authorization': "Bearer " + token,
      'accept': 'application/json'
    }
    img_fname = re.sub('json', 'jp2', fname)
    if exists(img_fname):
      files = {'image': (img_fname, open(img_fname, 'rb'), 'type=image/jp2')}        
      response = requests.put(mealie_url + "/api/recipes/" + slug + "/image", headers=headers, files=files, data={'extension':'jp2'})

filelist="./list.txt"
mail="changeme@email.com"
password="MyPassword"
mealie_url="http://mediabox:9925"

token = authentication(mail, password, mealie_url)
import_from_filelist(filelist, token, mealie_url)
print("Done")
