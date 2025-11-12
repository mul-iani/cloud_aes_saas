from flask import Flask, render_template, request, send_file
from supabase import create_client, Client
from aes_utils import encrypt_data, decrypt_data
from storage3.exceptions import StorageApiError
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if not file:
        return "❌ Tidak ada file diunggah."

    data = file.read()
    encrypted_data = encrypt_data(data)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"

    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename,
            encrypted_data,
            {"upsert": False}
        )
        return f"✅ File terenkripsi dan diunggah: {filename}"
    except StorageApiError as e:
        return f"❌ Gagal upload ke Supabase: {e.message}"
    except Exception as e:
        return f"⚠️ Terjadi error: {str(e)}"

@app.route("/download", strict_slashes=False)
def download():
    filename = request.args.get("filename")
    if not filename:
        return "❌ Nama file tidak diberikan."

    try:
        res = supabase.storage.from_(SUPABASE_BUCKET).download(filename)
        decrypted_data = decrypt_data(res)
        return send_file(
            BytesIO(decrypted_data),
            as_attachment=True,
            download_name=filename
        )
    except StorageApiError as e:
        return f"❌ Gagal mengunduh dari Supabase: {e.message}"
    except Exception as e:
        return f"⚠️ Terjadi error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
