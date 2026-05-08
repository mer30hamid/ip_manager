from flask import Flask, render_template, request
import os
import ipaddress

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 

ALLOWED_FILES = ['All.txt', 'irancell.txt', 'rightel.txt', 'samantel.txt', 'selected.txt']

def normalize_ip_entry(item):
    """Extract clean IP address from IP:port strings or CIDR notation"""
    try:
        # Try to parse as IP:port first
        ip_port_parts = item.split(':')
        if len(ip_port_parts) > 1 and ip_port_parts[-1].isdigit():
            item = ip_port_parts[0]  # Extract just the IP part

        # Try to parse as CIDR notation
        ip_obj = ipaddress.ip_network(item.strip(), strict=False)
        return str(ip_obj).split('/')[0] if '/' in str(ip_obj) else str(ip_obj)
    except ValueError:
        # Not a valid IP or CIDR
        raise

def get_existing_ips(filename):
    # Look for file in ips folder
    ips_folder = 'ips'
    filepath = os.path.join(ips_folder, filename)
    if not os.path.exists(filepath): return set()
    with open(filepath, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_ips(filename, ip_set):
    # Create ips folder if it doesn't exist
    ips_folder = 'ips'
    if not os.path.exists(ips_folder):
        os.makedirs(ips_folder)
    
    # Save file in ips folder (append mode)
    filepath = os.path.join(ips_folder, filename)
    with open(filepath, 'w') as f:
        for ip in sorted(list(ip_set)):
            f.write(f"{ip}\n")

@app.route('/', methods=['GET', 'POST'])
def index():
    report = None
    # تعیین فایل فعلی (اگر در URL نبود، All.txt)
    selected_file = request.args.get('current_file', 'All.txt')
    if selected_file not in ALLOWED_FILES:
        selected_file = 'All.txt'

    if request.method == 'POST':
        target_file = request.form.get('target_file')
        if target_file not in ALLOWED_FILES:
            report = {"error": "فایل نامعتبر!", "invalid_details": [], "added":0, "duplicates":0, "invalid":0, "total":0}
        else:
            input_items = []
            # اولویت ۱: فایل آپلود شده
            if 'file' in request.files and request.files['file'].filename != '':
                try:
                    content = request.files['file'].read().decode('utf-8')
                    input_items = [item.strip() for item in content.replace(',', '\n').split('\n') if item.strip()]
                except: report = {"error": "خطا در خواندن فایل!", "invalid_details": [], "added":0, "duplicates":0, "invalid":0, "total":0}
            # اولویت ۲: متن کپی شده
            else:
                raw_data = request.form.get('ip_list', '')
                input_items = [item.strip() for item in raw_data.replace(',', '\n').split('\n') if item.strip()]

            if report is None and not input_items:
                report = {"error": "ورودی خالی است!", "invalid_details": [], "added":0, "duplicates":0, "invalid":0, "total":0}
            elif report is None:
                existing_ips = get_existing_ips(target_file)
                added, dups, inv = 0, 0, 0
                inv_list = []
                cidr_count = 0

                for item in input_items:
                    try:
                        normalized_ip = normalize_ip_entry(item)
                        ip_obj = ipaddress.IPv4Address(normalized_ip)
                        clean_ip = str(ip_obj)

                        if '/' in item:
                            cidr_count += 1
                            # For CIDR ranges, add all IPs in the range to the target file
                            for ip in ip_obj.hosts():
                                if str(ip) not in existing_ips:
                                    existing_ips.add(str(ip))
                                    added += 1
                            dups += 1  # Count the entire CIDR as a duplicate of itself
                        else:
                            if clean_ip in existing_ips: dups += 1
                            else:
                                existing_ips.add(clean_ip)
                                added += 1
                    except:
                        inv += 1
                        if len(inv_list) < 500: inv_list.append(item)

                save_ips(target_file, existing_ips)
                report = {
                    "added": added, "duplicates": dups, "invalid": inv,
                    "invalid_details": inv_list, "total": len(existing_ips),
                    "target_file": target_file, "cidr_count": cidr_count
                }

    return render_template('index.html', report=report, selected_file=selected_file, allowed_files=ALLOWED_FILES)

if __name__ == '__main__':
    app.run(debug=True)
