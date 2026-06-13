CREATE TABLE IF NOT EXISTS job(
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(100) NOT NULL,
    file_path TEXT NOT NULL,
    status ENUM(
        'pending',
        'processing',
        'completed',
        'failed'
    ) DEFAULT 'pending' NOT NULL,

    row_count_raw INT,
    row_count_clean INT,

    created_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP
    NULL DEFAULT NULL,

    error_message TEXT
);
CREATE TABLE IF NOT EXISTS payment_transaction(
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    txn_id VARCHAR(50),
    date DATE NOT NULL, 
    merchant VARCHAR(100) NOT NULL, 
    amount DECIMAL(12,4) NOT NULL, 
    currency VARCHAR(10) NOT NULL,
    status ENUM('SUCCESS', 'FAILED', 'PENDING') NOT NULL, 
    category VARCHAR(50), 
    account_id VARCHAR(20) NOT NULL, 
    is_anomaly BOOLEAN DEFAULT FALSE, 
    anomaly_reason VARCHAR(100),
    llm_category VARCHAR(50), 
    llm_raw_response TEXT, 
    llm_failed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE
); 

CREATE TABLE IF NOT EXISTS job_summary(
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL UNIQUE, 
    total_spend_usd DECIMAL(12,4),
    total_spend_inr DECIMAL(12,4), 
    top_merchants JSON,
    anomaly_count INT DEFAULT 0, 
    narrative TEXT, 
    risk_level ENUM('LOW', 'MEDIUM', 'HIGH'),
    FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE
);