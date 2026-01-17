# Business Logic & Workflows

This document explains the real-world business rules and workflows that drive the Wals Honey Management System.

## Business Model Overview
The system is built for a honey aggregation and sales business. The core workflow involves **Purchasing** honey (acquisition), **Inventory Management** (tracking jerrycans/batches), and **Sales** (selling to customers).

---

## 1. Batch Tracking (Inventory)
The fundamental unit of inventory is the **Batch**.

### Batch ID Format
Batches are identified by a unique code, e.g., **A24G02**.
-   **Letter**: Represents the Supplier or Region (e.g., 'A' for Ahmed).
-   **Year**: Two digits for the year (e.g., '24' for 2024).
-   **Group**: A grouping identifier (e.g., 'G02').

### Why Individual Tracking?
We track specific jerrycans/batches because:
-   **Quality Control**: If a specific batch has quality issues, we can trace it back to the supplier.
-   **Costing**: Different batches may be bought at different prices per kg.
-   **Aging**: We need to know how old specific stock is (FIFO - First In, First Out).

### Workflow: Batch Creation
1.  Honey arrives from a supplier.
2.  It is weighed and assigned a Batch ID.
3.  Details (Weight, Cost, Supplier) are entered into the system.
4.  Status is set to 'Active' (Available for sale).

---

## 2. Sales Workflow

### Types of Sales
1.  **Direct Sales**: Selling small quantities (jars) to individuals.
2.  **Wholesale**: Selling bulk quantities (jerrycans) to other retailers.

### Customer Logic
-   **New Customers**: If a customer doesn't exist, they can be created on-the-fly during a sale (though typically we select from the autocomplete list).
-   **History**: We track every sale against a customer to monitor lifetime value and debt.

### Payment Status Logic
A Sale has three possible statuses, automatically calculated based on associated Payments:
1.  **UNPAID**: Total Payments = 0.
2.  **PARTIAL**: 0 < Total Payments < Sale Total.
3.  **PAID**: Total Payments >= Sale Total.

**Example:**
1.  Sale #101 created for **$1,000**. (Status: **UNPAID**)
2.  Customer pays **$200** deposit. (Status updates to: **PARTIAL**)
3.  Customer pays remaining **$800**. (Status updates to: **PAID**)

---

## 3. Expense Tracking
Expenses are tracked separately from product costs (Cost of Goods Sold).
-   **COGS**: The cost of buying the honey (recorded on the Batch model).
-   **Expenses**: Transport, packaging, marketing, rent (recorded on the Expense model).
This separation allows for accurate Gross Object vs. Net Profit calculation.

---

## 4. Audit Trail
**"Trust but Verify"**
-   **What is tracked?**
    -   Modifications to Batch details (e.g., changing weight).
    -   Deletion of Payments.
    -   Edits to crucial Sale info.
-   **Visibility**: Admins can view the "Change History" tab on any record to see *who* changed *what* and *when*.
-   **Value**: Prevents theft and accidental data loss.

---

## 5. Validation Rules
The system prevents common data entry errors:
-   **Duplicate Batches**: You cannot create two active batches with the exact same ID.
-   **Negative Values**: Sales amounts and weights cannot be negative.
-   **Dates**: Simple valid dates required (dd/mm/yyyy).

## Real-World Scenario: A Complete Cycle
1.  **Acquisition**: Walid buys 5 jerrycans from Supplier "Mountain". He enters them as Batch **M24G05**, Total Weight 120kg, Cost $500.
2.  **Sale**: Customer "Sweet Shop" orders 50kg.
3.  **Transaction**:
    -   User creates a Sale for "Sweet Shop".
    -   Items: 50kg Honey (from Batch M24G05) @ $10/kg = $500.
    -   Sale is saved -> Status **UNPAID**.
4.  **Payment**:
    -   Sweet Shop transfers $500.
    -   User adds a Payment of $500 linked to that Sale.
    -   System auto-updates Sale status to **PAID**.
5.  **Audit**:
    -   Later, an admin checks the Batch M24G05. He sees 50kg was sold, remaining stock is 70kg.
