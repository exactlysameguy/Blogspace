""" Anforderungen für Kaffee-Maschinen besteller

1. Als Nutzer möchte ich aus mehreren Kachen auswählen können,
    um einen Kaffee-Typ auszuwählen
2. Als Nutzer möchte ich durch Auswählen einer Kachel einen
Kaffee-Typ zu einer Liste hinzufügen, um den Prozess des Kaffeebrühens zu starten
3. Als Nutzer möchte ich eine Übersicht über die in der Warteschlange
befindlichen Kaffees zu sehen
4. Als Nutzer möchte ich in der Übersicht der Kaffees Einträge löschen können
5. Als System möchte ich die Position des Rotators nullen können

"""
import time

import flask
from flask import Flask, render_template_string, request, jsonify, url_for, views

# import RPi.GPIO as GPIO
# from RpiMotorLib import RpiMotorLib

# define GPIO pins
GPIO_pins = (14, 15, 18)  # Microstep Resolution MS1-MS3 -> GPIO Pin
direction = 20  # Direction -> GPIO Pin
step = 21  # Step -> GPIO Pin

class CoffeeRotatorMotor:
    def __init__(self) :
        # RotatorMotor= RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "A4988")
        self.CurrentPosition = 0
        self.SemaphoreBusy = False
        self.NumberOfCups = 4


class CoffeeHtml:

    def __init__(self, startposition) :
        self.TPL = ""
        self.CurrentPosition = startposition
        self.updateHtml(self.CurrentPosition)
        self.queued_coffees = []

    def updateHtml(this, position) -> object:
        this.CurrentPosition = position
        this.TPL = '''
        <html>
            <!DOCTYPE html>
            <head><title>Frederiks Kaffeerotator</title></head>
            <body>
            <h2> Kaffeebesteller</h2>
                <img src="{{url_for('static', filename='pos_''' + str(this.CurrentPosition) +'''.jpg')}}" alt="Rotator Position 0" width="100" height="100">
                <br>
                   <a href="/RotateMotorToPosition?zielposition=0"><button>0</button></a>
                   <a href="/RotateMotorToPosition?zielposition=1"><button>1</button></a>
                   <a href="/RotateMotorToPosition?zielposition=2"><button>2</button></a>
                   <a href="/RotateMotorToPosition?zielposition=3"><button>3</button></a>
                <form method="POST" action="FlushMachine">
                <h5> Spüle die Maschine aus </h5>
                <input type="submit" value="Spüle" name="Spüle" />
               </form>
                <h5> Bestelle einen Kaffee </h5>
                <a href="/OrderCoffee?coffee=Espresso"><button>Espresso</button></a>
                <a href="/OrderCoffee?coffee=Cappuccino"><button>Cappuccino</button></a>
                <a href="/OrderCoffee?coffee=Latte"><button>Latte</button></a>
                <a href="/OrderCoffee?coffee=Flatwhite"><button>Flat White</button></a>
                
            </body>
        </html>
        '''


    def toString(self) -> str:
        print(self.TPL)
        return self.TPL


# Declare an named instance of class pass GPIO pins numbers
# RotatorMotor= RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "A4988")
myRotatorMotor: CoffeeRotatorMotor = CoffeeRotatorMotor()
TPL = CoffeeHtml(0)
app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string(TPL.toString())

@app.route('/flush', methods=['POST'])
def flush_machine():
    # Spülvorgang durchführen
    return 'Machine flushed'


@app.route('/OrderCoffee')
def Order_Coffee():

    TPL.queued_coffees.append(request.args["coffee"])
    print(TPL.queued_coffees)
    return render_template_string(TPL.toString())


@app.route('/status')
def machine_status():
    global rotator_position, queued_coffees
    return jsonify({
        'rotator_position': rotator_position,
        'queued_coffees': queued_coffees
    })


@app.route("/RotateMotorToPosition")
def RotateMotorToPosition():
    """ Rotate the motor to an absolute position."""
    waytogo: int = 0
    if myRotatorMotor.SemaphoreBusy: exit()
    myRotatorMotor.SemaphoreBusy = True
    ziel = int(request.args["zielposition"])

    print("Zielposition: " , ziel)
    degrees: int = 360 / myRotatorMotor.NumberOfCups
    waytogo =  ziel - myRotatorMotor.CurrentPosition
    print (ziel,myRotatorMotor.CurrentPosition, waytogo)
    if waytogo > 0:
        myRotatorMotor.CurrentPosition += waytogo
        #            motor_go(clockwise, steptype, steps, stepdelay, verbose, initdelay)
        # RotatorMotor.motor_go(True, "Full", 600, int(abs(waytogo)*degrees), False, .05)

    else:
        myRotatorMotor.CurrentPosition -= waytogo
        #            motor_go(clockwise, steptype, steps, stepdelay, verbose, initdelay)
        # RotatorMotor.motor_go(False, "Full", 600, int(abs(waytogo)*degrees), False, .05)
    TPL.updateHtml(ziel)
    myRotatorMotor.SemaphoreBusy = False
    return render_template_string(TPL.toString())


# Run the app on the local development server
if __name__ == "__main__":
    app.run(host='0.0.0.0');
