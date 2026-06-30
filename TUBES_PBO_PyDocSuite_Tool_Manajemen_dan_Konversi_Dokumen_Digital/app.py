"""
CoreDoc - Main Flask Application
"""
import os
from flask import Flask, render_template

from config import ensure_runtime_directories
from controllers.word_pdf_controller import word_pdf_bp
from controllers.pdf_word_controller import pdf_word_bp
from controllers.ocr_controller import ocr_bp
from controllers.history_controller import history_bp
from controllers.batch_controller import batch_bp

def create_app() -> Flask:
    ensure_runtime_directories()
    
    app = Flask(__name__)
    app.secret_key = os.environ.get("PYDOCSUITE_SECRET_KEY", "coredoc-secret-key-12345")
    
    # Register blueprints
    app.register_blueprint(word_pdf_bp, url_prefix="/word-to-pdf")
    app.register_blueprint(pdf_word_bp, url_prefix="/pdf-to-word")
    app.register_blueprint(ocr_bp, url_prefix="/ocr")
    app.register_blueprint(history_bp, url_prefix="/history")
    app.register_blueprint(batch_bp, url_prefix="/batch")
    
    @app.route("/")
    def index():
        # Home page can just redirect to word-to-pdf or show a landing page
        # Since word-to-pdf has index.html as the landing, we'll route it there.
        from flask import redirect, url_for
        return redirect(url_for("word_pdf.index"))
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
