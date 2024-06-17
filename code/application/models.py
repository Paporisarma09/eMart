from application.database import db


# Create all the classes
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key = True,autoincrement=True,nullable=False)
    user_name = db.Column(db.String, unique=True,nullable = False)
    user_password = db.Column(db.String, nullable = False)
    user_role = db.Column(db.String, nullable = False)

class ProductCategory(db.Model):
    __tablename__ = 'productcategory'
    productcategory_id = db.Column(db.Integer, primary_key = True, autoincrement=True,)
    productcategory_name = db.Column(db.String, nullable = False)
    productcategory_isdeleted = db.Column(db.Integer, nullable = False)
    products = db.relationship('Product', backref = "productcategory")

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key = True, autoincrement=True,)
    product_name = db.Column(db.String, nullable = False)
    productcategory_id = db.Column(db.Integer, db.ForeignKey('productcategory.productcategory_id'), nullable = False)
    product_unit = db.Column(db.String, nullable = False)
    product_rateperunit = db.Column(db.Float, nullable = False)
    product_quantity = db.Column(db.Integer, nullable = False)
    product_expirydate = db.Column(db.DateTime, nullable = True)
    product_isdeleted = db.Column(db.Integer, nullable = False)
    
class UserCartDetails(db.Model):
    __tablename__ = 'usercartdetails'
    usercartdetails_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    usercartdetails_productquantity = db.Column(db.Integer, nullable=False)
    usercartdetails_totalamount = db.Column(db.Float, nullable=False)
    usercartdetails_cartstatus = db.Column(db.Integer, nullable = False)
    usercartdetails_checkoutdatetime = db.Column(db.DateTime, nullable = True)
    user = db.relationship('User', backref='usercartdetails')
    product = db.relationship('Product', backref='productcartdetails')
