# Tender Cycle Workflow
This guide manages official price lists, forecasting, and enforces pricing rules during sales.

## Visual Workflow
```mermaid
graph TD
    T["Tender (Custom DocType)"] --> T1["Tender Price List (Official Prices)"]
    T --> T2["Items FMD (Forecasting/Market Data)"]
    T --> T3["Tender Status Tracking"]
    
    subgraph "Sales Execution"
        SO["Sales Order (Standard)"] -->|Link: custom_tender_ref| T
        SO --> SI["Sales Invoice (Standard)"]
    end
    
    subgraph "Price Enforcement"
        SI --> V{"Below Tender Price?"}
        V -- No --> P["Post Invoice"]
        V -- Yes --> D["Deviation Approval Required"]
        D -->|Fill: Cause, Approver, Date| P
    end
    
    P -->|Update| STAT["Tender Fulfillment Status"]
```

## Step-by-Step Testing
1.  **Setup Tender**: Create a `Tender`. Link multiple `Price Lists` in the child table. Add items to the `Items FMD` (use text names for forecasting if item codes aren't ready).
2.  **Sales Order**: Create a `Sales Order`. Select your `Tender Reference`.
3.  **Invoice Validation**: Create a `Sales Invoice`.
    -   Try to set a rate **lower** than the tender price.
    -   Try to save/submit. The system should block you, demanding "Cause of Deviation" and "Approved By".
    -   Fill these fields and submit.
4.  **Fulfillment Check**: Go back to the `Tender` record. Verify that the "Fulfillment Status" and "Losses Value" in the technical deviation table have updated based on the invoice.
