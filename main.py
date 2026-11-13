import os
from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"  Agentic AI: Academic Research Assistant Team (CSE476)")
    print(f"  Running on: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=(env == 'development'))

