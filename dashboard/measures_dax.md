# DAX Measures

Create these measures in Power BI after importing the marts.

## Core KPI Measures

```DAX
Total Revenue = SUM('sales_overview'[total_revenue])
```

```DAX
Total Orders = SUM('sales_overview'[total_orders])
```

```DAX
Total Quantity = SUM('sales_overview'[total_quantity])
```

```DAX
Average Order Value = DIVIDE([Total Revenue], [Total Orders])
```

```DAX
Monthly Revenue = SUM('sales_overview'[monthly_revenue])
```

```DAX
Average Revenue Growth % = AVERAGE('sales_overview'[revenue_growth_pct])
```

## Product Measures

```DAX
Product Revenue = SUM('product_performance'[total_revenue])
```

```DAX
Product Quantity Sold = SUM('product_performance'[quantity_sold])
```

```DAX
Average Product Revenue =
AVERAGE('product_performance'[total_revenue])
```

```DAX
Top Product Rank =
MIN('product_performance'[revenue_rank])
```

## Customer Measures

```DAX
Customer Revenue = SUM('customer_performance'[total_revenue])
```

```DAX
Customer Count = DISTINCTCOUNT('customer_performance'[customer_key])
```

```DAX
Repeat Customer Count =
CALCULATE(
    DISTINCTCOUNT('customer_performance'[customer_key]),
    'customer_performance'[is_repeat_customer] = TRUE()
)
```

```DAX
Repeat Customer Rate =
DIVIDE([Repeat Customer Count], [Customer Count])
```

## Store Measures

```DAX
Store Revenue = SUM('store_performance'[total_revenue])
```

```DAX
Holiday Revenue = SUM('store_performance'[holiday_revenue])
```

```DAX
Non Holiday Revenue = SUM('store_performance'[non_holiday_revenue])
```

```DAX
Holiday Revenue Share =
DIVIDE([Holiday Revenue], [Holiday Revenue] + [Non Holiday Revenue])
```

```DAX
Average Sales Per Store Size =
AVERAGE('store_performance'[sales_per_store_size])
```

## Forecasting Measures

```DAX
Forecasting Base Revenue = SUM('forecasting_base'[revenue])
```

```DAX
Forecasting Record Count = COUNTROWS('forecasting_base')
```

```DAX
Average Weekly Revenue = AVERAGE('forecasting_base'[revenue])
```

```DAX
Holiday Week Revenue =
CALCULATE(
    SUM('forecasting_base'[revenue]),
    'forecasting_base'[holiday_flag] = TRUE()
)
```
