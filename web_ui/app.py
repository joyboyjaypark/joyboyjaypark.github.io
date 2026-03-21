from flask import Flask, render_template, request, redirect, url_for, flash
from duct import renewal
import threading

app = Flask(__name__)
app.secret_key = 'change-me-in-prod'

# Shared state for last run
last_result = {}
last_lock = threading.Lock()

@app.route('/')
def index():
    with last_lock:
        result = last_result.copy()
    return render_template('index.html', result=result)

@app.route('/run', methods=['POST'])
def run():
    url = request.form.get('url') or None
    headless = request.form.get('headless') == 'on'

    def worker(u, h):
        res = renewal.reset_site_storage(url=u if u else None, headless=h)
        with last_lock:
            last_result.clear()
            last_result.update(res)

    thread = threading.Thread(target=worker, args=(url, headless), daemon=True)
    thread.start()
    flash('작업이 시작되었습니다. 잠시 후 결과를 새로고침해서 확인하세요.', 'info')
    return redirect(url_for('index'))


@app.route('/engineer')
def engineer():
    return render_template('engineer.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
