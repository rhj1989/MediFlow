# Retail Medical Store Management System - Project Plan ✅

## Overview
Building a comprehensive web-based medical store management system with billing, inventory, supplier management, purchase tracking, expiry alerts, reporting functionality, customer management, and prescription tracking.

---

## Phase 1: Database Setup, Authentication & Dashboard UI ✅
- [x] Set up SQLite database schema (Medicines, Suppliers, Purchases, Sales, SaleItems, Users tables)
- [x] Create database initialization and helper functions
- [x] Implement user authentication (login/logout) with session management
- [x] Build main dashboard layout with sidebar navigation
- [x] Create dashboard cards displaying key metrics (Total Medicines, Low Stock, Today's Sales, Expiry Alerts)
- [x] Add responsive navigation with links to all modules

---

## Phase 2: Medicine Inventory & Supplier Management ✅
- [x] Build Medicines page with searchable table listing all medicines
- [x] Implement add/edit/delete medicine functionality with forms
- [x] Add medicine fields: name, batch_no, expiry_date, quantity, purchase_price, sale_price, supplier
- [x] **Add drug_type field with dropdown selection (Tablet, Capsule, Syrup, Injection, Cream, Ointment, Drops, Inhaler)**
- [x] **Add unit field for medicine measurement (Tablets, Bottles, Strips, ml, mg, gm, etc.)**
- [x] Create low stock alerts (medicines with quantity below threshold)
- [x] Create expiry alerts (medicines expiring within 30 days)
- [x] Build Suppliers page with table view of all suppliers
- [x] Implement add/edit/delete supplier functionality
- [x] Add supplier fields: name, contact_no, address
- [x] Link medicines to suppliers via dropdown selection

---

## Phase 3: Billing System & Purchase Entry ✅
- [x] Create billing page with medicine search and selection
- [x] Build shopping cart interface for adding multiple medicines to a bill
- [x] Display medicine details (name, batch, price, available quantity) during billing
- [x] Calculate total amount with item-wise breakdown
- [x] Generate bill and save to Sales and SaleItems tables
- [x] Automatically update medicine stock quantities after sale
- [x] Create purchase entry page for recording new stock arrivals
- [x] Build purchase form with supplier selection and medicine details
- [x] Record purchase details in Purchases table
- [x] Update medicine quantities upon purchase entry

---

## Phase 4: Reports & Data Management ✅
- [x] Create Reports page with multiple report types
- [x] Build Sales Report with date range filter showing daily/monthly sales
- [x] Create Stock Report displaying current inventory levels
- [x] Build Expiry Report showing medicines expiring soon with date filters
- [x] Add Low Stock Report highlighting medicines below threshold
- [x] Implement Supplier-wise Purchase Report
- [x] Create data export functionality (CSV download for reports)
- [x] Build Settings page for store configuration
- [x] Add backup functionality to export database
- [x] Implement restore functionality to import database backup

---

## Phase 5: Customer Management & Prescription Tracking ✅
- [x] Create Customers database table with fields: name, phone, email, address, date_registered
- [x] Create Prescriptions table with fields: customer_id, prescription_number, doctor_name, prescription_date, notes, image_path
- [x] Link Sales table to Customers table via customer_id foreign key
- [x] Build Customers page with searchable table of all registered customers
- [x] Implement add/edit/delete customer functionality with form validation
- [x] Add customer profile view showing personal details and purchase history

---

## Phase 6: Prescription Management & Enhanced Billing ✅
- [x] Update billing page to include customer selection/creation
- [x] Add optional customer association to sales transactions
- [x] Display customer selection dropdown during billing
- [x] Link customer_id to sales records when customer is selected
- [x] Support walk-in customers (no customer selection required)
- [x] **Add doctor's name field to billing page**
- [x] **Save doctor name with each sale transaction**
- [x] **Clear doctor name when bill is cleared or generated**

---

## Phase 7: Customer Purchase Reports & Analytics ✅
- [x] Create Customer Purchase Report showing individual customer spending
- [x] Build Customer-wise transaction history with date filters
- [x] Add customer purchase report type to reports page
- [x] Implement customer export functionality (CSV with purchase data)
- [x] Create dashboard widget for customer statistics (total customers)

---

## Phase 8: Prescription Module for Saved Customers ✅
- [x] Create Prescriptions page (`/prescriptions`) with searchable table
- [x] Build prescription form modal with fields:
  - Customer selection dropdown
  - Prescription number
  - Doctor name
  - Prescription date
  - Notes/remarks
  - Image upload for prescription scan
- [x] Implement add/edit/delete prescription functionality
- [x] Add prescription image upload to `assets/prescriptions/` folder
- [x] Display prescription image preview in form modal
- [x] Link prescriptions to customers via customer_id
- [x] Add "Prescriptions" link to sidebar navigation
- [x] Update Customers page to show prescription count
- [x] Add "View Prescriptions" button in customer table actions
- [x] Enable filtering prescriptions by customer from customer page
- [x] Search prescriptions by customer name or prescription number

---

## Notes
- Default login credentials: admin / admin
- All pages are protected and require authentication
- Real-time calculations and automatic stock updates
- Date-based filtering for reports
- Export functionality for data portability
- Customer data privacy and secure storage
- Walk-in customer support (billing without customer selection)
- Customer-linked sales tracking for analytics
- **Doctor name is now captured during billing for prescription tracking**
- Prescription images stored in `assets/prescriptions/` folder
- Prescriptions linked to customers for complete medical history tracking
- Prescription search by customer name or prescription number
- **Drug Type field categorizes medicines (Tablet, Capsule, Syrup, Injection, Cream, Ointment, Drops, Inhaler)**
- **Medicine units track measurement types (Tablets, Bottles, Strips, ml, mg, gm, Injections, Syrups)**