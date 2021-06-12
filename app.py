import db
from flask import Flask, request, Response
import json
import traceback
import mariadb

app = Flask(__name__)


@app.get('/animals')
def get_animals():
  conn = db.openConnection()
  cursor = db.openCursor(conn)
  animals = None
  result = None
  try:
    cursor.execute("SELECT name, id FROM animal")
    animals = cursor.fetchall()

    # loop animals and append the
    result = db.loopItems(cursor, animals)

# cant really think of any good excepts for a GET
  except:
    traceback.print_exc()
    print('Error getting animals!')

  db.closeAll(conn, cursor)

  #! curious if I should use if animals, or if result, so I did both :)
  if(animals == None or result == None):
    return Response('Error getting animals from DB', mimetype='text/plain', status=500)
  #! would the below elif be a good idea? not really an error if the db is empty.
  # elif(result == []):
  #   return Response('No animals in DB', mimetype='text/plain', status=500)
  else:
    animals_json = json.dumps(result, default=str)
    return Response(animals_json, mimetype='application/json', status=200)


@app.post('/animals')
def add_animal():
  try:
    animal_name = str(request.json['animalName'])

  except ValueError:
    traceback.print_exc()
    # 403 seems to be the best error status for this based on some research, I read that this means "We understand the request, but you're not allowed"
    return Response("Error: Input was not a string!", mimetype="text/plain", status=403)
  except:
    traceback.print_exc()
    return Response("Error: Unknown error with input!", mimetype="text/plain", status=400)

  conn = db.openConnection()
  cursor = db.openCursor(conn)

  row_count = 0
  new_animal = None
  result = None
  try:
    cursor.execute(
        "INSERT INTO animal (name) VALUES (?)", [animal_name, ])
    conn.commit()
    row_count = cursor.rowcount

    cursor.execute(
        "SELECT name, id FROM animal WHERE name = ?", [animal_name, ])
    # Used fetchall so I could use my loop to display data nicer.
    new_animal = cursor.fetchall()

    result = db.loopItems(cursor, new_animal)

  except mariadb.InternalError:
    # Basic 500 seems like an okay error here,
    traceback.print_exc()
    return Response("Internal Server Error: Failed to add animal", mimetype="text/plain", status=500)
  except mariadb.IntegrityError:
    # I think 409 fits well here, since it should be caused by a conflict like a duplicate, or foreign key issue, seems like a client issue, not a server issue?
    traceback.print_exc()
    return Response("Error: Possible duplicate data or foreign key conflict!", mimetype="text/plain", status=409)

  except:
    traceback.print_exc()
    print("Error with POST!")

  db.closeAll(conn, cursor)

  # 1 row should still work here! Added that the result also needed data, unsure if I still need new_animal condition, but more explicit cant be that bad, rightttt?
  if(row_count == 1 and new_animal != None and result != None):
    new_animal_json = json.dumps(result, default=str)
    return Response(new_animal_json, mimetype="application/json", status=201)
  else:
    return Response("Failed to add animal", mimetype="text/plain", status=400)


@app.patch('/animals')
def edit_animal():
  try:
    #! I considered not setting this to int, and using an if statement for if it was an int to compare to aniamls id, and if it was a string to compare to animal
    #! name, would this have been a cool thing to do? or NNOOOOO BAAAAAD!?

    # ? should each input have it's own try excpet, or is that overkill?
    animal_id = int(request.json['animalId'])
    new_animal_name = str(request.json['newAnimalName'])

  except ValueError:
    traceback.print_exc()
    # 403 seems to be the best error status for this based on some research, I read that this means "We understand the request, but you're not allowed"
    return Response("Error: ID Input was not a whole number, or Name input was not a string!", mimetype="text/plain", status=403)
  except:
    traceback.print_exc()
    return Response("Error: Unknown error with input!", mimetype="text/plain", status=400)

  conn = db.openConnection()
  cursor = db.openCursor(conn)

  updated_animal = None
  row_count = 0
  result = None
  try:
    cursor.execute(
        "UPDATE animal SET name = ? WHERE id = ?", [new_animal_name, animal_id])
    conn.commit()
    row_count = cursor.rowcount

    cursor.execute(
        "SELECT name, id FROM animal WHERE name = ?", [new_animal_name, ])
    # Used fetchall so I could use my loop to display data nicer.
    updated_animal = cursor.fetchall()

    result = db.loopItems(cursor, updated_animal)

  except mariadb.InternalError:
    # Basic 500 seems like an okay error here,
    traceback.print_exc()
    return Response("Internal Server Error: Failed to update animal", mimetype="text/plain", status=500)
  except mariadb.IntegrityError:
    # I think 409 fits well here, since it should be caused by a conflict like a duplicate, or foreign key issue, seems like a client issue, not a server issue?
    traceback.print_exc()
    return Response("Error: Possible duplicate data or foreign key conflict!", mimetype="text/plain", status=409)

  except:
    traceback.print_exc()
    print("Error with PATCH!")

  db.closeAll(conn, cursor)

  # 1 row should still work here! Added that the result also needed data, unsure if I still need new_animal condition, but more explicit cant be that bad, rightttt?
  if(row_count == 1 and updated_animal != None and result != None):
    updated_animal_json = json.dumps(result, default=str)
    return Response(updated_animal_json, mimetype="application/json", status=201)
  else:
    return Response("Failed to update animal", mimetype="text/plain", status=400)


app.run(debug=True)
