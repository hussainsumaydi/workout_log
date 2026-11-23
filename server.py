from flask import Flask, request
from workout_store import Workout, WorkoutStore

app = Flask(__name__)


@app.route('/workouts')
def get_workouts():
    muscle = request.args.get('muscle', '').strip()
    store = WorkoutStore('workouts.db')
    try:
        if muscle and muscle != 'All':
            workouts = store.filter_by_muscle(muscle)
        else:
            workouts = store.all()
        items = []
        for w in workouts:
            items.append(w.to_dict())
        return {'workouts': items}
    finally:
        store.close()


@app.route('/workouts/add', methods=['POST'])
def add_workout():
    name = request.form.get('name', '').strip()
    muscle = request.form.get('muscle', '').strip()
    weight_text = request.form.get('weight', '').strip()

    if not name or not muscle or not weight_text:
        return {'error': 'All fields (name, muscle, weight) are required.'}, 400

    try:
        weight = int(weight_text)
    except ValueError:
        return {'error': 'Weight must be a whole number.'}, 400

    if weight <= 0:
        return {'error': 'Weight must be greater than 0.'}, 400

    store = WorkoutStore('workouts.db')
    try:
        new_id = store.add(Workout(name, muscle, weight))
        return {'message': 'Workout added successfully.', 'id': new_id}
    finally:
        store.close()


@app.route('/workouts/edit', methods=['POST'])
def edit_workout():
    id_text = request.form.get('id', '').strip()
    name = request.form.get('name', '').strip()
    muscle = request.form.get('muscle', '').strip()
    weight_text = request.form.get('weight', '').strip()

    try:
        workout_id = int(id_text)
    except ValueError:
        return {'error': 'Invalid workout ID.'}, 400

    if not name or not muscle or not weight_text:
        return {'error': 'All fields (name, muscle, weight) are required.'}, 400

    try:
        weight = int(weight_text)
    except ValueError:
        return {'error': 'Weight must be a whole number.'}, 400

    if weight <= 0:
        return {'error': 'Weight must be greater than 0.'}, 400

    store = WorkoutStore('workouts.db')
    try:
        updated = store.update(Workout(name, muscle, weight, workout_id))
        if not updated:
            return {'error': 'Workout ID not found.'}, 404
        return {'message': 'Workout updated successfully.'}
    finally:
        store.close()


@app.route('/workouts/delete', methods=['POST'])
def delete_workout():
    id_text = request.form.get('id', '').strip()

    try:
        workout_id = int(id_text)
    except ValueError:
        return {'error': 'Invalid workout ID.'}, 400

    store = WorkoutStore('workouts.db')
    try:
        deleted = store.delete(workout_id)
        if not deleted:
            return {'error': 'Workout ID not found.'}, 404
        return {'message': 'Workout deleted successfully.'}
    finally:
        store.close()


if __name__ == '__main__':
    print('Workout server running on http://127.0.0.1:5050')
    app.run(port=5050)