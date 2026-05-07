from flask import Flask, request, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)
nama_file = "../mbg/riwayat_duid.json"

# Tampilan Web Sederhana untuk HP kamu
html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>ATM Mini</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="font-family: Arial; text-align: center; margin-top: 50px; background-color: #f4f4f9;">
    <h2 style="color: #333;">Setor Tunai (Ceritanya)</h2>
    <p style="color: #666;">Jumlah uang</p>
    <form method="POST">
        <input type="number" name="nominal" placeholder="Nominal (Rp)" required 
               style="padding: 15px; font-size: 18px; width: 80%; max-width: 300px; border-radius: 8px; border: 1px solid #ccc;"><br><br>
        <button type="submit" 
                style="padding: 15px 30px; font-size: 18px; background-color: #28a745; color: white; border: none; border-radius: 8px; cursor: pointer; width: 80%; max-width: 320px;">
            Setor
        </button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def mesin_atm():
    if request.method == 'POST':
        nominal_top_up = int(request.form['nominal'])
        
        if os.path.exists(nama_file):
            with open(nama_file, "r") as f:
                data = json.load(f)
        else:
            data = {"saldo": 0.0, "transaksi": []}
            
        data["saldo"] += nominal_top_up
        
        transaksi_baru = {
            "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nama"   : "Setor Tunai ATM",
            "rek"    : "-",
            "nominal": nominal_top_up,
            "bank"   : "Cash",
            "jenis"  : "Setor"
        }
        data["transaksi"].append(transaksi_baru)
        
        with open(nama_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return f"""
        <div style='font-family: Arial; text-align:center; margin-top:50px;'>
            <h1 style='color:green;'>✅ Berhasil!</h1>
            <h2>Uang Rp {nominal_top_up:,.0f} sudah masuk.</h2>
            <p>Silakan cek Menu "Saldo" atau "Riwayat" mu.</p>
            <br>
            <a href="/" style="padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Kembali</a>
        </div>
        """
    
    return render_template_string(html_form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)