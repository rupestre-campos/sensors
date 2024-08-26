
#!/bin/bash
source /home/cx/sensors/app/.venv/bin/activate
exec streamlit run /home/cx/sensors/app/app.py --server.headless true --server.port 8510
