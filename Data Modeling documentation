# RouteOptim Data Model Documentation

## Introduction

The "RouteOptim" project aims to enhance delivery efficiency for small businesses by optimizing delivery routes. This document provides a detailed overview of the data model, outlining the structure, relationships, and attributes of the database entities.

## Entity-Relationship Diagram (ERD)

The ERD visually represents the entities within the system and their interrelationships.

![Entity-Relationship Diagram](path/to/your/ERD/image.png)

## Entities and Attributes

The primary entities in the "RouteOptim" data model are:

1. **Users**
2. **Deliveries**
3. **Vehicles**
4. **Routes**
5. **Customers**

### 1. Users

This table stores information about all users interacting with the system, including administrators, drivers, and customers.

- **Attributes:**
  - `id`: Integer, Primary Key, Auto-increment
  - `name`: Varchar, User's full name
  - `email`: Varchar, Unique email address
  - `password_hash`: Varchar, Hashed password for authentication
  - `role`: Varchar, Defines user role (`admin`, `driver`, `customer`)
  - `contact_info`: Varchar, Contact details

### 2. Deliveries

This table manages details of each delivery order.

- **Attributes:**
  - `id`: Integer, Primary Key, Auto-increment
  - `pickup_address`: Varchar, Origin address
  - `delivery_address`: Varchar, Destination address
  - `customer_id`: Integer, Foreign Key referencing `customers.id`
  - `scheduled_time`: Datetime, Planned delivery time
  - `status`: Varchar, Current status (`pending`, `in-transit`, `delivered`)
  - `driver_id`: Integer, Foreign Key referencing `users.id`
  - `route_id`: Integer, Foreign Key referencing `routes.id`

### 3. Vehicles

This table contains information about the fleet of vehicles used for deliveries.

- **Attributes:**
  - `id`: Integer, Primary Key, Auto-increment
  - `license_plate`: Varchar, Unique vehicle identifier
  - `model`: Varchar, Vehicle model
  - `capacity`: Integer, Load capacity
  - `current_location`: Varchar, Real-time location
  - `driver_id`: Integer, Foreign Key referencing `users.id`

### 4. Routes

This table defines the optimized delivery routes.

- **Attributes:**
  - `id`: Integer, Primary Key, Auto-increment
  - `date`: Date, Route assignment date
  - `optimized_path`: Text, Serialized data of the route
  - `total_distance`: Float, Total distance covered
  - `estimated_time`: Float, Estimated duration
  - `vehicle_id`: Integer, Foreign Key referencing `vehicles.id`

### 5. Customers

This table holds information about customers receiving deliveries.

- **Attributes:**
  - `id`: Integer, Primary Key, Auto-increment
  - `name`: Varchar, Customer's full name
  - `contact_info`: Varchar, Contact details
  - `address`: Varchar, Delivery address

## Relationships

- **Users to Deliveries**: One-to-Many. A user (driver) can handle multiple deliveries.
- **Deliveries to Customers**: Many-to-One. Each delivery is linked to a single customer.
- **Vehicles to Routes**: One-to-Many. A vehicle can be assigned multiple routes over time.
- **Routes to Deliveries**: One-to-Many. Each route encompasses multiple deliveries.
- **Vehicles to Users**: One-to-One. Each vehicle is assigned to a single driver.

## Data Dictionary

The data dictionary provides detailed descriptions of each attribute within the tables.

### Users Table

| Attribute       | Data Type | Description                     |
|-----------------|-----------|---------------------------------|
| `id`            | Integer   | Unique identifier for each user |
| `name`          | Varchar   | Full name of the user           |
| `email`         | Varchar   | User's email address            |
| `password_hash` | Varchar   | Encrypted password              |
| `role`          | Varchar   | User's role in the system       |
| `contact_info`  | Varchar   | User's contact information      |

### Deliveries Table

| Attribute         | Data Type | Description                               |
|-------------------|-----------|-------------------------------------------|
| `id`              | Integer   | Unique identifier for each delivery       |
| `pickup_address`  | Varchar   | Address where the delivery originates     |
| `delivery_address`| Varchar   | Address where the delivery is destined    |
| `customer_id`     | Integer   | References the customer receiving the delivery |
| `scheduled_time`  | Datetime  | Planned time for the delivery             |
| `status`          | Varchar   | Current status of the delivery            |
| `driver_id`       | Integer   | References the driver assigned to the delivery |
| `route_id`        | Integer   | References the route assigned to the delivery |

### Vehicles Table

| Attribute        | Data Type | Description                               |
|------------------|-----------|-------------------------------------------|
| `id`             | Integer   | Unique identifier for each vehicle        |
| `license_plate`  | Varchar   | Vehicle's license plate number            |
| `model`          | Varchar   | Vehicle model                             |
| `capacity`       | Integer   | Load capacity of the vehicle              |
| `current_location`| Varchar  | Current location of the vehicle           |
| `driver_id`      | Integer   | References the driver assigned to the vehicle |

### Routes Table

| Attribute        | Data Type | Description                               |
|------------------|-----------|-------------------------------------------|
| `id`             | Integer   | Unique identifier for each route          |
| `date`           | Date      | Date of the route                         |
| `optimized_path` | Text      | Serialized data representing the route    |
| `total_distance` | Float     | Total distance of the route               |
| `estimated_time` | Float     | Estimated time to complete the route      |
| `vehicle_id`     | Integer   | References the vehicle assigned to the route |

### Customers Table

| Attribute       | Data Type | Description                               |
|-----------------|-----------|-------------------------------------------|
| `id`            | Integer   | Unique identifier for each customer       |
| `name`          | Varchar   | Full name of the customer                 |
| `contact_info`  | Varchar   | Contact information of the customer       |
| `address`       | Varchar   | Address of the customer                   |

## Notes

- Ensure that all foreign key relationships are properly indexed to maintain database integrity and optimize query performance.
- The `optimized_path` in the `routes` table should be structured in a format that can be easily parsed by the application for route reconstruction.
