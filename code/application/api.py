from flask_restful import Resource, fields, marshal_with, request, reqparse
from application.models import User, ProductCategory, Product, UserCartDetails
from application.database import db
from application.validation import BusinessValidationError, NotFoundError, DuplicationError
import datetime as datetime


user_fields = {
    "user_name": fields.String,
    "user_role": fields.String
}


create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('password')
create_user_parser.add_argument('role')

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('username')
update_user_parser.add_argument('newpassword')
update_user_parser.add_argument('role')

delete_user_parser = reqparse.RequestParser()
delete_user_parser.add_argument('username')
delete_user_parser.add_argument('role')

#User APIs Section
class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, username, role):
        existing_user = User.query.filter_by(user_name = username, user_role = role).first()
        if existing_user:
            return existing_user
        else:
            raise NotFoundError(404, "User not found")

    @marshal_with(user_fields)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        password = args.get("password", None)
        userrole = args.get("role", None)
        if username is None or not username.strip():
            raise BusinessValidationError(400, "US1002", "Username is required.")
        
        if password is None or not password.strip():
            raise BusinessValidationError(400, "US1003", "Password is required.")
        
        if userrole is None or not userrole.strip():
            raise BusinessValidationError(400, "US1004", "User Role is required")
        
        if password != None and len(password) < 8:
            raise BusinessValidationError(400, "US1005", "The length of password should be at least 8 characters long.")
        
        existinguser = User.query.filter_by(user_name = username, user_role = userrole).first()
        if existinguser != None:
            raise DuplicationError(409, "Username already exists")
        
        user = User(
                    user_name = username,
                    user_password = password,
                    user_role = userrole
                )
        db.session.add(user)
        db.session.commit()
        return user
    
    @marshal_with(user_fields)
    def put(self):
        args = update_user_parser.parse_args()
        username = args.get("username", None)
        newpassword = args.get("newpassword", None)
        userrole = args.get("role", None)
        if username is None or not username.strip():
            raise BusinessValidationError(400, "US1002", "Username is required")
        
        if newpassword is None or not newpassword.strip(): 
            raise BusinessValidationError(400, "US1003", "Password is required")
        
        if userrole is None or not userrole.strip():
            raise BusinessValidationError(400, "US1004", "User Role is required")
        
        if newpassword != None and len(newpassword) < 8:
            raise BusinessValidationError(400, "US1005", "The length of password should be at least 8 characters long")
        
        existinguser = User.query.filter_by(user_name = username, user_role = userrole).first()
        if existinguser is None:
            raise NotFoundError(404, "User not found")
        
        if existinguser.user_password ==  newpassword:
            raise BusinessValidationError(400, "US1006", "User password cannot be same as previous password.")
        
        existinguser.user_password = newpassword
        db.session.commit()
        return existinguser
    
    def delete(self, username, role):
        if username is None:
            raise BusinessValidationError(400, "US1002", "Username is required")
        
        if role is None:
            raise BusinessValidationError(400, "US1004", "User Role is required")
        
        existinguser = User.query.filter_by(user_name = username, user_role = role).first()
        if existinguser is None:
            raise NotFoundError(404, "User not found")
        usercartdetails = UserCartDetails.query.filter_by(user_id = existinguser.user_id).first()
        if usercartdetails:
            raise BusinessValidationError(400, "US1007", "User is associated with cart.")
        db.session.delete(existinguser)
        db.session.commit()
        return "User succesfully delted", 200

# ProductCategory APIs Section
productcategory_fields = {
    "productcategory_id": fields.String,
    "productcategory_name": fields.String,
    "productcategory_isdeleted": fields.Integer,
}

createproductcategory_parser = reqparse.RequestParser()
createproductcategory_parser.add_argument('productcategoryname')

update_productcategory_parser = reqparse.RequestParser()
update_productcategory_parser.add_argument('productcategoryid')
update_productcategory_parser.add_argument('newproductcategoryname')

class ProductCategoryAPI(Resource):
    @marshal_with(productcategory_fields)
    def get(self, productcategoryid):
        existing_productcategory = ProductCategory.query.get(productcategoryid)
        if existing_productcategory is not None:
            return existing_productcategory
        else:
            raise NotFoundError(404, "ProductCategory not found")

    @marshal_with(productcategory_fields)
    def post(self):
        args = createproductcategory_parser.parse_args()
        productcategoryname = args.get("productcategoryname", None)
        if productcategoryname is None or not productcategoryname.strip():
            raise BusinessValidationError(400, "PC1001", "ProductCategoryName is required.")
        
        existingproductcategory = ProductCategory.query.filter_by(productcategory_name = productcategoryname).first()
        if existingproductcategory != None:
            raise DuplicationError(409, "ProductCategory already exists")
        
        productcategory = ProductCategory(
                    productcategory_name = productcategoryname,
                    productcategory_isdeleted = 0)
        db.session.add(productcategory)
        db.session.commit()
        return productcategory
    
    @marshal_with(productcategory_fields)
    def put(self):
        args = update_productcategory_parser.parse_args()
        newproductcategoryname = args.get("newproductcategoryname", None)
        productcategoryid = args.get("productcategoryid", None)
        if newproductcategoryname is None or not newproductcategoryname.strip():
            raise BusinessValidationError(400, "PC1001", "ProductCategoryName is required.")
        
        existingproductcategory = ProductCategory.query.get(productcategoryid)
        if existingproductcategory is None:
            raise NotFoundError(404, "ProductCategory not found")
        
        existingproductcategory.productcategory_name = newproductcategoryname
        db.session.commit()
        return existingproductcategory
    
    def delete(self, productcategoryid):
        if productcategoryid == 0:
            raise BusinessValidationError(400, "PC1002", "ProductCategoryId is required.")
        
        existingproductcategory = ProductCategory.query.get(productcategoryid)
        if existingproductcategory is None:
            raise NotFoundError(404, "ProductCategory not found")
        associateproducts = Product.query.filter_by(productcategory_id = productcategoryid).first()
        if associateproducts:
            raise BusinessValidationError(400, "PC1003", "ProductCategory is associated with products.")
        existingproductcategory.productcategory_isdeleted = 1
        db.session.commit()
        return "ProductCategory succesfully deleted", 200

# Product APIs Section
product_fields = {
    "product_id": fields.Integer,
    "product_name": fields.String,
    "productcategory_id": fields.String,
    "product_unit": fields.String,
    "product_rateperunit": fields.Float,
    "product_quantity": fields.Integer,
    "product_expirydate": fields.String,
    "product_isdeleted": fields.Integer
}

createproduct_parser = reqparse.RequestParser()
createproduct_parser.add_argument('productname')
createproduct_parser.add_argument('productcategoryid')
createproduct_parser.add_argument('rateperunit')
createproduct_parser.add_argument('quantity')
createproduct_parser.add_argument('expirydate')
createproduct_parser.add_argument('unit')

update_product_parser = reqparse.RequestParser()
update_product_parser.add_argument('productid')
update_product_parser.add_argument('productname')
update_product_parser.add_argument('newunit')
update_product_parser.add_argument('newrateperunit')
update_product_parser.add_argument('newquantity')
update_product_parser.add_argument('newexpirydate')

class ProductAPI(Resource):
    @marshal_with(product_fields)
    def get(self, productid):
        existing_product = Product.query.get(productid)
        if existing_product is not None:
            return existing_product
        else:
            raise NotFoundError(404, "Product not found")

    @marshal_with(product_fields)
    def post(self):
        args = createproduct_parser.parse_args()
        productname = args.get("productname", None)
        productcategoryid = args.get("productcategoryid", None)
        rateperunit = args.get("rateperunit", None)
        quantity = args.get("quantity", None)
        unit = args.get("unit", None)
        expirydate = args.get("expirydate", None)
        if productname is None or not productname.strip():
            raise BusinessValidationError(400, "PR1002", "ProductName is required.")
        
        if productcategoryid is None or productcategoryid == 0:
            raise BusinessValidationError(400, "PR1003", "Associated ProductCateoryId is required.")
        
        if unit is None or not unit.strip():
            raise BusinessValidationError(400, "PR1004", "Product Unit is required.")
        
        if quantity is None or quantity == 0:
            raise BusinessValidationError(400, "PR1005", "Product Quantity is required.")
        
        if rateperunit is None or rateperunit == 0:
            raise BusinessValidationError(400, "PR1006", "Product Rate Per Unit is required.")
        
        existingproduct = Product.query.filter_by(product_name = productname).first()
        if existingproduct != None:
            raise DuplicationError(409, "Product already exists")
        
        if expirydate:
            expirydate = datetime.datetime.strptime(expirydate, '%Y-%m-%d')    
        product = Product(
                    product_name = productname,
                    productcategory_id = productcategoryid,
                    product_unit = unit,
                    product_rateperunit = rateperunit,
                    product_quantity = quantity,
                    product_expirydate = expirydate,
                    product_isdeleted = 0)
        db.session.add(product)
        db.session.commit()
        return product
    
    @marshal_with(product_fields)
    def put(self):
        args = update_product_parser.parse_args()
        productid = args.get("productid", None)
        productname = args.get("productname", None)
        newunit = args.get("newunit", None)
        newrateperunit = args.get("newrateperunit", None)
        newquantity = args.get("newquantity", None)
        newexpirydate = args.get("newexpirydate", None)
        
        if productid == '0':
            raise BusinessValidationError(400, "PR1001", "ProductId is required.")
        
        if newunit is None or not newunit.strip():
            raise BusinessValidationError(400, "PR1004", "Product Unit is required.")
        
        if newrateperunit is None or newrateperunit == '0':
            raise BusinessValidationError(400, "PR1006", "Product Rate Per Unit is required.")
        
        if newquantity is None or newquantity == '0':
            raise BusinessValidationError(400, "PR1005", "Product Quantity is required.")
        
        existingproduct = Product.query.filter_by(product_id = productid, product_name = productname).first()
        if existingproduct is None:
            raise NotFoundError(404, "Product not found")
        
        existingproduct.product_unit = newunit
        existingproduct.product_rateperunit = newrateperunit
        existingproduct.product_quantity = newquantity
        if newexpirydate:
            expirydate = datetime.datetime.strptime(newexpirydate, '%Y-%m-%d')   
            existingproduct.product_expirydate = expirydate    
        db.session.commit()
        return existingproduct
    
    def delete(self, productid):
        if productid == 0:
            raise BusinessValidationError(400, "PR1001", "ProductId is required.")
        
        existingproduct = Product.query.get(productid)
        if existingproduct is None:
            raise NotFoundError(404, "Product not found")
        associateduserCartDetails = UserCartDetails.query.filter_by(product_id = productid, usercartdetails_cartstatus = 1).first()
        if associateduserCartDetails:
            raise BusinessValidationError(400, "PR1007", "Product is associated with user cart.")
        existingproduct.product_isdeleted = 1
        db.session.commit()
        return "Product succesfully deleted", 200
    
# UserCartDetails APIs Section
usercart_fields = {
    "usercartdetails_id": fields.Integer,
    "user_id": fields.Integer,
    "product_id": fields.Integer,
    "usercartdetails_productquantity": fields.Integer,
    "usercartdetails_totalamount": fields.Float,
    "usercartdetails_cartstatus": fields.Integer,
    "usercartdetails_checkoutdatetime": fields.String
}

createusercart_parser = reqparse.RequestParser()
createusercart_parser.add_argument('userid')
createusercart_parser.add_argument('productid')
createusercart_parser.add_argument('productquantity')

updateusercart_parser = reqparse.RequestParser()
updateusercart_parser.add_argument('usercartdetailsid')
updateusercart_parser.add_argument('productquantity')
updateusercart_parser.add_argument('ischeckout')

class UserCartDetailsAPI(Resource):
    @marshal_with(usercart_fields)
    def get(self, id):
        existing_usercartdetails = UserCartDetails.query.get(id)
        if existing_usercartdetails is not None:
            return existing_usercartdetails
        else:
            raise NotFoundError(404, "User doesnt have any product in the cart")

    @marshal_with(usercart_fields)
    def post(self):
        args = createusercart_parser.parse_args()
        userid = args.get("userid", None)
        productid = args.get("productid", None)
        productquantity = args.get("productquantity", None)
        
        if userid is None or userid == '0':
            raise BusinessValidationError(400, "USC1001", "UserId is required.")
        
        if productid is None or productid == '0':
            raise BusinessValidationError(400, "USC1002", "ProductId is required.")
        try:
            productquantity = float(productquantity)
        except ValueError:
            raise BusinessValidationError(400, "USC1003", "Invalid Product Quantity format.")

        if productquantity is None or productquantity == '0':
            raise BusinessValidationError(400, "USC1003", "Product Qunatity should be greater than 0.")
        
        retrieved_product = Product.query.get(productid)
        if productquantity > retrieved_product.product_quantity:
            raise BusinessValidationError(400, "USC1004", f'Please select a quantity lesser than {retrieved_product.product_quantity}')
        else:
            retrieved_product.product_quantity = retrieved_product.product_quantity - productquantity
            existingusercartdetails = UserCartDetails.query.filter_by(product_id = productid, usercartdetails_cartstatus = 1).first()
            if existingusercartdetails:
                existingusercartdetails.usercartdetails_productquantity = existingusercartdetails.product_quantity + productquantity
                existingusercartdetails.usercartdetails_totalamount = retrieved_product.product_rateperunit * existingusercartdetails.usercartdetails_productquantity
            else:
                userCartDetails = UserCartDetails(
                                    user_id = userid,
                                    product_id = productid,
                                    usercartdetails_productquantity = productquantity,
                                    usercartdetails_totalamount = retrieved_product.product_rateperunit * productquantity,
                                    usercartdetails_cartstatus = 1)
                db.session.add(userCartDetails)
                
            db.session.commit()
        if existingusercartdetails:
            return existingusercartdetails
        else:
            return userCartDetails
    
    @marshal_with(usercart_fields)
    def put(self):
        args = updateusercart_parser.parse_args()
        usercartdetailsid = args.get('usercartdetailsid')
        productquantity= args.get('productquantity')
        ischeckout = args.get('ischeckout')    
        
        if usercartdetailsid is None or usercartdetailsid == '0':
            raise BusinessValidationError(400, "USC1005", "UserCartDetailsId is required.")
        
        if productquantity is None or productquantity == '0':
            raise BusinessValidationError(400, "USC1003", "Product Qunatity should be greater than 0.")
        
        existingusercartdetails = UserCartDetails.query.get(usercartdetailsid)
        if existingusercartdetails.usercartdetails_cartstatus == 2:
            raise BusinessValidationError(400, "USC1006", "Cannot update the user cart details, as it is already checked out.")
        
        retrieved_product = Product.query.get(existingusercartdetails.product.product_id)
        if retrieved_product:
            productquantityreceived = int(request.form['productquantity'])
            diffquantity = productquantityreceived - existingusercartdetails.usercartdetails_productquantity
            if diffquantity == 0 and ischeckout == False:
                raise BusinessValidationError(400, "USC1007", "There is no change in the product quantity.")
                
            if diffquantity > 0:
                if diffquantity > retrieved_product.product_quantity:
                    raise BusinessValidationError(400, "USC1004", f'Please select a quantity lesser than {retrieved_product.product_quantity}')
                else:
                    retrieved_product.product_quantity = retrieved_product.product_quantity - productquantityreceived
                    existingusercartdetails.usercartdetails_productquantity = existingusercartdetails.usercartdetails_productquantity + diffquantity
                    existingusercartdetails.usercartdetails_totalamount = retrieved_product.product_rateperunit * existingusercartdetails.usercartdetails_productquantity
                    if ischeckout == True:
                        existingusercartdetails.usercartdetails_checkoutdatetime = datetime.now()
                        existingusercartdetails.usercartdetails_cartstatus = 2
            else:
                retrieved_product.product_quantity = retrieved_product.product_quantity - diffquantity
                existingusercartdetails.usercartdetails_productquantity = existingusercartdetails.product_quantity + diffquantity
                existingusercartdetails.usercartdetails_totalamount = retrieved_product.product_rateperunit * existingusercartdetails.usercartdetails_productquantity
                if ischeckout == True:
                        existingusercartdetails.usercartdetails_checkoutdatetime = datetime.now()
                        existingusercartdetails.usercartdetails_cartstatus = 2
            db.session.commit()
            return existingusercartdetails
    
    def delete(self, id):
        existingusercartdetails = UserCartDetails.query.get(id)
        retrieved_product = Product.query.get(existingusercartdetails.product.product_id)
        if retrieved_product:
            retrieved_product.product_quantity = retrieved_product.product_quantity + existingusercartdetails.usercartdetails_productquantity
            db.session.delete(existingusercartdetails)
            db.session.commit()
        return "User Cart Details succesfully deleted", 200
    
