from flask import Flask, render_template_string
from summarize import get_email_summaries

app = Flask(__name__)

@app.route("/")
def index():
    summaries = get_email_summaries()
    return render_template_string("""
<h1>Today's Email Summaries</h1>
{% for item in summaries %}
<h3>{{ item.subject }}</h3>
<p>{{ item.summary }}</p>
<hr>
{% endfor %}
""", summaries=summaries)

if __name__ == "__main__":
    app.run(debug=True)