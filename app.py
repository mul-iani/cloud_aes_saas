from flask import Flask, render_template, request, send_file
from supabase import create_client, Client
from aes_utils import encrypt_data, decrypt_data  # Jika aes_utils.py sejajar dengan app.py
from storage3.exceptions import StorageApiError
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import os

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

# Init Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Init Flask
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
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

        return f"✅ File terenkripsi dan berhasil diunggah: {filename}"

    except StorageApiError as e:
        return f"❌ Gagal upload ke Supabase: {e.message}"

    except Exception as e:
        return f"⚠️ Terjadi error: {str(e)}"


@app.route("/download", methods=["GET"])
def download():
    filename = request.args.get("filename")
    if not filename:
        return "❌ Nama file tidak diberikan."

    try:
        # Download terenkripsi dari Supabase
        encrypted_data = supabase.storage.from_(SUPABASE_BUCKET).download(filename)

        # Dekripsi
        decrypted_data = decrypt_data(encrypted_data)

        # Kirim file hasil dekripsi
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
