import psutil
import time
import json
import numpy as np
import smtplib
from email.mime.text import MIMEText

# Function to collect system metrics
def get_system_metrics():
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory Usage
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Disk Usage
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    # Network Usage
    net = psutil.net_io_counters()
    bytes_sent = net.bytes_sent
    bytes_recv = net.bytes_recv
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'disk_percent': disk_percent,
        'bytes_sent': bytes_sent,
        'bytes_recv': bytes_recv
    }

# Function to load baseline data (previously recorded system metrics)
def load_baseline_data(filename='metrics_baseline.json'):
    baseline = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                baseline.append(json.loads(line))
    except Exception as e:
        print(f"Error loading baseline data: {e}")
    return baseline

# Function to save the metrics to the baseline file
def save_metrics(metrics, filename='metrics_baseline.json'):
    try:
        with open(filename, 'a') as f:
            json.dump(metrics, f)
            f.write("\n")  # New line for each entry
    except Exception as e:
        print(f"Error saving metrics: {e}")

# Function to send email alerts when an anomaly is detected
def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = 'Anomaly Detected in System Behavior'
    msg['From'] = 'your_email@example.com'  # Change to your email address
    msg['To'] = 'admin@example.com'  # Change to recipient's email address
    
    # Setup the SMTP server
    with smtplib.SMTP('smtp.example.com') as server:  # Replace with your SMTP server
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

# Function to detect anomalies based on baseline data
def detect_anomalies(real_time_data, baseline_data, threshold=20):
    # Compare real-time data to baseline
    for metric in real_time_data:
        baseline_values = [entry[metric] for entry in baseline_data]
        mean = np.mean(baseline_values)
        std_dev = np.std(baseline_values)
        deviation = abs(real_time_data[metric] - mean)
        
        if deviation > (threshold * std_dev):
            anomaly_message = f"Anomaly detected in {metric}: {real_time_data[metric]}\n"
            print(anomaly_message)  # Output to console
            send_alert(anomaly_message)  # Send email alert
            return True
    return False

# Function to display metrics in the terminal
def display_metrics(metrics):
    print("CPU Usage: {}%".format(metrics['cpu_percent']))
    print("Memory Usage: {}%".format(metrics['memory_percent']))
    print("Disk Usage: {}%".format(metrics['disk_percent']))
    print("Network Sent: {} bytes".format(metrics['bytes_sent']))
    print("Network Received: {} bytes".format(metrics['bytes_recv']))
    print("\n---\n")

# Main function to monitor the system and detect anomalies
if __name__ == "__main__":
    print("Monitoring system metrics...\n")
    
    # Load previously collected baseline data
    baseline_data = load_baseline_data()
    
    while True:
        metrics = get_system_metrics()
        display_metrics(metrics)
        
        # Detect anomalies in the real-time data
        if detect_anomalies(metrics, baseline_data):
            print("Anomaly detected!\n")
        
        # Save the current metrics to baseline file for future comparison
        save_metrics(metrics)
        
        time.sleep(5)  # Sleep for 5 seconds before collecting data again

