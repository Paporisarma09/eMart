from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
import os
from flask import redirect, url_for
from datetime import datetime
from flask import current_app as app
from application.models import db, User, Product, ProductCategory, UserCartDetails

# All the endpoints start here
@app.route("/", methods=["GET", "POST"])
def user():
    if request.method == 'GET':
        return render_template("login.html") 
    if request.method == 'POST':
         role= request.form.get('role')
         username= request.form.get('username')
         password=request.form.get('password')
         existing_user = User.query.filter_by(user_name = username, user_role = role).first()
         if existing_user:
             if existing_user.user_password != password:
                 message = "Invalid password. Please retry."
                 return render_template("login.html", message = message)
             if existing_user.user_role == 'Manager':
                 return redirect(url_for('getproductdetailsforadmin'))
             else:
                 return getproductdetailsforuser(existing_user)
         else:  
            message = "User not found. Please register first."
            return render_template("login.html", message = message)
         

@app.route("/getproductdetailsforadmin", methods=["GET"])
def getproductdetailsforadmin():
    retrievedProductCategories = ProductCategory.query.all()
    return render_template("product_category_details.html",
                           productCategories = retrievedProductCategories) 

@app.route("/getproductdetailsforuser/<int:userid>", methods=["GET"])
def getproductdetailsforuserbyuserid(userid):
    retrievedUser = User.query.get(userid)
    return getproductdetailsforuser(retrievedUser)

# @app.route("/getproductdetailsforuser", methods=["GET"])
def getproductdetailsforuser(user):
    retrievedProductCategories = ProductCategory.query.all()
    retrieved_userCartDetails = UserCartDetails.query.filter_by(user_id = user.user_id, usercartdetails_cartstatus = 1).all()
    numOfCartItems = 0
    if retrieved_userCartDetails:
        numOfCartItems = sum(cart_detail.usercartdetails_productquantity for cart_detail in retrieved_userCartDetails)
    return render_template("user_productcategories.html",
                           productCategories = retrievedProductCategories,
                           user = user,
                           numOfCartItems = numOfCartItems) 

# Register a new user here
@app.route("/register", methods=["GET", "POST"])
def Register():
    if request.method == 'GET':
        return render_template("register.html") 
    if request.method == 'POST':
        userrole = request.form['role']
        username = request.form['username']
        password = request.form['password']
        if userrole is None:
            message = "Please select a role."
            return render_template("register.html", message = message)
        # Check if the student is already present
        existing_user = User.query.filter_by(user_name = username, user_role = userrole).first()
        if existing_user:
            message = "User already registered. Please login."
            return render_template("register.html", message = message)
        
        user = User(
                    user_name = username,
                    user_password = password,
                    user_role = userrole
                )
        db.session.add(user)
        db.session.commit()
        message = "User registered succesfully. Please login now."
        return render_template("register.html", message = message)

#Add a new Product Category
@app.route("/addProductCategory", methods = ["GET", "POST"])
def add_category():
    if request.method == 'GET':
        return render_template("add_product_category.html")
    if request.method == 'POST':
        productcategoryname = request.form['productCategoryName']
        productcategory = ProductCategory(
                    productcategory_name = productcategoryname,
                    productcategory_isdeleted = 0)
        db.session.add(productcategory)
        db.session.commit()
        
    return redirect(url_for('getproductdetailsforadmin'))

# @app.route("<int:user_id>/addtoCart/<int:product_id>", methods = ["GET", "POST"])    
@app.route("/editProductCategory/<int:productcategory_id>", methods = ["GET", "POST"])
def editproductCategory(productcategory_id):
    if request.method == 'GET':
        retrieved_productcategory = ProductCategory.query.get(productcategory_id)
        return render_template("edit_product_category.html", retrieved_productcategory = retrieved_productcategory)
    if request.method == 'POST':
        retrieved_productcategory = ProductCategory.query.get(productcategory_id)
        if retrieved_productcategory:
            productcategoryname = request.form['productCategoryName']
            retrieved_productcategory.productcategory_name = productcategoryname
            db.session.commit()
            return redirect(url_for('getproductdetailsforadmin'))

@app.route("/deleteProductCategory/<int:productcategory_id>", methods = ["GET","POST"])
def deleteProductCategory(productcategory_id):
    retrieved_productcategory = ProductCategory.query.get(productcategory_id)
    if request.method == 'GET':
        return render_template("delete_product_category.html",
                               retrieved_productcategory = retrieved_productcategory)
    if request.method == 'POST':
        retrieved_productcategory = ProductCategory.query.get(productcategory_id)
        if retrieved_productcategory:
            products = Product.query.filter_by(productcategory_id = productcategory_id, product_isdeleted = 0).all()
            if products is not None and len(products) > 0 :
                error_message = f'{retrieved_productcategory.productcategory_name} is associated with products'
                return render_template("delete_product_category.html",
                                        retrieved_productcategory = retrieved_productcategory,
                                        error_message = error_message)
            userCartDetails = UserCartDetails.query.filter(UserCartDetails.product.has(productcategory_id = productcategory_id), UserCartDetails.usercartdetails_cartstatus == 1).all()
            if userCartDetails is not None and len(userCartDetails) > 0 :
                error_message = f'Product {retrieved_productcategory.productcategory_name} is already present in user cart'
                return render_template("delete_product_category.html",
                                        retrieved_productcategory = retrieved_productcategory,
                                        error_message = error_message)
            else:
                retrieved_productcategory.productcategory_isdeleted = 1
                db.session.commit()
    return redirect(url_for('getproductdetailsforadmin'))

# Restore Product Category
@app.route("/restoreProductCategory/<int:productcategory_id>", methods = ["GET","POST"])
def restoreProductCategory(productcategory_id):
    retrieved_productcategory = ProductCategory.query.get(productcategory_id)
    if retrieved_productcategory:
        retrieved_productcategory.productcategory_isdeleted = 0
        db.session.commit()
    return redirect(url_for('getproductdetailsforadmin'))

#Add a new Product for a Product Category
@app.route("/addProduct/<productcategory_id>", methods = ["GET", "POST"])
def add_product(productcategory_id):
    if request.method == 'GET':
        return render_template("add_product.html",
                               productcategoryid = productcategory_id)
    if request.method == 'POST':
        productcategory = ProductCategory.query.get(productcategory_id)
        if productcategory:
            expirydate = None
            productname = request.form['productname']
            unit= request.form['unit']
            rateperunit = request.form['rateperunit']
            quantity= request.form['quantity']
            expirydate_str = request.form['expirydate']
            if expirydate_str:
                expirydate = datetime.strptime(expirydate_str, '%Y-%m-%d')    
            product = Product(
                        product_name = productname,
                        productcategory_id = productcategory_id,
                        product_unit = unit,
                        product_rateperunit = rateperunit,
                        product_quantity = quantity,
                        product_expirydate = expirydate,
                        product_isdeleted = 0)
            db.session.add(product)
            db.session.commit()

    return redirect(url_for('getproductdetailsforadmin'))
        
    
@app.route("/editProduct/<product_id>", methods = ["GET", "POST"])
def edit_product(product_id):
    if request.method == 'GET':
        retrieved_product = Product.query.get(product_id)
        return render_template("edit_product.html",
                               retrieved_product = retrieved_product)
    if request.method == 'POST':
        retrieved_product = Product.query.get(product_id)
        if retrieved_product:
            retrieved_product.product_unit = request.form['unit']
            retrieved_product.product_rateperunit = request.form['rateperunit']
            retrieved_product.product_quantity = request.form['quantity']
            expirydate_str = request.form['expirydate']
            if expirydate_str:
                expirydate = datetime.strptime(expirydate_str, '%Y-%m-%d')   
                retrieved_product.product_expirydate = expirydate    
            db.session.commit()

    return redirect(url_for('getproductdetailsforadmin'))
    
@app.route("/deleteProduct/<product_id>", methods = ["GET","POST"])
def delete_product(product_id):
    retrieved_product = Product.query.get(product_id)
    if request.method == 'GET':
        return render_template("delete_product.html",
                               retrieved_product = retrieved_product)
    if retrieved_product:
        userCartDetails = UserCartDetails.query.filter_by(product_id = product_id, usercartdetails_cartstatus = 1).all()
        if userCartDetails is not None and len(userCartDetails) > 0:
            error_message = f'Product {retrieved_product.product_name} is already present in user cart'
            return render_template("delete_product.html",
                                    retrieved_product = retrieved_product,
                                    error_message = error_message)
        else:
            retrieved_product.product_isdeleted = 1
            db.session.commit()
    return redirect(url_for('getproductdetailsforadmin'))
# Restore Product
@app.route("/restoreProduct/<product_id>", methods = ["GET","POST"])
def restoreproduct(product_id):
    retrieved_product = Product.query.get(product_id)
    if retrieved_product:
        retrieved_product.product_isdeleted = 0
        db.session.commit()
    return redirect(url_for('getproductdetailsforadmin'))

# User Cart Section
@app.route("/<int:user_id>/addProductToCart/<int:product_id>", methods=["GET","POST"])
def addproducttoCart(user_id, product_id):
    retrieved_user = User.query.get(user_id)
    if request.method == 'GET':
        product = Product.query.get(product_id)
        return render_template("user_addproduct.html",
                            product = product,
                            user = retrieved_user)
    if request.method == 'POST':
        retrieved_product = Product.query.get(product_id)
        if retrieved_product:
            productquantity = int(request.form['productquantity'])
            if productquantity > retrieved_product.product_quantity:
                error_message = f'Please select a quantity lesser than {retrieved_product.product_quantity}'
                return render_template("user_addproduct.html", 
                                        product = retrieved_product,
                                        user = retrieved_user,
                                        error_message = error_message)
            else:
                retrieved_product.product_quantity = retrieved_product.product_quantity - productquantity
                existingusercartdetails = UserCartDetails.query.filter_by(product_id = product_id, usercartdetails_cartstatus = 1).first()
                if existingusercartdetails:
                    existingusercartdetails.usercartdetails_productquantity = existingusercartdetails.usercartdetails_productquantity + productquantity
                    existingusercartdetails.usercartdetails_totalamount = retrieved_product.product_rateperunit * existingusercartdetails.usercartdetails_productquantity
                else:
                    userCartDetails = UserCartDetails(
                                        user_id = user_id,
                                        product_id = product_id,
                                        usercartdetails_productquantity = productquantity,
                                        usercartdetails_totalamount = retrieved_product.product_rateperunit * productquantity,
                                        usercartdetails_cartstatus = 1)
                    db.session.add(userCartDetails)
                db.session.commit()
    return getproductdetailsforuser(retrieved_user)


@app.route("/<int:user_id>/buyProduct/<product_id>", methods = ["GET", "POST"])
def buyProduct(user_id, product_id):
    retrieved_user = User.query.get(user_id)
    if request.method == 'GET':
        product = Product.query.get(product_id)
        return render_template("user_buyproduct.html",
                               product = product,
                               user = retrieved_user)
    if request.method == 'POST':
        retrieved_product = Product.query.get(product_id)
        if retrieved_product:
            productquantity = int(request.form['productquantity'])
            if productquantity > retrieved_product.product_quantity:
                error_message = f'Please select a quantity lesser than {retrieved_product.product_quantity}'
                return render_template("user_buyproduct.html", 
                                        product = retrieved_product,
                                        user = retrieved_user,
                                        error_message = error_message)
            else:
                retrieved_product.product_quantity = retrieved_product.product_quantity - productquantity
                existingusercartdetails = UserCartDetails.query.filter_by(product_id = product_id, usercartdetails_cartstatus = 1).first()
                if existingusercartdetails:
                    existingusercartdetails.usercartdetails_productquantity = existingusercartdetails.usercartdetails_productquantity + productquantity
                    existingusercartdetails.usercartdetails_totalamount = retrieved_product.product_rateperunit * existingusercartdetails.usercartdetails_productquantity
                else:
                    userCartDetails = UserCartDetails(
                                        user_id = user_id,
                                        product_id = product_id,
                                        usercartdetails_productquantity = productquantity,
                                        usercartdetails_totalamount = retrieved_product.product_rateperunit * productquantity,
                                        usercartdetails_cartstatus = 1)
                    db.session.add(userCartDetails)
                db.session.commit()
    return getUserCartDetails(user_id)

def addProductForUser(user_id, product_id, templatename):
    user = User.query.get(user_id)
    retrieved_product = Product.query.get(product_id)
    if retrieved_product:
        productquantity = int(request.form['productquantity'])
        if productquantity > retrieved_product.product_quantity:
            error_message = f'Please select a quantity lesser than {retrieved_product.product_quantity}'
            return render_template(templatename, 
                                    product = retrieved_product,
                                    user = user,
                                    error_message = error_message)
        else:
            retrieved_product.product_quantity = retrieved_product.product_quantity - productquantity
            existingusercartdetails = UserCartDetails.query.filter_by(product_id = product_id, usercartdetails_cartstatus = 1).first()
            if existingusercartdetails:
                existingusercartdetails.usercartdetails_productquantity = existingusercartdetails.product_quantity + productquantity
                existingusercartdetails.usercartdetails_totalamount = retrieved_product.product_rateperunit * existingusercartdetails.usercartdetails_productquantity
            else:
                userCartDetails = UserCartDetails(
                                    user_id = user_id,
                                    product_id = product_id,
                                    usercartdetails_productquantity = productquantity,
                                    usercartdetails_totalamount = retrieved_product.product_rateperunit * productquantity,
                                    usercartdetails_cartstatus = 1)
                db.session.add(userCartDetails)
                
            db.session.commit()

@app.route("/getUserCartDetails/<user_id>", methods = ["GET", "POST"])
def getUserCartDetails(user_id):
    retrieved_userCartDetails = UserCartDetails.query.filter_by(user_id = user_id, usercartdetails_cartstatus = 1).all()
    user = User.query.get(user_id)
    if retrieved_userCartDetails:
        userproductcartbycategorydict = {}
        sumofproducts = 0
        for usercartdetail in retrieved_userCartDetails:
            productcategoryname = usercartdetail.product.productcategory.productcategory_name
            sumofproducts += usercartdetail.usercartdetails_totalamount
            if productcategoryname not in userproductcartbycategorydict:
                userproductcartbycategorydict[productcategoryname] = []
            userproductcartbycategorydict[productcategoryname].append(usercartdetail)

        return render_template('user_cart_details.html',
                               userProductCartByCategoryDict = userproductcartbycategorydict,
                               user = user,
                               sumofproducts = sumofproducts)
    else:
        message = 'No Items Added to the cart. Please add items to the cart.'
        return render_template('user_cart_details.html',
                               message = message,
                               user = user)

@app.route("/checkoutProducts/<user_id>", methods = ["GET", "POST"])
def checkoutproductsforuser(user_id):
    retrieved_userCartDetails = UserCartDetails.query.filter_by(user_id = user_id, usercartdetails_cartstatus = 1).all()
    if retrieved_userCartDetails:
        for retrieved_userCartDetail in retrieved_userCartDetails:
            retrieved_userCartDetail.usercartdetails_cartstatus = 2
            retrieved_userCartDetail.usercartdetails_checkoutdatetime = datetime.now()
        db.session.commit()
    
    retrieveduser = User.query.get(user_id)
    return getproductdetailsforuser(retrieveduser)

@app.route("/<int:user_id>/search", methods = ["GET", "POST"])
def searchproductsandproductcategories(user_id):
    user = User.query.get(user_id)
    numOfCartItems = 0
    retrieved_userCartDetails = UserCartDetails.query.filter_by(user_id = user_id, usercartdetails_cartstatus = 1).all()
    if retrieved_userCartDetails:
        numOfCartItems = sum(cart_detail.usercartdetails_productquantity for cart_detail in retrieved_userCartDetails)
    searchquery = request.form['searchquery']
    
    if searchquery:
        search_date = None
        try:
            search_date = datetime.strptime(searchquery, '%Y-%m-%d')
        except ValueError:
            search_date = None
        searchquery = "%{}%".format(searchquery)
        searcherrormessage = None
        retrieved_productcategories = ProductCategory.query.filter(ProductCategory.productcategory_name.like(searchquery), ProductCategory.productcategory_isdeleted == 0).all()
        retrievedproductcategorieswithfilteredproducts = {}
        if retrieved_productcategories:
            return render_template("user_productcategories.html",
                            productCategories = retrieved_productcategories,
                            user = user,
                            numOfCartItems = numOfCartItems)
        else:
            if search_date:
                retrieved_products = Product.query.filter(
                                and_(
                                    Product.product_expirydate.isnot(None),
                                    Product.product_expirydate > search_date
                                ), Product.product_isdeleted == 0).all()
            else:
                retrieved_products = Product.query.filter(
                                or_(
                                    Product.product_name.like(searchquery),
                                    Product.product_rateperunit.like(searchquery),
                                ), Product.product_isdeleted == 0).all()
            if retrieved_products is not None and len(retrieved_products) > 0:
                for product in retrieved_products:
                    if product.productcategory.productcategory_name not in retrievedproductcategorieswithfilteredproducts:
                        retrievedproductcategorieswithfilteredproducts[product.productcategory.productcategory_name] = []
                    retrievedproductcategorieswithfilteredproducts[product.productcategory.productcategory_name].append(product)
            else:
                searcherrormessage = "No Product Categories or Products are found by the seach criteria."
            return render_template("user_productcategories.html",
                    productCategories = retrieved_productcategories,
                    user = user,
                    numOfCartItems = numOfCartItems,
                    retrievedproductcategoriesdict = retrievedproductcategorieswithfilteredproducts,
                    searchErrorMessage = searcherrormessage)
    else:
        return getproductdetailsforuser(user) 

# Review user cart details    
@app.route("/<int:user_id>/reviewAndUpdateUserCartDetails/<usercartdetails_id>", methods = ["GET", "POST"])
def reviewAndUpdateUserCartDetails(user_id, usercartdetails_id):
    existingusercartdetails = UserCartDetails.query.get(usercartdetails_id)
    numOfCartItems = 0
    retrieved_userCartDetails = UserCartDetails.query.filter_by(user_id = user_id, usercartdetails_cartstatus = 1).all()
    if retrieved_userCartDetails:
        numOfCartItems = sum(cart_detail.usercartdetails_productquantity for cart_detail in retrieved_userCartDetails)
    if retrieved_userCartDetails:
        numOfCartItems = sum(cart_detail.usercartdetails_productquantity for cart_detail in retrieved_userCartDetails)
    user = User.query.get(user_id)
    return render_template("user_reviewproductincart.html",
                               userCartDetails = existingusercartdetails,
                               numOfCartItems = numOfCartItems,
                               user = user)
# Update user cart details  
@app.route("/<int:user_id>/updateUserCartDetails/<usercartdetails_id>", methods = ["GET", "POST"])
def updateUserCartDetails(user_id, usercartdetails_id):
    existingusercartdetails = UserCartDetails.query.get(usercartdetails_id)
    user = User.query.get(user_id)
    retrieved_product = Product.query.get(existingusercartdetails.product.product_id)
    if retrieved_product:
        productquantityreceived = int(request.form['productquantity'])
        diffquantity = productquantityreceived - existingusercartdetails.usercartdetails_productquantity
        if diffquantity == 0:
            error_message = f'There is no change in the product quantity.'
            return render_template("user_reviewproductincart.html", 
                                        product = retrieved_product,
                                        user = user,
                                        userCartDetails = existingusercartdetails,
                                        error_message = error_message)
        if diffquantity > 0:
            if diffquantity > retrieved_product.product_quantity:
                error_message = f'Please select a quantity lesser than {retrieved_product.product_quantity}'
                return render_template("user_reviewproductincart.html", 
                                            product = retrieved_product,
                                            user = user,
                                            userCartDetails = existingusercartdetails,
                                            error_message = error_message)
            else:
                    retrieved_product.product_quantity = retrieved_product.product_quantity - productquantityreceived
                    existingusercartdetails.usercartdetails_productquantity = existingusercartdetails.usercartdetails_productquantity + diffquantity
                    existingusercartdetails.usercartdetails_totalamount = retrieved_product.product_rateperunit * existingusercartdetails.usercartdetails_productquantity
        else:
            retrieved_product.product_quantity = retrieved_product.product_quantity - diffquantity
            existingusercartdetails.usercartdetails_productquantity = existingusercartdetails.usercartdetails_productquantity + diffquantity
            existingusercartdetails.usercartdetails_totalamount = retrieved_product.product_rateperunit * existingusercartdetails.usercartdetails_productquantity
            db.session.commit()
    return getUserCartDetails(user_id)

# Delete user cart details  
@app.route("/<int:user_id>/deleteUserCartDetails/<usercartdetails_id>", methods = ["GET", "POST"])
def deleteUserCartDetails(user_id, usercartdetails_id):
    existingusercartdetails = UserCartDetails.query.get(usercartdetails_id)
    retrieved_product = Product.query.get(existingusercartdetails.product.product_id)
    if retrieved_product:
        retrieved_product.product_quantity = retrieved_product.product_quantity + existingusercartdetails.usercartdetails_productquantity
        db.session.delete(existingusercartdetails)
        db.session.commit()
    return getUserCartDetails(user_id)
        
@app.route("/summary")
def Summary():
    return render_template("summary.html")

@app.route("/logout")
def Logout():
    return render_template("login.html")

@app.route("/profile/<int:user_id>")
def Prifile(user_id):
    user = User.query.get(user_id)
    return render_template("user_profile.html",
                           user = user)