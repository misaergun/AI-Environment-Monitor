
import csv
import time
from datetime import datetime
from pathlib import Path

import serial

# Arduino IDE'de görünen portu buraya yaz.
SERIAL_PORT = "/dev/cu.usbmodem11301"
BAUD_RATE = 9600

CSV_FILE = Path("sensor_data.csv")


def main():
    print(f"Connecting to Arduino on {SERIAL_PORT}...")

    try:
        with serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=2
        ) as arduino:
            # Arduino resetlenirse başlangıç mesajlarını bekle.
            time.sleep(2)
            print("Connected. Collecting sensor data.")
            print("Press Ctrl+C to stop.\n")

            file_exists = CSV_FILE.exists() and CSV_FILE.stat().st_size > 0

            with CSV_FILE.open("a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow([
                        "timestamp",
                        "temperature_c",
                        "humidity_percent",
                        "light_raw"
                    ])
                    file.flush()

                while True:
                    line = arduino.readline().decode(
                        "utf-8", errors="replace"
                    ).strip()

                    if not line:
                        continue

                    # Başlangıç mesajlarını atla.
                    if not line.startswith("Temperature:"):
                        print(f"Arduino: {line}")
                        continue

                    try:
                        parts = line.split("|")

                        temperature = float(
                            parts[0].split(":")[1]
                            .strip().split()[0]
                        )
                        humidity = float(
                            parts[1].split(":")[1]
                            .strip().split()[0]
                        )
                        light = int(
                            parts[2].split(":")[1].strip()
                        )

                    except (IndexError, ValueError) as error:
                        print(f"Invalid sensor data: {line} ({error})")
                        continue

                    timestamp = datetime.now().astimezone().isoformat(
                        timespec="seconds"
                    )

                    writer.writerow([
                        timestamp,
                        temperature,
                        humidity,
                        light
                    ])
                    file.flush()

                    print(
                        f"{timestamp} | "
                        f"Temperature: {temperature:.1f} C | "
                        f"Humidity: {humidity:.1f}% | "
                        f"Light: {light}"
                    )

    except serial.SerialException as error:
        print(f"Serial connection error: {error}")
        print("Check the USB cable, port name, and Serial Monitor.")
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()
