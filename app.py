import streamlit as st
import random as rd
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector as db

class FoodDeliveryManagementApp:
    def __init__(self):
        self.db_connection = db.connect(
            host="localhost",
            user="root",
            password="SathishMyilsamy@21601",
            database="zomato_db"
        )
        self.cursor = self.db_connection.cursor()
        self.fake = Faker()
        self.create_tables()

    def create_tables(self):
        tables = {
            "Customers": """
                CREATE TABLE IF NOT EXISTS Customers (
                    customer_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    phone VARCHAR(20) UNIQUE NOT NULL,  
                    location VARCHAR(255) NOT NULL,
                    signup_date DATE NOT NULL,
                    is_premium BOOLEAN DEFAULT FALSE,
                    preferred_cuisine VARCHAR(50) DEFAULT 'Not Specified',
                    total_orders INT DEFAULT 0,
                    average_rating FLOAT DEFAULT 0.0
                );
            """,
            "Restaurants": """
                CREATE TABLE IF NOT EXISTS Restaurants (
                    restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    cuisine_type VARCHAR(50) DEFAULT 'Not Specified',
                    location VARCHAR(255) NOT NULL,
                    owner_name VARCHAR(255),
                    average_delivery_time INT DEFAULT 30,
                    contact_number VARCHAR(20) UNIQUE,
                    rating FLOAT DEFAULT 0.0,
                    total_orders INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """,
            "Orders": """
                CREATE TABLE IF NOT EXISTS Orders (
                    order_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT,
                    restaurant_id INT,
                    delivery_person_id INT,
                    total_amount FLOAT,
                    distance FLOAT,
                    delivery_fee FLOAT,
                    payment_mode VARCHAR(50),
                    customer_feedback_rating INT,
                    FOREIGN KEY (delivery_person_id) REFERENCES DeliveryPersons(delivery_person_id),
                    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
                    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id)
                );
            """,
            "DeliveryPersons": """
                CREATE TABLE IF NOT EXISTS DeliveryPersons (
                    delivery_person_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    contact_number VARCHAR(20) UNIQUE,
                    vehicle_type VARCHAR(50),
                    total_deliveries INT DEFAULT 0,
                    average_rating FLOAT DEFAULT 0.0,
                    location VARCHAR(255) NOT NULL
                );
            """,
            "Deliveries": """
                CREATE TABLE IF NOT EXISTS Deliveries (
                    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    delivery_person_id INT,
                    delivery_status VARCHAR(50) DEFAULT 'Pending',
                    distance FLOAT NOT NULL,
                    delivery_time INT DEFAULT 0,
                    estimated_time INT,
                    delivery_fee FLOAT NOT NULL,
                    vehicle_type VARCHAR(50),
                    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
                    FOREIGN KEY (delivery_person_id) REFERENCES DeliveryPersons(delivery_person_id) ON DELETE SET NULL
                );
"""
        }
        
        for table_name, table_creation_query in tables.items():
            self.cursor.execute(table_creation_query)

        self.db_connection.commit()
        
    def manage_customers(self):
        st.header("Manage Customers")

        with st.form("add_customer"):
            st.subheader("Create New Customer")
            customer_data = {
                "name": st.text_input("Customer Name"),
                "email": st.text_input("Email"),
                "phone": st.text_input("Phone Number", value=""),  
                "location": st.text_area("Location", value=""),  
                "signup_date": st.date_input("Signup Date", datetime.today().date()),  
                "is_premium": st.checkbox("Is Premium Member", value=False),
                "preferred_cuisine": st.selectbox("Preferred Cuisine", ["Indian", "Chinese", "Italian", "Mexican"]),
                "total_orders": st.number_input("Total Orders", min_value=0, value=0),  
                "average_rating": st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.1, value=0.0)
            }

            if st.form_submit_button("Create Customer"):
                if not customer_data["email"] or not customer_data["phone"]:
                    st.warning("Email and Phone cannot be empty!")
                else:
                    phone = customer_data["phone"] if customer_data["phone"] else ""
                    location = customer_data["location"] if customer_data["location"] else ""
                    email = customer_data["email"] if customer_data["email"] else ""

                    self.cursor.execute("""
                        INSERT INTO Customers (name, email, phone, location, signup_date, is_premium, preferred_cuisine, total_orders, average_rating)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        customer_data["name"], email, phone, location,
                        customer_data["signup_date"], customer_data["is_premium"],
                        customer_data["preferred_cuisine"], customer_data["total_orders"], customer_data["average_rating"]
                    ))
                    self.db_connection.commit()
                    st.success("Customer created successfully!")

        st.subheader("All Customers")
        self.cursor.execute("SELECT * FROM Customers")
        customers = self.cursor.fetchall()

        for customer in customers:
            st.write(f"ID: {customer[0]}, Name: {customer[1]}, Email: {customer[2]}")
            st.write(f"Location: {customer[4]}, Preferred Cuisine: {customer[7]}, Total Orders: {customer[8]}, Average Rating: {customer[9]}")

            with st.expander(f"Actions for Customer ID {customer[0]}"):
                with st.form(f"update_customer_{customer[0]}"):
                    updated_name = st.text_input("Update Name", customer[1])
                    updated_email = st.text_input("Update Email", customer[2])
                    updated_phone = st.text_input("Update Phone", customer[3])
                    updated_location = st.text_area("Update Location", customer[4])

                    try:
                        updated_signup_date = datetime.strptime(customer[5], '%Y-%m-%d').date()
                    except Exception as e:
                        updated_signup_date = datetime.today().date()  

                    updated_signup_date = st.date_input("Update Signup Date", updated_signup_date)

                    updated_is_premium = st.checkbox("Is Premium Member", value=customer[6] if len(customer) > 6 else False)
                    updated_preferred_cuisine = st.selectbox("Update Preferred Cuisine", 
                                                            ["Indian", "Chinese", "Italian", "Mexican"], 
                                                            index=["Indian", "Chinese", "Italian", "Mexican"].index(customer[7]) if customer[7] in ["Indian", "Chinese", "Italian", "Mexican"] else 0)

                    updated_total_orders = st.number_input(
                        "Update Total Orders", 
                        min_value=0, 
                        value=int(customer[8]) if isinstance(customer[8], (int, float)) else 0  # Ensure numeric value
                    )

                    updated_average_rating = st.number_input(
                        "Update Average Rating", 
                        min_value=0.0, 
                        max_value=5.0, 
                        step=0.1, 
                        value=float(customer[9]) if isinstance(customer[9], (int, float)) else 0.0  # Ensure float value
                    )

                    if st.form_submit_button("Update Customer"):
                        if not updated_email or not updated_phone:
                            st.warning("Email and Phone cannot be empty!")
                        else:
                            updated_phone = updated_phone if updated_phone else ""
                            updated_email = updated_email if updated_email else ""
                            updated_location = updated_location if updated_location else ""

                            self.cursor.execute("""
                                UPDATE Customers
                                SET name = %s, email = %s, phone = %s, location = %s, signup_date = %s,
                                    is_premium = %s, preferred_cuisine = %s, total_orders = %s, average_rating = %s
                                WHERE customer_id = %s
                            """, (
                                updated_name, updated_email, updated_phone, updated_location, updated_signup_date,
                                updated_is_premium, updated_preferred_cuisine, updated_total_orders, updated_average_rating, customer[0]
                            ))
                            self.db_connection.commit()
                            st.success("Customer updated successfully!")

                if st.button("Delete Customer", key=f"delete_{customer[0]}"):
                    self.cursor.execute("DELETE FROM Customers WHERE customer_id=%s", (customer[0],))
                    self.db_connection.commit()
                    st.warning("Customer deleted successfully!")



    def manage_restaurants(self): 
        st.header("Manage Restaurants")

        with st.form("add_restaurant"):
            st.subheader("Create New Restaurant")
            restaurant_data = {
                "name": st.text_input("Restaurant Name"),
                "cuisine_type": st.text_input("Cuisine Type"),
                "location": st.text_area("Location"),
                "owner_name": st.text_input("Owner Name"),
                "average_delivery_time": st.number_input("Average Delivery Time (minutes)", min_value=0, step=1),
                "contact_number": st.text_input("Contact Number"),
                "rating": st.slider("Rating", 1, 5),
                "total_orders": st.number_input("Total Orders", min_value=0, step=1),
                "is_active": st.checkbox("Is Active?", value=False)
            }
            if st.form_submit_button("Create Restaurant"):
                self.cursor.execute("""
                    INSERT INTO Restaurants (name, cuisine_type, location, owner_name, average_delivery_time, contact_number, rating, total_orders, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(restaurant_data.values()))
                self.db_connection.commit()
                st.success("Restaurant created successfully!")

        st.subheader("All Restaurants")
        self.cursor.execute("SELECT * FROM Restaurants")
        restaurants = self.cursor.fetchall()

        for restaurant in restaurants:
            st.write(f"ID: {restaurant[0]}, Name: {restaurant[1]}, Rating: {restaurant[7]}")
            with st.expander(f"Actions for Restaurant ID {restaurant[0]}"):
                with st.form(f"update_restaurant_{restaurant[0]}"):
                    updated_name = st.text_input("Update Name", restaurant[1])
                    updated_cuisine_type = st.text_input("Update Cuisine Type", restaurant[2])
                    updated_location = st.text_area("Update Location", restaurant[3])
                    updated_owner_name = st.text_input("Update Owner Name", restaurant[4])
                    
                    try:
                        updated_average_delivery_time = st.number_input("Update Average Delivery Time", value=int(restaurant[5]), min_value=0, step=1)
                    except ValueError:
                        updated_average_delivery_time = st.number_input("Update Average Delivery Time", value=0, min_value=0, step=1)

                    updated_contact_number = st.text_input("Update Contact Number", restaurant[6])
                    
                    try:
                        rating_value = float(restaurant[7]) if restaurant[7] is not None else 3.0  
                        updated_rating = st.slider("Update Rating", 1, 5, int(rating_value))
                    except ValueError:
                        st.error("Invalid rating value.")
                        updated_rating = 3  

                    updated_total_orders = st.number_input("Update Total Orders", value=restaurant[8], min_value=0, step=1)
                    updated_is_active = st.checkbox("Is Active?", value=restaurant[9])

                    if st.form_submit_button("Update Restaurant"):
                        self.cursor.execute("""
                            UPDATE Restaurants 
                            SET name = %s, cuisine_type = %s, location = %s, owner_name = %s, average_delivery_time = %s, 
                                contact_number = %s, rating = %s, total_orders = %s, is_active = %s 
                            WHERE restaurant_id = %s
                        """, (updated_name, updated_cuisine_type, updated_location, updated_owner_name, updated_average_delivery_time, 
                            updated_contact_number, updated_rating, updated_total_orders, updated_is_active, restaurant[0]))
                        self.db_connection.commit()
                        st.success("Restaurant updated successfully!")

                if st.button("Delete Restaurant", key=f"delete_{restaurant[0]}"):
                    self.cursor.execute("DELETE FROM Restaurants WHERE restaurant_id=%s", (restaurant[0],))
                    self.db_connection.commit()
                    st.warning("Restaurant deleted successfully!")

    def manage_orders(self):
        st.header("Manage Orders")
        
        with st.form("add_order"):
            st.subheader("Create New Order")
            data = {
                "customer_id": st.number_input("Customer ID", min_value=1),
                "restaurant_id": st.number_input("Restaurant ID", min_value=1),
                "order_date": st.date_input("Order Date", datetime.today()),
                "delivery_time": st.time_input("Delivery Time", datetime.now()),
                "status": st.selectbox("Status", ["Pending", "Delivered", "Cancelled"]),
                "total_amount": st.number_input("Total Amount", min_value=0.0, format="%.2f"),
                "payment_mode": st.selectbox("Payment Mode", ["Credit Card", "Cash", "UPI"]),
                "discount_applied": st.number_input("Discount", min_value=0.0, format="%.2f"),
                "feedback_rating": st.slider("Rating", 1, 5)
            }
            if st.form_submit_button("Create Order"):
                self.cursor.execute(""" 
                    INSERT INTO Orders (customer_id, restaurant_id, order_date, delivery_time, 
                                        status, total_amount, payment_mode, discount_applied, feedback_rating) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(data.values()))
                self.db_connection.commit()
                st.success("Order created successfully!")

        st.subheader("All Orders")
        self.cursor.execute("SELECT * FROM Orders")
        orders = self.cursor.fetchall()

        for order in orders:
            st.write(f"ID: {order[0]}, Status: {order[5]}, Total: {order[7]}")
            with st.expander(f"Actions for Order ID {order[0]}"):
                with st.form(f"update_order_{order[0]}"):
                    updated_status = st.selectbox("Update Status", ["Pending", "Delivered", "Cancelled"], index=["Pending", "Delivered", "Cancelled"].index(order[5]))

                    try:
                        total_amount_value = float(order[7])
                    except ValueError:
                        total_amount_value = 0.0  

                    updated_total = st.number_input("Update Total Amount", min_value=0.0, value=total_amount_value, format="%.2f")

                    if st.form_submit_button("Update Order"):
                        self.cursor.execute(""" 
                            UPDATE Orders 
                            SET status = %s, total_amount = %s 
                            WHERE order_id = %s
                        """, (updated_status, updated_total, order[0]))
                        self.db_connection.commit()
                        st.success("Order updated successfully!")

                if st.button("Delete Order", key=f"delete_{order[0]}"):
                    self.cursor.execute("DELETE FROM Orders WHERE order_id=%s", (order[0],))
                    self.db_connection.commit()
                    st.warning("Order deleted successfully!")


    def manage_deliveries(self): 
        st.header("Manage Deliveries")

        with st.form("add_delivery"):
            st.subheader("Add New Delivery")
            order_id = st.number_input("Order ID", min_value=1, step=1)
            delivery_person_id = st.number_input("Delivery Person ID", min_value=1, step=1)
            delivery_status = st.selectbox("Delivery Status", ["On the way", "Delivered", "Pending", "Cancelled"])
            distance = st.number_input("Distance (in km)", min_value=0.0, step=0.1)
            delivery_time = st.number_input("Delivery Time (in minutes)", min_value=0.0, step=0.1)
            estimated_time = st.number_input("Estimated Time (in minutes)", value=0.0, min_value=0.0, step=0.1)
            delivery_fee = st.number_input("Delivery Fee (in $)", min_value=0.0, step=0.1)
            vehicle_type = st.selectbox("Vehicle Type", ["Bike", "Car", "Van", "Bicycle", "Scooter", "Other"])

            if st.form_submit_button("Add Delivery"):
                self.cursor.execute("""
                    INSERT INTO Deliveries (order_id, delivery_person_id, delivery_status, distance, delivery_time, 
                                            estimated_time, delivery_fee, vehicle_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (order_id, delivery_person_id, delivery_status, distance, delivery_time, estimated_time, delivery_fee, vehicle_type))
                self.db_connection.commit()
                st.success("Delivery added successfully!")

        st.subheader("All Deliveries")
        self.cursor.execute("SELECT * FROM Deliveries")
        deliveries = self.cursor.fetchall()
        for delivery in deliveries:
            with st.expander(f"Delivery ID: {delivery[0]} (Order ID: {delivery[1]}, Delivery Person ID: {delivery[2]})"):
                st.write(f"Status: {delivery[3]}")
                st.write(f"Distance: {delivery[4]} km")

                if isinstance(delivery[5], timedelta):
                    delivery_time_minutes = delivery[5].total_seconds() / 60 
                else:
                    delivery_time_minutes = delivery[5] 

                st.write(f"Delivery Time: {delivery_time_minutes} mins")
                st.write(f"Estimated Time: {delivery[6]} mins")
                st.write(f"Fee: ${delivery[7]}")
                st.write(f"Vehicle Type: {delivery[8]}")

                with st.form(f"update_delivery_{delivery[0]}"):
                    delivery_status = st.selectbox("Delivery Status", ["On the way", "Delivered", "Pending", "Cancelled"], 
                                                    index=["On the way", "Delivered", "Pending", "Cancelled"].index(delivery[3]), 
                                                    key=f"status_{delivery[0]}")
                    distance = st.number_input("Distance (in km)", value=delivery[4], min_value=0.0, step=0.1, key=f"distance_{delivery[0]}")

                    if isinstance(delivery[5], timedelta):
                        delivery_time_minutes = delivery[5].total_seconds() / 60
                    else:
                        delivery_time_minutes = delivery[5]

                    delivery_time = st.number_input("Delivery Time (in minutes)", value=delivery_time_minutes, min_value=0.0, step=0.1, key=f"time_{delivery[0]}")  # Ensure step is float
                    
                    estimated_time = st.number_input("Estimated Time (in minutes)", value=float(delivery[6]), min_value=0.0, step=0.1, key=f"est_time_{delivery[0]}")  # Ensure step is float
                    
                    delivery_fee = st.number_input("Delivery Fee (in $)", value=delivery[7], min_value=0.0, step=0.1, key=f"fee_{delivery[0]}")

                    vehicle_types = ["Bike", "Car", "Van", "Bicycle", "Scooter", "Other"]
                    vehicle_type_index = vehicle_types.index(delivery[8]) if delivery[8] in vehicle_types else vehicle_types.index("Other")

                    vehicle_type = st.selectbox("Vehicle Type", vehicle_types, index=vehicle_type_index, key=f"vehicle_{delivery[0]}")

                    if st.form_submit_button("Update Delivery"):
                        self.cursor.execute("""
                            UPDATE Deliveries SET delivery_status=%s, distance=%s, delivery_time=%s, 
                                                estimated_time=%s, delivery_fee=%s, vehicle_type=%s 
                            WHERE delivery_id=%s
                        """, (delivery_status, distance, delivery_time, estimated_time, delivery_fee, vehicle_type, delivery[0]))
                        self.db_connection.commit()
                        st.success("Delivery updated successfully!")

                if st.button("Delete Delivery", key=f"delete_{delivery[0]}"):
                    self.cursor.execute("DELETE FROM Deliveries WHERE delivery_id=%s", (delivery[0],))
                    self.db_connection.commit()
                    st.warning("Delivery deleted successfully!")
                    
    def manage_delivery_persons(self):
        st.header("Manage Delivery Personnel")

        with st.form("add_delivery_person"):
            st.subheader("Add New Delivery Person")
            delivery_data = {
                "name": st.text_input("Delivery Person Name"),
                "contact_number": st.text_input("Contact Number"),
                "vehicle_type": st.selectbox("Vehicle Type", ["Bike", "Car", "Bicycle", "Other"]),
                "total_deliveries": st.number_input("Total Deliveries", min_value=0, value=0),
                "average_rating": st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.1, value=0.0),
                "location": st.text_input("Base Location")
            }
            if st.form_submit_button("Add Delivery Person"):
                self.cursor.execute("""
                    INSERT INTO DeliveryPersons (name, contact_number, vehicle_type, total_deliveries, average_rating, location)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, tuple(delivery_data.values()))
                self.db_connection.commit()
                st.success("Delivery person added successfully!")

        st.subheader("All Delivery Personnel")
        self.cursor.execute("SELECT * FROM DeliveryPersons")
        delivery_persons = self.cursor.fetchall()

        for person in delivery_persons:
            st.write(f"ID: {person[0]}, Name: {person[1]}, Contact: {person[2]}")
            with st.expander(f"Actions for Delivery Person ID {person[0]}"):
                with st.form(f"update_delivery_person_{person[0]}"):
                    updated_name = st.text_input("Update Name", person[1])
                    updated_contact = st.text_input("Update Contact", person[2])
                    updated_vehicle = st.selectbox("Update Vehicle Type", ["Bike", "Car", "Bicycle", "Other"], index=["Bike", "Car", "Bicycle", "Other"].index(person[3]))
                    updated_total_deliveries = st.number_input("Update Total Deliveries", min_value=0, value=person[4])
                    updated_average_rating = st.number_input("Update Average Rating", min_value=0.0, max_value=5.0, step=0.1, value=person[5])
                    updated_location = st.text_input("Update Location", person[6])

                    if st.form_submit_button("Update Delivery Person"):
                        self.cursor.execute("""
                            UPDATE DeliveryPersons
                            SET name = %s, contact_number = %s, vehicle_type = %s,
                                total_deliveries = %s, average_rating = %s, location = %s
                            WHERE delivery_person_id = %s
                        """, (
                            updated_name, updated_contact, updated_vehicle, updated_total_deliveries, updated_average_rating, updated_location, person[0]
                        ))
                        self.db_connection.commit()
                        st.success("Delivery person updated successfully!")

                if st.button("Delete Delivery Person", key=f"delete_{person[0]}"):
                    self.cursor.execute("DELETE FROM DeliveryPersons WHERE delivery_person_id=%s", (person[0],))
                    self.db_connection.commit()
                    st.warning("Delivery person deleted successfully!")

    def show_insights(self):
        st.header("Insights")
        
        self.cursor.execute("SELECT COUNT(*) FROM Customers")
        total_customers = self.cursor.fetchone()[0]
        st.metric("Total Customers", total_customers)
        
        self.cursor.execute("SELECT COUNT(*) FROM Restaurants")
        total_restaurants = self.cursor.fetchone()[0]
        st.metric("Total Restaurants", total_restaurants)
        
        self.cursor.execute("SELECT COUNT(*) FROM Orders")
        total_orders = self.cursor.fetchone()[0]
        st.metric("Total Orders", total_orders)
        
        st.subheader("Top Restaurants by Rating")
        query = "SELECT name, rating FROM Restaurants ORDER BY rating DESC LIMIT 5"
        self.cursor.execute(query)
        top_restaurants = self.cursor.fetchall()
        for name, rating in top_restaurants:
            st.write(f"{name} - {rating}/5")

    def execute_query(self):
        st.header("Data Exploration")

        sql_query = st.text_area("Enter SQL Query", "SELECT * FROM Customers;")
        if st.button("Execute Query"):
            try:
                self.cursor.execute(sql_query)
                result = self.cursor.fetchall()
                st.write(result)
            except Exception as e:
                st.error(f"Error executing query: {e}")
                
    def generate_fake_data(self):
        try:
            self.cursor.execute("SELECT delivery_person_id FROM deliverypersons")
            delivery_person_ids = [row[0] for row in self.cursor.fetchall()]

            if not delivery_person_ids:
                st.error("No delivery persons available in the database. Please add delivery persons first.")
                return

            for _ in range(20):
                customer_name = self.fake.name()
                customer_email = self.fake.email()
                customer_phone = self.fake.phone_number()[:15]
                customer_location = self.fake.address()
                signup_date = self.fake.date_this_decade()
                is_premium = rd.choice([True, False])
                preferred_cuisine = rd.choice(["Indian", "Chinese", "Italian", "Mexican"])
                total_orders = rd.randint(1, 50)
                average_rating = round(rd.uniform(1, 5), 2)

                self.cursor.execute("""
                    INSERT INTO Customers (name, email, phone, location, signup_date, is_premium, preferred_cuisine, total_orders, average_rating)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (customer_name, customer_email, customer_phone, customer_location, signup_date, is_premium, preferred_cuisine, total_orders, average_rating))
                customer_id = self.cursor.lastrowid

                restaurant_name = self.fake.company()
                cuisine_type = rd.choice(["Indian", "Chinese", "Italian", "Mexican"])
                restaurant_location = self.fake.city()
                owner_name = self.fake.name()
                contact_number = self.fake.phone_number()[:15]
                average_delivery_time = rd.randint(15, 60)
                restaurant_rating = round(rd.uniform(1, 5), 2)
                total_orders = rd.randint(50, 200)
                is_active = rd.choice([True, False])

                self.cursor.execute("""
                    INSERT INTO Restaurants (name, cuisine_type, location, owner_name, contact_number, average_delivery_time, rating, total_orders, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (restaurant_name, cuisine_type, restaurant_location, owner_name, contact_number,
                    average_delivery_time, restaurant_rating, total_orders, is_active))
                restaurant_id = self.cursor.lastrowid

                for _ in range(rd.randint(1, 10)):
                    order_date = self.fake.date_between(start_date="-1y", end_date="today")
                    delivery_time = self.fake.time()
                    order_status = rd.choice(["Pending", "Delivered", "Cancelled"])
                    total_amount = round(rd.uniform(100, 500), 2)
                    payment_mode = rd.choice(["Credit Card", "Cash", "UPI"])
                    discount_applied = round(rd.uniform(0, 50), 2)
                    feedback_rating = rd.randint(1, 5)

                    self.cursor.execute("""
                        INSERT INTO Orders (customer_id, restaurant_id, order_date, delivery_time, status, total_amount, payment_mode, discount_applied, feedback_rating)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (customer_id, restaurant_id, order_date, delivery_time, order_status, total_amount, payment_mode,
                        discount_applied, feedback_rating))
                    order_id = self.cursor.lastrowid

                    delivery_person_id = rd.choice(delivery_person_ids)
                    distance = round(rd.uniform(1, 10), 2)
                    estimated_time = rd.randint(30, 90)
                    delivery_fee = round(rd.uniform(20, 50), 2)
                    vehicle_type = rd.choice(["Car", "Bike", "Scooter"])

                    self.cursor.execute("""
                        INSERT INTO Deliveries (order_id, delivery_person_id, delivery_status, distance, delivery_time, 
                                                estimated_time, delivery_fee, vehicle_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (order_id, delivery_person_id, order_status, distance, delivery_time, estimated_time,
                        delivery_fee, vehicle_type))

            self.db_connection.commit()
            st.success("Fake data generated successfully!")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            self.db_connection.rollback() 


app = FoodDeliveryManagementApp()

def main():
    st.title("Food Delivery Management System")

    menu = ["Manage Customers", "Manage Restaurants", "Manage Orders", "Manage Deliveries", "Manage Delivery Person", "Insights", "Data Exploration", "Generate Fake Data"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Manage Customers":
        app.manage_customers()
    elif choice == "Manage Restaurants":
        app.manage_restaurants()
    elif choice == "Manage Orders":
        app.manage_orders()
    elif choice == "Manage Deliveries":
        app.manage_deliveries()
    elif choice == "Manage Delivery Person":
        app.manage_delivery_persons()
    elif choice == "Insights":
        app.show_insights()
    elif choice == "Data Exploration":
        app.execute_query()
    elif choice == "Generate Fake Data":
        if st.button("Generate Data"):
            app.generate_fake_data()

if __name__ == "__main__":
    main()
