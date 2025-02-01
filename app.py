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
                    location VARCHAR(255) NOT NULL,
                    availability_status VARCHAR(50) DEFAULT 'Available'
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
                    delivery_date DATE, 
                    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
                    FOREIGN KEY (delivery_person_id) REFERENCES DeliveryPersons(delivery_person_id) ON DELETE SET NULL
                );
            
"""
        }
        
        for table_name, table_creation_query in tables.items():
            self.cursor.execute(table_creation_query)

        self.db_connection.commit()
        
    def show_homepage(self):
        
        st.write("Welcome to Food Delivery Management System!")
        st.image("D:\ZOMATO-DATA_INSIGHTS\env\Scripts\ezgif-6edec03c6ba51.gif")

        
    def manage_customers(self):
        st.header("Manage Customers")

        with st.form("add_customer"):
            st.subheader("Create New Customer")
            customer_data = {
                "customer_id": st.number_input("Customer ID", min_value=1),
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
                    st.error("Please fill all the required fields!")
                else:
                    phone = customer_data["phone"] if customer_data["phone"] else "N/A"
                    location = customer_data["location"] if customer_data["location"] else "N/A"
                    email = customer_data["email"] if customer_data["email"] else "N/A"

                    self.cursor.execute("""
                        INSERT INTO Customers (customer_id, name, email, phone, location, 
                        signup_date, is_premium, preferred_cuisine, total_orders, average_rating)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        customer_data["customer_id"], customer_data["name"], email, phone, location,
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
                                                            index=["Indian", "Chinese", "Italian", "Mexican"].index(customer[7]) 
                                                            if customer[7] in ["Indian", "Chinese", "Italian", "Mexican"] else 0)
                    updated_total_orders = st.number_input(
                        "Update Total Orders", 
                        min_value=0, 
                        value=int(customer[8]) if isinstance(customer[8], (int, float)) else 0 
                    )

                    updated_average_rating = st.number_input(
                        "Update Average Rating", 
                        min_value=0.0, 
                        max_value=5.0, 
                        step=0.1, 
                        value=float(customer[9]) if isinstance(customer[9], (int, float)) else 0.0  
                    )

                    if st.form_submit_button("Update Customer"):
                        if not updated_email or not updated_phone:
                            st.warning("Please fill all the required fields!")
                        else:
                            updated_phone = updated_phone if updated_phone else "N/A"
                            updated_email = updated_email if updated_email else "N/A"
                            updated_location = updated_location if updated_location else "N/A"

                            self.cursor.execute("""
                                UPDATE Customers
                                SET name = %s, email = %s, phone = %s, location = %s, signup_date = %s,
                                    is_premium = %s, preferred_cuisine = %s, total_orders = %s, average_rating = %s
                                WHERE customer_id = %s
                            """, (
                                updated_name, updated_email, updated_phone, updated_location, updated_signup_date,
                                updated_is_premium, updated_preferred_cuisine, updated_total_orders, 
                                updated_average_rating, customer[0]
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
                "restaurant_id": st.number_input("Restaurant ID", min_value=1),
                "name": st.text_input("Restaurant Name"),
                "cuisine_type": st.selectbox("Cuisine Type", ["Indian", "Chinese", "Italian", "Mexican"]),
                "location": st.text_area("Location"),
                "owner_name": st.text_input("Owner Name"),
                "average_delivery_time": st.number_input("Average Delivery Time (minutes)", min_value=0, step=1),
                "contact_number": st.text_input("Contact Number"),
                "rating": st.slider("Rating", 1, 5),
                "total_orders": st.number_input("Total Orders", min_value=0, step=1),
                "is_active": st.checkbox("Is Active?", value=False)
            }
            if st.form_submit_button("Create Restaurant"):
                if not restaurant_data["name"] or not restaurant_data["contact_number"]:
                    st.error("Please fill all the required fields!")
                else:
                    name = restaurant_data["name"] if restaurant_data["name"] else ""
                    contact_number = restaurant_data["contact_number"] if restaurant_data["contact_number"] else ""
                    self.cursor.execute("""
                        INSERT INTO Restaurants (restaurant_id, name, cuisine_type, location, owner_name, 
                        average_delivery_time, contact_number, rating, total_orders, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,(
                        restaurant_data["restaurant_id"], name, restaurant_data["cuisine_type"], restaurant_data["location"],
                        restaurant_data["owner_name"], restaurant_data["average_delivery_time"], contact_number,
                        restaurant_data["rating"], restaurant_data["total_orders"], restaurant_data["is_active"]
                        ), tuple(restaurant_data.values()))
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
                        updated_average_delivery_time = st.number_input("Update Average Delivery Time", 
                                                                        value=int(restaurant[5]), min_value=0, step=1)
                    except ValueError:
                        updated_average_delivery_time = st.number_input("Update Average Delivery Time", 
                                                                        value=0, min_value=0, step=1)

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
                        if not updated_name or not updated_contact_number:
                            st.error("Please fill all the required fields!")
                        else:
                            updated_name = updated_name if updated_name else ""
                            updated_contact_number = updated_contact_number if updated_contact_number else ""
                            
                            self.cursor.execute("""
                                UPDATE Restaurants 
                                SET name = %s, cuisine_type = %s, location = %s, owner_name = %s, average_delivery_time = %s, 
                                    contact_number = %s, rating = %s, total_orders = %s, is_active = %s 
                                WHERE restaurant_id = %s
                            """, (updated_name, updated_cuisine_type, updated_location, updated_owner_name, 
                                    updated_average_delivery_time, updated_contact_number, updated_rating, 
                                    updated_total_orders, updated_is_active, restaurant[0]))
                            self.db_connection.commit()
                            st.success("Restaurant updated successfully!")

                if st.button("Delete Restaurant", key=f"delete_{restaurant[0]}"):
                    self.cursor.execute("DELETE FROM Restaurants WHERE restaurant_id=%s", (restaurant[0],))
                    self.db_connection.commit()
                    st.warning("Restaurant deleted successfully!")
                    
    def manage_orders(self): 
        st.header("Manage Orders")
        
        # Add new order form
        with st.form("add_order"):
            st.subheader("Create New Order")
            data = {
                "order_id": st.number_input("Order ID", min_value=1),
                "customer_id": st.number_input("Customer ID", min_value=1),
                "restaurant_id": st.number_input("Restaurant ID", min_value=1),
                "order_date": st.date_input("Order Date", datetime.today()),
                "delivery_time": st.time_input("Delivery Time", datetime.now()),
                "status": st.selectbox("Status", ["Pending", "Delivered", "Cancelled"]),
                "total_amount": st.number_input("Total Amount", min_value=0.0, format="%.2f"),
                "payment_mode": st.selectbox("Payment Mode", ["Credit Card", "Cash", "UPI"]),
                "discount_applied": st.number_input("Discount", min_value=0.0, format="%.2f"),
                "customer_feedback_rating": st.slider("Rating", 1, 5)
            }
            if st.form_submit_button("Create Order"):
                try:
                    self.cursor.execute(""" 
                        INSERT INTO Orders (order_id, customer_id, restaurant_id, order_date, delivery_time, 
                                            status, total_amount, payment_mode, discount_applied, customer_feedback_rating) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(data.values()))
                    self.db_connection.commit()
                    st.success("Order created successfully!")
                except Exception as e:
                    st.error(f"Error creating order: {str(e)}")

        # Fetch and display all orders
        st.subheader("All Orders")
        try:
            self.cursor.execute("SELECT * FROM Orders")
            orders = self.cursor.fetchall()

            for order in orders:
                st.write(f"ID: {order[0]}, Status: {order[5]}, Payment Mode: {order[7]}, Total: {order[6]}")
                with st.expander(f"Actions for Order ID {order[0]}"):
                    with st.form(f"update_order_{order[0]}"):
                        updated_status = st.selectbox("Update Status", ["Pending", "Delivered", "Cancelled"], 
                                                    index=["Pending", "Delivered", "Cancelled"].index(order[5]))
                        updated_total = st.number_input("Update Total Amount", min_value=0.0, value=float(order[6]), 
                                                            format="%.2f")
                        if st.form_submit_button("Update Order"):
                            try:
                                self.cursor.execute(""" 
                                    UPDATE Orders 
                                    SET status = %s, total_amount = %s 
                                    WHERE order_id = %s
                                """, (updated_status, updated_total, order[0]))
                                self.db_connection.commit()
                                st.success("Order updated successfully!")
                            except Exception as e:
                                st.error(f"Error updating order: {str(e)}")

                    if st.button("Delete Order", key=f"delete_{order[0]}"):
                        try:
                            self.cursor.execute("DELETE FROM Orders WHERE order_id=%s", (order[0],))
                            self.db_connection.commit()
                            st.warning("Order deleted successfully!")
                        except Exception as e:
                            st.error(f"Error deleting order: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching orders: {str(e)}")


    def manage_delivery_persons(self):
        st.header("Manage Delivery Personnel")

        with st.form("add_delivery_person"):
            st.subheader("Add New Delivery Person")
            delivery_person_data = {
                "delivery_person_id": st.number_input("Delivery Person ID", min_value=1),
                "name": st.text_input("Delivery Person Name"),
                "contact_number": st.text_input("Contact Number"),
                "vehicle_type": st.selectbox("Vehicle Type", ["Bike", "Car", "Bicycle", "Scooter", "Other"]),
                "total_deliveries": st.number_input("Total Deliveries", min_value=0, value=0),
                "average_rating": st.number_input("Average Rating", min_value=0.0, max_value=5.0, step=0.1, value=0.0),
                "location": st.text_input("Base Location")
            }
            if st.form_submit_button("Add Delivery Person"):
                self.cursor.execute("""
                    INSERT INTO DeliveryPersons (delivery_person_id, name, contact_number, 
                    vehicle_type, total_deliveries, average_rating, location)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, tuple(delivery_person_data.values()))
                self.db_connection.commit()
                st.success("Delivery Person Added Successfully!")

        st.subheader("All Delivery Personnel")
        self.cursor.execute("SELECT * FROM DeliveryPersons")
        delivery_persons = self.cursor.fetchall()

        for person in delivery_persons:
            st.write(f"ID: {person[0]}, Name: {person[1]}, Contact: {person[2]}")
            with st.expander(f"Actions for Delivery Person ID {person[0]}"):
                with st.form(f"update_delivery_person_{person[0]}"):
                    updated_name = st.text_input("Update Name", person[1])
                    updated_contact = st.text_input("Update Contact", person[2])
                    updated_vehicle = st.selectbox("Update Vehicle Type", ["Bike", "Car", "Bicycle", "Scooter", "Other"], 
                                                    index=["Bike", "Car", "Bicycle", "Scooter", "Other"].index(person[3]))
                    updated_total_deliveries = st.number_input("Update Total Deliveries", min_value=0, value=person[4])
                    updated_average_rating = st.number_input("Update Average Rating", 
                                                                min_value=0.0, max_value=5.0, step=0.1, value=person[5])
                    updated_location = st.text_input("Update Location", person[6])

                    if st.form_submit_button("Update Delivery Person"):
                        self.cursor.execute("""
                            UPDATE DeliveryPersons
                            SET name = %s, contact_number = %s, vehicle_type = %s,
                                total_deliveries = %s, average_rating = %s, location = %s
                            WHERE delivery_person_id = %s
                        """, (
                            updated_name, updated_contact, updated_vehicle, updated_total_deliveries, 
                            updated_average_rating, updated_location, person[0]
                        ))
                        self.db_connection.commit()
                        st.success("Delivery person updated successfully!")

                if st.button("Delete Delivery Person", key=f"delete_{person[0]}"):
                    self.cursor.execute("DELETE FROM DeliveryPersons WHERE delivery_person_id=%s", (person[0],))
                    self.db_connection.commit()
                    st.warning("Delivery person deleted successfully!")

            
    def manage_deliveries(self): 
        st.header("Manage Deliveries")

        with st.form("add_delivery"):
            st.subheader("Add New Delivery")
            delivery_data = {
                "order_id": st.number_input("Order ID", min_value=1, step=1),
                "delivery_person_id": st.number_input("Delivery Person ID", min_value=1, step=1),
                "delivery_status": st.selectbox("Delivery Status", ["On the way", "Delivered", "Pending", "Cancelled"]),
                "distance": st.number_input("Distance (in km)", min_value=0.0, step=0.1),
                "delivery_time": st.number_input("Delivery Time (in minutes)", min_value=0.0, step=0.1),
                "estimated_time": st.number_input("Estimated Time (in minutes)", value=0.0, min_value=0.0, step=0.1),
                "delivery_fee": st.number_input("Delivery Fee (in ₹)", min_value=0.0, step=0.1),
                "vehicle_type": st.selectbox("Vehicle Type", ["Bike", "Car", "Van", "Bicycle", "Scooter", "Other"])
            }

            if st.form_submit_button("Add Delivery"):
                if not delivery_data["delivery_status"] or not delivery_data["vehicle_type"]:
                    st.error("Please fill all the required fields!")
                else:
                    delivery_person_id = delivery_data["delivery_person_id"]
                    self.cursor.execute("SELECT COUNT(*) FROM deliverypersons WHERE delivery_person_id = %s", (delivery_person_id,))
                    result = self.cursor.fetchone()

                    if result[0] == 0:
                        st.error(f"Delivery Person ID {delivery_person_id} does not exist!")
                    else:
                        delivery_status = delivery_data["delivery_status"]
                        vehicle_type = delivery_data["vehicle_type"]
                        try:
                            self.cursor.execute("""
                                INSERT INTO Deliveries (order_id, delivery_person_id, delivery_status, distance, delivery_time, 
                                                        estimated_time, delivery_fee, vehicle_type)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (delivery_data["order_id"], delivery_person_id, delivery_status, delivery_data["distance"], 
                                delivery_data["delivery_time"], delivery_data["estimated_time"], 
                                delivery_data["delivery_fee"], vehicle_type))
                            self.db_connection.commit()
                            st.success("Delivery added successfully!")
                        except Exception as e:
                            st.error(f"Error adding delivery: {str(e)}")

        st.subheader("All Deliveries")
        try:
            self.cursor.execute("SELECT * FROM Deliveries")
            deliveries = self.cursor.fetchall()

            for delivery in deliveries:
                with st.expander(f"Delivery ID: {delivery[0]} (Order ID: {delivery[1]}, Delivery Person ID: {delivery[2]})"):
                    st.write(f"Status: {delivery[3]}")
                    st.write(f"Distance: {float(delivery[4]):.2f} km")  

                    if isinstance(delivery[5], timedelta):
                        delivery_time_minutes = delivery[5].total_seconds() / 60
                    else:
                        delivery_time_minutes = float(delivery[5])  

                    st.write(f"Delivery Time: {delivery_time_minutes:.2f} mins")
                    st.write(f"Estimated Time: {float(delivery[6]):.2f} mins")  
                    st.write(f"Fee: ₹{float(delivery[7]):.2f}")  
                    st.write(f"Vehicle Type: {delivery[8]}")

                    with st.form(f"update_delivery_{delivery[0]}"):
                        updated_delivery_status = st.selectbox("Delivery Status", ["On the way", "Delivered", "Pending", "Cancelled"], 
                                                                index=["On the way", "Delivered", "Pending", "Cancelled"].index(delivery[3]), 
                                                                key=f"status_{delivery[0]}")
                        updated_distance = st.number_input("Distance (in km)", value=float(delivery[4]), 
                                                            min_value=0.0, step=0.1, key=f"distance_{delivery[0]}")

                        if isinstance(delivery[5], timedelta):
                            delivery_time_minutes = delivery[5].total_seconds() / 60
                        else:
                            delivery_time_minutes = float(delivery[5])

                        updated_delivery_time = st.number_input("Delivery Time (in minutes)", 
                                                                value=delivery_time_minutes, min_value=0.0, step=0.1, 
                                                                key=f"time_{delivery[0]}") 

                        updated_estimated_time = st.number_input("Estimated Time (in minutes)", value=float(delivery[6]), 
                                                                min_value=0.0, step=0.1, key=f"est_time_{delivery[0]}") 

                        updated_delivery_fee = st.number_input("Delivery Fee (in ₹)", value=float(delivery[7]), 
                                                                min_value=0.0, step=0.1, key=f"fee_{delivery[0]}")

                        updated_vehicle_types = ["Bike", "Car", "Van", "Bicycle", "Scooter", "Other"]
                        updated_vehicle_type_index = updated_vehicle_types.index(delivery[8]) if delivery[8] in updated_vehicle_types else updated_vehicle_types.index("Other")

                        updated_vehicle_type = st.selectbox("Vehicle Type", updated_vehicle_types, 
                                                            index= updated_vehicle_type_index, key=f"vehicle_{delivery[0]}")

                        if st.form_submit_button("Update Delivery"):
                            if not updated_delivery_status or not updated_distance or not updated_vehicle_type:
                                st.error("Please fill all the required fields!")
                            else:
                                updated_delivery_status = updated_delivery_status if updated_delivery_status else ""
                                updated_distance = updated_distance if updated_distance else 0.0
                                vehicle_type = updated_vehicle_type if updated_vehicle_type else ""                                  
                                try:
                                    self.cursor.execute("""
                                        UPDATE Deliveries SET delivery_status=%s, distance=%s, delivery_time=%s, 
                                                            estimated_time=%s, delivery_fee=%s, vehicle_type=%s 
                                        WHERE delivery_id=%s
                                    """, (updated_delivery_status, updated_distance, updated_delivery_time, 
                                            updated_estimated_time, updated_delivery_fee, vehicle_type, delivery[0]))
                                    self.db_connection.commit()
                                    st.success("Delivery updated successfully!")
                                except Exception as e:
                                    st.error(f"Error updating delivery: {str(e)}")
                    if st.button("Delete Delivery", key=f"delete_{delivery[0]}"):
                        try:
                            self.cursor.execute("DELETE FROM Deliveries WHERE delivery_id=%s", (delivery[0],))
                            self.db_connection.commit()
                            st.warning("Delivery deleted successfully!")
                        except Exception as e:
                            st.error(f"Error deleting delivery: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching deliveries: {str(e)}")
            
    def show_insights(self):
        st.header("Insights")
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Customers")
            total_customers = self.cursor.fetchone()[0]
            st.metric("Total Customers", total_customers)

            self.cursor.execute("SELECT COUNT(*) FROM Restaurants")
            total_restaurants = self.cursor.fetchone()[0]
            st.metric("Total Restaurants", total_restaurants)

            self.cursor.execute("SELECT COUNT(*) FROM Orders WHERE status = 'Delivered'")
            delivered_orders = self.cursor.fetchone()[0]
            st.metric("Delivered Orders", delivered_orders)

            self.cursor.execute("SELECT AVG(customer_feedback_rating) FROM Orders")
            avg_feedback = self.cursor.fetchone()[0] or 0
            st.metric("Average Customer Rating", f"{avg_feedback:.1f}")

            self.cursor.execute("SELECT restaurant_id, COUNT(*) AS order_count FROM Orders GROUP BY restaurant_id ORDER BY order_count DESC LIMIT 5")
            popular_restaurants = self.cursor.fetchall()
            st.subheader("Most Popular Restaurants")
            for restaurant in popular_restaurants:
                st.write(f"Restaurant ID: {restaurant[0]}, Orders: {restaurant[1]}")

            self.cursor.execute("""
                SELECT cuisine_type, COUNT(*) AS order_count 
                FROM Orders 
                JOIN Restaurants ON Orders.restaurant_id = Restaurants.restaurant_id 
                GROUP BY cuisine_type 
                ORDER BY order_count DESC 
                LIMIT 5
            """)
            popular_cuisines = self.cursor.fetchall()
            st.subheader("Most Popular Cuisines")
            for cuisine in popular_cuisines:
                st.write(f"{cuisine[0]}: {cuisine[1]} orders")

            self.cursor.execute("SELECT restaurant_id, SUM(total_amount) AS total_value, COUNT(*) AS order_count FROM Orders GROUP BY restaurant_id")
            restaurant_order_value = self.cursor.fetchall()
            st.subheader("Order Value and Frequency by Restaurant")
            for order_data in restaurant_order_value:
                st.write(f"Restaurant ID: {order_data[0]}, Total Value: ₹{order_data[1]:.2f}, Orders: {order_data[2]}")

            self.cursor.execute("""
                SELECT EXTRACT(HOUR FROM COALESCE(Orders.order_date, NOW())) AS hour, COUNT(*) AS order_count 
                FROM Orders
                JOIN Deliveries ON Orders.order_id = Deliveries.order_id
                GROUP BY hour
                ORDER BY order_count DESC 
                LIMIT 5
            """)
            peak_times = self.cursor.fetchall()
            st.subheader("Peak Order Times")
            for time in peak_times:
                st.write(f"Hour: {time[0]}, Orders: {time[1]}")

            self.cursor.execute("""
                SELECT o.order_id, d.delivery_time, d.estimated_time 
                FROM Orders o
                JOIN Deliveries d ON o.order_id = d.order_id
                WHERE d.delivery_time > d.estimated_time
            """)
            delayed_deliveries = self.cursor.fetchall()
            st.subheader("Delayed Deliveries")
            for delivery in delayed_deliveries:
                st.write(f"Order ID: {delivery[0]}, Delivery Time: {delivery[1]} mins, Estimated Time: {delivery[2]} mins")

            self.cursor.execute("SELECT customer_id, COUNT(*) AS order_count FROM Orders GROUP BY customer_id ORDER BY order_count DESC LIMIT 5")
            frequent_customers = self.cursor.fetchall()
            st.subheader("Top 5 Frequent Customers")
            for customer in frequent_customers:
                st.write(f"Customer ID: {customer[0]}, Orders: {customer[1]}")

        except Exception as e:
            st.error(f"Error fetching insights: {str(e)}")


    def execute_query(self): 
        st.header("Data Exploration")

        queries = {
            "View All Queries": "SELECT * FROM Restaurants;",
            "Top 10 premium customers by orders": """
                SELECT name, total_orders
                FROM Customers
                WHERE is_premium = TRUE
                ORDER BY total_orders DESC
                LIMIT 10;
            """,
            "Restaurants with the highest orders": """
                SELECT name, total_orders
                FROM Restaurants
                ORDER BY total_orders DESC
                LIMIT 10;
            """,
            "Average delivery time by restaurant": """
                SELECT name, AVG(average_delivery_time) as avg_time
                FROM Restaurants
                GROUP BY name;
            """,
            "Deliveries completed by delivery person": """
                SELECT name, total_deliveries
                FROM DeliveryPersons
                ORDER BY total_deliveries DESC;
            """,
            "Total orders by payment mode": """
                SELECT payment_mode, COUNT(*) as total_orders
                FROM Orders
                GROUP BY payment_mode
                ORDER BY total_orders DESC;
            """,
            "Pending deliveries": """
                SELECT *
                FROM Deliveries
                WHERE delivery_status = 'Pending';
            """,
            "Top 5 delivery persons by revenue generated": """
                SELECT dp.name, SUM(d.delivery_fee) as total_revenue
                FROM DeliveryPersons dp
                JOIN Deliveries d ON dp.delivery_person_id = d.delivery_person_id
                GROUP BY dp.name
                ORDER BY total_revenue DESC
                LIMIT 5;
            """,
            "Top 5 cuisines by customer preference": """
                SELECT preferred_cuisine, COUNT(*) as preference_count
                FROM Customers
                GROUP BY preferred_cuisine
                ORDER BY preference_count DESC
                LIMIT 5;
            """,
            "Customers with highest feedback ratings": """
                SELECT name, average_rating
                FROM Customers
                ORDER BY average_rating DESC
                LIMIT 10;
            """,
            "Average spending per customer": """
                SELECT Customers.name AS customer_name, 
                AVG(Orders.total_amount) AS avg_spending FROM Customers 
                JOIN Orders ON Customers.customer_id = Orders.customer_id 
                GROUP BY Customers.name ORDER BY avg_spending DESC;

            """,
            "Orders delivered by vehicle type": """
                SELECT vehicle_type, COUNT(*) as total_deliveries
                FROM Deliveries
                GROUP BY vehicle_type
                ORDER BY total_deliveries DESC;
            """,
            "Customer orders by location": """
                SELECT location, COUNT(*) as total_orders
                FROM Customers
                GROUP BY location
                ORDER BY total_orders DESC;
            """,
            "Deliveries exceeding estimated time": """
                SELECT d.delivery_id, d.delivery_time, d.estimated_time
                FROM Deliveries d
                WHERE d.delivery_time > d.estimated_time;
            """,
            "Most frequently ordered restaurant": """
                SELECT r.name, COUNT(o.order_id) as order_count
                FROM Restaurants r
                JOIN Orders o ON r.restaurant_id = o.restaurant_id
                GROUP BY r.name
                ORDER BY order_count DESC
                LIMIT 1;
            """,
            "Average delivery fee by distance range": """
                SELECT 
                    CASE
                        WHEN distance < 5 THEN '0-5 km'
                        WHEN distance BETWEEN 5 AND 10 THEN '5-10 km'
                        ELSE '10+ km'
                    END as distance_range,
                    AVG(delivery_fee) as avg_fee
                FROM Deliveries
                GROUP BY distance_range;
            """,
            "Top 10 customers by total spending": """
                SELECT c.name, SUM(o.total_amount) as total_spent
                FROM Customers c
                JOIN Orders o ON c.customer_id = o.customer_id
                GROUP BY c.name
                ORDER BY total_spent DESC
                LIMIT 10;
            """,
            "Delivery persons with most delayed deliveries": """
                SELECT dp.name, COUNT(*) as delayed_deliveries
                FROM Deliveries d
                JOIN DeliveryPersons dp ON d.delivery_person_id = dp.delivery_person_id
                WHERE d.delivery_time > d.estimated_time
                GROUP BY dp.name
                ORDER BY delayed_deliveries DESC;
            """,
            "Inactive restaurants": """
                SELECT name
                FROM Restaurants
                WHERE is_active = FALSE;
            """,
            "Total revenue by payment mode": """
                SELECT payment_mode, SUM(total_amount) AS total_revenue
                FROM Orders
                GROUP BY payment_mode
                ORDER BY total_revenue DESC;

            """,
            "Monthly order count by restaurant": """
                SELECT r.name AS restaurant_name,MONTH(o.order_date) AS order_month,
                COUNT(o.order_id) AS total_orders
                FROM Restaurants r
                JOIN Orders o ON r.restaurant_id = o.restaurant_id
                GROUP BY r.name, MONTH(o.order_date)
                ORDER BY r.name, order_month;
            """
        }

        selected_query = st.selectbox("Choose a Query", list(queries.keys()))
        sql_query = queries[selected_query]

        st.text_area("SQL Query", sql_query)
        
        if st.button("Execute Query"):
            try:
                self.cursor.execute(sql_query)
                result = self.cursor.fetchall()
                st.write(result)
            except Exception as e:
                st.error(f"Error executing query: {e}")
                
        general_query = st.text_area("Execute General Query", "SELECT * FROM Deliveries;")
        if st.button("Execute General Query"):
            try:
                self.cursor.execute(general_query)
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

            for _ in range(5):
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
                    INSERT INTO Customers (name, email, phone, location, signup_date, 
                    is_premium, preferred_cuisine, total_orders, average_rating)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (customer_name, customer_email, customer_phone, customer_location, 
                        signup_date, is_premium, preferred_cuisine, total_orders, average_rating))
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
                    INSERT INTO Restaurants (name, cuisine_type, location, owner_name, 
                    contact_number, average_delivery_time, rating, total_orders, is_active)
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
                    customer_feedback_rating = rd.randint(1, 5)

                    self.cursor.execute("""
                        INSERT INTO Orders (customer_id, restaurant_id, order_date, 
                        delivery_time, status, total_amount, payment_mode, discount_applied, customer_feedback_rating)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (customer_id, restaurant_id, order_date, delivery_time, order_status, total_amount, payment_mode,
                        discount_applied, customer_feedback_rating))
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

    menu = ["Home", "Manage Customers", "Manage Restaurants", "Manage Orders", 
            "Manage Delivery Person", "Manage Deliveries", "Insights", "Data Exploration", "Generate Fake Data"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Home":
        app.show_homepage()
    elif choice == "Manage Customers":
        app.manage_customers()
    elif choice == "Manage Restaurants":
        app.manage_restaurants()
    elif choice == "Manage Orders":
        app.manage_orders()
    elif choice == "Manage Delivery Person":
        app.manage_delivery_persons()
    elif choice == "Manage Deliveries":
        app.manage_deliveries()
    elif choice == "Insights":
        app.show_insights()
    elif choice == "Data Exploration":
        app.execute_query()
    elif choice == "Generate Fake Data":
        if st.button("Generate Data"):
            app.generate_fake_data()

if __name__ == "__main__":
    main()