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


@app.before_first_request
def create_tables():
    db.create_all()


# @app.before_request
# def create_tables():
#    db.drop_all()
#    db.create_all()


# MODELS #

class RootOrder(db.Model):
    __tablename__ = 'root_order'

    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"{self.id}, {self.length}"


class RootBasePanel(db.Model):
    __tablename__ = 'root_base_panel'

    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"{self.id}, {self.length}"


class BasePanel(db.Model):
    __tablename__ = 'base_panels'

    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer, nullable=False)
    isCut = db.Column(db.Boolean, default=False)
    waste = db.Column(db.Integer, default=12450)  # As of now all base lengths are 12450mm
    root_base_panel_id = db.Column(db.Integer, db.ForeignKey('root_base_panel.id'))
    root_base_panel = db.relationship('RootBasePanel', backref=db.backref('base_panels'))

    def __repr__(self):
        return f"{self.id}, {self.length}"


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer, nullable=False)
    isCut = db.Column(db.Boolean, default=False)
    root_order_id = db.Column(db.Integer, db.ForeignKey('root_order.id'))
    root_order = db.relationship('RootOrder', backref=db.backref('orders'))
    base_panel_id = db.Column(db.Integer, db.ForeignKey('base_panels.id'))
    base_panel = db.relationship('BasePanel', backref=db.backref('orders'))

    def __repr__(self):
        return f"{self.id}, {self.length}"


# SCHEMAS #


# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class RootOrderSchema(SQLAlchemySchema):
    class Meta:
        model = RootOrder

    id = auto_field()
    orders = fields.Nested('OrderSchema', many=True)  # try auto_field here as well


class RootBasePanelSchema(SQLAlchemySchema):
    class Meta:
        model = RootBasePanel

    id = auto_field()
    base_panels = fields.Nested('BasePanelSchema', many=True)


class BasePanelSchema(SQLAlchemySchema):
    class Meta:
        model = BasePanel

    id = auto_field()
    length = auto_field()
    isCut = auto_field()
    waste = auto_field()
    root_base_panel_id = auto_field()
    orders = fields.Nested('OrderSchema', many=True)


class OrderSchema(SQLAlchemySchema):
    class Meta:
        model = Order

    id = auto_field()
    length = auto_field()
    isCut = auto_field()
    base_panel_id = auto_field()
    root_order_id = auto_field()


# custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


root_order_schema = RootOrderSchema()
roots_order_schema = RootOrderSchema(many=True)

root_base_panel_schema = RootBasePanelSchema()
roots_base_panel_schema = RootBasePanelSchema(many=True)

base_panel_schema = BasePanelSchema()
base_panels_schema = BasePanelSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


### ROUTES ###

@app.route('/basepanels', methods=['POST'])
def add_base_panels():
    json_data = request.get_json()
    if not json_data:
        return {'message': 'No input data provided'}, 400
    # Validate and deserialize input
    try:
        data = root_base_panel_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    # Create a new root order
    root_base_panel = find_or_create_root_base(data)

    # Create base panels if no duplicate is found
    for base_panel in data['base_panels']:
        duplicate = BasePanel.query.filter_by(id=data['id']).first()
        if not duplicate:
            base_panel = BasePanel(id=base_panel['id'], length=base_panel['length'],
                                   root_base_panel_id=root_base_panel.id)
            db.session.add(base_panel)
    db.session.commit()
    result = root_base_panel_schema.dump(root_base_panel.query.get(root_base_panel.id))
    return {"status": 'success', 'data': result}, 201


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

    # Find or create root
    order = find_or_create_root_order(data)

    # Create new order if no duplicate is found
    find_or_create_order(data)

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

    root = find_or_create_root_order(data)

    # Create new order if no duplicate is found
    find_or_create_order(data)

    # Run optimization
    OptimizeCuttingStock_Dummy(root)

    db.session.commit()
    result = root_order_schema.dump(root.query.get(root.id))
    return {"status": 'success', 'data': result}, 201


@app.route('/basepanels', methods=['GET'])
def get_basepanels():
    base_panels = BasePanel.query.all()
    result = base_panels_schema.dump(base_panels)
    return {"status": 'success', 'data': result}, 201


@app.route('/order', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    results = orders_schema.dump(orders)
    return {"status": 'success', 'data': results}, 200


@app.route('/rootorder/<int:id>', methods=['GET'])
def get_root_order(id):
    try:
        root_order = RootOrder.query.filter_by(id=id).one()
    except NoResultFound:
        return {'message': 'Order not found'}, 404
    result = root_order_schema.dump(root_order)
    return {"status": 'success', 'data': result}, 200


@app.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    try:
        order = Order.query.filter_by(id=id).one()
    except NoResultFound:
        return {'message': 'Order not found'}, 404
    result = order_schema.dump(order)
    return {"status": 'success', 'data': result}, 200


### FUNCTIONS ###


# Dummy optimization function
def OptimizeCuttingStock_Dummy(root):
    # Dummy function to test the API
    # Returns a list of orders belonging to a base panel of length 12450

    # Get orders from root
    orders = root.orders.copy()

    # orders = Order.query.filter_by(root_id=root.id).all()

    # initialize base panel
    panels = BasePanel.query.filter_by(isCut=False).all()

    # A while loop that loops until all orders have isCut set to True or until all base panels are cut
    for panel in panels:
        while not panel.isCut and orders:
            for order in orders:
                if order.isCut:
                    continue
                if panel.waste - order.length >= 0:
                    order.isCut = True
                    order.base_panel_id = panel.id
                    order.root_order_id = root.id
                    panel.waste = panel.waste - order.length
                    orders.pop(orders.index(order))
                else:
                    panel.isCut = True
                    break


# Find or create root
def find_or_create_root_order(data):
    root = RootOrder.query.filter_by(id=data['id']).first()
    if not root:
        # Create a new root order
        root = RootOrder(id=data['id'])
        db.session.add(root)
    return root


# Find or create root
def find_or_create_root_base(data):
    root = RootBasePanel.query.filter_by(id=data['id']).first()
    if not root:
        # Create a new root order
        root = RootBasePanel(id=data['id'])
        db.session.add(root)
    return root


# Create order no duplicate is found
def find_or_create_order(data):
    for order in data['orders']:
        duplicate_order = Order.query.filter_by(id=order['id']).first()
        if not duplicate_order:
            new_order = Order(id=order['id'], length=order['length'],
                              root_order_id=order['root_order_id'])
            db.session.add(new_order)


if __name__ == "__main__":
    app.run(debug=True)  # only in testing environment
