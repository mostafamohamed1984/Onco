# Importation Cycle Workflow
This guide tracks the journey from initial quotation to final warehouse release, including cold chain and regulatory checks.

## Visual Workflow
```mermaid
graph TD
    A["Supplier Quotation (Standard)"] --> B["Purchase Order (Standard)"]
    B -->|Link: shipment_no| C["Shipments (Custom)"]
    
    subgraph "Shipment Management"
        C --> C1["Shipment Invoice (Child Table)"]
        C --> C2["Packing Detail (Child Table)"]
        C --> C3["Milestone Tracking (Status: In Progress)"]
    end
    
    C --> D["Purchase Receipt (Standard)"]
    D <--> E["Purchase Receipt Report (Custom)"]
    
    subgraph "Validation Gates"
        E --> E1["Vehicle Inspection"]
        E --> E2["Temperature Check (Cold Chain)"]
        E --> E3["Seal & Document Verification"]
    end
    
    E --> F["Authority Good Release (Custom)"]
    
    subgraph "Regulatory Release"
        F --> F1["Shortage Control Calculation"]
        F --> F2["Analysis Batch / Sample Logic"]
    end
    
    F -->|On Submit| G["Stock Entry (Automated)"]
    G --> G1["Sale Warehouse (Net Qty)"]
    G --> G2["Sample Warehouse (Withdrawals)"]
    
    G --> H["Purchase Invoice (Standard)"]
```

## Step-by-Step Testing
1.  **Initial Purchase**: Create a `Purchase Order`. Ensure you fill the `custom_shipment_no` field.
2.  **Create Shipment**: Go to `Shipments`, create a new record. Link it to your PO. Add data to the `Packing Details` (Pallets/Cartons) and `Invoices` tables.
3.  **Receive Goods**: Create a `Purchase Receipt` from the PO.
4.  **Quality Inspection**: Open `Purchase Receipt Report`. Check that it correctly links to your Receipt. Fill in the Vehicle and Temperature details. If temperature is out of range, ensure "Supplier Notified" is filled.
5.  **Final Release**: Create an `Authority Good Release` (AGR). 
    -   Click "Fetch Items". It will pull from the `Purchase Receipt Report`.
    -   Enter `Released Qty` and `Actual Qty`. Verify `Net Released Qty` calculates correctly.
    -   Submit the AGR. Check `Stock Entry` to see if goods moved from "Under Release" to "Sales Warehouse".
