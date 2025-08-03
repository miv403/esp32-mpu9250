import serial
import numpy as np
from io import StringIO
from time import sleep
import json
import datetime
import threading
import queue
import sys
import time
import matplotlib.pyplot as plt

# Import Device class from device.py
from device import Device, ser, CMD_SAVE_BIAS, CALIB_DONE

class StdoutCatcher:
    def __init__(self, q):
        self.q = q
        self._buffer = ''
    def write(self, s):
        self._buffer += s
        while '\n' in self._buffer:
            line, self._buffer = self._buffer.split('\n', 1)
            self.q.put(line)
    def flush(self):
        pass

def data_reader_thread(q, error_q):
    import sys as _sys
    try:
        esp32 = Device()
        catcher = StdoutCatcher(q)
        old_stdout = _sys.stdout
        _sys.stdout = catcher
        try:
            esp32.sendBias()
        finally:
            _sys.stdout = old_stdout
    except Exception as e:
        error_q.put(str(e))

def collect_yaw_data(duration=25, target_samples=1000):
    """
    Collect yaw data for specified duration with target number of samples
    """
    data_q = queue.Queue()
    error_q = queue.Queue()
    
    # Start data collection thread
    t = threading.Thread(target=data_reader_thread, args=(data_q, error_q), daemon=True)
    t.start()
    
    yaw_data = []
    timestamps = []
    start_time = time.time()
    sample_interval = duration / target_samples
    
    print(f"Collecting yaw data for {duration} seconds with {target_samples} samples...")
    print(f"Sample interval: {sample_interval:.3f} seconds")
    
    last_sample_time = start_time
    
    while time.time() - start_time < duration and len(yaw_data) < target_samples:
        # Get latest data from queue
        try:
            while True:
                line = data_q.get_nowait()
                line = line.strip()
                if line and (',' in line):
                    parts = line.split(',')
                    if len(parts) == 13:  # roll,pitch,yaw,accX,accY,accZ,gyroX,gyroY,gyroZ,magX,magY,magZ,temp
                        try:
                            roll, pitch, yaw = map(float, parts[0:3])
                            current_time = time.time()
                            
                            # Only collect sample if enough time has passed
                            if current_time - last_sample_time >= sample_interval:
                                yaw_data.append(yaw)
                                timestamps.append(current_time - start_time)
                                last_sample_time = current_time
                                print(f"Sample {len(yaw_data)}: yaw={yaw:.2f}°, time={timestamps[-1]:.3f}s")
                                
                                if len(yaw_data) >= target_samples:
                                    break
                        except ValueError:
                            pass
        except queue.Empty:
            pass
        
        # Check for errors
        try:
            while True:
                error = error_q.get_nowait()
                print(f"Error: {error}")
        except queue.Empty:
            pass
        
        time.sleep(0.001)  # Small sleep to prevent busy waiting
    
    print(f"Collected {len(yaw_data)} yaw samples")
    return np.array(yaw_data), np.array(timestamps)

def analyze_yaw_linearity(yaw_data, timestamps):
    """
    Analyze if yaw data increases linearly
    """
    if len(yaw_data) < 2:
        print("Not enough data for analysis")
        return
    
    # Calculate rate of change (degrees per second)
    yaw_rates = np.diff(yaw_data) / np.diff(timestamps)
    
    # Calculate statistics
    mean_rate = np.mean(yaw_rates)
    std_rate = np.std(yaw_rates)
    min_rate = np.min(yaw_rates)
    max_rate = np.max(yaw_rates)
    
    print(f"\nYaw Analysis Results:")
    print(f"Mean rate of change: {mean_rate:.3f} °/s")
    print(f"Standard deviation: {std_rate:.3f} °/s")
    print(f"Min rate: {min_rate:.3f} °/s")
    print(f"Max rate: {max_rate:.3f} °/s")
    print(f"Rate variation: {((max_rate - min_rate) / mean_rate * 100):.1f}%")
    
    # Check linearity (low standard deviation indicates linearity)
    if std_rate < 0.5:  # Threshold for linearity
        print("✓ Yaw appears to be changing linearly")
    else:
        print("✗ Yaw does not appear to be changing linearly")
    
    return yaw_rates

def visualize_yaw_data(yaw_data, timestamps, yaw_rates):
    """
    Visualize yaw data and its rate of change
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot 1: Yaw vs Time
    ax1.plot(timestamps, yaw_data, 'b-', linewidth=2, label='Yaw')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Yaw (°)')
    ax1.set_title('Yaw vs Time')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Rate of change vs Time
    if len(yaw_rates) > 0:
        rate_timestamps = timestamps[:-1]  # One less point for rates
        ax2.plot(rate_timestamps, yaw_rates, 'r-', linewidth=2, label='Rate of Change')
        ax2.axhline(y=np.mean(yaw_rates), color='g', linestyle='--', label=f'Mean: {np.mean(yaw_rates):.3f}°/s')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Rate of Change (°/s)')
        ax2.set_title('Yaw Rate of Change vs Time')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
    
    plt.tight_layout()
    plt.show()

def main():
    print("Yaw Data Analyzer")
    print("=" * 50)
    
    # Collect yaw data
    yaw_data, timestamps = collect_yaw_data(duration=5, target_samples=1000)
    
    if len(yaw_data) == 0:
        print("No yaw data collected. Check device connection.")
        return
    
    # Analyze linearity
    yaw_rates = analyze_yaw_linearity(yaw_data, timestamps)
    
    # Visualize data
    visualize_yaw_data(yaw_data, timestamps, yaw_rates)
    
    # Save data to file
    data_dict = {
        'timestamps': timestamps.tolist(),
        'yaw_data': yaw_data.tolist(),
        'yaw_rates': yaw_rates.tolist() if yaw_rates is not None else [],
        'collection_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': 5,
        'samples': len(yaw_data)
    }
    
    with open('yaw_analysis_data.json', 'w') as f:
        json.dump(data_dict, f, indent=4)
    
    print(f"\nData saved to yaw_analysis_data.json")

if __name__ == '__main__':
    main() 