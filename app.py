import psutil
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # Get CPU usage (waits 1 second for real value)
    cpu_metric = psutil.cpu_percent(interval=1)

    # Get detailed memory usage
    mem = psutil.virtual_memory()
    mem_metric = mem.percent

    # Print debug info to console
    print(f"[DEBUG] CPU: {cpu_metric}%")
    print(f"[DEBUG] Memory: {mem_metric}% used, {mem.used / (1024**3):.2f} GB used of {mem.total / (1024**3):.2f} GB")

    # Check for threshold breach
    Message = None
    if cpu_metric > 50 or mem_metric > 50:
        Message = "High CPU or Memory Detected, scale up!!!"
        print("[ALERT] Threshold crossed!")

    # Pass values to the HTML template
    return render_template("index.html", cpu_metric=cpu_metric, mem_metric=mem_metric, message=Message)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
