# E-Mart Project

## Project Description
E-Mart is a multi-user shopping app that offers a comprehensive shopping experience tailored for both admin and general users. With distinct roles, E-Mart ensures a seamless process for all.

### For Admin Users
- Manage product categories and their associated items with ease.
- Add or edit product categories to keep the catalogue current and organized.
- Adjust product details such as quantity, pricing, and expiry dates for precise inventory management.
- Delete a category or product when it becomes obsolete.

### For General Users
- Explore a wide array of products and add them to the cart effortlessly.
- Review and remove items from the cart for a tailored shopping experience.
- Place orders for products added to the cart.

### REST APIs
Developed following the Open API Specifications, the APIs allow access and modification of the app's database.

## Technologies Used
- **Python**: Develop the controllers and serve as the host programming language for the app.
- **HTML**: Develop the required web pages.
- **CSS**: Style the web pages.
- **Bootstrap**: Enhance the frontend's appearance and navigation.
- **SQLite**: Serve as the app's database.
- **Flask**: Serve as the web framework for the app.
  - **Flask-Restful**: Develop RESTful APIs.
  - **Flask-SQLAlchemy**: ORM for accessing and modifying the SQLite database.
  - **Flask-CORS**: Enable CORS for the app.
- **Swagger Open API**: Create documentation for the developed APIs.

## Database Schema
### User Table
- `user_id (Integer)`: Primary Key, Auto Increment
- `username (String)`: Unique, Not Null
- `user_password (String)`: Not Null
- `user_role (String)`: Not Null

### ProductCategory Table
- `productcategory_id (Integer)`: Primary Key, Auto Increment
- `productcategory_name (String)`: Not Null
- `productcategory_isdeleted (Integer)`: Not Null

### Product Table
- `product_id (Integer)`: Primary Key, Auto Increment
- `product_name (String)`: Not Null
- `productcategory_id (Integer)`: Foreign Key (ProductCategory.productcategory_id), Not Null
- `product_unit (String)`: Not Null
- `product_rateperunit (Float)`: Not Null
- `product_quantity (Integer)`: Not Null
- `product_expirydate (DateTime)`: Nullable
- `product_isdeleted (Integer)`: Not Null

### UserCartDetails Table
- `usercartdetails_id (Integer)`: Primary Key, Auto Increment
- `user_id (Integer)`: Foreign Key (User.user_id), Not Null
- `product_id (Integer)`: Foreign Key (Product.product_id), Not Null
- `usercartdetails_productquantity (Integer)`: Not Null
- `usercartdetails_totalamount (Float)`: Not Null
- `usercartdetails_cartstatus (Integer)`: Not Null
- `usercartdetails_checkoutdatetime (DateTime)`: Nullable

## API Design
The RESTful APIs are created using the Flask-Restful library for Python according to the OpenAPI Specifications. All the database tables have CRUD operations available through the API. For more information, refer to the `openapi.yaml` file.

## Architecture and Features
The application follows the standard MVC architecture.
- **View**: Created using HTML, CSS, and Bootstrap.
- **Controller**: Implemented using Python and Flask.
- **Models**: Established using SQLAlchemy.

### Features
- Registration and Login for Admin/General Users.
- **Admin User**:
  - Create/Update/Delete a new ProductCategory.
  - Create/Update/Delete a new Product for a particular Product Category.
  - Restore a deleted ProductCategory and Product.
- **General User**:
  - Search for a ProductCategory by name.
  - Search for Products by name, rate, or expiry date.
  - Add an available product to the cart.
  - View all products in the cart and check the total price.
  - Review and edit the quantity or delete the product from the cart.
  - Place orders for products in the cart.
  - Checkout the products.
  - View the user profile page.
  - Navigate between pages.
- **RESTful API** for User, ProductCategory, Products, and UserCartDetails.

## Test Users for eMart App
- **Admin**:  
  Username: `testadmin`  
  Password: `abc@1234`
- **User**:  
  Username: `testuser`  
  Password: `abc@1234`

## Video Demo
Watch the video demonstration of the eMart app [here](https://youtu.be/ZoaTCv9UVyo).
