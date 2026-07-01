const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

async function main() {
    // Read connection string from settings.json
    const settingsPath = path.join(__dirname, '.gemini', 'settings.json');
    if (!fs.existsSync(settingsPath)) {
        console.error("settings.json not found");
        process.exit(1);
    }
    const config = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    const connStr = config.mcpServers.postgres.args[config.mcpServers.postgres.args.length - 1];
    console.log("Using connection string:", connStr);

    const client = new Client({
        connectionString: connStr,
        ssl: {
            rejectUnauthorized: false
        }
    });

    try {
        await client.connect();
        console.log("Connected successfully using Node.js pg!");
    } catch (e) {
        console.error("Connection failed in Node.js:", e.message);
        process.exit(1);
    }

    const queries = {
        1: { desc: "What is the total revenue?", sql: "SELECT SUM(payment_value) AS total_revenue FROM fact_order_items;" },
        2: { desc: "How many orders have been placed?", sql: "SELECT COUNT(DISTINCT order_id) AS total_orders FROM fact_order_items;" },
        3: { desc: "How many unique customers do we have?", sql: "SELECT COUNT(DISTINCT customer_id) AS total_customers FROM fact_order_items;" },
        4: { desc: "What is the average review score?", sql: "SELECT AVG(review_score) AS average_review_score FROM fact_order_items;" },
        5: { desc: "Show monthly revenue.", sql: "SELECT DATE_TRUNC('month', shipping_limit_date) AS month, SUM(payment_value) AS revenue FROM fact_order_items GROUP BY month ORDER BY month;" },
        6: { desc: "Show the top 10 product categories by revenue.", sql: `
            SELECT dp.product_category_name, SUM(f.payment_value) AS revenue 
            FROM fact_order_items f 
            JOIN dim_products dp ON f.product_id = dp.product_id 
            GROUP BY dp.product_category_name 
            ORDER BY revenue DESC 
            LIMIT 10;
        `},
        7: { desc: "Show the top 10 sellers by revenue.", sql: "SELECT seller_id, SUM(payment_value) AS revenue FROM fact_order_items GROUP BY seller_id ORDER BY revenue DESC LIMIT 10;" },
        8: { desc: "Show the order distribution by payment type.", sql: "SELECT payment_type, COUNT(*) AS number_of_orders FROM fact_order_items GROUP BY payment_type;" },
        9: { desc: "Show the average order value by review score.", sql: "SELECT review_score, AVG(payment_value) AS average_order_value FROM fact_order_items GROUP BY review_score ORDER BY review_score;" },
        10: { desc: "Show the average freight cost by number of payment installments.", sql: "SELECT payment_installments, AVG(freight_value) AS average_freight FROM fact_order_items GROUP BY payment_installments ORDER BY payment_installments;" },
        11: { desc: "Show revenue by customer state.", sql: `
            SELECT c.customer_state, SUM(f.payment_value) AS revenue 
            FROM fact_order_items f 
            JOIN dim_customers c ON f.customer_id = c.customer_id 
            GROUP BY c.customer_state 
            ORDER BY revenue DESC;
        `}
    };

    const results = {};

    for (const [qNum, item] of Object.entries(queries)) {
        try {
            const res = await client.query(item.sql);
            results[qNum] = { sql: item.sql, cols: res.fields.map(f => f.name), rows: res.rows };
        } catch (e) {
            // Handle fallback for query 5 (shipping_date_limit)
            if (qNum == '5' && e.message.includes('column "shipping_limit_date" does not exist')) {
                try {
                    const altSql = "SELECT DATE_TRUNC('month', shipping_date_limit) AS month, SUM(payment_value) AS revenue FROM fact_order_items GROUP BY month ORDER BY month;";
                    const res = await client.query(altSql);
                    results[qNum] = { sql: altSql, cols: res.fields.map(f => f.name), rows: res.rows };
                    continue;
                } catch (err2) {
                    console.error(`Query ${qNum} fallback failed:`, err2.message);
                }
            }
            // Handle fallback for query 10 (payment_installment)
            if (qNum == '10' && e.message.includes('column "payment_installments" does not exist')) {
                try {
                    const altSql = "SELECT payment_installment, AVG(freight_value) AS average_freight FROM fact_order_items GROUP BY payment_installment ORDER BY payment_installment;";
                    const res = await client.query(altSql);
                    results[qNum] = { sql: altSql, cols: res.fields.map(f => f.name), rows: res.rows };
                    continue;
                } catch (err2) {
                    console.error(`Query ${qNum} fallback failed:`, err2.message);
                }
            }
            console.error(`Query ${qNum} failed:`, e.message);
            process.exit(1);
        }
    }

    await client.end();

    // Print results in markdown format
    for (const qNum of Object.keys(results).sort((a,b) => a-b)) {
        const item = results[qNum];
        console.log(`### Question ${qNum}: ${queries[qNum].desc}`);
        console.log("\n**SQL Query:**");
        console.log("```sql");
        console.log(item.sql.trim());
        console.log("```");
        console.log("\n**Query Result:**");
        
        if (item.rows && item.rows.length > 0) {
            // Print markdown table
            const header = "| " + item.cols.join(" | ") + " |";
            const separator = "| " + item.cols.map(() => "---").join(" | ") + " |";
            console.log(header);
            console.log(separator);
            for (const r of item.rows) {
                const rowStr = "| " + item.cols.map(col => {
                    const val = r[col];
                    if (val instanceof Date) {
                        return val.toISOString();
                    }
                    return val !== null && val !== undefined ? val : "NULL";
                }).join(" | ") + " |";
                console.log(rowStr);
            }
        } else {
            console.log("No results returned.");
        }
        console.log("\n" + "=".repeat(80) + "\n");
    }
}

main();
