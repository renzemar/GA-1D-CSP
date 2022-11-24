import datetime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import Schema, fields, ValidationError, pre_load
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from uuid import uuid4
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
db = SQLAlchemy(app)


@app.before_request
def create_tables():
    db.drop_all()
    db.create_all()


### MODELS ###

class RootOrder(db.Model):
    __tablename__ = 'root_order'

    id = db.Column(db.Integer, primary_key=True)

    # order = db.relationship('Order', backref=db.backref('root_order'))

    def __repr__(self):
        return f"{self.id}, {self.length}"


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer, nullable=False)
    base_panel_id = db.Column(db.Integer)
    root_order_id = db.Column(db.Integer, db.ForeignKey('root_order.id'))
    root_order = db.relationship('RootOrder', backref=db.backref('orders'))

    def __repr__(self):
        return f"{self.id}, {self.length}"


### SCHEMAS ###


# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class RootOrderSchema(SQLAlchemySchema):
    class Meta:
        model = RootOrder

    id = auto_field()
    orders = fields.Nested('OrderSchema', many=True)  # try auto_field here as well


class OrderSchema(SQLAlchemySchema):
    class Meta:
        model = Order

    id = auto_field()
    length = auto_field()
    base_panel_id = auto_field()
    root_order_id = auto_field()


# custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
root_order_schema = RootOrderSchema()
roots_order_schema = RootOrderSchema(many=True)


### ROUTES ###

@app.route('/order', methods=['POST'])
def add_order():
    json_data = request.get_json()
    if not json_data:
        return {'message': 'No input data provided'}, 400
    # Validate and deserialize input
    try:
        data = order_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    root = RootOrder.query.filter_by(id=data['root_order_id']).first()
    if not root:
        # Create a new root order
        root = RootOrder(id=data['root_order_id'])
        db.session.add(root)

    # Create new order
    order = Order(id=data['id'], length=data['length'],
                  root_order_id=data['root_order_id'])
    db.session.add(order)
    db.session.commit()
    result = order_schema.dump(Order.query.get(order.id))
    return {"status": 'success', 'data': result}, 201


@app.route('/rootorders', methods=['POST'])
def add_orders():
    json_data = request.get_json()
    if not json_data:
        return {'message': 'No input data provided'}, 400
    # Validate and deserialize input
    try:
        data = root_order_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    root = RootOrder.query.filter_by(id=data['id']).first()
    if not root:
        # Create a new root order
        root = RootOrder(id=data['id'])
        db.session.add(root)

    for order in data['orders']:
        # Create new order
        order = Order(id=order['id'], length=order['length'],
                      root_order_id=order['root_order_id'])
        db.session.add(order)

    # Run optimization
    OptimizeCuttingStock_Dummy(root)

    db.session.commit()
    result = root_order_schema.dump(root.query.get(root.id))
    return {"status": 'success', 'data': result}, 201


@app.route('/order', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    results = orders_schema.dump(orders)
    return {"status": 'success', 'orders': results}, 200


@app.route('/root/<int:id>', methods=['GET'])
def get_root_order(id):
    try:
        root_order = RootOrder.query.filter_by(id=id).one()
    except NoResultFound:
        return {'message': 'Order not found'}, 404
    result = root_order_schema.dump(root_order)
    return {"status": 'success', 'orders': result}, 200


@app.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    try:
        order = Order.query.filter_by(id=id).one()
    except NoResultFound:
        return {'message': 'Order not found'}, 404
    result = order_schema.dump(order)
    return {"status": 'success', 'orders': result}, 200


### FUNCTIONS ###


def OptimizeCuttingStock_Dummy(root):
    # Dummy function to test the API
    # Returns a list of orders belonging to a base panel of length 12450

    # Get all orders
    orders = Order.query.filter_by(root_order_id=root.id).all()

    # initialize base panel
    panels = [3100161, 3100162, 3100163, 3100164, 3100165, 3100165, 3100166, 3100167, 3100168, 3100169, 3100170]
    base_length = 12450
    cum_length = 0
    panel_index = 0
    iterations = len(orders)

    # Loop until all panels are used and panels list is empty
    while iterations > 0 and len(panels) > 0:
        for order in orders:
            if cum_length + order.length <= base_length:

                # Assign order to base panel
                order.base_panel_id = panels[0]

                # Update cumulative length
                cum_length += order.length
                iterations -= 1
            else:

                # Assign order to base panel
                order.base_panel_id = panels[panel_index]
                cum_length = order.length
                iterations -= 1

                # Remove base panel from list
                panels.pop(0)

                if len(panels) == 0:
                    break


if __name__ == "__main__":
    app.run(debug=True)  # only in testing environment
