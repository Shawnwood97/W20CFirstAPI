import db
from flask import Flask, request, Response
import json
import traceback

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

    # loop animals and append trhe
    headers = [i[0] for i in cursor.description]
    result = []
    for row in animals:
      result.append(dict(zip(headers, row)))
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


app.run(debug=True)
